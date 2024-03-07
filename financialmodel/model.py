

from gridcost import grid_cost


#solarcount: aantal zonnepanelen 


cost_grid=grid_cost(solar_count:int=1, panel_surface:int= 1 ,annual_degredation:int=0.02, tilt_angle:int=0, Orientation:str=N, temperature_dependency: int=0.02, battery_capacity: int= 1000, battery_count: int=1)   

batterycost=500

print(cost_grid)






