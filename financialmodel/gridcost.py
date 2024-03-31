import os
import sys
import pandas as pd
import pickle
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import powercalculations.powercalculations as pc
import financialanalysis.financialanalysis as fa




def grid_cost(solar_count: int=1, panel_surface:int= 1 ,annual_degredation: int=0.02, panel_efficiency: int= 0.55, temperature_Coefficient: int=0.02,  tilt_angle:int=0, Orientation:str="N", battery_capacity: int= 1000, battery_count: int=1):
        

    # GENK data
    latitude=50.99461 # [degrees]
    longitude=5.53972 # [degrees]
    file = open('data/combined_dataframe','rb')
    irradiance=pickle.load(file)
    file.close()
    print("1/4: file opened")
    irradiance.filter_data_by_date_interval(start_date="2018-1-1 00:00",end_date="2018-12-31 23:00",interval_str="1h")
    print("2/4: start calculations")
    irradiance.calculate_direct_irradiance(tilt_angle=tilt_angle,latitude=latitude,longitude=longitude,orientation=Orientation)
    irradiance.PV_generated_power(panel_count=solar_count, cell_area=panel_surface, efficiency_max=panel_efficiency*(1-annual_degredation),Temp_coeff=temperature_Coefficient)
    irradiance.power_flow(max_charge=battery_capacity*battery_count)
    irradiance.nettoProduction()

    print("3/4: Powerflows calculated, start cost calculations")
    #    formatter = pd.option_context('display.max_rows', None, 'display.max_columns', None)

    #with formatter:
    # print(powercalculations_test.get_grid_power())s
    #    print(irradiance.get_columns(["BatteryCharge", "GridFlow", "NettoProduction",'PV_generated_power',"Load_kW"]))

    financials=fa.FinancialAnalysis(irradiance.get_grid_power()[0],file_path_BelpexFilter="data/BelpexFilter.xlsx")
    #print(financials.get_dataset())
    financials.dual_tariff()    #TODO: make dynamic tariff work again
    #financials.dynamic_tariff()
    cost=financials.get_grid_cost_total(calculationtype='DualTariff')
    print("financial grid calculations finished")

    return cost

grid_cost()

    