import os
import re
import sys
import pandas as pd




df = pd.read_csv("../files/accumulo/train_data3.csv")

buggy = df.loc[df['buggy']==1]
clean = df.loc[df['buggy']==0]



print(buggy.shape)
print(clean.shape)




'''
df = pd.read_csv("../files/accumulo/train_data_test.csv")

print(df.columns.values)

df['vector'] = df['vector'].apply(lambda v : v.replace('\n','').split(' '))
df['vector'] = df['vector'].apply(lambda v : [float(i) for i in v])

buggy_vectors = df.loc[df['buggy']==1]
fixed_vectors = df.loc[df['fixed']==1]

print(buggy_vectors.shape)
print(fixed_vectors.shape)

for i,r in buggy_vectors.iterrows():
    print(len(r['vector']))



projects = ['accumulo', 'bookkeeper', 'camel', 'cassandra', 'cxf', 'derby', 'felix']#, 'hive', 'openjpa', 'pig', 'wicket']

buggy_list = []

for p in projects:
    df = pd.read_csv("../files/"+p+"/train_data_test.csv")
    print(p,df.shape)
    buggy_vectors = df.loc[df['buggy']==1]
    fixed_vectors = df.loc[df['fixed']==1]
    buggy_list.append(buggy_vectors)

    print("Buggy:",buggy_vectors.shape)
    print("Fixed:",fixed_vectors.shape)

all_buggy_df = pd.concat(buggy_list)
print(all_buggy_df.shape)
'''
