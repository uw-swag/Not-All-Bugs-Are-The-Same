import os
import re
import sys
import pandas as pd
import numpy as np

from os import listdir
from os.path import isfile, join




project = sys.argv[1]

df = pd.read_csv("../files/"+project+"/train_data.csv")
df = df.loc[df['buggy']==1]



#Loop through vector_data_output and add to DataFrame
#Export dataframe occasionally to keep speed up and data safe in case of crash
with open("../files/buggy_files_modified/"+project+"/vector_data.txt",'r') as vector_file:

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
            index = split[0].replace(".java","")
            vector = split[-1]

            #Add each method to the new dataframe
            df = df.append({
                'vector':vector,
                'buggy':0,
                'hash': np.nan,
                'fix_size':0,
                'priority':0,
                'experience':0,
                'index1':index,
                'index2':np.nan
                },ignore_index=True)

        except Exception as e:
            print(e)

df.to_csv("../files/"+project+"/train_data2.csv",index=False)
