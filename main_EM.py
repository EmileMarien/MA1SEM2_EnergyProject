


import pickle


file = open('data/combined_dataframe','rb')
irradiance=pickle.load(file)
file.close()

print(irradiance.get_dataset())
