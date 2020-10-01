from keras.models import Sequential
from keras.layers import Dense
import keras.metrics
import pandas as pd
import numpy as np
import math
import statistics
from keras.callbacks import CSVLogger
from sklearn.model_selection import train_test_split
import os
from keras.models import load_model
from keras.utils import np_utils



def load_df():
    print("loading full vector dataframe...")

    if os.path.exists("../files/all_methods2.pkl"):
        return pd.read_pickle("../files/all_methods2.pkl")

    #If it doesnt exist, create new pickle

    df = pd.read_csv("../files/all_target_file_vectors.csv")

    #Convert vector data to lists
    def make_vector_list(v):
        try:
            v = v.replace('\n','').split(' ')
            return [float(i) for i in v]
        except:
            return [0.0]*384

    df['vector'] = df['vector'].apply(lambda v : make_vector_list(v))


    nabats_df = pd.read_csv("../files/nabats_dataset.csv")
    nabats_df['filepath'] = nabats_df['filepath'].apply(lambda p : '/'.join(p.split('/')[7:]))
    df['filepath'] = df['filepath'].apply(lambda p : '/'.join(p.split('/')[8:]))

    df['cc'] = 0
    df['loc'] = 0
    for i,r in df.iterrows():
        df.at[i,'cc'] = nabats_df.loc[(nabats_df['filepath']==r['filepath'])&(nabats_df['project']==r['project'])&(nabats_df['minor']==r['minor'])].iloc[0]['CC']
        df.at[i,'loc'] = nabats_df.loc[(nabats_df['filepath']==r['filepath'])&(nabats_df['project']==r['project'])&(nabats_df['minor']==r['minor'])].iloc[0]['LOC']


    #quick fix
    p_dfs = []
    for p in ['accumulo', 'bookkeeper', 'camel', 'cassandra', 'cxf', 'derby', 'hive', 'openjpa']:

        p_df = df[df['project']==p]
        min_rel = p_df['minor'].min()
        p_df['release_id'] = p_df['minor'].apply(lambda r : int(r-min_rel))
        p_dfs.append(p_df)

    df = pd.concat(p_dfs)

    df.to_pickle("../files/all_methods.pkl")


    #NOTE save the df twice, once before and once after the prediction collection

    input = pd.DataFrame(df['vector'].to_list())
    input[len(input.columns)] = df['cc'].values
    input[len(input.columns)] = df['loc'].values

    for p in ['accumulo', 'bookkeeper', 'camel', 'cassandra', 'cxf', 'derby', 'hive', 'openjpa']:
        for r in [0,1,2]:
            for n in ['buggy','priority','fix_size','experience']:
                for i in ["","_all"]:
                    nn_name = n+"_"+p+"_"+str(r)+i

                    if os.path.exists("../files/nn_training/models/c2v_"+nn_name+".h5"):
                        print(nn_name)
                        model = load_model("../files/nn_training/models/c2v_"+nn_name+".h5")

                        #Get predictions
                        c2v_predictions = model.predict(input)

                        #Priority predictions are categorical, and must be converted to integers
                        if n == "priority":
                            c2v_predictions = (pd.DataFrame(c2v_predictions).idxmax(axis = 1, skipna = True)+1).to_numpy()

                        assert df.shape[0] == c2v_predictions.shape[0]
                        df[nn_name] = c2v_predictions


    df.to_pickle("../files/all_methods2.pkl")
    return df



def numbugs_to_buggy(x):
    if x > 0:
        return 1
    return 0



def pred_names():
    names = []
    for p in ['accumulo', 'bookkeeper', 'camel', 'cassandra', 'cxf', 'derby', 'hive', 'openjpa']:
        for r in [0,1,2]:
            for n in ['buggy','priority','fix_size','experience']:
                for i in ["","_all"]:
                    nn_name = n+"_"+p+"_"+str(r)+i

                    if os.path.exists("../files/nn_training/models/c2v_"+nn_name+".h5"):
                        names.append(nn_name)
    return names

# ----------------------- ^^^ methods ^^^ -------------------------------

input_size = 100
df = load_df()
pred_cols = pred_names()

nabats_df = pd.read_csv("../files/nabats_dataset.csv")
nabats_df['filepath'] = nabats_df['filepath'].apply(lambda p : '/'.join(p.split('/')[7:]))
nabats_df = nabats_df[['project','release_id','filepath','num_bugs','priority','exp','bfs']]
nabats_df['fix_size'] = nabats_df['bfs']
nabats_df['experience'] = nabats_df['exp']
nabats_df['buggy'] = nabats_df['num_bugs'].apply(lambda x : numbugs_to_buggy(x))


#Add pred names to nabats_df
for col in pred_cols:
    nabats_df[col] = ""




import pickle

#Hacky fix to split by project because full dict was taking all memory
#Need to clean this up
for p in ['accumulo', 'bookkeeper', 'camel', 'cassandra', 'cxf', 'derby', 'hive', 'openjpa']:

    print(p)


    full_data = {}
    for r in [0,1,2]:
        full_data[r] = {}
        for c in pred_cols:
            full_data[r][c] = {'X':[], 'y':[], 'filename':[]}

    p_nabats_df = nabats_df.loc[nabats_df['project']==p].reset_index()


    size = p_nabats_df.shape[0]
    for index,row in p_nabats_df.iterrows():


        #Output progress
        print(round(((index/size)*100)),"%",end="\r")


        methods = df.loc[(df['project']==row['project']) & (df['filepath'] == row['filepath']) & (df['release_id']==row['release_id'])]
        if methods.shape[0] > 0:

            for r in [0,1,2]:
                for n in ['buggy','priority','fix_size','experience']:
                    for scope in ["","_all"]:
                        nn_name = n+"_"+p+"_"+str(r)+scope
                        buggy_col = "buggy_"+p+"_"+str(r)+scope

                        if nn_name in pred_cols:

                            #Sort and get top <input_size>
                            methods = methods.sort_values(by=buggy_col, ascending=False).head(input_size)
                            x = methods[nn_name].to_list()
                            # If too short, pad with zeros
                            if len(x) < input_size:
                                x = x + ([0]*(input_size-len(x)))

                            full_data[row['release_id']][nn_name]['X'].append(x)
                            full_data[row['release_id']][nn_name]['filename'].append(row['filepath'])

                            expected_result = row[n]
                            if row['num_bugs'] > 0:
                                expected_result = expected_result/row['num_bugs']
                            full_data[row['release_id']][nn_name]['y'].append(expected_result)


    with open("../files/nn_training/pickle_barrel/rnn_input_dict_"+p+".pickle", 'wb') as handle:
        pickle.dump(full_data, handle, protocol=pickle.HIGHEST_PROTOCOL)
        handle.close()


#
