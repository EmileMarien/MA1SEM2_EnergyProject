
from math import acos, asin, cos, pi, sin, tan
import math
from typing import List
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

from torch import sgn
import pvlib

class FinancialAnalysis():
    def __init__(self, dataframe:pd.DataFrame):


        # Check if all required columns are present
        required_columns = ['DateTime', 'GlobRad', 'DiffRad', 'T_RV_degC', 'T_CommRoof_degC']
        missing_columns = [col for col in required_columns if col not in self.pd.columns]
        assert not missing_columns, f"The following columns are missing: {', '.join(missing_columns)}"

        #Assign 
        self.pd = dataframe
        self.
        # Initialize the columns that will be used for the calculations
        self.pd[''] = None




    # Imported methods

    
    from ._getters import get_dataset
    from ._getters import get_irradiance
    from ._getters import get_load
    from ._getters import get_direct_irradiance
    from ._getters import get_PV_generated_power

    from ._export import export_dataframe_to_excel
