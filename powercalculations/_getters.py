
from typing import List
import pandas as pd


def get_irradiance(self):
    """
    Returns the irradiance data
    """
    return self.pd['DiffRad']

def get_load(self):
    """
    Returns the load data
    """
    return self.pd['Load_kW']   

def get_dataset(self):
    """
    Returns the dataset
    """
    #print(self.pd.index.dtype)
    return self.pd

def get_direct_irradiance(self):
    """
    Returns the direct irradiance data
    """
    return self.pd['DirectIrradiance']

def get_PV_generated_power(self):
    """
    Returns the PV generated power data
    """
    return self.pd['PV_generated_power']


def get_energy_TOT(self,column_name:str='Load_kW',peak:str='peak'):
    """
    Calculates the total energy in kWh for the entire year in the DataFrame. The energy is calculated for the specified power values and peak or offpeak period.

    Args:
    column_name (str): The name of the column to be used for the calculation. Choose between: 'Load_kW', 'GridPower'. Default: 'Load_kW'
    peak (str): The period to calculate the energy. Choose between: 'peak', 'offpeak', 'weekend'. Default: 'peak'
    
    Returns:
        float: The total 'Load_kW' between 8h and 18h.
    """

    # Select only load data
    if column_name=='Load_kW':
        df_load=self.pd['Load_kW']
    elif column_name=='GridFlow':
        df_load=self.pd['GridFlow']
    else:
        AssertionError('The column_name must be either Load_kW or PowerGrid')

    if peak=='peak':
        # Select data between 8:00 and 18:00 for the entire year
        df_filtered = df_load[(df_load.index.hour >= 8) & (df_load.index.hour < 18)]
    elif peak=='offpeak':
        # Select data outside 8:00 and 18:00 for the entire year
        df_filtered = df_load[(df_load.index.hour <= 8) & (df_load.index.hour > 18)]
    else:
        AssertionError('The peak must be either peak or offpeak')

    # Sum the 'Load_kW' values in the filtered DataFrame
    load_tot_day = df_filtered.sum()
    
    # Check if the input data contains NA values
    assert not df_load.isnull().values.any(), 'The input data contains NA values'
    #Integrate the power over time to get the energy in [kWh]
    interval = pd.Timedelta(df_load.index.freq).total_seconds() / 3600 # Convert seconds to hours
    energy_peak=load_tot_day*interval# [kWh]

    return energy_peak



def get_columns(self,columns:List[str]):
    """
    Returns the dataset with the specific columns
    """

    assert all(col in self.pd.columns for col in columns), 'The columns must be present in the DataFrame'

    return self.pd[columns]
   
def get_PV_energy_per_hour(self):
    power=get_average_per_hour(self,"PV_generated_power")
    

def get_average_per_hour(self, column_name: str = 'Load_kW'):
    """
    Calculates the average load per hour for each hour of the day based on the entire year in the DataFrame. in kW

    Returns:
        pandas.Series: A Series containing the average 'Load_kW' for each hour of the day.
        The index of the Series is the hour (0-23).
    """

    # Extract the hour component from the index
    hour_component = self.pd.index.hour

    # Group the data by the hour component and calculate the mean
    df_hourly_avg = self.pd.groupby(hour_component)[column_name].mean()

    return df_hourly_avg

def get_average_per_day(self,column_name:str='Load_kW'):
    """
    Calculates the average load per day for each day of the year based on the entire year in the DataFrame. in kW

    Returns:
        pandas.Series: A Series containing the average 'Load_kW' for each day of the year.
        The index of the Series is the day of the year (1-365).
    """

    # Resample the DataFrame by day ('D') and calculate the mean
    df_daily_avg = self.pd[column_name].resample('D').mean()

    return df_daily_avg

def get_max_per_hour(self,column_name:str='Load_kW'):
    """
    Calculates the maximum load per hour for each hour in the day based on the entire year in the DataFrame. in kW

    Returns:
        pandas.Series: A Series containing the maximum 'Load_kW' for each hour of the day.
        The index of the Series is the hour (0-23).
    """

    # Resample the DataFrame by hour ('H') and calculate the mean
    df_hourly_max = self.pd[column_name].resample('h').max()

    return df_hourly_max

def get_grid_power(self):
    return [self.pd['GridFlow'], self.pd['BatteryCharge']]
