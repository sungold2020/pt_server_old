#!/usr/bin/bash

ID=$1
echo $ID
Start=${ID:0:2}
echo $Start
if [ $Start == "tt" ]
then
	SQL="update movies set imdbid=\"$1\" where number=\"$2\""
else
	SQL="update movies set doubanid=\"$1\" where number=\"$2\""
fi
echo $SQL
#mysql -uroot -pmoonbeam db_movies -e"$SQL"
