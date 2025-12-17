import logging

logger = logging.getLogger(__name__)

def capacity_tariff(self) -> float:
        """Calculates the yearly capacity tariff using `electricity_contract.capacity_tariff_rate`."""
        if self.electricity_contract is None:
            raise ValueError("ElectricityContract is required for capacity_tariff calculation.")

        highest_periods = []
        for month in range(1, 13):
            monthly_data = self.pd["GridFlow"][self.pd["GridFlow"].index.month == month]
            if monthly_data.empty:
                continue

            grouped_data = (
                monthly_data
                .resample("15min")
                .sum()
                / 60.0
            )
            highest_period = grouped_data.max()
            highest_periods.append(highest_period)

        if not highest_periods:
            return 0.0

        logger.debug("Monthly highest periods: %s", highest_periods)

        average_highest_kw = sum(highest_periods) / len(highest_periods)
        billing_kw = max(average_highest_kw, 2.5)

        capacity_cost = billing_kw * self.electricity_contract.capacity_tariff
        return float(capacity_cost)