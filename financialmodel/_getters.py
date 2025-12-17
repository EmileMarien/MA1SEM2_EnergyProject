from __future__ import annotations
from typing import Any, Callable, Mapping, Optional, Sequence, Tuple, Union

import numpy as np

from dataclasses import asdict, is_dataclass

import pandas as pd


def _get(obj: Any, key: str, default: Any = None) -> Any:
    """Get attribute/key from an object or mapping."""
    if obj is None:
        return default
    if isinstance(obj, Mapping):
        return obj.get(key, default)
    return getattr(obj, key, default)


def _as_compact_dict(obj: Any) -> dict[str, Any]:
    """Convert a (data)class or mapping to a plain dict for labeling."""
    if obj is None:
        return {}
    if isinstance(obj, Mapping):
        return dict(obj)
    if is_dataclass(obj):
        return asdict(obj)
    # fall back to a shallow attribute scrape
    out: dict[str, Any] = {}
    for k in (
        "name",
        "label",
        "id",
        "contract_id",
        "inverter_id",
        "contract_type",
        "AC_output",
        "DC_solar_panels",
        "DC_battery",
        "dual_peak_tariff",
        "dual_offpeak_tariff",
    ):
        v = getattr(obj, k, None)
        if v is not None:
            out[k] = v
    return out


def default_contract_label(contract: Any) -> str:
    """Make a short, stable-ish label for a contract object/dict."""
    d = _as_compact_dict(contract)

    for k in ("contract_id", "name", "label", "id"):
        if k in d and d[k] not in (None, ""):
            return str(d[k])

    ctype = str(d.get("contract_type") or "Contract")
    if ctype.lower().startswith("dual"):
        peak = d.get("dual_peak_tariff")
        off = d.get("dual_offpeak_tariff")
        if peak is not None and off is not None:
            return f"DualTariff (peak={float(peak):.3f}, off={float(off):.3f})"
        return "DualTariff"

    if ctype.lower().startswith("dynamic"):
        return "DynamicTariff"

    return ctype


def default_inverter_label(inverter: Any) -> str:
    """Make a short, stable-ish label for an inverter object/dict."""
    d = _as_compact_dict(inverter)

    for k in ("inverter_id", "name", "label", "model", "id"):
        if k in d and d[k] not in (None, ""):
            return str(d[k])

    ac = d.get("AC_output")
    pv = d.get("DC_solar_panels")
    bat = d.get("DC_battery")

    parts = []
    if ac is not None:
        parts.append(f"AC {float(ac):g}")
    if pv is not None:
        parts.append(f"PV {float(pv):g}")
    if bat is not None:
        parts.append(f"BAT {float(bat):g}")

    if parts:
        return " | ".join(parts)

    return str(inverter)


def default_cost_transform(v: float) -> float:
    """Transform costs to a positive '€ cost' convention.

    Some older optimisers return NPV as a *negative* cashflow number.
    This helper converts negative values to positive cost magnitudes.
    """
    v = float(v)
    return -v if v < 0 else v


def get_optimisation_cost_curve_data(
    results: Sequence[Mapping[str, Any]],
    *,
    cost_metric: str = "npv_cost",
    cost_transform: Optional[Callable[[float], float]] = None,
    aggregate: Optional[str] = "min",
    contract_labeler: Optional[Callable[[Any], str]] = None,
    inverter_labeler: Optional[Callable[[Any], str]] = None,
    include_raw_objects: bool = False,
) -> pd.DataFrame:
    """Return a tidy DataFrame for plotting optimisation cost curves.

    Supports results from:
      - FinancialModel.optimise_components()
        (keys: 'solar','battery','inverter','contract', 'npv_cost', ...)
      - OptimizerRunner.grid_search()
        (keys: 'params', 'cost', 'metrics', ...)

    Output columns (always):
      - solar_panel_count (int)
      - cost (float)
      - contract (str)
      - inverter (str)

    If include_raw_objects=True, also returns:
      - solar, battery, inverter_obj, contract_obj
    """
    if cost_transform is None:
        cost_transform = default_cost_transform
    if contract_labeler is None:
        contract_labeler = default_contract_label
    if inverter_labeler is None:
        inverter_labeler = default_inverter_label

    records: list[dict[str, Any]] = []

    for r in results:
        if not isinstance(r, Mapping):
            continue

        params = r.get("params") if isinstance(r.get("params"), Mapping) else None

        solar = (params or r).get("solar")
        battery = (params or r).get("battery")
        inverter = (params or r).get("inverter")
        contract = (params or r).get("contract")

        panel_count = _get(solar, "solar_panel_count")
        if panel_count is None:
            panel_count = _get(solar, "panel_count")
        if panel_count is None:
            continue

        cost_val = r.get(cost_metric)
        if cost_val is None:
            cost_val = r.get("cost")
        if cost_val is None and isinstance(r.get("metrics"), Mapping):
            m = r["metrics"]
            cost_val = (
                m.get(cost_metric)
                or m.get("npv_cost")
                or m.get("npv")
                or m.get("annual_cost_year1")
            )
        if cost_val is None:
            continue

        try:
            cost = float(cost_transform(float(cost_val)))
        except Exception:
            continue

        rec: dict[str, Any] = {
            "solar_panel_count": int(panel_count),
            "cost": float(cost),
            "contract": contract_labeler(contract),
            "inverter": inverter_labeler(inverter),
        }

        if include_raw_objects:
            rec.update(
                {
                    "solar": solar,
                    "battery": battery,
                    "inverter_obj": inverter,
                    "contract_obj": contract,
                }
            )

        records.append(rec)

    df = pd.DataFrame.from_records(records)
    if df.empty:
        return pd.DataFrame(columns=["solar_panel_count", "cost", "contract", "inverter"])

    if aggregate:
        df = (
            df.groupby(["solar_panel_count", "contract", "inverter"], as_index=False)["cost"]
            .agg(aggregate)
            .sort_values(["inverter", "contract", "solar_panel_count"], kind="stable")
            .reset_index(drop=True)
        )

    return df





Agg = Union[str, Callable[[pd.Series], float]]


def _default_contract_label(contract: Any) -> str:
    """Reasonable short label for ElectricityContract-like objects."""
    if contract is None:
        return "Unknown contract"
    supplier = getattr(contract, "supplier", None)
    product = getattr(contract, "product_name", None)
    ctype = getattr(contract, "contract_type", None)

    parts = [p for p in (supplier, product, ctype) if p]
    if parts:
        return " – ".join(map(str, parts))
    return str(contract)


def _default_inverter_label(inverter: Any) -> str:
    if inverter is None or inverter == "":
        return "default"
    return str(inverter)


def get_contract_comparison_data(
    results: Sequence[Mapping[str, Any]],
    *,
    cost_metric: str = "annual_cost_year1",
    cost_transform: Optional[Callable[[float], float]] = None,
    contract_labeler: Optional[Callable[[Any], str]] = None,
    inverter_labeler: Optional[Callable[[Any], str]] = None,
) -> pd.DataFrame:
    """
    Builds a tidy dataframe suitable for contract comparison plots.

    Expected (best effort) from each `result` mapping:
      - solar_panel_count (or n_solar_panels / solar_panels)
      - inverter (optional)
      - contract
      - cost metric: result[cost_metric] OR breakdown['total_cost'] OR result['annual_cost_year1']
      - breakdown consumption keys: consumption_kWh OR (consumption_peak_kWh + consumption_offpeak_kWh)
      - breakdown fixed keys: fixed_component + data_management_cost + capacity_cost (any missing treated as 0)
    """
    rows = []
    for r in results:
        bd = r.get("breakdown") or {}

        sp = r.get("solar_panel_count", r.get("n_solar_panels", r.get("solar_panels", np.nan)))

        inverter_obj = r.get("inverter", r.get("inverter_id", r.get("inverter_type", None)))
        inverter = (
            inverter_labeler(inverter_obj)
            if inverter_labeler is not None
            else _default_inverter_label(inverter_obj)
        )

        contract_obj = r.get("contract", None)
        contract = (
            contract_labeler(contract_obj)
            if contract_labeler is not None
            else _default_contract_label(contract_obj)
        )

        # Cost
        cost = r.get(cost_metric, None)
        if cost is None:
            cost = bd.get("total_cost", None)
        if cost is None:
            cost = r.get("annual_cost_year1", None)

        if cost is not None and cost_transform is not None:
            try:
                cost = cost_transform(float(cost))
            except Exception:
                cost = np.nan

        # Consumption
        cons = r.get("consumption_kWh", None)
        if cons is None:
            cons = bd.get("consumption_kWh", None)
        if cons is None:
            peak = bd.get("consumption_peak_kWh", None)
            off = bd.get("consumption_offpeak_kWh", None)
            if peak is None and off is None:
                cons = np.nan
            else:
                cons = float(peak or 0.0) + float(off or 0.0)

        # Fixed cost (best-effort)
        fixed_cost = 0.0
        any_fixed_key = False
        for k in ("fixed_component", "data_management_cost", "capacity_cost"):
            v = bd.get(k, None)
            if v is not None:
                any_fixed_key = True
                try:
                    fixed_cost += float(v)
                except Exception:
                    pass
        if not any_fixed_key:
            fixed_cost = np.nan

        rows.append(
            {
                "solar_panel_count": sp,
                "consumption_kWh": cons,
                "cost": cost,
                "contract": contract,
                "inverter": inverter,
                "fixed_cost": fixed_cost,
            }
        )

    return pd.DataFrame(rows)


def get_contract_comparison_curves(
    data: pd.DataFrame,
    *,
    cost_aggregate: Agg = "min",
    consumption_aggregate: Agg = "mean",
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Returns (cost_curve_df, consumption_curve_df)."""
    required = {"solar_panel_count", "cost", "contract", "consumption_kWh"}
    missing = required.difference(set(data.columns))
    if missing:
        raise ValueError(f"Missing required columns in `data`: {sorted(missing)}")

    df = data.copy()
    df["solar_panel_count"] = pd.to_numeric(df["solar_panel_count"], errors="coerce")
    df["cost"] = pd.to_numeric(df["cost"], errors="coerce")
    df["consumption_kWh"] = pd.to_numeric(df["consumption_kWh"], errors="coerce")
    df["contract"] = df["contract"].astype(str)

    cost_df = df.dropna(subset=["cost", "contract"])
    if cost_df.empty:
        raise ValueError("No rows to plot cost after cleaning (solar_panel_count/cost/contract).")

    cost_curve = (
        cost_df.groupby(["solar_panel_count", "contract"], as_index=False)["cost"]
        .agg(cost_aggregate)
        .rename(columns={"cost": "cost"})
    )

    cons_df = df.dropna(subset=["solar_panel_count", "consumption_kWh"])
    consumption_curve = (
        cons_df.groupby(["solar_panel_count"], as_index=False)["consumption_kWh"]
        .agg(consumption_aggregate)
        .rename(columns={"consumption_kWh": "consumption_kWh"})
    )

    return cost_curve, consumption_curve


def get_contract_comparison_summary_table(
    data: pd.DataFrame,
    *,
    cost_aggregate: Agg = "min",
    select: str = "min_cost",  # min_cost | max_cost | first
    solar_panel_count: Optional[float] = None,  # if set, pick (nearest) panel count for all contracts
) -> pd.DataFrame:
    """
    Returns a WIDE table with contracts as columns.
    Rows:
      - Solar panels (count)
      - Fixed cost (€)
      - Total cost (€)  (same 'cost' used in plotting)
    """
    required = {"solar_panel_count", "cost", "contract", "fixed_cost"}
    missing = required.difference(set(data.columns))
    if missing:
        raise ValueError(f"Missing required columns in `data`: {sorted(missing)}")

    df = data.copy()
    df["solar_panel_count"] = pd.to_numeric(df["solar_panel_count"], errors="coerce")
    df["cost"] = pd.to_numeric(df["cost"], errors="coerce")
    df["fixed_cost"] = pd.to_numeric(df["fixed_cost"], errors="coerce")
    df["contract"] = df["contract"].astype(str)

    # Collapse duplicates from e.g. multiple inverters per (contract, solar_panel_count)
    agg_df = (
        df.dropna(subset=["contract", "solar_panel_count", "cost"])
        .groupby(["contract", "solar_panel_count"], as_index=False)
        .agg(cost=("cost", cost_aggregate), fixed_cost=("fixed_cost", "first"))
    )
    if agg_df.empty:
        raise ValueError("No rows available to build summary table after cleaning/aggregation.")

    if solar_panel_count is not None:
        uniques = np.array(sorted(agg_df["solar_panel_count"].dropna().unique().tolist()))
        if uniques.size == 0:
            raise ValueError("No valid solar_panel_count values found for summary selection.")
        nearest = float(uniques[np.abs(uniques - float(solar_panel_count)).argmin()])
        sel = agg_df[agg_df["solar_panel_count"] == nearest].copy()
        # If some contracts don't exist at that count, keep them out (better than inventing).
    else:
        if select == "min_cost":
            idx = agg_df.groupby("contract")["cost"].idxmin()
            sel = agg_df.loc[idx].copy()
        elif select == "max_cost":
            idx = agg_df.groupby("contract")["cost"].idxmax()
            sel = agg_df.loc[idx].copy()
        elif select == "first":
            sel = (
                agg_df.sort_values(["contract", "solar_panel_count"])
                .groupby("contract", as_index=False)
                .first()
            )
        else:
            raise ValueError("select must be one of: 'min_cost', 'max_cost', 'first'")

    # Sort contracts by total cost (nice in the table)
    sel = sel.sort_values("cost", ascending=True)

    table = pd.DataFrame(
        {
            row["contract"]: {
                "Solar panels (count)": row["solar_panel_count"],
                "Fixed cost (€)": row["fixed_cost"],
                "Total cost (€)": row["cost"],
            }
            for _, row in sel.iterrows()
        }
    )
    return table
