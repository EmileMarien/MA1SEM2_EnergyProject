from gridcost.gridcost import GridCost
from gridcost._belpex import _scrape_belpex_page, BELPEX_QUARTER_HOURLY_URL
from financialmodel.models import ElectricityContract


consumption_csv="C:\\Users\\67583\\OneDrive - Bain\\Documents\\Personal projects\\MA1SEM2_EnergyProject\\data\\Consumption_data_541448965001643820_2025-11-27.csv"
# 0. (Optional) low-level Belpex scraping demo
#    This hits the Elexys Belpex page and returns a normalised DataFrame.
raw_belpex = _scrape_belpex_page(BELPEX_QUARTER_HOURLY_URL)
print("Preview of raw Belpex data scraped from the site:")
print(raw_belpex.head())

# 1. Update / create Belpex file under data/
#    This uses the same scraping logic internally and stores/updates:
#    data/belpex_quarter_hourly.csv (by default).
belpex_path = GridCost.update_belpex_quarter_hourly(
    # optional extras:
    initial_excel=r"C:\Users\67583\Downloads\quarter-hourly-spot-belpex--c--elexys (1).xlsx",
    # max_pages=32,
)
print(f"Belpex data updated and stored at: {belpex_path}")

# 2. Use that file as BelpexFilter input for GridCost
contract = ElectricityContract(contract_type="DynamicTariff")

gc = GridCost(
    consumption_data_csv=consumption_csv,
    electricity_contract=contract,
)

# 3. Compute total cost for the chosen tariff
total_cost = gc.calculate_total_cost(tariff="DynamicTariff")
print(f"Total cost (DynamicTariff): {total_cost:.2f} €")

# 4. Visualise: consumption vs cost on one graph
#    Requires that you've added the `plot_consumption_and_cost` method
#    inside the GridCost class as discussed.
gc.plot_consumption_and_cost(
    tariffs=["DynamicTariff"],  # or ["DynamicTariff", "DualTariff"] if both available
    # Optional:
    # start="2024-01-01",
    # end="2024-01-07",
    # rolling=4,  # smooth over 4 timesteps
)
