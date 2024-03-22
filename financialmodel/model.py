from gridcost import grid_cost
from components import SolarPanelType, BatteryType

def calculate_npv(capex, battery_lifetime, battery_cost, solar_panel_lifetime,total_solar_panel_cost, discount_rate, constant_cash_flow):
    # Calculate the least common multiple (LCM) of battery and solar panel lifetimes
    def lcm(x, y):
        from math import gcd
        return x * y // gcd(x, y)

    lcm_lifetime = lcm(battery_lifetime, solar_panel_lifetime)

    # Calculate cash flows for total project

    total_cash_flows = [-capex]

    for i in range(1, lcm_lifetime + 1):
        # Check if it's time for reinvestment
        if i % battery_lifetime == 0:
            total_cash_flows.append(constant_cash_flow - battery_cost)
        elif i % solar_panel_lifetime == 0:
            total_cash_flows.append(constant_cash_flow - total_solar_panel_cost)
        else:
            total_cash_flows.append(constant_cash_flow)

    # Calculate NPV
    npv = 0
    for i, cash_flow in enumerate(total_cash_flows):
        npv += cash_flow / (1 + discount_rate) ** (i)

    return npv
3
# Inputs
  
# Set-up
tilt_angle = ... #tilt_angle: angle of the solar panel, 
Orientation = ...#Orientation: richting naar waar de zonnepanelen staan N, E, S, W 






# Choose solar panel type:
chosen_panel_type = "Type A"  # Change this to switch between different types
chosen_panel = solar_panel_types[chosen_panel_type]
print(f"Total cost for {chosen_panel_type}: {chosen_panel.total_solar_panel_cost}")
print(f"Total surface for {chosen_panel_type}: {chosen_panel.total_panel_surface}")



# Choose battery type:
chosen_battery_type = "Type X"  # Change this to switch between different types
chosen_battery = battery_types[chosen_battery_type]
print(f"Total cost for {chosen_battery_type}: {chosen_battery.total_battery_cost}")

# non-changeable 
inverter_cost= 500
installation_cost= 1000
maintenance_cost = 0

#Economics
discount_rate = 0.1                                          #Discount rate
capex = total_solar_panel_cost + total_battery_cost + installation_cost + invertor_cost + maintenance_cost

#Calculations of the cashflows 
cost_grid = grid_cost(total_panel_surface= 1 ,annual_degredatio=0.02, panel_efficiency= 0.55, temperature_Coefficient=0.02,  tilt_angle=0, Orientation=N, battery_capacity= 1000, battery_count=1) 
constant_cash_flow = grid_cost(solar_count=0, battery_count=0) - cost_grid    #Besparing van kosten door zonnepanelen, kan men zien als de profit


# Calculate NPV
npv = calculate_npv(battery_cost, solar_panel_cost, battery_lifetime, solar_panel_lifetime, discount_rate, constant_cash_flow)
print("Net Present Value (NPV):", npv)


# bedenkingen 
# panel_efficiency degradation into account nemen -> dus geen constanr cash flows 
# energieprijzen van energiecrisis in rekening gebracht? -> zoja factor reduceren