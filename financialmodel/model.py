

from gridcost import grid_cost


#solar_count: aantal zonnepanelen 
#panel_surface: oppervlakte van 1 zonnepaneel [m^2]
#annual_degredation: efficientieverlies per jaar in [%]
#panel_efficiency: efficientie van het zonnepaneel in [%]
#tilt_angle: angle of the solar panel, 
#Orientation: richting naar waar de zonnepanelen staan N, E, S, W 
#temperature_coefficient: temperatuurafhankelijkheid van P_max in [%/degrees] 
#battery_capacity: capaciteit van de batterij 
#battery_count: hoeveel batterijen aanwezig, enkel relevant voor stacked batteries

cost_grid=grid_cost(solar_count: int=1, panel_surface:int= 1 ,annual_degredation: int=0.02, panel_efficiency: int= 0.55, temperature_Coefficient: int=0.02,  tilt_angle:int=0, Orientation:str=N, battery_capacity: int= 1000, battery_count: int=1)   

Profit = grid_cost(solar_count=0, battery_count=0) - cost_grid    #Besparing van kosten door zonnepanelen, kan men zien als de profit


#changeable 
Solarpanel_costs=500 
battery_cost = 500    


# non-changeable 
Convertor_cost=500
Installation_cost= 1000

Capex = Solarpanel_costs + battery_cost + Installation_cost + 


# 
profit
for i
NPV = Profit/(1 + i)t


print(cost_grid)







