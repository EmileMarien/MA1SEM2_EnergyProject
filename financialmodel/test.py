import pandas as pd
from financialmodel.models import ElectricityContract
from financialmodel.financialmodel import FinancialModel
from gridcost.gridcost import GridCost

# df must have DateTime + GridFlow (or DateTime index + numeric column)
df = pd.read_csv("data/Consumption_data_541448965001643820_2025-11-27.csv",sep=';')
#contract = ElectricityContract.from_pdf(
#    "data/contracts/Mega-FR-EL-B2C-BX-102025-TA0525-Var_(1).pdf",
#    contract_type="DynamicTariff",  # default
#)
#TODO: store in electricity contract also info of the provider (more metadata of contract)

belpex_path = GridCost.update_belpex_quarter_hourly()
contracts = [
    ElectricityContract(contract_type="DynamicTariff",
                        supplier="Mega",
                        language="FR",
                        dynamic_cons_var_peak=1.08,
                        dynamic_cons_var_offpeak=1.08,
                        dynamic_cons_fix_peak=1,
                        dynamic_cons_fix_offpeak=1,
                        dynamic_inj_var_peak=0.9,
                        dynamic_inj_var_offpeak=0.9,
                        dynamic_inj_fix_peak=-2.75,
                        dynamic_inj_fix_offpeak=-2.75,
                        dynamic_fix=31.8,
                        capacity_tariff_rate=53.2565,
                        green_power_fee=2.575,
                        excise_duty=5.03288,
                        energy_contribution=0.20417,
                        data_management_cost=13.95)

    ,
    ElectricityContract(contract_type="DualTariff",
                        supplier="EnergyVision",
                        language="NL",
                        dual_cons_peak=9.54,
                        dual_cons_offpeak=9.54,
                        dual_inj_peak=1.59,
                        dual_inj_offpeak=1.59,
                        dual_fix=111.3,
                        capacity_tariff_rate=53.2565,
                        green_power_fee=1.554,
                        excise_duty=5.03288,
                        energy_contribution=0.20417,
                        data_management_cost=13.95)]

fm = FinancialModel(discount_rate=0.05)

results = fm.optimise_contracts_from_consumption(
    contracts=contracts,
    consumption_data_df=df,
    horizon_years=20,
    return_breakdown=True,
    top_k=None,
)
print(f"Found {len(results)} optimisation results.")
npvs = [r["annual_cost_year1"] for r in results]
print("Annual cost year 1 (€):", npvs)
print(results)

best_contract = results[0]["contract"]
fm.plot_contract_comparison_cost_and_consumption(
    results=results)




