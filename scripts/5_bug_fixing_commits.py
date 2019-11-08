import os
import pandas as pd
import numpy as np
import re
import time
import datetime
import math

"""

This script creates the bugfixingcommits.csv file for Issue #4.

Requirements: for each project, github commit CSVs, jira issue CSVs, and link CSVs that link commits to issues.

"""

def get_release(version_data, link_row):

    #First, check JIRA
    release = link_row['Fix Version/s']
    if isinstance(release, str):
        version_regex = re.compile("(\d+\.)+\d+")
        version_search = re.search(version_regex, release)
        if version_search:
            return version_search.group()

    #If not in JIRA, then guess based on release dates
    commit_date = pd.to_datetime(link_row['committerTime'],unit='s')
    project = link_row['project']

    release = version_data.loc[(version_data['project'] == project.lower()) & (version_data['pre'] < commit_date) & (version_data['post'] > commit_date)]

    if release.shape[0] == 1:
        return release['release'].iloc[0]
        
    elif release.shape[0] == 0:
        return 0
    #if releases overlap go with the highest major release
    else:
        release = release.sort_values(by='major')
        return release.tail(1)['release'].iloc[0]

def get_major_minor(release):
    try:
        release = release.split(".")
        major = int(release[0])
        minor = int(release[1])
        return major, minor

    except Exception as e:
        return np.nan, np.nan
    
def get_stat_row(numstats, link_row):
    project = link_row['project']
    hash = link_row['hash']
    statrow = numstats.loc[(numstats['project'] == project) & (numstats['hash'] == hash)]

    if statrow.shape[0] == 1:
        return statrow.iloc[0]
    else:
        return -1

def get_ld(project_dfs, csv, row):
    if row == -1:
        return 0
    return project_dfs["file_change_stats/file_changes_"+csv].at[row,'la'] + project_dfs["file_change_stats/file_changes_"+csv].at[row,'ld']


# Experience is measured by the number of previous commits by that author before the post-release period
def get_author_exp(df, link_row, version_data, major, minor):

    project = link_row['project']
    author = link_row['authorName']
        
    r_date = version_data.loc[(version_data['project'] == project.lower()) & (version_data['major'] == major) & (version_data['minor'] == minor)]
    
    if r_date.shape[0] == 0:
        return np.nan
        
    r_date = r_date.iloc[0]['date']

    num_commits = df.loc[(df['authorName'] == author) & (df['committerTime'] < r_date) & (df['project'] == project)].shape[0]

    return num_commits



#Working directory
dir = os.getcwd()+"/.."
os.chdir(dir)

priorities = {
    'Major':3,
    'Blocker':5,
    'Normal':3,
    'Critical':4,
    'Trivial':1,
    'Minor':2,
    'Low':1,
    'Urgent':5
}

#Create empty df
bugfixingcommits = pd.DataFrame(columns=['BFC_id','bug_id','project','release','priority','BFC_date','fixing_time','author','author_exp'])

#Paths to CSVs

links = pd.read_csv(dir+"/intermediate_files/links.csv")
version_data = pd.read_csv(dir+"/intermediate_files/release_dates/version_data.csv")

#Make sure all time columns are of the correct type
links['committerTime'] = pd.to_numeric(links['committerTime'], errors='coerce')
links = links[pd.notnull(links['committerTime'])]
links['committerTime'] = pd.to_datetime(links['committerTime'], unit='s')

links['Created'] = pd.to_datetime(links['Created'], unit='s')
links['Resolved'] = pd.to_datetime(links['Resolved'], unit='s')

version_data['pre'] = pd.to_datetime(version_data['pre'])
version_data['post'] = pd.to_datetime(version_data['post'])
version_data['date'] = pd.to_datetime(version_data['date'])


for link_index, link_row in links.iterrows():
    print(link_index,"/",links.shape[0], end="\r")

    project = link_row['project']
    release = get_release(version_data, link_row)
    major, minor = get_major_minor(release)
    

    bugfixingcommits = bugfixingcommits.append({
        'BFC_id':link_row['hash'],
        'bug_id':link_row['Issue key'],
        'project':project,
        'release':release,
        'major':major,
        'minor':minor,
        'component':link_row['Component/s'],
        'priority':priorities[link_row['Priority']],
        'BFC_date':link_row['committerTime'],
        'fixing_time':math.floor((link_row['Resolved']-link_row['Created'])/np.timedelta64(1,'m')),
        'author':link_row['authorName'],
        'author_exp':get_author_exp(links, link_row, version_data, major, minor)
        },ignore_index=True)


# Since it takes a long time to make, if the CSV file is busy when it's time to write
# I'll just write it to a different file name
try:  
    bugfixingcommits.to_csv(dir+"/intermediate_files/bugfixingcommits.csv", index=False)
except PermissionError:
    print("Failed to write to bugfixingcommits.csv, writing to bugfixingcommits_new.csv instead!")
    bugfixingcommits.to_csv(dir+"/intermediate_files/bugfixingcommits_new.csv", index=False)
    

