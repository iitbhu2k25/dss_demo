from .models import Weight
from sklearn.preprocessing import MinMaxScaler
import pandas as pd
import numpy as np
def weight_redisturb(headings):
   weights=Weight.objects.values(*headings)
   weights=list(weights)
   print('weights',weights)
   weights=weights[0]
   sum:float=0.0
   for i in weights:
      sum+=weights[i]
   for i in weights:
      weights[i]=weights[i]/sum
   return weights

def normalize_data(data):
   numerical_columns = [key for key in data[0].keys() if isinstance(data[0][key], (int, float)) and key != 'name']
   numerical_data = [[entry[col] for col in numerical_columns] for entry in data]
   scaler = MinMaxScaler()
   normalized_values = scaler.fit_transform(numerical_data)
   normalized_data = []
   for i, entry in enumerate(data):
        normalized_entry = {'name': entry['name']}  # Keep the 'name' column unchanged
        for j, col in enumerate(numerical_columns):
            normalized_entry[col] = normalized_values[i][j]
        normalized_data.append(normalized_entry)
   return normalized_data

def rank_process(data,weight_key,headings):
    df = pd.DataFrame(data, columns=headings)
    ranks=df.rank(method='min', ascending=False)
    weightted_rank=ranks*pd.Series(weight_key)
    df['rank']=weightted_rank.sum(axis=1)
    # for find the rank probability
    # scaler = MinMaxScaler()
    # df['rank'] = scaler.fit_transform(df[['rank']])
    df['name'] = [entry['name'] for entry in data]
    final_results = df[['name', 'rank']]
    final_results=final_results.to_dict(orient='records')
    return final_results