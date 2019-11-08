import os
import pandas as pd
import numpy as np
import re
import time
import datetime
import math



"""

This script is used to make the tables for the paper. It outputs text files 
that contain latex code that can be pasted into overleaf.

"""




projects = ["accumulo","bookkeeper","camel","cassandra","cxf","derby","felix","hive","openjpa","pig","wicket"]

#Working directory
dir = os.getcwd()+"/../../"
os.chdir(dir)


#NOTE: table 9 data is computed by running t9_correlation_analysis.r which outputs the crrelation data to t9.csv
def table_9():
    #Accumulo	&	0.27	&	0.77	&	0.51	&   	-0.01	&	0.06	&	0.19    &   	-0.01	&	0.06	&	0.19	 	\\	\hline

	df = pd.read_csv(dir+"intermediate_files/t9.csv")

	#Create tex file for table 9
	table9_tex = ""

	with open("scripts/Analysis/blank_tables/table9.txt", "r") as f:
		for line in f.readlines():

			if "insert_data" not in line:
				table9_tex += line

			else:
				for i,r in df.iterrows():
					if r['V1'] in projects:
					
						if r['V1'] == 'hive':
							r['V4'] = r['V3']
							r['V7'] = r['V6']
							r['V10'] = r['V9']
							
							r['V3'] = 0 
							r['V6'] = 0 
							r['V9'] = 0 
					
					
						new_line = r['V1'].capitalize()

						for i in range(2,11):
							new_line += "\t&\t"+str(round(float(r['V'+str(i)]),2))
						new_line += "\t\\\\ \\hline\n"

						table9_tex += new_line


	f = open('Figures&Tables/tables_latex/table9.tex','w')
	f.write(table9_tex)
	f.close()	

	
	
	print("Updated file:    Figures&Tables/tables_latex/table9.tex")


def table_8():
	
	df = pd.read_csv(dir+"intermediate_files/final_dataset.csv")
	
	
	#Create dataframe with all required information
	t8 = pd.DataFrame(columns=['project','minor','independent', 'rank'])
	for p in projects:
		p_df = df.loc[df['project']==p]
		releases = set(p_df['minor'])
		
		
		
		#Temporary code to find bfs totals for paper
		temp_n = [0,0]
		temp_b = [0,0]
		
		
		for r in releases:
			r_df = p_df.loc[p_df['minor'] == r]
			
			rank_numbugs = r_df.sort_values(by=['num_bugs'],ascending=False).head(20)['shortpath'].tolist()
			rank_bfs = r_df.sort_values(by=['bfs'],ascending=False).head(20)['shortpath'].tolist()
			rank_exp = r_df.sort_values(by=['exp'],ascending=False).head(20)['shortpath'].tolist()
			
			#Temporary code to find bfs totals for paper
			
			temp_numbugs = r_df.sort_values(by=['num_bugs'],ascending=False)['bfs'].head(20).tolist()
			temp_n[0] += sum(temp_numbugs)
			temp_n[1] += 1
			
			temp_bfs = r_df.sort_values(by=['bfs'],ascending=False)['bfs'].head(20).tolist()
			temp_b[0] += sum(temp_bfs)
			temp_b[1] += 1
			
			
#			#Temporary code to find example for paper
#			for x in range(10):
#				if rank_exp[x] not in rank_numbugs:
#					
#					row = r_df.loc[r_df['shortpath']==rank_exp[x]].iloc[0]
#					if row['priority']/row['num_bugs'] > 3:
#						print("rank:",x)
#						print(row)
#						print("\n-------------------------\n")
			
			
			bfs_inter = 20-len(set(rank_numbugs) & set(rank_bfs))
			exp_inter = 20-len(set(rank_numbugs) & set(rank_exp))
			
			t8 = t8.append({'project':p, 'minor':r,'independent':'bfs','rank':bfs_inter},ignore_index=True)
			t8 = t8.append({'project':p, 'minor':r,'independent':'exp','rank':exp_inter},ignore_index=True)
			
	print(temp_n[0]/temp_n[1])
	print(temp_b[0]/temp_b[1])		
			
	#Create tex file for table 8
	table8_tex = ""
	with open("scripts/Analysis/blank_tables/table8.txt", "r") as f:
			for line in f.readlines():
				if "insert_data" not in line:
					table8_tex += line

				else:
					for p in projects:
						minors = sorted(set(t8.loc[t8['project']==p]['minor']))
						
						#Hive doesnt have any files in R2 so I put in "nan" instead
						if p == 'hive':
							bfs_r1 = t8.loc[(t8['project']==p) & (t8['independent'] == 'bfs') & (t8['minor']==minors[0])].iloc[0]['rank']
							bfs_r2 = "nan"
							bfs_r3 = t8.loc[(t8['project']==p) & (t8['independent'] == 'bfs') & (t8['minor']==minors[1])].iloc[0]['rank']
							exp_r1 = t8.loc[(t8['project']==p) & (t8['independent'] == 'exp') & (t8['minor']==minors[0])].iloc[0]['rank']
							exp_r2 = "nan"
							exp_r3 = t8.loc[(t8['project']==p) & (t8['independent'] == 'exp') & (t8['minor']==minors[1])].iloc[0]['rank']	
							
						else:
							bfs_r1 = t8.loc[(t8['project']==p) & (t8['independent'] == 'bfs') & (t8['minor']==minors[0])].iloc[0]['rank']
							bfs_r2 = t8.loc[(t8['project']==p) & (t8['independent'] == 'bfs') & (t8['minor']==minors[1])].iloc[0]['rank']
							bfs_r3 = t8.loc[(t8['project']==p) & (t8['independent'] == 'bfs') & (t8['minor']==minors[2])].iloc[0]['rank']
							exp_r1 = t8.loc[(t8['project']==p) & (t8['independent'] == 'exp') & (t8['minor']==minors[0])].iloc[0]['rank']
							exp_r2 = t8.loc[(t8['project']==p) & (t8['independent'] == 'exp') & (t8['minor']==minors[1])].iloc[0]['rank']
							exp_r3 = t8.loc[(t8['project']==p) & (t8['independent'] == 'exp') & (t8['minor']==minors[2])].iloc[0]['rank']		
							
						table8_tex += p.capitalize()+"\t&\t"+str(bfs_r1)+"\t&\t"+str(bfs_r2)+"\t&\t"+str(bfs_r3)+"\t&\t"+str(exp_r1)+"\t&\t"+str(exp_r2)+"\t&\t"+str(exp_r3)+"\t\\\\\\hline\n"					





	f = open('Figures&Tables/tables_latex/table8.tex','w')
	f.write(table8_tex)
	f.close()	



	print("Updated file:    Figures&Tables/tables_latex/table8.tex")



def table_7():


	df = pd.read_csv(dir+"intermediate_files/final_dataset.csv")
	df = df.loc[(df['project']=='accumulo') & (df['minor']==6)] 
	
	
	rank_numbugs = df.sort_values(by=['num_bugs'],ascending=False).head(5).reset_index()
	rank_exp = df.sort_values(by=['exp'],ascending=False).head(5).reset_index()
	
	similar_files = set(rank_numbugs['shortpath'].tolist()) & set(rank_exp['shortpath'].tolist())
	
	alphabet = ['A','B','C','D','E','F','G','H','I','J']
	latex_colors = ['airforceblue!50','carmine!30','applegreen','arylideyellow','brightube']
	latex_colors = ['red', 'green', 'cyan', 'magenta', 'yellow']
	
	#Set letters for numbug files
	for i in range(5):
		rank_numbugs.at[i,'letter'] = alphabet[i]
		rank_numbugs.at[i,'color'] = latex_colors[i]
	
	#Set letters for exp files, where letters match for same file in numbugs
	for i in range(5):
		
		#If there's a file match, get the letter from the macthing row in numbugs
		if rank_exp.at[i,'shortpath'] in similar_files:
			rank_exp.at[i,'letter'] = rank_numbugs.loc[rank_numbugs['shortpath']==rank_exp.at[i,'shortpath']].iloc[0]['letter']
			rank_exp.at[i,'color'] = rank_numbugs.loc[rank_numbugs['shortpath']==rank_exp.at[i,'shortpath']].iloc[0]['color']
	
		else:
			rank_exp.at[i,'letter'] = alphabet[5+i]
			

	
	#$f_{E}$	&	5	&	$f_{D}$	&	 200 \\
	
	
	
	#Read in a latex table and fill in the new statistics
	table7_tex = ""

	with open("scripts/Analysis/blank_tables/table7.txt", "r") as f:
		for line in f.readlines():
			if "insert_data" not in line:
				table7_tex += line
				
			else:

				for i in range(5):
				
					if rank_numbugs.at[i,'shortpath'] in similar_files:
						new_line = "\\cellcolor{"+rank_numbugs.at[i,'color']+"}$f_{"+rank_numbugs.at[i,'letter']+"}$\t&\t"+"\\cellcolor{"+rank_numbugs.at[i,'color']+"}"+str(int(rank_numbugs.at[i,'num_bugs']))+"\t&\t"
					else:
						new_line = "$f_{"+rank_numbugs.at[i,'letter']+"}$\t&\t"+str(int(rank_numbugs.at[i,'num_bugs']))+"\t&\t"
						
					if rank_exp.at[i,'shortpath'] in similar_files:
						new_line += "\\cellcolor{"+rank_exp.at[i,'color']+"}$f_{"+rank_exp.at[i,'letter']+"}$\t&\t"+"\\cellcolor{"+rank_exp.at[i,'color']+"}"+str(int(rank_exp.at[i,'exp']))+"\t\\\\\n"
					else:
						new_line += "$f_{"+rank_exp.at[i,'letter']+"}$\t&\t"+str(int(rank_exp.at[i,'exp']))+"\t\\\\\n"


					table7_tex += new_line
				table7_tex += "\\hline"	
					
					

			   
	f = open('Figures&Tables/tables_latex/table7.tex','w')
	f.write(table7_tex)
	f.close()	
	
	
	print("Updated file:    Figures&Tables/tables_latex/table7.tex")
	



def table_6():

	df = pd.read_csv(dir+"intermediate_files/t6_results.csv")

	#Read in a latex table and fill in the new statistics
	table6_tex = ""

	with open("scripts/Analysis/blank_tables/table6.txt", "r") as f:
		for line in f.readlines():
			if "insert_data" not in line:
				table6_tex += line

			else:
				for i,r in df.iterrows():
					if r['V1'] in projects:

						v3 = str(round(float(r['V3'])*100,1))
						v4 = str(round(float(r['V4'])*100,1))
						v5 = str(round(float(r['V5'])*100,1))
						v6 = str(round(float(r['V6'])*100,1))
						
						new_line = ""
						
						if r['V2'] == "X LOC":
							new_line += r['V1'].capitalize()

						new_line += "\t&\t"+r['V2']+"\t"
						new_line += "&\t"+v3+"\\%\t"
						new_line += "&\t"+v4+"\\%\t"
						new_line += "&\t"+v5+"\\%\t"
						new_line += "&\t"+v6+"\\%\t\\\\"
						
						if r['V2'] == "X churn":
							new_line += "\\hline"
						
						table6_tex += new_line+"\n"



	f = open('Figures&Tables/tables_latex/table6.tex','w')
	f.write(table6_tex)
	f.close()	

	print("Updated file:    Figures&Tables/tables_latex/table6.tex")



def table_5():
    
    df = pd.read_csv(dir+"intermediate_files/r2_results.csv")
    
    #Read in a latex table and fill in the new statistics
    table5_tex = ""

    with open("scripts/Analysis/blank_tables/table5.txt", "r") as f:
        for line in f.readlines():
            if "insert_data" not in line:
                table5_tex += line
                
            else:

                for i,r in df.iterrows():
                    
                    if r['V1'] in projects:
                    
                        v2 = str(round(float(r['V2'])*100))
                        v3 = str(round(float(r['V3'])*100))
                        v4 = str(round(float(r['V4'])*100))
                        v5 = str(round(float(r['V5'])*100))
                    
                        new_line = r['V1'].capitalize()+"\t"
                        new_line += "& & "+v2+"\\%\t"
                        new_line += "& & "+v3+"\\%\t["+str(round(float(r['V3'])/float(r['V2']),2))+"X]\t"
                        new_line += "&\t"+v4+"\\%\t["+str(round(float(r['V4'])/float(r['V2']),2))+"X]\t"
                        new_line += "&\t"+v5+"\\%\t["+str(round(float(r['V5'])/float(r['V2']),2))+"X]\t \\\\"
                        table5_tex += new_line+"\n"

                table5_tex += "\\hline"
                    
					

			       
    f = open('Figures&Tables/tables_latex/table5.tex','w')
    f.write(table5_tex)
    f.close()	
    
    print("Updated file:    Figures&Tables/tables_latex/table5.tex")



#This function is used to construct tables 3 and 4
#Since those tables require bug-level metrics, this function calculates the
#bfs, exp, and cost for each BFC, and returns them in lists
def get_bfs_exp_cost_lists(p_bfcs, p_numstats):
	
	bfs_list = []
	mean_exp_list = []
	cost_list = []
	

	for i,r in p_bfcs.iterrows():
		mean_exp=r['author_exp']
		
		bfs = 0
		bug_numstats = p_numstats.loc[p_numstats['hash'] == r['BFC_id']]
		for ni,nr in bug_numstats.iterrows():
			bfs += nr['la'] + nr['ld']
		cost = bfs*mean_exp
		
		
		bfs_list.append(bfs)
		mean_exp_list.append(mean_exp)
		cost_list.append(cost)
	return bfs_list, mean_exp_list, cost_list




#This function creates table 4 which contains RSDs
#Calculations are done at bug level not file level
def table_4():
    bfcs = pd.read_csv(dir+"intermediate_files/target_bfcs.csv")
    numstats = pd.read_csv(dir+"intermediate_files/numstats/all_numstats.csv")



    #Read in a latex table and fill in the new statistics
    table4_tex = ""

    with open("scripts/Analysis/blank_tables/table4.txt", "r") as f:
        for line in f.readlines():
            if "insert_data" not in line:
                table4_tex += line
            else:
                for project in projects:
                    p_bfcs = bfcs.loc[bfcs['project'] == project.upper()]
                    p_numstats = numstats.loc[numstats['project'] == project]

                    bfs_list, mean_exp_list, cost_list = get_bfs_exp_cost_lists(p_bfcs, p_numstats)

                    bfs_s = np.std(bfs_list)
                    exp_s = np.std(mean_exp_list)
                    cost_s = np.std(cost_list)
                    

                    bfs_rsd = round((100*bfs_s)/np.mean(bfs_list))
                    exp_rsd = round((100*exp_s)/np.mean(mean_exp_list))
                    cost_rsd = round((100*cost_s)/np.mean(cost_list))


                    new_line = project.capitalize()+"\t& &\t"
                    new_line += str(bfs_rsd)+"\\%\t& & &\t"
                    new_line += str(exp_rsd)+"\\%\t& & &\t"
                    new_line += str(cost_rsd)+"\\%\t& \\\\\n"
                    table4_tex += new_line
                    
                    
                table4_tex += "\\hline"
                    
					
    f = open('Figures&Tables/tables_latex/table4.tex','w')
    f.write(table4_tex)
    f.close()
    
    print("Updated file:    Figures&Tables/tables_latex/table4.tex")




#This function creates table 3 which contains Interquartile Ranges.
#Calculations are done at the bug level, not the file level.
def table_3():

	# Function to calculate IQR 
	def IQR(a, n):
		a.sort() 
		# Index of median of entire data 
		mid_index = median(a, 0, n) 
		# Median of first half 
		Q1 = a[median(a, 0, mid_index)] 
		# Median of second half 
		Q3 = a[median(a, mid_index + 1, n)] 
		# IQR calculation 

		return (Q3 - Q1)

	# Function to give index of the median 
	def median(a, l, r): 
		n = r - l + 1
		n = (n + 1) // 2 - 1
		return n + l 

	bfcs = pd.read_csv(dir+"intermediate_files/target_bfcs.csv")
	numstats = pd.read_csv(dir+"intermediate_files/numstats/all_numstats.csv")
	
	table3_tex = open("scripts/Analysis/blank_tables/table3.txt", "r").read()

	#print(final.columns.values)
	for project in projects:
	
		p_bfcs = bfcs.loc[bfcs['project'] == project.upper()]
		p_numstats = numstats.loc[numstats['project'] == project]
		
		bfs_list, mean_exp_list, cost_list = get_bfs_exp_cost_lists(p_bfcs, p_numstats)

		bfs_iqr = IQR(bfs_list,len(bfs_list))
		exp_iqr = IQR(mean_exp_list,len(mean_exp_list))
		cost_iqr = IQR(cost_list,len(cost_list))
		
		table3_tex = table3_tex.replace("bfs-"+project,str(bfs_iqr))
		table3_tex = table3_tex.replace("exp-"+project,str(exp_iqr))
		table3_tex = table3_tex.replace("cost-"+project,str(cost_iqr))

		
		
		
	f = open('Figures&Tables/tables_latex/table3.tex','w')
	f.write(table3_tex)
	f.close()	
	
	
	
	print("Updated file:    Figures&Tables/tables_latex/table3.tex")









#This function creates a dataframe to store the table information and then uses table2.txt
#to create the beginning of the table. The middle lines of latex are created without table2.txt.
#This is slightly different than table1 for no particular reason that I can remember.
def table_2():

	final = pd.read_csv(dir+"intermediate_files/final_dataset.csv")
	t_commits = pd.read_csv(dir+"intermediate_files/target_commits.csv")
	t_releases = pd.read_csv(dir+"intermediate_files/target_releases.csv")
	
	
	t2 = pd.DataFrame(columns=['project','release','pre','post','files','buggy_files'])
	
	
	#Start by making the table as a dataframe
	for p in projects:
		p_final = final.loc[(final['project'] == p)]
		minors = set(t_releases.loc[t_releases['project'] == p]['minor'])
		major = t_releases.loc[t_releases['project'] == p].iloc[0]['major']
		for minor in minors:
		    t2 = t2.append({
                'project':p,
                'release':str(major)+"."+str(minor)+".0",
                'pre':t_commits.loc[(t_commits['project'] == p) & (t_commits['minor'] == minor) & (t_commits['pre'] == 1)].shape[0],
                'post':t_commits.loc[(t_commits['project'] == p) & (t_commits['minor'] == minor) & (t_commits['post'] == 1)].shape[0],
                'files':p_final.loc[p_final['minor'] == minor]['filepath'].shape[0],
                'buggy_files':p_final.loc[(p_final['minor'] == minor)&(p_final['num_bugs']>0)].shape[0]
            },ignore_index=True)
		   
	
	#Read in a latex table and fill in the new statistics
	table2_tex = ""
	
	with open("scripts/Analysis/blank_tables/table2.txt", "r") as f:
		for line in f.readlines():
			if "insert_data" not in line:
				table2_tex += line
			else:
				counter = 1
				for i,r in t2.iterrows():
					new_line = ""
					if counter == 2:
						new_line += r['project'].capitalize()+"\t\t&"
					else:
						new_line += "\t\t&"

					new_line += str(r['release'])+"\t&\t"
					new_line += str(r['pre'])+"\t&\t"
					new_line += str(r['post'])+"\t&\t"
					new_line += str(r['files'])+"\t&\t"
					new_line += str(r['buggy_files'])

					new_line += "\t\t \\\\"

					if counter == 3:
						new_line += "\\hline"

					counter += 1
					if counter == 4:
						counter = 1
						
					table2_tex += new_line+"\n"
					
	f = open('Figures&Tables/tables_latex/table2.tex','w')
	f.write(table2_tex)
	f.close()	
	
	print("Updated file:    Figures&Tables/tables_latex/table2.tex")




#This function puts all of the required data in a dictionary and then reads table1.txt 
#which contains special characters which can be replaced to create the completed latex code.
def table_1():

	#Make dictionary to store stats
	table1_dict = {}
	for p in projects+['total']:
		table1_dict[p] = {"bugs":0,"commits":0,"releases":0, "links":0}

	#Open up relevant CSVs
	jira = pd.read_csv(dir+"intermediate_files/jira_issues.csv")
	git = pd.read_csv(dir+"intermediate_files/github_commits.csv")
	links = pd.read_csv(dir+"intermediate_files/links.csv")
    
    #Calculate table stats and store them in a dict
	for p in projects:
		jira_issue_keys = set(jira.loc[(jira['Project key'] == p.upper()) & (jira['Issue Type'] == 'Bug')]['Issue key'])
		link_issue_keys = set(links.loc[links['project'] == p.upper()]['Issue key'])
    
		table1_dict[p]["bugs"] = len(jira_issue_keys)
		table1_dict[p]["commits"] = git.loc[git['project'] == p].shape[0]
		table1_dict[p]["releases"] = len(set(jira.loc[jira['Project key'] == p.upper()]['Affects Version/s']))
		table1_dict[p]["links"] = math.floor((len(link_issue_keys)/len(jira_issue_keys))*100)
		
		table1_dict['total']["bugs"] += table1_dict[p]["bugs"]
		table1_dict['total']["commits"] += table1_dict[p]["commits"]
		table1_dict['total']["releases"] += table1_dict[p]["releases"]
		table1_dict['total']["links"] += table1_dict[p]["links"]
		
	table1_dict['total']['links'] = math.floor(table1_dict['total']['links']/len(projects))
	

	#Read in a latex table and fill in the new statistics
	table1_tex = ""
	
	with open("scripts/Analysis/blank_tables/table1.txt", "r") as f:
		for line in f.readlines():
			for p in table1_dict:
				if line.lower().startswith(p):
					line = line.replace("n1n1",str(table1_dict[p]['bugs']))
					line = line.replace("n2n2",str(table1_dict[p]['commits']))
					line = line.replace("n3n3",str(table1_dict[p]['releases']))
					line = line.replace("n4n4",str(table1_dict[p]['links'])+"\%")
			
			table1_tex += line
			
			
	f = open('Figures&Tables/tables_latex/table1.tex','w')
	f.write(table1_tex)
	f.close()	
	
	print("Updated file:    Figures&Tables/tables_latex/table1.tex")


##table_1()
#table_2()
#table_3()
#table_4()
#table_5()
#table_6()
#table_7()
table_8()
#table_9()

        


