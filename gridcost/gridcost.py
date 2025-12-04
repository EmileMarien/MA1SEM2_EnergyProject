import logging
from pathlib import Path
from typing import Optional, Union

import pandas as pd

from financialmodel.models import ElectricityContract
import gridcost._dualtariff
import gridcost._capacitytariff
import gridcost._dynamictariff 


logger = logging.getLogger(__name__)


class GridCost:
    """
    Handle grid cost data preparation and cost calculation, including:
    - Loading consumption data from a DataFrame or CSV
    - Optional merge with BelpexFilter data from Excel
    - Resampling and interpolation
    - Tariff application and total cost calculation
    """

    def __init__(
        self,
        *,
        consumption_data_df: Optional[pd.DataFrame] = None,
        consumption_data_csv: str = "",
        file_path_BelpexFilter: str = "",
        resample_freq: str = "1h",
        belpex_scale: float = 1.1261,
        electricity_contract: Optional[ElectricityContract] = None,
    ) -> None:
        # Store simple attributes
        self.resample_freq = resample_freq
        self.belpex_scale = belpex_scale
        self.electricity_contract = electricity_contract

        # --- 1. Load base consumption dataframe ---------------------------------
        dataframe = self._load_consumption_data(consumption_data_df, consumption_data_csv)

        # --- 2. Optionally merge BelpexFilter data ------------------------------
        dataframe = self._merge_belpex_filter(dataframe, file_path_BelpexFilter)

        # --- 3. Final cleaning / checks -----------------------------------------
        self._validate_required_columns(dataframe, required_columns=["GridFlow"])

        # Ensure DateTime column exists and is datetime
        if "DateTime" not in dataframe.columns:
            raise ValueError("Expected a 'DateTime' column in the input data.")
        dataframe["DateTime"] = pd.to_datetime(dataframe["DateTime"])

        # Set index to DateTime
        dataframe = dataframe.set_index("DateTime").sort_index()

        # Log duplicate index entries
        dup_idx = dataframe.index[dataframe.index.duplicated(keep=False)]
        if not dup_idx.empty:
            logger.debug(
                "Duplicate DateTime index entries found: %s",
                dup_idx.unique().tolist(),
            )

        # Infer dtypes
        dataframe = dataframe.infer_objects()

        # --- 4. Resample + interpolate ------------------------------------------
        dataframe = self._resample_and_interpolate(dataframe)

        # Final result
        self.pd = dataframe

    # -------------------------------------------------------------------------
    # Internal helpers
    # -------------------------------------------------------------------------
    def _load_consumption_data(
        self,
        consumption_data_df: Optional[pd.DataFrame],
        consumption_data_csv: str,
    ) -> pd.DataFrame:
        """Load and normalize the base consumption data."""
        if consumption_data_df is not None and not consumption_data_df.empty:
            df = consumption_data_df.copy()
            logger.debug("Using provided consumption_data_df with shape %s", df.shape)

            # Normalize accepted forms:
            if isinstance(df, pd.Series):
                df = df.to_frame(name="GridFlow")

            # If GridFlow column exists, keep only it (and DateTime if present)
            if "GridFlow" in df.columns:
                cols = [c for c in ["DateTime", "GridFlow"] if c in df.columns]
                df = df[cols]
            else:
                # Fall back to first numeric column as GridFlow
                numeric_cols = df.select_dtypes(include="number").columns
                if len(numeric_cols) == 0:
                    raise ValueError("No numeric data found to use as 'GridFlow'.")
                df = df[[numeric_cols[0]]].rename(columns={numeric_cols[0]: "GridFlow"})

            # Ensure index or column for DateTime
            if "DateTime" not in df.columns:
                if isinstance(df.index, pd.DatetimeIndex):
                    df = df.reset_index().rename(columns={"index": "DateTime"})
                else:
                    raise ValueError(
                        "Consumption DataFrame must have a DatetimeIndex or a 'DateTime' column."
                    )

            return df

        if consumption_data_csv:
            path = Path(consumption_data_csv)
            if not path.is_file():
                raise FileNotFoundError(f"Consumption CSV file not found: {path}")

            logger.debug("Reading consumption data from CSV: %s", path)

            # 1) Read the CSV without nested parse_dates (avoids the FutureWarning)
            raw = pd.read_csv(path, sep=";", dayfirst=True)

            # 2) Build Start/End timestamps explicitly
            raw["Start"] = pd.to_datetime(
                raw["Start Date"].astype(str) + " " + raw["Start Time"].astype(str),
                dayfirst=True,
                errors="coerce",
            )
            raw["End"] = pd.to_datetime(
                raw["End Date"].astype(str) + " " + raw["End Time"].astype(str),
                dayfirst=True,
                errors="coerce",
            )

            df = raw.rename(columns={"Start": "DateTime"})

            # Make sure Volume is numeric if present
            if "Volume" in df.columns:
                df["Volume"] = pd.to_numeric(df["Volume"], errors="coerce")

            # Basic sanity check
            if "DateTime" not in df.columns:
                raise ValueError(
                    "CSV input must contain 'Start Date' and 'Start Time' columns."
                )

            # 3) If a GridFlow-like column already exists, use it
            if "GridFlow" in df.columns:
                cols = ["DateTime", "GridFlow"]
                df = df[cols]
            else:
                # Try to derive GridFlow from Volume/Register if available
                if "Volume" in df.columns and "Register" in df.columns:
                    reg = df["Register"].astype(str)

                    off_mask = reg.str.contains("offtake", case=False) | reg.str.contains(
                        "consumption", case=False
                    )
                    inj_mask = reg.str.contains("injection", case=False)

                    if off_mask.any() or inj_mask.any():
                        # positive for offtake (consumption), negative for injection (export)
                        df["SignedVolume"] = 0.0
                        df.loc[off_mask, "SignedVolume"] = df.loc[off_mask, "Volume"].astype(float)
                        df.loc[inj_mask, "SignedVolume"] = -df.loc[inj_mask, "Volume"].astype(float)

                        # Sum by timestamp to get net flow
                        df = (
                            df.groupby("DateTime", as_index=False)["SignedVolume"]
                            .sum()
                            .rename(columns={"SignedVolume": "GridFlow"})
                        )
                    else:
                        # Just treat Volume as GridFlow if we have no idea what Register means
                        df = (
                            df.groupby("DateTime", as_index=False)["Volume"]
                            .sum()
                            .rename(columns={"Volume": "GridFlow"})
                        )
                else:
                    # Fallback: try any power/flow-like column
                    candidate_cols = [
                        c for c in df.columns if "flow" in c.lower() or "power" in c.lower()
                    ]
                    if candidate_cols:
                        df = df.rename(columns={candidate_cols[0]: "GridFlow"})
                        df = df[["DateTime", "GridFlow"]]
                    else:
                        raise ValueError(
                            "CSV must contain either 'Volume' (+ 'Register') or a "
                            "'GridFlow' / power-like column."
                        )

            logger.debug("Loaded consumption data from CSV with shape %s", df.shape)
            return df

        raise ValueError(
            "You must provide either a non-empty `consumption_data_df` or a `consumption_data_csv` path."
        )


    def _merge_belpex_filter(
        self,
        dataframe: pd.DataFrame,
        file_path_BelpexFilter: str,
    ) -> pd.DataFrame:
        """Optionally merge BelpexFilter data and scale it."""
        if not file_path_BelpexFilter:
            dataframe["BelpexFilter"] = None
            logger.debug("No BelpexFilter file provided; 'BelpexFilter' set to None.")
            return dataframe

        path = Path(file_path_BelpexFilter)
        if not path.is_file():
            raise FileNotFoundError(f"BelpexFilter Excel file not found: {path}")
        if path.suffix.lower() != ".xlsx":
            raise ValueError("BelpexFilter file must be an .xlsx Excel file.")

        logger.debug("Reading BelpexFilter data from Excel: %s", path)
        belpex_df = pd.read_excel(path)

        if "DateTime" not in belpex_df.columns:
            raise ValueError("'DateTime' column not found in the Belpex Excel file.")
        belpex_df["DateTime"] = pd.to_datetime(belpex_df["DateTime"])

        belpex_df = belpex_df.infer_objects()

        merged_df = pd.merge(belpex_df, dataframe, on="DateTime", how="right")

        # Scale BelpexFilter if present
        if "BelpexFilter" in merged_df.columns:
            merged_df["BelpexFilter"] = merged_df["BelpexFilter"] * self.belpex_scale
            logger.debug("BelpexFilter column scaled by factor %s", self.belpex_scale)
        else:
            merged_df["BelpexFilter"] = None
            logger.debug("BelpexFilter column not in Excel; created as None.")

        return merged_df

    @staticmethod
    def _validate_required_columns(df: pd.DataFrame, required_columns: list[str]) -> None:
        missing = [col for col in required_columns if col not in df.columns]
        if missing:
            raise ValueError(f"The following required columns are missing: {', '.join(missing)}")

    def _resample_and_interpolate(self, df: pd.DataFrame) -> pd.DataFrame:
        """Resample the dataframe and interpolate missing values."""
        try:
            logger.debug("Resampling dataframe with frequency %s", self.resample_freq)
            df_resampled = df.resample(self.resample_freq).mean()
        except Exception as exc:  # noqa: BLE001
            logger.warning(
                "Resampling with %s failed (%s). Falling back to 1h.",
                self.resample_freq,
                exc,
            )
            df_resampled = df.resample("1h").mean()

        df_resampled = df_resampled.interpolate(method="linear")
        return df_resampled

    # ---------------------------------------------------------------------
    # Energy totals (kWh)
    # ---------------------------------------------------------------------
    def get_total_injection_and_consumption(self) -> tuple[float, float, float, float]:
        """Compute total injection/consumption split (peak/off-peak) in kWh.

        Returns a tuple:
            (injection_peak_kWh, injection_offpeak_kWh,
             consumption_peak_kWh, consumption_offpeak_kWh)

        Convention:
          - positive GridFlow: injecting to the grid
          - negative GridFlow: consuming from the grid
        """
        if "GridFlow" not in self.pd.columns:
            raise ValueError("GridFlow column missing from dataset")

        series = self.pd["GridFlow"]
        idx = series.index

        # Masks for peak vs off-peak (weekdays 7:00-22:00 are peak)
        weekday_mask = idx.weekday < 5
        peak_hours_mask = (idx.hour >= 7) & (idx.hour < 22)
        peak_mask = weekday_mask & peak_hours_mask
        offpeak_mask = ~peak_mask

        inject = series > 0
        consume = series < 0

        injection_peak = series[inject & peak_mask].sum()
        injection_offpeak = series[inject & offpeak_mask].sum()
        consumption_peak = -series[consume & peak_mask].sum()
        consumption_offpeak = -series[consume & offpeak_mask].sum()

        # Integrate power over time to energy [kWh]
        try:
            interval_hours = pd.Timedelta(idx.freq).total_seconds() / 3600.0
        except Exception:
            diffs = pd.Series(idx).diff().dropna()
            interval_hours = pd.to_timedelta(diffs.median()).total_seconds() / 3600.0

        return (
            injection_peak * interval_hours,
            injection_offpeak * interval_hours,
            consumption_peak * interval_hours,
            consumption_offpeak * interval_hours,
        )

    # ---------------------------------------------------------------------
    # Total cost calculation
    # ---------------------------------------------------------------------

        
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


    def calculate_total_cost(
        self,
        *,
        tariff: Optional[str] = None,
        return_breakdown: bool = False,
    ) -> Union[float, dict]:
        """
        Calculate the total yearly electricity cost.

        If `tariff` is None, uses `electricity_contract.contract_type` if provided,
        else defaults to "DynamicTariff".

        By default returns a single float (total_cost).
        If `return_breakdown=True`, returns a dict with components.
        """
        c = self.electricity_contract

        # Select tariff
        tariff_label = (
            tariff
            or (c.contract_type if c is not None else None)
            or "DynamicTariff"
        )

        # Ensure tariffs columns exist
        if tariff_label == "DualTariff":
            self.dual_tariff()
        elif tariff_label == "DynamicTariff":
            self.dynamic_tariff()
        else:
            raise ValueError(f"Unknown tariff type: {tariff_label}")

        # Energy cost as sum of chosen tariff column
        energy_cost = float(self.pd[tariff_label].sum())

        # Contract or fallback values
        if c is not None:
            data_management_cost = c.data_management_cost
            purchase_rate_injection = c.purchase_rate_injection
            purchase_rate_consumption = c.purchase_rate_consumption
            excise_duty_energy_contribution_rate = (
                c.excise_duty_energy_contribution_rate
            )
            fixed_component_dual = c.fixed_component_dual
            fixed_component_dynamic = c.fixed_component_dynamic
        else:
            data_management_cost = 13.95
            purchase_rate_injection = 0.00414453
            purchase_rate_consumption = 0.0538613
            excise_duty_energy_contribution_rate = 0.0503288 + 0.0020417
            fixed_component_dual = 111.3
            fixed_component_dynamic = 100.7

        fixed_component = (
            fixed_component_dual if tariff_label == "DualTariff" else fixed_component_dynamic
        )

        # Injection/consumption totals
        inj_peak, inj_offpeak, cons_peak, cons_offpeak = (
            self.get_total_injection_and_consumption()
        )

        # Purchase costs
        purchase_cost_injection = purchase_rate_injection * (inj_peak + inj_offpeak)
        purchase_cost_consumption = purchase_rate_consumption * (cons_peak + cons_offpeak)

        # Capacity cost
        try:
            capacity_cost = float(self.capacity_tariff())
        except Exception:
            capacity_cost = 0.0

        # Levy/excise based on total consumption
        levy_base_kWh = (cons_peak + cons_offpeak)
        levy_cost = excise_duty_energy_contribution_rate * levy_base_kWh

        total_cost = (
            energy_cost
            + data_management_cost
            + purchase_cost_injection
            + purchase_cost_consumption
            + capacity_cost
            + levy_cost
            + fixed_component
        )

        if not return_breakdown:
            return float(total_cost)

        return {
            "total_cost": float(total_cost),
            "energy_cost": float(energy_cost),
            "fixed_component": float(fixed_component),
            "data_management_cost": float(data_management_cost),
            "purchase_cost_injection": float(purchase_cost_injection),
            "purchase_cost_consumption": float(purchase_cost_consumption),
            "capacity_cost": float(capacity_cost),
            "levy_cost": float(levy_cost),
            "injection_peak_kWh": float(inj_peak),
            "injection_offpeak_kWh": float(inj_offpeak),
            "consumption_peak_kWh": float(cons_peak),
            "consumption_offpeak_kWh": float(cons_offpeak),
        }

    from gridcost._capacitytariff import capacity_tariff
    from gridcost._dualtariff import dual_tariff
    from gridcost._dynamictariff import dynamic_tariff
    