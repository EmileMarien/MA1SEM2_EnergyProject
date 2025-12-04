# financialModel.py

from __future__ import annotations

from dataclasses import is_dataclass, asdict
from math import gcd
from typing import Iterable, List, Dict, Any, Optional, Union, Tuple

import os
import pickle

import pandas as pd
import powercalculations.powercalculations as pc  # type: ignore

from financialmodel.models import SolarSpec, BatterySpec, InverterSpec, ElectricityContract
from gridcost.gridcost import GridCost


def _lcm(a: int, b: int) -> int:
    """Least common multiple, robust against zeros."""
    return a * b // gcd(a, b) if a and b else max(a, b)


class FinancialModel:
    """
    High-level orchestrator for optimisation of components and contracts.

    Two main use cases:

    1) Full component optimisation
       - Varies solar, battery, inverter and contract options.
       - For each combination:
         * Builds a PowerCalculations object from a pickled dataset.
         * Runs PV + battery power flow to get a GridFlow time series.
         * Uses GridCost(electricity_contract=...) to compute annual grid cost.
         * Computes NPV of (capex + OPEX + replacements) over a lifetime horizon.

    2) Contract-only optimisation
       - Starts from an existing GridFlow time series (consumption_data_df/CSV).
       - For each contract option:
         * Builds a GridCost with that contract.
         * Computes annual cost and its NPV over a given horizon.
    """

    def __init__(
        self,
        *,
        orientation: str = "S",
        tilt_angle: int = 30,
        discount_rate: float = 0.05,
        default_tariff: str = "DynamicTariff",
        pkl_path: Optional[str] = None,
        belpex_filter_path: str = "",
    ) -> None:
        self.orientation = orientation
        self.tilt_angle = tilt_angle
        self.discount_rate = discount_rate
        self.default_tariff = default_tariff
        self.pkl_path = pkl_path
        self.belpex_filter_path = belpex_filter_path

        # cache for grid series keyed by component configuration
        self._grid_cache: Dict[Tuple, pd.Series | pd.DataFrame] = {}

    # ------------------------------------------------------------------
    # internal helpers
    # ------------------------------------------------------------------

    def _pickled_path(self) -> str:
        """Resolve which irradiance pickle to use for power flow."""
        if self.pkl_path:
            return self.pkl_path

        # Same mapping as in older code (electricity_cost / _optimizer / costs)
        pickles = {
            ("S", 37.5): "data/initialized_dataframes/pd_S_opt_37.5",
            ("EW", 32): "data/initialized_dataframes/pd_EW_opt_32",
            ("EW", 30): "data/initialized_dataframes/pd_EW_30",
            ("S", 30): "data/initialized_dataframes/pd_S_30",
            ("E", 30): "data/initialized_dataframes/pd_E_30",
            ("W", 30): "data/initialized_dataframes/pd_W_30",
        }

        return pickles.get((self.orientation, self.tilt_angle), "data/initialized_dataframes/pd_S_30")

    def _load_irradiance(self) -> pc.PowerCalculations:
        """Load the PowerCalculations object from pickle."""
        path = self._pickled_path()
        if not os.path.exists(path):
            raise FileNotFoundError(f"Required irradiance pickle not found: {path}")

        with open(path, "rb") as f:
            irradiance = pickle.load(f)

        if not isinstance(irradiance, pc.PowerCalculations):
            raise TypeError("Pickled object is not a powercalculations.PowerCalculations instance")

        return irradiance

    @staticmethod
    def _contract_to_obj(c: Union[ElectricityContract, Dict[str, Any]]) -> ElectricityContract:
        """Normalize various 'contract' inputs to an ElectricityContract."""
        if isinstance(c, ElectricityContract):
            return c
        if is_dataclass(c):
            # some other dataclass with same fields
            return ElectricityContract(**asdict(c))
        if isinstance(c, dict):
            return ElectricityContract(**c)
        raise TypeError(f"Unsupported contract type: {type(c)!r}")

    @staticmethod
    def _build_grid_cache_key(
        solar: SolarSpec,
        battery: BatterySpec,
        inverter: InverterSpec,
    ) -> Tuple:
        """Key for caching grid_series by component configuration."""
        return (
            int(solar.solar_panel_count),
            float(solar.panel_surface),
            float(solar.panel_efficiency),
            float(solar.annual_degredation),
            int(battery.battery_count),
            float(battery.battery_capacity),
            float(inverter.AC_output),
            float(inverter.DC_solar_panels),
            float(inverter.DC_battery),
        )

    def _compute_grid_series(
        self,
        solar: SolarSpec,
        battery: BatterySpec,
        inverter: InverterSpec,
    ) -> pd.Series | pd.DataFrame:
        """
        Run PV + battery power flow and return the resulting GridFlow time series.

        The result is whatever `PowerCalculations.get_grid_power()[0]` returns:
        typically a pandas Series/DataFrame indexed by DateTime with GridFlow power.
        """
        key = self._build_grid_cache_key(solar, battery, inverter)
        if key in self._grid_cache:
            return self._grid_cache[key]

        irradiance = self._load_irradiance()

        # PV generation
        irradiance.PV_generated_power(
            cell_area=solar.panel_surface,
            panel_count=solar.solar_panel_count,
            T_STC=25,
            efficiency_max=solar.panel_efficiency * (1 - solar.annual_degredation / 100.0),
            Temp_coeff=solar.temperature_coefficient,
        )

        # Battery + inverter power flow
        max_charge = battery.battery_capacity * battery.battery_count
        irradiance.power_flow(
            max_charge=max_charge,
            max_AC_power_output=inverter.AC_output,
            max_PV_input=inverter.DC_solar_panels,
            max_DC_batterypower=inverter.DC_battery,
            battery_roundtrip_efficiency=97.5,
            battery_PeakPower=battery.battery_capacity,
        )

        grid_series = irradiance.get_grid_power()[0]
        self._grid_cache[key] = grid_series
        return grid_series

    @staticmethod
    def _capex(solar: SolarSpec, battery: BatterySpec, inverter: InverterSpec) -> float:
        """Total upfront investment for this component set."""
        return (
            solar.total_solar_panel_cost
            + battery.total_battery_cost
            + inverter.inverter_cost
        )

    @staticmethod
    def _lifetime_horizon(
        solar: SolarSpec,
        battery: BatterySpec,
        inverter: InverterSpec,
    ) -> int:
        """LCM of component lifetimes (years)."""
        lcm_sb = _lcm(int(solar.solar_panel_lifetime), int(battery.battery_lifetime))
        return _lcm(lcm_sb, int(inverter.inverter_lifetime))

    # ------------------------------------------------------------------
    # 1) Full component optimisation (components + contracts)
    # ------------------------------------------------------------------

    def optimise_components(
        self,
        *,
        solar_options: Iterable[SolarSpec],
        battery_options: Iterable[BatterySpec],
        inverter_options: Iterable[InverterSpec],
        contract_options: Iterable[Union[ElectricityContract, Dict[str, Any]]],
        top_k: Optional[int] = None,
        discount_rate: Optional[float] = None,
        belpex_filter_path: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Evaluate every combination of (solar, battery, inverter, contract)
        and return results sorted by NPV of total cost (ascending).

        Returns a list of dicts with keys:
            - 'solar', 'battery', 'inverter', 'contract'
            - 'annual_cost_year1'
            - 'capex'
            - 'npv_cost'       (present value of all costs, > 0)
            - 'horizon_years'
        """
        if discount_rate is None:
            discount_rate = self.discount_rate
        if belpex_filter_path is None:
            belpex_filter_path = self.belpex_filter_path

        results: List[Dict[str, Any]] = []

        for solar in solar_options:
            for battery in battery_options:
                for inverter in inverter_options:
                    # 1) grid time series for this component combo
                    try:
                        grid_series = self._compute_grid_series(solar, battery, inverter)
                    except Exception as exc:  # noqa: BLE001
                        # skip invalid / failing combinations
                        continue

                    capex = self._capex(solar, battery, inverter)
                    horizon = self._lifetime_horizon(solar, battery, inverter)

                    for c in contract_options:
                        contract_obj = self._contract_to_obj(c)

                        # 2) annual cost using GridCost + ElectricityContract
                        gc = GridCost(
                            consumption_data_df=grid_series,
                            file_path_BelpexFilter=belpex_filter_path,
                            electricity_contract=contract_obj,
                        )
                        annual_cost_year1 = gc.calculate_total_cost(
                            tariff=contract_obj.contract_type
                            if contract_obj.contract_type
                            else self.default_tariff
                        )

                        # 3) NPV of costs (capex + yearly OPEX + replacements)
                        npv_cost = capex  # year 0 capex (undiscounted)
                        deg = solar.annual_degredation / 100.0

                        for year in range(1, horizon + 1):
                            # scale OPEX with degradation approx.
                            operating_cost = annual_cost_year1 * ((1 + deg) ** (year - 1))

                            # replacement costs at end-of-life years
                            replacement = 0.0
                            if year % int(solar.solar_panel_lifetime) == 0:
                                replacement += solar.total_solar_panel_cost
                            if year % int(battery.battery_lifetime) == 0:
                                replacement += battery.total_battery_cost
                            if year % int(inverter.inverter_lifetime) == 0:
                                replacement += inverter.inverter_cost

                            yearly_cost = operating_cost + replacement
                            npv_cost += yearly_cost / ((1 + discount_rate) ** year)

                        results.append(
                            {
                                "solar": solar,
                                "battery": battery,
                                "inverter": inverter,
                                "contract": contract_obj,
                                "annual_cost_year1": float(annual_cost_year1),
                                "capex": float(capex),
                                "npv_cost": float(npv_cost),
                                "horizon_years": int(horizon),
                            }
                        )

        # sort by NPV of cost (lower is better)
        results.sort(key=lambda r: r["npv_cost"])
        if top_k is not None:
            results = results[:top_k]
        return results

    # ------------------------------------------------------------------
    # 2) Contract-only optimisation (existing grid time series)
    # ------------------------------------------------------------------

    def optimise_contracts_from_consumption(
        self,
        *,
        contracts: Iterable[Union[ElectricityContract, Dict[str, Any]]],
        consumption_data_df: Optional[pd.DataFrame | pd.Series] = None,
        consumption_data_csv: str = "",
        horizon_years: int = 20,
        discount_rate: Optional[float] = None,
        belpex_filter_path: Optional[str] = None,
        return_breakdown: bool = False,
        top_k: Optional[int] = None,
        tariff: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Optimise only the contract choice starting from an already-known grid
        consumption time series.

        - `consumption_data_df` may be a DataFrame or Series with a DateTime
          index and a GridFlow column (or first numeric col used as GridFlow).
        - `consumption_data_csv` is a CSV in the format accepted by GridCost.

        Returns a list of dicts sorted by NPV of cost (ascending) with keys:
            - 'contract'
            - 'annual_cost_year1'
            - 'npv_cost'
            - 'breakdown' (if return_breakdown=True)
        """
        if consumption_data_df is None and not consumption_data_csv:
            raise ValueError(
                "You must provide either `consumption_data_df` or `consumption_data_csv`."
            )

        if discount_rate is None:
            discount_rate = self.discount_rate
        if belpex_filter_path is None:
            belpex_filter_path = self.belpex_filter_path

        results: List[Dict[str, Any]] = []

        for c in contracts:
            contract_obj = self._contract_to_obj(c)
            tariff_label = tariff or contract_obj.contract_type or self.default_tariff

            gc = GridCost(
                consumption_data_df=consumption_data_df,  # can be None
                consumption_data_csv=consumption_data_csv,
                file_path_BelpexFilter=belpex_filter_path,
                electricity_contract=contract_obj,
            )

            # Year-1 annual cost
            annual_cost = gc.calculate_total_cost(tariff=tariff_label)

            # NPV of repeated annual cost (no extra capex in this mode)
            npv_cost = 0.0
            for year in range(1, horizon_years + 1):
                yearly_cost = annual_cost
                npv_cost += yearly_cost / ((1 + discount_rate) ** year)

            entry: Dict[str, Any] = {
                "contract": contract_obj,
                "annual_cost_year1": float(annual_cost),
                "npv_cost": float(npv_cost),
                "horizon_years": int(horizon_years),
            }

            if return_breakdown:
                entry["breakdown"] = gc.calculate_total_cost(
                    tariff=tariff_label,
                    return_breakdown=True,
                )

            results.append(entry)

        results.sort(key=lambda r: r["npv_cost"])
        if top_k is not None:
            results = results[:top_k]
        return results
