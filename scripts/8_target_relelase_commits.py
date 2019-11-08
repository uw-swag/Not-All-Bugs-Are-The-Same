import os
import pandas as pd
import numpy as np
import time


""" 

This script filters down the github commits to only include commits within the 
target releases for each project. The output is target_commits.csv.

"""


#Guess release based on commit time
def get_release(version_data, committerTime, project):

    commit_date = pd.to_datetime(committerTime,unit='s')

    release = version_data.loc[(version_data['project'] == project.lower()) & (version_data['pre'] < commit_date) & (version_data['post'] > commit_date)]

    if release.shape[0] > 0:
        release = release.sort_values(by='major').iloc[0]
        if release['date'] > commit_date:
            return release['release'], 1
        else:
            return release['release'], 0
    
    return np.nan, np.nan
    
    
    

#Working directory
dir = os.getcwd()+"/.."
os.chdir(dir)

targets = pd.read_csv(dir+"/intermediate_files/target_releases.csv")
github_commits = pd.read_csv(dir+"/intermediate_files/github_commits.csv")

#Make sure all time columns are of the correct type
github_commits['committerTime'] = pd.to_numeric(github_commits['committerTime'], errors='coerce')
github_commits = github_commits[pd.notnull(github_commits['committerTime'])]
github_commits['committerTime'] = pd.to_datetime(github_commits['committerTime'], unit='s')

github_commits['authorTime'] = pd.to_numeric(github_commits['authorTime'], errors='coerce')
github_commits = github_commits[pd.notnull(github_commits['authorTime'])]

version_data = pd.read_csv(dir+"/intermediate_files/release_dates/version_data.csv")
version_data['pre'] = pd.to_datetime(version_data['pre'])
version_data['post'] = pd.to_datetime(version_data['post'])
version_data['date'] = pd.to_datetime(version_data['date'])


#Prepare new dataframe
target_commits_df = pd.DataFrame(columns=github_commits.columns.values)



total = github_commits.shape[0]
for i,r in github_commits.iterrows():
    percent_complete = int(100*(i/total))
    
    print("Locating target commits: "+str(percent_complete)+"%", end="\r")
    
    try:
        #Get release and pre/post
        release = np.nan

        committerTime = r['committerTime']
        project = r['project']
        release, pre = get_release(version_data, committerTime, project)
            
        #If release is found, determine major, minor, and churn
        if not pd.isnull(release):
            major = int(release.split('.')[0])
            minor = int(release.split(".")[1])
            
            #Find major/minor targets for this project
            project_targets = targets.loc[targets['project'] == project]
            t_major = int(project_targets.iloc[0]['major'])
            t_minors = project_targets['minor'].tolist()
            
            
            #Check if current row is a target
            if major == t_major and minor in t_minors:
                r['minor'] = minor
                r['major'] = major
                r['pre'] = pre
                r['post'] = 1-pre
                target_commits_df = target_commits_df.append(r, ignore_index = True)



    except Exception as e:
        print("Error with "+project+": "+e)
        print(e)
        pass

                   
        


target_commits_df.to_csv(dir+"/intermediate_files/target_commits.csv", index=False)


    
