

from gridcost import grid_cost


def calculate_npv(battery_cost, solar_panel_cost, battery_lifetime, solar_panel_lifetime, discount_rate, constant_cash_flow):
    # Calculate the least common multiple (LCM) of battery and solar panel lifetimes
    def lcm(x, y):
        from math import gcd
        return x * y // gcd(x, y)

    lcm_lifetime = lcm(battery_lifetime, solar_panel_lifetime)

    # Calculate cash flows for total project

    total_cash_flows = [-capex] + [constant_cash_flow] * (lcm_lifetime - 1)

    # Calculate NPV
    npv = 0
    for i in range(lcm_lifetime):
        npv += total_cash_flows[i] / (1 + discount_rate) ** (i + 1)

    return npv

# Inputs
  
# Set-up
tilt_angle = ... #tilt_angle: angle of the solar panel, 
Orientation = ...#Orientation: richting naar waar de zonnepanelen staan N, E, S, W 

# Components Changeable  
# Solar panel Type 
solar_panel_cost =                                           #cost of 1 solar panel
solar_count = ...                                            #solar_count: aantal zonnepanelen
total_solar_panel_cost = solar_panel_cost*solar_count
solar_panel_lifetime = 10 
panel_surface = ...                                          #panel_surface: oppervlakte van 1 zonnepaneel [m^2]
annual_degredation = ...                                     #annual_degredation: efficientieverlies per jaar in [%]
panel_efficiency = ...                                       #panel_efficiency: efficientie van het zonnepaneel in [%]
temperature_coefficient = ...                                #temperature_coefficient: temperatuurafhankelijkheid van P_max in [%/degrees] 
# Battery Type 
battery_cost = 10000                                         #cost of 1 battery
battery_count = ...                                          #battery_count: hoeveel batterijen aanwezig, enkel relevant voor stacked batteries 
total_battery_cost = battery_cost*battery_count      
battery_lifetime = 5
battery_capacity =  ...                                      #battery_capacity: capaciteit van de batterij 

# non-changeable 
convertor_cost= 500
installation_cost= 1000
maintenance_cost = 0

#Economics
discount_rate = 0.1                                          #Discount rate
capex = total_solar_panel_cost + total_battery_cost + installation_cost + convertor_cost + maintenance_cost

#Calculations 

cost_grid=grid_cost(solar_count: int=1, panel_surface:int= 1 ,annual_degredation: int=0.02, panel_efficiency: int= 0.55, temperature_Coefficient: int=0.02,  tilt_angle:int=0, Orientation:str=N, battery_capacity: int= 1000, battery_count: int=1)   
constant_cash_flow = grid_cost(solar_count=0, battery_count=0) - cost_grid    #Besparing van kosten door zonnepanelen, kan men zien als de profit

# Calculate NPV
npv = calculate_npv(battery_cost, solar_panel_cost, battery_lifetime, solar_panel_lifetime, discount_rate, constant_cash_flow)
print("Net Present Value (NPV):", npv)







