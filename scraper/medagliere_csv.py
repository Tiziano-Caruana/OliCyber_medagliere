# transorm medagliere.json to medagliere.csv

import pandas as pd
import json

with open(f'../data/medagliere.json', 'r') as f:
    json_data = json.load(f)

df = pd.DataFrame(json_data)
df.to_csv('../data/medagliere.csv', index=False)

