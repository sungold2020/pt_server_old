#!/usr/bin/python3
# coding=utf-8
import datetime
import time
import os
import requests
import feedparser
import re
import psutil

import movie
from rss import *
from info import Info
from torrent import Torrent
from mytorrent import *
from log import *
from ptsite import *
#from torrent_info import TorrentInfo
from client import PTClient
from client import get_hash


#连续NUMBEROFDAYS上传低于UPLOADTHRESHOLD，并且类别不属于'保种'的种子，会自动停止。
NUMBEROFDAYS = 2                           #连续多少天低于阈值
UPLOADTHRESHOLD = 0.03                    #阈值，上传/种子大小的比例

TORRENT_LIST_BACKUP = "data/pt.txt"  #种子信息备份目录（重要的是每天的上传量）
TRACKER_LIST_BACKUP = "data/tracker.txt"               
IGNORE_FILE = "data/ignore.txt"

TR_KEEP_DIR='/media/root/BT/keep/'   #TR种子缺省保存路径

class Torrents:
    def __init__(self):
        self.torrent_list = []
        self.tracker_data_list = [
                {'name':'FRDS'     ,'keyword':'frds'     ,'date_data':[]},
                {'name':'MTeam'    ,'keyword':'m-team'   ,'date_data':[]},
                {'name':'HDHome'   ,'keyword':'hdhome'   ,'date_data':[]},
                {'name':'BeiTai'   ,'keyword':'beitai'   ,'date_data':[]},
                {'name':'JoyHD'    ,'keyword':'joyhd'    ,'date_data':[]},
                {'name':'SoulVoice','keyword':'soulvoice','date_data':[]},
                {'name':'PTHome'   ,'keyword':'pthome'   ,'date_data':[]},
                {'name':'LeagueHD' ,'keyword':'leaguehd' ,'date_data':[]},
                {'name':'HDArea'   ,'keyword':'hdarea'   ,'date_data':[]},
                {'name':'PTSBao'   ,'keyword':'ptsbao'   ,'date_data':[]},
                {'name':'AVGV'     ,'keyword':'avgv'     ,'date_data':[]},
                {'name':'HDSky'    ,'keyword':'hdsky'    ,'date_data':[]}]
        self.last_check_date = "1970-01-01"
        
        #读取IGNORE_FILE
        self.ignore_list = []
        if os.path.isfile(IGNORE_FILE):
            for line in open(IGNORE_FILE):
                Path,Name = line.split('|',1)
                Path = Path.strip(); Name = Name.strip()
                if Name[-1:] == '\n' : Name = Name[:-1]
                self.ignore_list.append({'Path':Path,'Name':Name})
            ExecLog("read ignore from "+IGNORE_FILE)
        else :
            ExecLog(IGNORE_FILE+" does not exist")
        
        if self.read_pt_backup():
            ExecLog("read pt backup from :"+TORRENT_LIST_BACKUP)
            ExecLog("last_check_date = "+self.last_check_date)
        if self.read_tracker_backup():
            ExecLog("read tracker backup from :"+TRACKER_LIST_BACKUP)
        
    def get_torrent_index(self,mClient,mHASH):
        for i in range(len(self.torrent_list)) :
            if self.torrent_list[i].client == mClient and (mHASH == self.torrent_list[i].hash or mHASH == self.torrent_list[i].HASH): return i
        return -1   

    def add_torrent(self,mTorrent):
        self.torrent_list.append(mTorrent)
        self.write_pt_backup()

    def del_torrent(self,mClient,mHASH):
        for i in range(len(self.torrent_list)):
            if self.torrent_list[i].get_hash() == mHASH and self.torrent_list[i].client == mClient: 
                del self.torrent_list[i]
                self.write_pt_backup()
                return True
        return False

    def read_pt_backup(self):
        """
        读取备份目录下的pt.txt，用于恢复种子记录数据，仅当初始化启动时调用
        """
        
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

            tBasicTorrent = Torrent(Client,None)
            tBasicTorrent.date_data = DateData

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

            self.torrent_list.append(MyTorrent(tBasicTorrent,tRSS,tInfo,int(AddStatusStr)))  #init, can't use add_torrent
        #end for 
        self.last_check_date = tDate
        return 1

    def write_pt_backup(self):
        """
        把当前RSS列表写入备份文件
        """
        tToday = datetime.datetime.now().strftime('%Y-%m-%d')
        if tToday != self.last_check_date: tIsNewDay = True
        else                             : tIsNewDay = False        
        if tIsNewDay == True :
            DebugLog("new day is :"+tToday)
            tThisMonth = tToday[0:7] ; tThisYear = tToday[0:4]
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
            tLastDayFileName = TORRENT_LIST_BACKUP+"."+self.last_check_date
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
            
        for i in range(len(self.torrent_list)):
            tDateDataListStr = ""
            for j in range( len(self.torrent_list[i].date_data) ):        
                tDateDataStr = self.torrent_list[i].date_data[j]['date']+":" + str(self.torrent_list[i].date_data[j]['data'])
                tDateDataListStr += tDateDataStr+','
            if tDateDataListStr[-1:] == ',' : tDateDataListStr = tDateDataListStr[:-1] #去掉最后一个','
            tStr  =     self.torrent_list[i].client+'|'
            tStr +=     self.torrent_list[i].get_hash()+'|'
            tStr +=     self.torrent_list[i].name+'|'
            tStr +=     self.torrent_list[i].rss_name+'|'
            tStr +=     self.torrent_list[i].title+'|'
            tStr +=     self.torrent_list[i].download_link+'|'
            tStr += str(self.torrent_list[i].add_status)+'|'
            tStr +=     self.torrent_list[i].douban_id+'|'
            tStr +=     self.torrent_list[i].imdb_id+'|'
            tStr += str(self.torrent_list[i].spider_status)+'|'
            tStr += str(self.torrent_list[i].douban_status)+'|'
            tStr +=     self.torrent_list[i].douban_score+'|'
            tStr +=     self.torrent_list[i].imdb_score+'|'
            tStr +=     self.torrent_list[i].douban_link+'|'
            tStr +=     self.torrent_list[i].imdb_link+'|'
            tStr +=     self.torrent_list[i].movie_name+'|'
            tStr +=     self.torrent_list[i].foreign_name+'|'
            tStr +=     self.torrent_list[i].other_names+'|'
            tStr += str(self.torrent_list[i].type)+'|'
            tStr +=     self.torrent_list[i].nation+'|'
            tStr +=     self.torrent_list[i].director+'|'
            tStr +=     self.torrent_list[i].actors+'|'
            tStr +=     self.torrent_list[i].poster+'|'
            tStr += str(self.torrent_list[i].episodes)+'|'
            tStr +=     self.torrent_list[i].genre+'|'
            tStr +=     tDateDataListStr+'\n'
            fo.write(tStr)
      
        fo.close()
        ExecLog("{} torrents writed:".format(len(self.torrent_list)))
        return 1    
       
    def check_torrents(self,mClient):
        """
        进行TR/QB的所有种子进行检查和分析，并更新列表
        1、检查DIRName是否存在，否则暂停种子
        2、NEWDAY下：比对所有文件，大小，错误，暂停种子
        3、QB下，检查标签设置
        4、更新种子信息列表（增加，删除，更新）
        5、NEWDAY：计算DATA，低于阈值的暂停种子
        
        返回值：-1:错误，0:无更新，1:有更新 ，用于指示是否需要备份文件
        """

        tNumberOfAdded = tNumberOfDeleted = tNumberOfUpdated = 0
        tToday = datetime.datetime.now().strftime('%Y-%m-%d')
        if tToday != self.last_check_date: tIsNewDay = True
        else                             : tIsNewDay = False   
        #连接Client并获取TorrentList列表
        tPTClient = PTClient(mClient)
        if not tPTClient.connect():
            ErrorLog("failed to connect to "+mClient)
            return -1

        #先把检查标志复位,并对待加入的种子进行加入
        for i in range( len(self.torrent_list) ):
            if self.torrent_list[i].client == mClient: self.torrent_list[i].checked = 0
            if self.torrent_list[i].client == mClient and self.torrent_list[i].add_status == TO_BE_ADD: 
                self.torrent_list[i].checked = 1
                if tPTClient.add_torrent(download_link=self.torrent_list[i].download_link,is_paused=True):
                    tNumberOfAdded += 1
                    ExecLog("add new torrent:"+self.torrent_list[i].title)
                    self.torrent_list[i].add_status = TO_BE_START
                    #time.sleep(60)
                else:
                    ErrorLog("failed to add torrent:"+self.torrent_list[i].title)

        # 开始逐个获取torrent并检查
        for tTorrent in tPTClient.get_all_torrents(): 
            tIndex = self.get_torrent_index(mClient,tTorrent.hash)
            if tIndex == -1:
                ExecLog("findnew torrent:"+tTorrent.name)
                self.add_torrent(MyTorrent(tTorrent,None,None,STARTED))
                #tIndex = -1                   #指向刚加入的种子
                tNumberOfAdded += 1
                #self.torrent_list[tIndex].spider_status = RETRY
            self.torrent_list[tIndex].checked = 1
            self.torrent_list[tIndex].torrent.torrent = tTorrent.torrent  #刷新种子信息

            #检查并设置标签
            if mClient == "QB":
                tTracker = self.torrent_list[tIndex].tracker
                if tTracker.find("keepfrds") >= 0 :
                    if self.torrent_list[tIndex].tags != 'frds' : self.torrent_list[tIndex].set_tags('frds')
                elif tTracker.find("m-team") >= 0 :
                    if self.torrent_list[tIndex].tags != 'mteam': self.torrent_list[tIndex].set_tags('mteam')
                elif tTracker.find("hdsky") >= 0 :
                    if self.torrent_list[tIndex].tags != 'hdsky': self.torrent_list[tIndex].set_tags('hdsky')
                elif tTracker == "" : pass
                else:
                    if self.torrent_list[tIndex].tags != 'other': self.torrent_list[tIndex].set_tags('other')
                
            #检查文件
            if self.torrent_list[tIndex].progress == 100 :
                if self.torrent_list[tIndex].check_files(tIsNewDay) == False:
                    ExecLog(self.torrent_list[tIndex].torrent.error_string)
                    self.torrent_list[tIndex].stop()

            # mteam部分免费种，免费一天，但下载完成率很低
            if self.torrent_list[tIndex].status != "STOP" and self.torrent_list[tIndex].category == '下载' and self.torrent_list[tIndex].progress <= 95:
                tStartTime = datetime.datetime.strptime(self.torrent_list[tIndex].add_datetime,"%Y-%m-%d %H:%M:%S")
                tSeconds = (datetime.datetime.now()-tStartTime).total_seconds()
                if tSeconds >= 24*3600 : 
                    self.torrent_list[tIndex].stop()
                    ExecLog(self.torrent_list[tIndex].name+" have not done more than 1 day") 
                            
            #如果种子状态不是STARTED，启动它
            if self.torrent_list[tIndex].add_status == TO_BE_START and self.torrent_list[tIndex].status == "STOP":
                if self.torrent_list[tIndex].start_download():
                    ExecLog("start   torrent:"+self.torrent_list[tIndex].name)
                    tNumberOfUpdated += 1
                    self.torrent_list[tIndex].add_status = STARTED
                else:
                    ExecLog("failed to start_download:"+self.torrent_list[tIndex].name)
                    continue

            #如果种子spider_status不是OK
            if self.torrent_list[tIndex].spider_status == RETRY:
                DebugLog("checkqb: begin spider movie info:"+self.torrent_list[tIndex].name)
                tReturn = self.torrent_list[tIndex].spider_movie_info()
                if tReturn == OK:
                    tNumberOfUpdated += 1
                    ExecLog("spider movieinf:"+self.torrent_list[tIndex].name)
                elif tReturn == NOK:
                    tNumberOfUpdated += 1
                    ExecLog("failedto spider:"+self.torrent_list[tIndex].name)
                else: pass

            if self.torrent_list[tIndex].category == "save" : self.torrent_list[tIndex].save_movie()        
            if self.torrent_list[tIndex].category == "转移" : self.torrent_list[tIndex].move_to_tr(TR_LOGIN)        
        #end for torrents 
        
        #最后，找出没有Checked标志的种子列表，进行删除操作。
        i = 0; tLength = len(self.torrent_list)
        while i < len(self.torrent_list) :
            if self.torrent_list[i].checked == 0 and self.torrent_list[i].client == mClient:
                tNumberOfDeleted += 1
                ExecLog("delete  torrent:"+self.torrent_list[i].title)
                #del self.torrent_list[i] 
                self.del_torrent(self.torrent_list[i].client,self.torrent_list[i].hash)
            i += 1                
     
        DebugLog("complete check_torrents  from "+mClient)
        if tNumberOfAdded > 0   : DebugLog(str(tNumberOfAdded).zfill(4)+" torrents added")
        if tNumberOfDeleted > 0 : DebugLog(str(tNumberOfDeleted).zfill(4)+" torrents deleted")
        if  tNumberOfAdded >= 1 or tNumberOfDeleted >= 1 or tNumberOfUpdated >= 1: return 1
        else                                                                     : return 0
        
    def count_upload(self,mClient):
        """每天调用一次，进行统计上传量"""
        tToday = datetime.datetime.now().strftime('%Y-%m-%d')
        tPTClient = PTClient(mClient)
        if not tPTClient.connect(): 
            ExecLog("failed to connect "+mClient)
            return False
            
        for tTorrent in tPTClient.get_all_torrents():
            tIndex = self.get_torrent_index(mClient,tTorrent.hash)
            if tIndex < 0 : continue
            
            #新的一天，更新记录每天的上传量（绝对值）
            self.torrent_list[tIndex].date_data.append({'date':tToday,'data':self.torrent_list[tIndex].uploaded})
            if len(self.torrent_list[tIndex].date_data) >= NUMBEROFDAYS+3: del self.torrent_list[tIndex].date_data[0] #删除前面旧的数据
            
            #QB的下载类种子，如果上传量低于阀值，置类别为“低上传”
            if self.torrent_list[tIndex].client == "QB" and  self.torrent_list[tIndex].category == '下载':
                if self.torrent_list[tIndex].is_low_upload(NUMBEROFDAYS,UPLOADTHRESHOLD) :
                    self.torrent_list[tIndex].set_category("低上传")
                    ExecLog("low upload:"+self.torrent_list[tIndex].title)
                    ExecLog("           {}|{}|{}".format(self.torrent_list[tIndex].movie_name,self.torrent_list[tIndex].douban_score,self.torrent_list[tIndex].imdb_score))
                    # TODO 记录完整title
                    
    def tracker_data(self):
        """
        统计各站点的上传量
        """
        
        tToday = datetime.datetime.now().strftime('%Y-%m-%d')
        for i in range(len(self.tracker_data_list)):
            self.tracker_data_list[i]['date_data'].append( {'date':tToday,'data':0} )
            if len(self.tracker_data_list[i]['date_data']) >= 30: del self.tracker_data_list[i]['date_data'][0]

        for i in range(len(self.torrent_list)):
            if   len(self.torrent_list[i].date_data) == 0 :ErrorLog("date_data is null:"+self.torrent_list[i].HASH);  continue
            elif len(self.torrent_list[i].date_data) == 1 :tData = self.torrent_list[i].date_data[0]['data']
            else                                     :tData = self.torrent_list[i].date_data[-1]['data']-self.torrent_list[i].date_data[-2]['data']
        
            Tracker = self.torrent_list[i].tracker
            IsFind = False
            for j in range(len(self.tracker_data_list)):
                if Tracker.find(self.tracker_data_list[j]['keyword']) >= 0 : 
                    self.tracker_data_list[j]['date_data'][-1]['data'] += tData
                    IsFind = True ; break
            if IsFind == False: ErrorLog("unknown tracker:{} for torrent:{}:".format(Tracker,self.torrent_list[i].name))

        TotalUpload = 0
        for i in range(len(self.tracker_data_list)):
            tUpload = self.tracker_data_list[i]['date_data'][-1]['data']; TotalUpload += tUpload
            ExecLog( "{} upload(G):{}".format((self.tracker_data_list[i]['name']).ljust(10),round(tUpload/(1024*1024*1024),3)) )
        ExecLog( "{} upload(G):{}".format("total".ljust(10), round(TotalUpload/(1024*1024*1024),3)) )
        ExecLog( "average upload radio :{}M/s".format( round(TotalUpload/(1024*1024*24*3600),2) ) )
            
        for i in range(len(self.tracker_data_list)):
            tDateData = self.tracker_data_list[i]['date_data']
            j=len(tDateData)-1
            NumberOfDays=0
            while j >= 0 :
                if tDateData[j]['data'] == 0 : NumberOfDays += 1
                else                         : break
                j -= 1
            ExecLog( "{} {} days no upload".format(self.tracker_data_list[i]['name'].ljust(10),str(NumberOfDays).zfill(2)) )
        
        self.write_tracker_backup()
        return 1
        
    def read_tracker_backup(self):
        """
        读取TrackerList的备份文件，用于各个Tracker的上传数据
        """ 
        
        if not os.path.isfile(TRACKER_LIST_BACKUP):
            ExecLog(TRACKER_LIST_BACKUP+" does not exist")
            return False
            
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
            for i in range(len(self.tracker_data_list)):
                if Tracker == self.tracker_data_list[i]['name'] : 
                    self.tracker_data_list[i]['date_data'] = DateData
                    IsFind = True
            if IsFind == False: ErrorLog("unknown tracker in TrackerBackup:"+Tracker)               
        #end for 
        return True
            
    def write_tracker_backup(self):
        tToday = datetime.datetime.now().strftime('%Y-%m-%d')
        if tToday != self.last_check_date: tIsNewDay = True
        else                             : tIsNewDay = False
        if tIsNewDay == True :
            tThisMonth = tToday[0:7] ; tThisYear = tToday[0:4]
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
            tLastDayFileName = TRACKER_LIST_BACKUP+"."+self.last_check_date
            if os.path.isfile(TRACKER_LIST_BACKUP) :
                if  os.path.isfile(tLastDayFileName) : os.remove(tLastDayFileName)
                os.rename(TRACKER_LIST_BACKUP,tLastDayFileName) 
        else :LogClear(TRACKER_LIST_BACKUP)        

        try   :  fo = open(TRACKER_LIST_BACKUP,"w")
        except:  ErrorLog("Error:open ptbackup file to write："+TRACKER_LIST_BACKUP); return -1

        for i in range(len(self.tracker_data_list)):
            tDateDataList = self.tracker_data_list[i]['date_data']
            tDateDataListStr = ""
            for j in range(len(tDateDataList)):        
                tDateDataStr = tDateDataList[j]['date']+":" + str(tDateDataList[j]['data'])
                tDateDataListStr += tDateDataStr+','
            if tDateDataListStr[-1:] == ',' : tDateDataListStr = tDateDataListStr[:-1] #去掉最后一个','
            tStr = self.tracker_data_list[i]['name'] + '|' + tDateDataListStr + '\n'
            fo.write(tStr)
                 
        fo.close()
        ExecLog("success write tracklist")
        return 1

    def in_torrent_list(self,SavedPath,DirName):
        """
        判断SavedPath+DirName在不在TorrentList
        """
        for i in range( len(self.torrent_list) ) :
            tSrcDirName = os.path.join(SavedPath,DirName)
            for tFile in self.torrent_list[i].files:
                FirstFile = os.path.join(self.torrent_list[i].save_path,tFile['name'])
                tDestFile = os.path.realpath(FirstFile)
                if tSrcDirName in tDestFile:
                    #DebugLog(os.path.realpath(tSrcDirName))
                    #DebugLog(os.path.realpath(tDestDirName))
                    #DebugLog(self.torrent_list[i].Name+"::"+self.torrent_list[i].HASH)
                    return True
        return False

    def check_disk(self,tCheckDiskList):
        """
        对Path下的目录及文件逐个对比TorrentList，并进行标记。
        """

        def in_ignore_list(SavedPath,DirName) :
            if SavedPath[-1:] == '/' : SavedPath = SavedPath[:-1]
            for i in range( len(self.ignore_list) ) :
                if (self.ignore_list[i])['Path'] == SavedPath and (self.ignore_list[i])['Name'] == DirName:  return True
            return False
            
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
                            if in_ignore_list(fullpathfile,file2):
                                DebugLog("in Ignore List:"+fullpathfile2)
                                continue
                            if self.in_torrent_list(fullpathfile,file2): DebugLog(file2+":: find in torrent list")
                            else: ExecLog(file2+":: not find in torrent list"); tDirNameList.append({'DirPath':fullpathfile,'DirName':pathfile2})
                    else:
                        if self.in_torrent_list(DiskPath,file) : DebugLog(file+"::find in torrent list:")
                        else :                            ExecLog(file+"::not find in torrent list:"); tDirNameList.append({'DirPath':DiskPath,'DirName':file})
                else :
                    ExecLog("Error：not file or dir")
        return tDirNameList

    def keep_torrents(self,tDiskPath):
        """
        输入:待进行保种的目录列表
        1、查找movies表，获取下载链接及hash
        2、如果下载链接不空，就取下载链接，否则通过hash值去种子备份目录寻找种子文件
        3、加入qb，设置分类为'转移',跳检，不创建子文件夹
        """
        
        tPTClient = PTClient("TR")

        tDirNameList = check_disk(tDiskPath)  #检查tDiskPath,获取未保种的目录列表
        for tDirName in tDirNameList:
            ExecLog("begin to keep torrent:"+tDirName['DirPath']+tDirName['DirName'])
            tMovie = movie.Movie(tDirName['DirPath'],tDirName['DirName'])
            if tMovie.CheckDirName() == 0 :
                ExecLog("failed to checkdirname:"+tMovie.DirName)
                continue
            if not tMovie.get_torrent(): ExecLog("can't get torrent:"+self.DirName); continue
            if tPTClient.add_torrent(download_link=tMovie.download_link,torrent_file=tMovie.torrent_file,download_dir=TR_KEEP_DIR,is_paused=True):
                ExecLog("success add torrent to tr")
            else:
                ErrorLog("failed to add torrent:"+TorrentFile+"::"+DownloadLink)
                continue
            tLink = os.path.join(TR_KEEP_DIR,tr_torrent.name) 
            tFullPathDirName = os.path.join(tDirName['DirPath']+tDirName['DirName'])
            if os.path.exists(tLink) : os.remove(tLink)
            try:    
                os.symlink(tFullPathDirName,tLink)
            except:
                ErrorLog("failed create link:ln -s "+tFullPathDirName+" "+tLink)
            else: ExecLog("create link: ln -s "+tFullPathDirName+" "+tLink)

        #把新加入的种子加入列表
        self.check_torrents("TR")

    def request_free(self,mSiteName="",mTimeInterval=-1):

        DebugLog("request free:{}::{}".format(mSiteName,mTimeInterval))
        tTorrentList = []
        for site in NexusPage.site_list:
            if mSiteName.lower() == site['name'].lower() or (site['time_interval'] != 0 and mTimeInterval % site['time_interval'] == 0): 
                tSite = site
            else:
                continue
            site_log("begin request free:"+tSite['name'])
            tPage = NexusPage(tSite)
            if not tPage.request_free_page(): continue

            for tTask in tPage.find_free_torrents():
                site_log("{}|{}|{}|{}|{}".format(tTask['free'],tTask['title'],tTask['torrent_id'],tTask['douban_id'],tTask['imdb_id']))
                if tTask['free'] == False: continue

                TorrentID = tTask['torrent_id']
                Title = tTask['title']
                Details = tTask['details']
                DownloadLink = tTask['download_link']

                tRSS = RSS("",tPage.site['name'],DownloadLink,Title)
                if tRSS.select():   #rss记录已经存在
                    if tRSS.downloaded == 1: site_log("torrentID have been downloaded:"+TorrentID+"::"+Title); continue
                    if not tRSS.update_id(tTask['douban_id'],tTask['imdb_id']): return False  #比较更新douban_id和imdb_id
                    tInfo = Info(tRSS.douban_id,tRSS.imdb_id)
                    tTorrent = MyTorrent(rss=tRSS,info=tInfo)
                else:
                    ExecLog("failed to find rss from torrentid:"+tRSS.rss_name+"::"+tRSS.torrent_id)
                    #if not tPage.request_detail_page(TorrentID):
                    #    ExecLog("failed to request detail")
                    #    continue
                    """
                    tTorrentInfo = TorrentInfo(download_link=tRSS.download_link)
                    if not tTorrentInfo.get_info():
                        ExecLog("failed to get torrent info from :"+tRSS.download_link)
                        continue
                    """
                    tRSS.HASH = get_hash(download_link=tRSS.download_link)
                    if tRSS.HASH == "": ExecLog("failed to get hash from "+tRSS.download_link); continue
                    if not tRSS.insert():
                        ExecLog("failed to insert rss:{}|{}|{}".format(tRSS.HASH,tRSS.rss_name,tRSS.title))
                        continue
                    
                    site_log("get a torrent from link:{}|{}|{}".format(tRSS.download_link,tRSS.title,tRSS.HASH))
                    tTorrent= MyTorrent(rss=tRSS)

                if tTask['douban_id'] != ""   : tTorrent.douban_id = tTask['douban_id']
                if tTask['douban_link'] != "" : tTorrent.douban_link = tTask['douban_link']
                if tTask['douban_score'] != "": tTorrent.douban_score = tTask['douban_score']
                if tTask['imdb_id'] != ""     : tTorrent.imdb_id = tTask['imdb_id']
                if tTask['imdb_link'] != ""   : tTorrent.imdb_link = tTask['imdb_link']
                if tTask['imdb_score'] != ""  : tTorrent.imdb_score = tTask['imdb_score']
                if self.get_torrent_index("QB",tTorrent.HASH) >= 0:
                    ExecLog("torrent exists in list:"+tRSS.title)
                    tTorrent.rss.downloaded = 1
                    tTorrent.rss.update_or_insert()
                    continue
                DebugLog("free   torrent:"+tTorrent.HASH)
                ExecLog("free    torrent:"+Title)
                self.add_torrent(tTorrent)
        return True

    def request_rss(self,mRSSName="",mTimeInterval=-2):
        
        DebugLog("request rss:{}::{}".format(mRSSName,mTimeInterval))
        for i in range(len(RSS_LIST)):
            if mRSSName.lower() == RSS_LIST[i]['name'].lower() or\
                    (RSS_LIST[i]['time_interval'] != 0 and (mTimeInterval % RSS_LIST[i]['time_interval']) == 0) :
                RSSName  = RSS_LIST[i]['name']
                WaitFree = RSS_LIST[i]['wait_free']
                url      = RSS_LIST[i]['url']
            else: continue

            rss_log("==========begin {}==============".format(RSSName.ljust(10,' ')))
            try:
                parser = feedparser.parse(url)
                tEntries = parser.entries
            except Exception as err:
                print(err)
                print(parser)
                ExecLog("failed to feedparser:"+url)
                return False
            for tEntry in tEntries:
                try:
                    Title = tEntry.title
                    HASH  = tEntry.id
                    Detail = tEntry.links[0].href
                    DownloadLink = tEntry.links[1].href
                except Exception as err:
                    print(err)
                    print(tEntry)
                    ErrorLog("error to get entry:")
                    continue

                tSummary = ""
                try:
                    tSummary = BeautifulSoup(tEntry.summary,'lxml').get_text()
                except Exception as err:
                    pass
                tInfo = Info()
                tInfo.get_from_summary(tSummary)

                Title = Title.replace('|','')
                tRSS = RSS(HASH,RSSName,DownloadLink,Title,tInfo.douban_id,tInfo.imdb_id)
                
                if not tRSS.filter_by_keywords(): continue
                
                if tRSS.select():
                    rss_log("old rss:"+tRSS.title)
                    continue
                if not tRSS.insert():  #记录插入rss数据库
                    ErrorLog("failed to insert into rss:{}|{}".format(RSSName,HASH))
                    continue
                tTorrent = MyTorrent(None,tRSS,tInfo,TO_BE_ADD)

                if not WaitFree: 
                    ExecLog("new rss tobeadd:"+tTorrent.title)
                    ExecLog("               :{}/{}|{}/{}|{}|{}|{}|{}".format(tInfo.douban_id,tInfo.imdb_id,tInfo.douban_score,tInfo.imdb_score,tInfo.type,tInfo.nation,tInfo.movie_name,tInfo.director))
                    self.add_torrent(tTorrent)
                else:
                    rss_log("               :{}/{}|{}/{}|{}|{}|{}|{}".format(tInfo.douban_id,tInfo.imdb_id,tInfo.douban_score,tInfo.imdb_score,tInfo.type,tInfo.nation,tInfo.movie_name,tInfo.director))

            #end for Items
        return True
            
    def set_spider_id(self,RequestList,mSocket=None):

        if len(RequestList) != 2: return "invalid number of arguments"

        tName = RequestList[0]
        tID   = RequestList[1]
        ExecLog("begin set {} {}".format(tName,tID))
        tIndexList = []
        for i in range(len(self.torrent_list)):
            if tName in self.torrent_list[i].title or tName in self.torrent_list[i].name:
                #ExecLog("find match torrent:"+self.torrent_list[i].name)
                tIndexList.append(i)
        if len(tIndexList) == 0: return "not find matching torrent"
        elif len(tIndexList) == 1:
            i = tIndexList[0]
            if tID[:2] == 'tt': self.torrent_list[i].imdb_id = tID
            else              : self.torrent_list[i].douban_id = tID

            self.torrent_list[i].spider_status = RETRY
            self.torrent_list[i].douban_Status = RETRY
            return "success set {} {}".format(self.torrent_list[i].name,tID)
        else: 
            mSocket.send("2+ matching torrent")
            for i in tIndexList:
                mSocket.send("matching torrent:"+self.torrent_list[i].name)
                if mSocket.receive() == "y":
                    if tID[:2] == 'tt': self.torrent_list[i].imdb_id = tID
                    else              : self.torrent_list[i].douban_id = tID
                    ExecLog("set id:{}|{}".format(self.torrent_list[i].name,tID))
            mSocket.send('end')
                    
            return "completed"

    def print_low_upload(self):
        reply = ""
        for i in range(len(self.torrent_list)):
            if self.torrent_list[i].category == '低上传':
                tTorrent = self.torrent_list[i]
                reply += tTorrent.get_title()+'\n' 
                reply += '    {}|{}/{} \n'.format(tTorrent.info.movie_name,tTorrent.info.douban_score,tTorrent.info.imdb_score)
        return reply

    def query_torrents(self,mList=[]):
        """
        mList =
        []   : default qb+null
        qb   : qb
        all  : all
        tr   : tr
        null : null
        """
        if   len(mList) == 0: tClientList =  ['QB','']
        elif len(mList) >= 2: ErrorLog("invalid arg mList="+' '.join(mList)); return ""
        else                : # len(mList) == 1
            if   mList[0].lower() == 'qb': tClientList = ['QB']
            elif mList[0].lower() == 'tr': tClientList = ['TR']
            elif mList[0].lower() == 'all': tClientList = ['QB','TR','']
            elif mList[0].lower() == 'null': tClientList = ['']
            elif mList[0].lower() == 'default': tClientList = ['QB','']
            else: ErrorLog("invalid arg mList="+mList[0]); return ""

        tReply = ""
        for i in range(len(self.torrent_list)):
            if self.torrent_list[i].client in tClientList:
                tReply += self.torrent_list[i].client+'|'
                tReply += self.torrent_list[i].get_hash()+'|'
                tReply += str(self.torrent_list[i].add_status)+'|'
                tReply += self.torrent_list[i].get_name()+'|'
                tReply += self.torrent_list[i].rss_name+'|'
                tReply += self.torrent_list[i].download_link+'|'
                tReply += str(self.torrent_list[i].progress)+'|'
                tReply += str(self.torrent_list[i].status)+'|'
                tReply += self.torrent_list[i].category+'|'
                tReply += str(self.torrent_list[i].total_size)+'|'
                tReply += self.torrent_list[i].add_datetime+'|'
                tReply += self.torrent_list[i].douban_id+'|'
                tReply += self.torrent_list[i].imdb_id+'|'
                tReply += self.torrent_list[i].douban_score+'|'
                tReply += self.torrent_list[i].imdb_score+'|'
                tReply += self.torrent_list[i].movie_name+'|'
                tReply += self.torrent_list[i].nation+'\n'
        return tReply


    def request_set_id(self,mRequestStr):
        """
        client|hash|doubanid|imdbid
        """
        tClient,tHASH,tDoubanID,tIMDBID = mRequestStr.split('|',3)
        if tHASH == "" or (tIMDBID == "" and tDoubanID == ""): return "False,empty hash or empty id"
        for i in range(len(self.torrent_list)):
            if tClient == self.torrent_list[i].client and tHASH == self.torrent_list[i].hash:
                self.torrent_list[i].douban_id = tDoubanID
                self.torrent_list[i].imdb_id   = tIMDBID
                return "Success"
        return "False, not find matched torrent"

    def request_del_torrent(self,mRequestStr):
        """
        client|hash|is_delete_file
        """
        try:
            tClient,tHASH,tIsDeleteFileStr = mRequestStr.split('|',2)
        except Exception as err:
            print(err)
            ExecLog("failed to split:"+mRequestStr)
            return "error requeststr:"+mRequestStr
        DebugLog("to del {}|{}".format(tClient,tHASH))
        tIsDeleteFile = (tIsDeleteFileStr.lower() == "true")

        tIndex = self.get_torrent_index(tClient,tHASH)
        if tIndex == -1: return "False, not find matched torrent"
        tAddStatus = self.torrent_list[tIndex].add_status 
        if not self.del_torrent(tClient,tHASH): return "False, not find matched torrent"
        if tAddStatus != TO_BE_ADD:
            tPTClient = PTClient(tClient)
            if not (tPTClient.connect() and tPTClient.del_torrent(tHASH,is_delete_file=tIsDeleteFile)): 
                return "False, can't delete torrent in "+tClient
        return "Success"

