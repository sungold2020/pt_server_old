#!/usr/bin/bash

SQL='alter table movies add OtherNames char(100) default ""'
mysql -uroot -pmoonbeam db_movies -e"$SQL"
SQL='alter table movies add ForeignName  char(50) default ""'
mysql -uroot -pmoonbeam db_movies -e"$SQL"
SQL='alter table movies add DoubanID char(15) default ""'
mysql -uroot -pmoonbeam db_movies -e"$SQL"
SQL='alter table movies add DoubanScore char(5) default ""'
mysql -uroot -pmoonbeam db_movies -e"$SQL"
SQL='alter table movies add IMDBScore char(5) default ""'
mysql -uroot -pmoonbeam db_movies -e"$SQL"
SQL='alter table movies add Director char(50) default ""'
mysql -uroot -pmoonbeam db_movies -e"$SQL"
SQL='alter table movies add Actors char(200) default ""'
mysql -uroot -pmoonbeam db_movies -e"$SQL"
SQL='alter table movies add Episodes tinyint default 0'
mysql -uroot -pmoonbeam db_movies -e"$SQL"
SQL='alter table movies add Poster char(100) default ""'
mysql -uroot -pmoonbeam db_movies -e"$SQL"
