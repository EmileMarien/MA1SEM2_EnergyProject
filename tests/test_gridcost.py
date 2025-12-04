import os
import unittest
import pandas as pd

from context import fa  # fa should expose GridCost, e.g. `import gridcost.gridcost as fa` in context.py


class TestGridCost(unittest.TestCase):
    def setUp(self):
        # Use the consumption CSV you specified
        self.consumption_path = os.path.join(
            "data",
            "Consumption_data_541448965001643820_2025-11-27.csv",
        )

        self.gridcost_test = fa.GridCost(
            consumption_data_csv=self.consumption_path,
            file_path_BelpexFilter="",  # or e.g. "data/BelpexFilter.xlsx" if you want Belpex pricing
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
        self.assertEqual(
            len(values), 4, "Expected 4 values: inj_peak, inj_offpeak, cons_peak, cons_offpeak"
        )
        for v in values:
            self.assertIsInstance(v, float, "All returned values should be floats")

    def test_calculate_total_cost_scalar(self):
        """calculate_total_cost should return a single float when return_breakdown=False."""
        total = self.gridcost_test.calculate_total_cost()
        print(f"Total cost calculated: {total} €")
        self.assertIsInstance(total, float, "Total cost should be a float")

    def test_calculate_total_cost_breakdown(self):
        """calculate_total_cost should return a breakdown dict when requested."""
        breakdown = self.gridcost_test.calculate_total_cost(return_breakdown=True)

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


if __name__ == "__main__":
    unittest.main()
