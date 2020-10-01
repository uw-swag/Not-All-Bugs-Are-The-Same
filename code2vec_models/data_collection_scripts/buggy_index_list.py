import os
import re
import sys
import pandas as pd


"""
This file saves a list of buggy file indexes for each project
"""

projects = ['accumulo', 'bookkeeper', 'camel', 'cassandra', 'cxf', 'derby', 'hive', 'openjpa', 'pig', 'wicket']

for p in projects:

    try:
        os.mkdir("../../files/buggy_files/"+p)
        os.mkdir("../../files/buggy_files_modified/"+p) #Used later to store "clean" versions
    except:
        pass


    df = pd.read_csv("../../files/"+p+"/train_data.csv")

    f = open("../../files/buggy_files/"+p+"/buggy_file_indexes",'w')

    indexes = set(df['index1'].to_list())

    for i in indexes:

        f.write(str(i)+"\n")

    f.close()
