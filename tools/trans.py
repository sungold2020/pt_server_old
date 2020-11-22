#!/usr/bin/python3

from info import *
from database import *

tSelectResult = select("select doubanid,imdbid,doubanscore,imdbscore,name,nation,type,foreignname,othernames,year,director,actors,episodes,poster,genre from movies",None)
for tResult in tSelectResult:
    DoubanID = tResult[0]
    IMDBID = tResult[1]
    tInfo = Info(DoubanID,IMDBID)
    if tInfo.spider_status == OK: continue
    tInfo.douban_score = tResult[2]
    tInfo.imdb_score = tResult[3]
    tInfo.movie_name = tResult[4]
    tInfo.nation = tResult[5]
    tInfo.type = tResult[6]
    tInfo.foreign_name = tResult[7]
    tInfo.other_names = tResult[8]
    tInfo.year = tResult[9]
    tInfo.director = tResult[10]
    tInfo.actor = tResult[11]
    tInfo.episodes = tResult[12]
    tInfo.poster = tResult[13]
    tInfo.genre = tResult[14]

    if tInfo.director != "": 
        tInfo.spider_status = OK
    if tInfo.poster != "":
        tInfo.douban_status = OK
    else:
        tInfo.douban_status = NOK
    print("{}:{}:{}".format(tInfo.imdb_id,tInfo.douban_id,tInfo.movie_name))

    if tInfo.imdb_id == "": continue
    if tInfo.insert():
        print("insert:"+tInfo.movie_name)

