def power_flow(self, cumulative_charge):
    def power_flow_row(row, cumulative_charge):
        PV_power = row['PV_generated_power']
        load = row['Load_kW']
        max_battery_charge = 1.0
        excess_power = PV_power - load
        new_charge = cumulative_charge + excess_power
        if new_charge > 0 and new_charge < max_battery_charge:
            return new_charge
    
    max_battery_charge = 1.0
    if new_charge > 0 and new_charge < max_battery_charge: 
        self.pd['battery_charge'] = new_charge
    else:
        self.pd['battery_charge'] = 0
        self.pd['grid_tap'] = -new_charge
            # Calculate the PV generated power
    self.pd['Battery_charge'] = self.pd.apply(
        lambda row: power_flow_row(row=row, cumulative_charge=cumulative_charge)
    )

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