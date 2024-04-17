from electricitycost import electricity_cost
from components import SolarPanel, Battery, Inverter, solar_panel_types, battery_types, inverter_types

def calculate_npv(battery_cost, total_solar_panel_cost, inverter_cost, discount_rate, constant_cash_flow):
    # Calculate the least common multiple (LCM) of battery and solar panel lifetimes

    capex = (total_solar_panel_cost + inverter_cost)*4  # multiplication for installation_cost + maintenance_cost
    investment_cost = capex + battery_cost + \
                      inverter_cost / pow(1 + discount_rate, 10) + \
                      inverter_cost / pow(1 + discount_rate, 20) - \
                      inverter_cost / pow(1 + discount_rate, 25) 

    cost_savings = sum(constant_cash_flow / pow(1 + discount_rate, t) for t in range(1, 26))
    npv = -investment_cost + cost_savings

    return npv


# Inputs
# Components Changeable  
# Solar panel Type 
class SolarPanelType:
    def __init__(self, solar_panel_cost, solar_panel_count, solar_panel_lifetime, panel_surface, annual_degredation, panel_efficiency, temperature_coefficient):
        self.solar_panel_cost = solar_panel_cost
        self.solar_panel_count = solar_panel_count
        self.solar_panel_lifetime = solar_panel_lifetime
        self.panel_surface = panel_surface
        self.annual_degredation = annual_degredation
        self.panel_efficiency = panel_efficiency
        self.temperature_coefficient = temperature_coefficient
        self.calculate_total_cost()
        self.calculate_total_surface()

    def calculate_total_cost(self):
        self.total_solar_panel_cost = self.solar_panel_cost * self.solar_panel_count

    def calculate_total_surface(self):
        self.total_panel_surface = self.panel_surface * self.solar_panel_count

# Define different types of solar panels
solar_panel_types = {        
  "Canadian": SolarPanelType(
        solar_panel_cost=110.4,            #cost of 1 solar panel
        solar_panel_count=10,            #aantal zonnepanelen
        solar_panel_lifetime=25,        
        panel_surface=1.953,              #oppervlakte van 1 zonnepaneel [m^2]
        annual_degredation=0.35,         #annual_degredation: efficientieverlies per jaar in [%]
        panel_efficiency=22.5,          #panel_efficiency: efficientie van het zonnepaneel in [%]
        temperature_coefficient=-0.26    #temperature_coefficient: temperatuurafhankelijkheid 
    ),
    "Jinko": SolarPanelType(
        solar_panel_cost=105.6,           
        solar_panel_count=10,           
        solar_panel_lifetime=25,        
        panel_surface=1.998,              
        annual_degredation=0.4,         
        panel_efficiency=22.53,            
        temperature_coefficient=-0.30  
    ),
    "Longi": SolarPanelType(
        solar_panel_cost=121.2,           
        solar_panel_count=10,           
        solar_panel_lifetime=25,        
        panel_surface=1.953,              
        annual_degredation=0.4,         
        panel_efficiency=23.0,            
        temperature_coefficient=-0.29  
    ),
    "REC": SolarPanelType(
        solar_panel_cost=181.8,           
        solar_panel_count=10,           
        solar_panel_lifetime=25,        
        panel_surface=1.934,              
        annual_degredation=0.25,         
        panel_efficiency=22.3,            
        temperature_coefficient=-0.26 
    ),
    "Sunpower": SolarPanelType(
        solar_panel_cost=294,           
        solar_panel_count=10,           
        solar_panel_lifetime=40,        
        panel_surface=1.895,              
        annual_degredation=0.25,         
        panel_efficiency=21.9,            
        temperature_coefficient=-0.27 
    ),
        "Poly": SolarPanelType(
        solar_panel_cost=104.63,           
        solar_panel_count=10,           
        solar_panel_lifetime=25,        
        panel_surface=2.174,              
        annual_degredation=0.55,         
        panel_efficiency=20.7,            
        temperature_coefficient=-0.34 
    ),
    }



# Choose solar panel type:
chosen_panel_type = "Canadian"  # Change this to switch between different types
chosen_panel = solar_panel_types[chosen_panel_type]
total_solar_panel_cost = chosen_panel.total_solar_panel_cost
solar_panel_lifetime = chosen_panel.solar_panel_lifetime
total_panel_surface = chosen_panel.total_panel_surface
annual_degredation =  chosen_panel.annual_degredation
panel_efficiency = chosen_panel.panel_efficiency
temperature_Coefficient = chosen_panel.temperature_coefficient
panel_surface = chosen_panel.panel_surface
solar_panel_count = chosen_panel.solar_panel_count

print(f"Total cost for {chosen_panel_type}: {chosen_panel.total_solar_panel_cost}")
print(f"Total surface for {chosen_panel_type}: {chosen_panel.total_panel_surface}")
# battery type 
class BatteryType:
    def __init__(self, battery_cost, battery_lifetime, battery_capacity, battery_inverter,
                 battery_Roundtrip_Efficiency, battery_PeakPower, battery_Degradation):
        self.battery_cost = battery_cost
        self.battery_lifetime = battery_lifetime
        self.battery_capacity = battery_capacity
        self.battery_inverter = battery_inverter
        self.battery_Roundtrip_Efficiency = battery_Roundtrip_Efficiency
        self.battery_PeakPower = battery_PeakPower
        self.battery_Degradation = battery_Degradation

# Define different types of batteries
battery_types = {
    "Panasonic EverVolt S": BatteryType(
        battery_inverter = 0,
        battery_cost=10000,                
        battery_lifetime=5,         
        battery_capacity=5000,
        battery_Roundtrip_Efficiency=10000,  
        battery_PeakPower=10000,  
        battery_Degradation=10000,     
    ),
    "Panasonic EverVolt M": BatteryType(
        battery_inverter = 0,
        battery_cost=10000,                
        battery_lifetime=5,         
        battery_capacity=5000,
        battery_Roundtrip_Efficiency=10000,  
        battery_PeakPower=10000,  
        battery_Degradation=10000,     
    ),
    "Panasonic EverVolt L": BatteryType(
        battery_inverter = 0,
        battery_cost=10000,                
        battery_lifetime=5,         
        battery_capacity=5000,
        battery_Roundtrip_Efficiency=10000,  
        battery_PeakPower=10000,  
        battery_Degradation=10000,     
    ),
    "LG RESU Prime S": BatteryType(
        battery_inverter = 1,
        battery_cost=10000,                
        battery_lifetime=5,         
        battery_capacity=5000,
        battery_Roundtrip_Efficiency=10000,  
        battery_PeakPower=10000,  
        battery_Degradation=10000,     
    ),
    "LG RESU Prime L": BatteryType(
        battery_inverter = 1,
        battery_cost=10000,                
        battery_lifetime=5,         
        battery_capacity=5000,
        battery_Roundtrip_Efficiency=10000,  
        battery_PeakPower=10000,  
        battery_Degradation=10000,     
    ),
    "tesla Powerwall 3": BatteryType(
        battery_inverter = 0,
        battery_cost=10000,                
        battery_lifetime=5,         
        battery_capacity=5000,
        battery_Roundtrip_Efficiency=10000,  
        battery_PeakPower=10000,  
        battery_Degradation=10000,     
    ),
    "Generac PWRcell 1": BatteryType(
        battery_inverter = 1,
        battery_cost=10000,                
        battery_lifetime=5,         
        battery_capacity=5000,
        battery_Roundtrip_Efficiency=10000,  
        battery_PeakPower=10000,  
        battery_Degradation=10000,     
    ),
    "Generac PWRcell 2": BatteryType(
        battery_inverter = 1,
        battery_cost=10000,                
        battery_lifetime=5,         
        battery_capacity=5000,
        battery_Roundtrip_Efficiency=10000,  
        battery_PeakPower=10000,  
        battery_Degradation=10000,     
    ),
    "Generac PWRcell 3": BatteryType(
        battery_inverter = 1,
        battery_cost=10000,                
        battery_lifetime=5,         
        battery_capacity=5000,
        battery_Roundtrip_Efficiency=10000,  
        battery_PeakPower=10000,  
        battery_Degradation=10000,     
    ),
    "Generac PWRcell 4": BatteryType(
        battery_inverter = 1,
        battery_cost=10000,                
        battery_lifetime=5,         
        battery_capacity=5000,
        battery_Roundtrip_Efficiency=10000,  
        battery_PeakPower=10000,  
        battery_Degradation=10000,     
    ),
    "Generac PWRcell 5": BatteryType(
        battery_inverter = 1,
        battery_cost=10000,                
        battery_lifetime=5,         
        battery_capacity=5000,
        battery_Roundtrip_Efficiency=10000,  
        battery_PeakPower=10000,  
        battery_Degradation=10000,     
    ),
    "Generac PWRcell 6": BatteryType(
        battery_inverter = 1,
        battery_cost=10000,                
        battery_lifetime=5,         
        battery_capacity=5000,
        battery_Roundtrip_Efficiency=10000,  
        battery_PeakPower=10000,  
        battery_Degradation=10000,     
    ),
    # Define more types as needed
}

# Choose battery type:
chosen_battery_type = "Panasonic EverVolt S" # Change this to switch between different types
chosen_battery = battery_types[chosen_battery_type]
print(f"Total cost for {chosen_battery_type}: {chosen_battery.battery_cost}")
battery_cost = chosen_battery.battery_cost
battery_lifetime = chosen_battery.battery_lifetime
battery_capacity = chosen_battery.battery_capacity



# bedenkingen 
# panel_efficiency degradation into account nemen -> dus geen constanr cash flows 
# energieprijzen van energiecrisis in rekening gebracht? -> zoja factor reduceren
class InverterType:
    def __init__(self, inverter_cost, inverter_size_AC, inverter_maxinput_DC, inverter_lifetime, inverter_efficiency):
        self.inverter_cost = inverter_cost
        self.inverter_size = inverter_size_AC
        self.inverter_maxinput_DC = inverter_maxinput_DC
        self.inverter_lifetime = inverter_lifetime
        self.inverter_efficiency = inverter_efficiency
# Define different types of batteries
inverter_types = {
    "Sungrow_3": InverterType(
        inverter_cost = 1219,
        inverter_size_AC = 3,
        inverter_maxinput_DC = 10,
        inverter_lifetime = 10,
        inverter_efficiency = 0.97,
    ),
    "Sungrow_3.6": InverterType(
        inverter_cost = 1380,
        inverter_size_AC = 3.68,
        inverter_maxinput_DC = 10.7,
        inverter_lifetime = 10,
        inverter_efficiency = 0.971,  
    ),
    "Sungrow_4": InverterType(
        inverter_cost = 1460,
        inverter_size_AC = 4,
        inverter_maxinput_DC = 11,
        inverter_lifetime = 10,
        inverter_efficiency = 0.972,
    ),
    "Fronius_3": InverterType(
        inverter_cost = 1579,
        inverter_size_AC = 3,
        inverter_maxinput_DC = 4.5,
        inverter_lifetime = 10,
        inverter_efficiency = 0.968,
    ),
    "Fronius_3.6": InverterType(
        inverter_cost = 1650,
        inverter_size_AC = 3.68,
        inverter_maxinput_DC = 5.52,        
        inverter_lifetime = 10,
        inverter_efficiency = 0.97,   
    ),
    "Fronius_4": InverterType(
        inverter_cost = 1702,
        inverter_size_AC = 4,
        inverter_maxinput_DC = 6,
        inverter_lifetime = 10,
        inverter_efficiency = 0.971,    
    ),
    "Fronius_4.6": InverterType(
        inverter_cost = 1826,
        inverter_size_AC = 4.6,
        inverter_maxinput_DC = 6.9,
        inverter_lifetime = 10,
        inverter_efficiency = 0.972,    
    ),
    # Define more types as needed
}
chosen_inverter_type = "Sungrow_3" # Change this to switch between different types
chosen_inverter = inverter_types[chosen_inverter_type]
inverter_cost = chosen_inverter.inverter_cost
print(f"Total cost for {chosen_inverter_type}: {chosen_inverter.inverter_cost}")


# Set-up
tilt_angle = 30 #tilt_angle: angle of the solar panel, 
Orientation = 'S'#Orientation: richting naar waar de zonnepanelen staan N, E, S, W 
	

# non-changeable 
invertor_cost= 500
installation_cost= 1000
maintenance_cost = 0

#Economics
discount_rate = 0.1                                          #Discount rate


#Calculations of the cashflows 
cost_grid = electricity_cost(solar_panel_count, panel_surface, annual_degredation, panel_efficiency, temperature_Coefficient, tilt_angle, Orientation, battery_capacity)

solar_panel_count = 0 
constant_cash_flow = electricity_cost(solar_panel_count, panel_surface, annual_degredation, panel_efficiency, temperature_Coefficient, tilt_angle, Orientation, battery_capacity) - cost_grid   #Besparing van kosten door zonnepanelen, kan men zien als de profit

# Calculate NPV
npv = calculate_npv(battery_cost, total_solar_panel_cost, inverter_cost, discount_rate, constant_cash_flow)
print("Net Present Value (NPV):", npv)




