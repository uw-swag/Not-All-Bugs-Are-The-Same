import os
import pandas as pd
import numpy as np
import re
import time
import datetime
import math


"""

This script parses thorugh all of the output from UNDERSTAND (by scitools), which contains
the LOC and CC data for each target file. The output is all_metrics.csv which 
contains all of the metric data that will be used as independent variables.
The output will then be passed to independent.py to create a dataframe containing
all independent variables.

"""


#Working directory
dir = os.getcwd()+"/.."
os.chdir(dir)

complete_metric_df = pd.DataFrame(columns=['project','version','major','minor','filename','filepath','loc','cc'])

metric_dfs = dict()
targets = pd.read_csv(dir+"/intermediate_files/target_releases.csv")
for i,r in targets.iterrows():

    p_name = r['project']+"-"+r['release']

    if r['project'] == "felix":
        p_name = r['project']+".scr-"+r['release']

    metric_dfs[p_name] = pd.read_csv(dir+"/cloned_repos/"+p_name+"/"+p_name+".csv")

files = [] 
counter = 0
for key,df in metric_dfs.items():
    print(key,"-",counter,"/",len(metric_dfs.keys()))
    
    counter += 1
    for i,r in df.iterrows():
        if r['Kind'] == 'File':
            file_type = r['Name'].split('.')[-1]
            file_path = r['Name'].replace('\\','/')
            
            if file_type == "java" or file_type == "py" or file_type == "cc" or file_type == "js" or file_type == "cpp":
                complete_metric_df = complete_metric_df.append({
                'project':key.split('-')[0],
                'version':key.split('-')[1].replace(".csv",""),
                'filename':file_path.split('/')[-1],
                'filepath': file_path,
                'major': key.split('-')[1].split('.')[0],
                'minor': key.split('-')[1].split('.')[1],
                'loc': r['CountLineCode'],
                'cc':r['SumCyclomatic']
                },ignore_index=True)


complete_metric_df.to_csv(dir+"/intermediate_files/cc_loc/all_metrics.csv", index = False)


    
    

