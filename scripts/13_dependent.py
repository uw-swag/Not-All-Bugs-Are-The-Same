import os
import pandas as pd
import numpy as np
import re
import datetime
import math
from datetime import time

"""

This script takes the output from independent.py (independent.csv), which 
contains all of the independent variables for each file, and adds in the 
dependent variables. The output is final_dataset.csv, the complete dataset.

"""

def short_path(path):
    split = path.split('/')
    sp = ""
    num_dirs = 4
    for x in range(-1*num_dirs,0):
        if len(split) >= abs(x):
            sp = sp+"/"+split[x]
    return sp


#Working directory
dir = os.getcwd()+"/.."
os.chdir(dir)

project_names = ["accumulo","bookkeeper","camel","cassandra","cxf","derby","felix","hive","openjpa","pig","wicket"]


#Necessary pre-made data frames
bfc_df = pd.read_csv(dir+"/intermediate_files/target_bfcs.csv")
numstats = pd.read_csv(dir+"/intermediate_files/numstats/all_numstats.csv")
release_dates_df = pd.read_csv(dir+"/intermediate_files/release_dates/version_data.csv")
targets = pd.read_csv(dir+"/intermediate_files/target_releases.csv")

release_dates_df['pre'] = pd.to_datetime(release_dates_df['pre'])
release_dates_df['post'] = pd.to_datetime(release_dates_df['post'])
release_dates_df['date'] = pd.to_datetime(release_dates_df['date'])

bfc_df['BFC_date'] = pd.to_datetime(bfc_df['BFC_date'])

#The final df starts out containing only independent variables
final_df = pd.read_csv(dir+"/intermediate_files/independent.csv")


total_rows = bfc_df.shape[0]
total_rows_counted = 1



for project_name in project_names:

    #Make a dict to track numbugs
    numbug_dict = {}

    #Divide dataframes by project to make searching faster
    project_bfcs = bfc_df.loc[bfc_df['project'] == project_name.upper()]
    project_releases = release_dates_df.loc[release_dates_df['project'] == project_name]
    project_numstats = numstats.loc[numstats['project'] == project_name]
    
    #Get version info
    target_versions = sorted(targets.loc[targets['project'] == project_name]['minor'].tolist())
    
    counter = 1
    

    for index, row in project_bfcs.iterrows():
        
        #print(project_name,(10-len(project_name))*" ",":  ",counter,"/",project_bfcs.shape[0], end="\r")
        print("Finalizing dataset: "+str(math.floor((total_rows_counted/total_rows)*100 ))+"%", end="\r")
        counter += 1
        total_rows_counted += 1
        
        #get numstat subset
        commit_numstats = project_numstats.loc[project_numstats['hash'] == row['BFC_id']]
          
        #If the commit happened in the post release period, add the dependent variables to the final dataframe

        for i,r in commit_numstats.iterrows():
        
            if r['pre'] == 0:
            
                sp = short_path(r['filepath'])
                
                #Multiple commits can be made to the same file to address the same bug.
                #This should still only count as one bug, therefore we will
                #check if the issue has already been counted for current file (for num_bugs calculation)
                newbug = 0
                if row['minor'] in numbug_dict:
                    if sp in numbug_dict[row['minor']]:
                        if row['bug_id'] not in numbug_dict[row['minor']][sp]:
                            newbug = 1
                            numbug_dict[row['minor']][sp].append(row['bug_id'])
                    else:
                        newbug = 1
                        numbug_dict[row['minor']][sp] = [row['bug_id']]
                else:
                    newbug = 1
                    numbug_dict[row['minor']] = {sp:[row['bug_id']]}
                    
                    

                
                final_row = final_df.loc[(final_df['shortpath'] == sp) & (final_df['minor'] == row['minor'])]
                final_df.loc[(final_df['project'] == project_name) & (final_df['shortpath'] == sp) & (final_df['minor'] == row['minor']),'num_post'] = final_row['num_post'] + 1
                final_df.loc[(final_df['project'] == project_name) & (final_df['shortpath'] == sp) & (final_df['minor'] == row['minor']),'exp'] = final_row['exp'] + row['author_exp']*newbug #Multiply by newbug because exp is already an average of all devs who commited a fix for that bug
                final_df.loc[(final_df['project'] == project_name) & (final_df['shortpath'] == sp) & (final_df['minor'] == row['minor']),'priority'] = final_row['priority'] + row['priority']*newbug #Multiply by newbug because we dont want to double the priority if the bug has 2 commits
                final_df.loc[(final_df['project'] == project_name) & (final_df['shortpath'] == sp) & (final_df['minor'] == row['minor']),'bfs'] = final_row['bfs'] + r['la'] + r['ld']
                final_df.loc[(final_df['project'] == project_name) & (final_df['shortpath'] == sp) & (final_df['minor'] == row['minor']),'num_bugs'] = final_row['num_bugs'] + newbug
                final_df.loc[(final_df['project'] == project_name) & (final_df['shortpath'] == sp) & (final_df['minor'] == row['minor']),'release_id'] = target_versions.index(int(row['minor']))                                  
                
                    
               
#    print("")
            
       

final_df.to_csv(dir+"/intermediate_files/final_dataset2.csv", index=False)






