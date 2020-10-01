import pandas as pd
import numpy as np
import math
import os
import statistics

vector_file = open("../files/all_target_file_vectors.txt",'r')
dfs = []

df = pd.DataFrame(columns = ['vector','filepath', 'filename','project', 'major', 'minor'])

#Get file length
file_length = 0.0
for line in vector_file:
    file_length += 1.0
vector_file.seek(0)

#Loop through c2v output
line_num=0
for line in vector_file:
    try:
        #Output progress
        line_num += 1
        progress = str(round(100*(line_num/file_length),2))+'%'+"\t Vector number:"+str(line_num)
        print(progress,end='\r')

        split = line.split(',')
        name = split[0]
        method_name = split[1]
        vector = split[-1]
        release = name.split('/')[6].split('-')[1].split('.')
        major = int(release[0])
        minor = int(release[1])
        project = name.split('/')[7]

        #Add each method to the new dataframe
        df = df.append({
            'vector':vector,
            'filepath': name,
            'filename': name.split('/')[-1],
            'method': method_name,
            'project': project,
            'major': major,
            'minor': minor
            },ignore_index=True)

        #Trying to speed it up
        if df.shape[0] == 10000:
            dfs.append(df)
            df = pd.DataFrame(columns = ['vector','filepath', 'filename','project', 'major', 'minor'])




    except Exception as e:
        print(e)

vector_file.close()

dfs.append(df)

df = pd.concat(dfs)
df.to_csv("../files/all_target_file_vectors.csv",index=False)
