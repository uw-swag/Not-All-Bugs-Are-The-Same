from keras.models import Sequential
from keras.layers import Dense
import keras.metrics
import pandas as pd
import numpy as np
import math
from keras.callbacks import CSVLogger
from sklearn.model_selection import train_test_split
import os
import statistics
from keras.models import load_model
from sklearn.metrics import mean_squared_error
from keras.utils import np_utils



'''

Add correct release IDs to nabats_dataset.csv

'''




df = pd.read_csv("../files/nabats_dataset.csv")
projects = set(df['project'].tolist())


#Get map of releases
releases = {}
for p in projects:
        releases[p] = df[df['project']==p]['minor'].min()

def get_release_id(releases, project, rel):
    try:
        min = releases[project]
        return int(range(min, min+3).index(rel))
    except:
        return 3

for i,r in df.iterrows():
    df.at[i,'release_id'] = get_release_id(releases,r['project'],r['minor'])

df.to_csv("../files/nabats_dataset.csv")
