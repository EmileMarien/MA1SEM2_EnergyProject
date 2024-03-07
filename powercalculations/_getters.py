
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

def get_loadTOT_day(self):
    """
    Calculates the sum of 'Load_kW' values between 8h and 18h for the entire year in the DataFrame.

    Returns:
        float: The total 'Load_kW' between 8h and 18h.
    """
    # Select only load data
    df_load=self.pd['Load_kW']

    # Select data between 8:00 and 18:00 for the entire year
    df_filtered = df_load[(df_load.index.hour >= 8) & (df_load.index.hour < 18)]

    # Sum the 'Load_kW' values in the filtered DataFrame
    load_tot_day = df_filtered['Load_kW'].sum()

    return load_tot_day

def get_loadTOT_night(self):
    """
    Calculates the sum of 'Load_kW' values outside 8h and 18h for the entire year in the DataFrame.

    Returns:
        float: The total 'Load_kW' outside 8h and 18h.
    """
    # Select only load data
    df_load=self.pd['Load_kW']

    # Select data between 8:00 and 18:00 for the entire year
    df_filtered = df_load[(df_load.index.hour <= 8) & (df_load.index.hour > 18)]

    # Sum the 'Load_kW' values in the filtered DataFrame
    load_tot_day = df_filtered['Load_kW'].sum()

    return load_tot_day

def get_average_per_hour(self,column_name:str='Load_kW'):
    """
    Calculates the average load per hour for each hour in the day based on the entire year in the DataFrame.

    Returns:
        pandas.Series: A Series containing the average 'Load_kW' for each hour of the day.
        The index of the Series is the hour (0-23).
    """

    # Resample the DataFrame by hour ('H') and calculate the mean
    df_hourly_avg = self.pd[column_name].resample('H').mean()

    return df_hourly_avg
