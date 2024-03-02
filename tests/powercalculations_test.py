import unittest
import pandas as pd
from powercalculations import PowerCalculations  # replace with your actual module and class

class TestDirectIrradiance(unittest.TestCase):
    def setUp(self):
        self.your_class_instance = YourClass()  # replace with your actual class initialization if needed

    def test_calculate_direct_irradiance_specific(self):
        # Test with some specific values
        result = self.your_class_instance.calculate_direct_irradiance_specific(latitude=50, tilt_angle=30, day='2022-03-10 00:00', longitude=0, temperature=25)
        self.assertIsNotNone(result)
        self.assertIsInstance(result, float)

        # Test with some edge cases
        result = self.your_class_instance.calculate_direct_irradiance_specific(latitude=0, tilt_angle=0, day='2022-03-10 00:00', longitude=0, temperature=0)
        self.assertIsNotNone(result)
        self.assertIsInstance(result, float)

    def test_direct_irradiance(self):
        # Assuming your class has a pd attribute that is a DataFrame
        self.your_class_instance.pd = pd.DataFrame({
            'dayTime': ['2022-03-10 00:00', '2022-03-11 00:00', '2022-03-12 00:00']
        })
        self.your_class_instance.direct_irradiance()
        self.assertIn('DirectIrradiance', self.your_class_instance.pd.columns)
        self.assertEqual(len(self.your_class_instance.pd['DirectIrradiance']), 3)

if __name__ == '__main__':
    unittest.main()