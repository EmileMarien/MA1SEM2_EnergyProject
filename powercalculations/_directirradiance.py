


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

    """
    OLDDDD
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