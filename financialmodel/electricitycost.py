import os
import sys
import pandas as pd
import pickle
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import powercalculations.powercalculations as pc
import gridcost.gridcost as gc

def electricity_cost(solar_panel_count: int=1, panel_surface:int= 1 ,annual_degredation: float=0.02, panel_efficiency: int= 0.55, temperature_Coefficient: float=0.02,  tilt_angle:int=-1, Orientation:str="S", battery_capacity: float= 1000, battery_count: int=1, data_management_rate: float =53.86, purchase_rate: float=0.05, capacity_rate: float=0.5):
    """
    Calculates
    if provided tilt angle is -1, the optimal angle for this orientation is chosen
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
        file = open('data/combined_dataframe')
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
    else: 
        None # Direct irradiance at the location is already calculated in a few cases specified above
    print("2.1/4: Direct irradiance calculated")
    irradiance.PV_generated_power(panel_count=solar_panel_count, cell_area=panel_surface, efficiency_max=panel_efficiency*(1-annual_degredation),Temp_coeff=temperature_Coefficient)
    print("2.2/4: PV generated power calculated")
    irradiance.power_flow(max_charge=battery_capacity*battery_count)
    print("2.3/4: Powerflows calculated")
    irradiance.nettoProduction()

    print("3/4: start cost calculations")
    #formatter = pd.option_context('display.max_rows', None, 'display.max_columns', None)

    #with formatter:
        #print(powercalculations_test.get_grid_power())
    #    print(irradiance.get_columns(["BatteryCharge", "GridFlow", "NettoProduction",'PV_generated_power',"Load_kW"]))

    financials=gc.GridCost(irradiance.get_grid_power()[0],file_path_BelpexFilter="data/BelpexFilter.xlsx")

    nettarief=0

    financials.dual_tariff(peak_tariff=0.171)    
    financials.dynamic_tariff()
    # print(financials.get_grid_cost_perhour(calculationtype='DynamicTariff'))
    print(financials.get_dataset())
    energy_cost=financials.get_grid_cost_total(calculationtype='DualTariff')
    print("financial grid calculations finished")

    # Network rates
    Data_management_cost=data_management_rate
    purchase_cost=purchase_rate*financials.get_total_energy_from_grid()
    capacity_cost=financials.capacity_tariff(capacity_rate)

    # Levies
    energy_contribution = 3.06
    energy_fund_contribution = 0
    special_excise_duty=75.49

    # Total cost
    cost=energy_cost+Data_management_cost+purchase_cost+capacity_cost+energy_contribution+energy_fund_contribution+special_excise_duty
    return cost

electricity_cost(Orientation='W',tilt_angle=30)

    