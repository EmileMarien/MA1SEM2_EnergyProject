import unittest
import pandas as pd

from context import pc

class TestPowerCalculations(unittest.TestCase):
    def setUp(self):
        
        self.powercalculations_test = pc.PowerCalculations(file_path_irradiance='data/Irradiance_data_vtest.xlsx',file_path_load='data/Load_profile_6_vtest.xlsx') 

    def test_calculate_direct_irradiance_specific(self):
        # Test with some specific values
        result = self.powercalculations_test.calculate_direct_irradiance_specific(latitude=50, tilt_angle=30, day='2022-03-10 00:00', longitude=0, temperature=25)
        self.assertIsNotNone(result)
        self.assertIsInstance(result, float)

        # Test with some edge cases
        result = self.powercalculations_test.calculate_direct_irradiance_specific(latitude=0, tilt_angle=0, day='2022-03-10 00:00', longitude=0, temperature=0)
        self.assertIsNotNone(result)
        self.assertIsInstance(result, float)

    def test_direct_irradiance(self):
        # Assuming your class has a pd attribute that is a DataFrame
        self.powercalculations_test.pd = pd.DataFrame({
            'dayTime': ['2022-03-10 00:00', '2022-03-11 00:00', '2022-03-12 00:00']
        })
        self.powercalculations_test.direct_irradiance()
        self.assertIn('DirectIrradiance', self.powercalculations_test.pd.columns)
        self.assertEqual(len(self.powercalculations_test.pd['DirectIrradiance']), 3)

class TestGetters(unittest.TestCase):
    def setUp(self):
        self.powercalculations_test = pc.PowerCalculations(file_path_irradiance='data/Irradiance_data_vtest.xlsx',file_path_load='data/Load_profile_6_vtest.xlsx') 

    def test_get_dataset(self):
        result = self.powercalculations_test.get_dataset()
        self.assertIsNotNone(result)
        self.assertIsInstance(result, pd.DataFrame)

    def test_get_irradiance(self):
        result = self.powercalculations_test.get_irradiance()
        self.assertIsNotNone(result)
        self.assertIsInstance(result, pd.DataFrame)

    def test_get_load(self):
        result = self.powercalculations_test.get_load()
        self.assertIsNotNone(result)
        self.assertIsInstance(result, pd.DataFrame)

if __name__ == '__main__':
    unittest.main()