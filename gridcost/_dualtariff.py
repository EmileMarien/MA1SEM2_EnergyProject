def dual_tariff(self) -> None:
        """Calculates and fills the `DualTariff` column using `electricity_contract`."""
        if self.electricity_contract is None:
            raise ValueError("ElectricityContract is required for dual_tariff calculation.")

        c = self.electricity_contract

        # Ensure GridFlow dtype
        self.pd["GridFlow"] = self.pd["GridFlow"].astype(float)

        def calculate_tariff_row(row):
            grid_flow = row["GridFlow"]
            dt = row.name

            if grid_flow < 0:  # consumption
                if dt.weekday() < 5 and 7 <= dt.hour < 22:
                    variable_tariff = c.dual_cons_peak
                else:
                    variable_tariff = c.dual_cons_offpeak
                cost = variable_tariff * (-grid_flow)
            else:  # production / injection
                # Revenue (likely negative cost)
                if dt.weekday() < 5 and 7 <= dt.hour < 22:
                    cost = c.dual_inj_peak * grid_flow
                else:
                    cost = c.dual_inj_offpeak * grid_flow

            return cost/100

        self.pd["DualTariff"] = self.pd.apply(calculate_tariff_row, axis=1)



        




