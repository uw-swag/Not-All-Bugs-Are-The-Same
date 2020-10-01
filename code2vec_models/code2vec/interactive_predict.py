import traceback

from common import common
from extractor import Extractor

from os import listdir
from os.path import isfile, join

SHOW_TOP_CONTEXTS = 10
MAX_PATH_LENGTH = 8
MAX_PATH_WIDTH = 2
JAR_PATH = 'JavaExtractor/JPredict/target/JavaExtractor-0.0.1-SNAPSHOT.jar'


class InteractivePredictor:
    exit_keywords = ['exit', 'quit', 'q']

    def __init__(self, config, model):
        model.predict([])
        self.model = model
        self.config = config
        self.path_extractor = Extractor(config,
                                        jar_path=JAR_PATH,
                                        max_path_length=MAX_PATH_LENGTH,
                                        max_path_width=MAX_PATH_WIDTH)

    def read_file(self, input_filename):
        with open(input_filename, 'r') as file:
            return file.readlines()

    def predict(self):
        print('Starting interactive prediction...')

        # Make sure not to analyze the same file twice when I have to re-run

        #Config for buggy methods
        #test_files_path = "/home/kilby/Documents/code/c2v_models/files/"+self.config.PROJECT+"/buggy_methods"
        #vector_data_path = "/home/kilby/Documents/code/c2v_models/files/"+self.config.PROJECT+"/vector_data.txt"

        #Config for clean methods of buggy files
        #test_files_path = "/home/kilby/Documents/code/c2v_models/files/buggy_files_modified/"+self.config.PROJECT
        #vector_data_path = "/home/kilby/Documents/code/c2v_models/files/buggy_files_modified/"+self.config.PROJECT+"/vector_data.txt"

        #.. config continued for both configs above...
        #test_files = [f for f in listdir(test_files_path) if isfile(join(test_files_path, f))]
        #ignore_files = set()
        #CHANGE THIS BACK!
        #with open(vector_data_path, 'r') as vector_file:
            #for line in vector_file:
                #line = line.split(',')
                #ignore_files.add(line[0])
        #test_files = set(test_files) - ignore_files

        #Config to collect all methods from all cloned repos
        test_files_path = ""
        vector_data_path = "/home/kilby/Documents/code/c2v_models/files/all_target_file_vectors.txt"

        import pandas as pd
        import os

        df = pd.read_csv("/home/kilby/Documents/code/c2v_models/files/nabats_dataset.csv")

        test_files = []
        for i,r in df.iterrows():
            path = r['filepath']
            path = path.replace('NABATS','code').replace('kjbaron','kilby')
            path = path.split('/')
            path.insert(7,r['project'])
            path = "/".join(path)
            if os.path.isfile(path):
                test_files.append(path)

        counter = 0
        total = len(test_files)

        for input_filename in test_files:

            print(counter,"/", total, input_filename)
            counter += 1

            try:
                # predict_lines, hash_to_string_dict = self.path_extractor.extract_paths(input_filename)
                predict_lines, hash_to_string_dict = self.path_extractor.extract_paths(
                    test_files_path + '/' + input_filename)
            except ValueError as e:
                print(e)
                print(input_filename)
                continue
            raw_prediction_results = self.model.predict(predict_lines)
            method_prediction_results = common.parse_prediction_results(
                raw_prediction_results, hash_to_string_dict,
                self.model.vocabs.target_vocab.special_words, topk=SHOW_TOP_CONTEXTS)

            for raw_prediction, method_prediction in zip(raw_prediction_results, method_prediction_results):

                # print('Original name:\t' + method_prediction.original_name)
                # for name_prob_pair in method_prediction.predictions:
                #    print('\t(%f) predicted: %s' % (name_prob_pair['probability'], name_prob_pair['name']))
                # print('Attention:')
                # for attention_obj in method_prediction.attention_paths:
                #    print('%f\tcontext: %s,%s,%s' % (
                #    attention_obj['score'], attention_obj['token1'], attention_obj['path'], attention_obj['token2']))

                # MODIFIED BY KILBY TO COLLECT VECTORS ALONG WITH FILE AND METHOD NAMES
                if self.config.EXPORT_CODE_VECTORS:
                    # print('Code vector:')
                    # print(' '.join(map(str, raw_prediction.code_vector)))



                    with open(vector_data_path, 'a') as f:
                        f.write(input_filename + "," + raw_prediction.original_name + "," + ' '.join(
                            map(str, raw_prediction.code_vector)) + "\n")
