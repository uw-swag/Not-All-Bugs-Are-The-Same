import os
import pandas as pd
import numpy as np
import re
import time
import datetime
import math



"""

This script parses through all of the text output created by numstat.sh. 
The numstat output contains all of the lines added and deleted from every commit.
The output of this script is all_numstats.csv, which contains all of the churn data
that will be used to calculate the independent variable "churn" and the dependent variable
"bug fix size".

"""


#Working directory
dir = os.getcwd()+"/../intermediate_files/"
os.chdir(dir)

project_names = ["accumulo","bookkeeper","camel","cassandra","cxf","derby","felix","hive","openjpa","pig","wicket"]

commit_df = pd.read_csv(dir+"target_commits.csv")

#Create empty df
numstat_df = pd.DataFrame(columns=['project','hash','major','minor','pre','post','issue_key','filename','la', 'ld'])


hash = np.nan
issue_key = np.nan
new_issue_key = False

#Parse one project's numstats at a time...
print("Parsing numstat output...")
for project in project_names:
    with open(dir+"numstats/target_github_commits/"+project+".txt", encoding="utf-8") as f:

        #Get file length to monitor progress
        for i, l in enumerate(f):
            pass
        file_length = i
        line_counter = 0
        f.seek(0)

    
        #For each line of numstat search for file information
        for line in f:
        
            #Print % of file that has been parsed
            completion = int((line_counter/file_length)*100)
            line_counter += 1
            print(project+": "+str(completion)+"%", end="\r")

        
            #Regex for lines containing hash
            if re.search("commit [a-zA-z0-9]{30,50}",line) and " " not in line[7:].replace("\n",""):
                hash = line[7:].replace("\n","")
                gitrow = commit_df.loc[commit_df['hash'] == hash].iloc[0]
                major = gitrow['major']
                minor = gitrow['minor']
                pre = gitrow['pre']
                post = gitrow['post']
                new_issue_key = False
            
            else:
            
                #Regex for line containing issue key
                issue_key_search = re.search(project.upper()+"-[0-9]+", line)
                if issue_key_search:
                    issue_key = issue_key_search.group(0)
                    new_issue_key = True
  

                #Regex for lines added and deleted detects la <tab> ld <tab> filename
                elif re.search("[0-9]+\t[0-9]+\t([a-zA-Z]+\/)*[a-zA-Z]+.",line):
                
                    if not new_issue_key:
                        issue_key = np.nan
                   
                    line = line.split("\t")
                    line[2] = line[2].replace('\n','')
                    filepath = line[2]
                    filename = filepath.split('/')[-1]
                    la = int(line[0])
                    ld = int(line[1])

                    numstat_df = numstat_df.append({
                        'project': project,
                        'hash':hash,
                        'major':major,
                        'minor':minor,
                        'pre':pre,
                        'post':post,
                        'filename':filename,
                        'filepath':filepath,
                        'issue_key':issue_key,
                        'la':la,
                        'ld':ld
                    },ignore_index=True)

    numstat_df.to_csv(dir+"numstats/all_numstats/all_"+project+"_numstats.csv", index=False)   
                    
    print("")            

numstat_df.to_csv(dir+"numstats/all_numstats.csv", index=False)

                    


