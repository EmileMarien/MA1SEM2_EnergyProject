import pandas as pd


def power_flow(self, max_charge: int = 8, max_AC_power_output: int = 2, max_DC_batterypower: int = 2, max_PV_input: int = 10):
    """
    Calculates power flows, how much is going to and from the battery and how much is being tapped from the grid
    #TODO: add units, PV_generated_power and Load_kW are both in kW. Depending on the frequency of this data, a different amount is subtracted from the battery charge (in kWh?) (e.g. if 1h freq, the load of each line can be subtracted directly since 1kW*1h=1kWh. If in minutes, then 1kW*1min=1/60kWh) 
    ADD BATTERY DEGRADATION

    Args:
        max_charge (int, optional): Maximum charge capacity of the battery in kWh. Defaults to 8.
        max_AC_power_output (int): Maximum power that can be sent to the grid in kW. Defaults to 2.
        max_DC_batterypower_output (int, optional): Maximum power that can be sent to the battery in kW. Defaults to 2.

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
