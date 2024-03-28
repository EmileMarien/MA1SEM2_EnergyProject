def PV_generated_power(self,cell_area:int=1, panel_count:int=1, T_STC:int=25, Temp_coeff:int = -0.026,efficiency_max:int = 0.2):
        """
        Converts the irradiance data to power data using the specified column name
        https://www.researchgate.net/post/How_can_I_calculate_the_power_output_of_a_PV_system_in_one_day_using_a_function_of_the_temperature_of_the_cell_and_the_reference_temperature
        Args:
        df (DataFrame): The DataFrame containing the dataset
        column_name (str): The name of the column to be converted. Choose between: GlobRad, DiffRad

        Returns:
        None 
        """
        
        T_cell=self.pd['T_RV_degC']
        # Check if the 'beamirradiance' column is empty
        if 'DirectIrradiance' in self.pd.columns and not self.pd['DirectIrradiance'].empty:
            # Calculate the PV generated power in [kW]
            self.pd['PV_generated_power'] = efficiency_max*cell_area*self.pd['DirectIrradiance']*(1+Temp_coeff)*(T_cell-T_STC)*panel_count
        else:
            raise ValueError("The 'DirectIrradiance' column is empty or not present in the DataFrame")
        return None