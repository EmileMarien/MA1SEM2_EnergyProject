
def dynamic_tariff(self, tariff:float=0):
    """
    Calculates the dynamic tariff for a specific time, day and colation
    """ 
    # Define a function to calculate the dynamic tariff for a single row
    def calculate_tariff_row(row, tariff):
 