import os
import sys
import pandas as pd
import pickle
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import powercalculations.powercalculations as pc

### Initialisation
# Load dataset
file=open('data/combined_dataframe','rb')
data=pickle.load(file)
file.close()


# Set coordinates of PV installation (GENk)
latitude=50.99461 # [degrees]
longitude=5.53972 # [degrees]

### test most optimal panel tilt angle for each azimuth angle case
"""
- Only using directIrradiance function. 
- the tilt angle at which the total direct irradiance over 1 full year, for a specific azimuth angle, is the highest, is the optimal tilt angle
"""
findAngle=True
if findAngle:
    
    orientations=["N","O","W","S"]
    tiltAngles=[i for i in range(0,90,10)]

    temperature = 10
    for orientation in orientations:
        optimalAngle=(-1,0) #(angle, total directIrradiance at that angle)

        for tiltAngle in tiltAngles:
            data.calculate_direct_irradiance(latitude=latitude, tilt_angle=tiltAngle,longitude=longitude,temperature=temperature,orientation=orientation)
            totalIrradiance=data.get_direct_irradiance().sum()
            print(tiltAngle)
            if totalIrradiance>optimalAngle[1]:
                optimalAngle=(tiltAngle,totalIrradiance)
            else:
                continue
        
        print("The optimal angle for the "+str(orientation)+ " Orientation is: "+ str(optimalAngle)+" degrees")


"""
To put in report:
- the irradiance output of the solar panels for the different orientations with optimal angle throughout the year
- waterfall chart 


"""