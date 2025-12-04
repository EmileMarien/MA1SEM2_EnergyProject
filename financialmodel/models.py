from dataclasses import dataclass

@dataclass
class SolarSpec:
    solar_panel_cost: float
    solar_panel_count: int
    solar_panel_lifetime: int
    panel_surface: float
    annual_degredation: float
    panel_efficiency: float
    temperature_coefficient: float

    @property
    def total_solar_panel_cost(self) -> float:
        return self.solar_panel_cost * self.solar_panel_count

    @property
    def total_panel_surface(self) -> float:
        return self.panel_surface * self.solar_panel_count


@dataclass
class BatterySpec:
    battery_cost: float
    battery_count: int
    battery_lifetime: int
    battery_capacity: float

    @property
    def total_battery_cost(self) -> float:
        return self.battery_cost * self.battery_count


@dataclass
class InverterSpec:
    inverter_cost: float
    inverter_lifetime: int
    inverter_efficiency: float
    DC_battery: float
    DC_solar_panels: float
    AC_output: float


from dataclasses import dataclass


@dataclass
class ElectricityContract:
    """
    Contains all contract-related cost parameters.

    All monetary values are in €/kWh or €/year unless stated otherwise.
    """

    # Contract type label used for GridCost tariff selection
    contract_type: str = "DynamicTariff"  # "DualTariff" or "DynamicTariff"

    # --- Dual tariff parameters (€/kWh) ---
    dual_peak_tariff: float = 0.30          # example
    dual_offpeak_tariff: float = 0.20       # example
    dual_injection_tariff: float = -0.05    # €/kWh (negative = revenue)
    dual_fixed_tariff: float = 0.0          # €/kWh adder, if any

    # --- Capacity tariff (€/kW/year) ---
    capacity_tariff_rate: float = 40.0      # example

    # --- Other components (defaults can be overridden) ---
    data_management_cost: float = 13.95     # €/year
    purchase_rate_injection: float = 0.00414453    # €/kWh
    purchase_rate_consumption: float = 0.0538613   # €/kWh
    excise_duty_energy_contribution_rate: float = (0.0503288 + 0.0020417)  # €/kWh
    fixed_component_dual: float = 111.3     # €/year
    fixed_component_dynamic: float = 100.7  # €/year

