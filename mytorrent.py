#!/usr/bin/python3
# coding=utf-8
import os
import time
import shutil
import re
import requests
#from gen import Gen

from movie import *
from log import *
from rss import RSS
from torrent import *
from info import *
from ptsite import *
from client import PTClient

DOWNLOAD_FOLDER = "/media/root/BT/movies"
TO_BE_PATH = "/media/root/BT/tobe/"           #保存的电影所在临时目录
TR_KEEP_DIR = "/media/root/BT/keep/"

#QB的备份目录BT_backup，我的运行环境目录如下，如有不同请搜索qbittorrent在不同OS下的配置
QB_BACKUP_DIR  = "/root/.local/share/data/qBittorrent/BT_backup"
TR_BACKUP_DIR = "/root/.config/transmission"

#转移做种以后，把种子文件和快速恢复文件转移到QBTorrentsBackupDir目录进行保存，以备需要
QB_TORRENTS_BACKUP_DIR = "data/qb_backup"   
TR_TORRENTS_BACKUP_DIR = "data/tr_backup"   

MANUAL      = -1
TO_BE_ADD   =  0
TO_BE_START =  1
STARTED     =  2
MOVED       =  3         

class MyTorrent:

    def __init__(self,torrent=None,rss=None,add_status=TO_BE_ADD):
        self.torrent = torrent if torrent != None else Torrent("QB",None)
        self.rss = rss      
        #self.info = info    if info != None else Info()
        self.add_status = add_status
        self.checked = 1              #每次检查时用于标记它是否标记到，检查结束后，如果发现Checked为0，说明种子已经被删除。
                                      #新建对象时肯定Checked=1
        self.is_check_nfo = False
    #------------- begin rss------------------------------
    @property
    def rss_name(self):
        if self.rss == None: return ""
        else               : return self.rss.rss_name
    @rss_name.setter
    def rss_name(self,rss_name):
        if self.rss == None: ErrorLog("set rss_name,but rss is none")
        else               : self.rss.rssname = rss_name
    @property
    def HASH(self):
        if self.rss == None: return ""
        else               : return self.rss.HASH
    @HASH.setter
    def HASH(self,HASH):
        if self.rss == None: ErrorLog("set HASH,but rss is none")
        else               : self.rss.HASH = HASH
    @property
    def download_link(self):
        if self.rss == None: return ""
        else               : return self.rss.download_link
    @download_link.setter
    def download_link(self,download_link):
        if self.rss == None: ErrorLog("set download_link,but rss is none")
        else               : self.rss.download_link = download_link
    @property
    def title(self):
        if self.rss == None: return ""
        else               : return self.rss.title
    @title.setter
    def title(self,title):
        if self.rss == None: ErrorLog("set title,but rss is none")
        else               : self.rss.title = title
    @property
    def torrent_id(self):
        if self.rss == None: return ""
        else               : return self.rss.torrent_id
    @torrent_id.setter
    def torrent_id(self,torrent_id):
        if self.rss == None: ErrorLog("set torrent_id,but rss is none")
        else               : self.rss.torrent_id = torrent_id
    @property
    def add_datetime(self):
        if self.rss == None: return ""
        else               : return self.rss.add_datetime
    @add_datetime.setter
    def add_datetime(self,add_datetime):
        if self.rss == None: ErrorLog("set add_datetime,but rss is none")
        else               : self.rss.add_datetime = add_datetime
    @property
    def total_size(self):
        return self.torrent.total_size if self.torrent.torrent != None else self.rss.total_size
    @total_size.setter
    def total_size(self,total_size):
        if self.rss == None: ErrorLog("set total_size,but rss is none")
        else               : self.rss.total_size = total_size
    @property
    def downloaded(self):
        if self.rss == None: return 0
        else               : return self.rss.downloaded
    @downloaded.setter
    def downloaded(self,downloaded):
        if self.rss == None: ErrorLog("set downloaded,but rss is none")
        else               : self.rss.downloaded = downloaded
    @property
    def id_status(self):
        return self.rss.id_status 
    @id_status.setter
    def id_status(self,id_status):
        if self.rss == None: ErrorLog("set id_status,but rss is none")
        else               : self.rss.id_status = id_status
    def set_id(self,douban_id,imdb_id):
        return self.rss.set_id(douban_id,imdb_id) if self.rss != None else  False

        #------------------begin info-------------------
    @property
    def douban_id(self):
        return self.rss.douban_id if self.rss != None else ""
    @douban_id.setter
    def douban_id(self,douban_id):
        self.rss.douban_id = douban_id
    @property
    def douban_score(self):
        return self.rss.douban_score if self.rss != None else ""
    @douban_score.setter
    def douban_score(self,douban_score):
        self.rss.douban_score = douban_score
    @property
    def imdb_id(self):
        return self.rss.imdb_id if self.rss != None else ""
    @imdb_id.setter
    def imdb_id(self,imdb_id):
        self.rss.imdb_id = imdb_id
    @property
    def imdb_score(self):
        return self.rss.imdb_score if self.rss != None else ""
    @imdb_score.setter
    def imdb_score(self,imdb_score):
        self.rss.imdb_score = imdb_score
    @property
    def douban_link(self):
        return self.rss.douban_link if self.rss != None else ""
    @douban_link.setter
    def douban_link(self,douban_link):
        self.rss.douban_link = douban_link
    @property
    def imdb_link(self):
        return self.rss.imdb_link if self.rss != None else ""
    @imdb_link.setter
    def imdb_link(self,imdb_link):
        self.rss.imdb_link = imdb_link
    @property
    def movie_name(self):
        return self.rss.movie_name if self.rss != None else ""
    @movie_name.setter
    def movie_name(self,movie_name):
        self.rss.movie_name = movie_name
    @property
    def type(self):
        return self.rss.type if self.rss != None else ""
    @type.setter
    def type(self,mType):
        self.rss.type = mType
    @property
    def nation(self):
        return self.rss.nation if self.rss != None else ""
    @property
    def poster(self):
        return self.rss.poster if self.rss != None else ""
    @nation.setter
    def nation(self,nation):
        self.rss.nation = nation
    @property
    def douban_status(self):
        return self.rss.douban_status 
    @douban_status.setter
    def douban_status(self,douban_status):
        self.rss.douban_status = douban_status
    @property
    def douban_retry_times(self):
        return self.rss.douban_retry_times if self.rss != None else ""
    @douban_retry_times.setter
    def douban_retry_times(self,douban_retry_times):
        self.rss.douban_retry_times = douban_retry_times
    @property
    def foreign_name(self):
        return self.rss.foreign_name if self.rss != None else ""
    @property
    def other_names(self):
        return self.rss.other_names if self.rss != None else ""
    @property
    def director(self):
        return self.rss.director if self.rss != None else ""
    @property
    def actors(self):
        return self.rss.actors if self.rss != None else ""
    @property
    def episodes(self):
        return self.rss.episodes if self.rss != None else ""
    @property
    def poster(self):
        return self.rss.poster if self.rss != None else ""
    @property
    def genre(self):
        return self.rss.genre if self.rss != None else ""
        #------------------end info---------------
    #-------------------end rss------------------------

    #------------------begin torrent-------------------
    @property
    def client(self):
        if self.torrent == None: return ""
        else               : return self.torrent.client
    @property
    def date_data(self):
        if self.torrent == None: return []
        else               : return self.torrent.date_data
    @date_data.setter
    def date_data(self,date_data):
        self.torrent.date_data = date_data
    @property
    def hash(self):
        if self.torrent == None: return ""
        else               : return self.torrent.hash
    @property
    def name(self):
        if self.torrent == None: return ""
        else               : return self.torrent.name
    @property
    def progress(self):
        if self.torrent == None: return 0
        else               : return self.torrent.progress
    @property
    def status(self):
        if self.torrent == None: return "UNKNOWN"
        else               : return self.torrent.status
    @property
    def tracker_status(self):
        if self.torrent == None: return "UNKNOWN"
        else               : return self.torrent.tracker_status
    @property
    def torrent_status(self):
        if self.torrent == None: return "UNKNOWN"
        else               : return self.torrent.torrent_status
    @property
    def category(self):
        if self.torrent == None: return ""
        else               : return self.torrent.category
    @property
    def tags(self):
        if self.torrent == None: return ""
        else               : return self.torrent.tags
    @property
    def save_path(self):
        if self.torrent == None: return ""
        else               : return self.torrent.save_path
    @property
    def add_datetime(self):
        if self.torrent.torrent != None: return self.torrent.add_datetime
        else                           : return self.rss.add_datetime
    @property
    def tracker(self):
        if self.torrent == None: return ""
        else               : return self.torrent.tracker
    @property
    def uploaded(self):
        if self.torrent == None: return ""
        else               : return self.torrent.uploaded
    #@property
    #def total_size(self):   defined in rss part
    @property
    def files(self):
        if self.torrent == None: return []
        else               : return self.torrent.files
    #重定义函数
    def start(self):
        if self.torrent == None: return False
        else               : return self.torrent.resume()
    def stop(self):
        if self.torrent == None: return False
        else               : return self.torrent.stop()
    def pause(self):
        if self.torrent == None: return False
        else               : return self.torrent.pause()
    def resume(self):
        if self.torrent == None: return False
        else               : return self.torrent.resume()
    def set_category(self,category=""):
        if self.torrent == None: return False
        else               : return self.torrent.set_category(category)
    def set_tags(self,tags=""):
        if self.torrent == None: return False
        else               : return self.torrent.set_tags(tags)
    def is_root_folder(self):
        if self.torrent == None: return False
        else               : return self.torrent.is_root_folder()
    def check_files(self,mIsNewDay):
        if self.torrent == None: return False
        else               : return self.torrent.check_files(mIsNewDay)
    def is_low_upload(self,mNumberOfDays,mUploadThreshold):
        if self.torrent == None: return False
        else               : return self.torrent.is_low_upload(mNumberOfDays,mUploadThreshold)
    #------------------end torrent-------------------

    def get_name(self):
        return self.name if self.name != "" else self.title
    def get_title(self):
        return self.title if self.title != "" else self.name
    def get_compiled_name(self):
        return self.rss.name if (self.rss != None and self.rss.name != "") else self.name
    def get_hash(self):
        if self.hash != self.HASH and self.hash != "" and self.HASH != "": ErrorLog("error:diff hash and HASH:{}|{}".format(self.hash,self.HASH))
        return self.hash if self.hash != "" else self.HASH

    def set_tag(self):
        if self.client == "QB":
            tTracker = self.tracker
            if tTracker.find("keepfrds") >= 0 :
                if self.tags != 'frds' : self.set_tags('frds')
            elif tTracker.find("m-team") >= 0 :
                if self.tags != 'mteam': self.set_tags('mteam')
            elif tTracker.find("hdsky") >= 0 :
                if self.tags != 'hdsky': self.set_tags('hdsky')
            elif tTracker == "" : pass
            else:
                if self.tags != 'other': self.set_tags('other')     
    
    def start_download(self):
        if self.torrent == None: ErrorLog("torrent does not exist"); return False

        if not self.rss.update_downloaded(): ErrorLog("failed to update rss:"+self.name+':'+self.HASH)

        tBTStat =  os.statvfs(DOWNLOAD_FOLDER)
        tFreeSize = (tBTStat.f_bavail * tBTStat.f_frsize) /(1024*1024*1024)
        #DebugLog("free size:"+str(tFreeSize))
        tSize = self.torrent.total_size /(1024*1024*1024)
        #DebugLog("Size:"+str(tSize))
        if tFreeSize < tSize+1 :ExecLog("diskspace is not enough"); return False
        if  self.resume() and self.set_category("下载"):
            DebugLog("start download:"+self.name)
            return True
        else:
            ExecLog("failed to start torrent:"+self.name)
            return False

    def get_id_from_nfo(self):
        if self.progress != 100: 
            ErrorLog("begin to get id from nfo,but torrent have not done.")
            return False
        
        #如果已经检查过nfo了，就不用再检查了
        if self.is_check_nfo == True: return False
        self.is_check_nfo = True
        
        #检查下有没有nfo文件
        tNfoFileName = ""
        tFiles = self.files
        for tFile in tFiles:
            if tFile['name'][-4:].lower() == '.nfo' :
                tNfoFileName = os.path.join(self.save_path,tFile['name'])
                DebugLog("find  nfo  file:"+self.name)
                break
        if tNfoFileName == "": ExecLog("n_find nfo file:"+self.name); return False
        
        #检索nfo文件内容是否包含
        IMDBLink = DoubanLink = ""
        for line in open(tNfoFileName,"rb"):
            line = line.decode("utf8","ignore")
            if line[-1:] == '\n': line = line[:-1]
            line = line.strip()                   #去除前后的空字符，换行符等
            line = line.lower()
            tIndex = line.find("https://www.imdb.com/title")
            if tIndex >= 0 : IMDBLink = line[tIndex:]
            tIndex = line.find("http://www.imdb.com/title")
            if tIndex >= 0 : IMDBLink = line[tIndex:]
            tIndex = line.find("http://movie.douban.com/subject")
            if tIndex >= 0 : DoubanLink = line[tIndex:1]
            tIndex = line.find("https://movie.douban.com/subject")
            if tIndex >= 0 : DoubanLink = line[tIndex:1] 
        douban_id = Info.get_id_from_link(DoubanLink,DOUBAN)
        imdb_id   = Info.get_id_from_link(IMDBLink,IMDB)
        DebugLog("DoubanLink:{} :: IMDBLink:{}".format(DoubanLink,IMDBLink))
        DebugLog("find DoubanID:{} :: IMDBID:{}".format(douban_id,imdb_id))

        if douban_id == "" and imdb_id == "": ExecLogLog("can't find id from nfo:"+self.get_name()); return False
        ExecLog("get id from nfo:{}|{}{}".format(self.get_name(),douban_id,imdb_id)); 
        if not self.rss.set_id(douban_id,imdb_id): ExecLog("failed to set_id:{}|{}|{}".format(self.title,douban_id,imdb_id))
        return  True

    def check_movie_info(self):
        """
        检查是否已经获取豆瓣详情：1、首先检查是否具备ID（获取ID后，会创建Info对象，并检索info表的数据）2、根据id爬取豆瓣详情页
        """
        #检查id
        if self.id_status == NOK:  return NOK
        elif self.id_status == RETRY:
            isIDOK = self.rss.get_id_from_detail()
            if isIDOK == NOK:
                #尝试读取nfo文件找id
                if self.progress == 100:
                    if not self.get_id_from_nfo(): self.id_status = NOK; return NOK
                else: return RETRY
            elif isIDOK == RETRY: return RETRY
        else : pass  # ID is OK
        
        if self.rss.info == None:  ErrorLog("id is ok,but info is null")
        if self.douban_status == OK   : return self.douban_status
        elif self.douban_status == NOK: ExecLog("can't find record for {}|{}".format(self.douban_id,self.imdb_id)); return NOK
        else :     # self.douban_status == RETRY
            DebugLog("begin to check_movie_info")
            return self.rss.spider_douban()

    def save_movie(self):
        """
        0、暂停种子
        1、检查影片爬取信息
        2、移入或者更名至tobe目录下的目录文件夹
        3、保存种子文件到该目录，插入记录download表等
        4 下载poster.jpg文件    
        5、检查该目录并加入表
        6、更新豆瓣刮削信息到表movies
        7、把种子分类设为空  
        """
        
        DebugLog("begin save torrent:"+self.name)
        if self.stop() == False:
            ErrorLog("failed to stop torrent:"+self.name); return False
        
        #1、检查影片信息爬取
        if self.douban_status != OK:
            self.douban_status = RETRY
            if not self.check_movie_info():
                ExecLog("failed to spider movie info")
                return False
        DebugLog("{}|{}|{}|{}".format(self.movie_name,self.nation,self.douban_id,self.imdb_id))
        if self.movie_name == "" or self.nation == "" or (self.douban_id == "" and self.imdb_id == "") : ExecLog("empty name or nation or imdbid"); return False
        
        #2、移入或者更名至tobe目录下的目录文件夹 
        #2.1 组装目标文件夹名需要先获取Number和Copy
        Number = Copy = 0
        if self.douban_id != "":
            sel_sql = 'select number,copy from movies where doubanid = %s'
            sel_val = (self.douban_id,)
        else:
            sel_sql = 'select number,copy from movies where imdbid = %s'
            sel_val = (self.imdb_id,)
        SelectResult = select(sel_sql,sel_val)
        if SelectResult == None : 
            ErrorLog("error:select from movies")
            return False
        elif len(SelectResult) == 0: #说明不存在，需要获取max(number)+1
            sel_sql = 'select max(number) from movies'
            SelectResult = select(sel_sql,None)
            Number = SelectResult[0][0]+1
        elif len(SelectResult) == 1:
            Number = SelectResult[0][0]
            Copy   = SelectResult[0][1]
        else:
            #多条记录，有可能是正常的，也可能是异常的。先取第一条记录的Number,记录下日志，待手工检查
            ExecLog("2+ record in movies where imdbid = "+self.imdb_id)
            Number = SelectResult[0][0]
            for i in range(len(SelectResult)):
                if SelectResult[i][0] != Number: ErrorLog("diff number in case of same imdbid:"+self.imdb_id); break
        
        #2.2 组装新的目标文件夹名
        tTorrentName = re.sub(u"[\u4e00-\u9f50]+","",self.name) #去掉name中的中文字符
        tTorrentName = re.sub("[,。，·]+","",tTorrentName)       #去掉特殊标点符号
        tTorrentName = tTorrentName.strip()                         #去掉前后空格
        if tTorrentName[:1] == '.': tTorrentName = tTorrentName[1:] #去掉第一个.
        tTorrentName = re.sub(" ",".",tTorrentName)                 #空格替换为.
        #部分种子只有一个视频文件，name会以.mkv类似格式结尾
        if tTorrentName[-4:] == '.mp4' or tTorrentName[-4:] == '.mkv' or tTorrentName[-4:] == 'avi' or tTorrentName[-4:] == 'wmv': tTorrentName = tTorrentName[:-4]
        if Copy > 0 : DirName = str(Number).zfill(4)+'-'+str(Copy)+'-'+self.nation
        else        : DirName = str(Number).zfill(4)              +'-'+self.nation
        if   self.type == 0: DirName +=              '-'+self.movie_name+' '+tTorrentName
        elif self.type == 1: DirName += '-'+'电视剧'+'-'+self.movie_name+' '+tTorrentName
        elif self.type == 2: DirName += '-'+'纪录片'+'-'+self.movie_name+' '+tTorrentName
        else: ErrorLog("error type:"+self.type)

        #2.3 移动或者更名至目标文件夹
        tSaveDirName = os.path.join(self.save_path,self.name)
        tToBeDirName = os.path.join(TO_BE_PATH,self.name)
        DestDirName  = os.path.join(TO_BE_PATH,DirName)
        if os.path.exists(DestDirName):   ExecLog("dest dir exists:"+DestDirName)
        else:
            DebugLog("dest dir does not exists:"+DestDirName)
            if os.path.exists(tToBeDirName):  srcDirName = tToBeDirName  #从tobe目录中去改名
            else:                             srcDirName = tSaveDirName  #去原始保存目录移动到目标目录
            try:
                #原种子没有目录只是一个文件，那就新建目标目录，move函数就会把这个文件移动到目标目录
                if os.path.isfile(srcDirName): os.mkdir(DestDirName) 
                shutil.move(srcDirName,DestDirName)
            except Exception as err:
                ErrorLog("failed to mv dir:"+DestDirName)
                Print(err)
                return False
            else:  ExecLog("success mv dir to tobe:"+DestDirName)

        #3、保存torrent和resume文件至该目录
        if not self.save_torrent_file(DestDirName):
            ExecLog("failed to save torrent file:"+DestDirName)
            return False

        #4 下载poster.jpg文件
        DestFullFile=os.path.join(DestDirName,"poster.jpg")
        if self.rss.download_poster(DestDirName): ExecLog("success download poster file")
        else                                     : ErrorLog("failed to download poster.jpg from:"+self.poster)
            
        #5 检查该目录并加入表
        tMovie = Movie(TO_BE_PATH, DirName,"tobe")
        if tMovie.douban_id == "": tMovie.douban_id = self.douban_id
        if tMovie.imdb_id   == "": tMovie.imdb_id   = self.imdb_id
        if tMovie.check_movie() != 1: ErrorLog("failed to check:"+DirName)  ; return False
        else                        : ExecLog("success insert table movies")
        
        #6 更新信息至表movies
        up_sql = "update movies set DoubanID=%s,IMDBID=%s,DownloadLink=%s,HASH=%s where Number=%s and Copy=%s"
        up_val =(self.douban_id,self.imdb_id,self.download_link,self.hash, Number, Copy)
        if update(up_sql,up_val):
            ExecLog("success update table:"+DirName)
        else:
            ErrorLog("update error:"+DirName+":"+up_sql)
            return False
        
        #7 插入download表 
        if not self.insert_download(Number,Copy,tMovie.dir_name):
            ErrorLog("failed to insert table download:"+DestDirName)
            return False

        #8 把种子分类设为空    
        self.set_category("")
        return True

    def move_to_tr(self):
        """
        根据是否创建子文件夹(is_root_folder)分两种情况：
        一、创建了子文件夹：例如
            save_path = '2020-xx-xx xxx"
            files     =  xxxx.mkv
                         xxxx.nfo
            这个时候,在keep目录下创建链接到save_path,tr的save_path指向keep目录
        二、未创建子文件夹
            save_path = /BT/book"
            files     = kindle伴侣/xxx.txt
                        kindle伴侣/xxx.txt
            不创建链接，tr的save_path指向同一save_path即可
        """

        if not self.pause(): ErrorLog("failed to stop torrent:"+self.name)

        tTorrentFile = os.path.join(QB_BACKUP_DIR,self.hash+".torrent")
        if self.is_root_folder():
            tDestSavedPath = self.save_path
        else :   #为TR的保存路径创建链接
            if self.name[-4:] == '.mkv' : tLink = os.path.join(TR_KEEP_DIR,self.name[:-4])  #移除name中的.mkv后缀
            else                        : tLink = os.path.join(TR_KEEP_DIR,self.name)
            try:    
                if not os.path.exists(tLink) : os.symlink(os.path.realpath(self.save_path),tLink)
            except:
                ErrorLog("failed create link:ln -s "+os.path.realpath(self.save_path)+" "+tLink)
                return False            
            tDestSavedPath = TR_KEEP_DIR

        tTRClient = PTClient("TR")
        if tTRClient.connect() and tTRClient.add_torrent(torrent_file=tTorrentFile,download_dir=tDestSavedPath,is_paused=True):
            ErrorLog("failed to add torrent:"+tTorrentFile)
            return False               
        else:
            ExecLog("move torrent to tr:"+tr_torrent.name+'::'+tr_torrent.hashString)
            time.sleep(5)

        if not self.set_category(""):
            ErrorLog("failed to set category:"+self.name)
            return False
        return True

    def save_torrent_file(self,mDestDir):
        if self.client == 'QB':
            tTorrentFile = os.path.join(QB_BACKUP_DIR,self.hash+".torrent")
            tResumeFile  = os.path.join(QB_BACKUP_DIR,self.hash+".fastresume")
        else:
            tTorrentFile = os.path.join(os.path.join(TR_BACKUP_DIR,'torrents/'),self.name+'.'+self.hash[:16]+'.torrent')
            tResumeFile  = os.path.join(os.path.join(TR_BACKUP_DIR,'resume/'),self.name+'.'+self.hash[:16]+'.resume')
        tDestTorrentFile = os.path.join(mDestDir,self.name+'.'+self.hash[:16]+".torrent")
        tDestResumeFile  = os.path.join(mDestDir,self.name+'.'+self.hash[:16]+".resume")
        try:
            shutil.copyfile(tTorrentFile,tDestTorrentFile)
            shutil.copyfile(tResumeFile ,tDestResumeFile)
        except:
            ErrorLog("failed to copy torrent and resume file:"+self.hash)
            return False

        # 创建download.txt，写入hash和download_link
        fullFileName = os.path.join(mDestDir,"download.txt")
        if os.path.isfile(fullFileName):
            try:
                os.remove(fullFileName)
            except:
                print("failed to remove :"+fullFileName)
                return False
        fo = open(fullFileName,"a+")
        fo.write(self.hash+"|"+self.download_link)
        fo.close()
        return True

    def insert_download(self,mNumber,mCopy,mDirName): 
        tSelectResult = select("select downloadlink,number,copy from download where hash=%s",(self.hash,))
        if tSelectResult == None:
            ErrorLog("failed to exec select download")
            return False

        if len(tSelectResult) > 0:
            DebugLog("download exists:"+self.hash)    
            up_sql = "update download set downloadlink=%s,number=%s,copy=%s,dirname=%s where hash=%s"
            up_val = (self.download_link,mNumber,mCopy,mDirName,self.hash)
            if update(up_sql,up_val):
                DebugLog("update download success")
                return True
            else:
                ErrorLog("error:"+up_sql+"::"+self.hash)
                return False
        else:
            in_sql = "insert into download(downloadlink,number,copy,dirname,hash) values(%s,%s,%s,%s,%s)"
            in_val = (self.download_link,mNumber,mCopy,mDirName,self.hash)
            if insert(in_sql,in_val):
                DebugLog("insert download success")
                return True
            else:
                ErrorLog("error:"+up_sql+"::"+self.hash)
                return False




