#!/usr/bin/env bash

accumulo bookkeeper camel cassandra cxf derby hive felix openjpa pig wicket
for project in hive felix openjpa pig wicket
do

  mkdir "/media/kilby/UUI/buggy_files_modified/$project"
  echo $project
  cp "../files/buggy_files_modified/$project/vector_data.txt" "/media/kilby/UUI/buggy_files_modified/$project"


done
