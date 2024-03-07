# Function to plot a given dataset
from typing import List

from matplotlib import pyplot as plt
import pandas as pd


def plot_columns(self, column_names: List[str]):
    """
    Plots multiple columns from the DataFrame with a datetime index.

    Args:
        column_names (list): A list of column names to plot.
    """

    # Assert column names are valid
    assert all(col in self.pd.columns for col in column_names), f"Invalid column names: {', '.join(set(column_names) - set(self.pd.columns))}"

    # Create the plot
    fig, ax = plt.subplots()

    # Iterate through columns and plot them
    for col in column_names:
        ax.plot(self.pd.index, self.pd[col], label=col)

    # Add labels and title
    ax.set_xlabel("Datetime")
    ax.set_ylabel(column_names)
    ax.set_title(f'Plot of {column_names}')

    # Add legend
    ax.legend()

    # Show the plot
    plt.show()

def plot_dataframe(self, df:pd.DataFrame=pd.DataFrame):
    """
    Plots a given DataFrame with a datetime index.

    Args:
        df (DataFrame): The DataFrame to plot.
    """

    # Create the plot
    fig, ax = plt.subplots()

    # Iterate through columns and plot them
    for col in df.columns:
        ax.plot(df.index, df[col], label=col)

    # Add labels and title
    ax.set_xlabel("Datetime")
    ax.set_ylabel(df.columns)
    ax.set_title(f'Plot of {df.columns}')

    # Add legend
    ax.legend()

    # Show the plot
    plt.show()