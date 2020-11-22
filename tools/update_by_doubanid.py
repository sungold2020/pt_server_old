#!/usr/bin/python3
# coding=utf-8
"""
    根据movies中的doubanid，重新完整刷新或者插入info表数据
    如果movies中的imdbid不存在，同步更新movies中的imdbid
"""
import os
import os.path
import shutil
import re
import datetime
import time
import random

from info import *

select_sql = "select Nation, Year, DoubanID, IMDBID, Name, ForeignName, Director, Actors, Episodes, Poster, Number, Copy ,DirName from movies"
result = select(select_sql,None)
for tSelect in result:
    dbNation      = tSelect[0]
    dbYear        = tSelect[1]
    dbDoubanID    = tSelect[2]
    dbIMDBID      = tSelect[3]
    dbName        = tSelect[4]
    dbForeignName = tSelect[5]
    dbDirector    = tSelect[6]
    dbActors      = tSelect[7]
    dbEpisodes    = tSelect[8]
    dbPoster      = tSelect[9]
    dbNumber      = tSelect[10]
    dbCopy        = tSelect[11]
    dbDirName     = tSelect[12]
    dbNumberName    = str(dbNumber).zfill(4)+"-"+dbName

    #如果director非空，说明已经刮削过。否则开始刮削
    #if dbIMDBID != "" and dbDoubanID != "" and dbDirector != "" : DebugLog("igore :"+dbNumberName);continue
    
    tInfo = Info(dbDoubanID,dbIMDBID)
    tToBeUpdate = False
    if tInfo.douban_id == "" or tInfo.imdb_id == "" or tInfo.poster == "" or dbDoubanID == "" or dbIMDBID == "":
        DebugLog("id is empty:"+dbDirName)
        tToBeUpdate = True
    if not(dbName in tInfo.movie_name or tInfo.movie_name in dbName):
        ExecLog("different name:{}|{}|{}".format(dbName,tInfo.movie_name,dbDirName))
        tToBeUpdate = True
    if dbNation != tInfo.nation :
        ExecLog("different nation:{}|{}|{}".format(dbNation,tInfo.nation,dbDirName))
        tToBeUpdate = True
    if abs(dbYear-tInfo.year) >= 2:
        ExecLog("different year:{}|{}|{}".format(dbYear,tInfo.year,dbDirName))
        tToBeUpdate = True

    tToBeUpdate = False
    if tToBeUpdate == False:
        print("ignore:"+dbDirName)
        continue

    #ExecLog("tobeexec:"+dbDirName)
    if not tInfo.douban_detail():
        ExecLog("failed to douban detail"+dbDoubanID)
        continue

    if tInfo.update_or_insert():
        ExecLog("success to update or insert info:"+dbDirName)
    else:
        ExecLog("failed to update or insert info:"+dbDirName)
    
    if dbIMDBID == "" and tInfo.imdb_id != "": 
        up_sql = "update movies set imdbid=%s where number=%s and copy=%s"
        up_val = (tInfo.imdb_id,dbNumber,dbCopy)
        if  update(up_sql,up_val):
            ExecLog("update movies set imdbid={} where dirname={}".format(tInfo.imdb_id,dbDirName))
        else:
            ExecLog("failed to exec:{}|{}".format(up_sql,up_val))
        
    tSeconds = random.randint(120,600)
    print("sleep {} Seconds:".format(tSeconds))
    time.sleep(tSeconds)

