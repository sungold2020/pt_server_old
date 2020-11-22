#!/usr/bin/python3
# coding=utf-8

import feedparser

import movie
from rss import *
from info import Info
from mytorrent import *
from log import *
from ptsite import *
from client import PTClient
from rsssite import *
import threading 


#连续NUMBEROFDAYS上传低于UPLOADTHRESHOLD，并且类别不属于'保种'的种子，会自动停止。
NUMBEROFDAYS = 1                           #连续多少天低于阈值
UPLOADTHRESHOLD = 0.03                    #阈值，上传/种子大小的比例

TORRENT_LIST_BACKUP = "data/pt.txt"  #种子信息备份目录（重要的是每天的上传量）
TRACKER_LIST_BACKUP = "data/tracker.txt"               
IGNORE_FILE = "data/ignore.txt"

TR_KEEP_DIR = '/media/root/BT/keep/'   #TR种子缺省保存路径

class Torrents:
    def __init__(self):
        self.torrent_list = []
        self.lock = threading.RLock()
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
        
        # 读取IGNORE_FILE
        self.ignore_list = []
        if os.path.isfile(IGNORE_FILE):
            for line in open(IGNORE_FILE):
                path,name = line.split('|',1)
                path = path.strip(); name = name.strip()
                if name[-1:] == '\n' : name = name[:-1]
                self.ignore_list.append({'Path':path,'Name':name})
            ExecLog(f"read ignore from {IGNORE_FILE}")
        else :
            ExecLog(f"{IGNORE_FILE} does not exist")
        
        if self.read_pt_backup():
            ExecLog(f"read pt backup from {TORRENT_LIST_BACKUP}")
            ExecLog(f"last_check_date = {self.last_check_date}")
        if self.read_tracker_backup(): ExecLog(f"read tracker backup from {TRACKER_LIST_BACKUP}")

    def get_torrent_index(self,mClient,mHASH):
        for i in range(len(self.torrent_list)) :
            if self.torrent_list[i].client == mClient and (mHASH == self.torrent_list[i].hash or mHASH == self.torrent_list[i].HASH): return i
        return -1   

    def get_torrent(self,mClient,mHASH):
        for i in range(len(self.torrent_list)) :
            if self.torrent_list[i].client == mClient and (mHASH == self.torrent_list[i].hash or mHASH == self.torrent_list[i].HASH): return self.torrent_list[i]
        return None


    def append_list(self,mTorrent):
        if self.get_torrent_index(mTorrent.client,mTorrent.get_hash()) >= 0: ExecLog(f"torrent exists:{mTorrent.get_compiled_name()}"); return False
        self.lock.acquire() 
        self.torrent_list.append(mTorrent)
        self.lock.release()
        self.write_pt_backup()
        return True

    def del_list(self,mClient,mHASH):
        self.lock.acquire()
        for i in range(len(self.torrent_list)):
            if self.torrent_list[i].get_hash() == mHASH and self.torrent_list[i].client == mClient: 
                del self.torrent_list[i]
                self.write_pt_backup()
                self.lock.release()
                return True
        self.lock.release()
        return False

    def add_torrent(self,mClient,mHASH):
        self.lock.acquire()
        i = self.get_torrent_index(mClient,mHASH)
        if i == -1: 
            self.lock.release()
            return "not find matched torrent"
        tPTClient = PTClient(mClient)
        if not tPTClient.connect(): return "failed to connect "+mClient
        if tPTClient.add_torrent(HASH=mHASH,download_link=self.torrent_list[i].download_link,is_paused=True):
            ExecLog("add new torrent:"+self.torrent_list[i].get_compiled_name())
            self.torrent_list[i].add_status = TO_BE_START
            self.lock.release()
            self.write_pt_backup()
            return "Success"
        else:
            ErrorLog("failed to add torrent:"+self.torrent_list[i].get_compiled_name())
            self.lock.release()
            return "failed to add torrent"

    def del_torrent(self,mClient,mHASH,is_delete_file=True):
        tIndex = self.get_torrent_index(mClient,mHASH)
        if tIndex == -1: return "False, not find matched torrent"
        tAddStatus = self.torrent_list[tIndex].add_status 
        tTitle     = self.torrent_list[tIndex].get_compiled_name()
        if not self.del_list(mClient,mHASH): return "False, failed to del_list"
        if tAddStatus != TO_BE_ADD and tAddStatus != MANUAL:
            tPTClient = PTClient(mClient)
            if not tPTClient.connect(): return "False, failed to connect "+mClient
            if not tPTClient.del_torrent(mHASH,is_delete_file=is_delete_file): 
                return "False, can't delete torrent in "+mClient
        ExecLog("del  torrent:"+tTitle)
        return "Success"

    def reset_checked(self,mClient,tPTClient):
        tNumberOfAdded=0
        self.lock.acquire()
        for i in range( len(self.torrent_list) ):
            if self.torrent_list[i].client == mClient: 
                self.torrent_list[i].checked = 0
                if self.torrent_list[i].add_status == TO_BE_ADD: 
                    self.torrent_list[i].checked = 1
                    if tPTClient.add_torrent(HASH=self.torrent_list[i].HASH,download_link=self.torrent_list[i].download_link,is_paused=True):
                        tNumberOfAdded += 1
                        ExecLog("add new torrent:"+self.torrent_list[i].get_compiled_name())
                        self.torrent_list[i].add_status = TO_BE_START
                        self.write_pt_backup()
                        #time.sleep(60)
                    else:
                        ErrorLog("failed to add torrent:"+self.torrent_list[i].get_compiled_name())
                elif self.torrent_list[i].add_status == MANUAL: self.torrent_list[i].check_movie_info()
                else: pass
                    
        self.lock.release()
        return tNumberOfAdded
            
    def read_pt_backup(self):
        """
        读取备份目录下的pt.txt，用于恢复种子记录数据，仅当初始化启动时调用
        """
        if not os.path.isfile(TORRENT_LIST_BACKUP): ExecLog(TORRENT_LIST_BACKUP+" does not exist"); return False
        tDate = "1970-01-01"
        for line in open(TORRENT_LIST_BACKUP):
            Client,HASH,Name,SiteName,Title,DownloadLink,AddStatusStr,TotalSizeStr,AddDateTime,DoubanID,IMDBID,IDStatusStr,DoubanStatusStr,DoubanScore,IMDBScore,tDateDataStr = line.split('|',15)
            if tDateDataStr [-1:] == '\n' :  tDateDataStr = tDateDataStr[:-1]  #remove '\n'
            tDateDataList = tDateDataStr.split(',')
            DateData = []
            try:
                for i in range(len(tDateDataList)) :
                    if tDateDataList[i] == "" :  break      #最后一个可能为空就退出循环
                    tDate = (tDateDataList[i])[:10]
                    tData = int( (tDateDataList[i])[11:] )
                    DateData.append({'date':tDate,'data':tData})
            except Exception as err:
                print(err)
                print(f"{Name}|{HASH}")
                exit()

            tTorrent = Torrent(Client,None)
            tTorrent.date_data = DateData
            tRSS = RSS(HASH,SiteName,DownloadLink,'',Title,DoubanID,IMDBID,AddDateTime,int(TotalSizeStr),int(IDStatusStr))
            if tRSS.douban_status == RETRY: tRSS.douban_status = int(DoubanStatusStr)
            if tRSS.douban_score == "": tRSS.douban_score = DoubanScore
            if tRSS.imdb_score   == "": tRSS.imdb_score   = IMDBScore  
            self.torrent_list.append(MyTorrent(tTorrent,tRSS,int(AddStatusStr)))  #init, can't use add_torrent
        self.last_check_date = tDate
        return True

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

        self.lock.acquire()
        try : 
            fo = open(TORRENT_LIST_BACKUP,"w")
        except: 
            ErrorLog("Error:open ptbackup file to write："+TORRENT_LIST_BACKUP)
            self.lock.release()
            return False
            
        for i in range(len(self.torrent_list)):
            tDateDataListStr = ""
            for j in range( len(self.torrent_list[i].date_data) ):        
                tDateDataStr = self.torrent_list[i].date_data[j]['date']+":" + str(self.torrent_list[i].date_data[j]['data'])
                tDateDataListStr += tDateDataStr+','
            if tDateDataListStr[-1:] == ',' : tDateDataListStr = tDateDataListStr[:-1] #去掉最后一个','
            tStr  =     self.torrent_list[i].client+'|'
            tStr +=     self.torrent_list[i].get_hash()+'|'
            tStr +=     self.torrent_list[i].name.replace('|','')+'|'
            tStr +=     self.torrent_list[i].rss_name+'|'
            tStr +=     self.torrent_list[i].title.replace('|','')+'|'
            tStr +=     self.torrent_list[i].download_link+'|'
            tStr += str(self.torrent_list[i].add_status)+'|'
            tStr += str(self.torrent_list[i].total_size)+'|'
            tStr +=     self.torrent_list[i].add_datetime+'|'
            tStr +=     self.torrent_list[i].douban_id+'|'
            tStr +=     self.torrent_list[i].imdb_id+'|'
            tStr += str(self.torrent_list[i].id_status)+'|'
            tStr += str(self.torrent_list[i].douban_status)+'|'
            tStr +=     self.torrent_list[i].douban_score+'|'
            tStr +=     self.torrent_list[i].imdb_score+'|'
            tStr +=     tDateDataListStr+'\n'
            fo.write(tStr)
      
        fo.close()
        DebugLog(f"{len(self.torrent_list)} torrents writed")
        self.lock.release()
        return True    
       
    def check_torrents(self,mClient):
        """
        进行TR/QB的所有种子进行检查和分析，并更新列表
        返回值：-1:错误，0:无更新，1:有更新 ，用于指示是否需要备份文件
        """
        tNumberOfAdded = tNumberOfDeleted = tNumberOfUpdated = 0
        tToday = datetime.datetime.now().strftime('%Y-%m-%d')
        if tToday != self.last_check_date: tIsNewDay = True
        else                             : tIsNewDay = False   
        #连接Client并获取TorrentList列表
        tPTClient = PTClient(mClient)
        if not tPTClient.connect(): ErrorLog("failed to connect to "+mClient); return -1

        #先把检查标志复位,并对待加入的种子进行加入
        tNumberOfAdded += self.reset_checked(mClient,tPTClient)
		
        # 开始逐个获取torrent并检查
        for torrent in tPTClient.get_all_torrents(): 
            tIndex = self.get_torrent_index(mClient,torrent.hash)
            if tIndex == -1:
                ExecLog("findnew torrent:"+torrent.name)
                tRSS = RSS(torrent.hash,"",'',"",torrent.name,"","","",torrent.total_size,RETRY)
                self.append_list(MyTorrent(torrent,tRSS,STARTED))
                #tIndex = -1                   #指向刚加入的种子
                tNumberOfAdded += 1
            self.torrent_list[tIndex].checked = 1
            self.torrent_list[tIndex].torrent.torrent = torrent.torrent  #刷新种子信息
            tTorrent = self.torrent_list[tIndex]

            #check addStatus
            if tTorrent.status == 'GOING'and (tTorrent.add_status == MANUAL or tTorrent.add_status == TO_BE_START): tTorrent.add_status = STARTED
            if tTorrent.status == 'STOP' and tTorrent.add_status == MANUAL: tTorrent.add_status = TO_BE_START

            #检查并设置标签
            tTorrent.set_tag()
                
            #检查文件
            if tTorrent.progress == 100 :
                if tTorrent.check_files(tIsNewDay) == False:
                    ExecLog(tTorrent.torrent.error_string)
                    tTorrent.stop()

            # mteam部分免费种，免费一天，但下载完成率很低
            if tTorrent.status != "STOP" and tTorrent.category == '下载' and tTorrent.progress <= 95:
                tStartTime = datetime.datetime.strptime(tTorrent.add_datetime,"%Y-%m-%d %H:%M:%S")
                tSeconds = (datetime.datetime.now()-tStartTime).total_seconds()
                if tSeconds >= 24*3600 : 
                    tTorrent.stop()
                    ExecLog(tTorrent.name+" have not done more than 1 day") 
                            
            #如果种子状态不是STARTED，启动它
            if tTorrent.add_status == TO_BE_START and tTorrent.status == "STOP":
                if tTorrent.start_download():
                    ExecLog("start   torrent:"+tTorrent.name)
                    tNumberOfUpdated += 1
                    self.torrent_list[tIndex].add_status = STARTED
                else:
                    ExecLog("failed to start_download:"+self.torrent_list[tIndex].name)
                    continue

            #check movie_info
            tTorrent.check_movie_info()

            #保存电影
            if tTorrent.category == "save" : 
                if tTorrent.save_movie():  
                    #ExecLog("delete  torrent:"+tTorrent.get_compiled_name())
                    self.del_torrent(tTorrent.client,tTorrent.get_hash(),False)
            if tTorrent.category == "转移" : tTorrent.move_to_tr()
        #end for torrents 
        
        #最后，找出没有Checked标志的种子列表
        for torrent in self.torrent_list:
            if torrent.checked == 0 and torrent.client == mClient :
                if torrent.add_status != MANUAL and torrent.add_status != TO_BE_ADD:
                    tNumberOfDeleted += 1
                    ExecLog("delete  torrent:"+torrent.get_compiled_name())
                    self.del_list(torrent.client,torrent.get_hash())

        DebugLog("complete check_torrents  from "+mClient)
        if tNumberOfAdded > 0   : DebugLog(str(tNumberOfAdded).zfill(4)+" torrents added")
        if tNumberOfDeleted > 0 : DebugLog(str(tNumberOfDeleted).zfill(4)+" torrents deleted")
        if  tNumberOfAdded >= 1 or tNumberOfDeleted >= 1 or tNumberOfUpdated >= 1: return 1
        else                                                                     : return 0
        
    def count_upload(self,mClient):
        """每天调用一次，进行统计上传量"""
        tToday = datetime.datetime.now().strftime('%Y-%m-%d')
        tPTClient = PTClient(mClient)
        if not tPTClient.connect(): ExecLog("failed to connect "+mClient); return False
            
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
                    ExecLog("low upload:"+self.torrent_list[tIndex].get_compiled_name())
                    
    def tracker_data(self):
        """
        统计各站点的上传量
        """
        tToday = datetime.datetime.now().strftime('%Y-%m-%d')
        for i in range(len(self.tracker_data_list)):
            self.tracker_data_list[i]['date_data'].append( {'date':tToday,'data':0} )
            if len(self.tracker_data_list[i]['date_data']) >= 30: del self.tracker_data_list[i]['date_data'][0]

        for i in range(len(self.torrent_list)):
            if self.torrent_list[i].add_status == MANUAL or self.torrent_list[i].add_status == TO_BE_ADD: continue
            if   len(self.torrent_list[i].date_data) == 0: ErrorLog("date_data is null:"+self.torrent_list[i].HASH); continue
            elif len(self.torrent_list[i].date_data) == 1: tData = self.torrent_list[i].date_data[0]['data']
            else : tData = self.torrent_list[i].date_data[-1]['data']-self.torrent_list[i].date_data[-2]['data']
        
            Tracker = self.torrent_list[i].tracker
            IsFind = False
            for j in range(len(self.tracker_data_list)):
                if Tracker.find(self.tracker_data_list[j]['keyword']) >= 0 : 
                    self.tracker_data_list[j]['date_data'][-1]['data'] += tData
                    IsFind = True ; break
            if IsFind == False: ErrorLog(f"unknown tracker:{Tracker} for torrent:{self.torrent_list[i].name}:")

        TotalUpload = 0
        for i in range(len(self.tracker_data_list)):
            tUpload = self.tracker_data_list[i]['date_data'][-1]['data']; TotalUpload += tUpload
            ExecLog(f"{self.tracker_data_list[i]['name'].ljust(10)} upload(G):{round(tUpload/(1024*1024*1024),3)}")
        ExecLog(f"total       upload(G):{round(TotalUpload/(1024*1024*1024),3)}")
        ExecLog(f"average upload radio :{round(TotalUpload/(1024*1024*24*3600),2)}M/s")
            
        for i in range(len(self.tracker_data_list)):
            tDateData = self.tracker_data_list[i]['date_data']
            j=len(tDateData)-1
            NumberOfDays=0
            while j >= 0 :
                if tDateData[j]['data'] == 0 : NumberOfDays += 1
                else                         : break
                j -= 1
            ExecLog(f"{self.tracker_data_list[i]['name'].ljust(10)} {str(NumberOfDays).zfill(2)} days no upload")
        
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
            if len(self.torrent_list[i].files) == 0: continue
            FirstFile = os.path.realpath(os.path.join(self.torrent_list[i].save_path,self.torrent_list[i].files[0]['name']))
            if tSrcDirName in FirstFile: return True
            """
            for tFile in self.torrent_list[i].files:
                FirstFile = os.path.join(self.torrent_list[i].save_path,tFile['name'])
                tDestFile = os.path.realpath(FirstFile)
                if tSrcDirName in tDestFile: return True
            """
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
                            else: ExecLog(file2+":: not find in torrent list"); tDirNameList.append({'DirPath':fullpathfile,'DirName':fullpathfile2})
                    else:
                        if self.in_torrent_list(DiskPath,file) : DebugLog(file+"::find in torrent list:")
                        else: ExecLog(file+"::not find in torrent list:"); tDirNameList.append({'DirPath':DiskPath,'DirName':file})
                else :
                    ExecLog("Error：not file or dir")
        return tDirNameList


    def request_free(self,mSiteName="",mTimeInterval=-1):

        DebugLog(f"request free:{mSiteName}::{mTimeInterval}")
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
                site_log("{}|{}|{}|{}|{}".format(tTask['auto'],tTask['title'],tTask['torrent_id'],tTask['douban_id'],tTask['imdb_id']))
                #if tTask['free'] == False: continue

                TorrentID = tTask['torrent_id']
                Title = tTask['title']
                Details = tTask['details']

                DownloadLink = tTask['download_link']
                if RSS.old_free(TorrentID,site['name']):
                    DebugLog("old free torrents,ignore it:"+Title);
                    continue

                IDStatus = RETRY if tTask['douban_id'] == "" and tTask['imdb_id'] == "" else OK
                tRSS = RSS("",tPage.site['name'],DownloadLink,Details,Title,tTask['douban_id'],tTask['imdb_id'],"",0,IDStatus)
                if tRSS.HASH == "": ExecLog("cann't get hash,ignore it:"+Title); continue
                if not tRSS.insert():
                    ExecLog("failed to insert rss:{}|{}|{}".format(tRSS.HASH,tRSS.rss_name,tRSS.name))
                    continue
                    
                add_status = TO_BE_ADD if tTask['auto'] else MANUAL
                tTorrent= MyTorrent(torrent=None,rss=tRSS,add_status=add_status)

                if tTask['douban_link'] != "" : tTorrent.douban_link = tTask['douban_link']
                if tTask['douban_score'] != "": tTorrent.douban_score = tTask['douban_score']
                if tTask['imdb_link'] != ""   : tTorrent.imdb_link = tTask['imdb_link']
                if tTask['imdb_score'] != ""  : tTorrent.imdb_score = tTask['imdb_score']

                DebugLog("free   torrent:"+tTorrent.HASH)
                ExecLog("free    torrent:"+Title)
                self.append_list(tTorrent)
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

                if RSS.old_rss(HASH,RSSName):
                    rss_log("old rss:"+Title)
                    continue
                #if not tRSS.filter_by_keywords(): continue
                toBeDownloaded = to_be_downloaded(RSSName,Title)
                if toBeDownloaded == IGNORE_DOWNLOAD: continue
                addStatus = TO_BE_ADD if toBeDownloaded == AUTO_DOWNLOAD else MANUAL

                tSummary = ""
                try:
                    tSummary = BeautifulSoup(tEntry.summary,'lxml').get_text()
                except Exception as err:
                    pass
                return_code,douban_id,imdb_id = Info.get_from_summary(tSummary)

                Title = Title.replace('|','')
                IDStatus = OK if douban_id != "" or imdb_id != "" else RETRY
                tRSS = RSS(HASH,RSSName,DownloadLink,Detail,Title,douban_id,imdb_id,"",0,IDStatus)
                
                if not tRSS.insert():  #记录插入rss数据库
                    ErrorLog("failed to insert into rss:{}|{}".format(RSSName,HASH))
                    continue
                tTorrent = MyTorrent(None,tRSS,addStatus)

                if not WaitFree: 
                    ExecLog("new rss tobeadd:"+tTorrent.get_compiled_name())
                    ExecLog("               :{}/{}|{}/{}|{}|{}|{}|{}".format(tRSS.douban_id,tRSS.imdb_id,tRSS.douban_score,tRSS.imdb_score,tRSS.type,tRSS.nation,tRSS.movie_name,tRSS.director))
                    self.append_list(tTorrent)
                else:
                    rss_log("               :{}/{}|{}/{}|{}|{}|{}|{}".format(tRSS.douban_id,tRSS.imdb_id,tRSS.douban_score,tRSS.imdb_score,tRSS.type,tRSS.nation,tRSS.movie_name,tRSS.director))

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
                reply += tTorrent.get_compiled_name()+'\n' 
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

        #qb，返回前刷新下状态
        if mList[0].lower() == 'qb': self.check_torrents("QB")

        tReply = ""
        for i in range(len(self.torrent_list)):
            if self.torrent_list[i].client in tClientList:
                tReply += self.torrent_list[i].client+'|'
                tReply += self.torrent_list[i].get_hash()+'|'
                tReply += str(self.torrent_list[i].add_status)+'|'
                tReply += self.torrent_list[i].get_compiled_name()+'|'
                tReply += self.torrent_list[i].rss_name+'|'
                tReply += self.torrent_list[i].download_link+'|'
                tReply += str(self.torrent_list[i].progress)+'|'
                tReply += str(self.torrent_list[i].torrent_status)+'|'
                tReply += self.torrent_list[i].category+'|'
                tReply += self.torrent_list[i].tags+'|'
                tReply += str(self.torrent_list[i].total_size)+'|'
                tReply += self.torrent_list[i].add_datetime+'|'
                tReply += self.torrent_list[i].douban_id+'|'
                tReply += self.torrent_list[i].imdb_id+'|'
                if self.torrent_list[i].douban_score == "":
                    tReply += '-'+'|'
                else:
                    tReply += self.torrent_list[i].douban_score+'|'
                if self.torrent_list[i].imdb_score == "":
                    tReply += '-'+'|'
                else:
                    tReply += self.torrent_list[i].imdb_score+'|'
                tReply += self.torrent_list[i].movie_name+'|'
                tReply += self.torrent_list[i].nation+'|'
                tReply += self.torrent_list[i].poster+'\n'
        return tReply


    def request_set_id(self,mRequestStr):
        """
        client|hash|doubanid|imdbid
        """
        tClient,tHASH,tDoubanID,tIMDBID = mRequestStr.split('|',3)
        if tHASH == "" or (tIMDBID == "" and tDoubanID == ""): return "False,empty hash or empty id"
        for i in range(len(self.torrent_list)):
            if tClient == self.torrent_list[i].client and tHASH == self.torrent_list[i].get_hash():
                if self.torrent_list[i].set_id(tDoubanID,tIMDBID):
                    self.write_pt_backup()
                    return "Success"
                else:
                    return "False,failed set id"
        return "False, not find matched torrent"

    def request_set_category(self,mRequestStr):
        """
        client|hash|category
        """
        try:
            tClient,tHASH,tCategory = mRequestStr.split('|',2)
        except Exception as err:
            print(err)
            ExecLog("failed to split:"+mRequestStr)
            return "error requeststr:"+mRequestStr
        DebugLog("to set_cateory {}|{}|{}".format(tClient,tHASH,tCategory))
        client = PTClient(tClient)
        if not client.connect():
            ExecLog("failed to connect "+tClient)
            return "failed to connect "+tClient
        if client.set_category(tHASH,tCategory):
            ExecLog(f"set_category:{self.get_torrent(tClient,tHASH).get_compiled_name()}|{tCategory}")
            return "Success"
        else:
            return "failed to set category"



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

        return self.del_torrent(tClient,tHASH,tIsDeleteFile)

    def request_act_torrent(self,mRequestStr):
        """
        client|hash|action
        """
        try:
            tClient,tHASH,tAction = mRequestStr.split('|',2)
        except Exception as err:
            print(err)
            ExecLog("failed to split:"+mRequestStr)
            return "error requeststr:"+mRequestStr
        DebugLog("to act {}|{}|{}".format(tClient,tHASH,tAction))
        
        if tAction == "add": return self.add_torrent(tClient,tHASH)

        # TODO
        tIndex = self.get_torrent_index(tClient,tHASH)
        if tIndex == -1: return "not find match torrent"
        if tAction == "start": self.torrent_list[tIndex].start()
        elif tAction == "stop": self.torrent_list[tIndex].stop()
        ExecLog(f"{tAction} :{self.torrent_list[tIndex].get_compiled_name()}")
        return "Success"


    def request_saved_movie(self,mRequestStr):
        """
        request:
            movie doubanid|imdbid
        reply:
            dirname|disk|deleted\n
            dirname|disk|deleted\n
        """
        try:
            DoubanID,IMDBID = mRequestStr.split('|',1)
        except Exception as err:
            print(err)
            ExecLog("failed to split:"+mRequestStr)
            return "failed:error requeststr:"+mRequestStr
        DebugLog("to movie {}|{}".format(DoubanID,IMDBID))
        
        if DoubanID != "":
            sel_sql = 'select dirname,disk,deleted from movies where doubanid = %s'
            sel_val = (DoubanID,)
        else:
            sel_sql = 'select dirname,disk,deleted from movies where imdbid = %s'
            sel_val = (IMDBID,)
        SelectResult = select(sel_sql,sel_val)
        if SelectResult == None or len(SelectResult) == 0: 
            return "failed: no record"
        reply = ""
        for tSelect in SelectResult:
            reply += tSelect[0]+'|'   #dirname
            reply += tSelect[1]+'|'   #disk
            reply += str(tSelect[2])+'|'+'\n' #deleted
        return reply


    def request_tracker_message(self,mRequestStr):
        """
        client|hash
        """
        try:
            tClient,tHASH = mRequestStr.split('|',1)
        except Exception as err:
            print(err)
            ExecLog("failed to split:"+mRequestStr)
            return "error requeststr:"+mRequestStr
        DebugLog("get_tracker_message {}|{}".format(tClient,tHASH))
        
        torrent = self.get_torrent(tClient,tHASH)
        return torrent.tracker_message if torrent != None else "failed"
