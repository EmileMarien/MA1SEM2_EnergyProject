import math
import pandas as pd
import pvlib


def calculate_direct_irradiance(self, latitude:int=0, tilt_angle:int=0,longitude:int=0,temperature:int=0): 
    """
    Calculates the direct irradiance on a solar panel for a specific time, day and colation
    """ 
    

    # Define a function to calculate the direct irradiance for a single row
    def calculate_irradiance_row(row, latitude, tilt_angle, longitude, temperature):
        GHI = row['GlobRad']
        GDI = row['DiffRad']
        
        day_datetime_index = row.name
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
        
        # Calculate Incidence Angle
        slope_angle = 0
        incidence_angle = math.acos(math.cos(slope_angle)*math.cos(solar_zenith_angle + math.sin(slope_angle)*math.sin()))

        # TODO: finish the calculation of the beam irradiance
        direct_irradiance = 1.0
        return direct_irradiance

    # Convert the string to a pandas Timestamp
    #day_datetime = pd.to_datetime(day)

    # Convert the Timestamp to a pandas DatetimeIndex
    #day_datetime_index = pd.DatetimeIndex([day_datetime])
    #day_datetime_index = entry.index
    # Irradiances at specific day
    #GHI=entry['GlobRad'] #Global Horizontal Irradiance
    #GDI=entry['DiffRad'] #Diffuse Horizontal Irradiance
    #GHI=self.pd.loc[self.pd['DateTime'] == day_datetime, 'GlobRad'] #Global Horizontal Irradiance
    #GDI=self.pd.loc[self.pd['DateTime'] == day_datetime, 'DiffRad'] #Diffuse Horizontal Irradiance

    # Apply the calculation function to each row with vectorized operations
    self.pd['DirectIrradiance'] = self.pd.apply(
        lambda row: calculate_irradiance_row(row=row, latitude=latitude, tilt_angle=tilt_angle, longitude=longitude,temperature=temperature), axis=1
    )

    return None
"""
def direct_irradiance(self):
    
    Calculates the direct irradiance on a solar panel of all the data in the dataset
    
    #TODO:check if this works
    self.pd['DirectIrradiance'] = self.pd.apply(calculate_direct_irradiance_specific,args=())
    return None
"""
