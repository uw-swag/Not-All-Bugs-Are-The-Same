from keras.models import Sequential
from keras.layers import Dense
import keras.metrics
import pandas as pd
import numpy as np
import math
from keras.callbacks import CSVLogger
from sklearn.model_selection import train_test_split
import os
import statistics
from keras.models import load_model
from sklearn.metrics import mean_squared_error
from keras.utils import np_utils
import pickle

class Prediction_Model:

    def __init__(self, project, release, all_projects=False, restart=False):
        self.nn_name = "ccc_"+self.target_column+"_"+project+"_"+str(release)
        if all_projects:
            self.nn_name = self.nn_name + "_all"
        self.project = project
        self.all_projects = all_projects
        self.release = release
        self.filenames = None

        if restart:
            self.restart()

        self.model = self.load_nn()


    def restart(self):
        try:
            os.remove("../files/nn_training/models/NN_"+self.nn_name+".h5")
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

        df = pd.read_csv("../files/nabats_dataset.csv")


        #Standardize independent variables
        df['CC'] = df['CC']-df['CC'].mean() / df['CC'].std()
        df['LOC'] = df['LOC']-df['LOC'].mean() / df['LOC'].std()
        df['churn'] = df['churn']-df['churn'].mean() / df['churn'].std()

        #Make a binary buggy column
        if self.target_column == "buggy":
            def is_buggy(n):
                if n >= 1:
                    return 1.0
                return 0.0
            df['buggy'] = df['num_bugs'].apply(lambda b : is_buggy(b))


        if self.target_column != "buggy" and self.target_column != "num_bugs":
            #Drop non-buggy rows
            df = df.loc[df['num_bugs']>0]

            #Get the average bfs per bug in each file
            df['bfs'] = df['bfs']/df['num_bugs']
            #Get the average exp per bug in each file
            df['exp'] = df['exp']/df['num_bugs']
            #Get average priority for each file
            df['priority'] = (df['priority']/df['num_bugs']).apply(lambda p : int(round(p))-1)


        # Make train and test sets based on release

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


        X_train = train_set[['CC','LOC','churn']]
        X_test = test_set[['CC','LOC','churn']]
        y_train = train_set[self.target_column]
        y_test = test_set[self.target_column]
        self.filenames = test_set['filepath'].to_list()

        if self.target_column == "priority" or self.target_column == "exp_cat":
            y_train = pd.DataFrame(np_utils.to_categorical(y_train, 5))
            y_test = pd.DataFrame(np_utils.to_categorical(y_test, 5))

        #Save train and test sets
        #X_train.to_pickle("../files/nn_training/pickle_barrel/X_train_"+self.nn_name+".pkl")
        #X_test.to_pickle("../files/nn_training/pickle_barrel/X_test_"+self.nn_name+".pkl")
        #y_train.to_pickle("../files/nn_training/pickle_barrel/y_train_"+self.nn_name+".pkl")
        #y_test.to_pickle("../files/nn_training/pickle_barrel/y_test_"+self.nn_name+".pkl")

        return X_train,X_test,y_train,y_test


    def get_dataset(self):

        #Saving seems unnecessary, so probably dont need this anymore
        #try:
        #    X_train = pd.read_pickle("../files/nn_training/pickle_barrel/X_train_"+self.nn_name+".pkl")
        #    X_test = pd.read_pickle("../files/nn_training/pickle_barrel/X_test_"+self.nn_name+".pkl")
        #    y_train = pd.read_pickle("../files/nn_training/pickle_barrel/y_train_"+self.nn_name+".pkl")
        #    y_test = pd.read_pickle("../files/nn_training/pickle_barrel/y_test_"+self.nn_name+".pkl")

        #except:
        X_train,X_test,y_train,y_test = self.build_dataset()


        return X_train,X_test,y_train,y_test



    def train(self, nepochs):

        X_train,X_test,y_train,y_test = self.get_dataset()

        #Train model
        print("training...")
        csv_logger = CSVLogger("../files/nn_training/training/nn_training_"+self.nn_name+".csv", append=True)
        self.model.fit(X_train,y_train,validation_data = (X_test,y_test), epochs=nepochs, verbose=0, callbacks=[csv_logger])
        self.model.save("../files/nn_training/models/NN_"+self.nn_name+".h5")


class Buggy_Model(Prediction_Model):

    def __init__(self, project, release, all_projects=False, restart=False):
        self.target_column = "buggy"
        Prediction_Model.__init__(self, project, release, all_projects, restart)


    def load_nn(self):

        if os.path.exists("../files/nn_training/models/NN_"+self.nn_name+".h5"):
            return load_model("../files/nn_training/models/NN_"+self.nn_name+".h5")

        input_dimensions = 3
        output_dimensions = 1

        model = Sequential()
        model.add(Dense(45, input_dim=input_dimensions,activation='relu'))
        model.add(Dense(45, activation='relu'))
        model.add(Dense(output_dimensions,activation='sigmoid'))
        model.compile(loss="binary_crossentropy", optimizer='adam')

        return model


    def test(self, print_result=True):

        X_train,X_test,y_train,y_test = self.get_dataset()
        y_pred = self.model.predict(X_test)

        from sklearn.metrics import precision_recall_curve
        from sklearn.metrics import auc
        precision, recall, thresholds = precision_recall_curve(y_test, y_pred)

        auc = auc(recall, precision)

        print("auc:",auc)


        from matplotlib import pyplot

        no_skill = len(y_test[y_test==1]) / len(y_test)
        pyplot.plot([0, 1], [no_skill, no_skill], linestyle='--', label='No Skill')
        pyplot.plot(recall, precision, marker='.', label='Logistic')
        # axis labels
        pyplot.xlabel('Recall')
        pyplot.ylabel('Precision')

        # show the legend
        pyplot.legend()
        # show the plot
        #pyplot.show()

        # #Converting predictions to label
        # pred = list()
        # test = list()
        #
        # false_pos = 0.0
        # false_neg = 0.0
        # true_pos = 0.0
        # true_neg = 0.0
        #
        # #save positive filepaths to compare with other model
        # tp_filepaths = []
        # fp_filepaths = []
        #
        # for i in range(len(y_pred)):
        #
        #     #prediction = int((y_pred[i][0]).round())
        #     prediction = 0
        #     if y_pred[i][0] > 0.5:
        #         prediction = 1
        #
        #     actual = y_test.iloc[i]
        #
        #     pred.append(prediction)
        #     test.append(actual)
        #
        #     if prediction == 1:
        #         if actual == 1:
        #             tp_filepaths.append(self.filenames[i])
        #             true_pos += 1
        #         else:
        #             fp_filepaths.append(self.filenames[i])
        #             false_pos += 1
        #     else:
        #         if actual == 0:
        #             true_neg += 1
        #         else:
        #             false_neg += 1
        #
        #
        # #Save files that tested positive, for comparison with other model (c2v)
        # with open("../files/nn_training/pickle_barrel/files_detected_by_"+self.nn_name+".pickle", 'wb') as handle:
        #     pickle.dump([tp_filepaths, fp_filepaths], handle, protocol=pickle.HIGHEST_PROTOCOL)
        #     handle.close()
        #
        # from sklearn.metrics import accuracy_score
        # a = accuracy_score(pred,test)
        # if (true_pos+false_pos) == 0:
        #     precision = 0
        # else:
        #     precision = true_pos/(true_pos+false_pos)
        #
        # if (false_neg+true_pos) == 0:
        #     recall = 0
        # else:
        #     recall = true_pos/(false_neg+true_pos)
        #
        # if print_result:
        #     print("False positives:",false_pos)
        #     print("False negatives:",false_neg)
        #     print("True positives:",true_pos)
        #     print("True negatives:",true_neg)
        #     print("precision:",precision)
        #     print("recall:",recall)
        #     print('Accuracy is:', a*100)

        #return [precision,recall]

        return [0,auc]


class Numbugs_Model(Prediction_Model):

    def __init__(self, project, release, all_projects=False, restart=False ):
        self.target_column = "num_bugs"
        Prediction_Model.__init__(self, project, release, all_projects, restart)


    def load_nn(self):

        if os.path.exists("../files/nn_training/models/NN_"+self.nn_name+".h5"):
            return load_model("../files/nn_training/models/NN_"+self.nn_name+".h5")

        input_dimensions = 3
        output_dimensions = 1

        model = Sequential()
        model.add(Dense(45, input_dim=input_dimensions,activation='relu'))
        model.add(Dense(45, activation='relu'))
        model.add(Dense(output_dimensions,activation='linear'))
        model.compile(loss="mean_squared_error", optimizer='adam')

        return model


    def test(self, print_result=True):

        X_train,X_test,y_train,y_test = self.get_dataset()
        y_pred = self.model.predict(X_test)

        MSE = mean_squared_error(y_test,y_pred)
        return MSE


class Fix_Size_Model(Prediction_Model):

    def __init__(self, project, release, all_projects=False, restart=False ):
        self.target_column = "bfs"
        Prediction_Model.__init__(self, project, release, all_projects, restart )


    def load_nn(self):

        if os.path.exists("../files/nn_training/models/NN_"+self.nn_name+".h5"):
            return load_model("../files/nn_training/models/NN_"+self.nn_name+".h5")

        input_dimensions = 3
        output_dimensions = 1
        hidden_layer_size = 100

        model = Sequential()
        model.add(Dense(hidden_layer_size, input_dim=input_dimensions,activation='relu'))
        model.add(Dense(hidden_layer_size, activation='relu'))
        model.add(Dense(hidden_layer_size, activation='relu'))
        model.add(Dense(output_dimensions,activation='linear'))
        model.compile(loss="mean_squared_error", optimizer='adam')

        return model


    def test(self, print_result=True):

        X_train,X_test,y_train,y_test = self.get_dataset()
        y_pred = self.model.predict(X_test)
        #Converting predictions to label
        pred = list()
        test = list()
        MAE = []
        MSE = 0.0
        for i in range(len(y_pred)):
            MAE.append(abs((y_pred[i][0]) - (y_test.iloc[i])))
            MSE += (y_pred[i][0] - y_test.iloc[i])**2

        MAE = statistics.median(MAE)
        MSE = MSE/len(y_pred)

        return MSE #temporarily returning MSE instead!!!


class Experience_Model(Prediction_Model):

    def __init__(self, project, release, all_projects=False, restart=False ):
        self.target_column = "exp"
        Prediction_Model.__init__(self, project, release, all_projects, restart )


    def load_nn(self):

        if os.path.exists("../files/nn_training/models/NN_"+self.nn_name+".h5"):
            return load_model("../files/nn_training/models/NN_"+self.nn_name+".h5")

        input_dimensions = 3
        output_dimensions = 1
        hidden_layer_size = 100

        model = Sequential()
        model.add(Dense(hidden_layer_size, input_dim=input_dimensions,activation='relu'))
        model.add(Dense(hidden_layer_size, activation='relu'))
        model.add(Dense(hidden_layer_size, activation='relu'))
        model.add(Dense(output_dimensions,activation='linear'))
        model.compile(loss="mean_squared_error", optimizer='adam')

        return model


    def test(self, print_result=True):

        X_train,X_test,y_train,y_test = self.get_dataset()
        y_pred = self.model.predict(X_test)
        #Converting predictions to label
        pred = list()
        test = list()
        MAE = []
        MSE = 0
        for i in range(len(y_pred)):
            MAE.append(abs((y_pred[i][0]) - (y_test.iloc[i])))
            MSE += (y_pred[i][0] - y_test.iloc[i])**2
        MAE = statistics.median(MAE)
        MSE = MSE/len(y_pred)

        return MSE #temporarily returning MSE instead!!!


class Priority_Model(Prediction_Model):

    def __init__(self, project, release, all_projects=False, restart=False ):
        self.target_column = "priority"
        Prediction_Model.__init__(self, project, release, all_projects, restart )


    def load_nn(self):

        if os.path.exists("../files/nn_training/models/NN_"+self.nn_name+".h5"):
            return load_model("../files/nn_training/models/NN_"+self.nn_name+".h5")

        input_dimensions = 3
        input_dimensions = 3
        output_dimensions = 5
        hidden_layer_size = 100

        model = Sequential()
        model.add(Dense(hidden_layer_size, input_dim=input_dimensions,activation='relu'))
        model.add(Dense(hidden_layer_size, activation='relu'))
        model.add(Dense(hidden_layer_size, activation='relu'))
        model.add(Dense(output_dimensions,activation='softmax'))
        model.compile(loss="mean_squared_error", optimizer='adam')

        return model


    def test(self, print_result=True):
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
        print('Accuracy is:', a*100)
        return a


class Exp_Cat_Model(Prediction_Model):

    def __init__(self, project, release, all_projects=False, restart=False ):
        self.target_column = "exp_cat"
        Prediction_Model.__init__(self, project, release, all_projects, restart )


    def load_nn(self):

        if os.path.exists("../files/nn_training/models/NN_"+self.nn_name+".h5"):
            return load_model("../files/nn_training/models/NN_"+self.nn_name+".h5")

        input_dimensions = 3
        output_dimensions = 3
        hidden_layer_size = 100

        model = Sequential()
        model.add(Dense(hidden_layer_size, input_dim=input_dimensions,activation='relu'))
        model.add(Dense(hidden_layer_size, activation='relu'))
        model.add(Dense(hidden_layer_size, activation='relu'))
        model.add(Dense(output_dimensions,activation='softmax'))
        model.compile(loss="categorical_crossentropy", optimizer='adam')

        return model


    def test(self, print_result=True):

        #self.model = self.load_nn()
        X_train,X_test,y_train,y_test = self.get_dataset()

        y_pred = self.model.predict(X_test)
        #Converting predictions to label
        pred = list()
        test = list()
        for i in range(len(y_pred)):
            #if y_test.iloc[i].to_list() != [0,0,1,0,0]:
            pred.append(np.argmax(y_pred[i]))
            test.append(np.argmax(y_test.iloc[i].to_list()))


        from sklearn.metrics import accuracy_score
        a = accuracy_score(pred,test)
        print('Accuracy is:', a*100)
        return a





















#
