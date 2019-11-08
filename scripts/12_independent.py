import os
import pandas as pd
import numpy as np
import re
#import time
import datetime
import math
from datetime import time

"""

This script creates a dataframe that contains a row for every target file
that will be in the final dataset. All of the independent variables are 
calculated and added to the dataframe. The output is independent.csv, which will
be passed to dependent.py to add the dependent variables to create the final dataset.

"""


def file_type(path):
    return path.split('.')[-1]
    
def contains_test(path):
    if "/test/" in path:
        return 0
    return 1

def contains_src(path):

    if "derby" in path:
        return 1

    if "src/" in path:
        return 1
    return 0


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

metrics = metric_df = pd.read_csv(dir+"/intermediate_files/cc_loc/all_metrics.csv")
targets = pd.read_csv(dir+"/intermediate_files/target_releases.csv")
numstats = pd.read_csv(dir+"/intermediate_files/numstats/all_numstats.csv")     #CHANGED THIS TO ALL_NUMSTATS INSTEAD OF TARGET_NUMSTATS TO SEE THE DIFFERENCE


#Filter like Harold:
##################################

#Filter out non-java files
metrics['filetype'] = metrics['filename'].apply(file_type)
metrics = metrics.loc[metrics['filetype'] == 'java']

#Filter out test files
metrics['test_file'] = metrics['filepath'].apply(contains_test)
metrics = metrics.loc[metrics['test_file'] == 1]

#Filter out non-src files:
metrics['src_file'] = metrics['filepath'].apply(contains_src)
metrics = metrics.loc[metrics['src_file'] == 1]



####################################

#I add the combined churn stats to a dict and then converting the dict to a dataframe at the end
independent_df = pd.DataFrame(columns=['project','major','minor','release','filename','filepath','shortpath','churn', 'la', 'ld', 'CC', 'LOC', 'num_pre'])
cn_dict = {}

version_data = pd.read_csv(dir+"/intermediate_files/release_dates/version_data.csv")
version_data['pre'] = pd.to_datetime(version_data['pre'])
version_data['post'] = pd.to_datetime(version_data['post'])
version_data['date'] = pd.to_datetime(version_data['date'])


project_names = ["accumulo","bookkeeper","camel","cassandra","cxf","derby","felix","hive","openjpa","pig","wicket"]


metrics = metrics.reset_index()
#Iterate through all metric files from UNDERSTAND
total = metrics.shape[0]
for i,r in metrics.iterrows():
    percent_complete = int(100*(i/total))
    print("Generating independent variables: "+str(percent_complete)+"%", end="\r")
    


    #Initialize independent variables
    la = 0
    ld = 0
    num_pre = 0

    #Find rows for the same file and release in NUMSTATS
    metrics_sp = short_path(r['filepath'])
    
    #Start by finding numstat rows with the same filename
    name_matches = numstats.loc[(numstats['filename'] == r['filename']) & (numstats['project'] == r['project']) & (numstats['pre'] == 1) & (numstats['minor'] == r['minor'])]

    #Then make sure it's the same file by comparing short paths
    for name_i, name_r in name_matches.iterrows():
        numstats_sp = short_path(name_r['filepath'])
        if numstats_sp == metrics_sp:
            la += int(name_r['la'])
            ld += int(name_r['ld'])
            num_pre += 1

    # Update the independent variable dataframe
    independent_df = independent_df.append({
        'project':r['project'],
        'major': r['major'],
        'minor': r['minor'],
        'release':r['version'],
        'filename': r['filename'],
        'filepath':r['filepath'],
        'shortpath':short_path(r['filepath']),
        'churn': la+ld,
        'la': la,
        'ld': ld,
        'CC':r['cc'],
        'LOC':r['loc'],
        'num_pre':num_pre,
        'num_post':0,
        'exp':0,
        'priority':0,
        'bfs':0,
        'num_bugs':0,
        'release_id':0
    },ignore_index=True)

        

independent_df.to_csv(dir+"/intermediate_files/independent.csv", index=False)

    
