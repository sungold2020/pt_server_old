#!/usr/bin/bash

SQL='alter table rss add OtherNames char(100) default ""'
mysql -uroot -pmoonbeam db_movies -e"$SQL"
