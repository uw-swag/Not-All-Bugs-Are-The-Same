import os
import pandas as pd
import numpy as np
import re



"""

This script filters down the bug fixing commits to only include the target versions.

***
This file should really be updated to work from target_release_commits.py because 
its currently pretty redudant. It should just be able to output the intersection
between target_commits.csv and bugfixingcommits.csv.
***


"""



def get_target_versions():
    target_versions = dict()
    targets = pd.read_csv(dir+"intermediate_files/target_releases.csv")
    for i,r in targets.iterrows():

        project = r['project']
        major = r['major']
        minor = r['minor']

        if project in target_versions:
            target_versions[project]["minor"].append(minor)
        else:
            target_versions[project] = {"major":major, "minor":[minor]}

    return target_versions


#Working directory
dir = os.getcwd()+"/../"
os.chdir(dir)

projects = ["accumulo","bookkeeper","camel","cassandra","cxf","derby","felix","hive","openjpa","pig","wicket"]

target_versions = get_target_versions()
for p in target_versions:
    print(p)
    for v in target_versions[p]:
        print(target_versions[p][v])
        

bfcs = pd.read_csv(dir+"intermediate_files/bugfixingcommits.csv")
targets = []

for project in projects:

    if project == 'felix':
        target = bfcs.loc[(bfcs['project'] == project.upper()) &
         (bfcs['major'] == target_versions[project]['major']) &
          (bfcs['minor'] >= target_versions[project]['minor'][0]) &
           (bfcs['minor'] <= target_versions[project]['minor'][2]) &
            (bfcs['component'] == "Declarative Services (SCR)")]
    else:
        target = bfcs.loc[(bfcs['project'] == project.upper()) &
         (bfcs['major'] == target_versions[project]['major']) & 
          (bfcs['minor'].isin(target_versions[project]['minor']))]

    print(target.shape)

    targets.append(target)


target_bfcs = pd.concat(targets, axis=0)
target_bfcs.to_csv(dir+"intermediate_files/target_bfcs.csv",index=False)








