
def dual_tariff(self, day_tariff:int=0, night_tariff:int=0,fixed_tariff:int=1):
    """
    Calculates the dual tariff for a specific time, day and colation
    """ 
    # Define a function to calculate the dual tariff for a single row
    def calculate_tariff_row(row, day_tariff, night_tariff,fixed_tariff=0):
        """
        Calculates the dual tariff for a single row
        """
        if row['time'] >= 7 and row['time'] <= 22:
            variable_tariff=day_tariff
        else:
            variable_tariff=night_tariff

        cost=variable_tariff*row['GridPower']+fixed_tariff
        return cost
    
    # Apply the calculation function to each row with vectorized operations
    self.pd['DualTariffCost'] = self.pd.apply(
        lambda row: calculate_tariff_row(row=row, day_tariff=day_tariff,night_tariff=night_tariff, fixed_tariff=fixed_tariff), axis=1
    )

    return None

