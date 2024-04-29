

import pandas as pd


def add_EV_load(self,filepath:str=''):
    if filepath != '':
        self.pd['Load_EV_kW'] = pd.read_excel(filepath)
    else:
        self.pd['Load_EV_kW'] = 0
    self.pd['Load_EV_kW'] = self.pd['Load_EV_kW'].interpolate(method='linear')
    self.pd['Load_house_kW']=self.pd['Load_kW']
    self.pd['Load_kW'] = self.pd['Load_house_kW'] + self.pd['Load_EV_kW']
    return None
