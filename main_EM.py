


import pickle
from visualisations import plot_columns, plot_dataframe, plot_series

# Load dataset
file = open('data/initialized_dataframes/pd_EW_30','rb')
irradiance_pd_EW_30=pickle.load(file)
file.close()

file= open('data/initialized_dataframes/pd_S_30','rb')
irradiance_pd_S_30=pickle.load(file)
file.close()

file= open('data/initialized_dataframes/pd_EW_opt','rb')
irradiance_pd_EW_opt=pickle.load(file)
file.close()

file= open('data/initialized_dataframes/pd_S_opt','rb')
irradiance_pd_S_opt=pickle.load(file)
file.close()


# Plot hourly direct irradiance for the different orientations and tilt angles
plot_hourly_direct_irradiance=False
if plot_hourly_direct_irradiance:
    hourly_irradiance_pd_EW_30=irradiance_pd_EW_30.get_average_per_hour('DirectIrradiance')
    hourly_irradiance_pd_S_30=irradiance_pd_S_30.get_average_per_hour('DirectIrradiance')
    hourly_irradiance_pd_EW_opt=irradiance_pd_EW_opt.get_average_per_hour('DirectIrradiance')
    hourly_irradiance_pd_S_opt=irradiance_pd_S_opt.get_average_per_hour('DirectIrradiance')
    hourly_series=[hourly_irradiance_pd_EW_30,hourly_irradiance_pd_S_30,hourly_irradiance_pd_EW_opt,hourly_irradiance_pd_S_opt]
    plot_series(hourly_series)

# Print average net load consumption for the different orientations and tilt angles

# Plot comparison of direct, global and diffuse irradiance for S 30 scenario
plot_comparison_irradiance=False
if plot_comparison_irradiance:
    hourly_direct_irradiance_pd_S_30=irradiance_pd_S_30.get_average_per_hour('DirectIrradiance')
    hourly_global_irradiance_pd_S_30=irradiance_pd_S_30.get_average_per_hour('GlobRad')
    hourly_diffuse_irradiance_pd_S_30=irradiance_pd_S_30.get_average_per_hour('DiffRad')
    hourly_series=[hourly_direct_irradiance_pd_S_30,hourly_global_irradiance_pd_S_30,hourly_diffuse_irradiance_pd_S_30]
    plot_series(hourly_series)

# Plot hourly flows (pv-load) 
plot_hourly_flows=False
if plot_hourly_flows:
    hourly_pv_generated_power_pd_S_30=irradiance_pd_S_30.get_average_per_hour('PV_generated_power')
    hourly_load_pd_S_30=irradiance_pd_S_30.get_average_per_hour('Load_kW')
    hourly_netto_production_pd_S_30=irradiance_pd_S_30.get_average_per_hour('NettoProduction')
    hourly_battery_charge_pd_S_30=irradiance_pd_S_30.get_average_per_hour('BatteryCharge')
    hourly_grid_flow_pd_S_30=irradiance_pd_S_30.get_average_per_hour('GridFlow')
    hourly_series=[hourly_pv_generated_power_pd_S_30,hourly_load_pd_S_30,hourly_netto_production_pd_S_30,hourly_battery_charge_pd_S_30,hourly_grid_flow_pd_S_30]
    plot_series(hourly_series)