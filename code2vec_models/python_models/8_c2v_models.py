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


class Prediction_Model:

    def __init__(self, project, release, all_projects=False, restart=False, cc_loc=True):

        self.nn_name = "c2v_"+self.target_column+"_"+project+"_"+str(release)
        if all_projects:
            self.nn_name = self.nn_name + "_all"
        self.project = project
        self.all_projects = all_projects
        self.cc_loc = cc_loc
        self.release = release

        if restart:
            self.restart()

        self.model = self.load_nn()

    def restart(self):
        try:
            os.remove("../files/nn_training/models/"+self.nn_name+".h5")
        except:
            pass

        try:
            os.remove("../files/nn_training/pickle_barrel/X_train_"+self.nn_name+".pkl")
            os.remove("../files/nn_training/pickle_barrel/X_test_"+self.nn_name+".pkl")
            os.remove("../files/nn_training/pickle_barrel/y_train_"+self.nn_name+".pkl")
            os.remove("../files/nn_training/pickle_barrel/y_test_"+self.nn_name+".pkl")
        except:
            pass

    def build_dataset(self):

        print("building dataset...")

        #Assemble data
        projects = [self.project]
        if self.all_projects:
            projects = ['accumulo', 'bookkeeper', 'camel', 'cassandra', 'cxf', 'derby', 'hive', 'openjpa']
        dfs = []
        for p in projects:
            p_df = pd.read_csv("../files/"+p+"/train_data5.csv")
            p_df['project'] = p

            buggy = p_df.loc[p_df['buggy']==1]
            clean = p_df.loc[p_df['buggy']==0]
            #Make sure not to load too many vectors or youll run out of memory
            #if p_df.loc[p_df['buggy']==0].shape[0] > 100000:
            #    clean = p_df.loc[p_df['buggy']==0].sample(n=100000)

            dfs.append(buggy)
            if self.target_column == "buggy":
                dfs.append(clean)


        df = pd.concat(dfs)

        #Convert vector data to lists
        def make_vector_list(v):
            try:
                v = v.replace('\n','').split(' ')
                return [float(i) for i in v]
            except:
                return [0.0]*384

        df['vector'] = df['vector'].apply(lambda v : make_vector_list(v))


        #Make sure exp has no na sort_values
        df['experience'] = df['experience'].fillna(0.0)
        df['priority'] = df['priority'].apply(lambda p : int(p-1))

        # Split data into train and test sets

        # If using all projects, only look at one release from each
        # Test on one project, train on the others
        if self.all_projects:
            df = df.loc[df['release_id']==self.release]
            test_set = df.loc[df['project']==self.project]
            train_set = df.loc[df['project']!=self.project]

        # If using one project, train on one release, test on the next
        else:
            df = df.loc[df['project']==self.project]
            test_set = df.loc[df['release_id']==self.release+1]
            train_set = df.loc[df['release_id']==self.release]

        # Specify inputs and outputs
        X_train = pd.DataFrame(train_set['vector'].to_list())
        y_train = train_set[self.target_column]
        X_test = pd.DataFrame(test_set['vector'].to_list())
        y_test = test_set[self.target_column]

        # If wanted, include cc and loc in the input data
        if self.cc_loc:

            X_train[len(X_train.columns)] = train_set['cc'].values
            X_train[len(X_train.columns)] = train_set['loc'].values
            X_test[len(X_test.columns)] = test_set['cc'].values
            X_test[len(X_test.columns)] = test_set['loc'].values

        # If the target is categorical, remake the y data so that the vector is spread throughout the columns
        if self.target_column == "priority":
            y_train = pd.DataFrame(np_utils.to_categorical(y_train, 5))
            y_test = pd.DataFrame(np_utils.to_categorical(y_test, 5))


        print(X_train.shape[1])



        #X_train = X_train.fillna(0.0)
        #X_test = X_test.fillna(0.0)

        #Only need to save the intra project sets, because inter project divisions are always the same
        #if not self.all_projects:
            #Save train and test sets
            #X_train.to_pickle("../files/nn_training/pickle_barrel/X_train_"+self.nn_name+".pkl")
            #X_test.to_pickle("../files/nn_training/pickle_barrel/X_test_"+self.nn_name+".pkl")
            #y_train.to_pickle("../files/nn_training/pickle_barrel/y_train_"+self.nn_name+".pkl")
            #y_test.to_pickle("../files/nn_training/pickle_barrel/y_test_"+self.nn_name+".pkl")


        with open("../method_counts.txt", 'a') as f:
            print(self.nn_name, X_train.shape[0], X_test.shape[0])
            f.write(self.nn_name +","+str(X_train.shape[0])+","+str(X_test.shape[0])+"\n")

        return X_train,X_test,y_train,y_test

    def get_dataset(self):

        #If the dataset has never been made, make it
        if not os.path.exists("../files/nn_training/pickle_barrel/X_train_"+self.nn_name+".pkl"):
            return self.build_dataset()

        #If it has been made, load the saved dataset
        X_train = pd.read_pickle("../files/nn_training/pickle_barrel/X_train_"+self.nn_name+".pkl")
        X_test = pd.read_pickle("../files/nn_training/pickle_barrel/X_test_"+self.nn_name+".pkl")
        y_train = pd.read_pickle("../files/nn_training/pickle_barrel/y_train_"+self.nn_name+".pkl")
        y_test = pd.read_pickle("../files/nn_training/pickle_barrel/y_test_"+self.nn_name+".pkl")

        return X_train,X_test,y_train,y_test

    def train(self, nepochs):


        X_train,X_test,y_train,y_test = self.get_dataset()

        #Train model
        print("training...")
        csv_logger = CSVLogger("../files/nn_training/training/nn_training_"+self.nn_name+".csv", append=True)
        self.model.fit(X_train,y_train,validation_data = (X_test,y_test), epochs=nepochs, verbose=1, callbacks=[csv_logger])
        self.model.save("../files/nn_training/models/"+self.nn_name+".h5")


class Buggy_Model(Prediction_Model):
    def __init__(self, project, release, all_projects=False , restart=False):
        self.target_column = "buggy"
        Prediction_Model.__init__(self, project, release, all_projects , restart)

    def test(self, print_result=False):
        X_train,X_test,y_train,y_test = self.get_dataset()

        y_pred = self.model.predict(X_test)

        pred = list()
        test = list()

        false_pos = 0.0
        false_neg = 0.0
        true_pos = 0.0
        true_neg = 0.0

        for i in range(len(y_pred)):

            prediction = int((y_pred[i][0]).round())
            actual = y_test.iloc[i]

            pred.append(prediction)
            test.append(actual)

            if prediction == 1:
                if actual == 1:
                    true_pos += 1
                else:
                    false_pos += 1
            else:
                if actual == 0:
                    true_neg += 1
                else:
                    false_neg += 1

        from sklearn.metrics import accuracy_score
        a = accuracy_score(pred,test)

        if (true_pos+false_pos) == 0:
            precision = 0
        else:
            precision = true_pos/(true_pos+false_pos)

        if (false_neg+true_pos) == 0:
            recall = 0
        else:
            recall = true_pos/(false_neg+true_pos)

        if print_result:
            print("False positives:",false_pos)
            print("False negatives:",false_neg)
            print("True positives:",true_pos)
            print("True negatives:",true_neg)
            print("precision:",precision)
            print("recall:",recall)
            print('Accuracy is:', a*100)

        return [precision,recall]

    def load_nn(self):
        if os.path.exists("../files/nn_training/models/"+self.nn_name+".h5"):
            return load_model("../files/nn_training/models/"+self.nn_name+".h5")

        input_dimensions = 384
        if self.cc_loc:
            input_dimensions = 386

        output_dimensions = 1

        model = Sequential()
        model.add(Dense(output_dimensions, input_dim=input_dimensions,activation='sigmoid'))
        model.compile(loss="binary_crossentropy", optimizer='adam')
        return model



class Priority_Model(Prediction_Model):
    def __init__(self, project, release, all_projects=False , restart=False):
        self.target_column = "priority"
        Prediction_Model.__init__(self,project, release,all_projects ,restart)

    def test(self, print_result=False):
        X_train,X_test,y_train,y_test = self.get_dataset()

        #Convert priority data for softmax output
        priority_conversion_dict = {
        1: [1,0,0,0,0],
        2: [0,1,0,0,0],
        3: [0,0,1,0,0],
        4: [0,0,0,1,0],
        5: [0,0,0,0,1]
        }
        y_pred = self.model.predict(X_test)
        #Converting predictions to label
        pred = list()
        test = list()
        for i in range(len(y_pred)):
            #if y_test.iloc[i].to_list() != [0,0,1,0,0]:
            pred.append(priority_conversion_dict[np.argmax(y_pred[i])+1])
            test.append(y_test.iloc[i].to_list())


        from sklearn.metrics import accuracy_score
        a = accuracy_score(pred,test)

        if print_result:
            print('Accuracy is:', a*100)

        return a

    def load_nn(self):
        if os.path.exists("../files/nn_training/models/"+self.nn_name+".h5"):
            return load_model("../files/nn_training/models/"+self.nn_name+".h5")

        input_dimensions = 384
        if self.cc_loc:
            input_dimensions = 386

        output_dimensions = 5

        model = Sequential()
        model.add(Dense(128, input_dim=input_dimensions,activation='relu'))
        model.add(Dense(32, activation='relu'))
        model.add(Dense(output_dimensions,activation='softmax'))
        model.compile(loss="categorical_crossentropy", optimizer='adam')

        return model


class Fix_Size_Model(Prediction_Model):
    def __init__(self, project, release, all_projects=False , restart=False):
        self.target_column = "fix_size"
        Prediction_Model.__init__(self,project,release,all_projects ,restart)

    def test(self, print_result=False):

        X_train,X_test,y_train,y_test = self.get_dataset()

        model = load_model("../files/nn_training/models/"+self.nn_name+".h5")
        y_pred = model.predict(X_test)
        #Converting predictions to label
        pred = list()
        test = list()
        MAE = []
        for i in range(len(y_pred)):
            MAE.append(abs((y_pred[i][0]) - (y_test.iloc[i])))
        MAE = statistics.median(MAE)

        if print_result:
            print("Mean Absolute Error:",MAE)

        return MAE

    def load_nn(self):
        if os.path.exists("../files/nn_training/models/"+self.nn_name+".h5"):
            return load_model("../files/nn_training/models/"+self.nn_name+".h5")


        input_dimensions = 384
        if self.cc_loc:
            input_dimensions = 386

        output_dimensions = 1

        model = Sequential()
        model.add(Dense(128, input_dim=input_dimensions,activation='relu'))
        model.add(Dense(32, activation='relu'))
        model.add(Dense(output_dimensions,activation='linear'))
        model.compile(loss="mean_squared_error", optimizer='adam')

        return model


class Experience_Model(Prediction_Model):

    def __init__(self, project, release, all_projects=False , restart=False):
        self.target_column = "experience"
        Prediction_Model.__init__(self,project, release, all_projects ,restart)


    def test(self, print_result=False):

        X_train,X_test,y_train,y_test = self.get_dataset()


        model = load_model("../files/nn_training/models/"+self.nn_name+".h5")
        y_pred = model.predict(X_test)
        #Converting predictions to label
        pred = list()
        test = list()
        MAE = []
        MSE = []
        for i in range(len(y_pred)):
            MAE.append(abs((y_pred[i][0]) - (y_test.iloc[i])))
            MSE.append(((y_pred[i][0]) - (y_test.iloc[i]))**2)
        MAE = statistics.median(MAE)
        MSE = statistics.mean(MSE)

        if print_result:
            print("Mean Absolute Error:",MAE)
            print("Mean Squared Error:",MSE)

        return MAE


    def load_nn(self):
        if os.path.exists("../files/nn_training/models/"+self.nn_name+".h5"):
            return load_model("../files/nn_training/models/"+self.nn_name+".h5")

        input_dimensions = 384
        if self.cc_loc:
            input_dimensions = 386

        output_dimensions = 1
        model = Sequential()
        model.add(Dense(128, input_dim=input_dimensions,activation='relu'))
        model.add(Dense(32, activation='relu'))
        model.add(Dense(output_dimensions,activation='linear'))
        model.compile(loss="mean_squared_error", optimizer='adam')
        return model




#
