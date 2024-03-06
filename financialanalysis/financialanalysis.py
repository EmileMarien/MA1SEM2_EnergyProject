
from math import acos, asin, cos, pi, sin, tan
import math
from typing import List
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

from torch import sgn
import pvlib

class FinancialAnalysis():
    def __init__(self, data):
        # Convert Series to DataFrame if data is a Series
        if isinstance(data, pd.Series):
            dataframe = pd.DataFrame({'PowerGrid': data})
            dataframe.index = pd.to_datetime(dataframe.index)
        # Use DataFrame directly if data is a DataFrame
        elif isinstance(data, pd.DataFrame):
            dataframe = pd.DataFrame(data['PowerGrid'])
        else:
            raise ValueError("Input data must be either a Series or a DataFrame")

        # Check if all required columns are present
        required_columns = ['PowerGrid']
        missing_columns = [col for col in required_columns if col not in dataframe.columns]
        assert not missing_columns, f"The following columns are missing: {', '.join(missing_columns)}"

        # Assign the DataFrame to self.pd
        self.pd = dataframe

        # Initialize the columns that will be used for the calculations
        self.pd['DualTariffCost'] = None
        self.pd['DynamicTariffCost'] = None




    # Imported methods

    
    from ._getters import get_dataset
    from ._getters import get_irradiance
    from ._getters import get_load
    from ._getters import get_direct_irradiance
    from ._getters import get_PV_generated_power

    from ._export import export_dataframe_to_excel
