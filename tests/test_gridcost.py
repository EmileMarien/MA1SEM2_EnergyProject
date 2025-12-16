import os
import unittest
from pathlib import Path

import pandas as pd

from context import fa  # fa should expose GridCost & update_belpex_quarter_hourly

# Full historical Belpex Excel file (user-specific path)
BELPEX_INITIAL_XLSX = Path(
    r"C:\Users\67583\Downloads\quarter-hourly-spot-belpex--c--elexys (1).xlsx"
)


class TestGridCost(unittest.TestCase):
    def setUp(self):
        # Use the consumption CSV you specified
        self.consumption_path = os.path.join(
            "data",
            "Consumption_data_541448965001643820_2025-11-27.csv",
        )

        self.gridcost_test = fa.GridCost(
            consumption_data_csv=self.consumption_path,
            file_path_BelpexFilter="",  # no Belpex for these tests
            resample_freq="1h",
            electricity_contract=fa.ElectricityContract(  # Example contract
                dual_peak_tariff=0.20,
                dual_offpeak_tariff=0.10,
                dual_injection_tariff=-0.05,
                dual_fixed_tariff=0.01,
            ),
        )

    def test_total_injection_and_consumption(self):
        """get_total_injection_and_consumption should return 4 float values."""
        values = self.gridcost_test.get_total_injection_and_consumption()
        print("[GridCost debug] Injection/consumption values:", values)

        self.assertEqual(
            len(values), 4, "Expected 4 values: inj_peak, inj_offpeak, cons_peak, cons_offpeak"
        )
        for v in values:
            self.assertIsInstance(v, float, "All returned values should be floats")

    def test_calculate_total_cost_scalar(self):
        """calculate_total_cost should return a single float when return_breakdown=False."""
        total = self.gridcost_test.calculate_total_cost()
        print(f"[GridCost debug] Total cost calculated: {total} €")
        self.assertIsInstance(total, float, "Total cost should be a float")

    def test_calculate_total_cost_breakdown(self):
        """calculate_total_cost should return a breakdown dict when requested."""
        breakdown = self.gridcost_test.calculate_total_cost(return_breakdown=True)

        print("[GridCost debug] Cost breakdown keys:", list(breakdown.keys()))
        print("[GridCost debug] Cost breakdown:", breakdown)

        self.assertIsInstance(breakdown, dict, "Breakdown should be a dict")
        self.assertIn("total_cost", breakdown, "Breakdown should contain 'total_cost'")
        self.assertIsInstance(
            breakdown["total_cost"], float, "'total_cost' in breakdown should be a float"
        )

        # Optional: check some other expected keys if you like
        for key in [
            "energy_cost",
            "fixed_component",
            "data_management_cost",
            "purchase_cost_injection",
            "purchase_cost_consumption",
            "capacity_cost",
            "levy_cost",
        ]:
            self.assertIn(key, breakdown, f"Breakdown should contain '{key}'")


class TestBelpexScraping(unittest.TestCase):
    """
    Tests + DEBUGGING for the Belpex scraper.
    These will help you see *why* the CSV is ending up empty.
    """

    def setUp(self):
        self.belpex_url = fa.GridCost.BELPEX_QUARTER_HOURLY_URL
        self.output_path = Path("data") / "belpex_quarter_hourly_test.csv"

        # Start from a clean file for each run
        if self.output_path.exists():
            self.output_path.unlink()

        print(
            "[Belpex debug] Initial Excel path:",
            BELPEX_INITIAL_XLSX,
            "exists?:",
            BELPEX_INITIAL_XLSX.exists(),
        )

    def test_scrape_single_page_and_debug(self):
        """
        Inspect what our scraper returns for a single Belpex page.
        """
        normalised = fa.GridCost._scrape_belpex_page(self.belpex_url)

        print("[Belpex debug] Normalised Belpex dataframe head:\n", normalised.head())

        # Even if the page structure changes, these basic expectations should hold
        self.assertIn("DateTime", normalised.columns)
        self.assertIn("BelpexFilter", normalised.columns)
        self.assertFalse(
            normalised.empty,
            "Normalised Belpex dataframe is empty – check SSL / HTML structure / logging.",
        )

    def test_update_belpex_csv_append_only(self):
        """
        Test the high-level updater: it should create a CSV with data
        and on a second run, not shrink the dataset or introduce duplicates.
        """
        print("\n[Belpex debug] Running first update_belpex_quarter_hourly()")

        df_first = fa.GridCost.update_belpex_quarter_hourly(
            output_path=self.output_path,
            max_pages=1,
            initial_excel=BELPEX_INITIAL_XLSX,
        )

        df_on_disk_first = pd.read_csv(self.output_path)
        print(
            "[Belpex debug] On-disk CSV after first update shape:",
            df_on_disk_first.shape,
        )
        print(
            "[Belpex debug] On-disk CSV columns:",
            df_on_disk_first.columns.tolist(),
        )
        print("[Belpex debug] On-disk CSV head:\n", df_on_disk_first.head())
        print("[Belpex debug] On-disk CSV tail:\n", df_on_disk_first.tail())

        self.assertIn("DateTime", df_on_disk_first.columns)
        self.assertIn("BelpexFilter", df_on_disk_first.columns)
        self.assertFalse(
            df_on_disk_first.empty,
            "Belpex CSV on disk is empty after first update – check the scrape debug test.",
        )

        # Second update: should not remove rows and should not create duplicates
        print("\n[Belpex debug] Running second update_belpex_quarter_hourly()")

        df_second = fa.GridCost.update_belpex_quarter_hourly(
            output_path=self.output_path,
            max_pages=1,
            initial_excel=BELPEX_INITIAL_XLSX,
        )
        print("[Belpex debug] Second update returned shape:", df_second.shape)
        print("[Belpex debug] Second update head:\n", df_second.head())
        print("[Belpex debug] Second update tail:\n", df_second.tail())

        df_on_disk_second = pd.read_csv(self.output_path)
        print(
            "[Belpex debug] On-disk CSV after second update shape:",
            df_on_disk_second.shape,
        )
        print(
            "[Belpex debug] On-disk CSV columns:",
            df_on_disk_second.columns.tolist(),
        )
        print("[Belpex debug] On-disk CSV head:\n", df_on_disk_second.head())
        print("[Belpex debug] On-disk CSV tail:\n", df_on_disk_second.tail())

        self.assertGreaterEqual(
            len(df_on_disk_second),
            len(df_on_disk_first),
            "Number of Belpex rows should stay the same or increase after an update.",
        )

        # Check duplicates on DateTime
        duplicated = df_on_disk_second["DateTime"].duplicated().sum()
        print(f"[Belpex debug] Number of duplicated DateTime entries: {duplicated}")
        self.assertEqual(
            duplicated,
            0,
            "There should be no duplicate DateTime rows in the Belpex CSV.",
        )


class TestGridCostWithBelpex(unittest.TestCase):
    """
    Integration-style test: run Belpex update, then feed it into GridCost
    and check that BelpexFilter is present and sensible.
    """

    def setUp(self):
        self.consumption_path = os.path.join(
            "data",
            "Consumption_data_541448965001643820_2025-11-27.csv",
        )
        self.belpex_path = Path("data") / "belpex_quarter_hourly_test_for_gridcost.csv"

        if self.belpex_path.exists():
            self.belpex_path.unlink()

        print(
            "[Belpex+GridCost debug] Consumption CSV path:",
            os.path.abspath(self.consumption_path),
        )
        print(
            "[Belpex+GridCost debug] Consumption CSV exists?:",
            os.path.exists(self.consumption_path),
        )
        print(
            "[Belpex+GridCost debug] Belpex CSV path for GridCost:",
            self.belpex_path.resolve(),
        )
        print(
            "[Belpex+GridCost debug] Initial Excel path:",
            BELPEX_INITIAL_XLSX,
            "exists?:",
            BELPEX_INITIAL_XLSX.exists(),
        )

        # Update Belpex data (single page for speed) using Excel as initialiser
        self.belpex_df = fa.GridCost.update_belpex_quarter_hourly(
            output_path=self.belpex_path,
            max_pages=1,
            initial_excel=BELPEX_INITIAL_XLSX,
        )
        print(
            "[Belpex+GridCost debug] Belpex dataframe shape (for GridCost):",
            self.belpex_df.shape,
        )
        print("[Belpex+GridCost debug] Belpex head:\n", self.belpex_df.head())

        # Initialise GridCost with BelpexFilter
        self.gc = fa.GridCost(
            consumption_data_csv=self.consumption_path,
            file_path_BelpexFilter=str(self.belpex_path),
            resample_freq="1h",
            electricity_contract=fa.ElectricityContract(
                dual_peak_tariff=0.20,
                dual_offpeak_tariff=0.10,
                dual_injection_tariff=-0.05,
                dual_fixed_tariff=0.01,
            ),
        )

    def test_gridcost_has_belpex_column(self):
        print(
            "[Belpex+GridCost debug] GridCost dataframe shape:",
            self.gc.pd.shape,
        )
        print(
            "[Belpex+GridCost debug] GridCost dataframe columns:",
            self.gc.pd.columns.tolist(),
        )
        print("[Belpex+GridCost debug] GridCost head:\n", self.gc.pd.head())

        self.assertIn(
            "BelpexFilter",
            self.gc.pd.columns,
            "GridCost dataframe should contain a 'BelpexFilter' column when a Belpex file is provided.",
        )

        if not self.belpex_df.empty:
            non_na = self.gc.pd["BelpexFilter"].notna().sum()
            print(
                "[Belpex+GridCost debug] Non-NA BelpexFilter entries in GridCost DF:",
                non_na,
            )
            self.assertGreater(
                non_na,
                0,
                "Expected at least some non-NA BelpexFilter values in GridCost dataframe.",
            )


if __name__ == "__main__":
    unittest.main()
