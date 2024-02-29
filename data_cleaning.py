from math import acos, asin, cos, pi, sin, tan
import math
from typing import List
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

from torch import sgn
import pvlib

class PowerCalculations:
    def __init__(self, file_path_irradiance: str,file_path_load: str):
        assert file_path_irradiance.endswith('.xlsx'), 'The file must be an Excel file'
        assert file_path_load.endswith('.xlsx'), 'The file must be an Excel file'
        
        # Read the dataset from the Excel file
        self.pd = pd.read_excel(file_path_irradiance)
        # Check if all required columns are present
        required_columns = ['DateTime', 'GlobRad', 'DiffRad', 'T_RV_degC', 'T_CommRoof_degC']
        missing_columns = [col for col in required_columns if col not in self.pd.columns]
        assert not missing_columns, f"The following columns are missing: {', '.join(missing_columns)}"

        # Read the dataset from the Excel file
        self.pd = pd.merge(self.pd, pd.read_excel(file_path_load), on='DateTime', how='outer')        
        #self.pd['load'] = pd.read_excel(file_path_load)['Load_kW']
        #self.pd['PV_output'] = pd.DataFrame()
        #self.pd['irbeamirradiance'] = pd.DataFrame()


    # Function to filter data by date interval
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

    def get_irradiance(self):
        """
        Returns the irradiance data
        """
        return self.pd['irradiance']

    def get_load(self):
        """
        Returns the load data
        """
        return self.pd['load']   

    def get_dataset(self):
        """
        Returns the dataset
        """
        return self.pd
    
    # Function to plot a given dataset
    def plot(self, column_name: List[str]):
        """
        Plots the given dataset using the specified column name

        Args:
        df (DataFrame): The DataFrame containing the dataset
        column_name (str[]): The name of the column(s) to be plotted. Choose between: GlobRad, DiffRad, T_CommRoof_degC, T_RV_degC 
        """
        for col in column_name:
            plt.plot(self.pd['DateTime'], self.pd[col])
        plt.xlabel('Date Time')
        plt.ylabel(column_name)
        plt.title(f'Plot of {column_name}')
        plt.legend(column_name)
        plt.show()        

    def calculate_beam_irradiance(self, latitude:int=0, tilt_angle:int=0, t_s:int=0, efficiency:int=0, area:int=0, day:str='2018-03-10 00:00',longitude:int=0,temperature:int=0): 
        """
        Calculates the beam irradiance using the formula: Beam Irradiance = Global Horizontal Irradiance - Diffuse Horizontal Irradiance
        Args:
        df (DataFrame): The DataFrame containing the dataset

        Returns:
        DataFrame: The DataFrame containing the calculated beam irradiance
        """
        # Convert the string to a pandas Timestamp
        day_datetime = pd.to_datetime(day)

        # Convert the Timestamp to a pandas DatetimeIndex
        day_datetime_index = pd.DatetimeIndex([day_datetime])

        # Irradiances at specific day
        print(self.pd['DateTime'])
        GHI=self.pd.loc[self.pd['DateTime'] == day_datetime, 'GlobRad'] #Global Horizontal Irradiance
        GDI=self.pd.loc[self.pd['DateTime'] == day_datetime, 'DiffRad'] #Diffuse Horizontal Irradiance

        """
    
            # Solar time
        rad = pi/180
        deg = 180/pi
        t_clk = day.hour + day.minute/60 + day.second/3600 #time in hours
        delta_t_dst = -1 #daylight saving time used
        phi_lat_deg = 55 + 36/60 + 20/60/60 #pos lattitude
        phi_lat = phi_lat_deg*rad
        phi_longt = -13 #east is neagtive
        phi_std = -15 #Time zone meridian
        n = self.get_calenderday(day)#101 #April 10th 2016(leap year)

        EOT = 0.258*cos(2*pi*(n-1)/365)+(-7.416*sin(2*pi*(n-1)/365)) + (-3.648*cos(4*pi*(n-1)/365)) + (-9.228*sin(4*pi*(n-1)/365));

        t_s = t_clk + (phi_std-phi_longt)/15 + EOT/60 + delta_t_dst

        #Solar angles calculation
        t_s=0 # time [hours]
        hour_angle=pi/12*(t_s-12) # omega [radians]
        declination_angle=asin(0.39795*cos(2*pi*(n-173)/365)) # delta
        length_of_day=24/pi*acos(-tan(latitude)*tan(declination_angle)) # N [hours]
        
        solar_zenith_angle=acos(cos(latitude)*cos(declination_angle)*cos(hour_angle)+sin(latitude)*sin(declination_angle)) # theta_z [degrees]
        solar_azimuth_angle=sgn(hour_angle)*acos((cos(solar_zenith_angle*sin(latitude)-sin(declination_angle)))/(sin(solar_zenith_angle))) # gamma_s [degrees]
        surface_azimuth_angle=0 # gamma_c [degrees]
    """

        # Solar angles calculation
        A=pvlib.solarposition.get_solarposition(day_datetime_index, latitude=latitude,longitude=longitude,temperature=temperature)
        
        solar_zenith_angle = float(A['zenith'].iloc[0])        
        print(solar_zenith_angle)
        solar_azimuth_angle=float(A['azimuth'].iloc[0])
        print(solar_azimuth_angle)
        surface_azimuth_angle=0 # gamma_c [degrees]

        # Beam Irradiance calculation

        # Calculate the Angle of Incidence (AOI)
        AOI = math.acos(
            math.cos(tilt_angle) * math.cos(solar_zenith_angle) +
            math.sin(tilt_angle) * math.sin(solar_zenith_angle) * math.cos(solar_azimuth_angle - surface_azimuth_angle)
        )

        # Calculate the Direct Normal Irradiance (DNI)
        DNI = (GHI - GDI) / math.cos(solar_zenith_angle)
        return A
        
    def PV_generated_power(self,cell_area:int=1, panel_count:int=1, T_STC:int=25, V_OC_STC:int=0.6, delta_V_OC:int=-2.5, I_sc_a:int=300, FF:int=0.8, T_cell:int=30, irradiance_STC:int=100, irradiance_a:int=120):
        """
        Converts the irradiance data to power data using the specified column name
        https://www.researchgate.net/post/How_can_I_calculate_the_power_output_of_a_PV_system_in_one_day_using_a_function_of_the_temperature_of_the_cell_and_the_reference_temperature
        Args:
        df (DataFrame): The DataFrame containing the dataset
        column_name (str): The name of the column to be converted. Choose between: GlobRad, DiffRad

        Returns:
        DataFrame: The DataFrame containing the converted power data
        """
        

        # Check if the 'beamirradiance' column is empty
        if 'beamirradiance' in self.pd.columns and not self.pd['beamirradiance'].empty:
            # Calculate the PV generated power
            self.pd['PV_generated_power'] = FF*cell_area*I_sc_a*irradiance_a/irradiance_STC*(V_OC_STC+delta_V_OC*(T_cell-T_STC))*panel_count
        else:
            raise ValueError("The 'beamirradiance' column is empty or not present in the DataFrame")
        return None
    
    def battery_charge(self, efficiency, area):
        """
        Converts the irradiance data to power data using the specified column name
        https://www.researchgate.net/post/How_can_I_calculate_the_power_output_of_a_PV_system_in_one_day_using_a_function_of_the_temperature_of_the_cell_and_the_reference_temperature
        Args:
        df (DataFrame): The DataFrame containing the dataset
        column_name (str): The name of the column to be converted. Choose between: GlobRad, DiffRad

        Returns:
        DataFrame: The DataFrame containing the converted power data
        """
        # Convert irradiance to power using the formula: Power = Irradiance * Area
        area = 1

########################################################################################
file_path_irradiance = 'data/Irradiance_data_v2.xlsx'
file_path_load = 'data/Load_profile_6.xlsx'
irradiance=PowerCalculations(file_path_irradiance=file_path_irradiance,file_path_load=file_path_load)

# GENK data
latitude=50.99461 # [degrees]
longitude=5.53972 # [degrees]
start_date = '2018-03-1 00:00'
end_date = '2018-12-1 00:10'
interval = '1h'  # Interval of 1 hour
irradiance.filter_data_by_date_interval(start_date, end_date, interval)

#irradiance.calculate_beam_irradiance()
#irradiance.PV_generated_power(0.15, 1)
print(irradiance.get_dataset())

#irradiance.plot(['DiffRad'])
irradiance.calculate_beam_irradiance(latitude=latitude, tilt_angle=0, t_s=0, efficiency=0, area=0, day='2018-03-10 00:00',longitude=0,temperature=20)
