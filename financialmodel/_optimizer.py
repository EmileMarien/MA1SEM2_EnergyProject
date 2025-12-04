"""Simple combinatorial optimizer for component selection.

Given lists of component instances (SolarPanel, Battery, Inverter) and a list
of contract descriptors (either initialized `GridCost` instances or dicts with
tariff settings), evaluate each combination and return the combinations that
minimize the Net Present Value (NPV) of the project cost.

Notes / assumptions implemented here:
- Uses `powercalculations.PowerCalculations` pickled datasets (same approach
  as `electricity_cost`) to generate PV production and run the `power_flow` to
  obtain a grid flow time series for a given component combination.
- For each contract passed in, the optimizer creates a fresh `GridCost` using
  the calculated grid flow series and the tariff/settings taken from the
  provided contract object/dict.
- Annual operating cost is approximated from the grid-cost calculation in
  year 1 and scaled by panel degradation in subsequent years.
- Replacement costs for panels, batteries and inverters are applied when the
  component's lifetime completes (simple full replacement model).

Return value: a sorted list of results (lowest NPV first). Each result is a
dict with keys: 'solar','battery','inverter','contract','npv','capex','annual_cost'.
"""

from math import gcd
import pickle
import os
from typing import Iterable, List

import powercalculations.powercalculations as pc
import gridcost.gridcost as gc


def _lcm(a: int, b: int) -> int:
    return a * b // gcd(a, b) if a and b else max(a, b)


def optimizer(
    solarpanels: Iterable,
    batteries: Iterable,
    inverters: Iterable,
    contracts: Iterable,
    *,
    orientation: str = "S",
    tilt_angle: int = 30,
    discount_rate: float = 0.05,
    tariff: str = "DynamicTariff",
):
    """Evaluate combinations and return sorted results by NPV (ascending).

    solarpanels, batteries, inverters: iterables of component instances as
    defined in `components`.
    contracts: iterable of either `gc.GridCost` instances or dict-like objects
    that contain the GridCost init parameters (e.g. 'peak_tariff', 'offpeak_tariff', ...)
    """

    results: List[dict] = []

    # Map orientation/tilt to existing pickle files (same as electricity_cost)
    pickles = {
        ("S", 37.5): "data/initialized_dataframes/pd_S_opt_37.5",
        ("EW", 32): "data/initialized_dataframes/pd_EW_opt_32",
        ("EW", 30): "data/initialized_dataframes/pd_EW_30",
        ("S", 30): "data/initialized_dataframes/pd_S_30",
        ("E", 30): "data/initialized_dataframes/pd_E_30",
        ("W", 30): "data/initialized_dataframes/pd_W_30",
    }

    pkl_path = pickles.get((orientation, tilt_angle), "data/initialized_dataframes/pd_S_30")
    if not os.path.exists(pkl_path):
        raise FileNotFoundError(f"Required irradiance pickle not found: {pkl_path}")

    # Iterate through all combinations
    for solar in solarpanels:
        for battery in batteries:
            for inverter in inverters:
                # Build PV/load dataset for this configuration (coarse approximation)
                with open(pkl_path, "rb") as f:
                    irradiance = pickle.load(f)

                # Ensure irradiance object is a PowerCalculations instance
                if not isinstance(irradiance, pc.PowerCalculations):
                    raise TypeError("Pickled irradiance object is not a PowerCalculations instance")

                # Run PV generation and power flow with component params
                try:
                    irradiance.PV_generated_power(
                        cell_area=solar.panel_surface,
                        panel_count=solar.solar_panel_count,
                        T_STC=25,
                        efficiency_max=solar.panel_efficiency * (1 - solar.annual_degredation / 100),
                        Temp_coeff=solar.temperature_coefficient,
                    )
                except Exception:
                    # Best-effort: continue to next combo if PV generation fails
                    continue

                max_charge = battery.battery_capacity * battery.battery_count
                try:
                    irradiance.power_flow(
                        max_charge=max_charge,
                        max_AC_power_output=getattr(inverter, "AC_output", None),
                        max_PV_input=getattr(inverter, "DC_solar_panels", None),
                        max_DC_batterypower=getattr(inverter, "DC_battery", None),
                        battery_roundtrip_efficiency=97.5,
                        battery_PeakPower=getattr(battery, "battery_capacity", None),
                    )
                except Exception:
                    continue

                grid_series = irradiance.get_grid_power()[0]

                # compute capex
                capex = 0
                capex += getattr(solar, "total_solar_panel_cost", 0)
                capex += getattr(battery, "total_battery_cost", 0)
                capex += getattr(inverter, "inverter_cost", 0)

                # compute base annual operating cost for year 1 per contract
                for contract in contracts:
                    # contract may be an initialized GridCost or a dict-like
                    if isinstance(contract, gc.GridCost):
                        # extract parameters to re-initialize GridCost with our grid data
                        params = dict(
                            resample_freq=getattr(contract, "resample_freq", "1h"),
                            belpex_scale=getattr(contract, "belpex_scale", 1.0),
                            dual_peak_tariff=getattr(contract, "peak_tariff", 0.1701),
                            dual_offpeak_tariff=getattr(contract, "offpeak_tariff", 0.1463),
                            dual_fixed_tariff=getattr(contract, "fixed_tariff", 0.01554),
                            dual_injection_tariff=getattr(contract, "injection_tariff", 0.03),
                            capacity_tariff_rate=getattr(contract, "capacity_tariff_rate", 41.3087),
                        )
                    elif isinstance(contract, dict):
                        params = contract.copy()
                    else:
                        raise TypeError("Each contract must be a GridCost instance or a dict with contract settings")

                    # Create GridCost for this grid series and contract settings
                    financials = gc.GridCost(grid_series, file_path_BelpexFilter="", **params)
                    # Calculate both tariffs so that get_grid_cost_total works
                    try:
                        financials.dual_tariff()
                    except Exception:
                        # ignore tariff calc errors per-contract
                        pass
                    try:
                        financials.dynamic_tariff()
                    except Exception:
                        pass

                    # Choose tariff type
                    tariff_type = tariff

                    try:
                        annual_energy_cost = financials.get_grid_cost_total(calculationtype=tariff_type)
                    except Exception:
                        # Fallback: sum of hourly cost series
                        series = financials.get_grid_cost_perhour(calculationtype=tariff_type)
                        annual_energy_cost = float(series.sum())

                    # Add fixed components approximated from electricity_cost defaults
                    fixed_component_dual = 111.3
                    fixed_component_dynamic = 100.7
                    fixed_component = fixed_component_dual if tariff_type == "DualTariff" else fixed_component_dynamic
                    annual_cost_year1 = annual_energy_cost + fixed_component

                    # Build lifetime horizon as LCM of component lifetimes
                    lcm_sb = _lcm(int(getattr(solar, "solar_panel_lifetime", 10)), int(getattr(battery, "battery_lifetime", 5)))
                    lcm_all = _lcm(lcm_sb, int(getattr(inverter, "inverter_lifetime", 10)))
                    horizon = lcm_all

                    # NPV calculation with replacements at end of lifetimes
                    npv = -capex
                    for year in range(1, horizon + 1):
                        # Approximate degradation effect: increase operating cost with PV degradation
                        deg = getattr(solar, "annual_degredation", 0) / 100.0
                        # Assume operating cost scales inversely with production: approx (1 + deg)^(year-1)
                        operating_cost = annual_cost_year1 * ((1 + deg) ** (year - 1))

                        # Replacement costs
                        repl = 0
                        if year % getattr(solar, "solar_panel_lifetime", 10) == 0:
                            repl += getattr(solar, "total_solar_panel_cost", 0)
                        if year % getattr(battery, "battery_lifetime", 5) == 0:
                            repl += getattr(battery, "total_battery_cost", 0)
                        if year % getattr(inverter, "inverter_lifetime", 10) == 0:
                            repl += getattr(inverter, "inverter_cost", 0)

                        cashflow = -operating_cost - repl
                        npv += cashflow / ((1 + discount_rate) ** year)

                    results.append(
                        {
                            "solar": solar,
                            "battery": battery,
                            "inverter": inverter,
                            "contract_params": params,
                            "npv": npv,
                            "capex": capex,
                            "annual_cost_year1": annual_cost_year1,
                        }
                    )

    # sort by NPV (lowest is best)
    results.sort(key=lambda x: x["npv"]) 
    return results


def grid_search(param_grid: dict, cost_fn, *, top_k: int = 10, progress: bool = False):
    """Perform a grid search over the provided parameter grid using cost_fn.

    Args:
        param_grid: dict mapping parameter names to iterables of values.
        cost_fn: callable that accepts a dict of parameters and returns a scalar cost
                (lower is better). It should raise on invalid parameter sets.
        top_k: number of best results to return (default 10).
        progress: if True, prints progress to stdout (simple counter).

    Returns:
        list of dicts sorted by cost ascending. Each dict contains 'params' and 'cost'.

    Example:
        def my_cost(params):
            # build components using params and return npv
            return compute_npv_from_params(params)

        grid = { 'panel_count': [0,10,20], 'battery_count': [0,1] }
        best = grid_search(grid, my_cost, top_k=5)
"""

    from itertools import product

    keys = list(param_grid.keys())
    pools = [list(param_grid[k]) for k in keys]

    results = []
    total = 1
    for p in pools:
        total *= max(1, len(p))

    i = 0
    for combo in product(*pools):
        i += 1
        params = dict(zip(keys, combo))
        try:
            cost = float(cost_fn(params))
        except Exception:
            # skip invalid parameter combinations
            continue

        results.append({"params": params, "cost": cost})
        if progress and i % 50 == 0:
            print(f"Evaluated {i}/{total} combinations")

    results.sort(key=lambda x: x["cost"]) 
    return results[:top_k]
    