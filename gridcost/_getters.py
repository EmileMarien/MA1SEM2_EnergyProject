
from typing import List

def get_irradiance(self):
    """
    Returns the irradiance data
    """
    return self.pd['DiffRad']

def get_load(self):
    """
    Returns the load data
    """
    return self.pd['Load_kW']   

def get_dataset(self):
    """
    Returns the dataset
    """
    return self.pd

def get_direct_irradiance(self):
    """
    Returns the direct irradiance data
    """
    return self.pd['DirectIrradiance']

def get_PV_generated_power(self):
    """
    Returns the PV generated power data
    """
    return self.pd['PV_generated_power']

def get_grid_cost_perhour(self,calculationtype:str="DualTariff"):
    """
    Returns the grid cost data based on the specified type of cost calculation
    """
    return self.pd[calculationtype]

def get_grid_cost_total(self,calculationtype:str="DualTariff"):
    cost_perhour=self.pd[calculationtype]
    cost_total=sum(cost_perhour)
    return cost_total

def get_columns(self,columns:List[str]):
    """
    Returns the dataset with the specific columns
    """

    assert all(col in self.pd.columns for col in columns), 'The columns must be present in the DataFrame'

    return self.pd[columns]

def get_total_energy_from_grid(self):
    """
    Returns the total energy in kWh taken from the grid
    """
    return sum(self.pd['GridFlow'])