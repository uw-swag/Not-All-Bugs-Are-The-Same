import os
import pandas as pd
import numpy as np
import re
import time
import datetime
import math


import matplotlib.pyplot as plt
import statistics
import os



"""

This script is used to make the figures for the paper. It outputs the figures to the Figures 
folder.

"""


projects = ["accumulo","bookkeeper","camel","cassandra","cxf","derby","felix","hive","openjpa","pig","wicket"]

#Working directory
dir = os.getcwd()+"/../../"
os.chdir(dir)


def make_bug_lvl_df():


    if os.path.exists(dir+"/intermediate_files/bfc_df.csv"):
        return pd.read_csv(dir+"/intermediate_files/bfc_df.csv")


    print("Creating the bug level dataframe...")

    bfcs = pd.read_csv(dir+"intermediate_files/target_bfcs.csv")
    numstats = pd.read_csv(dir+"intermediate_files/numstats/all_numstats.csv")

    bug_df = pd.DataFrame(columns=['project','hash','bfs','exp','cost'])


    for i,r in bfcs.iterrows():
        mean_exp=r['author_exp']

        bfs = 0
        bug_numstats = numstats.loc[numstats['hash'] == r['BFC_id']]
        for ni,nr in bug_numstats.iterrows():
            bfs += nr['la'] + nr['ld']
        cost = bfs*mean_exp
        
        if bfs>0:
            bug_df = bug_df.append({
            'project':r['project'].lower(),
            'hash':r['BFC_id'],
            'bfs':bfs,
            'exp':mean_exp,
            'cost':cost
            },ignore_index=True)

    print(bug_df.head())
    
    bug_df.to_csv(dir+"/intermediate_files/bfc_df.csv", index=False)

    return bug_df
        




dir = "/home/kjbaron/Documents/NABATS/"

df = make_bug_lvl_df()
projects = ["accumulo","bookkeeper","camel","cassandra","cxf","derby","felix","hive","openjpa","pig","wicket"]




def figure1():
    bfs = []
    exp = []
    cost = []

    for project in projects:
        bfs_list = df.loc[df['project'] == project]['bfs'].tolist()
        exp_list = df.loc[df['project'] == project]['exp'].tolist()
        cost_list = df.loc[df['project'] == project]['cost'].tolist()
        
        bfs.append(bfs_list)
        exp.append(exp_list)
        cost.append(cost_list)

    plt.figure(figsize=(11, 3))
    plt.boxplot(bfs)
    plt.yscale('log')
    plt.xticks(range(1,12), projects)
    plt.ylabel("Bug Fix Size")
    plt.savefig(dir+"Figures&Tables/Figure1/BFS_Boxplots.png")

    plt.figure(figsize=(11, 3))
    plt.boxplot(exp)
    plt.yscale('symlog')
    plt.xticks(range(1,12), projects)
    plt.ylabel("Dev Experience")
    plt.savefig(dir+"Figures&Tables/Figure1/EXP_Boxplots.png")

    plt.figure(figsize=(11, 3))
    plt.boxplot(cost)
    plt.yscale('symlog')
    plt.xticks(range(1,12), projects)
    plt.ylabel("Cost")
    plt.savefig(dir+"Figures&Tables/Figure1/COST_Boxplots.png")




def bar_chart(list, x_label, y_label, project):
    counts = []
    num_groups = 10
    scale = int(max(list)/num_groups)
    scale = scale+(10-scale%10)

    if x_label == "Cost":
        scale = 1000


    for x in range(1,11):
        counts.append(len([i for i in list if i > (x-1)*scale and i < (x*scale)]))

    plt.figure()
    #fig, ax = plt.subplots()
    plt.bar(range(num_groups), counts)
    plt.xticks(range(1,num_groups+1), range(scale, int(max(list)), scale))
    plt.ylabel(y_label)
    plt.xlabel(x_label)
    plt.title(project)
    plt.tight_layout()



    plt.savefig(dir+"Figures&Tables/Figure2/"+project+'_'+x_label+'.png')



def figure2():
    for project in projects:
        p_df = df.loc[df['project'] == project]

        #Exp will be the same for all files so just look for the mean exp from the first occurance of each bug_id
        exp_dict = dict()
        exps = []
        bfss = []
        costs = []
        
        #The maximums are required because we can only show a certain number of bars. 
        #I got the maximums from the old charts
        max_bfs = 100
        max_cost = 10000
        
        for index, row in p_df.iterrows():
            if row['hash'] in exp_dict:
                exp_dict[row['hash']].append(row['exp'])
            else:
                exp_dict[row['hash']] = [row['exp']]

            if row['bfs'] < max_bfs:
                bfss.append(row['bfs'])

            cost = row['bfs']*row['exp']
            if cost < max_cost:
                costs.append(cost)

        for key in exp_dict:
            exps.append(statistics.mean(exp_dict[key]))


        bar_chart(exps, "Dev_Experience", "#_Bugs", project)
        bar_chart(bfss, "Bug_Fix_Size", "#_Bugs", project)
        bar_chart(costs, "Cost", "#_Bugs", project)


figure1()




























	
