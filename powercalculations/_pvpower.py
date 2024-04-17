<<<<<<< HEAD
def PV_generated_power(self,cell_area:int=1, panel_count_series:int=1,panel_count_parallel:int=1, T_STC:int=25, T_cell:int=30, irradiance_a:int=120, efficiency_max = 0.2, Temp_coeff = -0.026 ):
=======
def PV_generated_power(self,cell_area:int=20, panel_count:int=1, T_STC:int=25, Temp_coeff:int = -0.0026,efficiency_max:int = 0.2):
>>>>>>> 6666c750d3438d189e75762f36d929d438dfabdf
        """
        Calculates the PV generated power in [kW] based on the DirectIrradiance column in the DataFrame.
        The formula used is:
        P = (1/1000)*efficiency_max*cell_area*DirectIrradiance*(1+Temp_coeff)*(T_STC-T_cell)*panel_count
        
        Args:
        - P is the PV generated power in [kW]
        - efficiency_max is the maximum efficiency of the panel
        - cell_area is the area of the cell in [m^2]
        - DirectIrradiance is the direct irradiance in [W/m^2]
        - Temp_coeff is the temperature coefficient of the panel
        - T_STC is the standard test condition temperature in [°C]
        - T_cell is the cell temperature in [°C]
        - panel_count is the number of panels

        Returns:
        - None   
        """
        
        T_cell=self.pd['T_RV_degC']
        # Check if the 'beamirradiance' column is empty
        if 'DirectIrradiance' in self.pd.columns and not self.pd['DirectIrradiance'].empty:
<<<<<<< HEAD
            # Calculate the PV generated power
            self.pd['PV_generated_power'] = efficiency_max*cell_area*self.pd['DirectIrradiance']*(1+Temp_coeff)*panel_count_parallel*panel_count_series
=======
            # Calculate the PV generated power in [kW]
            self.pd['PV_generated_power'] = (1/1000)*efficiency_max*cell_area*self.pd['DirectIrradiance']*(1+(Temp_coeff*(T_cell-T_STC)))*panel_count
>>>>>>> 6666c750d3438d189e75762f36d929d438dfabdf
        else:
            raise ValueError("The 'DirectIrradiance' column is empty or not present in the DataFrame")
        return None