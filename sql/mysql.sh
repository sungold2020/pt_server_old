#!/usr/bin/bash
create_db="create database IF NOT EXISTS movies"
#mysql -u root -pmoonbeam -e"${create_db}"
create_table='create table IF  NOT EXISTS test (\
	Number      SMALLINT   default 0,  \
	Copy        TINYINT    default 0,  \
	Nation      char(20)   default "", \
    Type        TINYINT   default 0,  \
	Name        char(50)   default "", \
    Min         SMALLINT   default 0,  \
    FormatStr   char(200)  default "", \
    DirName     char(200)  default "", \
	Jpg         TINYINT   default 0,  \
	Nfo         TINYINT   default 0,  \
	NumberOfSP  TINYINT   default 0,  \
	NumberOfVideo TINYINT default 0,  \
	EnglishName char(50)   default "", \
    Year        SMALLINT   default 0,  \
	Radio       char(12)    default "", \
    Version     char(20)   default "", \
    NationVersion char(10) default "", \
	Special     char(10)   default "", \
    Source      char(20)   default "", \
	Compress    char(8)    default "", \
	Audio       char(15)   default "", \
	Track       char(12)    default "", \
	Bit         char(10)   default 0,  \
	HDR         char(10)   default 0,  \
	ZipGroup    char(20)   default "", \
    Deleted     TINYINT   default 0,  \
	Disk       char(10)   default "", \
    UpdateTime  DATETIME   default "1900-01-01 00:00:00", \
	CheckTime   DATETIME   default "1900-01-01 00:00:00", \
	imdbID     char(10)   default "",\
	Genre      char(50)   default "",\
	viewed     char(1)    default "N",\
    PRIMARY KEY (Number,Copy))'
     	
#create_table='create table IF  NOT EXISTS test4 (\
#        Number      SMALLINT   default 0,  \
#        Track       char(20)   default "" )'
#create_table="create table IF  NOT EXISTS test (Number int,Name char(20))"

mysql -udummy -pmoonbeam db_movies -e"${create_table}"

	
