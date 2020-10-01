import os
import re
import sys
import pandas as pd
import numpy as np

from os import listdir
from os.path import isfile, join


def extract_metrics_from_line(line):

    vector, buggy, hash, fix_size, priority, experience, index1, index2 = 0,0,0,0,0,0,0,np.nan

    line = line.split(',')
    vector = line[-1]
    info = line[0].split('_')
    hash = info[0]
    fix_size = info[1]
    index1 = info[3]
    index2 = info[4]

    if info[2] == "buggy":
        buggy = 1

    #Differentiate between methods that were fixed and methods that never had a bug
    if info[2] == "unchanged":
        buggy = 2

    # If the method is buggy, extract the last few metrics
    if buggy == 1:

        bfc_row = bfcs.loc[bfcs['BFC_id']==hash]
        bfc_row.reset_index(inplace=True)

        experience  = bfc_row.at[0,'author_exp']
        priority = bfc_row.at[0,'priority']

    return vector, buggy, hash, fix_size, priority, experience, index1, index2


#Get project name as argument
project = sys.argv[1]
path = '/home/kilby/Documents/code/c2v_models/files/'+project

#Prepare dataframe to hold training data
vector_df = pd.DataFrame(columns=['buggy','fix_size','priority','experience','hash','index1','index2','vector'])


#Use bfc data to get priority and experience levels
bfcs = pd.read_csv(path+'/bfcs.csv')


#Loop through vector_data_output and add to DataFrame
#Export dataframe occasionally to keep speed up and data safe in case of crash
with open("../files/"+project+"/vector_data.txt",'r') as vector_file:

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


            vector, buggy, hash, fix_size, priority, experience, index1, index2 = extract_metrics_from_line(line)

            #Add each method to the new dataframe
            vector_df = vector_df.append({
                'vector':vector,
                'buggy':buggy,
                'hash': hash,
                'fix_size':fix_size,
                'priority':priority,
                'experience':experience,
                'index1':index1,
                'index2':index2
                },ignore_index=True)

        except Exception as e:
            print(e)


vector_df.to_csv("../files/"+project+"/train_data.csv",index=False)
