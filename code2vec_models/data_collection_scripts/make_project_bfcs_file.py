import os
import re
import sys
import pandas as pd
import numpy as np

#Get project name as argument
project = sys.argv[1]


df = pd.read_csv('../files/bugfixingcommits.csv')
p_df = df.loc[df['project']==project.upper()]

p_df.to_csv('../files/'+project+'/bfcs.csv', index=False)
