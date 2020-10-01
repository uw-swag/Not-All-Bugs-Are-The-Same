#!/usr/bin/env bash

project=$1
output_file="../files/$project/modified_functions.csv"


mkdir -p "../files/$project"
mkdir -p "../files/$project/buggy_methods"
python3 "make_project_bfcs_file.py" $project

cd "../../cloned_repos/$project"

awk -F "\"*,\"*" '{print}' "../../c2v_models/files/$project/bfcs.csv" | while read -r ROW

do

    hash=$(echo "$ROW" |cut -d ',' -f1 )
    hash="${hash}^!"

    git diff --no-prefix -U10000 $hash | python3 "../../c2v_models/scripts/save_diff_methods.py" $hash $project

done


exit 0
