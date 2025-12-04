print('hello')
import pandas as pd
from financialmodel.models import ElectricityContract
from financialmodel.financialModel import FinancialModel

# df must have DateTime + GridFlow (or DateTime index + numeric column)
df = pd.read_csv("my_gridflow.csv", parse_dates=["DateTime"])

contracts = [
    ElectricityContract(contract_type="DynamicTariff", ...),
    ElectricityContract(contract_type="DualTariff", ...),
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
