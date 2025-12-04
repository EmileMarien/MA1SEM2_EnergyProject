"""Cost function builders and helpers for optimizer.

Provides make_cost_fn(...) which returns (cost_fn, compute_metrics_fn). The cost
function returns a scalar cost (NPV). compute_metrics_fn returns a detailed
breakdown including capex and annual costs and the grid time series.
"""
from typing import Tuple, Callable, Dict, Any
from math import gcd
import pickle
import os

import powercalculations.powercalculations as pc
import gridcost.gridcost as gc

# Simple in-memory cache for generated grid_series keyed by a tuple
_DEFAULT_GRID_CACHE = {}


def _lcm(a: int, b: int) -> int:
    return a * b // gcd(a, b) if a and b else max(a, b)


def _ensure_pickled_irradiance(pkl_path: str):
    if not os.path.exists(pkl_path):
        raise FileNotFoundError(f"Pickle path not found: {pkl_path}")
    with open(pkl_path, "rb") as f:
        irradiance = pickle.load(f)
    return irradiance


def make_cost_fn(
    orientation: str = "S",
    tilt_angle: int = 30,
    tariff: str = "DynamicTariff",
    discount_rate: float = 0.05,
    pkl_path: str = None,
    cache: Dict = None,
) -> Tuple[Callable[[Dict[str, Any]], float], Callable[[Dict[str, Any]], Dict[str, Any]]]:
    """Return (cost_fn, compute_metrics_fn).

    cost_fn(params) -> float (NPV). Params may be a dict containing keys
    'solar','battery','inverter','contract' where each value is either a
    dataclass-like object with attributes or a dict with the expected keys.

    compute_metrics_fn(params) -> dict with detailed outputs.
    """

    if cache is None:
        cache = _DEFAULT_GRID_CACHE

    # Map known orientation/tilt combos to pickles (reuse your repo convention)
    pickles = {
        ("S", 37.5): "data/initialized_dataframes/pd_S_opt_37.5",
        ("EW", 32): "data/initialized_dataframes/pd_EW_opt_32",
        ("EW", 30): "data/initialized_dataframes/pd_EW_30",
        ("S", 30): "data/initialized_dataframes/pd_S_30",
        ("E", 30): "data/initialized_dataframes/pd_E_30",
        ("W", 30): "data/initialized_dataframes/pd_W_30",
    }

    if pkl_path is None:
        pkl_path = pickles.get((orientation, tilt_angle), "data/initialized_dataframes/pd_S_30")

    def _as_obj(v):
        # Accept dict or object, return object-like with attribute access
        if v is None:
            return None
        if isinstance(v, dict):
            class D:
                pass

            d = D()
            for k, val in v.items():
                setattr(d, k, val)
            return d
        return v

    def _build_cache_key(solar, battery, inverter):
        return (
            int(getattr(solar, "solar_panel_count", 0)),
            float(getattr(solar, "panel_surface", 0.0)),
            float(getattr(solar, "panel_efficiency", 0.0)),
            int(getattr(battery, "battery_count", 0)),
            float(getattr(battery, "battery_capacity", 0.0)),
            float(getattr(inverter, "AC_output", 0.0)),
            float(getattr(inverter, "DC_solar_panels", 0.0)),
        )

    def compute_grid_series(solar, battery, inverter):
        key = _build_cache_key(solar, battery, inverter)
        if key in cache:
            return cache[key]

        irradiance = _ensure_pickled_irradiance(pkl_path)

        # copy to avoid mutating the cached object
        # many PowerCalculations objects are mutable; load fresh each call
        # (we re-open the pickle to get a fresh instance)
        irradiance = _ensure_pickled_irradiance(pkl_path)

        # PV generation
        irradiance.PV_generated_power(
            cell_area=getattr(solar, "panel_surface", 0.0),
            panel_count=getattr(solar, "solar_panel_count", 0),
            T_STC=25,
            efficiency_max=getattr(solar, "panel_efficiency", 0.0) * (1 - getattr(solar, "annual_degredation", 0.0) / 100.0),
            Temp_coeff=getattr(solar, "temperature_coefficient", 0.0),
        )

        max_charge = getattr(battery, "battery_capacity", 0.0) * getattr(battery, "battery_count", 0)

        irradiance.power_flow(
            max_charge=max_charge,
            max_AC_power_output=getattr(inverter, "AC_output", None),
            max_PV_input=getattr(inverter, "DC_solar_panels", None),
            max_DC_batterypower=getattr(inverter, "DC_battery", None),
            battery_roundtrip_efficiency=97.5,
            battery_PeakPower=getattr(battery, "battery_capacity", None),
        )

        grid_series = irradiance.get_grid_power()[0]
        cache[key] = grid_series
        return grid_series

    def compute_metrics(params: Dict[str, Any]) -> Dict[str, Any]:
        # Normalize inputs
        solar = _as_obj(params.get("solar"))
        battery = _as_obj(params.get("battery"))
        inverter = _as_obj(params.get("inverter"))
        contract = params.get("contract")
        if contract is None:
            contract = {}
        if not isinstance(contract, dict):
            # try dataclass-like
            try:
                contract = contract.as_dict()
            except Exception:
                # fallback: build from attributes
                contract = {
                    "resample_freq": getattr(contract, "resample_freq", "1h"),
                    "belpex_scale": getattr(contract, "belpex_scale", 1.1261),
                    "dual_peak_tariff": getattr(contract, "dual_peak_tariff", getattr(contract, "peak_tariff", 0.1701)),
                    "dual_offpeak_tariff": getattr(contract, "dual_offpeak_tariff", getattr(contract, "offpeak_tariff", 0.1463)),
                    "dual_fixed_tariff": getattr(contract, "dual_fixed_tariff", getattr(contract, "fixed_tariff", 0.01554)),
                    "dual_injection_tariff": getattr(contract, "dual_injection_tariff", getattr(contract, "injection_tariff", 0.03)),
                    "capacity_tariff_rate": getattr(contract, "capacity_tariff_rate", 41.3087),
                }

        # Build grid series (cached)
        grid_series = compute_grid_series(solar, battery, inverter)

        # Create GridCost with contract params
        financials = gc.GridCost(grid_series, file_path_BelpexFilter="", **contract)

        # calculate tariffs
        try:
            financials.dual_tariff()
        except Exception:
            pass
        try:
            financials.dynamic_tariff()
        except Exception:
            pass

        # compute annual energy cost and fixed component
        tariff_type = params.get("tariff", tariff)
        try:
            annual_energy_cost = financials.get_grid_cost_total(calculationtype=tariff_type)
        except Exception:
            # fallback sum
            annual_energy_cost = float(financials.get_grid_cost_perhour(calculationtype=tariff_type).sum())

        fixed_component_dual = 111.3
        fixed_component_dynamic = 100.7
        fixed_component = fixed_component_dual if tariff_type == "DualTariff" else fixed_component_dynamic

        annual_cost_year1 = annual_energy_cost + fixed_component

        # capex
        capex = 0
        capex += getattr(solar, "total_solar_panel_cost", getattr(solar, "solar_panel_cost", 0) * getattr(solar, "solar_panel_count", 0))
        capex += getattr(battery, "total_battery_cost", getattr(battery, "battery_cost", 0) * getattr(battery, "battery_count", 0))
        capex += getattr(inverter, "inverter_cost", 0)

        # NPV over horizon = LCM of lifetimes
        solar_life = int(getattr(solar, "solar_panel_lifetime", 10))
        battery_life = int(getattr(battery, "battery_lifetime", 5))
        inverter_life = int(getattr(inverter, "inverter_lifetime", 10))
        horizon = _lcm(_lcm(solar_life, battery_life), inverter_life)

        npv = -capex
        for year in range(1, horizon + 1):
            # approximate degradation scaling
            deg = getattr(solar, "annual_degredation", 0.0) / 100.0
            operating_cost = annual_cost_year1 * ((1 + deg) ** (year - 1))

            repl = 0
            if year % solar_life == 0:
                repl += getattr(solar, "total_solar_panel_cost", 0)
            if year % battery_life == 0:
                repl += getattr(battery, "total_battery_cost", 0)
            if year % inverter_life == 0:
                repl += getattr(inverter, "inverter_cost", 0)

            cashflow = -operating_cost - repl
            npv += cashflow / ((1 + discount_rate) ** year)

        return {
            "npv": npv,
            "capex": capex,
            "annual_energy_cost": annual_energy_cost,
            "fixed_component": fixed_component,
            "annual_cost_year1": annual_cost_year1,
            "grid_series": grid_series,
            "horizon": horizon,
        }

    def cost_fn(params: Dict[str, Any]) -> float:
        metrics = compute_metrics(params)
        return float(metrics["npv"])

    return cost_fn, compute_metrics
