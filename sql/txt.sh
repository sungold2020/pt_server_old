#!/usr/bin/bash

echo $1
SQL="select * from movies into outfile '/tmp/sel.txt' fields terminated by '|' lines terminated by '\n'"
mysql -uroot -pmoonbeam db_movies -e"$SQL"
Today=`date +%Y%m%d`
mv /tmp/sel.txt /root/py/sql/$Today.txt

SQL="select * from rss into outfile '/tmp/sel.txt' fields terminated by '|' lines terminated by '\n'"
mysql -uroot -pmoonbeam db_movies -e"$SQL"
Today=`date +%Y%m%d`
mv /tmp/sel.txt /root/py/sql/rss_$Today.txt
