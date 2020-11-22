#!/usr/bin/python3
import re
import os

TORRENT_LIST_BACKUP = "data/pt.txt"  #种子信息备份目录（重要的是每天的上传量）
if not os.path.isfile(TORRENT_LIST_BACKUP): print(TORRENT_LIST_BACKUP+" does not exist"); exit()
    
for line in open(TORRENT_LIST_BACKUP):
    Client,HASH,Name,SiteName,Title,DownloadLink,AddStatusStr,DoubanID,IMDBID,SpiderStatusStr,DoubanStatusStr,DoubanScore,IMDBScore,DoubanLink,IMDBLink,MovieName,ForeignName,OtherNames,TypeStr,Nation,Director,Actors,Poster,EpisodesStr,Genre,tDateDataStr = line.split('|',25)
    if tDateDataStr [-1:] == '\n' :  tDateDataStr = tDateDataStr[:-1]  #remove '\n'
    tDateDataList = tDateDataStr.split(',')
    DateData = []
    for i in range(len(tDateDataList)) :
        if tDateDataList[i] == "" :  break      #最后一个可能为空就退出循环
        tDate = (tDateDataList[i])[:10]
        tData = int( (tDateDataList[i])[11:] )
        DateData.append({'date':tDate,'data':tData})
    
    if Client == "TR": continue

    print(Name+":"+SpiderStatusStr)

