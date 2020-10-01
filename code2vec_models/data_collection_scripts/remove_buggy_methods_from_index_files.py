import os
import re
import sys
import pandas as pd
import numpy as np
from os import listdir
from os.path import isfile, join

#NOTE: I manually copied the buggy_file folder and called it buggy_files_modified before running this script

def remove_buggy_methods(project):
    method_files_path = "/home/kilby/Documents/code/c2v_models/files/"+project+"/buggy_methods"
    method_files = [f for f in listdir(method_files_path) if isfile(join(method_files_path, f)) and "buggy" in f]

    index_file_path = "/home/kilby/Documents/code/c2v_models/files/buggy_files_modified/"+project+"/"

    count = 0
    print(len(method_files))

    for method_file in method_files:

        #Get method contents
        mf = open(method_files_path+"/"+method_file)
        method = mf.read()[2:-2]

        #Get the individual lines too
        mf.seek(0)
        method_lines = mf.readlines()[1:]
        mf.close()

        #Find method contents in index file
        target_file_name = method_file.split('_')[3]+".java"
        try:
            target_file = open(index_file_path+target_file_name,"r")
            contents = target_file.read()

            #Try to find and replace the method the easy way
            if method in contents:
                new_contents = contents.replace(method,"")
                count += 1

            #If the easy way didnt work, theres a white space problem
            #Try matching line by line and ignoring leading white space
            else:
                target_file.seek(0)
                target_lines = target_file.readlines()
                ml = 0
                remove_line_indeces = []

                for tl in range(len(target_lines)):
                    if method_lines[ml].lstrip() in target_lines[tl]:
                        remove_line_indeces.append(tl)
                        ml += 1
                        #If we matched every line, we're done
                        if ml == len(method_lines):
                            count += 1
                            break
                    else:
                        ml = 0
                        remove_line_indeces = []

                #Rewrite file, omitting buggy method lines
                new_contents = ""
                for tl in range(len(target_lines)):
                    if tl not in remove_line_indeces:
                        new_contents += target_lines[tl]

            target_file.close()

            target_file = open(index_file_path+target_file_name, "w")
            target_file.write(new_contents)
            target_file.close()



        except Exception as e:
            #print(e)
            pass

    print(count)






projects = ['accumulo', 'bookkeeper', 'camel', 'cassandra', 'cxf', 'derby', 'hive', 'openjpa', 'pig', 'wicket']
for p in projects:
    print(p)
    remove_buggy_methods(p)


#
