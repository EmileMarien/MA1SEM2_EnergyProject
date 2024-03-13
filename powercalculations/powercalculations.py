
from math import acos, asin, cos, pi, sin, tan
import math
from typing import List
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

from torch import sgn

class PowerCalculations():
    def __init__(self, file_path_irradiance: str,file_path_load: str, dataset: pd.DataFrame = None):
        """
        Initializes the PowerCalculations class with the given dataset
        
        Args:
        file_path (str): The file path to the Excel file containing the dataset 
        dataset (DataFrame): The dataset to be used for the calculations if file_path is not provided       
        """
        if dataset is not None:
            # Use the dataset directly if provided
            merged_df = dataset
        else:
            assert file_path_irradiance.endswith('.xlsx'), 'The file must be an Excel file'
            assert file_path_load.endswith('.xlsx'), 'The file must be an Excel file'
            
            # Read the dataset from the Excel file
            irradiance_df = pd.read_excel(file_path_irradiance)
            
            # Read the Excel file into a DataFrame
            load_df = pd.read_excel(file_path_load)

            # Assert that 'Load_kW' and 'DateTime' columns are present in the Excel file
            assert 'DateTime' in irradiance_df.columns, "'DateTime' column not found in the Irradiance Excel file"
            assert 'DateTime' in load_df.columns, "'DateTime' column not found in the Load Excel file"
            
            # Merge the DataFrame with the one read from excel
            merged_df = pd.merge(irradiance_df, load_df, on='DateTime', how='outer') 
        
        # Check if all required columns are present
        required_columns = ['DateTime', 'GlobRad', 'DiffRad', 'T_RV_degC', 'T_CommRoof_degC','Load_kW']
        missing_columns = [col for col in required_columns if col not in merged_df.columns]
        assert not missing_columns, f"The following columns are missing: {', '.join(missing_columns)}"


        expected_columns = ['DateTime', 'Load_kW', 'GlobRad', 'DiffRad', 'T_RV_degC', 'T_CommRoof_degC']
        self.pd=merged_df[expected_columns]
        
        #Set a datetime index
        self.pd.set_index('DateTime', inplace=True)

        # Initialize the columns that will be used for the calculations
        self.pd['DirectIrradiance'] = None       
        self.pd['PV_generated_power'] = None
        self.pd['PowerGrid'] = None


    # Imported methods
    from ._datacleaning import filter_data_by_date_interval
    from ._datacleaning import interpolate_columns
    
    from ._pvpower import PV_generated_power
    
    from ._visualisations import plot_columns
    from ._visualisations import plot_dataframe
    
    from ._directirradiance import calculate_direct_irradiance

    from ._powerflows import power_flow
    
    from ._getters import get_dataset
    from ._getters import get_irradiance
    from ._getters import get_load
    from ._getters import get_direct_irradiance
    from ._getters import get_PV_generated_power
    from ._getters import get_energy_TOT
    from ._getters import get_average_per_hour
    from ._getters import get_grid_power

    from ._export import export_dataframe_to_excel
