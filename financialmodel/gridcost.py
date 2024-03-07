import os
import sys
import pandas as pd

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import powercalculations.powercalculations as pc
import financialanalysis.financialanalysis as fa




def grid_cost():
    file_path_irradiance = 'data/Irradiance_data_vtest.xlsx'
    file_path_load = 'data/Load_profile_6_vtest.xlsx'

    #Geographical data
    latitude=50.99461 # [degrees]
    longitude=5.53972 # [degrees]

    irradiance=pc.PowerCalculations(file_path_irradiance=file_path_irradiance,file_path_load=file_path_load)
    irradiance.fill_load_with_weighted_values()
    irradiance.calculate_direct_irradiance()
    irradiance.PV_generated_power()
    irradiance.power_flow()
    
    financials=fa.FinancialAnalysis(irradiance.get_grid_power())
    financials.dual_tariff()
    financials.dynamic_tariff()
    cost=financials.get_grid_cost_total()

    return cost