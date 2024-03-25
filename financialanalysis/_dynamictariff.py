
def dynamic_tariff(self, tariff:float=0):
    """
    Calculates the dynamic tariff for a specific time, day and location
    """ 
    # Define a function to calculate the dynamic tariff for a single row
    def calculate_tariff_row(row, tariff):
        grid_flow = row['Grid_flow']
        dynamic_cost = row['Dynamic_cost']
        if grid_flow > 0:
            cost = (0.1044*dynamic_cost+0.37)*1.06
            return cost
        if grid_flow < 0:
            cost = 0.0825*dynamic_cost - 0.955
            return cost
    return 0
