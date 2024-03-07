# Function to filter data by date interval
import pandas as pd


def filter_data_by_date_interval(self, start_date: str, end_date: str, interval='1h'):
    """
    Filters the given DataFrame to include only the rows with DateTime values within the specified start and end dates, with an interval specified by 'interval'

    Args:
    self.df (DataFrame): The DataFrame containing the dataset
    start_date (str): The start date of the interval
    end_date (str): The end date of the interval
    interval (str): The interval for filtering the data. Options: '1M' (monthly), '1W' (weekly), '1D' (daily), '1h' (hourly, default), '1T' (minutely)

    Returns:
    DataFrame: The filtered DataFrame
    """

    # Convert start_date and end_date to datetime objects
    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)
    
    # Create a date range with the specified interval
    date_range = pd.date_range(start=start_date, end=end_date, freq=interval)
    
    # Filter the DataFrame to include only the rows with DateTime values in the date_range
    self.pd = self.pd.loc[self.pd.index.isin(date_range)]
    #self.irradiance = self.irradiance[self.irradiance['DateTime'].isin(date_range)]
    #self.load = self.load[self.load['DateTime'].isin(date_range)]

def interpolate_columns(self, interval:int='1h'):
    """
    Fills the NaN values in each column with weighted values
    """
    
    # Resample the dataframe to the specified interval and interpolate missing values
    self.pd = self.pd.resample(interval).interpolate(method='linear')

    return None
