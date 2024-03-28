import pandas as pd

class FinancialAnalysis():
    def __init__(self, data):
        # Convert Series to DataFrame if data is a Series
        if isinstance(data, pd.Series):
            dataframe = pd.DataFrame({'GridFlow': data})
            dataframe.index = pd.to_datetime(dataframe.index)
        # Use DataFrame directly if data is a DataFrame
        elif isinstance(data, pd.DataFrame):
            dataframe = pd.DataFrame(data['GridFlow'])
        else:
            raise ValueError("Input data must be either a Series or a DataFrame")

        # Check if all required columns are present
        required_columns = ['PowerGrid'] # [kW]
        missing_columns = [col for col in required_columns if col not in dataframe.columns]
        assert not missing_columns, f"The following columns are missing: {', '.join(missing_columns)}"

        # Assign the DataFrame to self.pd
        self.pd = dataframe

        # Initialize the columns that will be used for the calculations
        self.pd['DualTariff'] = None
        self.pd['DynamicTariff'] = None





    # Imported methods
    from ._getters import get_dataset
    from ._getters import get_irradiance
    from ._getters import get_load
    from ._getters import get_direct_irradiance
    from ._getters import get_PV_generated_power
    from ._getters import get_grid_cost_perhour
    from ._getters import get_grid_cost_total


    from ._export import export_dataframe_to_excel

    from ._dualtariff import dual_tariff
    from ._dynamictariff import dynamic_tariff
