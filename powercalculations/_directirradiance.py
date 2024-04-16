import math
import pvlib
def calculate_direct_irradiance(self, latitude:int=0, tilt_angle:int=0,longitude:int=0,temperature:int=0,orientation:str='N'): 
    """
    Calculate the direct irradiance on a tilted surface for each row in the DataFrame.

    Parameters:
    - latitude: Latitude of the location [degrees].
    - tilt_angle: Tilt angle of the surface [degrees].
    - longitude: Longitude of the location [degrees].
    - temperature: Temperature of the location [degrees Celsius].
    - orientation: Orientation of the surface [N, E, W, S].

    Returns:
    - None.
    """

    # Define a function to calculate the direct irradiance for a single row
    def calculate_irradiance_row(row, latitude, tilt_angle, longitude, temperature,surface_azimuth_angle):
        """
        Calculate the direct irradiance on a tilted surface for a single row in the DataFrame.
        
        Parameters:
        - row: Row in the DataFrame.
        - latitude: Latitude of the location [degrees].
        - tilt_angle: Tilt angle of the surface [degrees].
        - longitude: Longitude of the location [degrees].
        - temperature: Temperature of the location [degrees Celsius].
        - surface_azimuth_angle: Azimuth angle of the surface [degrees].
        """

        GHI = row['GlobRad']
        GDI = row['DiffRad']
        temperature2= row['T_RV_degC']
        #TODO: check if temperature can be taken from provided irradiance data in the excel sheet
        day_datetime_index = row.name
        # Solar angles calculation
        A = pvlib.solarposition.get_solarposition(day_datetime_index, latitude=latitude, longitude=longitude, temperature=temperature2)

        solar_zenith_angle = float(A['zenith'].iloc[0]) # [degrees] starting from the vertical
        solar_azimuth_angle=float(A['azimuth'].iloc[0]) # [degrees] starting from the north

        # Beam Irradiance calculation

        # Calculate the Angle of Incidence (AOI)
        AOI = math.acos(
            math.cos(math.radians(tilt_angle)) * math.cos(math.radians(solar_zenith_angle)) +
            math.sin(math.radians(tilt_angle)) * math.sin(math.radians(solar_zenith_angle)) * math.cos(math.radians(solar_azimuth_angle - surface_azimuth_angle))
        ) # [radians]

        # Calculate the Direct Normal Irradiance (DNI)
        if solar_zenith_angle > 90:
            DNI = 0 # if the sun is below the horizon, no direct irradiance
        else:
            DNI = (GHI - GDI) / math.cos(math.radians(solar_zenith_angle)) # if the sun is above the horizon, calculate DNI
        
        # calculate direct irradiance
        direct_irradiance = DNI*math.cos(AOI) + GDI
        if direct_irradiance<0:
            #print(GHI,GDI,AOI,DNI,solar_zenith_angle)
            direct_irradiance=0
        
        return direct_irradiance

    #TODO: check right angles of azimuth
    if orientation =="N":
        surface_azimuth_angle=0 # gamma_c [degrees]
    elif orientation=="E":
        surface_azimuth_angle=90
    elif orientation=="W":
        surface_azimuth_angle=270
    elif orientation=="S":
        surface_azimuth_angle=180
    elif orientation=="EW":
        # Calculate the direct irradiance for both "E" and "W" orientations
        # Apply the calculation function to each row with vectorized operations
        self.pd['DirectIrradiance'] = self.pd.apply(
            lambda row: (calculate_irradiance_row(row=row, latitude=latitude, tilt_angle=tilt_angle, longitude=longitude,temperature=temperature,surface_azimuth_angle=90)+calculate_irradiance_row(row=row, latitude=latitude, tilt_angle=tilt_angle, longitude=longitude,temperature=temperature,surface_azimuth_angle=270))/2, axis=1
        )
        return None
    else:
        raise ValueError("Given orientation is unvalid or not implemented")
    


    # Apply the calculation function to each row with vectorized operations
    self.pd['DirectIrradiance'] = self.pd.apply(
        lambda row: calculate_irradiance_row(row=row, latitude=latitude, tilt_angle=tilt_angle, longitude=longitude,temperature=temperature,surface_azimuth_angle=surface_azimuth_angle), axis=1
    )

    return None

