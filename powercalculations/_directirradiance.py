import math
import pvlib
def calculate_direct_irradiance(self, latitude:int=0, tilt_angle:int=0,longitude:int=0,temperature:int=0,orientation:str='N'): 
    #TODO: add documentation
    #TODO: check right angles of azimuth
    if orientation =="N":
        surface_azimuth_angle=180 # gamma_c [degrees]
    elif orientation=="E":
        surface_azimuth_angle=90
    elif orientation=="W":
        surface_azimuth_angle=-90
    elif orientation=="S":
        surface_azimuth_angle=0
    else:
        raise ValueError("Given orientation is unvalid or not implemented")
    

    # Define a function to calculate the direct irradiance for a single row
    def calculate_irradiance_row(row, latitude, tilt_angle, longitude, temperature,surface_azimuth_angle):
        GHI = row['GlobRad']
        GDI = row['DiffRad']
        #TODO: check if temperature can be taken from provided irradiance data in the excel sheet
        day_datetime_index = row.name
        # Solar angles calculation
        A = pvlib.solarposition.get_solarposition(day_datetime_index, latitude=latitude, longitude=longitude, temperature=temperature)

        solar_zenith_angle = float(A['zenith'].iloc[0])
        solar_azimuth_angle=float(A['azimuth'].iloc[0])

        # Beam Irradiance calculation

        # Calculate the Angle of Incidence (AOI)
        AOI = math.acos(
            math.cos(tilt_angle) * math.cos(solar_zenith_angle) +
            math.sin(tilt_angle) * math.sin(solar_zenith_angle) * math.cos(solar_azimuth_angle - surface_azimuth_angle)
        )

        # Calculate the Direct Normal Irradiance (DNI)
        DNI = (GHI - GDI) / math.cos(solar_zenith_angle)
        
        # Calculate Incidence Angle
        slope_angle = 0 #gamma_s
        incidence_angle = math.acos(math.cos(slope_angle)*math.cos(solar_zenith_angle) + math.sin(slope_angle)*math.sin(solar_zenith_angle)*math.cos(solar_azimuth_angle-surface_azimuth_angle))

        # calculate direct irradiance
        direct_irradiance = DNI*math.cos(incidence_angle) + GDI
        return direct_irradiance


    # Apply the calculation function to each row with vectorized operations
    self.pd['DirectIrradiance'] = self.pd.apply(
        lambda row: calculate_irradiance_row(row=row, latitude=latitude, tilt_angle=tilt_angle, longitude=longitude,temperature=temperature,surface_azimuth_angle=surface_azimuth_angle), axis=1
    )

    return None

