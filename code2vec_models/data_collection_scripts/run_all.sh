
for i in accumulo bookkeeper camel cassandra cxf derby hive felix openjpa pig wicket
do
 ./run.sh $i
 #./link_indexes_with_filenames.sh $i

done
