import unittest
import pandas as pd
from context import pc

class TestDirectIrradiance(unittest.TestCase):
    def setUp(self):
        
        self.powercalculations_test = pc.PowerCalculations(file_path_irradiance='data/Irradiance_data_vtest.xlsx',file_path_load='data/Load_profile_6_vtest.xlsx') 

    def test_calculate_direct_irradiance(self):
        # Test with some specific values
        result = self.powercalculations_test.calculate_direct_irradiance(latitude=50, tilt_angle=30, longitude=0, temperature=25)
        self.assertIsNotNone(result)
        self.assertIsInstance(result, float)

        # Test with some edge cases
        result = self.powercalculations_test.calculate_direct_irradiance(latitude=90, tilt_angle=45, longitude=0, temperature=1)
        self.assertIsNotNone(result)
        self.assertIsInstance(result, float)


class TestPVGeneratedPower(unittest.TestCase):
    def setUp(self):
        self.powercalculations_test = pc.PowerCalculations(file_path_irradiance='data/Irradiance_data_vtest.xlsx',file_path_load='data/Load_profile_6_vtest.xlsx') 
        self.powercalculations_test.calculate_direct_irradiance()

    def test_PV_generated_power(self):
        self.powercalculations_test.PV_generated_power(cell_area=1, panel_count=1, T_STC=25, V_OC_STC=0.6, delta_V_OC=-2.5, I_sc_a=300, FF=0.8, T_cell=30, irradiance_STC=100, irradiance_a=120)
        result=self.powercalculations_test.get_PV_generated_power()
        self.assertIsNone(result)

class TestDataCleaning(unittest.TestCase):
    def setUp(self):
        self.powercalculations_test = pc.PowerCalculations(file_path_irradiance='data/Irradiance_data_vtest.xlsx',file_path_load='data/Load_profile_6_vtest.xlsx') 

    def test_filter_data_by_date_interval(self):
        # Test with some specific values
        print(self.powercalculations_test.get_dataset())
        self.powercalculations_test.filter_data_by_date_interval(start_date='2018-02-10 10:00', end_date='2018-02-10 17:00', interval='1h')
        result=self.powercalculations_test.get_dataset() 
        print(result)
        self.assertIsNotNone(result)
        self.assertIsInstance(result, pd.DataFrame)

        if isinstance(result.index, pd.DatetimeIndex):
            # Assert hourly data spacing for DatetimeIndex
            time_diffs = result.index.to_series().diff()  # Calculate time differences directly
            print(time_diffs)
            assert all(time_diffs[1:] == pd.Timedelta(hours=1))
        else:
            # Handle non-DatetimeIndex scenarios (if applicable)
            raise ValueError("Unexpected index type: {}".format(type(result.index)))

    def test_fill_load_with_weighted_values(self):
        # Test with some specific values
        result = self.powercalculations_test.fill_load_with_weighted_values()
        self.assertIsNotNone(result)
        self.assertIsInstance(result, pd.Series)

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
        self.assertIsInstance(result, pd.Series)

    def test_get_load(self):
        result = self.powercalculations_test.get_load()
        self.assertIsNotNone(result)
        self.assertIsInstance(result, pd.Series)
    
    def test_get_direct_irradiance(self):
        result = self.powercalculations_test.get_direct_irradiance()
        self.assertIsNotNone(result)
        self.assertIsInstance(result, pd.Series)

    def test_get_PV_generated_power(self):
        result = self.powercalculations_test.get_PV_generated_power()
        self.assertIsNotNone(result)
        self.assertIsInstance(result, pd.Series)

class TestPowerflows(unittest.TestCase):
    def setUp(self):
        self.powercalculations_test = pc.PowerCalculations(file_path_irradiance='data/Irradiance_data_vtest.xlsx',file_path_load='data/Load_profile_6_vtest.xlsx') 



############################################################################################################

if __name__ == '__main__':
    unittest.main()