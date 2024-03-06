import os
import sys


sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import powercalculations.powercalculations as pc

file_path_irradiance = 'data/Irradiance_data_v2.xlsx'
file_path_load = 'data/Load_profile_6.xlsx'
irradiance=pc.PowerCalculations(file_path_irradiance=file_path_irradiance,file_path_load=file_path_load)

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
irradiance.calculate_direct_irradiance_specific(latitude=latitude, tilt_angle=0, day='2018-03-10 00:00',longitude=0,temperature=20)
print(irradiance.get_loadTOT_day())
