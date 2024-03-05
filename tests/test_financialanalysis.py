import os
import unittest
import pandas as pd
from context import pc
from context import fa

class test_DualTariff(unittest.TestCase):
    def setUp(self):
        
        self.powercalculations_test = pc.PowerCalculations(file_path_irradiance='data/Irradiance_data_vtest.xlsx',file_path_load='data/Load_profile_6_vtest.xlsx') 

    def test_calculate(self):
        return None