import os
import pandas as pd
import numpy as np
import re
import datetime
import math


import matplotlib.pyplot as plt
import statistics

'''
#Working directory
dir = os.getcwd()+"/../.."
os.chdir(dir)

df = pd.read_csv(dir+"/intermediate_files/final_dataset.csv")
df = df.loc[df['num_post']>0]
df['avg_pri'] = round(df['priority']/df['num_post'])


x = []
y_mean = []
y_median = []
y_count = []

while df.shape[0] > 0:
	df = df.sort_values(by=['avg_pri'])
	min_pri = df.iloc[0]['avg_pri']
	
	x.append(min_pri)
	y_mean.append(df.loc[df['avg_pri'] == min_pri]['exp'].mean())
	y_median.append(df.loc[df['avg_pri'] == min_pri]['exp'].median())
	y_count.append(df.loc[df['avg_pri'] == min_pri].shape[0])

	
	df = df.loc[df['avg_pri'] > min_pri]




plt.figure()
plt.bar(range(len(y_median)), y_median)
plt.xticks(range(len(x)), x)
plt.ylabel("Median Experience")
plt.xlabel("Priority")
plt.title("priority vs Experience")
plt.tight_layout()
plt.savefig(dir+"/Figures&Tables/priority_vs_exp/median_exp_vs_priority.png")

plt.figure()
plt.bar(range(len(y_mean)), y_mean)
plt.xticks(range(len(x)), x)
plt.ylabel("Mean Experience")
plt.xlabel("Priority")
plt.title("priority vs Experience")
plt.tight_layout()
plt.savefig(dir+"/Figures&Tables/priority_vs_exp/mean_exp_vs_priority.png")

plt.figure()
plt.bar(range(len(y_count)), y_count)
plt.xticks(range(len(x)), x)
plt.ylabel("number of files")
plt.xlabel("Priority")
plt.title("priority vs Experience")
plt.tight_layout()
plt.savefig(dir+"/Figures&Tables/priority_vs_exp/file_counts_vs_priority.png")

'''


#Working directory
dir = os.getcwd()+"/../.."
os.chdir(dir)

df = pd.read_csv(dir+"/intermediate_files/target_bfcs.csv")



x = []
y_mean = []
y_median = []
y_count = []

while df.shape[0] > 0:
	df = df.sort_values(by=['priority'])
	min_pri = df.iloc[0]['priority']
	
	x.append(min_pri)
	y_mean.append(df.loc[df['priority'] == min_pri]['author_exp'].mean())
	y_median.append(df.loc[df['priority'] == min_pri]['author_exp'].median())
	y_count.append(df.loc[df['priority'] == min_pri].shape[0])

	
	df = df.loc[df['priority'] > min_pri]




plt.figure()
plt.bar(range(len(y_median)), y_median)
plt.xticks(range(len(x)), x)
plt.ylabel("Median Experience")
plt.xlabel("Priority")
plt.title("priority vs Experience")
plt.tight_layout()
plt.savefig(dir+"/Figures&Tables/priority_vs_exp/bug_lvl_median_exp_vs_priority.png")

plt.figure()
plt.bar(range(len(y_mean)), y_mean)
plt.xticks(range(len(x)), x)
plt.ylabel("Mean Experience")
plt.xlabel("Priority")
plt.title("priority vs Experience")
plt.tight_layout()
plt.savefig(dir+"/Figures&Tables/priority_vs_exp/bug_lvl_mean_exp_vs_priority.png")

plt.figure()
plt.bar(range(len(y_count)), y_count)
plt.xticks(range(len(x)), x)
plt.ylabel("number of files")
plt.xlabel("Priority")
plt.title("priority vs Experience")
plt.tight_layout()
plt.savefig(dir+"/Figures&Tables/priority_vs_exp/bug_counts_vs_priority.png")





