# Function to filter data by date interval
import pandas as pd


def filter_data_by_date_interval(self, start_date: str, end_date: str, interval='1S'):
    """
    Filters the given DataFrame to include only the rows with DateTime values within the specified date interval

    Args:
    df (DataFrame): The DataFrame containing the dataset
    start_date (str): The start date of the interval
    end_date (str): The end date of the interval
    interval (str): The interval for filtering the data. Default is '1S' (1 second)

    Returns:
    DataFrame: The filtered DataFrame
    """

    # Convert start_date and end_date to datetime objects
    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)
    
    # Create a date range with the specified interval
    date_range = pd.date_range(start=start_date, end=end_date, freq=interval)
    
    # Filter the DataFrame to include only the rows with DateTime values in the date_range
    self.pd = self.pd[self.pd['DateTime'].isin(date_range)]
    #self.irradiance = self.irradiance[self.irradiance['DateTime'].isin(date_range)]
    #self.load = self.load[self.load['DateTime'].isin(date_range)]

def fill_load_with_weighted_values(self):
    """
    Fills the NaN values in the load column with weighted values
    """
    # Interpolate the NaN values in the load column using linear interpolation
    self.pd['Load_kW']= self.pd['Load_kW'].interpolate(method='linear')

    return None
