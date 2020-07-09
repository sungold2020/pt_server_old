#!/usr/bin/bash
DistinctList=("nation" "source" "radio" "version" "nationversion" "special" "compress" "audio" "track" "hdr" "bit" "zipgroup" "viewed")
for Distinct in ${DistinctList[@]}
do
	echo "##################$Distinct###################################"
mysql -uroot -pmoonbeam db_movies -e"select distinct $Distinct from movies"
done
