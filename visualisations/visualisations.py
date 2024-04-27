
# Function to plot a given dataset
from typing import List

from matplotlib import pyplot as plt
import pandas as pd
import scienceplots
"""

def plot_columns(column_names: List[str]):
    
    Plots multiple columns from the DataFrame with a datetime index.

    Args:
        column_names (list): A list of column names to plot.
    

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

"""

def plot_dataframe(df:pd.DataFrame=pd.DataFrame):
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
    #plt.style.use(['science','ieee'])
    # Add legend
    ax.legend()

    # Show the plot
    plt.show()

def plot_series(series:List[pd.Series]=[pd.Series], title:str='Series', xlabel:str='Datetime', ylabel:str='Value', secondary_series:List[pd.Series]=[],ylabel2:str='Value'):
    """
    Plots a given Series with a datetime index.

    Args:
        series (List[pd.Series]): The primary Series to plot.
        title (str): The title of the plot.
        xlabel (str): The label for the x-axis.
        ylabel (str): The label for the y-axis.
        secondary_series (List[pd.Series]): The secondary Series to plot on a secondary axis.
    """

    # Create the plot
    fig, ax = plt.subplots()
    legendentries= []

    # Plot the primary Series
    for serie in series:
        ax.plot(serie.index, serie)
        legendentries.append(serie.name)

    # Plot the secondary Series on a secondary axis
    for secondary_serie in secondary_series:
        ax2 = ax.twinx()
        ax2.plot(secondary_serie.index, secondary_serie, linestyle='--')
        legendentries.append(secondary_serie.name)

    # Add labels and title
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    if 'ax2' in locals():
        ax2.set_ylabel(ylabel2)
    ax.set_title(title)
    #plt.style.use(['science','ieee'])

    # Add legend
    ax.legend(legendentries)

    # Show the plot
    plt.show()