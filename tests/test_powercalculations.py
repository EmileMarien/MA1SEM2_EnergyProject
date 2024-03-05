import os
import unittest
import pandas as pd
from context import pc

class test_DirectIrradiance(unittest.TestCase):
    def setUp(self):
        
        self.powercalculations_test = pc.PowerCalculations(file_path_irradiance='data/Irradiance_data_vtest.xlsx',file_path_load='data/Load_profile_6_vtest.xlsx') 

    def test_calculate_direct_irradiance(self):
        # Test with some specific values
        self.powercalculations_test.calculate_direct_irradiance(latitude=50, tilt_angle=30, longitude=0, temperature=25)
        result=self.powercalculations_test.get_direct_irradiance()
        self.assertIsNotNone(result)
        self.assertIsInstance(result, pd.Series)

        # Test with some edge cases
        self.powercalculations_test.calculate_direct_irradiance(latitude=90, tilt_angle=45, longitude=0, temperature=1)
        result=self.powercalculations_test.get_direct_irradiance()
        self.assertIsNotNone(result)
        self.assertIsInstance(result, pd.Series)

class test_PVGeneratedPower(unittest.TestCase):
    def setUp(self):
        self.powercalculations_test = pc.PowerCalculations(file_path_irradiance='data/Irradiance_data_vtest.xlsx',file_path_load='data/Load_profile_6_vtest.xlsx') 
        self.powercalculations_test.calculate_direct_irradiance()

    def test_PV_generated_power(self):
        self.powercalculations_test.PV_generated_power(cell_area=1, panel_count=1, T_STC=25, V_OC_STC=0.6, delta_V_OC=-2.5, I_sc_a=300, FF=0.8, T_cell=30, irradiance_STC=100, irradiance_a=120)
        result=self.powercalculations_test.get_PV_generated_power()
        self.assertIsNotNone(result)
        self.assertIsInstance(result, pd.Series)

class test_DataCleaning(unittest.TestCase):
    def setUp(self):
        self.powercalculations_test = pc.PowerCalculations(file_path_irradiance='data/Irradiance_data_vtest.xlsx',file_path_load='data/Load_profile_6_vtest.xlsx') 

    def test_filter_data_by_date_interval(self):
        # Test with some specific values
        #print(self.powercalculations_test.get_dataset())
        self.powercalculations_test.filter_data_by_date_interval(start_date='2018-02-10 10:00', end_date='2018-02-10 17:00', interval='1h')
        result=self.powercalculations_test.get_dataset() 
        #print(result)
        self.assertIsNotNone(result)
        self.assertIsInstance(result, pd.DataFrame)

        if isinstance(result.index, pd.DatetimeIndex):
            # Assert hourly data spacing for DatetimeIndex
            time_diffs = result.index.to_series().diff()  # Calculate time differences directly
            #print(time_diffs)
            assert all(time_diffs[1:] == pd.Timedelta(hours=1))
        else:
            # Handle non-DatetimeIndex scenarios (if applicable)
            raise ValueError("Unexpected index type: {}".format(type(result.index)))

    def test_fill_load_with_weighted_values(self):
        # Test with some specific values
        #print(self.powercalculations_test.get_load())
        self.powercalculations_test.fill_load_with_weighted_values()
        result=self.powercalculations_test.get_load()
        #print(result)
        self.assertIsNotNone(result)
        self.assertIsInstance(result, pd.Series)

class test_Getters(unittest.TestCase):
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

class test_Powerflows(unittest.TestCase):
    def setUp(self):
        self.powercalculations_test = pc.PowerCalculations(file_path_irradiance='data/Irradiance_data_vtest.xlsx',file_path_load='data/Load_profile_6_vtest.xlsx') 

class test_Export(unittest.TestCase):
    def setUp(self):
        self.powercalculations_test = pc.PowerCalculations(file_path_irradiance='data/Irradiance_data_vtest.xlsx',file_path_load='data/Load_profile_6_vtest.xlsx') 

    def test_export_dataframe_to_excel(self):
            # Define the output file path for testing (avoid overwriting actual data)
            output_file_path = "test_output.xlsx"

            # Call the export function
            self.powercalculations_test.export_dataframe_to_excel(output_file_path)

            # Verify the file exists
            self.assertTrue(os.path.exists(output_file_path))

            # Optionally, verify the file content (more advanced testing)
            # ... (code to check file contents, e.g., using libraries like pandas.read_excel)

            # Clean up the test file
            os.remove(output_file_path)


############################################################################################################

if __name__ == '__main__':
    unittest.main()