def battery_charge(self, efficiency, area):
    """
    Converts the irradiance data to power data using the specified column name
    https://www.researchgate.net/post/How_can_I_calculate_the_power_output_of_a_PV_system_in_one_day_using_a_function_of_the_temperature_of_the_cell_and_the_reference_temperature
    Args:
    df (DataFrame): The DataFrame containing the dataset
    column_name (str): The name of the column to be converted. Choose between: GlobRad, DiffRad

    Returns:
    DataFrame: The DataFrame containing the converted power data
    """
    # Convert irradiance to power using the formula: Power = Irradiance * Area
    area = 1