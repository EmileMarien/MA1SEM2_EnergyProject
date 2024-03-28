import os
import sys
import pandas as pd
import pickle
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import powercalculations.powercalculations as pc

#file_path_irradiance = 'data/Irradiance_data_v7.xlsx'
#file_path_load = 'data/Load_profile_6_v2.xlsx'
#file_path_combined = 'data/combined_data_v3.xlsx'
#irradiance=pc.PowerCalculations(file_path_combined=file_path_combined)
#file = open('data/combined_dataframe','rb')
#irradiance=pickle.load(file)
#file.close()

#print(irradiance.get_dataset())
#irradiance.export_dataframe_to_excel('test_output_v2.xlsx')
#irradiance.export_dataframe_to_excel('test_output.xlsx')
#formatter = pd.option_context('display.max_rows', None, 'display.max_columns', None)
#irradiance.interpolate_columns(interval='1h')
#irradiance.export_dataframe_to_excel('test_output.xlsx')
# GENK data
#latitude=50.99461 # [degrees]
#longitude=5.53972 # [degrees]
#start_date = '2018-03-12 00:00'
#end_date = '2018-03-16 18:00'
#interval = '1min'  # Interval of 1 hour
#irradiance.filter_data_by_date_interval(start_date, end_date, interval)
#with formatter:
#print(irradiance.get_dataset())
file=open('data/combined_dataframe_test','rb')
powercalculations_test=pickle.load(file)
file.close()
print(powercalculations_test.get_dataset())
powercalculations_test.filter_data_by_date_interval(start_date="2018-1-24 08:30",end_date="2018-1-25 08:30",interval_str="1h")
powercalculations_test.calculate_direct_irradiance()
powercalculations_test.PV_generated_power()
powercalculations_test.power_flow()
powercalculations_test.nettoProduction()
formatter = pd.option_context('display.max_rows', None, 'display.max_columns', None)
#print(irradiance.get_dataset())
#print("test")
# print(irradiance.get_average_per_hour('Load_kW'))
with formatter:
    # print(powercalculations_test.get_grid_power())s
    print(powercalculations_test.get_columns(["BatteryCharge", "GridFlow", "NettoProduction"]))

#irradiance.calculate_beam_irradiance()
#irradiance.PV_generated_power(0.15, 1)
#print(irradiance.get_dataset())
#irradiance.calculate_direct_irradiance(latitude=latitude, tilt_angle=0, day='2018-03-10 00:00',longitude=0,temperature=20)
#print(irradiance.get_loadTOT_day())