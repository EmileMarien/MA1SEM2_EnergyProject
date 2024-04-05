import os
import sys
import pandas as pd
import pickle
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import powercalculations.powercalculations as pc


#file_path_combined = 'data/combined_data_v5.xlsx'
#irradiancefilepath='data/Irradiance_data_vtest.xlsx'
#loadfilepath='data/Load_profile_6_vtest.xlsx'
#irradiance=pc.PowerCalculations(file_path_combined= file_path_combined)
#irradiance.interpolate_columns(interval='1min')
latitude=50.99461 # [degrees]
longitude=5.53972 # [degrees]
file=open('data/initialized_dataframes/pd_S_30','rb')
irradiance=pickle.load(file)
file.close()
irradiance.calculate_direct_irradiance(latitude=latitude, tilt_angle=30,longitude=longitude,temperature=10,orientation='W')
file = open('data/initialized_dataframes/pd_W_30','wb')

pickle.dump(irradiance,file)
file.close()
print('upload finished')


