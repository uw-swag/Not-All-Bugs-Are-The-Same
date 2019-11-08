import os
import pandas as pd
import numpy as np
import re



"""

This script combines all of the JIRA issue csvs into a singluar CSV called jira_issues.csv


"""




#Working directory
dir = os.getcwd()+"/.."
os.chdir(dir)

issue_csvs = os.listdir(dir+"/jira_issues")

target_columns = ['Summary', 'Issue key', 'Issue id', 'Issue Type',
	'Status', 'Project key','Project name', 'Project type',
	'Priority', 'Assignee' ,'Creator','Created', 'Updated' ,
	'Resolved', 'Affects Version/s', 'Fix Version/s', 'Component/s',
	'Time Spent',  'Security Level']

unified_df = None
first=True

for issue_csv in issue_csvs:
    
	df = pd.read_csv(dir+"/jira_issues/"+issue_csv)
    
	for col in target_columns:
		if col not in df.columns:
			df[col] = np.nan

	df = df[target_columns]

	if first:
		unified_df = df
		first = False
	else:
		unified_df = pd.concat([unified_df, df], axis=0)

#Drop duplicate issues before saving
unified_df = unified_df.drop_duplicates(subset='Issue key', keep='first')
unified_df.to_csv(dir+"/intermediate_files/jira_issues.csv",index=False)



#Code below was to make sure no rows' formatting got screwed up


#Drop rows where summary overflows into other columns after saving
#unified_df = pd.read_csv(dir+"/intermediate_files/jira_issues.csv")

#project_names = ["accumulo","bookkeeper","camel","cassandra","cxf","derby","felix","hive","openjpa","pig","wicket"]
#for i,r in unified_df.iterrows():
#	key = r['Issue key']
#	found = False
#	
#	for proj in project_names:
#		if proj.upper() in key:
#			found = True
#	
#	if not found:
#		print(i)
	




#unified_df = unified_df[pd.notnull(unified_df['Issue key'])]
#unified_df.to_csv(dir+"/intermediate_files/jira_issues.csv",index=False)
