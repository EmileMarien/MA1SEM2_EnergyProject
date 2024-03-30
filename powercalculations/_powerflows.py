def power_flow(self, max_charge: int = 500):
    #TODO: add units, PV_generated_power and Load_kW are both in kW. Depending on the frequency of this data, a different amount is subtracted from the battery charge (in kWh?) (e.g. if 1h freq, the load of each line can be subtracted directly since 1kW*1h=1kWh. If in minutes, then 1kW*1min=1/60kWh) 
    #TODO: add documentation on top (look at other functions for inspiration)

    previous_charge = 0  # Variable to store the previous cumulative charge
    
    def power_flow_row(row, previous_charge, max_charge):
        PV_power = row['PV_generated_power']
        load = row['Load_kW']
        excess_power = PV_power - load

        if excess_power > 0:  # Excess power from PV
            available_space = max_charge - previous_charge
            if available_space > 0:  # Battery has room for excess power
                if excess_power <= available_space:  # Excess power fills battery partially
                    new_charge = previous_charge + excess_power
                    return [new_charge, 0]  # No grid draw
                else:  # Battery almost full, partially fill it and send excess to grid
                    new_charge = max_charge
                    grid_draw = excess_power - available_space
                    return [new_charge, grid_draw]
            else:  # Battery full, send excess power to the grid
                new_charge = max_charge
                return [max_charge, excess_power]
        elif excess_power < 0:  # Insufficient PV power, need to draw from battery or grid
            # Updated logic: Utilize battery charge to cover the deficit before drawing from the grid
            if previous_charge >= -excess_power:  # Battery has enough power to cover load deficit
                new_charge = previous_charge + excess_power
                return [max(new_charge, 0), 0]  # No grid tap
            else:  # Battery does not have enough power, draw from battery and grid
                grid_draw = -excess_power - previous_charge
                return [0, -grid_draw]
        else:  # No excess power or deficit
            return [0, 0]

    for index, row in self.pd.iterrows():
        result = power_flow_row(row, previous_charge, max_charge)
        self.pd.at[index, 'BatteryCharge'] = result[0]
        self.pd.at[index, 'GridFlow'] = result[1]
        previous_charge = result[0]
    

    return None


def nettoProduction(self):
    """
    Calculates the netto production by subtracting the load from the PV generated power
    """

    assert 'PV_generated_power' in self.pd.columns, 'The column PV_generated_power is missing'
    assert 'Load_kW' in self.pd.columns, 'The column Load_kW is missing'

    self.pd['NettoProduction'] = self.pd['PV_generated_power'] - self.pd['Load_kW']
    return None