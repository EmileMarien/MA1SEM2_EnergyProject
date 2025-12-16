import pandas as pd
from financialmodel.models import ElectricityContract
from financialmodel.financialmodel import FinancialModel
from gridcost.gridcost import GridCost

# df must have DateTime + GridFlow (or DateTime index + numeric column)
df = pd.read_csv("data/Consumption_data_541448965001643820_2025-11-27.csv")
contract = ElectricityContract.from_pdf(
    "data/contracts/Mega-FR-EL-B2C-BX-102025-TA0525-Var_(1).pdf",
    contract_type="DynamicTariff",  # default
)
#TODO: store in electricity contract also info of the provider (more metadata of contract)

belpex_path = GridCost.update_belpex_quarter_hourly()
contracts = [
    ElectricityContract(contract_type="DynamicTariff"),
    ElectricityContract(contract_type="DualTariff"),
]

fm = FinancialModel(discount_rate=0.05)

results = fm.optimise_contracts_from_consumption(
    contracts=contracts,
    consumption_data_df=df,
    horizon_years=20,
    return_breakdown=True,
    top_k=None,
)

best_contract = results[0]["contract"]
fm.plot_optimisation_cost_vs_solar_panels(results=results, cost_metric="npv_cost")





