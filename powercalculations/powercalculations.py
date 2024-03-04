
from math import acos, asin, cos, pi, sin, tan
import math
from typing import List
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

from torch import sgn
import pvlib

class PowerCalculations():
    def __init__(self, file_path_irradiance: str,file_path_load: str):
        """
        Initializes the PowerCalculations class with the given dataset
        
        Args:
        file_path (str): The file path to the Excel file containing the dataset        
        """
        assert file_path_irradiance.endswith('.xlsx'), 'The file must be an Excel file'
        assert file_path_load.endswith('.xlsx'), 'The file must be an Excel file'
        
        # Read the dataset from the Excel file
        self.pd = pd.read_excel(file_path_irradiance)
        # Check if all required columns are present
        required_columns = ['DateTime', 'GlobRad', 'DiffRad', 'T_RV_degC', 'T_CommRoof_degC']
        missing_columns = [col for col in required_columns if col not in self.pd.columns]
        assert not missing_columns, f"The following columns are missing: {', '.join(missing_columns)}"

        # Read the dataset from the Excel file and concatenate with the existing DataFrame
        self.pd = pd.merge(self.pd, pd.read_excel(file_path_load), on='DateTime', how='outer') 

        # Initialize the columns that will be used for the calculations
        self.pd['DirectIrradiance'] = None       
        self.pd['PV_generated_power'] = None
        self.pd.set_index('DateTime', inplace=True)


    # Imported methods
    from ._datacleaning import filter_data_by_date_interval
    from ._datacleaning import fill_load_with_weighted_values
    
    from ._pvpower import PV_generated_power
    
    from ._visualisations import plot
    
    from ._directirradiance import calculate_direct_irradiance
    
    from ._getters import get_dataset
    from ._getters import get_irradiance
    from ._getters import get_load
    from ._getters import get_direct_irradiance
    from ._getters import get_PV_generated_power
