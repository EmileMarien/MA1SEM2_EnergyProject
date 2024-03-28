import os
import sys
import pandas as pd
import pickle
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import powercalculations.powercalculations as pc


#file_path_combined = 'data/combined_data_v4.xlsx'
irradiancefilepath='data/Irradiance_data_vtest.xlsx'
loadfilepath='data/Load_profile_6_vtest.xlsx'
irradiance=pc.PowerCalculations(file_path_irradiance=irradiancefilepath,file_path_load=loadfilepath)
irradiance.interpolate_columns(interval='1min')
file = open('data/combined_dataframe_test','wb')
pickle.dump(irradiance,file)
file.close()
print('upload finished')

