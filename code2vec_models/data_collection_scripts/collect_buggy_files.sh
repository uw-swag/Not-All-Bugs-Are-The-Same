#!/usr/bin/env bash

cd "../.."

for project in accumulo bookkeeper camel cassandra cxf derby felix hive openjpa pig wicket
do

	echo $project


	file_path="files/clean_files/$project/buggy_file_indexes"
	target_indexes=`cat $file_path`

	cd "../cloned_repos/$project"

	for index in $target_indexes;
	do
		git show $index > "../../c2v_models/files/buggy_files/$project/$index.java"
	done

	cd "../../c2v_models"


done
