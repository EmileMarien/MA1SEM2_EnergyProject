# Components Changeable  
# Solar panel Type 
class SolarPanel:
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
    "Type A": SolarPanelType(
        solar_panel_cost=100,            #cost of 1 solar panel
        solar_panel_count=10,            #aantal zonnepanelen
        solar_panel_lifetime=10,        
        panel_surface=1.5,              #oppervlakte van 1 zonnepaneel [m^2]
        annual_degredation=0.5,         #annual_degredation: efficientieverlies per jaar in [%]
        panel_efficiency=0.90,          #panel_efficiency: efficientie van het zonnepaneel in [%]
        temperature_coefficient=0.05    #temperature_coefficient: temperatuurafhankelijkheid 
    ),
    "Type B": SolarPanelType(
        solar_panel_cost=120,           
        solar_panel_count=12,           
        solar_panel_lifetime=12,        
        panel_surface=1.8,              
        annual_degredation=0.6,         
        panel_efficiency=0.85,            
        temperature_coefficient=0.06   
    ),
    # Define more types as needed
}

# battery type 
class BatteryType:
    def __init__(self, battery_cost, battery_count, battery_lifetime, battery_capacity):
        self.battery_cost = battery_cost
        self.battery_count = battery_count
        self.battery_lifetime = battery_lifetime
        self.battery_capacity = battery_capacity
        self.calculate_total_cost()

    def calculate_total_cost(self):
        self.total_battery_cost = self.battery_cost * self.battery_count

# Define different types of batteries
battery_types = {
    "Type X": BatteryType(
        battery_cost=10000,         
        battery_count=5,            
        battery_lifetime=5,         
        battery_capacity=5000       
    ),
    "Type Y": BatteryType(
        battery_cost=12000,         
        battery_count=3,            
        battery_lifetime=6,         
        battery_capacity=8000       
    ),
    # Define more types as needed
}