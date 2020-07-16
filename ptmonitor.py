#!/usr/bin/python3
# coding=utf-8
import datetime
import time
import socket
import os
import requests
import feedparser
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
from torrent_info import TorrentInfo
from viewed import *

#运行设置############################################################################
#日志文件
PTPORT = 12346
#TR/QB的连接设置    
TR_LOGIN = {'host':"localhost", 'port':9091, 'username':'dummy', 'password':'moonbeam' }
QB_LOGIN = {'host_port':'localhost:8989', 'username':'admin', 'password':'moonbeam' }



#连续NUMBEROFDAYS上传低于UPLOADTHRESHOLD，并且类别不属于'保种'的种子，会自动停止。
NUMBEROFDAYS = 1                           #连续多少天低于阈值
UPLOADTHRESHOLD = 0.03                     #阈值，上传/种子大小的比例


TORRENT_LIST_BACKUP = "data/pt.txt"  #种子信息备份目录（重要的是每天的上传量）

#配置自己要检查的磁盘/保存路径，看下面是否有文件夹/文件已经不在种子列表，这样就可以转移或者删除了。
#CHECK_DISK_LIST = [ "/media/root/SG8T","/media/root/BT/movies"]
CHECK_DISK_LIST = ["/media/root/BT/movies"]
#如果有一些文件夹/文件不想总是被检查，可以建一个忽略清单
IGNORE_FILE = "data/ignore.txt"

TRACKER_LIST_BACKUP = "data/tracker.txt"               
TrackerDataList = [\
        {'name':'FRDS'     ,'keyword':'frds'     ,'date_data':[]},\
        {'name':'MTeam'    ,'keyword':'m-team'   ,'date_data':[]},\
        {'name':'HDHome'   ,'keyword':'hdhome'   ,'date_data':[]},\
        {'name':'BeiTai'   ,'keyword':'beitai'   ,'date_data':[]},\
        {'name':'JoyHD'    ,'keyword':'joyhd'    ,'date_data':[]},\
        {'name':'SoulVoice','keyword':'soulvoice','date_data':[]},\
        {'name':'PTHome'   ,'keyword':'pthome'   ,'date_data':[]},\
        {'name':'LeagueHD' ,'keyword':'leaguehd' ,'date_data':[]},\
        {'name':'HDArea'   ,'keyword':'hdarea'   ,'date_data':[]},\
        {'name':'PTSBao'   ,'keyword':'ptsbao'   ,'date_data':[]},\
        {'name':'AVGV'     ,'keyword':'avgv'     ,'date_data':[]},\
        {'name':'HDSky'    ,'keyword':'hdsky'    ,'date_data':[]}]

#运行设置结束#################################################################################



#可变全局变量
gPTIgnoreList = []
gTorrentList = [] 
global gLastCheckDate
gLastCheckDate = "1970-01-01"
global gIsNewDay
gIsNewDay = False
global gToday
gToday = "1970-01-01"


def get_torrent_index(mClient,mHASH):
    for i in range(len(gTorrentList)) :
        if gTorrentList[i].client == mClient and (mHASH == gTorrentList[i].hash or mHASH == gTorrentList[i].HASH): return i

    return -1   

def read_pt_backup():
    """
    读取备份目录下的pt.txt，用于恢复种子记录数据，仅当初始化启动时调用
    """
    
    global gTorrentList
    global gLastCheckDate
    
    if not os.path.isfile(TORRENT_LIST_BACKUP): ExecLog(TORRENT_LIST_BACKUP+" does not exist"); return 0
        
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

        #tTorrent = Torrent(Client,None,HASH,SiteName,Title,DownloadLink,int(AddStatusStr),DoubanID,IMDBID,int(SpiderStatusStr))
        tBasicTorrent = Torrent(Client,None)
        tBasicTorrent.date_data   =     DateData

        tRSS = RSS(HASH,SiteName,DownloadLink,Title,DoubanID,IMDBID)
        
        tInfo = Info(DoubanID,IMDBID,int(SpiderStatusStr))
        tInfo.douban_status = int(DoubanStatusStr)
        tInfo.douban_score  =     DoubanScore
        tInfo.imdb_score    =     IMDBScore
        tInfo.douban_link   =     DoubanLink
        tInfo.imdb_link     =     IMDBLink
        tInfo.movie_name    =     MovieName
        tInfo.foreign_name  =     ForeignName
        tInfo.other_names   =     OtherNames
        tInfo.type          = int(TypeStr)
        tInfo.nation        =     Nation
        tInfo.director      =     Director
        tInfo.actors        =     Actors
        tInfo.poster        =     Poster
        tInfo.episodes      = int(EpisodesStr)
        tInfo.genre         =     Genre

        tMyTorrent = MyTorrent(tBasicTorrent,tRSS,tInfo,int(AddStatusStr))
        #if tMyTorrent.client == 'TR':
        #    tMyTorrent.add_status = STARTED
        #    if tMyTorrent.spider_status == RETRY: tMyTorrent.spider_status = NOK
        #    if tMyTorrent.douban_status == RETRY: tMyTorrent.douban_status = NOK
        gTorrentList.append(tMyTorrent)
    #end for 
    
    gLastCheckDate = tDate
    return 1

def write_pt_backup():
    """
    把当前RSS列表写入备份文件
    """
    
    if gIsNewDay == True :
        DebugLog("new day is :"+gToday)
        tThisMonth = gToday[0:7] ; tThisYear = gToday[0:4]
        if tThisMonth[5:7] == "01" :  tLastMonth = str(int(tThisYear)-1)+"-"+"12"      
        else                       :  tLastMonth = tThisYear+"-"+str(int(tThisMonth[5:7])-1).zfill(2)
        
        tFileName = os.path.basename(TORRENT_LIST_BACKUP)
        tLength = len(tFileName)
        tDirName = os.path.dirname(TORRENT_LIST_BACKUP)
        for file in os.listdir(tDirName):
            if file[:tLength] == tFileName and len(file) == tLength+11:  #说明是TORRENT_LIST_BACKUP的每天备份文件
                if file[tLength+1:tLength+8] != tLastMonth and file[tLength+1:tLength+8] != tThisMonth : #仅保留这个月和上月的备份文件
                    try :   os.remove(os.path.join(tDirName,file))
                    except: ErrorLog("failed to  file:"+os.path.join(tDirName,file))
        
        #把旧文件备份成昨天日期的文件,后缀+"."+gLastCheckDate
        tLastDayFileName = TORRENT_LIST_BACKUP+"."+gLastCheckDate
        if os.path.isfile(TORRENT_LIST_BACKUP) :
            if  os.path.isfile(tLastDayFileName) : os.remove(tLastDayFileName)
            os.rename(TORRENT_LIST_BACKUP,tLastDayFileName) 
            DebugLog("backup pt file:"+tLastDayFileName)
    else : LogClear(TORRENT_LIST_BACKUP)        

    try : 
        fo = open(TORRENT_LIST_BACKUP,"w")
    except: 
        ErrorLog("Error:open ptbackup file to write："+TORRENT_LIST_BACKUP)
        return False
        
    for i in range(len(gTorrentList)):
        tDateDataListStr = ""
        for j in range( len(gTorrentList[i].date_data) ):        
            tDateDataStr = gTorrentList[i].date_data[j]['date']+":" + str(gTorrentList[i].date_data[j]['data'])
            tDateDataListStr += tDateDataStr+','
        if tDateDataListStr[-1:] == ',' : tDateDataListStr = tDateDataListStr[:-1] #去掉最后一个','
        tStr  =     gTorrentList[i].client+'|'
        tStr +=     gTorrentList[i].HASH+'|'
        tStr +=     gTorrentList[i].name+'|'
        tStr +=     gTorrentList[i].rss_name+'|'
        tStr +=     gTorrentList[i].title+'|'
        tStr +=     gTorrentList[i].download_link+'|'
        tStr += str(gTorrentList[i].add_status)+'|'
        tStr +=     gTorrentList[i].douban_id+'|'
        tStr +=     gTorrentList[i].imdb_id+'|'
        tStr += str(gTorrentList[i].spider_status)+'|'
        tStr += str(gTorrentList[i].douban_status)+'|'
        tStr +=     gTorrentList[i].douban_score+'|'
        tStr +=     gTorrentList[i].imdb_score+'|'
        tStr +=     gTorrentList[i].douban_link+'|'
        tStr +=     gTorrentList[i].imdb_link+'|'
        tStr +=     gTorrentList[i].movie_name+'|'
        tStr +=     gTorrentList[i].foreign_name+'|'
        tStr +=     gTorrentList[i].other_names+'|'
        tStr += str(gTorrentList[i].type)+'|'
        tStr +=     gTorrentList[i].nation+'|'
        tStr +=     gTorrentList[i].director+'|'
        tStr +=     gTorrentList[i].actors+'|'
        tStr +=     gTorrentList[i].poster+'|'
        tStr += str(gTorrentList[i].episodes)+'|'
        tStr +=     gTorrentList[i].genre+'|'
        tStr +=     tDateDataListStr+'\n'
        # TODO  增加is_root_folder
        fo.write(tStr)
  
    fo.close()
    ExecLog("{} torrents writed:".format(len(gTorrentList)))
    return 1    
   
def check_torrents(mClient):
    """
    进行TR/QB的所有种子进行检查和分析，并更新列表
    1、检查DIRName是否存在，否则暂停种子
    2、NEWDAY下：比对所有文件，大小，错误，暂停种子
    3、QB下，检查标签设置
    4、更新种子信息列表（增加，删除，更新）
    5、NEWDAY：计算DATA，低于阈值的暂停种子
    
    返回值：-1:错误，0:无更新，1:有更新 ，用于指示是否需要备份文件
    """
    global gTorrentList
    
    tNumberOfAdded = tNumberOfDeleted = tNumberOfUpdated = 0

    #连接Client并获取TorrentList列表
    try:
        if mClient == "TR" :
            tr_client = transmissionrpc.Client(TR_LOGIN['host'], port=TR_LOGIN['port'],user=TR_LOGIN['username'],password=TR_LOGIN['password'])
        else :
            qb_client = qbittorrentapi.Client(host=QB_LOGIN['host_port'], username=QB_LOGIN['username'], password=QB_LOGIN['password'])            
            qb_client.auth_log_in()
        DebugLog("connect to  "+mClient)
    except Exception as err:
        print(err)
        ErrorLog("failed to connect to "+mClient)
        return -1

    #先把检查标志复位,并对待加入的种子进行加入
    for i in range( len(gTorrentList) ):
        if gTorrentList[i].client == mClient: gTorrentList[i].checked = 0
        if gTorrentList[i].client == mClient and gTorrentList[i].add_status == TO_BE_ADD: 
            gTorrentList[i].checked = 1
            try :
                if gTorrentList[i].client == "QB":
                    qb_client.torrents_add(urls=gTorrentList[i].download_link,paused=True)
                else:
                    tr_client.add_torrent(gTorrentList[i].download_link,paused=True)
            except Exception as err:
                print(err)
                ErrorLog("failed to add torrent:"+gTorrentList[i].title)
            else:
                tNumberOfAdded += 1
                ExecLog("add new torrent:"+gTorrentList[i].title)
                gTorrentList[i].add_status = TO_BE_START
                time.sleep(60)
                continue

    # 开始逐个获取torrent并检查
    if mClient == "QB":
        tTorrents = qb_client.torrents_info()            
    else:
        tTorrents = tr_client.get_torrents()
    for tOriginalTorrent in tTorrents: 
        
        tTorrent = Torrent(mClient,tOriginalTorrent)
        tIndex = get_torrent_index(mClient,tTorrent.hash)
        if tIndex == -1:
            ExecLog("add new torrent:"+tTorrent.name)
            #tTorrent.title = tTorrent.name #从客户端获取的新种子，title置为torrent.name
            gTorrentList.append(MyTorrent(tTorrent,None,None,STARTED))
            #tIndex = -1                   #指向刚加入的种子
            tNumberOfAdded += 1
            #gTorrentList[tIndex].spider_status = RETRY

        gTorrentList[tIndex].checked = 1
        gTorrentList[tIndex].torrent.torrent = tOriginalTorrent  #刷新种子信息

        #检查并设置标签
        if mClient == "QB":
            tTracker = gTorrentList[tIndex].tracker
            if tTracker.find("keepfrds") >= 0 :
                if gTorrentList[tIndex].tags != 'frds' : gTorrentList[tIndex].set_tags('frds')
            elif tTracker.find("m-team") >= 0 :
                if gTorrentList[tIndex].tags != 'mteam': gTorrentList[tIndex].set_tags('mteam')
            elif tTracker.find("hdsky") >= 0 :
                if gTorrentList[tIndex].tags != 'hdsky': gTorrentList[tIndex].set_tags('hdsky')
            elif tTracker == "" : pass
            else:
                if gTorrentList[tIndex].tags != 'other': gTorrentList[tIndex].set_tags('other')
            

        #检查文件
        if gTorrentList[tIndex].progress == 100 :
            if gTorrentList[tIndex].check_files(gIsNewDay) == False:
                ExecLog(gTorrentList[tIndex].error_string)
                gTorrentList[tIndex].stop()

        # mteam部分免费种，免费一天，但下载完成率很低
        if gTorrentList[tIndex].status != "STOP" and gTorrentList[tIndex].category == '下载' and gTorrentList[tIndex].progress <= 95:
            tStartTime = datetime.datetime.strptime(gTorrentList[tIndex].add_datetime,"%Y-%m-%d %H:%M:%S")
            tSeconds = (datetime.datetime.now()-tStartTime).total_seconds()
            if tSeconds >= 24*3600 : 
                gTorrentList[tIndex].stop()
                ExecLog(gTorrentList[tIndex].name+" have not done more than 1 day") 
                
        if gIsNewDay == True :   
            #新的一天，更新记录每天的上传量（绝对值）
            gTorrentList[tIndex].date_data.append({'date':gToday,'data':gTorrentList[tIndex].uploaded})
            if len(gTorrentList[tIndex].date_data) >= NUMBEROFDAYS+3: del gTorrentList[tIndex].date_data[0] #删除前面旧的数据
            #QB的下载类种子，如果上传量低于阀值，置类别为“低上传”
            if gTorrentList[tIndex].client == "QB" and  gTorrentList[tIndex].category == '下载':
                if gTorrentList[tIndex].is_low_upload(NUMBEROFDAYS,UPLOADTHRESHOLD) :
                    gTorrentList[tIndex].set_category("低上传")
                    ExecLog("low upload:"+gTorrentList[tIndex].title)
                    ExecLog("           {}|{}|{}".format(gTorrentList[tIndex].movie_name,gTorrentList[tIndex].douban_score,gTorrentList[tIndex].imdb_score))
                    # TODO 记录完整title
    
        #如果种子状态不是STARTED，启动它
        if gTorrentList[tIndex].add_status == TO_BE_START:
            if gTorrentList[tIndex].start_download():
                ExecLog("start   torrent:"+gTorrentList[tIndex].name)
                tNumberOfUpdated += 1
                gTorrentList[tIndex].add_status = STARTED
            else:
                ExecLog("failed to start_download:"+gTorrentList[tIndex].name)
                continue

        #如果种子spider_status不是OK
        if gTorrentList[tIndex].spider_status == RETRY:
            DebugLog("checkqb: begin spider movie info:"+gTorrentList[tIndex].name)
            tReturn = gTorrentList[tIndex].spider_movie_info()
            if tReturn == OK:
                tNumberOfUpdated += 1
                ExecLog("spider movieinf:"+gTorrentList[tIndex].name)
            elif tReturn == NOK:
                tNumberOfUpdated += 1
                ExecLog("failedto spider:"+gTorrentList[tIndex].name)
            else: pass

        #保存电影到TOBE
        if gTorrentList[tIndex].category == "save" : gTorrentList[tIndex].save_movie()
        
        if gTorrentList[tIndex].category == "转移" : gTorrentList[tIndex].move_to_tr(TR_LOGIN)
        
    #end for torrents 
    
    #最后，找出没有Checked标志的种子列表，进行删除操作。
    i = 0; tLength = len(gTorrentList)
    while i < len(gTorrentList) :
        if gTorrentList[i].checked == 0 and gTorrentList[i].client == mClient:
            tNumberOfDeleted += 1
            ExecLog("delete   torrent:"+gTorrentList[i].title)
            del gTorrentList[i] 
        else:
            i += 1                
 
    DebugLog("complete check_torrents  from "+mClient)
    if tNumberOfAdded > 0   : DebugLog(str(tNumberOfAdded).zfill(4)+" torrents added")
    if tNumberOfDeleted > 0 : DebugLog(str(tNumberOfDeleted).zfill(4)+" torrents deleted")
    if  tNumberOfAdded >= 1 or tNumberOfDeleted >= 1 or tNumberOfUpdated >= 1:
        return 1
    else :
        return 0
 
def tracker_data():
    """
    统计各站点的上传量
    """
    
    for i in range(len(TrackerDataList)):
        TrackerDataList[i]['date_data'].append( {'date':gToday,'data':0} )
        if len(TrackerDataList[i]['date_data']) >= 30: del TrackerDataList[i]['date_data'][0]

    for i in range(len(gTorrentList)):
        if   len(gTorrentList[i].date_data) == 0 :ErrorLog("date_data is null:"+gTorrentList[i].HASH);  continue
        elif len(gTorrentList[i].date_data) == 1 :tData = gTorrentList[i].date_data[0]['data']
        else                                    :tData = gTorrentList[i].date_data[-1]['data']-gTorrentList[i].date_data[-2]['data']
    
        Tracker = gTorrentList[i].tracker
        IsFind = False
        for j in range(len(TrackerDataList)):
            if Tracker.find(TrackerDataList[j]['keyword']) >= 0 : 
                TrackerDataList[j]['date_data'][-1]['data'] += tData
                IsFind = True ; break
        if IsFind == False: ErrorLog("unknown tracker:{} for torrent:{}:".format(Tracker,gTorrentList[i].name))

    TotalUpload = 0
    for i in range(len(TrackerDataList)):
        tUpload = TrackerDataList[i]['date_data'][-1]['data']; TotalUpload += tUpload
        ExecLog( "{} upload(G):{}".format((TrackerDataList[i]['name']).ljust(10),round(tUpload/(1024*1024*1024),3)) )
    ExecLog( "{} upload(G):{}".format("total".ljust(10), round(TotalUpload/(1024*1024*1024),3)) )
    ExecLog( "average upload radio :{}M/s".format( round(TotalUpload/(1024*1024*24*3600),2) ) )
        
    for i in range(len(TrackerDataList)):
        tDateData = TrackerDataList[i]['date_data']
        j=len(tDateData)-1
        NumberOfDays=0
        while j >= 0 :
            if tDateData[j]['data'] == 0 :NumberOfDays += 1
            else                         :break
            j -= 1
        ExecLog( "{} {} days no upload".format(TrackerDataList[i]['name'].ljust(10),str(NumberOfDays).zfill(2)) )
    
    write_tracker_backup()
    return 1
    
def read_tracker_backup():
    """
    读取TrackerList的备份文件，用于各个Tracker的上传数据
    """
    global TrackerDataList 
    
    if not os.path.isfile(TRACKER_LIST_BACKUP):
        ExecLog(TRACKER_LIST_BACKUP+" does not exist")
        return 0
        
    for line in open(TRACKER_LIST_BACKUP):
        Tracker,tDateDataStr = line.split('|',1)
        if tDateDataStr [-1:] == '\n' :  tDateDataStr = tDateDataStr[:-1]  #remove '\n'
        tDateDataList = tDateDataStr.split(',')
        DateData = []
        for i in range( len(tDateDataList) ):
            if tDateDataList[i] == "" :  break      #最后一个可能为空就退出循环
            tDate = (tDateDataList[i])[:10]
            tData = int( (tDateDataList[i])[11:] )
            DateData.append({'date':tDate,'data':tData})

        IsFind = False
        for i in range(len(TrackerDataList)):
            if Tracker == TrackerDataList[i]['name'] : 
                TrackerDataList[i]['date_data'] = DateData
                IsFind = True
        if IsFind == False: ErrorLog("unknown tracker in TrackerBackup:"+Tracker)
                
    #end for 
    return 1
        
def write_tracker_backup():

    if gIsNewDay == True :
        tThisMonth = gToday[0:7] ; tThisYear = gToday[0:4]
        if tThisMonth[5:7] == "01" : tLastMonth = str(int(tThisYear)-1)+"-"+"12"      
        else                       : tLastMonth = tThisYear+"-"+str(int(tThisMonth[5:7])-1).zfill(2)
        
        tFileName = os.path.basename(TRACKER_LIST_BACKUP)
        tLength = len(tFileName)
        tDirName = os.path.dirname(TRACKER_LIST_BACKUP)
        for file in os.listdir(tDirName):
            if file[:tLength] == tFileName and len(file) == tLength+11:  #说明是TorrentListBackup的每天备份文件
                if file[tLength+1:tLength+8] != tLastMonth and file[tLength+1:tLength+8] != tThisMonth : #仅保留这个月和上月的备份文件
                    try :   os.remove(os.path.join(tDirName,file))
                    except: ErrorLog("failed to delete file:"+os.path.join(tDirName,file))
        
        #把旧文件备份成昨天日期的文件,后缀+"."+gLastCheckDate
        tLastDayFileName = TRACKER_LIST_BACKUP+"."+gLastCheckDate
        if os.path.isfile(TRACKER_LIST_BACKUP) :
            if  os.path.isfile(tLastDayFileName) : os.remove(tLastDayFileName)
            os.rename(TRACKER_LIST_BACKUP,tLastDayFileName) 
    else :LogClear(TRACKER_LIST_BACKUP)        

    try   :  fo = open(TRACKER_LIST_BACKUP,"w")
    except:  ErrorLog("Error:open ptbackup file to write："+TRACKER_LIST_BACKUP); return -1

    for i in range(len(TrackerDataList)):
        tDateDataList = TrackerDataList[i]['date_data']
        tDateDataListStr = ""
        for j in range(len(tDateDataList)):        
            tDateDataStr = tDateDataList[j]['date']+":" + str(tDateDataList[j]['data'])
            tDateDataListStr += tDateDataStr+','
        if tDateDataListStr[-1:] == ',' : tDateDataListStr = tDateDataListStr[:-1] #去掉最后一个','
        tStr = TrackerDataList[i]['name'] + '|' + tDateDataListStr + '\n'
        fo.write(tStr)
             
    fo.close()
    ExecLog("success write tracklist")
    
    return 1

def in_ignore_list(SavedPath,DirName) :

    if SavedPath[-1:] == '/' : SavedPath = SavedPath[:-1]
    for i in range( len(gPTIgnoreList) ) :
        if (gPTIgnoreList[i])['Path'] == SavedPath and (gPTIgnoreList[i])['Name'] == DirName:  return True

    return False

def in_torrent_list(SavedPath,DirName):
    """
    判断SavedPath+DirName在不在TorrentList
    """
    for i in range( len(gTorrentList) ) :
        tSrcDirName = os.path.join(SavedPath,DirName)
        FirstFile = os.path.join(gTorrentList[i].save_path,gTorrentList[i].files[0]['name'])
        tDestFile = os.path.realpath(FirstFile)
        if tSrcDirName in tDestFile:
            #DebugLog(os.path.realpath(tSrcDirName))
            #DebugLog(os.path.realpath(tDestDirName))
            #DebugLog(gTorrentList[i].Name+"::"+gTorrentList[i].HASH)
            return True
    return False
#end def InTorrentList
def check_disk(tCheckDiskList):
    """
    对Path下的目录及文件逐个对比TorrentList，并进行标记。
    """

    tDirNameList = []   
    for DiskPath in tCheckDiskList:
        DebugLog("begin check:"+DiskPath)
        for file in os.listdir(DiskPath):        
            fullpathfile = os.path.join(DiskPath,file)
            if os.path.isdir(fullpathfile) or os.path.isfile(fullpathfile) :        
                #一些特殊文件夹忽略
                if file == 'lost+found' or file[0:6] == '.Trash' or file[0:4] == '0000' :
                    DebugLog ("ignore some dir:"+file)
                    continue 
            
                if in_ignore_list(DiskPath,file):
                    DebugLog ("in Ignore List:"+DiskPath+"::"+file)
                    continue
                
                #合集
                if os.path.isdir(fullpathfile) and len(file) >= 9 and re.match("[0-9][0-9][0-9][0-9]-[0-9][0-9][0-9][0-9]",file[:9]) :
                    for file2 in os.listdir(fullpathfile):
                        fullpathfile2 = os.path.join(fullpathfile,file2)
                        if os.path.isfile( fullpathfile2) : continue
                        if in_igore_list(fullpathfile,file2):
                            DebugLog("in Ignore List:"+fullpathfile2)
                            continue
                        if in_torrent_list(fullpathfile,file2): DebugLog(file2+":: find in torrent list")
                        else: ExecLog(file2+":: not find in torrent list"); tDirNameList.append({'DirPath':fullpathfile,'DirName':pathfile2})
                else:
                    if in_torrent_list(DiskPath,file) : DebugLog(file+"::find in torrent list:")
                    else :                            ExecLog(file+"::not find in torrent list:"); tDirNameList.append({'DirPath':DiskPath,'DirName':file})
            else :
                ExecLog("Error：not file or dir")
    return tDirNameList

def backup_torrents():
    """
    把QB和TR的torrents备份到相应目录
    """

    global QB_BACKUP_DIR
    global TR_BACKUP_DIR
    global QB_TORRENTS_BACKUP_DIR
    global TR_TORRENTS_BACKUP_DIR

    if QB_BACKUP_DIR[-1:] != '/' : QB_BACKUP_DIR = QB_BACKUP_DIR+'/'
    if TR_BACKUP_DIR[-1:] != '/' : TR_BACKUP_DIR = TR_BACKUP_DIR+'/'
    if QB_TORRENTS_BACKUP_DIR[-1:] != '/' : QB_TORRENTS_BACKUP_DIR = QB_TORRENTS_BACKUP_DIR+'/'
    if TR_TORRENTS_BACKUP_DIR[-1:] != '/' : TR_TORRENTS_BACKUP_DIR = TR_TORRENTS_BACKUP_DIR+'/'

    QBCopyCommand = "cp -n "+QB_BACKUP_DIR+"* "+QB_TORRENTS_BACKUP_DIR
    #ExecLog("exec:"+QBCopyCommand)
    if os.system(QBCopyCommand) == 0 : ExecLog ("success exec:"+QBCopyCommand)
    else : ExecLog("failed to exec:"+QBCopyCommand); return False

    TRCopyCommand1 = "cp -n "+TR_BACKUP_DIR+"torrents/* "+TR_TORRENTS_BACKUP_DIR
    #ExecLog("exec:"+TRCopyCommand1)
    if os.system(TRCopyCommand1) == 0 : ExecLog ("success exec:"+TRCopyCommand1)
    else : ExecLog("failed to exec:"+TRCopyCommand1); return False
    TRCopyCommand2 = "cp -n "+TR_BACKUP_DIR+"resume/* "+TR_TORRENTS_BACKUP_DIR
    #ExecLog("exec:"+TRCopyCommand2)
    if os.system(TRCopyCommand2) == 0 : ExecLog ("success exec:"+TRCopyCommand2)
    else : ExecLog("failed to exec:"+TRCopyCommand2); return False

def keep_torrents(tDiskPath):
    """
    输入:待进行保种的目录列表
    1、查找movies表，获取下载链接及hash
    2、如果下载链接不空，就取下载链接，否则通过hash值去种子备份目录寻找种子文件
    3、加入qb，设置分类为'转移',跳检，不创建子文件夹
    """
    
    try:
        tr_client = transmissionrpc.Client(TR_LOGIN['host'], port=TR_LOGIN['port'],user=TR_LOGIN['username'],password=TR_LOGIN['password'])
    except Exception as err:
        print(err)
        ErrorLog("failed to connect tr")
        return False

    tDirNameList = check_disk(tDiskPath)  #检查tDiskPath,获取未保种的目录列表
    for tDirName in tDirNameList:
        ExecLog("begin to keep torrent:"+tDirName['DirPath']+tDirName['DirName'])
        tMovie = movie.Movie(tDirName['DirPath'],tDirName['DirName'])
        if tMovie.CheckDirName() == 0 :
            ExecLog("failed to checkdirname:"+tMovie.DirName)
            continue
        if not tMovie.get_torrent(): ExecLog("can't get torrent:"+self.DirName); continue
        try:
            if self.download_link != "": 
                tr_torrent = tr_client.add_torrent(self.download_link,download_dir=TR_KEEP_DIR,paused=True)
            elif self.torrent_file != "":
                tr_torrent = tr_client.add_torrent(torrent=self.torrent_file,download_dir=TR_KEEP_DIR,paused=True)
        except Exception as err:
            Print(err)
            ErrorLog("failed to add torrent:"+TorrentFile+"::"+DownloadLink)
            continue
        else:
            ExecLog("success add torrent to tr")
        
        tLink = os.path.join(TR_KEEP_DIR,tr_torrent.name) 
        tFullPathDirName = os.path.join(tDirName['DirPath']+tDirName['DirName'])
        if os.path.exists(tLink) : os.remove(tLink)
        try:    
            os.symlink(tFullPathDirName,tLink)
        except:
            ErrorLog("failed create link:ln -s "+tFullPathDirName+" "+tLink)
        else: ExecLog("create link: ln -s "+tFullPathDirName+" "+tLink)

    #把新加入的种子加入列表
    check_torrents("TR")

def request_free(mSiteName="",mTimeInterval=-1):

    DebugLog("request free:{}::{}".format(mSiteName,mTimeInterval))
    tTorrentList = []
    for site in NexusPage.site_list:
        if mSiteName.lower() == site['name'].lower() or (site['time_interval'] != 0 and mTimeInterval % site['time_interval'] == 0): 
            tSite = site
        else:
            continue
        DebugLog("begin request free:"+tSite['name'])
        tPage = NexusPage(tSite)
        if not tPage.request_free_page():
            #ExecLog(tPage.error_string)
            continue

        for tTask in tPage.find_free_torrents():
            DebugLog("{}|{}|{}|{}".format(tTask[0],tTask[1],tTask[2],tTask[3]))
            TorrentID = tTask[0]
            Title = tTask[1]
            Details = tTask[2]
            DownloadLink = tTask[3]

            if tSite['name'] == 'HDSky':
                if Title.find("265") >= 0 and Title.find("HDS") >= 0  and Title.find("HDSWEB") == -1 and Title.find("HDSPad") == -1 and Title.find("HDSTV") == -1:
                    DebugLog("find a 265 HDS torrent:"+Title)
                else: 
                    DebugLog("not 265 HDS torrent,ignore it"+Title)
                    continue

            tRSS = RSS("",tPage.site['name'],DownloadLink,Title)
            if tRSS.select():   #rss记录已经存在
                if tRSS.downloaded == 1: DebugLog("torrentID have been downloaded:"+TorrentID+"::"+Title); continue
                tInfo = Info(tRSS.douban_id,tRSS.imdb_id)
                tTorrent = MyTorrent(rss=tRSS,info=tInfo)
            else:
                ExecLog("failed to find rss from torrentid:"+tRSS.rss_name+"::"+tRSS.torrent_id)
                #if not tPage.request_detail_page(TorrentID):
                #    ExecLog("failed to request detail")
                #    continue
                tTorrentInfo = TorrentInfo(download_link=tRSS.download_link)
                if not tTorrentInfo.get_info():
                    ExecLog("failed to get torrent info from :"+tRSS.download_link)
                    continue
                tRSS.HASH = tTorrentInfo.hash
                if not tRSS.insert():
                    ExecLog("failed to insert rss:{}|{}|{}".format(tRSS.HASH,tRSS.name,tRSS.title))
                    continue
                
                DebugLog("get a torrent from link:{}|{}".format(tTorrentInfo.hash,tTorrentInfo.name))
                tTorrent= MyTorrent(rss=tRSS)

            if get_torrent_index("QB",tTorrent.HASH) >= 0:
                ExecLog("torrent exists in list:"+tRSS.title)
                continue
            ExecLog("free    torrent:"+Title)
            tTorrentList.append(MyTorrent(rss=tRSS,info=tInfo))
    return tTorrentList

def request_rss(mRSSName="",mTimeInterval=-2):
    
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.82 Safari/537.36'}

    DebugLog("request rss:{}::{}".format(mRSSName,mTimeInterval))
    tTorrentList = []
    for i in range(len(RSS_LIST)):
        if mRSSName.lower() == RSS_LIST[i]['name'].lower() or\
                (RSS_LIST[i]['time_interval'] != 0 and (mTimeInterval % RSS_LIST[i]['time_interval']) == 0) :
            RSSName  = RSS_LIST[i]['name']
            WaitFree = RSS_LIST[i]['wait_free']
            url      = RSS_LIST[i]['url']
        else: continue

        DebugLog("==========begin {}==============".format(RSSName.ljust(10,' ')))
        parser = feedparser.parse(url)
        for tEntry in parser.entries:
            Title = tEntry.title
            HASH  = tEntry.id
            Detail = tEntry.links[0].href
            DownloadLink = tEntry.links[1].href
            tSummary = ""
            try:
                tSummary = BeautifulSoup(tEntry.summary,'lxml').get_text()
            except Exception as err:
                pass
            tInfo = Info()
            tInfo.get_from_summary(tSummary)

            if RSSName == 'HDSky' and Title.find("x265") == -1: DebugLog("hdsky not x265,ignore it"+Title); continue
            
            Title = Title.replace('|','')
            tRSS = RSS(HASH,RSSName,DownloadLink,Title,tInfo.douban_id,tInfo.imdb_id)
            if tRSS.select():
                DebugLog("old rss:"+tRSS.title)
                continue
            if not tRSS.insert():  #记录插入rss数据库
                ExecLog("failed to insert into rss:{}|{}".format(RSSName,HASH))
                continue
            tTorrent = MyTorrent(None,tRSS,tInfo,TO_BE_ADD)

            if not WaitFree: 
                ExecLog("new rss tobeadd:"+tTorrent.title)
                ExecLog("               :{}/{}|{}/{}|{}|{}|{}|{}".format(tInfo.douban_id,tInfo.imdb_id,tInfo.douban_score,tInfo.imdb_score,tInfo.type,tInfo.nation,tInfo.movie_name,tInfo.director))
                tTorrentList.append(tTorrent)
            else:
                DebugLog("               :{}/{}|{}/{}|{}|{}|{}|{}".format(tInfo.douban_id,tInfo.imdb_id,tInfo.douban_score,tInfo.imdb_score,tInfo.type,tInfo.nation,tInfo.movie_name,tInfo.director))

        #end for Items
    return tTorrentList
        
def restart_qb():

    try:
        qb_client = qbittorrentapi.Client(host=QB_LOGIN['host_port'], username=QB_LOGIN['username'], password=QB_LOGIN['password'])
        qb_client.auth_log_in()
        #qb_client.torrents.pause.all()
        qb_client.app_shutdown()
    except:
        ExecLog("failed to stop QB")
        return False
    else:
        ExecLog("success to stop QB")
        
    time.sleep(600)
    if os.system("/usr/bin/qbittorrent &") == 0 : ExecLog ("success to start qb")
    else : ExecLog("failed to start qb"); return False
    
    """
    time.sleep(10)
    try:
        qb_client = qbittorrentapi.Client(host=QB_LOGIN['host_port'], username=QB_LOGIN['username'], password=QB_LOGIN['password'])
        qb_client.auth_log_in()
        torrents = qb_client.torrents.info()
    except:
        debugLog("failed to resume qb torrents")
        return False
        
    for torrent in torrents:
        tIndex = FindTorrent(QB,torrent.hash)
        if tIndex == -1 : ExecLog("not find in torrentlist:"+torrent.name); continue
        if gTorrentList[tIndex].Status == "GOING":  
            try: torrent.resume()
            except: ExecLog("failed to resume:"+torrent.name)
    """
    return True
        
def set_spider_id(RequestList):

    if len(RequestList) != 2: return "invalid number of arguments"

    ExecLog("begin set {} {}".format(tName,tID))
    tName = RequestList[0]
    tID   = RequestList[1]
    tIndexList = []
    for i in range(len(gTorrentList)):
        if tName in gTorrentList[i].title or tName in gTorrentList[i].name:
            ExecLog("find match torrent:"+gTorrentList[i].name)
            tIndexList.append(i)
    if len(tIndexList) == 0: return "not find torrent"
    if len(tIndexList) >= 2: return "2+ torrent found"

    if tID[:2] == 'tt': gTorrentList[i].imdb_id = tID
    else              : gTorrentList[i].douban_id = tID

    gTorrentList[i].spider_status = RETRY
    gTorrentList[i].douban_Status = RETRY
    return "success set {} {}".format(gTorrentList[i].name,tID)

def handle_task(Request):
    ExecLog("accept request:"+Request)
    RequestList = Request.split()
    Task = RequestList[0].lower(); del RequestList[0]
    if   Task == 'checkdisk': 
        if len(RequestList) > 0 : check_disk(RequestList)
        else                    : check_disk(CHECK_DISK_LIST)
    elif Task == 'rss'      : 
        if len(RequestList) > 0 : 
            for RSSName in RequestList: 
                for tTorrent in request_rss(RSSName,-1):
                    gTorrentList.append(tTorrent)
    elif Task == 'free'     :
        if len(RequestList) > 0 : 
            for tTorrent in request_free(RequestList[0]):
                gTorrentList.append(tTorrent)
        else                    : 
            for tTorrent in request_free('MTeam'):
                gTorrentList.append(tTorrent)
    elif Task == 'checkqb'      : 
        if check_torrents("QB") > 0: write_pt_backup()
    elif Task == 'checktr'      : 
        if check_torrents("TR") > 0: write_pt_backup()
    elif Task == 'backuptorrent': backup_torrents()
    elif Task == 'keep'         : keep_torrents( check_disk(RequestList) )
    elif Task == 'spider'       : return set_spider_id(RequestList)
    elif Task == 'view'         : 
        if len(RequestList) == 1 and RequestList[0] == 'all':
            return str(update_viewed(False))
        else:
            return str(update_viewed(True))
    else                        : ExecLog("unknown request task:"+Task) ; return "unknown request task"     
    
    return "completed"

if __name__ == '__main__' :

    tCurrentTime = datetime.datetime.now()
    gToday = tCurrentTime.strftime('%Y-%m-%d')
    
    ExecLog("Begin ReadPTBackup from "+TORRENT_LIST_BACKUP)
    if read_pt_backup() == True:
        ExecLog("success ReadPTBackup. set gLastCheckDate="+gLastCheckDate)

    #初始化建立gTorrentList
    if  check_torrents("QB") == -1: exit()
    if  check_torrents("TR") == -1: exit()
    write_pt_backup()
    
    if read_tracker_backup() == 1:  ExecLog("success ReadTrackerBackup:"+TRACKER_LIST_BACKUP)

    #if ReadIgnoreList() == 1:
    #    ExecLog("success ReadIgnoreList:")
        #for tFile in gPTIgnoreList : DebugLog(tFile['Path']+"::"+tFile['name'])      
    #if ReadTrackerBackup() == 1:  ExecLog("success ReadTrackerBackup:"+TRACKER_LIST_BACKUP)
    #if ReadRSSTorrentBackup() > 0: ExecLog("success read rss torrent backup:"+RSSTorrentBackupFile)
    
    socket.setdefaulttimeout(60)
    try:
        Socket = socket.socket()
        HOST = socket.gethostname()
        Socket.bind((HOST,PTPORT))
        Socket.listen(5)
        Socket.settimeout(60)
    except Exception as err:
        Print("fail to make socket")
        Print(err)
        exit()
   
    LoopTimes = 0
    while True:
        LoopTimes += 1
        Print("loop times :"+str(LoopTimes%120) )
        tCurrentTime = datetime.datetime.now()
        gToday = tCurrentTime.strftime('%Y-%m-%d')
        if gToday != gLastCheckDate :      gIsNewDay = True
        else:                              gIsNewDay = False

        #RSS和FREE种子订阅及查找
        for tTorrent in request_rss("",LoopTimes):
            gTorrentList.append(tTorrent)
        for tTorrent in request_free("",LoopTimes):
            gTorrentList.append(tTorrent)
            
        if gIsNewDay : 
            check_torrents("QB")
            check_torrents("TR")
            write_pt_backup()
            tracker_data()                   #tracker_data执行要在check_torrents()之后，这样才有新的记录
            backup_torrents()
            check_disk(CHECK_DISK_LIST)
            #一月备份一次qb，tr,data
            if gToday[8:10] == '01' : os.system("/root/backup.sh"); ExecLog("exec:/root/backup.sh")
        else:
            if LoopTimes % 5 == 0 : 
                if check_torrents("QB") > 0 : write_pt_backup()
        
        gLastCheckDate = tCurrentTime.strftime("%Y-%m-%d")
        DebugLog("update gLastCheckDate="+gLastCheckDate)        

        #检查一下内存占用
        tMem = psutil.virtual_memory()
        DebugLog("memory percent used:"+str(tMem.percent))
        if tMem.percent >= 92: ExecLog("memory percent used:"+str(tMem.percent)); restart_qb()
                

        #监听Client是否有任务请求
        #Print("begin accept")
        try:
            Connect,Address = Socket.accept()
            Print(Address)
        except socket.timeout:
            #Print("accept timeout")
            continue
        except Exception as err:
            ErrorLog("accept error:")
            Print(err)
            continue

        #接受请求
        Print("begin recv") 
        try:
            data = Connect.recv(1024)
        except socket.timeout:
            Print("recv timeout")
            continue
        except Exception as err:
            ErrorLog("recv error")
            Print(err)
        else:
            Request = str(data, encoding="utf-8")
            Print("recv success:"+Request)

        Reply = handle_task(Request)
        Print("begin send")
        try:
            Connect.send( bytes(Reply,encoding="utf-8") )
        except socket.timeout:
            Print("send timeout")
            continue
        except Exception as err:
            Print(err)
            continue
        else:
            Print("send success:"+Reply)

        Connect.close()
