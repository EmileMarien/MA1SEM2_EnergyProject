import os
import sys
import pandas as pd

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import powercalculations.powercalculations as pc




def gridcost()
    file_path_irradiance = 'data/Irradiance_data_v2.xlsx'
    file_path_load = 'data/Load_profile_6_v2.xlsx'
    irradiance=pc.PowerCalculations(file_path_irradiance=file_path_irradiance,file_path_load=file_path_load)
    irradiance.fill_load_with_weighted_values()

return cost