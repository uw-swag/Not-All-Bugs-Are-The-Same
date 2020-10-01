#!/usr/bin/env bash


cd /home/kilby/Documents/code/c2v_models/code2vec/

echo "" > "../april10progress.txt"

# accumulo bookkeeper camel cassandra cxf derby hive felix openjpa pig wicket
for project in hive felix openjpa pig wicket
do
  echo "$project " >> "../april10progress.txt"
  #touch "../files/buggy_files_modified/$project/vector_data.txt"
  echo "" > "../files/buggy_files_modified/$project/vector_data.txt"

  python3 code2vec.py --load models/java14_model/saved_model_iter8.release --predict -p $project


done
