"""
This module formats the data from our model
and outputs it as a JSON file.
"""
import pandas as pd
from model import predictions, probs, test
from clean import countries_json

# Retain categoricals in groupby.
f = {'milper': 'mean', 'irst': 'mean', 'tpop': 'mean', 'milex': 'mean', 'exports': 'mean', 'pred_proba': 'mean', 'StateNme': 'first'}

test['pred_proba'] = probs.T[1]
country_year_groups = test.groupby(['ccode', 'year']).agg(f).reset_index()

geo_df = pd.merge(left=country_year_groups, right=countries_json, on = ['StateNme'], how = 'left')
# Remove countries with missing lat./long.
geo_df = geo_df.dropna(subset=['latitude', 'longitude'])
geo_df_2007 = geo_df[geo_df['year'] == 2007].drop(axis=1, columns='year')

with open('mvp_lat_long_features.json', 'w') as f:
  f.write(geo_df_2007.to_json(orient='records'))