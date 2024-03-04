
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