
# Function to plot a given dataset
from typing import List

from matplotlib import pyplot as plt
import pandas as pd
import scienceplots
import re
import sys
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

def plot_series(series:List[pd.Series]=[pd.Series], title:str='Series', xlabel:str='Datetime', ylabel:str='Value', secondary_series:List[pd.Series]=[],ylabel2:str='Value',selected_format:str=None,display_time = None):
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
    #plt.rcParams['text.usetex'] = True
    fontsize=15
    fig, ax = plt.subplots(figsize=(6, 4), tight_layout=True)
    lns=[]
    line_styles=['-', '--', '-.', ':', 'solid', 'dashdot', 'dotted', 'dashed']
    line_colors=['b', 'r', 'c', 'm', 'y', 'k', 'g','w']
    # Plot the primary Series
    for i in range(len(series)):
        serie=series[i]
        lns+=ax.plot(serie.index, serie,label=serie.name,linestyle=line_styles[i],color=line_colors[i])

    # Plot the secondary Series on a secondary axis
    for j in range(len(secondary_series)):
        secondary_serie=secondary_series[j]
        ax2 = ax.twinx()
        lns+=ax2.plot(secondary_serie.index, secondary_serie,label=secondary_serie.name, color=line_colors[j+2],linestyle=line_styles[j+2])

    length=series[0].shape[0]
    if display_time=='hour':
        ax.set_xticks(range(0, length, length//24))
    # Add labels and title
    ax.set_xlabel(xlabel,fontsize=fontsize)
    ax.set_ylabel(ylabel,fontsize=fontsize)
    if 'ax2' in locals():
        ax2.set_ylabel(ylabel2)
    
    # add legend
    labs = [l.get_label() for l in lns]
    ax.legend(lns, labs, loc=0,fontsize=fontsize)
    ax.set_title(title,fontsize=fontsize)
    #plt.style.use(['science','ieee'])
    #if selected_format!=None:
    #    ax.xaxis.set_major_formatter(selected_format)

    # Show the plot
    plt.show()