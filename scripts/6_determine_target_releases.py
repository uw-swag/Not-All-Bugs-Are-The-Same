import os
import pandas as pd
import numpy as np
import re
import time
import datetime
import math



"""

This script locates the 3 consecutive minor releases of each project
with the most post release bug fixing commits.

"""



def count_pre_post():
    version_data = pd.read_csv(dir+"/intermediate_files/release_dates/version_data.csv")
    version_data['date'] = pd.to_datetime(version_data['date'])
    bfcs = pd.read_csv(dir+"/intermediate_files/bugfixingcommits.csv")
    
    
    
    #Make sure all time columns are of the correct type
    #bfcs['committerTime'] = pd.to_numeric(bfcs['BFC_date'], errors='coerce')
    #bfcs = bfcs[pd.notnull(bfcs['BFC_date'])]
    #bfcs['committerTime'] = pd.to_datetime(bfcs['BFC_date'], unit='s')
    bfcs['BFC_date'] = pd.to_datetime(bfcs['BFC_date'])



    count = {}

    for bfc_index, bfc_row in bfcs.iterrows():

        if not np.isnan(bfc_row['major']):

            proj = bfc_row['project'].lower()
            major = int(bfc_row['major'])
            minor = int(bfc_row['minor'])
            rel = str(major)+"."+str(minor)
            commit_date = pd.to_datetime(bfc_row['BFC_date'],unit='s')

            vd_row = version_data.loc[(version_data['project'] == proj) & (version_data['major'] == major) & (version_data['minor'] == minor)]
            if vd_row.shape[0] > 0:
                rel_date = vd_row['date'].iloc[0]

                pre = 0
                if rel_date > commit_date:
                    pre = 1
                post = 1-pre
                
                if proj in count:
                    if rel in count[proj]:
                        count[proj][rel]["pre"] += pre
                        count[proj][rel]["post"] += post
                    else:
                        count[proj][rel] = {"pre":pre, "post":post}
                else:
                    count[proj] = {rel:{"pre":pre, "post":post}}



    #Create empty df and fill it
    df = pd.DataFrame(columns=['project','release','major','minor','pre','post'])
    for k1 in count:
        for k2 in count[k1]:
            df = df.append({
                'project': k1,
                'release': k2,
                'major': k2.split(".")[0],
                'minor' : k2.split(".")[1],
                'pre': count[k1][k2]["pre"],
                'post': count[k1][k2]["post"]
            },ignore_index=True)
    return df
    
    
 
#Working directory
dir = os.getcwd()+"/.."
os.chdir(dir)   
    

#new df to fill with target releases
targets = pd.DataFrame(columns=['project','release','major','minor', 'pre', 'post'])

#count the number of commits for each release
df = count_pre_post()
print(sum(df['post'].tolist()))
df['minor'] = df['minor'].astype(int)
df['major'] = df['major'].astype(int)

#Import version data to find exact release numbers
version_data = pd.read_csv(dir+"/intermediate_files/release_dates/version_data.csv")

#Find the 3 consecutive releases in each project with the most pre-release bfcs
projects = ["accumulo","bookkeeper","camel","cassandra","cxf","derby","hive","openjpa","pig","wicket"]
for project in projects:
    
    #target will hold the major/minor of the first target release
    target = None
    most_post_commits = 0

    #Get a df of the commit counts for the current project
    p_df = df.loc[df['project'] == project]
    
    #Loop through a list of all major versions
    major_versions = set(p_df['major'].tolist())
    for maj in major_versions:
    
        #Loop through a list of all minor versions in the current major version
        pv_df = p_df.loc[p_df['major'] == maj]
        minor_versions = set(pv_df['minor'].tolist())
        for minor in minor_versions:
        
            #If there exist 3 consecutive minor releases starting from the current minor release,
            #and the sum of post-release bfcs is the most so far, save the major/minor
            if minor+1 in minor_versions and minor+2 in minor_versions:
                c1 = pv_df.loc[pv_df['minor'] == minor].iloc[0]['post']
                c2 = pv_df.loc[pv_df['minor'] == minor+1].iloc[0]['post']
                c3 = pv_df.loc[pv_df['minor'] == minor+2].iloc[0]['post']
                
                if most_post_commits < c1+c2+c3:
                    most_post_commits = c1+c2+c3
                    target = {'major':maj,'minor':minor}
    
    #Add the 3 target releases to the target dataframe
    for x in range(3):
        if target == None:
            print(project,"targets not found!")
        else:
            p_row = p_df.loc[(p_df['major'] == target['major']) & (p_df['minor'] == target['minor']+x)].iloc[0]
            v = version_data.loc[(version_data['major'] == target['major']) & (version_data["minor"] == target['minor']+x)].iloc[0]['release']                     
            targets = targets.append({'project':project,'release':v,'major':target['major'],'minor':target['minor']+x, 'pre':p_row['pre'], 'post':p_row['post']},ignore_index=True)

targets.to_csv(dir+"/intermediate_files/target_releases.csv", index=False)












