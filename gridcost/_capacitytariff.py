
def capacity_tariff(self, tariff:int=1):
    """
    Calculates the capacity tariff cost for the full period which is depending on the highest consumption for each month
    """
    month = 1
    grouped_data = self.pd["GridFlow"][self.pd["GridFlow"].index.month == month].resample('15min').sum() / 60
    #print(grouped_data)
    highest_periods = []
    for month in range(1, 13):
        grouped_data = self.pd["GridFlow"][self.pd["GridFlow"].index.month == month].resample('15min').sum() / 60
        highest_period= grouped_data.max()
        Capacity_tariff = tariff * highest_period
        highest_periods.append(Capacity_tariff)
<<<<<<< HEAD:gridcost/capacitytariff.py
    Capacity_cost=highest_periods.sum()
    return Capacity_cost
=======

    Capacity_cost=sum(highest_periods)
    return Capacity_cost

>>>>>>> b0b61f5aa3a31abc0e50e5fcd6db6e49bc01cd2d:gridcost/_capacitytariff.py
