import os
import pandas as pd
import numpy as np
import re
import time
import datetime


"""
This script parses through version data extracted from GitHub to assemble dates of each release for each project

Requirement: <project>_versions.txt files for each project. These files must contain text extracted from each project's GitHub release page. (Ex. https://github.com/apache/derby/releases)

Output: A CSV called version_data.csv

NOTE: Felix is not included in this script because it has different version for every component. In the end I 
got felix versions manually by counting the number of commits for each component, then
counting the number of commits for each version of the top 2 components
(declarative services (scr) and Framework), then I went online and found the 
dates for the most popular versions of the most popular component (SCR 1.4, 1.6, 1.8)

"""


def first_major_minor(split):
    #Do no count if version is a patch or bug fix (ie 2.3.x.x --> x's must be zeros)
    if len(split) > 2:
        for i in range(2,len(split)):
            if split[i] != '0':
                return False
    return True
    

#Working directory
dir = "C:/Users/Kilby/Code/Waterloo/NotAllBugsAreTheSame_Gema/intermediate_files/release_dates/"
os.chdir(dir)


#Store project names
project_names = ["accumulo","bookkeeper","camel","cassandra","cxf","derby","hive","openjpa","pig","wicket"]

version_data = pd.DataFrame(columns=['project','release', 'major','minor','date','pre','post','component'])

version_regex = re.compile("(\d+\.)+\d+")
date_regex = re.compile(r", 20")

date = ""
version = ""

for project in project_names:
    print(project)

    with open("github_text/"+project+"_versions.txt") as f:

        lines = f.readlines() # list containing lines of file

        for line in lines:

            #If the line is a date, extract the datetime
            if re.match("on ", line):
                date = line[3:].strip()
                if not re.search(date_regex, date):
                    date += ", 2019"
                date = pd.to_datetime(date)

            #If line has a version number in it, add version and date to dataframe
            version_search = re.search(version_regex, line)
            if version_search:
                version = version_search.group().split(".")
                major = int(version[0])
                minor = int(version[1])
                #Do no count if version is a patch or bug fix (ex 2.3.x.x --> x's must be zeros)


                if first_major_minor(version) or project == "derby":
                    if not ((version_data['project'] == project) & (version_data['major'] == major) & (version_data['minor'] == minor)).any():
                        version_data = version_data.append({'project':project, 'release': version_search.group(), 'major':major, 'minor':minor, 'date':date},ignore_index=True)


version_data = version_data.sort_values(by=['project','component', 'major','minor',]).reset_index(drop=True)
for index,row in version_data.iterrows():
    project = row['project']
    component = row['component']
    major = row['major']
    minor = row['minor']
    date = row['date']
    lower_date = None
    higher_date = None

    #GET PREVIOUS RELEASE DATE
    #All project rows of same major rel with smaller minor rel, sorted
    lower_rows = version_data.loc[(version_data['project'] == project) & (version_data['minor'] < minor) & (version_data['major'] == major)].sort_values(by="minor")

    #If no releases with same major have a smaller minor, find next lowest major
    if lower_rows.shape[0] == 0:
        lower_majors = version_data.loc[(version_data['project'] == project) & (version_data['major'] < major)].sort_values(by=["major","minor"])

        if lower_majors.shape[0] != 0:
            lower_date = lower_majors.tail(1)['date']
    
    else:
        lower_date = lower_rows.tail(1)['date']
    
    #GET NEXT RELEASE DATE
    #All project rows of same major rel with larger minor rel, sorted
    higher_rows = version_data.loc[(version_data['project'] == project) & (version_data['minor'] > minor) & (version_data['major'] == major)].sort_values(by="minor")

    #If no releases with same major have a larger minor, find next highest major
    if higher_rows.shape[0] == 0:
        higher_majors = version_data.loc[(version_data['project'] == project) & (version_data['major'] > major)].sort_values(by=["major","minor"])

        if higher_majors.shape[0] != 0:
            higher_date = higher_majors.head(1)['date']
    
    else:
        higher_date = higher_rows.head(1)['date']



    if isinstance(lower_date, pd.core.series.Series):
        lower_midpoint = (date - (date-lower_date)/2).iloc[0] 
    else:
        #An arbitrary date that will be before the earliest release
        lower_midpoint = np.datetime64('1978-01-01')

    if isinstance(higher_date, pd.core.series.Series):
        higher_midpoint = (date + (higher_date-date)/2).iloc[0] 
    else:
        higher_midpoint = pd.to_datetime('today')

    version_data.at[index,'pre'] = lower_midpoint  
    version_data.at[index,'post'] = higher_midpoint



print("DONE")
        


version_data.to_csv("version_data.csv", index=False)
