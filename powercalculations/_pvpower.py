def PV_generated_power(self,cell_area:int=1, panel_count:int=1, T_STC:int=25, V_OC_STC:int=0.6, delta_V_OC:int=-2.5, I_sc_a:int=300, FF:int=0.8, T_cell:int=30, irradiance_STC:int=100, irradiance_a:int=120):
        """
        Converts the irradiance data to power data using the specified column name
        https://www.researchgate.net/post/How_can_I_calculate_the_power_output_of_a_PV_system_in_one_day_using_a_function_of_the_temperature_of_the_cell_and_the_reference_temperature
        Args:
        df (DataFrame): The DataFrame containing the dataset
        column_name (str): The name of the column to be converted. Choose between: GlobRad, DiffRad

        Returns:
        DataFrame: The DataFrame containing the converted power data
        """
        

        # Check if the 'beamirradiance' column is empty
        if 'DirectIrradiance' in self.pd.columns and not self.pd['DirectIrradiance'].empty:
            # Calculate the PV generated power
            self.pd['PV_generated_power'] = FF*cell_area*I_sc_a*self.pd['DirectIrradiance']/irradiance_STC*(V_OC_STC+delta_V_OC*(T_cell-T_STC))*panel_count
        else:
            raise ValueError("The 'directIrradiance' column is empty or not present in the DataFrame")
        return None