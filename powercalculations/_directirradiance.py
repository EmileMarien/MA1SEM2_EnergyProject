import math
import pandas as pd
import pvlib


def calculate_direct_irradiance_specific(self, latitude:int=0, tilt_angle:int=0, day:str='2018-03-10 00:00',longitude:int=0,temperature:int=0): 
    """
    Calculates the direct irradiance on a solar panel for a specific time, day and colation
    """ 

    # Convert the string to a pandas Timestamp
    day_datetime = pd.to_datetime(day)

    # Convert the Timestamp to a pandas DatetimeIndex
    day_datetime_index = pd.DatetimeIndex([day_datetime])

    # Irradiances at specific day
    GHI=self.pd.loc[self.pd['DateTime'] == day_datetime, 'GlobRad'] #Global Horizontal Irradiance
    GDI=self.pd.loc[self.pd['DateTime'] == day_datetime, 'DiffRad'] #Diffuse Horizontal Irradiance

    # Solar angles calculation
    A = pvlib.solarposition.get_solarposition(day_datetime_index, latitude=latitude, longitude=longitude, temperature=temperature)

    solar_zenith_angle = float(A['zenith'].iloc[0])
    solar_azimuth_angle=float(A['azimuth'].iloc[0])
    surface_azimuth_angle=0 # gamma_c [degrees]

    # Beam Irradiance calculation

    # Calculate the Angle of Incidence (AOI)
    AOI = math.acos(
        math.cos(tilt_angle) * math.cos(solar_zenith_angle) +
        math.sin(tilt_angle) * math.sin(solar_zenith_angle) * math.cos(solar_azimuth_angle - surface_azimuth_angle)
    )

    # Calculate the Direct Normal Irradiance (DNI)
    DNI = (GHI - GDI) / math.cos(solar_zenith_angle)
    
    # TODO: finish the calculation of the beam irradiance
    direct_irradiance = 0
    return direct_irradiance


def direct_irradiance(self):
    """
    Calculates the direct irradiance on a solar panel of all the data in the dataset
    """
    #TODO:check if this works
    self.pd['DirectIrradiance'] = self.pd['dayTime'].apply(calculate_direct_irradiance_specific)
    return None