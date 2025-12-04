
import pandas as pd


def dynamic_tariff(self) -> None:
    """
    Calculates the dynamic tariff and fills the `DynamicTariff` column.
    Uses `BelpexFilter` prices.
    """
    if "BelpexFilter" not in self.pd.columns:
        raise ValueError(
            "BelpexFilter column missing. Provide file_path_BelpexFilter in GridCost init."
        )

    def calculate_tariff_row(row):
        grid_flow = row["GridFlow"]
        dynamic_cost = row["BelpexFilter"]  # €/MWh (assumption)

        if pd.isna(dynamic_cost):
            return 0.0

        if grid_flow < 0:  # consumption
            cost_per = ((0.1 * dynamic_cost + 1.1) * 1.06)  # cent per kWh
            cost = (-grid_flow) * cost_per  # cent total
        elif grid_flow > 0:  # injection
            cost_per = (0.1 * dynamic_cost - 0.905)  # cent per kWh (profit)
            cost = (-grid_flow) * cost_per  # cent total (negative)
        else:
            cost = 0.0

        return cost * 0.01  # convert cent to €

    self.pd["DynamicTariff"] = self.pd.apply(calculate_tariff_row, axis=1)
