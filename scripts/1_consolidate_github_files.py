import os
import pandas as pd
import numpy as np
import re

"""

This scripts takes all of the CSVs in the github_commits directory and combines
them into one CSV called github_commits.csv in the intermediate_files directory.

"""

#Working directory
dir = os.getcwd()+"/../github_commits/"
os.chdir(dir)

project_names = ["accumulo","bookkeeper","camel","cassandra","cxf","derby","felix","hive","openjpa","pig","wicket"]

target_columns = ["project","hash","subject","authorName","authorTime","committerName","committerTime"]

unified_df = None
first=True


for project in project_names:
    print(project)
    df = pd.read_csv(dir+project+".csv")
    df = df.drop_duplicates(subset='subject', keep='first')
    
    df['project'] = project
    
   

    if first:
        unified_df = df
        first = False
    else:
        unified_df = pd.concat([unified_df, df], axis=0)
        
unified_df = unified_df[target_columns]
unified_df.to_csv(dir+"../intermediate_files/github_commits.csv",index=False)




