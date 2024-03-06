
def dual_tariff(self, daytariff:int=0, nighttariff:int=0):
    """
    Calculates the dual tariff for a specific time, day and colation
    """ 
    # Define a function to calculate the dual tariff for a single row
    def calculate_tariff_row(row, daytariff, nighttariff,fixed_tariff=0):
        """
        Calculates the dual tariff for a single row
        """
        if row['time'] >= 7 and row['time'] <= 22:
            variable_tariff=daytariff
        else:
            variable_tariff=nighttariff

        cost=variable_tariff*row['GridPower']+fixed_tariff

