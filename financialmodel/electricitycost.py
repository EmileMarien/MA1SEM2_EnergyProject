import os
import sys
import pandas as pd
import pickle
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import powercalculations.powercalculations as pc
import gridcost.gridcost as gc

def electricity_cost(solar_panel_count: int=1, panel_surface:int= 1.6 ,annual_degredation: float=0.02, panel_efficiency: int= 0.55, temperature_Coefficient: float=0.02, inverter_size_AC: int = 5, inverter_maxinput_DC: int = 5, tilt_angle:int=-1, Orientation:str="S", battery_capacity: float= 1000, battery_count: int=1, data_management_rate: float =53.86, capacity_rate: float=41.3087, tariff: str='DualTariff', purchase_rate_injection: float=0.0041125, purchase_rate_consumption: float=0.0538613):
    """
    Calculate the electricity cost for a given solar panel configuration and tariff.

    Args:
    solar_panel_count (int): The number of solar panels.
    panel_surface (float): The surface area of a single solar panel in m^2.
    annual_degredation (float): The annual degradation rate of the solar panels.
    panel_efficiency (float): The efficiency of the solar panels.
    temperature_Coefficient (float): The temperature coefficient of the solar panels.
    tilt_angle (int): The tilt angle of the solar panels.
    Orientation (str): The orientation of the solar panels.
    battery_capacity (float): The capacity of the battery in kWh.
    battery_count (int): The number of batteries.
    data_management_rate (float): The data management rate.
    capacity_rate (float): The capacity rate.
    tariff (str): The tariff type.
    purchase_rate_injection (float): The purchase rate for injection.
    purchase_rate_consumption (float): The purchase rate for consumption.

    Returns:
    float: The electricity cost.
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
    irradiance.filter_data_by_date_interval(start_date="2018-1-1 00:00",end_date="2018-12-31 23:00",interval_str="1h")
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
        
    else: 
        None # Direct irradiance at the location is already calculated in a few cases specified above
    print("2.1/4: Direct irradiance calculated")
    irradiance.PV_generated_power(panel_count=solar_panel_count, cell_area=panel_surface, efficiency_max=panel_efficiency*(1-annual_degredation),Temp_coeff=temperature_Coefficient)
    print("2.2/4: PV generated power calculated")
    irradiance.power_flow(max_charge=battery_capacity*battery_count,max_AC_power_output = inverter_size_AC, max_DC_batterypower = inverter_maxinput_DC)
    print("2.3/4: Powerflows calculated")
    irradiance.nettoProduction()

    print("3/4: start cost calculations")

    financials=gc.GridCost(irradiance.get_grid_power()[0],file_path_BelpexFilter="data/BelpexFilter.xlsx")

    financials.dual_tariff(peak_tariff=0.171)    
    financials.dynamic_tariff()
    energy_cost=financials.get_grid_cost_total(calculationtype=tariff)
    print("financial grid calculations finished")
    
    ## Network rates
    Data_management_cost=data_management_rate

    # Calculate the purchase cost
    purchase_cost_injection=purchase_rate_injection*irradiance.get_total_injection_and_consumption()[0]
    purchase_cost_consumption=purchase_rate_consumption*irradiance.get_total_injection_and_consumption()[1]

    purchase_cost=purchase_cost_injection+purchase_cost_consumption
    capacity_cost = max(-(irradiance.get_monthly_peaks('GridFlow').sum() / 12), 2.5) * capacity_rate
    
    ## Levies
    energy_contribution = 3.06
    energy_fund_contribution = 0
    special_excise_duty=75.49

    # Total cost
    cost=energy_cost+Data_management_cost+purchase_cost+capacity_cost+energy_contribution+energy_fund_contribution+special_excise_duty
    return [cost, energy_cost]

print(electricity_cost(Orientation='S',tilt_angle=30, tariff='DualTariff',solar_panel_count=0))
print(electricity_cost(Orientation='S',tilt_angle=30, tariff='DualTariff',solar_panel_count=10))
print(electricity_cost(Orientation='S',tilt_angle=30, tariff='DualTariff',solar_panel_count=30))

