

import pandas as pd

from visualisations.visualisations import plot_series



def add_EV_load(self,type:str='smart'):
    """
    Add electric vehicle (EV) load data to the DataFrame.
    The EV load data is read from an Excel file and interpolated to match the time index of the DataFrame.
    The EV load is added to the 'Load_kW' column of the DataFrame.
    type: str
    """
    filepath='data/EV Calculation.xlsx'

    xls = pd.ExcelFile(filepath)
    df1 = pd.read_excel(xls, 'Sheet1')

    # Raise error if the EV load file does not contain the required columns (Datetime, Load_EV_kW_no_SC, Load_EV_kW_with_SC, Week & Correction_factor)
    assert 'Datetime' in df1.columns, "The EV load file does not contain the column 'Datetime'."
    assert 'Load_EV_kW_no_SC' in df1.columns, "The EV load file does not contain the column 'Load_EV_kW'."
    assert 'Week' in df1.columns, "The EV load file does not contain the column 'Week'."
    assert 'Correction_factor' in df1.columns, "The EV load file does not contain the column 'Correction_factor'."

    # Create dataframe with the EV load data for the first week
    if type=='B2G':
        return None
            



    elif type=='smart':
        week_values=df1[['Datetime','Load_EV_kW_with_SC']]
        week_values.rename(columns={'Load_EV_kW_with_SC':'Load_EV_kW'},inplace=True)
    elif type=='dumb':
        week_values=df1[['Datetime','Load_EV_kW_no_SC']]
        week_values.rename(columns={'Load_EV_kW_no_SC':'Load_EV_kW'},inplace=True)
    else:
        raise ValueError("The type must be either 'smart', 'B2G' or 'dumb'.")
    week_values.set_index('Datetime',inplace=True)
    week_values.index = pd.to_datetime(week_values.index).round('T')
    frequence=self.pd.index.freq
    week_values=week_values.asfreq(freq=frequence, method='bfill')
    print(week_values)
    week_values.reset_index(drop=True, inplace=True)  # Reset the index of values

    # Create a DataFrame with the weekly correction factors
    correction_factors = df1['Correction_factor'].head(53).tolist()
    #print(correction_factors)

    # Create a new column in the DataFrame for the EV load
    date_range_year = pd.date_range(start=self.pd.index[0], end=self.pd.index[-1], freq='W-MON')  # Weekly frequency
    # Initialize the 'Load_EV_kW' column with zeros
    self.pd['Load_EV_kW'] = 0.0

    for i in range(len(date_range_year)):
        week_start_date = date_range_year[i]
        print(week_start_date)
        values=week_values*correction_factors[i]
        
        # Calculate the end date, 
        end_date=min(week_start_date + pd.DateOffset(hours=167),self.pd.index[-1])

        values=values.head(int((end_date-week_start_date).total_seconds()/60+1)).set_index(self.pd.loc[week_start_date:end_date, 'Load_EV_kW'].index)

        self.pd.loc[week_start_date:end_date].update(values)
        print(self.pd.loc[week_start_date:end_date, 'Load_EV_kW'])


    plot_series([self.pd['Load_EV_kW']], title='EV Load', xlabel='Datetime', ylabel='Load [kW]', display_time='year')
    #self.pd['Load_EV_kW'] = self.pd['Load_EV_kW'].interpolate(method='linear')
    self.pd['Load_house_kW']=self.pd['Load_kW']
    self.pd['Load_kW'] = self.pd['Load_house_kW'] + self.pd['Load_EV_kW']
    return None

