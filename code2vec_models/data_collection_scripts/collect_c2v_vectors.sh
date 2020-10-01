#!/usr/bin/env bash


cd /home/kilby/Documents/code/c2v_models/code2vec/


project=$1

#touch "../files/$project/vector_data.txt"

python3 code2vec.py --load models/java14_model/saved_model_iter8.release --predict -p $project
