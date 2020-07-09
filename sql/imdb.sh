#!/usr/bin/bash

SQL='update movies set imdbid="tt0838221" where number=1695'
mysql -uroot -pmoonbeam db_movies -e"$SQL"
