# Function to plot a given dataset
from typing import List

from matplotlib import pyplot as plt


def plot(self, column_name: List[str]):
    """
    Plots the given dataset using the specified column name

    Args:
    df (DataFrame): The DataFrame containing the dataset
    column_name (str[]): The name of the column(s) to be plotted. Choose between: GlobRad, DiffRad, T_CommRoof_degC, T_RV_degC 
    """
    for col in column_name:
        plt.plot(self.pd['DateTime'], self.pd[col])
    plt.xlabel('Date Time')
    plt.ylabel(column_name)
    plt.title(f'Plot of {column_name}')
    plt.legend(column_name)
    plt.show()   