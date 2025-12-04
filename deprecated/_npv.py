

def calculate_npv(capex, battery_lifetime, battery_cost, solar_panel_lifetime, total_solar_panel_cost, discount_rate, total_panel_surface ,annual_degredation, panel_efficiency, temperature_Coefficient,  tilt_angle, Orientation, battery_capacity, battery_count):
    # Calculate the least common multiple (LCM) of battery and solar panel lifetimes
    

    def lcm(x, y):
        from math import gcd
        return x * y // gcd(x, y)

    lcm_lifetime = lcm(battery_lifetime, solar_panel_lifetime)

    # Calculate cash flows for total project
    total_cash_flows = [-capex]

    for i in range(1, lcm_lifetime + 1):
        # Calculate cash flow for the current year
        current_year_in_cycle = (i - 1) % solar_panel_lifetime + 1
        current_cash_flow = grid_cost_initial - grid_cost(year_in_lifetime=current_year_in_cycle, total_panel_surface ,annual_degredation, panel_efficiency, temperature_Coefficient,  tilt_angle, Orientation, battery_capacity, battery_count)
        total_cash_flows.append(current_cash_flow)

        # Check if it's time for reinvestment in solar panels
        if i % solar_panel_lifetime == 0:
            total_cash_flows[i] -= total_solar_panel_cost

        # Check if it's time for reinvestment in batteries
        if i % battery_lifetime == 0:
            total_cash_flows[i] -= battery_cost

    # Calculate NPV
    npv = 0
    for i, cash_flow in enumerate(total_cash_flows):
        npv += cash_flow / (1 + discount_rate) ** i

    return npv