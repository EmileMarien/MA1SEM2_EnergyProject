import os
import unittest
import pandas as pd
import pytest
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
        self.powercalculations_test.PV_generated_power(cell_area=1, panel_count=1, T_STC=25, efficiency_max= 0.02, Temp_coeff= -0.026)
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
    
    def test_interpolate_column(self):
        # Interpolate the Load_kW column with minute interval
        interval = 'T'  # T represents minute interval
        self.powercalculations_test.interpolate_column(interval)

        # Check if there are no NaN values after interpolation
        self.assertFalse(self.powercalculations_test.pd['Load_kW'].isnull().any())
        self.assertFalse(self.powercalculations_test.pd['DiffRad'].isnull().any())


        # Check if the data is correctly interpolated
        self.assertEqual(self.powercalculations_test.pd.loc['2018-02-28 04:30:00', 'DiffRad'], 15)


class test_Getters(unittest.TestCase):
    def setUp(self):
        self.powercalculations_test = pc.PowerCalculations(file_path_irradiance='data/Irradiance_data_vtest.xlsx',file_path_load='data/Load_profile_6_vtest.xlsx') 
        self.powercalculations_test.interpolate_columns(interval='1h')
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

    def test_get_energy_TOT(self):
        result = self.powercalculations_test.get_energy_TOT(column_name='Load_kW', peak='peak')
        print(result)
        self.assertIsNotNone(result)


    def test_get_average_per_hour(self):

        # Assert returned Series has expected index and average values
        result = self.powercalculations_test.get_average_per_hour('GlobRad')
        self.assertIsInstance(result, pd.Series)
        self.assertEqual(len(result),24)  # 24 hours in a day
        self.assertEqual(list(result.index) == [i for i in range(24)])  # Assuming hour index starts from 0
        self.assertAlmostEqual(result.tolist()[23] == 0)  # Assuming no irradiance at 23:00

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