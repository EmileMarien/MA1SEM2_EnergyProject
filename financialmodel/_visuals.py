# TODO: generate charts for grid cost analysis that allow to visualize cost of different contracts.
"""Visualisations for optimisation outputs.

The heavy lifting to *extract/aggregate* plot-ready data lives in
:mod:`financialmodel._getters`.
"""

from __future__ import annotations

from typing import Any, Callable, Mapping, Optional, Sequence, Tuple

import pandas as pd


def plot_optimisation_cost_vs_solar_panels(
    *,
    results: Optional[Sequence[Mapping[str, Any]]] = None,
    data: Optional[pd.DataFrame] = None,
    cost_metric: str = "npv_cost",
    cost_transform: Optional[Callable[[float], float]] = None,
    aggregate: Optional[str] = "min",
    contract_labeler: Optional[Callable[[Any], str]] = None,
    inverter_labeler: Optional[Callable[[Any], str]] = None,
    title: Optional[str] = None,
    xlabel: str = "Solar panels (count)",
    ylabel: str = "Cost (€)",
    ax=None,
    show: bool = True,
) -> Tuple[Any, Any]:
    """Line chart of cost vs solar panel count.

    Encoding:
      - Contract  -> line style
      - Inverter  -> color
    """
    import itertools
    import matplotlib.pyplot as plt
    from matplotlib.lines import Line2D

    if data is None:
        if results is None:
            raise ValueError("Provide either `results` or `data`.")
        from financialmodel._getters import get_optimisation_cost_curve_data

        data = get_optimisation_cost_curve_data(
            results,
            cost_metric=cost_metric,
            cost_transform=cost_transform,
            aggregate=aggregate,
            contract_labeler=contract_labeler,
            inverter_labeler=inverter_labeler,
        )

    required = {"solar_panel_count", "cost", "contract", "inverter"}
    missing = required.difference(set(data.columns))
    if missing:
        raise ValueError(f"Missing required columns in `data`: {sorted(missing)}")

    df = data.copy()
    df["solar_panel_count"] = pd.to_numeric(df["solar_panel_count"], errors="coerce")
    df["cost"] = pd.to_numeric(df["cost"], errors="coerce")
    df = df.dropna(subset=["solar_panel_count", "cost", "contract", "inverter"])
    if df.empty:
        raise ValueError("No rows to plot after cleaning the input data.")

    inverters = sorted(df["inverter"].astype(str).unique().tolist())
    contracts = sorted(df["contract"].astype(str).unique().tolist())

    base_colors = plt.rcParams.get("axes.prop_cycle", None)
    if base_colors is not None:
        base_colors = base_colors.by_key().get("color", [])
    base_colors = base_colors or ["C0", "C1", "C2", "C3", "C4", "C5", "C6", "C7", "C8", "C9"]

    color_cycle = itertools.cycle(base_colors)
    color_by_inverter = {inv: next(color_cycle) for inv in inverters}

    line_styles = ["-", "--", ":", "-."]
    style_cycle = itertools.cycle(line_styles)
    style_by_contract = {c: next(style_cycle) for c in contracts}

    if ax is None:
        fig, ax = plt.subplots(figsize=(10, 6))
    else:
        fig = ax.figure

    for inv in inverters:
        for c in contracts:
            sub = df[(df["inverter"].astype(str) == inv) & (df["contract"].astype(str) == c)]
            if sub.empty:
                continue
            sub = sub.sort_values("solar_panel_count")
            ax.plot(
                sub["solar_panel_count"],
                sub["cost"],
                linestyle=style_by_contract[c],
                color=color_by_inverter[inv],
                marker="o",
                linewidth=2,
            )

    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.grid(True, alpha=0.25)
    ax.set_title(title or "Optimisation cost vs solar panels")

    inverter_handles = [
        Line2D([0], [0], color=color_by_inverter[inv], lw=2, linestyle="-", label=str(inv))
        for inv in inverters
    ]
    contract_handles = [
        Line2D([0], [0], color="black", lw=2, linestyle=style_by_contract[c], label=str(c))
        for c in contracts
    ]

    leg1 = ax.legend(handles=inverter_handles, title="Inverter", loc="upper right")
    ax.add_artist(leg1)
    ax.legend(handles=contract_handles, title="Contract", loc="upper left")

    fig.tight_layout()
    if show:
        plt.show()

    return fig, ax
