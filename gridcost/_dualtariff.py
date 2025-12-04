def dual_tariff(self) -> None:
        """Calculates and fills the `DualTariff` column using `electricity_contract`."""
        if self.electricity_contract is None:
            raise ValueError("ElectricityContract is required for dual_tariff calculation.")

        c = self.electricity_contract

        # Ensure GridFlow dtype
        self.pd["GridFlow"] = self.pd["GridFlow"].astype(float)

        def calculate_tariff_row(row):
            grid_flow = row["GridFlow"]

            if grid_flow < 0:  # consumption
                dt = row.name
                if dt.weekday() < 5 and 7 <= dt.hour < 22:
                    variable_tariff = c.dual_peak_tariff
                else:
                    variable_tariff = c.dual_offpeak_tariff

                cost_per_kwh = variable_tariff + c.dual_fixed_tariff
                cost = cost_per_kwh * (-grid_flow)
            else:  # production / injection
                # Revenue (likely negative cost)
                cost = c.dual_injection_tariff * grid_flow

            return cost

        self.pd["DualTariff"] = self.pd.apply(calculate_tariff_row, axis=1)




