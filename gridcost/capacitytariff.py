
def capacity_tariff(self, tariff:int=1):
    """
    Calculates the capacity tariff cost for the full period which is depending on the highest consumption for each month
    """
    month = 1
    grouped_data = self.pd["GridFlow"][self.pd["GridFlow"].index.month == month].resample('15T').sum() / 60
    print(grouped_data)
    highest_periods = []
    for month in range(1, 13):
        grouped_data = self.pd["GridFlow"][self.pd["GridFlow"].index.month == month].resample('15T').sum() / 60
        highest_period= grouped_data.max()
        Capacity_tariff = tariff * highest_period
        highest_periods.append(Capacity_tariff)
    Capacity_cost=highest_periods.sum()
    return Capacity_cost