import os
import sys
import pandas as pd
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import powercalculations.powercalculations as pc

file_path_irradiance = 'data/Irradiance_data_v7.xlsx'
file_path_load = 'data/Load_profile_6_v2.xlsx'
file_path_combined = 'data/combined_data_v3.xlsx'
irradiance=pc.PowerCalculations(file_path_combined=file_path_combined)
#irradiance.interpolate_columns(interval='1min')
irradiance.export_dataframe_to_excel('test_output.xlsx')
formatter = pd.option_context('display.max_rows', None, 'display.max_columns', None)
print(irradiance.get_dataset())
#irradiance.interpolate_columns(interval='1h')
#irradiance.export_dataframe_to_excel('test_output.xlsx')
# GENK data
latitude=50.99461 # [degrees]
longitude=5.53972 # [degrees]
start_date = '2018-03-12 00:00'
end_date = '2018-03-16 18:00'
interval = '1h'  # Interval of 1 hour
irradiance.filter_data_by_date_interval(start_date, end_date, interval)
formatter = pd.option_context('display.max_rows', None, 'display.max_columns', None)
with formatter:
    print(irradiance.get_irradiance())

#irradiance.calculate_beam_irradiance()
#irradiance.PV_generated_power(0.15, 1)
#print(irradiance.get_dataset())
#irradiance.calculate_direct_irradiance(latitude=latitude, tilt_angle=0, day='2018-03-10 00:00',longitude=0,temperature=20)
#print(irradiance.get_loadTOT_day())
