import math
import pvlib
counter = 0
length=0
def calculate_direct_irradiance(self, latitude:int=0, tilt_angle:int=0,longitude:int=0,orientation:str='S'): 
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
    def calculate_irradiance_row(row, tilt_angle,surface_azimuth_angle):
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
        global counter 
        global length
        counter += 1
        print(f"Calculating direct irradiance for row {counter}/{length}", end="\r")
        GHI = row['GlobRad']
        GDI = row['DiffRad']

        # Solar angles calculation

        solar_zenith_angle = row['SolarZenithAngle'] #float(A['zenith'].iloc[0]) # [degrees] starting from the vertical
        solar_azimuth_angle=row['SolarAzimuthAngle'] #float(A['azimuth'].iloc[0]) # [degrees] starting from the north

        # Beam Irradiance calculation

        # Calculate the Angle of Incidence (AOI)
        AOI = math.acos(
            math.cos(math.radians(tilt_angle)) * math.cos(math.radians(solar_zenith_angle)) +
            math.sin(math.radians(tilt_angle)) * math.sin(math.radians(solar_zenith_angle)) * math.cos(math.radians(solar_azimuth_angle - surface_azimuth_angle))
        ) # [radians]

        # Calculate the Direct Normal Irradiance (DNI)
        DNI = (GHI - GDI) / math.cos(math.radians(solar_zenith_angle)) # if the sun is above the horizon, calculate DNI
        
        # Calculate the Direct Irradiance which is the sum of the DNI and the GDI but limited to positive values
        direct_irradiance = max([DNI*math.cos(AOI),0]) + GDI

        # Limit the direct irradiance to the GHI value if the sun is close to the horizon
        if solar_zenith_angle > 87:
            direct_irradiance=min([GHI,direct_irradiance])
        
        return direct_irradiance, DNI

    #angles of azimuth
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
            lambda row: (calculate_irradiance_row(row=row, latitude=latitude, tilt_angle=tilt_angle, longitude=longitude,surface_azimuth_angle=90)+calculate_irradiance_row(row=row, latitude=latitude, tilt_angle=tilt_angle, longitude=longitude,surface_azimuth_angle=270))/2, axis=1
        )
        return None
    else:
        raise ValueError("Given orientation is unvalid or not implemented")
    

    global length
    length=self.pd.shape[0]
    global counter
    counter=0
    # Apply the calculation function to each row with vectorized operations
    self.pd['DirectIrradiance'] = self.pd.apply(
        lambda row: calculate_irradiance_row(row=row, latitude=latitude, tilt_angle=tilt_angle, longitude=longitude,surface_azimuth_angle=surface_azimuth_angle), axis=1
    )

    return None



def calculate_solar_angles(self, latitude:int=0, longitude:int=0):
    """
    Calculate the solar angles for each row in the DataFrame.

    Parameters:
    - latitude: Latitude of the location [degrees].
    - longitude: Longitude of the location [degrees].

    Returns:
    - None.
    """
    solar_zenith_angles = []  # List to store calculated solar zenith angles
    solar_azimuth_angles = []  # List to store calculated solar azimuth angles

    print("Calculating solar angles...", end="\r")
    for _, row in self.pd.iterrows():

        print(f"Calculating solar angles for row {row.name}", end="\r")
        # Solar angles calculation
        A = pvlib.solarposition.get_solarposition(time=row.name, latitude=latitude, longitude=longitude, temperature=row['T_RV_degC'])

        solar_zenith_angles.append(A['zenith'].iloc[0])     # [degrees] starting from the vertical
        solar_azimuth_angles.append(A['azimuth'].iloc[0])   # [degrees] starting from the north


    # Update DataFrame with calculated solar angles
    self.pd['SolarZenithAngle'] = solar_zenith_angles
    self.pd['SolarAzimuthAngle'] = solar_azimuth_angles

    return None




def calculate_irradiance_new(self, tilt_angle,orientation):
    
    GHI = self.pd['GlobRad']
    GDI = self.pd['DiffRad']

    # Solar angles calculation
        
    return None

