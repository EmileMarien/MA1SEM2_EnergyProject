# TODO: generate charts for grid cost analysis that allow to visualize cost of different contracts.
"""Visualisations for optimisation outputs.

The heavy lifting to *extract/aggregate* plot-ready data lives in
:mod:`financialmodel._getters`.
"""

from __future__ import annotations

from typing import Any, Callable, Mapping, Optional, Sequence, Tuple

import pandas as pd
import itertools
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec

from financialmodel._getters import (
    get_contract_comparison_data,
    get_contract_comparison_curves,
    get_contract_comparison_summary_table,
)
def plot_contract_comparison_cost_and_consumption(
    self,
    *,
    results=None,
    data=None,
    cost_metric: str = "annual_cost_year1",
    cost_transform=None,
    show_belpex: bool = False,
    show_consumption: bool = True,  #TODO: incorporate
    cost_aggregate: str = "min",
    consumption_aggregate: str = "mean",
    contract_labeler=None,
    inverter_labeler=None,
    table_select: str = "min_cost",          # min_cost | max_cost | first
    table_solar_panel_count=None,            # pick a fixed panel count for the table (nearest match)
    title: str | None = None,
    xlabel: str = "Solar panels (count)",
    consumption_ylabel: str = "Electricity consumption (kWh)",
    cost_ylabel: str = "Cost (€)",
    show: bool = True,
):
    """
    Plots:
      - Consumption vs solar panels (left y-axis)
      - Cost vs solar panels per contract (right y-axis)
      - Summary table under the plot (contracts as columns)
    """


    if data is None:
        if results is None:
            raise ValueError("Provide either `results` or `data`.")
        data = get_contract_comparison_data(
            results,
            cost_metric=cost_metric,
            cost_transform=cost_transform,
            contract_labeler=contract_labeler,
            inverter_labeler=inverter_labeler,
        )

    cost_curve, cons_curve = get_contract_comparison_curves(
        data,
        cost_aggregate=cost_aggregate,
        consumption_aggregate=consumption_aggregate,
    )

    summary = get_contract_comparison_summary_table(
        data,
        cost_aggregate=cost_aggregate,
        select=table_select,
        solar_panel_count=table_solar_panel_count,
    )

    # Layout: plot on top, table below
    fig = plt.figure(figsize=(12, 8))
    gs = GridSpec(nrows=2, ncols=1, height_ratios=[3, 1], figure=fig)
    ax = fig.add_subplot(gs[0])
    ax_tbl = fig.add_subplot(gs[1])
    ax_tbl.axis("off")

    # Consumption line (left axis)
    if not cons_curve.empty:
        cons_curve = cons_curve.sort_values("solar_panel_count")
        ax.plot(
            cons_curve["solar_panel_count"],
            cons_curve["consumption_kWh"],
            marker="o",
            linewidth=2,
            label="Consumption",
        )

    ax.set_xlabel(xlabel)
    ax.set_ylabel(consumption_ylabel)
    ax.grid(True, alpha=0.25)
    ax.set_title(title or "Consumption & contract cost vs solar panels")

    # Cost lines per contract (right axis)
    ax_cost = ax.twinx()
    ax_cost.set_ylabel(cost_ylabel)

    contracts = sorted(cost_curve["contract"].astype(str).unique().tolist())

    base_colors = plt.rcParams.get("axes.prop_cycle", None)
    if base_colors is not None:
        base_colors = base_colors.by_key().get("color", [])
    base_colors = base_colors or [f"C{i}" for i in range(10)]

    color_cycle = itertools.cycle(base_colors)
    color_by_contract = {c: next(color_cycle) for c in contracts}

    line_styles = ["-", "--", ":", "-."]
    style_cycle = itertools.cycle(line_styles)
    style_by_contract = {c: next(style_cycle) for c in contracts}

    for c in contracts:
        sub = cost_curve[cost_curve["contract"].astype(str) == c].sort_values("solar_panel_count")
        ax_cost.plot(
            sub["solar_panel_count"],
            sub["cost"],
            linestyle=style_by_contract[c],
            color=color_by_contract[c],
            marker="o",
            linewidth=2,
            label=f"Cost — {c}",
        )

    # Combined legend
    h1, l1 = ax.get_legend_handles_labels()
    h2, l2 = ax_cost.get_legend_handles_labels()
    ax_cost.legend(h1 + h2, l1 + l2, loc="upper right")

    # Table formatting (wide: contracts as columns)
    table_fmt = summary.copy()

    def _fmt_cell(row_name: str, v):
        if pd.isna(v):
            return ""
        if "Solar panels" in row_name:
            return str(int(round(float(v))))
        return f"{float(v):,.2f}"

    for r in table_fmt.index:
        table_fmt.loc[r] = table_fmt.loc[r].map(lambda v, rr=r: _fmt_cell(rr, v))

    tbl = ax_tbl.table(
        cellText=table_fmt.values,
        rowLabels=table_fmt.index.tolist(),
        colLabels=table_fmt.columns.tolist(),
        cellLoc="center",
        rowLoc="center",
        loc="center",
    )
    tbl.auto_set_font_size(False)
    tbl.set_fontsize(10)
    tbl.scale(1.0, 1.4)

    fig.tight_layout()
    if show:
        plt.show()

    return fig, (ax, ax_cost, ax_tbl)

def plot_optimisation_cost_vs_solar_panels(
    self,
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
