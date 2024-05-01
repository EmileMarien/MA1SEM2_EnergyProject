import pandas as pd


def power_flow(self, max_charge: int = 8, max_AC_power_output: int = 2, max_DC_batterypower: int = 2, max_PV_input: int = 10, max_EV_power: int = 3.7, max_EV_charge=82.3):
    """
    Calculates power flows, how much is going to and from the battery and how much is being tapped from the grid
    #TODO: add units, PV_generated_power and Load_kW are both in kW. Depending on the frequency of this data, a different amount is subtracted from the battery charge (in kWh?) (e.g. if 1h freq, the load of each line can be subtracted directly since 1kW*1h=1kWh. If in minutes, then 1kW*1min=1/60kWh) 
    ADD BATTERY DEGRADATION

    Args:
        max_charge (int, optional): Maximum charge capacity of the battery in kWh. Defaults to 8.
        max_AC_power_output (int): Maximum power that can be sent to the grid in kW. Defaults to 2.
        max_DC_batterypower_output (int, optional): Maximum power that can be sent to the battery in kW. Defaults to 2.
        max_PV_input (int, optional): Maximum power that can be sent to the battery in kW. Defaults to 10.
        max_EV_power (int, optional): Maximum power that can be sent to the EV in kW. Defaults to 3.7.
        max_EV_charge (int, optional): Maximum charge capacity of the EV in kWh. Defaults to 82.3.
    Returns:
        None
    """ 
    # Initialize variables
    previous_charge = 0  # Initialize as integer
    battery_charge = []  # List to store calculated battery charges
    grid_flow_list = []  # List to store calculated grid flows
    power_loss_list = [] # List to store calculated power loss
    battery_flow_list = [] # List to store flow to and from the battery
    max_charge=max_charge*60 #kWmin
    # Iterate over DataFrame rows
    for _, row in self.pd.iterrows():
        PV_power = min(row['PV_generated_power'], max_PV_input) 
        power_loss = row['PV_generated_power'] - PV_power
        load = row['Load_kW']
        excess_power = PV_power - load
        available_space = max_charge - previous_charge #kWh
        # Calculate battery charge and grid flow
        if load > max_AC_power_output:  # Load too high for inverter, switch to grid-tie to avoid overloading of inverter
            battery_flow = min(available_space, PV_power, max_DC_batterypower) # kW, PV power is sent straight to battery, depending on how much space there is
            power_loss += min(available_space, PV_power) - battery_flow # kWh, Battery charging power is limited, causing power loss
            grid_flow = -load + (PV_power-battery_flow) # kW, All power that is not sent to the battery, is sent to the grid
            new_charge = previous_charge + battery_flow
        elif excess_power > 0:  # Excess power from PV
            if available_space > 0:  # Battery has room for excess power
                if excess_power <= available_space:  # Excess power fills battery partially
                    battery_flow = min(excess_power, max_DC_batterypower) # Powerflow to battery has limit, excess is power loss
                    power_loss += excess_power - battery_flow
                    new_charge = previous_charge + battery_flow
                    grid_flow = 0  # No grid draw
                else:  # Battery almost full, partially fill it and send excess to grid
                    battery_flow = min(available_space, max_DC_batterypower) # Battery is filled, or is limited by power flow
                    new_charge = previous_charge + battery_flow # Update battery charge
                    grid_flow = min(excess_power - battery_flow, max_AC_power_output) # Excess power is sent to grid (positive flow), limited by power flow
                    power_loss += (available_space - battery_flow) + ((excess_power-battery_flow)-grid_flow) #Power loss due to limited battery flow, and due to limited grid flow
            else:  # Battery full, send excess power to the grid
                battery_flow = 0
                new_charge = max_charge
                grid_flow = min(excess_power, max_AC_power_output) # All power is sent to grid (positive flow), output has limit
                power_loss += excess_power - grid_flow
        elif excess_power < 0:  # Insufficient PV power, need to draw from battery or grid
            if previous_charge >= -excess_power:  # Battery has enough power to cover load deficit
                battery_flow = -min(-excess_power, max_DC_batterypower)  # Adjusted here to prevent overcharging the battery
                new_charge = previous_charge + battery_flow
                grid_flow = 0  # No grid flow
                power_loss += (-excess_power) - (-battery_flow) # Power loss due to limited battery flow
            else:  # Battery does not have enough power, draw from battery and grid
                battery_flow = -min(previous_charge, max_DC_batterypower)
                new_charge = 0
                grid_flow = previous_charge - (-excess_power) # Draw from grid (negative)
                power_loss += previous_charge - (-battery_flow) # Power loss due to limited battery flow
        else:  # No excess power or deficit
            battery_flow = 0
            new_charge = previous_charge
            grid_flow = 0
            power_loss = 0

        # Append calculated values to lists
        battery_charge.append(new_charge/60) #kWmin -> kWh
        grid_flow_list.append(grid_flow)
        power_loss_list.append(power_loss)
        battery_flow_list.append(battery_flow)
        previous_charge = new_charge  # Update previous charge for next iteration

    # Update DataFrame with optimized data
    self.pd['BatteryCharge'] = battery_charge
    self.pd['GridFlow'] = grid_flow_list # Negative values indicate power drawn from the grid, positive values indicate power sent to the grid
    self.pd['PowerLoss'] = power_loss_list
    self.pd['BatteryFlow'] = battery_flow_list

    return None


def power_flow_v2(self, max_charge: int = 8, max_AC_power_output: int = 2, max_DC_batterypower: int = 2, max_PV_input: int = 10, max_EV_power: int = 3.7, max_EV_charge=82.3):
    """
    Calculates power flows, how much is going to and from the battery and how much is being tapped from the grid
    #TODO: add units, PV_generated_power and Load_kW are both in kW. Depending on the frequency of this data, a different amount is subtracted from the battery charge (in kWh?) (e.g. if 1h freq, the load of each line can be subtracted directly since 1kW*1h=1kWh. If in minutes, then 1kW*1min=1/60kWh) 
    ADD BATTERY DEGRADATION

    Args:
        max_charge (int, optional): Maximum charge capacity of the battery in kWh. Defaults to 8.
        max_AC_power_output (int): Maximum power that can be sent to the grid in kW. Defaults to 2.
        max_DC_batterypower_output (int, optional): Maximum power that can be sent to the battery in kW. Defaults to 2.
        max_PV_input (int, optional): Maximum power that can be sent to the battery in kW. Defaults to 10.
        max_EV_power (int, optional): Maximum power that can be sent to the EV in kW. Defaults to 3.7.
        max_EV_charge (int, optional): Maximum charge capacity of the EV in kWh. Defaults to 82.3.
    Returns:
        None
    """ 
    # Initialize variables
    previous_charge_battery = 0  # Initialize as integer
    previous_charge_EV = 0  # Initialize as integer


    # Iterate over DataFrame rows
    for _, row in self.pd.iterrows():
        PV_power = min(row['PV_generated_power'], max_PV_input) #power_loss = row['PV_generated_power'] - PV_power
        load = -row['Load_kW']

        # Calculate battery charge and grid flow
        if load > max_AC_power_output:  # Load too high for inverter, switch to grid-tie to avoid overloading of inverter
            load_to_EV = PV_power
            load_to_battery, new_charge_EV= EV_B2G(load_to_EV, previous_charge_EV)
            load_from_battery, new_charge_battery = battery(load_to_battery, previous_charge_battery)
            grid_flow = load + load_from_battery

        else:
            load_to_EV =PV_power+load
            load_to_battery, new_charge_EV= EV_B2G(load_to_EV, previous_charge_EV)
            load_from_battery, new_charge_battery = battery(load_to_battery, previous_charge_battery)
            grid_flow = load_from_battery
        
        grid_flow = min(grid_flow, max_AC_power_output) # Limit grid flow to max AC power output
        previous_charge_battery=new_charge_battery
        previous_charge_EV=new_charge_EV

        row['BatteryCharge'] = new_charge_battery/60
        row['GridFlow'] = grid_flow
        #row['PowerLoss'] = power_loss
        row['BatteryFlow'] = load_to_battery-load_from_battery
        row['EVCharge'] = new_charge_EV
        row['EVFlow'] = load_to_EV-load_to_battery
    return None

def battery(self,load_to_battery:float,old_capacity:float)-> tuple[float,float]:
    """
    Calculate load after the battery and the new battery capacity using the old capacity and load
    """
    #power_loss=0
    min_capacity=40
    max_capacity=60
    max_DC_batterypower=2
    if load_to_battery > 0:  # Excess power from PV
        max_input=min(max_capacity-old_capacity,load_to_battery,max_DC_batterypower) #TODO: add function that it can be better to charge at a later time and move more to the grid now
        load_from_battery=load_to_battery-max_input
        new_capacity=old_capacity+max_input
        #power_loss += min(max_capacity-old_capacity, load) - max_input

    elif load_to_battery < 0:  # Insufficient PV power, need to draw from battery
        max_output=min(max_DC_batterypower,old_capacity-min_capacity,-load_to_battery)
        load_from_battery=load_to_battery-max_output
        new_capacity=old_capacity-max_output
        #power_loss += old_capacity - min(min_capacity, old_capacity) - max_output

    else:  # No excess power or deficit
        load_from_battery=load_to_battery
        new_capacity=old_capacity

    return load_from_battery,new_capacity

def EV_B2G(self,load_to_EV:float,old_capacity:float)-> tuple[float,float]:
    """
    Calculate the EV load for a bidirectional charging strategy. Based on the time of the week, it returns the total load consumed (by the EV and household) and the new battery charge of the EV. It gets as parameter the charge that is requested to be added or removed from the battery by the household and the old battery capacity of the EV.
    """
    max_input_power=3.7
    max_output_power=3.7
    min_capacity_morning=40
    min_capacity_evening=20
    max_capacity=60
    # During the weekdays
    if self.pd.index.weekday<5:
        # During the weekdays, from 9:00 to 17:00, the load of the EV is zero so it returns the same load as the household, but the EV battery decreases by 0.2 kWh per hour
        if self.pd.index.hour>=9 and self.pd.index.hour<17:
            load_from_EV=load_to_EV
            new_capacity=old_capacity-0.2
        # During the weekdays in the morning, from 7:00 to 9:00, and evening, from 17:00 to 19:00, the EV is uncharging, reducing the household load and the battery capacity as long as the battery capacity is greater than 40 kWh in the morning and 20kWh at 19:00
        elif (self.pd.index.hour>=7 and self.pd.index.hour<9) or (self.pd.index.hour>=17 and self.pd.index.hour<19):
            min_capacity= min_capacity_morning if self.pd.index.hour<9 else min_capacity_evening # minimal capacity of the battery
            max_output=min(max_output_power,old_capacity-min_capacity,load_to_EV)
            load_from_EV=load_to_EV-max_output
            new_capacity=old_capacity-max_output 
        
        # During the weekdays in the rest of the hours, the EV is charging, increasing the household load and the battery capacity as long as the battery capacity is less than 60 kWh
        else:
            max_input=min(max_input_power,max_capacity-old_capacity,load_to_EV)
            load_from_EV=load_to_EV+max_input
            new_capacity=min(max_capacity,old_capacity+max_input_power)
        
    # During the weekends
    if self.pd.index.weekday>=5:
        # During the weekends, from 9:00 to 17:00, 
        if self.pd.index.hour>=9 and self.pd.index.hour<17:
            load_from_EV=load_to_EV
            new_capacity=old_capacity-0.2
        # During the weekends in the morning, from 7:00 to 9:00, and evening, from 17:00 to 19:00, the EV is uncharging, reducing the household load and the battery capacity as long as the battery capacity is greater than 40 kWh in the morning and 20kWh at 19:00
        elif (self.pd.index.hour>=7 and self.pd.index.hour<9) or (self.pd.index.hour>=17 and self.pd.index.hour<19):
            min_capacity= min_capacity_morning if self.pd.index.hour<9 else min_capacity_evening
    
    #TODO: finish this part, check if to be charged the whole night

    return load_from_EV,new_capacity    

def nettoProduction(self):
    """
    Calculates the netto production by subtracting the load from the PV generated power
    """

    assert 'PV_generated_power' in self.pd.columns, 'The column PV_generated_power is missing'
    assert 'Load_kW' in self.pd.columns, 'The column Load_kW is missing'

    self.pd['NettoProduction'] = self.pd['PV_generated_power'] - self.pd['Load_kW']
    return None

def optimized_charging(time:pd.DatetimeIndex, max_charge: int = 8, max_AC_power_output: int = 2, max_DC_batterypower: int = 2, max_PV_input: int = 10):
    """
    Calculates power flows, how much is going to and from the battery and how much is being tapped from the grid
    """
    return None

"""
import numpy as np
from scipy.optimize import minimize

def objective_function(X, B):
    return -np.dot(X, B)  # Maximizing X * B is equivalent to minimizing -X * B

def constraint(X, total_sum):
    return np.sum(X) - total_sum  # Constraint on the total sum of X

# Initial guess for vector X
initial_guess_X = np.zeros_like(B)

# Total sum constraint for vector X
total_sum_constraint = 10  # Change this value to your desired total sum

# Bounds for each element of vector X
bounds = [(0, None) for _ in range(len(B))]  # Each element of X should be non-negative

# Define the optimization problem
problem = {
    'fun': objective_function,
    'x0': initial_guess_X,
    'args': (B,),
    'constraints': {'type': 'eq', 'fun': constraint, 'args': (total_sum_constraint,)},
    'bounds': bounds
}

# Solve the optimization problem
result = minimize(**problem)

# Extract the optimized vector X
optimized_X = result.x

print("Optimized vector X:", optimized_X)
print("Maximum value of X * B:", -result.fun)  # Since we were minimizing -X * B


"""
