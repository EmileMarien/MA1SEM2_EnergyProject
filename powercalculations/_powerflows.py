def power_flow(self, max_charge: int = 500, eff_solar_to_battery_to_home: int = 0.89, eff_solar_to_home: int = 0.97):
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
            if previous_charge > 0:  # Battery has some energy
                if -excess_power <= previous_charge:  # Battery has enough power to cover load
                    new_charge = previous_charge + excess_power
                    return [max(new_charge, 0), 0]  # No grid tap
                else:  # Battery does not have enough power, draw from battery and grid
                    grid_tap = min(-excess_power, previous_charge)
                    grid_draw = -excess_power - grid_tap
                    return [0, -grid_tap if grid_tap > 0 else 0]
            else:  # Battery is empty, draw from the grid
                return [0, excess_power]
        else:  # No excess power or deficit
            return [0, 0]

    for index, row in self.pd.iterrows():
        result = power_flow_row(row, previous_charge, max_charge)
        self.pd.at[index, 'BatteryCharge'] = result[0]
        self.pd.at[index, 'GridFlow'] = result[1]
        previous_charge = result[0]
    
    """
    Converts the irradiance data to power data using the specified column name
    https://www.researchgate.net/post/How_can_I_calculate_the_power_output_of_a_PV_system_in_one_day_using_a_function_of_the_temperature_of_the_cell_and_the_reference_temperature
    Args:
    df (DataFrame): The DataFrame containing the dataset
    column_name (str): The name of the column to be converted. Choose between: GlobRad, DiffRad

    Returns:
    DataFrame: The DataFrame containing the converted power data
    """
    return None

def nettoProduction(self):
    """
    Calculates the netto production by subtracting the load from the PV generated power
    """
    assert 'PV_generated_power' in self.pd.columns, 'The column PV_generated_power is missing'
    assert 'Load_kW' in self.pd.columns, 'The column Load_kW is missing'
    self.pd['NettoProduction'] = self.pd['PV_generated_power'] - self.pd['Load_kW']
    return None