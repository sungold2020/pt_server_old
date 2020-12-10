#!/usr/bin/python3
# coding=utf-8
import datetime
import time
import socket
import os
import requests
import re
import psutil
import codecs 
from bs4 import BeautifulSoup
import transmissionrpc
import qbittorrentapi

import movie
from rss import *
from info import Info
from torrent import Torrent
from mytorrent import *
from log import *
from ptsite import *
def request_rss(mRSSName="",mTimeInterval=-2):
    
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.82 Safari/537.36'}

    debug_log("request rss:{}::{}".format(mRSSName, mTimeInterval))
    tTorrentList = []
    for i in range(len(RSS_LIST)):
        if mRSSName.lower() == RSS_LIST[i]['name'].lower() or\
                (RSS_LIST[i]['time_interval'] != 0 and (mTimeInterval % RSS_LIST[i]['time_interval']) == 0) :
            RSSName  = RSS_LIST[i]['name']
            WaitFree = RSS_LIST[i]['wait_free']
            url      = RSS_LIST[i]['url']
        else: continue

        debug_log("==========begin {}==============".format(RSSName.ljust(10, ' ')))
        debug_log("URL:" + url)
        try: 
            page = requests.get(url, timeout=60, headers=headers)
        except Exception as err: 
            print(err)
            exec_log("failed to requests:" + RSSName)
            continue
        page.encoding = 'utf-8'
        page_content = page.text
        soup = BeautifulSoup(page_content, 'lxml-xml')
        items = soup.select('rss > channel > item')
        for i in range(len(items)):
            Title = items[i].title.string
            Title = Title.replace('|',',')   #避免Title中出现|分隔符
            ID    = items[i].guid.string
            DownloadLink = items[i].enclosure.get('url')
            #TorrentID    = get_torrent_id(DownloadLink)
            debug_log(Title + ":" + ID + ":" + DownloadLink)

            if RSSName == "HDSky" and Title.find("x265") == -1 : debug_log("hdsky not x265, ignore it:" + Title); continue
            #if RSSName == "MTeam" and Title.find("x264") >= 0  : DebugLog("mteam x264, ignore it:"+Title); continue

            tRSS = RSS(ID,RSSName,DownloadLink,Title)
            if tRSS.select(): 
                debug_log("old rss,ignore it:" + Title)
                continue

            Type = -1
            Nation = Name = Director = Actors = DoubanScore = DoubanID = DoubanLink = IMDBLink = IMDBScore = IMDBID = ""
            tInfo = None
            if RSSName == "LeagueHD" or\
               RSSName == "JoyHD"    or\
               RSSName == "HDArea"   or\
               RSSName == "PTSBao"   or\
               RSSName == "BeiTai"   or\
               RSSName[:5] == "HDSky"    or\
               RSSName[:5] == "MTeam"    :
                SummaryStr = items[i].description.string
                SummaryStr = re.sub(u'\u3000',u' ',SummaryStr)
                SummaryStr = re.sub(u'\xa0', u' ', SummaryStr)
                SummaryStr = re.sub('&nbsp;',' ',  SummaryStr)
                SummaryStr = SummaryStr.lower()
                debug_log(SummaryStr)
                        
                tInfo = Info()
                tIndex = SummaryStr.find("豆瓣评分")
                if tIndex >= 0 :
                    tempstr = SummaryStr[tIndex+5:tIndex+16]
                    tSearch = re.search("[0-9]\.[0-9]",tempstr)
                    if tSearch : DoubanScore = tSearch.group()
                    else:        DoubanScore = ""
                    debug_log("douban score:" + DoubanScore)
                else: debug_log("douban score:not find")
                tInfo.douban_score = DoubanScore
                
                tIndex = SummaryStr.find("豆瓣链接")
                if tIndex >= 0 :
                    tempstr = SummaryStr[tIndex:]
                    tIndex = tempstr.find("href=")
                    if tIndex >= 0:
                        tempstr = tempstr[tIndex+6:]
                        tIndex = tempstr.find('\"')
                        if tIndex >= 0 : DoubanLink = tempstr[:tIndex]; debug_log("douban link:" + DoubanLink)
                        else: debug_log("douban link:error:not find \"")
                    else: debug_log("douban link:error:not find href=")
                else: debug_log("douban link:not find")
                DoubanID = get_id_from_link(DoubanLink, DOUBAN)
                debug_log("DoubanLink:" + DoubanLink)
                tInfo.douban_id = DoubanID
                tInfo.douban_link = DoubanLink

                if   SummaryStr.find("imdb评分")    >= 0: tIndex = SummaryStr.find("imdb评分")           
                elif SummaryStr.find('imdb.rating') >= 0: tIndex = SummaryStr.find('imdb.rating')
                elif SummaryStr.find('imdb rating') >= 0: tIndex = SummaryStr.find('imdb rating')            
                else: tIndex = -1               
                if tIndex >= 0 :
                    tempstr = SummaryStr[tIndex+6:tIndex+36]
                    tSearch = re.search("[0-9]\.[0-9]",tempstr)
                    if tSearch :  IMDBScore = tSearch.group()
                debug_log("imdb score:" + IMDBScore)
                tInfo.imdb_score = IMDBScore
                
                if   SummaryStr.find("imdb链接")    >= 0: tIndex = SummaryStr.find("imdb链接")
                elif SummaryStr.find('imdb.link')   >= 0: tIndex = SummaryStr.find("imdb.link")
                elif SummaryStr.find('imdb link')   >= 0: tIndex = SummaryStr.find("imdb link")
                elif SummaryStr.find('imdb url')    >= 0: tIndex = SummaryStr.find('idmb url')           
                else                                    : tIndex = -1            
                if tIndex >= 0 :
                    tempstr = SummaryStr[tIndex:tIndex+200]
                    tIndex = tempstr.find("href=")
                    if tIndex >= 0:
                        tempstr = tempstr[tIndex+6:]
                        tIndex = tempstr.find('\"')
                        if tIndex >= 0 : IMDBLink = tempstr[:tIndex]
                        else:  debug_log("imdb link:error:not find \"")
                    else:
                        tIndex = tempstr.find('http')
                        if tIndex >= 0:
                            tempstr = tempstr[tIndex:]
                            tIndex = tempstr.find('<')
                            if tIndex >= 0 : IMDBLink = tempstr[:tIndex] 
                IMDBID = get_id_from_link(IMDBLink, IMDB)
                debug_log("imdb link:" + IMDBLink)
                tInfo.imdb_id = IMDBID

                if   SummaryStr.find("国  家")    >= 0: tIndex = SummaryStr.find("国  家")
                elif SummaryStr.find("产  地")    >= 0: tIndex = SummaryStr.find("产  地")
                else                                  : tIndex = -1
                if tIndex >= 0 :
                    Nation = SummaryStr[tIndex+5:tIndex+20]
                    if Nation.find('\n') >= 0: Nation = Nation[:Nation.find('\n')]
                    if Nation.find('<')  >= 0: Nation = Nation[ :Nation.find('<') ]
                    if Nation.find('/')  >= 0: Nation = Nation[ :Nation.find('/') ]
                    Nation = Nation.strip()
                    if   Nation[-1:] == '国' : Nation = Nation[:-1]  #去除国家最后的国字
                    elif Nation == '香港'    : Nation = '港'
                    elif Nation == '中国香港': Nation = '港'
                    elif Nation == '中国大陆': Nation = '国'
                    elif Nation == '中国台湾': Nation = '台'
                    elif Nation == '日本'    : Nation = '日'
                    else : pass
                    debug_log("Nation:" + Nation)
                else: debug_log("failed find nation")
                tInfo.nation = Nation

                tIndex = SummaryStr.find("类  别") 
                if tIndex >= 0 and SummaryStr[tIndex:tIndex+100].find("纪录") >= 0 : Type = RECORD
                elif SummaryStr.find("集  数") >= 0                                : Type = TV
                else                                                               : Type = MOVIE
                debug_log("type:" + str(Type))
                tInfo.type = Type

                if Nation == '港' or Nation == '国' or Nation == '台' : tIndex = SummaryStr.find("片  名")
                else                                                  : tIndex = SummaryStr.find("译  名")
                if tIndex >= 0 :
                    Name = SummaryStr[tIndex+5:tIndex+100]
                    if   Name.find("/")  >= 0 : Name = (Name[ :Name.find("/") ]).strip() 
                    elif Name.find("<")  >= 0 : Name = (Name[ :Name.find("<") ]).strip() 
                    elif Name.find('\n') >= 0 : Name = (Name[ :Name.find('\n') ]).strip()
                    else: debug_log("failed find name"); Name = ""
                else: debug_log("failed find name"); Name = ""
                #ExecLog("name:"+Name)
                if Name.find('<') >= 0 : Name = Name[:Name.find('<')]
                debug_log("name:" + Name)
                tInfo.movie_name = Name
                
                tIndex = SummaryStr.find("导  演")
                if tIndex >= 0 :
                    Director = SummaryStr[tIndex+5:tIndex+100]
                    tEndIndex = Director.find('\n')
                    if tEndIndex >= 0 : Director = Director[:tEndIndex]
                    else : Director = ""
                    Director = (Director[ :Director.find('<') ]).strip()
                else :Director = ""
                debug_log("director:" + Director)
                tInfo.director = Director

                tInfo.select() #尝试找下数据库的记录
                if tInfo.imdb_id != "":
                    if not tInfo.update_or_insert():
                        exec_log("failed to update or insert info:" + tInfo.imdb_id)
            #end if RSSName ==
            
            tRSS.douban_id = DoubanID
            tRSS.imdb_id = IMDBID
            if not tRSS.insert():  #记录插入rss数据库
                exec_log("failed to insert into rss:{}|{}".format(RSSName, ID))
                continue
            tTorrent = MyTorrent(None,tRSS,tInfo,TO_BE_ADD)

            if not WaitFree: 
                exec_log("new rss to be add torrent:" + tTorrent.title)
                exec_log("doubanID:{}|DoubanScore:{}|IMDBID:{}|IMDBScore:{}|Type:{}|Nation:{}|Name:{}|Director:{}|".format(DoubanID, DoubanScore, IMDBID, IMDBScore, Type, Nation, Name, Director))
                tTorrentList.append(tTorrent)
            else:
                debug_log("doubanID:{}|DoubanScore:{}|IMDBID:{}|IMDBScore:{}|Type:{}|Nation:{}|Name:{}|Director:{}|".format(DoubanID, DoubanScore, IMDBID, IMDBScore, Type, Nation, Name, Director))

        #end for Items
