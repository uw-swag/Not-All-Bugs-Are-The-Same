import os
import pandas as pd
import numpy as np
import re


"""

This script links github commits with jira issues by matching
JIRA issue keys in git commit descriptions

INPUT:
    - /github_commits/github_commits.csv
    - /jira_issues/jira_issues.csv

OUTPUT:
    - /intermediate_files/links.csv

"""

#Working directory
dir = os.getcwd()+"/.."
os.chdir(dir)

#Paths to CSVs
commits = pd.read_csv(dir+"/intermediate_files/github_commits.csv")
issues = pd.read_csv(dir+"/intermediate_files/jira_issues.csv")

#Make new data frame to store results
link_df = pd.DataFrame(columns=['project','hash', 'committerTime', 'authorName', 'subject', 'Issue key', 'Fix Version/s', 'Component/s', 'Priority', 'Created', 'Resoved', 'c_message'])


projects = ["accumulo","bookkeeper","camel","cassandra","cxf","derby","felix","hive","openjpa","pig","wicket"]

for project in projects:
    print("")
    print(project)


    project_issues = issues.loc[issues['Project key'] == project.upper()]
    project_commits = commits.loc[commits['project'] == project]


    #Extract unique identifiers from ISSUES and search for them in comments of Git COMMITS
    counter = 0
    for index,row in project_issues.iterrows():
        print(counter,"/",project_issues.shape[0], end="\r")
        counter += 1

        issue_key = row['Issue key']
        project = row['Project key']

        for comm_index, comm_row in project_commits.iterrows():
            #Use regex to find issue key in commit message
            #Match with strings that start with any character, followed by the key, followed by anything except for a number
            regex = "(?=.*"+issue_key+"(?![0-9]))"
            if re.search(regex,comm_row['subject']):
                link_df = link_df.append({
                'project':project,
                'hash':comm_row['hash'],
                'committerTime':comm_row['committerTime'],
                'authorName':comm_row['authorName'],
                'subject':comm_row['subject'],
                'Issue key':row['Issue key'],
                'Fix Version/s':row['Fix Version/s'],
                'Component/s':row['Component/s'],
                'Priority':row['Priority'],
                'Created':row['Created'],
                'Resolved':row['Resolved'],
                'c_message':comm_row.subject
                },ignore_index=True)
                
                
    #Save after every project in case something fails           
    link_df.to_csv(dir+"/intermediate_files/links.csv",index=False)  

link_df.to_csv(dir+"/intermediate_files/links.csv",index=False)            
