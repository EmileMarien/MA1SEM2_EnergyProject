import os
import tempfile
import unittest

import pandas as pd

# Adjust these imports to match your project layout.
# If you have a context.py similar to your GridCost tests, you can instead do:
#   from context import fm  # where fm exposes FinancialModel and ElectricityContract

from context import fm  # fm should expose FinancialModel, e.g. `import financialmodel.financialmodel as fm` in context.py
from context import fm_models  # fm_models should expose ElectricityContract, e.g. `import financialmodel.models as fm_models` in context.py


class TestFinancialModelOptimiseContractsFromConsumption(unittest.TestCase):
    def setUp(self):
        # Simple synthetic hourly GridFlow profile for 2 days
        idx = pd.date_range("2025-01-01", periods=48, freq="H")
        self.df = pd.DataFrame(
            {
                "DateTime": idx,
                # Positive values = net consumption
                "GridFlow": [1.0] * len(idx),
            }
        )

        # Financial model instance, use whatever default discount rate you like
        self.fm = fm.FinancialModel()

        # Two simple contract variants to compare
        self.contracts = [
            fm_models.ElectricityContract(
                contract_type="DualTariff",
                dual_peak_tariff=0.25,
                dual_offpeak_tariff=0.15,
                dual_injection_tariff=-0.05,
                dual_fixed_tariff=0.0,
            ),
            fm_models.ElectricityContract(
                contract_type="DualTariff",
                dual_peak_tariff=0.20,
                dual_offpeak_tariff=0.12,
                dual_injection_tariff=-0.04,
                dual_fixed_tariff=0.0,
            ),
        ]

        # Create a temporary CSV version of the same data to test the CSV code path
        tmp = tempfile.NamedTemporaryFile(suffix=".csv", delete=False)
        self.consumption_csv_path = "data\Consumption_data_541448965001643820_2025-11-27.csv"

    def tearDown(self):
        # Clean up temp file
        if os.path.exists(self.consumption_csv_path):
            os.remove(self.consumption_csv_path)

    def test_requires_consumption_data(self):
        """
        optimise_contracts_from_consumption should raise if no
        consumption_data_df and no consumption_data_csv are provided.
        """
        with self.assertRaises(ValueError):
            self.fm.optimise_contracts_from_consumption(
                contracts=self.contracts,
            )

    def test_returns_results_from_dataframe(self):
        """
        Basic happy-path: using a DataFrame should return a non-empty,
        sorted list of result dicts with the expected keys and types.
        """
        results = self.fm.optimise_contracts_from_consumption(
            contracts=self.contracts,
            consumption_data_df=self.df,
            horizon_years=10,
            return_breakdown=False,
        )

        self.assertIsInstance(results, list, "Expected a list of results")
        self.assertGreater(len(results), 0, "Expected at least one result")

        # Check structure of the result
        first = results[0]
        for key in ["contract", "annual_cost_year1", "npv_cost", "horizon_years"]:
            self.assertIn(key, first, f"Result entry should contain '{key}'")

        self.assertIsInstance(first["contract"], fm_models.ElectricityContract)
        self.assertIsInstance(first["annual_cost_year1"], float)
        self.assertIsInstance(first["npv_cost"], float)
        self.assertIsInstance(first["horizon_years"], int)

        # Ensure results are sorted by npv_cost ascending
        npvs = [r["npv_cost"] for r in results]
        self.assertEqual(
            npvs,
            sorted(npvs),
            "Results should be sorted by 'npv_cost' ascending",
        )

    def test_top_k_and_breakdown(self):
        """
        top_k should limit the number of returned results, and
        return_breakdown=True should add a 'breakdown' dict containing 'total_cost'.
        """
        top_k = 1
        results = self.fm.optimise_contracts_from_consumption(
            contracts=self.contracts,
            consumption_data_df=self.df,
            horizon_years=15,
            return_breakdown=True,
            top_k=top_k,
        )

        self.assertLessEqual(
            len(results),
            top_k,
            "Number of returned results should be <= top_k",
        )

        entry = results[0]
        self.assertIn("breakdown", entry, "Result should contain a 'breakdown' dict")
        self.assertIsInstance(entry["breakdown"], dict)
        self.assertIn("total_cost", entry["breakdown"])
        self.assertIsInstance(entry["breakdown"]["total_cost"], float)

    def test_accepts_csv_path(self):
        """
        Using consumption_data_csv instead of a DataFrame should also work.
        """
        results = self.fm.optimise_contracts_from_consumption(
            contracts=self.contracts,
            consumption_data_csv=self.consumption_csv_path,
            horizon_years=5,
        )

        self.assertIsInstance(results, list)
        self.assertGreater(len(results), 0)
        self.assertIn("contract", results[0])
        self.assertIn("annual_cost_year1", results[0])
        self.assertIn("npv_cost", results[0])


if __name__ == "__main__":
    unittest.main()
