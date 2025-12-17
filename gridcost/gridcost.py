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
        file_path_BelpexFilter: str = r"C:\Users\67583\OneDrive - Bain\Documents\Personal projects\MA1SEM2_EnergyProject\data\belpex_quarter_hourly.csv",
        resample_freq: str = "1h",
        electricity_contract: Optional[ElectricityContract] = None,
    ) -> None:
        # Store simple attributes
        self.resample_freq = resample_freq
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
        """Load and normalize the base consumption data.

        Supports:
        - Time-series: DateTime + GridFlow (or DatetimeIndex)
        - Supplier interval tables: Start Date/Time, End Date/Time, Register, Volume, Unit
            (e.g. one row for offtake and one row for injection per interval)

        Convention used throughout GridCost:
        - GridFlow < 0 : consumption (offtake)
        - GridFlow > 0 : injection

        If input provides interval energy (kWh per 15min), we convert to average kW by
        dividing by the interval length in hours.
        """

        def _norm_col(name: object) -> str:
            return (
                str(name)
                .strip()
                .lower()
                .replace("_", " ")
                .replace("-", " ")
            )

        def _find_col(df_: pd.DataFrame, *candidates: str) -> str | None:
            # Map normalised -> original (first wins)
            norm_map: dict[str, str] = {}
            for c in df_.columns:
                k = _norm_col(c)
                norm_map.setdefault(k, str(c))
            for cand in candidates:
                k = _norm_col(cand)
                if k in norm_map:
                    return norm_map[k]
            return None

        def _to_numeric_volume(s: pd.Series) -> pd.Series:
            # Handle both 0.01 and 0,01 formats.
            if pd.api.types.is_numeric_dtype(s):
                return s.astype(float)
            return pd.to_numeric(s.astype(str).str.replace(",", ".", regex=False), errors="coerce")

        def _unit_to_kwh_factor(unit_val: object) -> float:
            u = str(unit_val).strip().lower()
            if u in ("kwh",):
                return 1.0
            if u in ("wh",):
                return 1.0 / 1000.0
            if u in ("mwh",):
                return 1000.0
            # unknown: assume already kWh
            return 1.0

        def _derive_gridflow_from_interval_table(df_: pd.DataFrame) -> pd.DataFrame:
            """Handle CSV-like interval tables (Start Date/Time, End Date/Time, Register, Volume)."""
            start_date = _find_col(df_, "Start Date", "StartDate")
            start_time = _find_col(df_, "Start Time", "StartTime")
            end_date = _find_col(df_, "End Date", "EndDate")
            end_time = _find_col(df_, "End Time", "EndTime")

            # Build DateTime + EndTime if possible
            if start_date and start_time:
                start_dt = pd.to_datetime(
                    df_[start_date].astype(str) + " " + df_[start_time].astype(str),
                    dayfirst=True,
                    errors="coerce",
                )
            else:
                dt_col = _find_col(df_, "DateTime", "Datetime", "Timestamp", "Start")
                if not dt_col:
                    raise ValueError(
                        "Interval table must contain 'Start Date' + 'Start Time' or a 'DateTime' column."
                    )
                start_dt = pd.to_datetime(df_[dt_col], dayfirst=True, errors="coerce")

            end_dt = None
            if end_date and end_time:
                end_dt = pd.to_datetime(
                    df_[end_date].astype(str) + " " + df_[end_time].astype(str),
                    dayfirst=True,
                    errors="coerce",
                )

            vol_col = _find_col(df_, "Volume")
            if not vol_col:
                raise ValueError("Interval table must contain a 'Volume' column.")
            vol = _to_numeric_volume(df_[vol_col])

            # Convert to kWh based on Unit column if present
            unit_col = _find_col(df_, "Unit")
            if unit_col and df_[unit_col].notna().any():
                unit_val = df_.loc[df_[unit_col].notna(), unit_col].iloc[0]
                vol = vol * _unit_to_kwh_factor(unit_val)

            # Determine sign from Register if present
            reg_col = _find_col(df_, "Register")
            signed_energy = vol.copy()

            if reg_col:
                reg = df_[reg_col].astype(str)

                # Common keywords across EN/NL/FR-ish exports
                off_mask = (
                    reg.str.contains("offtake", case=False, na=False)
                    | reg.str.contains("consumption", case=False, na=False)
                    | reg.str.contains("afname", case=False, na=False)
                    | reg.str.contains("verbruik", case=False, na=False)
                    | reg.str.contains("import", case=False, na=False)
                )
                inj_mask = (
                    reg.str.contains("injection", case=False, na=False)
                    | reg.str.contains("inject", case=False, na=False)
                    | reg.str.contains("export", case=False, na=False)
                    | reg.str.contains("terug", case=False, na=False)  # teruglever/retour
                    | reg.str.contains("production", case=False, na=False)
                    | reg.str.contains("opwek", case=False, na=False)
                )

                if off_mask.any() or inj_mask.any():
                    signed_energy = pd.Series(0.0, index=df_.index, dtype="float")
                    # Convention: consumption negative, injection positive
                    signed_energy.loc[off_mask] = -vol.loc[off_mask].astype(float)
                    signed_energy.loc[inj_mask] = vol.loc[inj_mask].astype(float)
                else:
                    signed_energy = vol.astype(float)

            # Convert interval energy (kWh) to average power (kW)
            interval_hours = None
            if end_dt is not None:
                dh = (end_dt - start_dt).dt.total_seconds() / 3600.0
                dh = dh.replace([0, float("inf"), -float("inf")], pd.NA)
                if dh.notna().any():
                    interval_hours = float(dh.dropna().median())
            if interval_hours is None or interval_hours <= 0:
                diffs = pd.Series(start_dt).sort_values().diff().dropna()
                if not diffs.empty:
                    interval_hours = float(pd.to_timedelta(diffs.median()).total_seconds() / 3600.0)
            if interval_hours is None or interval_hours <= 0:
                interval_hours = 0.25  # last resort: assume 15 minutes

            signed_power = signed_energy.astype(float) / float(interval_hours)

            out = pd.DataFrame({"DateTime": start_dt, "GridFlow": signed_power})

            # Aggregate rows (e.g., offtake + injection) to net flow per timestamp
            out = (
                out.dropna(subset=["DateTime"])
                .groupby("DateTime", as_index=False)["GridFlow"]
                .sum()
            )
            return out

        # -------------------- DataFrame input --------------------
        if consumption_data_df is not None and not consumption_data_df.empty:
            df_any = consumption_data_df.copy()
            print(df_any.head())
            logger.debug("Using provided consumption_data_df with shape %s", getattr(df_any, "shape", None))

            # Accept Series directly
            if isinstance(df_any, pd.Series):
                df_any = df_any.to_frame(name="GridFlow")

            # If this looks like an interval table (supplier export), parse it.
            if _find_col(df_any, "Start Date") and _find_col(df_any, "Start Time"):
                return _derive_gridflow_from_interval_table(df_any)

            # Otherwise, treat as a regular time series with GridFlow.
            df = df_any

            dt_col = _find_col(df, "DateTime", "Datetime", "Timestamp")
            if dt_col and dt_col != "DateTime":
                df = df.rename(columns={dt_col: "DateTime"})

            if "GridFlow" in df.columns:
                cols = [c for c in ["DateTime", "GridFlow"] if c in df.columns]
                df = df[cols]
            else:
                numeric_cols = df.select_dtypes(include="number").columns
                if len(numeric_cols) == 0:
                    raise ValueError("No numeric data found to use as 'GridFlow'.")
                df = df[[numeric_cols[0]]].rename(columns={numeric_cols[0]: "GridFlow"})

            if "DateTime" not in df.columns:
                if isinstance(df.index, pd.DatetimeIndex):
                    df = df.reset_index().rename(columns={"index": "DateTime"})
                else:
                    raise ValueError(
                        "Consumption DataFrame must have a DatetimeIndex or a 'DateTime' column."
                    )

            return df

        # -------------------- CSV input --------------------
        if consumption_data_csv:
            path = Path(consumption_data_csv)
            if not path.is_file():
                raise FileNotFoundError(f"Consumption CSV file not found: {path}")

            logger.debug("Reading consumption data from CSV: %s", path)

            try:
                raw = pd.read_csv(path, sep=";", dayfirst=True)
            except Exception:
                raw = pd.read_csv(path, sep=None, engine="python", dayfirst=True)

            # Tolerate minor column name variations
            start_date = _find_col(raw, "Start Date", "StartDate")
            start_time = _find_col(raw, "Start Time", "StartTime")
            end_date = _find_col(raw, "End Date", "EndDate")
            end_time = _find_col(raw, "End Time", "EndTime")

            if start_date and start_time:
                raw["DateTime"] = pd.to_datetime(
                    raw[start_date].astype(str) + " " + raw[start_time].astype(str),
                    dayfirst=True,
                    errors="coerce",
                )
            else:
                dt_col = _find_col(raw, "DateTime", "Datetime", "Timestamp", "Start")
                if not dt_col:
                    raise ValueError(
                        "CSV input must contain 'Start Date' + 'Start Time' (or a DateTime-like column)."
                    )
                raw["DateTime"] = pd.to_datetime(raw[dt_col], dayfirst=True, errors="coerce")

            if end_date and end_time:
                raw["End"] = pd.to_datetime(
                    raw[end_date].astype(str) + " " + raw[end_time].astype(str),
                    dayfirst=True,
                    errors="coerce",
                )

            df = raw

            vol_col = _find_col(df, "Volume")
            if vol_col:
                df[vol_col] = pd.to_numeric(
                    df[vol_col].astype(str).str.replace(",", ".", regex=False),
                    errors="coerce",
                )

            gf_col = _find_col(df, "GridFlow")
            if gf_col:
                if gf_col != "GridFlow":
                    df = df.rename(columns={gf_col: "GridFlow"})
                return df[["DateTime", "GridFlow"]]

            # If no GridFlow column, try to build it from interval Volume/Register
            if not vol_col:
                candidate_cols = [c for c in df.columns if "flow" in c.lower() or "power" in c.lower()]
                if candidate_cols:
                    df = df.rename(columns={candidate_cols[0]: "GridFlow"})
                    return df[["DateTime", "GridFlow"]]
                raise ValueError(
                    "CSV must contain either 'Volume' (+ optional 'Register') or a 'GridFlow' / power-like column."
                )

            # Determine interval duration
            interval_hours = None
            if "End" in df.columns and df["End"].notna().any():
                dh = (df["End"] - df["DateTime"]).dt.total_seconds() / 3600.0
                dh = dh.replace([0, float("inf"), -float("inf")], pd.NA)
                if dh.notna().any():
                    interval_hours = float(dh.dropna().median())
            if interval_hours is None or interval_hours <= 0:
                diffs = pd.Series(df["DateTime"]).sort_values().diff().dropna()
                if not diffs.empty:
                    interval_hours = float(pd.to_timedelta(diffs.median()).total_seconds() / 3600.0)
            if interval_hours is None or interval_hours <= 0:
                interval_hours = 0.25

            # Convert Volume to kWh based on Unit
            unit_col = _find_col(df, "Unit")
            if unit_col and df[unit_col].notna().any():
                unit_val = df.loc[df[unit_col].notna(), unit_col].iloc[0]
                factor = _unit_to_kwh_factor(unit_val)
                vol_kwh = df[vol_col] * factor
            else:
                vol_kwh = df[vol_col].astype(float)

            # Sign based on Register
            reg_col = _find_col(df, "Register")
            if reg_col:
                reg = df[reg_col].astype(str)
                off_mask = (
                    reg.str.contains("offtake", case=False, na=False)
                    | reg.str.contains("consumption", case=False, na=False)
                    | reg.str.contains("afname", case=False, na=False)
                    | reg.str.contains("verbruik", case=False, na=False)
                    | reg.str.contains("import", case=False, na=False)
                )
                inj_mask = (
                    reg.str.contains("injection", case=False, na=False)
                    | reg.str.contains("inject", case=False, na=False)
                    | reg.str.contains("export", case=False, na=False)
                    | reg.str.contains("terug", case=False, na=False)
                    | reg.str.contains("production", case=False, na=False)
                    | reg.str.contains("opwek", case=False, na=False)
                )

                if off_mask.any() or inj_mask.any():
                    signed_kwh = pd.Series(0.0, index=df.index, dtype="float")
                    signed_kwh.loc[off_mask] = -vol_kwh.loc[off_mask].astype(float)
                    signed_kwh.loc[inj_mask] = vol_kwh.loc[inj_mask].astype(float)
                else:
                    signed_kwh = vol_kwh.astype(float)
            else:
                signed_kwh = vol_kwh.astype(float)

            df["GridFlow"] = signed_kwh / float(interval_hours)

            df = (
                df.dropna(subset=["DateTime"])
                .groupby("DateTime", as_index=False)["GridFlow"]
                .sum()
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
            raise FileNotFoundError(f"BelpexFilter file not found: {path}")

        logger.debug("Reading BelpexFilter data from: %s", path)

        suffix = path.suffix.lower()
        if suffix == ".xlsx":
            belpex_df = pd.read_excel(path)
        elif suffix == ".csv":
            belpex_df = pd.read_csv(path)
        else:
            raise ValueError("BelpexFilter file must be an .xlsx or .csv file.")

        if "DateTime" not in belpex_df.columns:
            raise ValueError("'DateTime' column not found in the Belpex file.")
        belpex_df["DateTime"] = pd.to_datetime(belpex_df["DateTime"])

        belpex_df = belpex_df.infer_objects()

        merged_df = pd.merge(belpex_df, dataframe, on="DateTime", how="right")

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

    def calculate_total_cost(
        self,
        *,
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

        # Ensure tariffs columns exist
        if c.contract_type == "DualTariff":
            self.dual_tariff()
        elif c.contract_type == "DynamicTariff":
            self.dynamic_tariff()
        else:
            raise ValueError(f"Unknown tariff type: {c.contract_type}")

        # Energy cost as sum of chosen tariff column
        energy_cost = float(self.pd[c.contract_type].sum())

        fixed_component = (
            c.dual_fix if c.contract_type == "DualTariff" else c.dynamic_fix
        )

        # Injection/consumption totals
        inj_peak, inj_offpeak, cons_peak, cons_offpeak = (
            self.get_total_injection_and_consumption()
        )

        # Purchase costs
        purchase_cost_injection = c.purchase_rate_injection * (inj_peak + inj_offpeak)/100 #TODO: check need
        purchase_cost_consumption = c.purchase_rate_consumption * (cons_peak + cons_offpeak)/100

        # Capacity cost
        try:
            capacity_cost = float(self.capacity_tariff())
        except Exception:
            capacity_cost = 0.0

        # Levy/excise based on total consumption
        levy_base_kWh = (cons_peak + cons_offpeak)
        levy_cost = (c.excise_duty + c.energy_contribution + c.green_power_fee)/100 * levy_base_kWh

        total_cost = (
            energy_cost
            + c.data_management_cost
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
            "data_management_cost": float(c.data_management_cost),
            "purchase_cost_injection": float(purchase_cost_injection),
            "purchase_cost_consumption": float(purchase_cost_consumption),
            "capacity_cost": float(capacity_cost),
            "levy_cost": float(levy_cost),
            "injection_peak_kWh": float(inj_peak),
            "injection_offpeak_kWh": float(inj_offpeak),
            "consumption_peak_kWh": float(cons_peak),
            "consumption_offpeak_kWh": float(cons_offpeak),
            "GridCost_dataframe": self.pd,
        }

    from gridcost._capacitytariff import capacity_tariff
    from gridcost._dualtariff import dual_tariff
    from gridcost._dynamictariff import dynamic_tariff
    from gridcost._belpex import update_belpex_quarter_hourly
    from gridcost._belpex import BELPEX_QUARTER_HOURLY_URL
    from gridcost._belpex import _scrape_belpex_page
    from gridcost._visual import get_consumption_and_cost_timeseries
    from gridcost._visual import _prepare_tariff_columns
    from gridcost._visual import plot_consumption_and_cost
    