import os
import re
import sys
import pandas as pd
import numpy as np

from os import listdir
from os.path import isfile, join

project = sys.argv[1]

df = pd.read_csv("../files/"+project+"/train_data2.csv")
df['cc'] = 0
df['loc'] = 0

metrics = pd.read_csv("../files/buggy_cc_loc.csv")
metrics = metrics.loc[metrics['Kind']=="File"]
metrics['index'] = metrics["Name"].apply(lambda n : n.replace(".java",""))

size = df.shape[0]

for i,r in df.iterrows():
    #print(i,size,end="\r")

    try:
        metric_row = metrics.loc[metrics['index'] == r['index1']].iloc[0]
        df.at[i,'cc'] = metric_row['SumCyclomatic']
        df.at[i,'loc'] = metric_row['CountLineCode']

        print(metric_row['SumCyclomatic'])

    except Exception as e:
        print(e)
        pass


df.to_csv("../files/"+project+"/train_data3.csv",index=False)
print(df[['cc','loc']].head())
