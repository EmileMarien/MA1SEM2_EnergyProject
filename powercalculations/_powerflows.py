def power_flow(self, max_charge:int = 0, max_AC_power_output: int = 5, max_DC_batterypower_output: int = 5):
    """
    Calculates power flows, how much is going to and from the battery and how much is being tapped from the grid
    #TODO: add units, PV_generated_power and Load_kW are both in kW. Depending on the frequency of this data, a different amount is subtracted from the battery charge (in kWh?) (e.g. if 1h freq, the load of each line can be subtracted directly since 1kW*1h=1kWh. If in minutes, then 1kW*1min=1/60kWh) 
    ADD BATTERY DEGRADATION

    Args:
        max_charge (int, optional): Maximum charge capacity of the battery. Defaults to 500.
        max_AC_power_output (int): Maximum power that can be sent to the grid.
        max_DC_batterypower_output (int, optional): Maximum power that can be sent to the battery. Defaults to 500.

    Returns:
        None
    """ 
    # Initialize variables
    previous_charge = 0  # Variable to store the previous cumulative charge
    battery_charge = []  # List to store calculated battery charges
    grid_flow_list = []  # List to store calculated grid flows
    power_loss = []  # List to store calculated power loss
    # Iterate over DataFrame rows
    for _, row in self.pd.iterrows():
        PV_power = row['PV_generated_power']
        load = row['Load_kW']
        excess_power = PV_power - load
        available_space = max_charge - previous_charge
        # Calculate battery charge and grid flow
        if excess_power > 0:  # Excess power from PV
            if available_space > 0:  # Battery has room for excess power
                if excess_power <= available_space:  # Excess power fills battery partially
                    sent_to_battery = excess_power
                    new_charge = previous_charge + sent_to_battery
                    grid_flow = 0  # No grid draw
                else:  # Battery almost full, partially fill it and send excess to grid
                    sent_to_battery = available_space
                    new_charge = max_charge
                    grid_flow = excess_power - available_space # Excess power is sent to grid (positive flow)
            else:  # Battery full, send excess power to the grid
                sent_to_battery = 0
                new_charge = max_charge
                grid_flow = excess_power # All power is sent to grid (positive flow)
        elif excess_power < 0:  # Insufficient PV power, need to draw from battery or grid
            if previous_charge >= -excess_power:  # Battery has enough power to cover load deficit
                sent_to_battery = 0
                new_charge = previous_charge + excess_power
                grid_flow = 0  # No grid flow
            else:  # Battery does not have enough power, draw from battery and grid
                sent_to_battery = 0
                new_charge = 0
                grid_flow = previous_charge + excess_power # Draw from grid (negative)
        else:  # No excess power or deficit
            sent_to_battery = 0
            new_charge = previous_charge
            grid_flow = 0

        # Calculate power loss
        loss = (excess_power - sent_to_battery - grid_flow) if excess_power > 0 else (-excess_power - sent_to_battery - grid_flow)

        # Append calculated values to lists
        battery_charge.append(new_charge)
        grid_flow_list.append(grid_flow)
        power_loss.append(loss)
        previous_charge = new_charge  # Update previous charge for next iteration

    # Update DataFrame with optimized data
    self.pd['BatteryCharge'] = battery_charge
    self.pd['GridFlow'] = grid_flow_list
    self.pd['PowerLoss'] = power_loss

    return None




def nettoProduction(self):
    """
    Calculates the netto production by subtracting the load from the PV generated power
    """

    assert 'PV_generated_power' in self.pd.columns, 'The column PV_generated_power is missing'
    assert 'Load_kW' in self.pd.columns, 'The column Load_kW is missing'

    self.pd['NettoProduction'] = self.pd['PV_generated_power'] - self.pd['Load_kW']
    return None