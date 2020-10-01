
import pandas as pd
import numpy as np
import math
import os
import statistics


full_df = pd.read_csv("../files/all_target_file_vectors.csv")
nabats_df = pd.read_csv("../files/nabats_dataset.csv")
projects = ['accumulo', 'bookkeeper', 'camel', 'cassandra', 'cxf', 'derby', 'hive', 'openjpa']



#Convert paths so that they match
nabats_df['filepath'] = nabats_df['filepath'].apply(lambda p : '/'.join(p.split('/')[7:]))
full_df['filepath'] = full_df['filepath'].apply(lambda p : '/'.join(p.split('/')[8:]))


for p in projects:
    print(p)
    c2v_df = pd.read_csv("../files/"+p+"/train_data5.csv")
    new_c2v_df = pd.DataFrame(columns = c2v_df.columns.values)

    #Narrow dfs to project
    p_full_df = full_df[full_df['project']==p]
    p_nabats_df = nabats_df[nabats_df['project']==p]

    #Sort through one release at a time
    releases = set(p_nabats_df['minor'].to_list())
    min_rel = releases.min()
    for r in releases:

        print(r)

        #Narrow project dfs to release
        r_full_df = p_full_df[p_full_df['minor']==r]
        r_nabats_df = p_nabats_df[p_nabats_df['minor']==r]
        r_c2v_df = c2v_df[c2v_df['minor']==r]

        #Remove duplicate methods from the same release
        r_full_df.drop_duplicates(subset ="vector", keep = 'first', inplace = True)
        r_c2v_df.drop_duplicates(subset ="vector", keep = 'first', inplace = True)


        #Remove all buggy files
        buggy_files = r_nabats_df[r_nabats_df['num_bugs']>0]['filepath']
        r_full_df = r_full_df[~r_full_df['filepath'].isin(buggy_files)]


        r_full_df['cc'] = r_full_df['filepath'].apply(lambda p : r_nabats_df[r_nabats_df['filepath']==p].iloc[0]['CC'])
        r_full_df['loc'] = r_full_df['filepath'].apply(lambda p : r_nabats_df[r_nabats_df['filepath']==p].iloc[0]['LOC'])
        r_full_df = r_full_df[['vector', 'major', 'minor', 'project', 'cc', 'loc']]
        r_full_df['buggy'] = 0
        r_full_df['hash'] = np.nan
        r_full_df['fix_size'] = 0
        r_full_df['priority'] = 0
        r_full_df['experience'] = 0
        r_full_df['index1'] = np.nan
        r_full_df['index2'] = np.nan
        r_full_df['date'] = np.nan
        r_full_df['release_id'] = range(min_rel,min_rel+3).index(r)

        #We remake the new c2v df because we have removed duplicate methods
        new_c2v_df = pd.concat([new_c2v_df, r_c2v_df, r_full_df])
        print(new_c2v_df.shape[0])



    #c2v_df.drop_duplicates(subset ="vector", keep = 'first', inplace = True)
    new_c2v_df.to_csv("../files/"+p+"/train_data5.csv")
