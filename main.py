import os
import sys
import pandas as pd
import pickle
from visualisations.visualisations import plot_dataframe, plot_series

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import powercalculations.powercalculations as pc
import gridcost.gridcost as gc

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
file=open('data/initialized_dataframes/pd_S_30','rb')
powercalculations_test=pickle.load(file)
powercalculations_test.add_EV_load(smart=False)

#powercalculations_test.filter_data_by_date_interval(start_date="2018-9-20 01:00",end_date="2018-9-30 01:00",interval_str="1h")
#powercalculations_test.PV_generated_power()
print("1")
#print("3")
#powercalculations_test.power_flow()
file.close()
#financials=gc.GridCost(powercalculations_test.get_grid_power()[0],file_path_BelpexFilter="data/BelpexFilter.xlsx")
print("0")

print(powercalculations_test.get_dataset())

#print("1")
#powercalculations_test.calculate_direct_irradiance()
#print("2")
print("2")
#powercalculations_test.plot_columns(["BatteryCharge", "GridFlow", "DirectIrradiance"])
#powercalculations_test.plot_columns(["PowerGrid"])

#print("4")
#powercalculations_test.nettoProduction()
#financials.dynamic_tariff()
#financials.dual_tariff()
#print("5")
#formatter = pd.option_context('display.max_rows', None, 'display.max_columns', None)
#print(irradiance.get_dataset())
#print("test")
# print(irradiance.get_average_per_hour('Load_kW'))
#with formatter:
    # print(powercalculations_test.get_grid_power())s
    #print(powercalculations_test.get_dataset())
    #print(powercalculations_test.get_columns(["Load_kW", "NettoProduction", "GridFlow", "BatteryCharge"]))
#    print(financials.get_columns(["DualTariff", "DynamicTariff", "BelpexFilter"]))

#irradiance.calculate_beam_irradiance()
#irradiance.PV_generated_power(0.15, 1)
#print(irradiance.get_dataset())
#irradiance.calculate_direct_irradiance(latitude=latitude, tilt_angle=0, day='2018-03-10 00:00',longitude=0,temperature=20)
#print(irradiance.get_loadTOT_day())
#plot_dataframe(financials.get_columns(["DynamicTariff", "DualTariff"]))
#plot_dataframe(powercalculations_test.get_columns(["Load_kW", "PV_generated_power", "GridFlow", "BatteryFlow", "BatteryCharge", "PowerLoss"]))
#plot_dataframe(financials.get_columns(["DynamicTariff", "DualTariff"]))