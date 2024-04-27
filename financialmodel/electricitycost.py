import os
import sys
import pandas as pd
import pickle

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from visualisations.visualisations import plot_dataframe

import powercalculations.powercalculations as pc
import gridcost.gridcost as gc

def electricity_cost(solar_panel_count: int=10, panel_surface:int= 1.998 ,annual_degradation: float=0.004, panel_efficiency: int= 0.2253, temperature_coefficient: float=-0.0030 , inverter_size_AC: int = 3, inverter_maxsolar_DC: int = 10, inverter_maxbattery_DC: int=6.6,tilt_angle:int=-1, Orientation:str="S", battery_capacity: float= 0, battery_count: int=1,tariff: str='DualTariff', ):
    """
    Calculate the electricity cost for a given solar panel configuration and tariff.

    Args:
    solar_panel_count (int): The number of solar panels.
    panel_surface (float): The surface area of a single solar panel in m^2.
    annual_degradation (float): The annual degradation rate of the solar panels (%, geef kommagetal).
    panel_efficiency (float): The efficiency of the solar panels (%, geef kommagetal).
    temperature_Coefficient (float): The temperature coefficient of the solar panels (%/°C).
    tilt_angle (int): The tilt angle of the solar panels (°).
    Orientation (str): The orientation of the solar panels.
    battery_capacity (float): The capacity of the battery in kWh.
    battery_count (int): The number of batteries.
    data_management_cost (float): The data management rate (€/year).
    capacity_rate (float): The capacity rate (€/kW peak).
    tariff (str): The tariff type, choose from 'DualTariff' or 'DynamicTariff'.
    purchase_rate_injection (float): The purchase rate for injection (€/kWh).
    purchase_rate_consumption (float): The purchase rate for consumption (€/kWh).

    Returns:
    float: The electricity cost (€).
    """     

    # Opens the file including the direct irradiance on the roof for the optimal tilt angle depending on the orientation provided
    notYetCalculated=False

    if (Orientation =='S') & (tilt_angle==-1):
        file = open('data/initialized_dataframes/pd_S_opt_41','rb')
    elif (Orientation =='EW') & (tilt_angle==-1):
        file = open('data/initialized_dataframes/pd_W_opt_32','rb')
    elif (Orientation =='EW') & (tilt_angle==30):
        file = open('data/initialized_dataframes/pd_EW_30','rb')
    elif (Orientation =='S') & (tilt_angle==30):
        file = open('data/initialized_dataframes/pd_S_30','rb')
    else:
        print("situation not yet calculated, starting calculations from scratch ( this may take a while :( )")
        file = open('data/initialized_dataframes/pd_S_30','rb')
        notYetCalculated=True

    irradiance=pickle.load(file)
    file.close()
    print("1/4: file opened")
    irradiance.filter_data_by_date_interval(start_date="2018-1-1 00:00",end_date="2018-12-31 23:00",interval_str="1min")
    print("2/4: start calculations")

    if notYetCalculated:
        # GENK data
        latitude=50.99461 # [degrees]
        longitude=5.53972 # [degrees]
        irradiance.calculate_direct_irradiance(tilt_angle=tilt_angle,latitude=latitude,longitude=longitude,orientation=Orientation)

        #Store the calculated data
        file = open('data/initialized_dataframes/pd_'+Orientation+'_'+str(tilt_angle),'wb')
        pickle.dump(irradiance,file)
        file.close()
        
    print("2.1/4: Direct irradiance calculated")
    irradiance.PV_generated_power(panel_count=solar_panel_count, cell_area=panel_surface, efficiency_max=panel_efficiency*(1-annual_degradation),Temp_coeff=temperature_coefficient)
    print("2.2/4: PV generated power calculated")
    irradiance.power_flow(max_charge=battery_capacity*battery_count, max_AC_power_output = inverter_size_AC, max_PV_input = inverter_maxsolar_DC, max_DC_batterypower = inverter_maxbattery_DC)
    print("2.3/4: Powerflows calculated")

    print("3/4: start cost calculations")
    #plot_dataframe(irradiance.get_columns(["Load_kW", "PV_generated_power", "GridFlow", "BatteryFlow", "BatteryCharge", "PowerLoss"]))
    
    financials=gc.GridCost(irradiance.get_grid_power()[0],file_path_BelpexFilter="data/BelpexFilter.xlsx")

    financials.dual_tariff()
    financials.dynamic_tariff()
    print("financial grid calculations finished")
    
    #Financial components
    purchase_rate_injection=0.00414453
    purchase_rate_consumption=0.0538613
    energy_contribution_levy=8.72
    energy_fund_contribution_levy=0
    special_excise_duty_levy=215.16
    data_management_cost: float =53.86
    capacity_rate: float=41.3087
     
    ## Electricity cost
    fixed_component_dual=42.4 # [€/year]
    fixed_component_dynamic=100.7 # [€/year]
    energy_cost=financials.get_grid_cost_total(calculationtype=tariff)+fixed_component_dual if tariff=='DualTariff' else financials.get_grid_cost_total(calculationtype=tariff)+fixed_component_dynamic
    print(financials.get_grid_cost_total(calculationtype=tariff))
    ## Network rates
    #data_management_cost

    # Calculate the purchase cost
    purchase_cost_injection=purchase_rate_injection*irradiance.get_total_injection_and_consumption()[0]
    purchase_cost_consumption=purchase_rate_consumption*irradiance.get_total_injection_and_consumption()[1]

    purchase_cost=purchase_cost_injection+purchase_cost_consumption
    capacity_cost = max(-(irradiance.get_monthly_peaks('GridFlow').sum() / 12), 2.5) * capacity_rate
    ## Levies
    levy_cost=energy_contribution_levy+energy_fund_contribution_levy+special_excise_duty_levy

    # Total cost
    cost=energy_cost+data_management_cost+purchase_cost+capacity_cost+levy_cost
    print("Components of the cost:")
    print("Energy cost:", energy_cost)
    print("Data management cost:", data_management_cost)
    print("Purchase cost (injection):", purchase_cost_injection)
    print("Purchase cost (consumption):", purchase_cost_consumption)
    print("Capacity cost:", capacity_cost)
    print("Levy cost:", levy_cost)
    print("Total cost:", cost)
    print("Total injection:", irradiance.get_total_injection_and_consumption()[0])
    print("Total consumption:", irradiance.get_total_injection_and_consumption()[1])
    return cost

print(electricity_cost(Orientation='S',tilt_angle=30, tariff='DynamicTariff',solar_panel_count=0))
#print(electricity_cost(Orientation='S',tilt_angle=30, tariff='DynamicTariff',solar_panel_count=0))
#print(electricity_cost(Orientation='S',tilt_angle=30, tariff='DualTariff',solar_panel_count=10))
#print(electricity_cost(Orientation='S',tilt_angle=30, tariff='DualTariff',solar_panel_count=30))



