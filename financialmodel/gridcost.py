import os
import sys
import pandas as pd

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import powercalculations.powercalculations as pc
import financialanalysis.financialanalysis as fa




def grid_cost(solar_count: int=1, panel_surface:int= 1 ,annual_degredation: int=0.02, panel_efficiency: int= 0.55, temperature_Coefficient: int=0.02,  tilt_angle:int=0, Orientation:str="N", battery_capacity: int= 1000, battery_count: int=1):
    #solar_count: aantal zonnepanelen 
    #panel_surface: oppervlakte van 1 zonnepaneel [m^2]
    #annual_degredation: efficientieverlies per jaar in [%]
    #panel_efficiency: efficientie van het zonnepaneel in [%]
    #tilt_angle: angle of the solar panel, 
    #Orientation: richting naar waar de zonnepanelen staan N, E, S, W 
    #temperature_coefficient: temperatuurafhankelijkheid van P_max in [%/degrees] 
    #battery_capacity: capaciteit van de batterij 
    #battery_count: hoeveel batterijen aanwezig, enkel relevant voor stacked batteries
    file_path_irradiance = 'data/Irradiance_data_vtest.xlsx'
    file_path_load = 'data/Load_profile_6_vtest.xlsx'

    #Geographical data GENK
    latitude=50.99461 # [degrees]
    longitude=5.53972 # [degrees]

    irradiance=pc.PowerCalculations(file_path_irradiance=file_path_irradiance,file_path_load=file_path_load)
    irradiance.fill_load_with_weighted_values()
    irradiance.calculate_direct_irradiance(tilt_angle=tilt_angle,latitude=latitude,longitude=longitude)
    irradiance.PV_generated_power(N=solar_count, cell_area=panel_surface, efficiency_max=panel_efficiency,Temp_coeff=temperature_Coefficient)
    irradiance.power_flow(max_charge=battery_capacity*battery_count)
    
    financials=fa.FinancialAnalysis(irradiance.get_grid_power())
    financials.dual_tariff()
    financials.dynamic_tariff()
    cost=financials.get_grid_cost_total()

    return cost