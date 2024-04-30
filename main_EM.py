


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

# calculate the power flow
max_charge= 8 #kWh
max_AC_power_output= 5
max_DC_batterypower_output= 5
irradiance_pd_S_30.power_flow(max_charge, max_AC_power_output, max_DC_batterypower_output)
irradiance_pd_S_30.nettoProduction()

### Calculations for the other scenarios
calculate_others=True
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
    #irradiance_pd_S_30.nettoProduction()
    #irradiance_pd_EW_opt.nettoProduction()
    #irradiance_pd_S_opt.nettoProduction()

    # Calculate the PV power output
    cell_area=20
    panel_count=1
    T_STC=25
    Temp_coeff=-0.0026
    efficiency_max=0.2
    #irradiance_pd_EW_30.PV_generated_power(cell_area, panel_count, T_STC, Temp_coeff, efficiency_max)
    #irradiance_pd_S_30.PV_generated_power(cell_area, panel_count, T_STC, Temp_coeff, efficiency_max)
    #irradiance_pd_EW_opt.PV_generated_power(cell_area, panel_count, T_STC, Temp_coeff, efficiency_max)
    #irradiance_pd_S_opt.PV_generated_power(cell_area, panel_count, T_STC, Temp_coeff, efficiency_max)

    # calculate the power flow
    max_charge= 8
    max_AC_power_output= 5
    #max_DC_batterypower_output= 5
    #irradiance_pd_EW_30.power_flow(max_charge, max_AC_power_output, max_DC_batterypower_output)
    #irradiance_pd_S_30.power_flow(max_charge, max_AC_power_output, max_DC_batterypower_output)
    #irradiance_pd_EW_opt.power_flow(max_charge, max_AC_power_output, max_DC_batterypower_output)
    #irradiance_pd_S_opt.power_flow(max_charge, max_AC_power_output, max_DC_batterypower_output)



#### Plots underneath
print('start plots')
# Plot hourly direct irradiance for the different orientations and 30 degree angles
plot_hourly_direct_irradiance=True #Already calculated
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
    plot_series(hourly_series_30,title='Hourly average incident irradiance for the household under study, 30 degrees tilt angle for different orientations',xlabel="Time",ylabel='$Power [\mathrm{\\frac{kW}{m^2}}]$',display_time='hour')

# Plot hourly direct irradiance for the different orientations and optimal tilt angles
plot_hourly_direct_irradiance=True
if plot_hourly_direct_irradiance:
    irradiance_pd_EW_opt=irradiance_pd_EW_30.calculate_direct_irradiance(tilt_angle=32,orientation='EW')
    hourly_irradiance_pd_EW_opt=irradiance_pd_EW_opt.get_average_per_minute_day('DirectIrradiance') #30 degrees tilt angle
    hourly_irradiance_pd_EW_opt.name='EW optimal'
    #irradiance_pd_S_30=irradiance_pd_S_30.calculate_direct_irradiance(tilt_angle=30,orientation='S')
    hourly_irradiance_pd_S_opt=irradiance_pd_S_opt.get_average_per_minute_day('DirectIrradiance') #30 degrees tilt angle
    hourly_irradiance_pd_S_opt.name='S optimal'
    hourly_series_opt=[hourly_irradiance_pd_EW_opt,hourly_irradiance_pd_S_opt]
    plot_series(hourly_series_opt,title='Hourly average incident irradiance for the household under study, optimal tilt angle for different orientations',xlabel="Time",ylabel='$Power [\mathrm{\\frac{kW}{m^2}}]$',display_time='hour')

# Print average net load consumption for the different orientations and tilt angles

# Plot comparison of direct, global and diffuse irradiance for S 30 scenario, winter 
## Mean irradiance during summer and winter (GHI, DHI, DNI)

plot_comparison_irradiance=True
if plot_comparison_irradiance:
    irradiance_pd_S_30.filter_data_by_date_interval('2018-06-21 0:00','2018-09-20 23:00',interval_str='1min') #Summer
    #irradiance_pd_S_30.filter_data_by_date_interval('2018-12-21 0:00','2019-03-20 23:00',interval_str='1min') #Winter
    irradiance_pd_S_30.calculate_direct_irradiance(tilt_angle=30,orientation='S')
    hourly_d_irradiance_pd_S_30=irradiance_pd_S_30.get_average_per_minute_day('DNI')
    hourly_global_irradiance_pd_S_30=irradiance_pd_S_30.get_average_per_minute_day('GlobRad')
    hourly_diffuse_irradiance_pd_S_30=irradiance_pd_S_30.get_average_per_minute_day('DiffRad')
    #hourly_direct_irradiance_pd_S_30=irradiance_pd_S_30.get_average_per_minute_day('DirectIrradiance')
    hourly_series=[hourly_d_irradiance_pd_S_30,hourly_global_irradiance_pd_S_30,hourly_diffuse_irradiance_pd_S_30,]
    plot_series(hourly_series,title='Comparison of direct, global and diffuse irradiance for the household under study, during summer',xlabel='Time',ylabel='$Power [\mathrm{\\frac{kW}{m^2}}]$',display_time='hour')

# Plot minutely nettoproduction per day for the S 30 scenario
plot_minutely_nettoproduction=False
if plot_minutely_nettoproduction:
    irradiance_pd_S_30.filter_data_by_date_interval('2018-01-01 1:00','2018-12-30 23:00',interval_str='1min')
    minutely_nettoproduction_pd_S_30=irradiance_pd_S_30.get_average_per_minute_day('NettoProduction')
    hourly_battery_charge_pd_S_30 = irradiance_pd_S_30.get_average_per_minute_day('BatteryCharge')
    minutely_series=[minutely_nettoproduction_pd_S_30]
    plot_series(series=minutely_series,title='Minutely average netto production for S 30 scenario',secondary_series=[hourly_battery_charge_pd_S_30],xlabel='Time',ylabel='Power [kWh]',ylabel2='Battery charge (kWh)')


# Plot hourly flows (pv-load) 
plot_hourly_flows=False
if plot_hourly_flows:
    irradiance_pd_S_30.filter_data_by_date_interval('2018-06-01 1:00','2018-09-30 23:00',interval_str='1min')
    hourly_pv_generated_power_pd_S_30=irradiance_pd_S_30.get_average_per_hour('PV_generated_power')
    hourly_load_pd_S_30=irradiance_pd_S_30.get_average_per_hour('Load_kW')
    hourly_netto_production_pd_S_30=irradiance_pd_S_30.get_average_per_hour('NettoProduction')
    hourly_battery_charge_pd_S_30=irradiance_pd_S_30.get_average_per_hour('BatteryCharge')
    hourly_grid_flow_pd_S_30=irradiance_pd_S_30.get_average_per_hour('GridFlow')
    hourly_battery_flow_pd_S_30=irradiance_pd_S_30.get_average_per_hour('BatteryFlow')
    hourly_series=[hourly_netto_production_pd_S_30, hourly_pv_generated_power_pd_S_30, hourly_load_pd_S_30, hourly_grid_flow_pd_S_30, hourly_battery_flow_pd_S_30]
    plot_series(series=hourly_series,title='Hourly average power flows for S 30 scenario, summer',secondary_series=[hourly_battery_charge_pd_S_30],xlabel='hours',ylabel='Power [kWh]',ylabel2='Battery charge (kWh)',display_time='hour')

# Plot average hourly load consumption for winter and summer
plot_average_load_consumption=False
if plot_average_load_consumption:
    hourly_load_summer=irradiance_summer.get_average_per_hour('Load_kW').rename('Summer')
    hourly_load_winter=irradiance_winter.get_average_per_hour('Load_kW').rename('Winter')
    hourly_series=[hourly_load_summer,hourly_load_winter]
    plot_series(hourly_series)

# Plot hourly load consumption for each day of the weak on one graph
plot_weekly_load_consumption=False
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

# Return key figures
print_key_figures=False
if print_key_figures:
    print("the total power consumption is:",irradiance_pd_S_30)


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

financials=GridCost(irradiance_pd_S_30.get_grid_power()[0],file_path_BelpexFilter="data/BelpexFilter.xlsx")
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
print(irradiance_pd_S_30.get_monthly_peaks(column_name='GridFlow'))
#plot_dataframe(irradiance_pd_S_30.get_columns(['SolarZenithAngle','SolarAzimuthAngle']))

#irradiance_pd_S_30.filter_data_by_date_interval('2018-01-01 1:00','2018-12-31 23:00',interval_str='1h')
#plot_dataframe(irradiance_pd_S_30.get_columns(['DirectIrradiance']))

#plot_series(load_df)
"""
print('end plots')
tilt_angle=30
solar_zenith_angles= [i for i in range(85,90)]
solar_azimuth_angle=242
surface_azimuth_angle=180
AOI=[]
for solar_zenith_angle in solar_zenith_angles:
    AOI.append(math.degrees(math.acos(
                math.cos(math.radians(tilt_angle)) * math.cos(math.radians(solar_zenith_angle)) +
                math.sin(math.radians(tilt_angle)) * math.sin(math.radians(solar_zenith_angle)) * math.cos(math.radians(solar_azimuth_angle - surface_azimuth_angle)))))

print(AOI)
"""
