import pandas as pd
import logging

logger = logging.getLogger(__name__)
import pandas as pd



def export_dataframe_to_excel(self, file_path: str):
    """
    Exports the DataFrame to an Excel file.

    Args:
        file_path (str): The path to the Excel file to be created.
    """

    self.pd.to_excel(file_path)

    logger.info("DataFrame exported successfully to: %s", file_path)
