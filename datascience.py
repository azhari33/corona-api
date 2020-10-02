import pandas as pd
import json
from pandas.io.json import json_normalize
url = pd.read_json('https://corona-live-api.herokuapp.com/')

df = pd.DataFrame(url)
covid = pd.json_normalize(df['data'])
covid.to_excel('hasil.xlsx')
