
# LSTM with Dropout for sequence classification in the IMDB dataset
import numpy as np
import pandas as pd
from keras.datasets import imdb
from keras.models import Sequential
from keras.layers import Dense
from keras.layers import LSTM
from keras.layers import Dropout
from keras.layers.embeddings import Embedding
from keras.preprocessing import sequence
import pickle
from keras.utils import np_utils
import os
from keras.models import load_model
from keras.losses import mean_squared_error
import statistics


def get_model(output_activation, loss_function, output_dimensions):
    model = Sequential()
    model.add(Dense(100, input_dim=100,activation='relu'))
    model.add(Dense(100, activation='relu'))
    model.add(Dense(100, activation='relu'))
    model.add(Dense(100, activation='relu'))
    model.add(Dense(output_dimensions, activation=output_activation))
    model.compile(loss=loss_function, optimizer='adam')
    return model



def buggy_results(current_model, X, y, file_names):

    #save positive filepaths to compare with other model
    tp_filepaths = []
    fp_filepaths = []

    y_pred = current_model.predict(X)

    #Converting predictions to label
    pred = list()
    test = list()

    false_pos = 0.0
    false_neg = 0.0
    true_pos = 0.0
    true_neg = 0.0

    for i in range(len(y_pred)):

        prediction = 0
        if y_pred[i][0] > 0.5:
            prediction = 1

        actual = y[i]

        pred.append(prediction)
        test.append(actual)

        if prediction == 1 and actual == 1:
                tp_filepaths.append(file_names[i])
                true_pos += 1
        elif prediction == 1 and actual == 0:
                fp_filepaths.append(file_names[i])
                false_pos += 1
        elif actual == 0:
                true_neg += 1
        else:
                false_neg += 1

    if (true_pos+false_pos) == 0:
        precision = 0
    else:
        precision = true_pos/(true_pos+false_pos)

    if (false_neg+true_pos) == 0:
        recall = 0
    else:
        recall = true_pos/(false_neg+true_pos)

    #This seperate calculation gets precision and recall for every threshold and then calculate the AUC
    #The section above uses a threshold of 0.5 as a test to compare file detections with the CCC model
    from sklearn.metrics import precision_recall_curve
    from sklearn.metrics import auc
    precision, recall, thresholds = precision_recall_curve(y.astype(int), y_pred)

    auc = auc(recall, precision)


    from matplotlib import pyplot
    y = y.astype(int)
    no_skill = len(y[y==1]) / len(y_test)
    pyplot.plot([0, 1], [no_skill, no_skill], linestyle='--', label='No Skill')
    pyplot.plot(recall, precision, marker='.', label='Logistic')
    # axis labels
    pyplot.xlabel('Recall')
    pyplot.ylabel('Precision')

    #pyplot.plot(thresholds, precision[:-1], marker='.', label='Precision')
    #pyplot.plot(thresholds, recall[:-1], marker='.', label='Recall')

    # axis labels
    #pyplot.xlabel('Threshold')
    #pyplot.ylabel('Precision / Recall')

    # show the legend
    #pyplot.legend()
    # show the plot
    #pyplot.show()




    print("auc:",auc)

    return [precision, recall, [tp_filepaths, fp_filepaths], auc]


def priority_results(current_model, X, y, file_names):
    #Convert priority data for softmax output

    y_pred = current_model.predict(X)
    #Converting predictions to label
    pred = list()
    test = list()
    for i in range(len(y_pred)):
        #if y_test.iloc[i].to_list() != [0,0,1,0,0]:
        pred.append(int(np.argmax(y_pred[i])+1))
        test.append(int(np.argmax(y[i])))

    from sklearn.metrics import accuracy_score
    a = accuracy_score(pred,test)
    print('Accuracy is:', a*100)
    return a



def linear_results(current_model, X, y, file_names):

    y_pred = current_model.predict(X)
    #Converting predictions to label
    pred = list()
    test = list()
    MAE = []
    MSE = 0.0
    ME_list = []
    for i in range(len(y_pred)):
        MAE.append(abs((y_pred[i][0]) - (y[i])))
        MSE += (y_pred[i][0] - y[i])**2
        ME_list.append(abs(y_pred[i][0] - y[i]))


    ME_list.sort()
    print(ME_list)



    from matplotlib import pyplot

    pyplot.plot(range(0,len(y_pred)), ME_list, marker='.', label='Logistic')
    # axis labels
    pyplot.xlabel('Prediction')
    pyplot.ylabel('Error')

    #pyplot.plot(thresholds, precision[:-1], marker='.', label='Precision')
    #pyplot.plot(thresholds, recall[:-1], marker='.', label='Recall')

    # axis labels
    #pyplot.xlabel('Threshold')
    #pyplot.ylabel('Precision / Recall')

    # show the legend
    #pyplot.legend()
    # show the plot
    pyplot.show()




    MAE = statistics.median(MAE)
    MSE = MSE/len(y_pred)


    return MSE




def test_model(current_model, type, X, y, file_names):
    if type == 'buggy':
        return buggy_results(current_model, X, y, file_names)

    elif type == 'priority':
        return priority_results(current_model, X, y, file_names)

    else:
        return linear_results(current_model, X, y, file_names)










full_data = {}
for p in ['accumulo', 'bookkeeper', 'camel', 'cassandra', 'cxf', 'derby', 'hive', 'openjpa']:

    with open("../files/nn_training/pickle_barrel/rnn_input_dict_"+p+".pickle", 'rb') as handle:
        full_data[p] = pickle.load(handle)



projects = ['accumulo', 'bookkeeper', 'camel', 'cassandra', 'cxf', 'derby', 'hive', 'openjpa']

model_specs = {"buggy":["sigmoid", "binary_crossentropy", 1],
                "numbugs":["relu", "mean_squared_error", 1],
                "fix_size":["relu", "mean_squared_error", 1],
                "priority":["softmax", "categorical_crossentropy", 5],
                "experience":["relu", "mean_squared_error", 1]
                }


result_df = pd.DataFrame(columns=['project','release'])
for name in ['buggy','priority','fix_size','experience']: #col
    for scope in ["","_all"]:
        if name == "buggy":
            result_df[name+scope+"_precision"] = 0
            result_df[name+scope+"_recall"] = 0
        else:
            result_df[name+scope] = 0
result_row = 0


for project in projects: #row

    for release in [0,1,2]: #row
        result_row += 1
        result_df.at[result_row,'project'] = project
        result_df.at[result_row,'release'] = release
        #result_df.at[result_row,''] =

        for name in ['buggy','priority','fix_size','experience']: #col

            for scope in ["","_all"]: #col


                nn_name = name+"_"+project+"_"+str(release)+scope
                if nn_name in full_data[project][release]:



                    #Initialize train and test sets so that they are reset
                    X_train = []
                    y_train = []
                    X_test = []
                    y_test = []
                    test_file_names = []

                    #INTRA
                    if scope == "":
                        if release < 2:
                            X_train = full_data[project][release][nn_name]['X']
                            y_train = full_data[project][release][nn_name]['y']
                            X_test = full_data[project][release+1][nn_name]['X']
                            y_test = full_data[project][release+1][nn_name]['y']
                            test_file_names = full_data[project][release+1][nn_name]['filename']

                    #INTER
                    if scope == "_all":
                        for p2 in projects:
                            if p2 != project:
                                temp_name = name+"_"+p2+"_"+str(release)+scope
                                if temp_name in full_data[p2][release]:
                                    X_train = X_train + full_data[p2][release][temp_name]['X']
                                    y_train = y_train + full_data[p2][release][temp_name]['y']
                        X_test = full_data[project][release][nn_name]['X']
                        y_test = full_data[project][release][nn_name]['y']
                        test_file_names = full_data[project][release][nn_name]['filename']


                    X_train = np.array(X_train)
                    y_train = np.array(y_train)
                    X_test = np.array(X_test)
                    y_test = np.array(y_test)



                    #If re not predicting bugs, only use buggy files
                    if name != "buggy" and name != "numbugs":
                        assert X_train.shape[0] == y_train.shape[0]
                        assert X_test.shape[0] == y_test.shape[0]
                        X_train = X_train[y_train != 0]
                        y_train = y_train[y_train != 0]
                        #re-arranged to filter the filepaths as well
                        #X_test = X_test[y_test != 0]
                        #y_test = y_test[y_test != 0]

                        new_y_test = []
                        new_X_test = []
                        new_filepaths = []

                        for y_index in range(len(y_test)):
                            if y_test[y_index]!=0:
                                new_y_test.append(y_test[y_index])
                                new_X_test.append(X_test[y_index])
                                new_filepaths.append(test_file_names[y_index])
                        y_test = np.array(new_y_test)
                        X_test = np.array(new_X_test)
                        test_file_names = new_filepaths

                    print(nn_name)
                    print(y_test.shape[0], len(test_file_names))

                    assert X_train.shape[0] == y_train.shape[0]
                    assert X_test.shape[0] == y_test.shape[0]
                    assert y_test.shape[0] == len(test_file_names)


                    #As long as there is data in the train and test sets...
                    if X_train.shape[0]>0 and X_test.shape[0]>0:

                        if name == "priority":
                            y_train = np_utils.to_categorical(y_train-1, 5)
                            y_test = np_utils.to_categorical(y_test-1, 5)

                        if os.path.exists("../files/nn_training/models/file_c2v_"+nn_name+".h5"):
                            model = load_model("../files/nn_training/models/file_c2v_"+nn_name+".h5")
                        else:
                            model = get_model(model_specs[name][0], model_specs[name][1], model_specs[name][2])

                        print("training...")


                        #nepochs = 100
                        #model.fit(X_train,y_train,validation_data = (X_test,y_test), epochs=nepochs, verbose=1)
                        #model.save("../files/nn_training/models/file_c2v_"+nn_name+".h5")


                        print("testing...")
                        #Testing...
                        result = test_model(model, name, X_test, y_test, test_file_names)
                        if name == "buggy":
                            #Hacky chnage to gather auc VALUES
                            #result_df.at[result_row,name+scope+"_precision"] = result[0]
                            #result_df.at[result_row,name+scope+"_recall"] = result[1]
                            result_df.at[result_row,name+scope+"_precision"] = -1
                            result_df.at[result_row,name+scope+"_recall"] = result[3]



                            with open("../files/nn_training/pickle_barrel/files_detected_by_"+nn_name+".pickle", 'wb') as handle:
                                pickle.dump(result[2], handle, protocol=pickle.HIGHEST_PROTOCOL)
                                handle.close()
                        else:
                            result_df.at[result_row,name+scope] = str(result)


#NOTE!!! RECALL COLUMN WAS CHANGED TO AUC TO QUICKLY GATHER RESULTS!!

result_df.to_csv("../c2v_file_level_model_results_MSE_TEST.csv")














#
