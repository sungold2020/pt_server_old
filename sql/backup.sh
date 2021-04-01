#!/usr/bin/bash

Today=`date +%Y%m%d`
NewTable="movies_$Today"
echo $NewTable
mysql -uroot -pmoonbeam db_movies -e"drop table if exists $NewTable"
mysql -uroot -pmoonbeam db_movies -e"create table $NewTable select * from movies"

NewTable="rss_$Today"
echo $NewTable
mysql -uroot -pmoonbeam db_movies -e"drop table if exists $NewTable"
mysql -uroot -pmoonbeam db_movies -e"create table $NewTable select * from rss"
