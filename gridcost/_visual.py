
from pyparsing import Optional

import pandas as pd
from typing import Union


def _prepare_tariff_columns(self, tariffs: list[str] = None) -> list[str]:
    """
    Ensure that tariff columns for the requested tariff names exist on ``self.pd``.

    Parameters
    ----------
    tariffs:
        List of tariff labels to prepare. Supported values:
        - "DualTariff"
        - "DynamicTariff"

        If ``None``, the method will infer a sensible default:
        * If an ``electricity_contract`` is set, it will include "DualTariff".
        * If a ``BelpexFilter`` column is present, it will include "DynamicTariff".

    Returns
    -------
    List of tariff labels that are available on ``self.pd`` after this call.
    """
    if tariffs is None:
        tariffs = []
        if self.electricity_contract is not None:
            tariffs.append("DualTariff")
        if "BelpexFilter" in self.pd.columns:
            tariffs.append("DynamicTariff")

    # De-duplicate while preserving order
    seen: set[str] = set()
    clean_tariffs: list[str] = []
    for t in tariffs:
        if t not in seen:
            clean_tariffs.append(t)
            seen.add(t)

    available: list[str] = []
    for t in clean_tariffs:
        if t == "DualTariff":
            if "DualTariff" not in self.pd.columns:
                # May raise if no contract attached; let it bubble up
                self.dual_tariff()
            available.append("DualTariff")
        elif t == "DynamicTariff":
            if "DynamicTariff" not in self.pd.columns:
                # May raise if no BelpexFilter data attached
                self.dynamic_tariff()
            available.append("DynamicTariff")
        else:
            raise ValueError(f"Unsupported tariff label: {t!r}")

    if not available:
        raise ValueError(
            "No tariff columns could be prepared. "
            "Attach an ElectricityContract and/or Belpex data or "
            "pass an explicit list of tariffs."
        )

    return available

def get_consumption_and_cost_timeseries(
    self,
    *,
    tariffs: list[str] = None,
    start: Union[str, "pd.Timestamp"] = None,
    end: Union[str, "pd.Timestamp"] = None,
) -> "pd.DataFrame":
    """
    Build a DataFrame with consumption-from-grid and cost time series.

    The returned DataFrame uses the internal index (DateTime) and contains:

    - ``Consumption_kW``: positive values representing power taken *from*
        the grid (in kW, based on negative ``GridFlow`` values).
    - One column per requested tariff, e.g. ``DualTariff`` and/or
        ``DynamicTariff`` with the cost per time step (in EUR).
    """
    if "GridFlow" not in self.pd.columns:
        raise ValueError("GridFlow column missing from dataset.")

    # Make sure the required tariff columns exist on self.pd
    tariffs_available = self._prepare_tariff_columns(tariffs)

    df = self.pd.copy()

    # Optional time window
    if start is not None or end is not None:
        df = df.loc[start:end]

    # Consumption from the grid: only negative GridFlow values, made positive
    consumption = df["GridFlow"].copy()
    consumption[consumption > 0] = 0.0  # ignore injection
    consumption_kW = -consumption

    result_cols = {"Consumption_kW": consumption_kW}
    for t in tariffs_available:
        result_cols[t] = df[t]

    result = pd.DataFrame(result_cols, index=df.index)
    return result

def plot_consumption_and_cost(
    self,
    *,
    tariffs: list[str] = None,
    start: Union[str, "pd.Timestamp"] = None,
    end: Union[str, "pd.Timestamp"] = None,
    rolling: int = None,
    show: bool = True,
):
    """
    Plot electricity consumption and cost time series on a single figure.

    The plot uses:

    - left y-axis: ``Consumption_kW`` (kW from the grid)
    - right y-axis: cost per time step for each requested tariff
        (e.g. DualTariff, DynamicTariff).

    Parameters
    ----------
    tariffs:
        List of tariff labels to plot. If ``None``, a sensible default is
        inferred (see ``_prepare_tariff_columns``). Supported values:
        "DualTariff" and "DynamicTariff".
    start, end:
        Optional bounds on the DateTime index.
    rolling:
        Optional window size (in number of time steps) to apply a simple
        moving average to both consumption and cost series to smooth the
        plot. If ``None`` or ``1``, no smoothing is applied.
    show:
        If ``True`` (default), ``matplotlib.pyplot.show()`` is called
        before returning.

    Returns
    -------
    matplotlib.figure.Figure
        The created matplotlib figure.
    """
    try:
        import matplotlib.pyplot as plt  # type: ignore
    except ImportError as exc:
        raise RuntimeError(
            "matplotlib is required for 'plot_consumption_and_cost'. "
            "Install it with 'pip install matplotlib'."
        ) from exc

    ts = self.get_consumption_and_cost_timeseries(
        tariffs=tariffs,
        start=start,
        end=end,
    )

    # Apply optional smoothing
    if rolling is not None and rolling > 1:
        ts = ts.rolling(rolling, min_periods=1).mean()

    fig, ax1 = plt.subplots(figsize=(12, 5))

    # Left axis: consumption
    ax1.plot(ts.index, ts["Consumption_kW"], label="Consumption from grid [kW]")
    ax1.set_xlabel("Time")
    ax1.set_ylabel("Power from grid [kW]")
    ax1.tick_params(axis="y")

    # Right axis: one line per tariff
    ax2 = ax1.twinx()
    for t in ts.columns:
        if t == "Consumption_kW":
            continue
        ax2.plot(ts.index, ts[t], linestyle="--", label=f"{t} cost [€/interval]")
    ax2.set_ylabel("Cost [€ per interval]")
    ax2.tick_params(axis="y")

    # Combine legends from both axes
    lines_1, labels_1 = ax1.get_legend_handles_labels()
    lines_2, labels_2 = ax2.get_legend_handles_labels()
    ax1.legend(lines_1 + lines_2, labels_1 + labels_2, loc="upper left")

    fig.tight_layout()

    if show:
        plt.show()

    return fig
