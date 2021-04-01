#!/usr/bin/bash

SQL="select name,englishname,year,special,version,nationversion,source,radio,audio,track,compress,hdr,bit,zipgroup from movies where number=$1"
mysql -uroot -pmoonbeam db_movies -e"$SQL"
