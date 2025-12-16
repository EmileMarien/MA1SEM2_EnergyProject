
"""Data getters / transformers for visualisations.

This module contains *pure* helper functions that turn optimisation outputs
into tidy pandas DataFrames.

The plotting code lives in :mod:`financialmodel._visuals`.
"""

from __future__ import annotations

from dataclasses import asdict, is_dataclass
from typing import Any, Callable, Mapping, Optional, Sequence

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
