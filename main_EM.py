


import math
import pickle

import pandas as pd
from gridcost.gridcost import GridCost
from visualisations.visualisations import plot_dataframe, plot_series
import matplotlib.dates as md

# Load dataset


file= open('data/initialized_dataframes/pd_S_30','rb')
irradiance_pd_S_30=pickle.load(file)
file.close()

### Calculations for the S 30 scenario
#irradiance_pd_S_30.nettoProduction()
# Calculate the PV power output

panel_count=6
print('start calculations')
irradiance_pd_S_30.PV_generated_power(panel_count=panel_count)
financials=GridCost(irradiance_pd_S_30.get_grid_power()[0],file_path_BelpexFilter="data/BelpexFilter.xlsx")
# calculate the power flow
max_charge= 8 #kWh
max_AC_power_output= 5
max_DC_batterypower_output= 5
#irradiance_pd_S_30.power_flow(max_charge, max_AC_power_output, max_DC_batterypower_output)
irradiance_pd_S_30.nettoProduction()
financials=GridCost(irradiance_pd_S_30.get_grid_power()[0],file_path_BelpexFilter="data/BelpexFilter.xlsx")

### Calculations for the other scenarios
calculate_others=False
if calculate_others:
    file = open('data/initialized_dataframes/pd_EW_30','rb')
    irradiance_pd_EW_30=pickle.load(file)
    file.close()

    file = open('data/initialized_dataframes/pd_E_30','rb')
    irradiance_pd_E_30=pickle.load(file)
    file.close()

    file = open('data/initialized_dataframes/pd_W_30','rb')
    irradiance_pd_W_30=pickle.load(file)
    file.close()

    file= open('data/initialized_dataframes/pd_S_30','rb')
    irradiance_summer=pickle.load(file)
    file.close()

    file= open('data/initialized_dataframes/pd_S_30','rb')
    irradiance_winter=pickle.load(file)
    file.close()

    file= open('data/initialized_dataframes/pd_EW_opt_32','rb')
    irradiance_pd_EW_opt=pickle.load(file)
    file.close()

    file= open('data/initialized_dataframes/pd_S_opt_37.5','rb')
    irradiance_pd_S_opt=pickle.load(file)
    file.close()

    #irradiance_summer.filter_data_by_date_interval('2018-06-01','2018-08-31',interval_str='1h')
    #irradiance_winter.filter_data_by_date_interval('2018-12-01','2019-02-28',interval_str='1h')
    # Calculate the netto production
    #irradiance_pd_EW_30.nettoProduction()
    irradiance_pd_S_30.nettoProduction()
    #irradiance_pd_EW_opt.nettoProduction()
    #irradiance_pd_S_opt.nettoProduction()

    # Calculate the PV power output
    cell_area=20
    panel_count=1
    T_STC=25
    Temp_coeff=-0.0026
    efficiency_max=0.2
    #irradiance_pd_EW_30.PV_generated_power(cell_area, panel_count, T_STC, Temp_coeff, efficiency_max)
    irradiance_pd_S_30.PV_generated_power(cell_area, panel_count, T_STC, Temp_coeff, efficiency_max)
    #irradiance_pd_EW_opt.PV_generated_power(cell_area, panel_count, T_STC, Temp_coeff, efficiency_max)
    #irradiance_pd_S_opt.PV_generated_power(cell_area, panel_count, T_STC, Temp_coeff, efficiency_max)

    # calculate the power flow
    max_charge= 8
    max_AC_power_output= 5
    max_DC_batterypower_output= 5
    #irradiance_pd_EW_30.power_flow(max_charge, max_AC_power_output, max_DC_batterypower_output)
    irradiance_pd_S_30.power_flow(max_charge, max_AC_power_output, max_DC_batterypower_output)
    #irradiance_pd_EW_opt.power_flow(max_charge, max_AC_power_output, max_DC_batterypower_output)
    #irradiance_pd_S_opt.power_flow(max_charge, max_AC_power_output, max_DC_batterypower_output)



#### Plots underneath
print('start plots')
# Plot hourly direct irradiance for the different orientations and 30 degree angles
plot_hourly_direct_irradiance=False #OK
if plot_hourly_direct_irradiance:
    #irradiance_pd_EW_30=irradiance_pd_EW_30.calculate_direct_irradiance(tilt_angle=30,orientation='EW')
    hourly_irradiance_pd_EW_30=irradiance_pd_EW_30.get_average_per_minute_day('DirectIrradiance') #30 degrees tilt angle
    hourly_irradiance_pd_EW_30.name='EW 30 degrees'
    #irradiance_pd_S_30=irradiance_pd_S_30.calculate_direct_irradiance(tilt_angle=30,orientation='S')
    hourly_irradiance_pd_S_30=irradiance_pd_S_30.get_average_per_minute_day('DirectIrradiance') #30 degrees tilt angle
    hourly_irradiance_pd_S_30.name='S 30 degrees'
    #irradiance_pd_E_30=irradiance_pd_EW_30.calculate_direct_irradiance(tilt_angle=30,orientation='E')
    hourly_irradiance_pd_E_30=irradiance_pd_E_30.get_average_per_minute_day('DirectIrradiance') #30 degrees tilt angle
    hourly_irradiance_pd_E_30.name='E 30 degrees'
    #irradiance_pd_W_30=irradiance_pd_EW_30.calculate_direct_irradiance(tilt_angle=30,orientation='EW')
    hourly_irradiance_pd_W_30=irradiance_pd_W_30.get_average_per_minute_day('DirectIrradiance') #30 degrees tilt angle
    hourly_irradiance_pd_W_30.name='W 30 degrees'
    hourly_series_30=[hourly_irradiance_pd_EW_30,hourly_irradiance_pd_S_30,hourly_irradiance_pd_E_30,hourly_irradiance_pd_W_30]
    #hourly_irradiance_pd_EW_opt=irradiance_pd_EW_opt.get_average_per_hour('DirectIrradiance') #optimal tilt angle
    #hourly_irradiance_pd_S_opt=irradiance_pd_S_opt.get_average_per_hour('DirectIrradiance') #optimal tilt angle
    #hourly_series_opt=[hourly_irradiance_pd_EW_opt,hourly_irradiance_pd_S_opt]
    plot_series(hourly_series_30,title='Hourly average incident irradiance for the household under study, 30 degrees tilt angle for different orientations',xlabel="Time",ylabel='Power $[\mathrm{\\frac{W}{m^2}}]$',display_time='hour')

# Plot direct irradiance of 30, Z
plot_direct_irradiance_30=False
if plot_direct_irradiance_30:
    hourly_direct_irradiance_pd_S_30=irradiance_pd_S_30.get_columns(['DirectIrradiance']).squeeze() 
    hourly_direct_irradiance_pd_S_30.name='S 30 degrees'
    plot_series([hourly_direct_irradiance_pd_S_30],title='Hourly average incident irradiance for the household under study, 30 degrees tilt angle for the South orientation',xlabel="Day",ylabel='Power $[\mathrm{\\frac{W}{m^2}}]$',display_time='yearly')

# Plot the load for the period of december to show the difference between the reference and predicted load
plot_load_dec=False #OK
if plot_load_dec:
    irradiance_pd_S_30.filter_data_by_date_interval('2018-12-01 0:00','2018-12-31 23:00',interval_str='1h')
    hourly_load_nov_dec = irradiance_pd_S_30.get_columns(['Load_kW']).squeeze()

    # Split the series into two parts based on the date
    before_dec_17 = hourly_load_nov_dec.loc[:'2018-12-17 00:00']
    before_dec_17.name='Reference load'
    after_dec_17 = hourly_load_nov_dec.loc['2018-12-17 01:00':]
    after_dec_17.name='Predicted load'

    plot_series([before_dec_17,after_dec_17],display_time='yearly',title='Comparison of the referenced and predicted load',xlabel='Day',ylabel='Power [kW]')

# PLot the GHI and GDI for feb-march to show the difference between the reference and predicted load
plot_GHI_GDI=False #OK
if plot_GHI_GDI:
    irradiance_pd_S_30.filter_data_by_date_interval('2018-02-01 0:00','2018-03-31 23:00',interval_str='1h')
    hourly_GHI_feb_march = irradiance_pd_S_30.get_columns(['GlobRad']).squeeze()
    hourly_GDI_feb_march = irradiance_pd_S_30.get_columns(['DiffRad']).squeeze()

    # Split the series into two parts based on the date
    GHI_feb = hourly_GHI_feb_march.loc[:'2018-03-13 00:00':]
    GHI_feb.name='Global horizontal irradiance, reference'
    GHI_march = hourly_GHI_feb_march.loc['2018-03-13 01:00':]
    GHI_march.name='Global horizontal irradiance, external data'

    GDI_feb = hourly_GDI_feb_march.loc[:'2018-03-13 00:00':]
    GDI_feb.name='Diffuse horizontal irradiance, reference'
    GDI_march = hourly_GDI_feb_march.loc['2018-03-13 01:00':]
    GDI_march.name='Diffuse horizontal irradiance, external data'

    hourly_series=[GHI_feb,GHI_march,GDI_feb,GDI_march]

    

    plot_series(hourly_series,display_time='yearly',title='Global and diffuse horizontal irradiance for the first irradiance gap',xlabel='Day',ylabel='Power $[\mathrm{\\frac{W}{m^2}}]$')

# Plot hourly direct irradiance for the different orientations and optimal tilt angles
plot_hourly_direct_irradiance=False #OK
if plot_hourly_direct_irradiance:
    #irradiance_pd_EW_30.calculate_direct_irradiance(tilt_angle=30,orientation='EW')
    hourly_irradiance_pd_EW_opt=irradiance_pd_EW_opt.get_average_per_minute_day('DirectIrradiance') 
    #30 degrees tilt angle
    hourly_irradiance_pd_EW_opt.name='EW optimal'


    #irradiance_pd_S_30=irradiance_pd_S_30.calculate_direct_irradiance(tilt_angle=30,orientation='S')
    hourly_irradiance_pd_S_opt=irradiance_pd_S_opt.get_average_per_minute_day('DirectIrradiance') #30 degrees tilt angle
    hourly_irradiance_pd_S_opt.name='S optimal'
    hourly_series_opt=[hourly_irradiance_pd_EW_opt,hourly_irradiance_pd_S_opt]

    plot_series(hourly_series_opt,title='Hourly average incident irradiance for the household under study, optimal tilt angle for different orientations',xlabel="Time",ylabel='Power $[\mathrm{\\frac{W}{m^2}}]$',display_time='hour')

# Print average net load consumption for the different orientations and tilt angles

# Plot comparison of direct, global and diffuse irradiance for S 30 scenario, winter 
## Mean irradiance during summer and winter (GHI, DHI, DNI)
plot_comparison_irradiance=False #OK
if plot_comparison_irradiance:
    irradiance_pd_S_30.filter_data_by_date_interval('2018-06-21 0:00','2018-09-20 23:00',interval_str='1min') #Summer OK
    #irradiance_pd_S_30.filter_data_by_date_interval('2018-12-21 0:00','2019-03-20 23:00',interval_str='1min') #Winter
    irradiance_pd_S_30.calculate_direct_irradiance(tilt_angle=30,orientation='S')
    hourly_d_irradiance_pd_S_30=irradiance_pd_S_30.get_average_per_minute_day('DNI')
    hourly_d_irradiance_pd_S_30.name='Direct normal irradiance'
    hourly_global_irradiance_pd_S_30=irradiance_pd_S_30.get_average_per_minute_day('GlobRad')
    hourly_global_irradiance_pd_S_30.name='Global horizontal irradiance'
    hourly_diffuse_irradiance_pd_S_30=irradiance_pd_S_30.get_average_per_minute_day('DiffRad')
    hourly_diffuse_irradiance_pd_S_30.name='Diffuse horizontal irradiance'
    #hourly_direct_irradiance_pd_S_30=irradiance_pd_S_30.get_average_per_minute_day('DirectIrradiance')
    hourly_series=[hourly_d_irradiance_pd_S_30,hourly_global_irradiance_pd_S_30,hourly_diffuse_irradiance_pd_S_30,]
    plot_series(hourly_series,title='Comparison of the different irradiances during summer',xlabel='Time',ylabel='Power $[\mathrm{\\frac{W}{m^2}}]$',display_time='hour')

# Plot minutely nettoproduction per day for the S 30 scenario
plot_minutely_nettoproduction=False
if plot_minutely_nettoproduction:
    irradiance_pd_S_30.filter_data_by_date_interval('2018-01-01 1:00','2018-12-30 23:00',interval_str='1min')
    minutely_nettoproduction_pd_S_30=irradiance_pd_S_30.get_average_per_minute_day('NettoProduction')
    hourly_battery_charge_pd_S_30 = irradiance_pd_S_30.get_average_per_minute_day('BatteryCharge')
    minutely_series=[minutely_nettoproduction_pd_S_30]
    plot_series(series=minutely_series,title='Minutely average netto production for S 30 scenario')#,secondary_series=[hourly_battery_charge_pd_S_30],xlabel='Time',ylabel='Power [kWh]',ylabel2='Battery charge (kWh)')

power_flow_one_day = True
if power_flow_one_day:
    irradiance_pd_S_30.filter_data_by_date_interval(start_date="2018-6-5 0:00",end_date="2018-6-7 23:00",interval_str="1min")
    # irradiance_pd_S_30.filter_data_by_date_interval(start_date="2018-2-03 0:00",end_date="2018-2-04 0:00",interval_str="1min")
    irradiance_pd_S_30.power_flow_old()
    load = irradiance_pd_S_30.get_columns(["Load_kW"]).squeeze()
    PV_generated_power = irradiance_pd_S_30.get_columns(["PV_generated_power"]).squeeze()
    grid_flow = irradiance_pd_S_30.get_columns(["GridFlow"]).squeeze()
    battery_flow = irradiance_pd_S_30.get_columns(["BatteryFlow"]).squeeze()
    power_loss = irradiance_pd_S_30.get_columns(["PowerLoss"]).squeeze()
    battery_charge = irradiance_pd_S_30.get_columns(["BatteryCharge"]).squeeze()
    series_flows = [load, PV_generated_power, grid_flow, battery_flow, power_loss]
    series_battery = [battery_charge]
    plot_series(series=series_flows,title='Power flows and battery charge for a summer day',secondary_series=series_battery,xlabel='Time',ylabel='Power plow [kW]',ylabel2='Battery charge [kWh]')

# Plot hourly flows (pv-load) 
plot_minutely_flows=False
if plot_minutely_flows:
    irradiance_pd_S_30.filter_data_by_date_interval('2018-08-01 0:00','2018-09-01 0:00',interval_str='1min')
    # irradiance_pd_S_30.filter_data_by_date_interval('2018-01-01 0:00','2018-02-01 0:00',interval_str='1min')
    irradiance_pd_S_30.power_flow_old()
    hourly_pv_generated_power_pd_S_30=irradiance_pd_S_30.get_average_per_minute_day('PV_generated_power')
    hourly_load_pd_S_30=irradiance_pd_S_30.get_average_per_minute_day('Load_kW')
    hourly_netto_production_pd_S_30=irradiance_pd_S_30.get_average_per_minute_day('NettoProduction')
    hourly_battery_charge_pd_S_30=irradiance_pd_S_30.get_average_per_minute_day('BatteryCharge')
    hourly_grid_flow_pd_S_30=irradiance_pd_S_30.get_average_per_minute_day('GridFlow')
    hourly_battery_flow_pd_S_30=irradiance_pd_S_30.get_average_per_minute_day('BatteryFlow')
    hourly_series=[hourly_netto_production_pd_S_30, hourly_pv_generated_power_pd_S_30, hourly_load_pd_S_30, hourly_grid_flow_pd_S_30, hourly_battery_flow_pd_S_30]
    plot_series(series=hourly_series,title='Hourly average power flows for S 30 scenario, summer',secondary_series=[hourly_battery_charge_pd_S_30],xlabel='hours',ylabel='Power [kW]',ylabel2='Battery charge (kWh)',display_time='hour')

# Plot average hourly load consumption for winter and summer
plot_average_load_consumption=False
if plot_average_load_consumption:
    hourly_load_summer=irradiance_summer.get_average_per_hour('Load_kW').rename('Summer')
    hourly_load_winter=irradiance_winter.get_average_per_hour('Load_kW').rename('Winter')
    hourly_series=[hourly_load_summer,hourly_load_winter]
    plot_series(hourly_series)

# Plot hourly load consumption for each day of the weak on one graph
plot_weekly_load_consumption=False #OK
if plot_weekly_load_consumption:

    #irradiance_pd_S_30.filter_data_by_date_interval('2018-06-01 1:00','2018-09-30 23:00',interval_str='1min')
    print(irradiance_pd_S_30.get_dataset())
    hourly_load_pd_S_30=irradiance_pd_S_30.get_columns(['Load_kW'])

    # Extract hour and minute from DateTimeIndex
    hourly_load_pd_S_30['hour'] = hourly_load_pd_S_30.index.hour
    hourly_load_pd_S_30['minute'] = hourly_load_pd_S_30.index.minute

    # Create an empty list to store the Series
    daily_load_series_list = []
    # List of day names
    day_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

    # Iterate over the days of the week
    for day in range(5):  # 0 represents Monday, 1 represents Tuesday, ..., 6 represents Sunday
        # Filter rows where the DateTimeIndex corresponds to the current day
        day_rows = hourly_load_pd_S_30[hourly_load_pd_S_30.index.dayofweek == day]
        
        # Group by hour and minute and calculate average value for the current day
        average_load_by_hour_minute = day_rows.groupby(['hour', 'minute'])['Load_kW'].mean()
        average_load_by_hour_minute.index = [f"{x[0]:02d}:{x[1]:02d}" for x in average_load_by_hour_minute.index]
        average_load_by_hour_minute.name=day_names[day]
        print(average_load_by_hour_minute)
        # Append the Series to the list
        daily_load_series_list.append(average_load_by_hour_minute)
    plot_series(daily_load_series_list,display_time='hour',title='Hourly load consumption for each weekday',xlabel='Hour of the day',ylabel='Power [kW]')

# Plot hourly belpex for the week
plot_weekly_nettoproduction_belpex_consumption=False #OK
if plot_weekly_nettoproduction_belpex_consumption:
    irradiance_pd_S_30.filter_data_by_date_interval('2018-01-01 1:00','2018-12-31 23:00',interval_str='1h')
    #irradiance_pd_S_30.filter_data_by_date_interval('2018-06-01 1:00','2018-09-30 23:00',interval_str='1min')
    hourly_belpex=financials.get_columns(['BelpexFilter'])
    hourly_nettoproduction = irradiance_pd_S_30.get_columns(['NettoProduction'])
    # Extract hour and minute from DateTimeIndex
    hourly_belpex['hour'] = hourly_belpex.index.hour
    hourly_belpex['minute'] = hourly_belpex.index.minute
    hourly_nettoproduction['hour'] = hourly_nettoproduction.index.hour
    hourly_nettoproduction['minute'] = hourly_nettoproduction.index.minute

    daily_price_series_list= []
    daily_load_series_list = []

    # Filter rows where the DateTimeIndex corresponds to a weekday
    weekday_rows = hourly_belpex[(hourly_belpex.index.dayofweek >= 0) & (hourly_belpex.index.dayofweek <= 4)]
    weekday_nettoproduction_rows = hourly_nettoproduction[(hourly_nettoproduction.index.dayofweek >= 0) & (hourly_nettoproduction.index.dayofweek <= 4)]
    #weekendday_rows = hourly_belpex[(hourly_belpex.index.dayofweek >= 5) & (hourly_belpex.index.dayofweek <= 6)]

    # Group by hour and minute and calculate average value for the current day
    average_weekdayprice_by_hour_minute = weekday_rows.groupby(['hour', 'minute'])['BelpexFilter'].mean()
    average_weekdayprice_by_hour_minute.index = [f"{x[0]:02d}:{x[1]:02d}" for x in average_weekdayprice_by_hour_minute.index]
    average_weekdayprice_by_hour_minute.name='Average weekday belpexprice'
    print(average_weekdayprice_by_hour_minute)
    average_weekday_production_by_hour_minute = weekday_nettoproduction_rows.groupby(['hour','minute'])['NettoProduction'].mean()
    average_weekday_production_by_hour_minute.index = [f"{x[0]:02d}:{x[1]:02d}" for x in average_weekday_production_by_hour_minute.index]
    average_weekday_production_by_hour_minute.name='Average weekday netto production'
    print(average_weekday_production_by_hour_minute)
    # Append the Series to the list
    daily_price_series_list.append(average_weekdayprice_by_hour_minute)
    daily_load_series_list.append(average_weekday_production_by_hour_minute)

    # Filter rows where the DateTimeIndex corresponds to a weekendday
    weekendday_rows = hourly_belpex[(hourly_belpex.index.dayofweek >= 5) & (hourly_belpex.index.dayofweek <= 6)]
    weekendday_production_rows = hourly_nettoproduction[(hourly_nettoproduction.index.dayofweek >= 5) & (hourly_nettoproduction.index.dayofweek <= 6)]

    # Group by hour and minute and calculate average value for the current day
    average_weekenddayprice_by_hour_minute = weekendday_rows.groupby(['hour', 'minute'])['BelpexFilter'].mean()
    average_weekenddayprice_by_hour_minute.index = [f"{x[0]:02d}:{x[1]:02d}" for x in average_weekenddayprice_by_hour_minute.index]
    average_weekenddayprice_by_hour_minute.name='Average weekend belpexprice'
    print(average_weekenddayprice_by_hour_minute)
    average_weekendday_production_by_hour_minute = weekendday_production_rows.groupby(['hour', 'minute'])['NettoProduction'].mean()
    average_weekendday_production_by_hour_minute.index = [f"{x[0]:02d}:{x[1]:02d}" for x in average_weekendday_production_by_hour_minute.index]
    average_weekendday_production_by_hour_minute.name = 'Average weekend netto production'
    # Append the Series to the list
    daily_price_series_list.append(average_weekenddayprice_by_hour_minute)
    daily_load_series_list.append(average_weekendday_production_by_hour_minute)


    plot_series(daily_price_series_list,display_time='hour',title='Average hourly belpex price',xlabel='Hour of the day',ylabel='Price [€/MWh]')
    plot_series(daily_load_series_list,display_time='hour',title='Average hourly net production',xlabel='Hour of the day',ylabel='Net production [kW]')

# Plot the total irradiance for the S orientations and iterate over the different tilt angles
plot_total_irradiance=False #OK
if plot_total_irradiance:
    # Define the tilt angles
    indices=['20.0', '20.5', '21.0', '21.5', '22.0', '22.5', '23.0', '23.5', '24.0', '24.5', '25.0', '25.5', '26.0', '26.5', '27.0', '27.5', '28.0', '28.5', '29.0', '29.5', '30.0', '30.5', '31.0', '31.5', '32.0', '32.5', '33.0', '33.5', '34.0', '34.5', '35.0', '35.5', '36.0', '36.5', '37.0', '37.5', '38.0', '38.5', '39.0', '39.5', '40.0', '40.5', '41.0', '41.5', '42.0', '42.5', '43.0', '43.5', '44.0', '44.5', '45.0', '45.5', '46.0', '46.5', '47.0', '47.5', '48.0', '48.5', '49.0', '49.5', '50.0']
    # Create a series with the total irradiance for S and different tilt angles:
    tilt_angles_S={'20.0': 134.6733500664645, '20.5': 134.86101097040967, '21.0': 135.04351846662593, '21.5': 135.22085814248638, '22.0': 135.3929828524523, '22.5': 135.559873823752, '23.0': 135.7215118370833, '23.5': 135.8778181342936, '24.0': 136.02889510319514, '24.5':136.17488445770132,'25.0': 136.31571925627287,
    '25.5': 136.4513030275388,
    '26.0': 136.5814943216128,
    '26.5': 136.70627636033257,
    '27.0': 136.8256328248779,
    '27.5': 136.93956628714298,
    '28.0': 137.0480302471163,
    '28.5': 137.15103627540202,
    '29.0': 137.24868006677346,
    '29.5': 137.3409980045969,
    '30.0': 137.42792135645485,
    '30.5': 137.50944092988402,
    '31.0': 137.58554643926908,
    '31.5': 137.65625904757252,
    '32.0': 137.72166906030182,
    '32.5': 137.78182065294712,
    '33.0': 137.83660712044198,
    '33.5': 137.88587443813057,
    '34.0': 137.92967057507997,
    '34.5': 137.96793489637463,
    '35.0': 138.00066586914687,
    '35.5': 138.02789518181137,
    '36.0': 138.04965075338473,
    '36.5': 138.06597153487738,
    '37.0': 138.07681383460672,
    '37.5': 138.08223921791262,
    '38.0': 138.08216450380328,'38.5': 138.07656378165458, '39.0': 138.06549048166548, '39.5': 138.04902631848418, '40.0': 138.02714842539928, '40.5': 137.99978490817443, '41.0': 137.96724181156893, '41.5': 137.92949917526514, '42.0': 137.88629628974223}

    irradiances_S = pd.Series(data=tilt_angles_S, index=indices)
    irradiances_S.name = 'Mean incident irradiance'

    # Plot the total irradiance for the different orientations and tilt angles
    plot_series([irradiances_S], title='Mean yearly incident irradiance for the S orientation and different tilt angles', xlabel='Tilt angle [degrees]', ylabel='Power $[\mathrm{\\frac{W}{m^2}}]$')

# Print the influence of the EV load on the grid flow
print_EV_influence=False
if print_EV_influence:
    irradiance_pd_S_30.filter_data_by_date_interval('2018-06-05 0:00','2018-06-11 23:00',interval_str='1min')
    irradiance_pd_S_30.power_flow(max_charge=5, max_AC_power_output=max_AC_power_output, max_DC_batterypower=2,EV_type='no_SC') # other EV types: 'no_EV', 'with_SC', 'no_SC', 'B2G
    irradiances_S_30_EV=irradiance_pd_S_30.get_columns(['GridFlow']).squeeze()
    irradiances_S_30_EV.name='GridFLow'
    irradiance_pd_S_30.nettoProduction()
    net_production=irradiance_pd_S_30.get_columns(['NettoProduction']).squeeze()
    net_production.name='NettoProduction'

    EV_flow=irradiance_pd_S_30.get_columns(['EVFlow']).squeeze()
    #print(irradiance_pd_S_30.get_columns(['Load_EV_kW_with_SC']))
    EV_charge=irradiance_pd_S_30.get_columns(['EVCharge']).squeeze()
    battery_charge=irradiance_pd_S_30.get_columns(['BatteryCharge']).squeeze()
    battery_flow = irradiance_pd_S_30.get_columns(['BatteryFlow']).squeeze()
    # formatter = pd.option_context('display.max_rows', None, 'display.max_columns', None)
    #with formatter:
     #   print(irradiance_pd_S_30.get_columns(['NettoProduction','GridFlow','EVFlow','EVCharge']))
    #print(irradiance_pd_S_30.get_columns(['Load_EV_kW_with_SC','Load_EV_kW_no_SC']))
    plot_series([EV_flow],title='Influence of the EV load on the grid flow',xlabel='Time',ylabel='Power [kW]',display_time='yearly',secondary_series=[EV_charge],ylabel2='EV charge [kW]')

# Return key figures
print_key_figures=False
if print_key_figures:
    print("the total power consumption is:",irradiance_pd_S_30)


# Print the total solar energy generated from 50 solar panels to see why load still exists when the solar panels are generating MUCH power
print_total_solar_energy=False
if print_total_solar_energy:
    irradiance_pd_S_30.PV_generated_power(panel_count=1)
    irradiance_pd_S_30.nettoProduction()
    PV_power=irradiance_pd_S_30.get_columns(['PV_generated_power']).squeeze()*1000
    load=irradiance_pd_S_30.get_columns(['Load_kW']).squeeze()*1000
    irradiance=irradiance_pd_S_30.get_columns(['DirectIrradiance']).squeeze()/1000
    netto_production=irradiance_pd_S_30.get_columns(['NettoProduction']).squeeze()*1000
    print(netto_production)
    netto_production.name='Netto production'
    plot_series([netto_production,PV_power,load],title='Hourly average power generated by one solar panel',xlabel='Time',ylabel='Power [W]',display_time='yearly')
    print('the total solar energy generated from one solar panel is:',irradiance_pd_S_30.get_energy_TOT(column_name='PV_generated_power'))

# Plot average 15min load consumption


# Print some general figures about the data we have
#irradiance_pd_S_30.filter_data_by_date_interval('2018-01-01 1:00','2018-12-31 23:00',interval_str='1h')

print("start calculations")
#irradiance_pd_S_30.calculate_solar_angles(latitude=50.99461, longitude=5.53972)
#irradiance_pd_S_30.calculate_direct_irradiance(tilt_angle=30,latitude=50.99461,longitude=5.53972,orientation='S')

#file=open('data/initialized_dataframes/pd_S_30','wb')
#pickle.dump(irradiance_pd_S_30,file)
#file.close()
print("angles calculated")
#print("irradiance calculated")
#formatter = pd.option_context('display.max_rows', None, 'display.max_columns', None)

#with formatter:
    # print(powercalculations_test.get_grid_power())s
    #print(powercalculations_test.get_dataset())
    #print(irradiance_pd_S_30.get_columns(['DirectIrradiance','GlobRad','DiffRad']))



#plot_dataframe(irradiance_pd_S_30.get_columns(['Load_kW']))

#plot_dataframe(irradiance_pd_S_30.get_columns(['PV_generated_power','Load_kW','NettoProduction','BatteryCharge','GridFlow']))

financials.dynamic_tariff()
financials.dual_tariff()
#plot_dataframe(financials.get_dataset())


print_figures=False
if print_figures:
    print('the total energy taken from the grid is:',financials.get_columns(['GridFlow']).sum())
    print('the total load consumed is:',irradiance_pd_S_30.get_columns(['Load_kW']).sum()/60)
    print(financials.get_grid_cost_total(calculationtype='DualTariff'))
    print(financials.get_grid_cost_total(calculationtype='DynamicTariff'))

#print('the total offpeak energy taken from the grid is:',irradiance_pd_S_30.get_energy_TOT(column_name='GridFlow',peak="offpeak"))
#print('the total peak energy taken from the grid is:',irradiance_pd_S_30.get_energy_TOT(column_name='GridFlow',peak="peak"))

#print(financials.capacity_tariff())
#print(irradiance_pd_S_30.get_monthly_peaks(column_name='GridFlow'))
#plot_dataframe(irradiance_pd_S_30.get_columns(['SolarZenithAngle','SolarAzimuthAngle']))

#irradiance_pd_S_30.filter_data_by_date_interval('2018-01-01 1:00','2018-12-31 23:00',interval_str='1h')
#plot_dataframe(irradiance_pd_S_30.get_columns(['DirectIrradiance']))

#plot_series(load_df)

print('end plots')

