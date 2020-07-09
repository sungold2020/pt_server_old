import os
import shutil
import re
import requests
from gen import Gen

from movie import *
from log import *
from rss import RSS
from torrent import *
from info import *
from ptsite import *

DOWNLOAD_FOLDER = "/media/root/BT/movies"
TO_BE_PATH = "/media/root/BT/tobe/"           #保存的电影所在临时目录
TR_KEEP_DIR = "/media/root/BT/keep/"

#QB的备份目录BT_backup，我的运行环境目录如下，如有不同请搜索qbittorrent在不同OS下的配置
QB_BACKUP_DIR  = "/root/.local/share/data/qBittorrent/BT_backup"
TR_BACKUP_DIR = "/root/.config/transmission"

#转移做种以后，把种子文件和快速恢复文件转移到QBTorrentsBackupDir目录进行保存，以备需要
QB_TORRENTS_BACKUP_DIR = "data/qb_backup"   
TR_TORRENTS_BACKUP_DIR = "data/tr_backup"   

TO_BE_ADD   =  0
TO_BE_START =  1
STARTED     =  2
MOVED       =  3         

class MyTorrent:

    def __init__(self,torrent=None,rss=None,info=None,add_status=TO_BE_ADD):
        
        self.torrent = torrent if torrent != None else Torrent("QB",None)
        self.rss = rss      if rss != None else RSS()
        self.info = info    if info != None else Info()

        self.add_status = add_status
        self.checked = 1              #每次检查时用于标记它是否标记到，检查结束后，如果发现Checked为0，说明种子已经被删除。
                                      #新建对象时肯定Checked=1
        if self.HASH == "" :  self.HASH = self.hash

    #------------- begin rss------------------------------
    @property
    def rss_name(self):
        if self.rss == None: return ""
        else               : return self.rss.rss_name
    @rss_name.setter
    def rss_name(self,rss_name):
        self.rss.rssname = rss_name
    @property
    def HASH(self):
        if self.rss == None: return ""
        else               : return self.rss.HASH
    @HASH.setter
    def HASH(self,HASH):
        self.rss.HASH = HASH
    @property
    def download_link(self):
        if self.rss == None: return ""
        else               : return self.rss.download_link
    @download_link.setter
    def download_link(self,download_link):
        self.rss.download_link = download_link
    @property
    def title(self):
        if self.rss == None: return ""
        else               : return self.rss.title
    @title.setter
    def title(self,title):
        self.rss.title = title
    @property
    def torrent_id(self):
        if self.rss == None: return ""
        else               : return self.rss.torrent_id
    @torrent_id.setter
    def torrent_id(self,torrent_id):
        self.rss.torrent_id = torrent_id
    @property
    def add_date(self):
        if self.rss == None: return ""
        else               : return self.rss.add_date
    @add_date.setter
    def add_date(self,add_date):
        self.rss.add_date = add_date
    @property
    def downloaded(self):
        if self.rss == None: return 0
        else               : return self.rss.downloaded
    @downloaded.setter
    def downloaded(self,downloaded):
        self.rss.downloaded = downloaded
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
        if self.torrent == None: return ""
        else               : return self.torrent.progress
    @property
    def status(self):
        if self.torrent == None: return ""
        else               : return self.torrent.status
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
        if self.torrent == None: return ""
        else               : return self.torrent.add_datetime
    @property
    def tracker(self):
        if self.torrent == None: return ""
        else               : return self.torrent.tracker
    @property
    def uploaded(self):
        if self.torrent == None: return ""
        else               : return self.torrent.uploaded
    @property
    def total_size(self):
        if self.torrent == None: return 0
        else               : return self.torrent.total_size
    @property
    def files(self):
        if self.torrent == None: return []
        else               : return self.torrent.files
    #重定义函数
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

    def check_files(self,mIsNewDay):
        if self.torrent == None: return False
        else               : return self.torrent.check_files(mIsNewDay)
    def is_low_upload(self,mNumberOfDays,mUploadThreshold):
        if self.torrent == None: return False
        else               : return self.torrent.is_low_upload(mNumberOfDays,mUploadThreshold)
    #------------------end torrent-------------------

    #------------------begin info-------------------
    @property
    def douban_id(self):
        if self.info == None: return ""
        else                : return self.info.douban_id
    @douban_id.setter
    def douban_id(self,douban_id):
        self.info.douban_id = douban_id
        self.rss.douban_id = douban_id

    @property
    def imdb_id(self):
        if self.info == None: return ""
        else                : return self.info.imdb_id
    @imdb_id.setter
    def imdb_id(self,imdb_id):
        self.info.imdb_id = imdb_id
        self.rss.imdb_id = imdb_id

    @property
    def spider_status(self):
        if self.info == None: return 0
        else                : return self.info.spider_status
    @spider_status.setter
    def spider_status(self,spider_status):
        self.info.spider_status = spider_status

    @property
    def douban_score(self):
        if self.info == None: return ""
        else                : return self.info.douban_score
    @douban_score.setter
    def douban_score(self,douban_score):
        self.info.douban_score = douban_score

    @property
    def imdb_score(self):
        if self.info == None: return ""
        else                : return self.info.imdb_score
    @imdb_score.setter
    def imdb_score(self,imdb_score):
        self.info.imdb_score = imdb_score

    @property
    def douban_link(self):
        if self.info == None: return ""
        else                : return self.info.douban_link
    @douban_link.setter
    def douban_link(self,douban_link):
        self.info.douban_link = douban_link

    @property
    def imdb_link(self):
        if self.info == None: return ""
        else                : return self.info.imdb_link
    @imdb_link.setter
    def imdb_link(self,imdb_link):
        self.info.imdb_link = imdb_link

    @property
    def movie_name(self):
        if self.info == None: return ""
        else                : return self.info.movie_name
    @movie_name.setter
    def movie_name(self,movie_name):
        self.info.movie_name = movie_name

    @property
    def type(self):
        if self.info == None: return ""
        else                : return self.info.type
    @type.setter
    def type(self,mType):
        self.info.type = mType

    @property
    def nation(self):
        if self.info == None: return ""
        else                : return self.info.nation
    @nation.setter
    def nation(self,nation):
        self.info.nation = nation

    @property
    def douban_status(self):
        if self.info == None: return ""
        else                : return self.info.douban_status
    @douban_status.setter
    def douban_status(self,douban_status):
        self.info.douban_status = douban_status

    @property
    def douban_retry_times(self):
        if self.info == None: return ""
        else                : return self.info.douban_retry_times
    @douban_retry_times.setter
    def douban_retry_times(self,douban_retry_times):
        self.info.douban_retry_times = douban_retry_times

    @property
    def foreign_name(self):
        if self.info == None: return ""
        else                : return self.info.foreign_name

    @property
    def other_names(self):
        if self.info == None: return ""
        else                : return self.info.other_names

    @property
    def director(self):
        if self.info == None: return ""
        else                : return self.info.director
    @property
    def actors(self):
        if self.info == None: return ""
        else                : return self.info.actors

    @property
    def episodes(self):
        if self.info == None: return ""
        else                : return self.info.episodes
    @property
    def poster(self):
        if self.info == None: return ""
        else                : return self.info.poster
    @property
    def genre(self):
        if self.info == None: return ""
        else                : return self.info.genre
    #------------------end info--------------------------------

    def start_download(self):
        if self.torrent == None: ExecLog("torrent does not exist"); return False
        tBTStat =  os.statvfs(DOWNLOAD_FOLDER)
        tFreeSize = (tBTStat.f_bavail * tBTStat.f_frsize) /(1024*1024*1024)
        #DebugLog("free size:"+str(tFreeSize))
        tSize = self.total_size /(1024*1024*1024)
        #DebugLog("Size:"+str(tSize))
        if tFreeSize < tSize+1 :ExecLog("diskspace is not enough"); return False
        if  self.resume() and self.set_category("下载"):
            ExecLog("start download:"+self.name)
        else:
            ExecLog("failed to start torrent:"+self.name)
            return False
        if self.rss.rss_name != "":
            self.rss.downloaded == 1
            if self.rss.update():
                ExecLog("success to update rss:"+self.name)
                return True
            else:   
                ExecLog("failed to update rss:"+self.name+':'+self.HASH)
                return False
        else: return True

    def get_id_from_nfo(self):

        if self.progress != 100: 
            ErrorLog("begin to get id from nfo,but torrent have not done.")
            return False

        #检查下有没有nfo文件
        tNfoFileName = ""
        tFiles = self.files
        for tFile in tFiles:
            if tFile['name'][-4:].lower() == '.nfo' :
                tNfoFileName = os.path.join(self.save_path,tFile['name'])
                ExecLog("success find nfo file:"+self.name)
                break
        if tNfoFileName == "": ExecLog("can't find nfo file:"+self.name); return False
        
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
        self.douban_link = DoubanLink
        self.imdb_link = IMDBLink
        self.douban_id = get_id_from_link(DoubanLink,DOUBAN)
        self.imdb_id   = get_id_from_link(IMDBLink,IMDB)
        DebugLog("DoubanLink:{} :: IMDBLink:{}".format(DoubanLink,IMDBLink))
        ExecLog("find DoubanID:{} :: IMDBID:{}".format(self.douban_id,self.imdb_id))
        if self.douban_id == "" and self.imdb_id == "": return False
        else                                          : return True

    def get_id_from_rss(self):

        sel_sql = "select doubanid,imdbid,rssname from rss where hash=%s"
        sel_val = (self.hash,)
        tReturn = select(sel_sql,sel_val)
        if tReturn == None or len(tReturn) == 0: 
            DebugLog("failed to find id from rss:{}|{}".format(self.rss_name,self.hash))
            return False
        else: 
            for tResult in tReturn:
                if tResult[0] != "": self.douban_id = tResult[0]
                if tResult[1] != "": self.imdb_id   = tResult[1]
            if self.douban_id != "" or self.imdb_id != "": return True
            else: return False
    
    def spider_movie_info(self):
        if self.spider_status != RETRY: return self.spider_status

        DebugLog("begin to spider_movie_info")
        if self.douban_id == "" and self.imdb_id == "":
            if self.progress == 100:
                if self.get_id_from_rss():
                    ExecLog("find id from rss:{}::{}".format(self.douban_id,self.imdb_id))
                else:
                    if self.get_id_from_nfo():
                        ExecLog("find id from nfo:{}::{}".format(self.douban_id,self.imdb_id))
                    else:
                        # TODO get id from detail
                        if self.spider_detail(): 
                            ExecLog("find id from detail:{}::{}".format(self.douban_id,self.imdb_id))
                        else:
                            DebugLog("failed to get id from nfo")
                            self.spider_status = NOK
                            return self.spider_status
            else: 
                DebugLog("torrent have not done")
                return self.spider_status

        if self.info.select():    #尝试从info表中获取记录
            ExecLog("find a record from nfo")
        if self.spider_status == OK: return self.spider_status

        if self.douban_status == RETRY:
            tReturn = self.info.spider_douban()
            if tReturn == OK: 
                DebugLog("success to spider douban")
                self.info.spider_status = OK
                #return self.spider_status
            elif tReturn == RETRY:
                DebugLog("retry to spider douban again")
                return self.spider_status
            else: # NOK
                DebugLog("failed to spider douban")
                pass

        # 必要信息已经具备
        if self.movie_name != "" and self.nation != "" and self.imdb_id != "":
            DebugLog("name nation imdbid exist")
            self.spider_status = OK
        else:
            ExecLog("failed to spider movie info")
            self.spider_status = NOK
        self.info.update_or_insert()  #更新或者插入到表info
        return self.spider_status

    def spider_detail(self):

        if self.torrent_id == "": return False

        tSite = None
        for site in NexusPage.site_list:
            if self.rss_name == site['name']: 
                tSite = site
                break
            else:
                continue
        if tSite == None : ExecLog("unknown site name:"+self.rss_name); return False
        DebugLog("find site:{}".format(tSite['name']))
                    
        tPage = NexusPage(tSite)
        if not tPage.request_detail_page(self.torrent_id):
            #ExecLog(tPage.error_string)
            return False    

        self.copy_info(tPage.info)
        if self.imdb_id != "" or self.douban_id != "": return True
        else                                         : return False
        

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
        if self.spider_status != OK:
            self.spider_status = RETRY
            if not self.spider_movie_info():
                ExecLog("failed to spider movie info")
                return False
        if self.movie_name == "" or self.nation == "" or self.imdb_id == "" : ExecLog("empty name or nation or imdbid"); return False
        
        #2、移入或者更名至tobe目录下的目录文件夹 
        #2.1 组装目标文件夹名需要先获取Number和Copy
        Number = Copy = 0
        sel_sql = 'select number,copy from movies where imdbid = %s'
        sel_val = (self.imdb_id,)
        SelectResult = select(sel_sql,sel_val)
        if SelectResult == None : 
            ExecLog("error:select max(number) from movies")
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
            ExecLog("2+ record in movies where imdbid = "+IMDBID)
            Number = SelectResult[0][0]
            for i in range(len(SelectResult)):
                if SelectResult[i][0] != Number: ErrorLog("diff number in case of same imdbid:"+self.imdb_id); break
        
        #2.2 组装新的目标文件夹名
        tTorrentName = re.sub(u"[\u4e00-\u9f50]+","",self.name) #去掉name中的中文字符
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
        if not self.insert_download(Number,Copy):
            ExecLog("failed to insert table download:"+DestDirName)
            return False

        #4 下载poster.jpg文件
        DestFullFile=os.path.join(DestDirName,"poster.jpg")
        try:
            f=requests.get(self.poster)
            with open(DestFullFile,"wb") as code:
                code.write(f.content)
        except Exception as err:
            Print(err)
            ErrorLog("failed to download poster.jpg from:"+self.poster)
        else : ExecLog("success download jpg file")

        #5 检查该目录并加入表
        tMovie = Movie(TO_BE_PATH, DirName)
        if tMovie.CheckMovie() != 1      :  ErrorLog("failed to check:"+DirName)  #; continue，继续插入表
        if tMovie.CheckTable("tobe") != 1:  ErrorLog("faied to table:"+DirName); return False
        else : ExecLog("success insert table movies")
        
        #6 更新信息至表movies
        up_sql = "update movies set DoubanID=%s,IMDBID=%s,DownloadLink,HASH=%s where Number=%s and Copy=%s"
        up_val =(self.douban_id,self.imdb_id,self.download_link,self.hash, Number, Copy)
        if update(up_sql,up_val):
            ExecLog("success update table:"+DirName)
        else:
            ErrorLog("update error:"+DirName+":"+up_sql)
            return False
        
        #7 把种子分类设为空    
        self.set_category("")
        return True

    def move_to_tr(self,mTRLogin):
    
        # TODO

        if not self.pause(): ExecLog("failed to stop torrent:"+self.name)
        
        #备份转移种子的torrent文件和fastresume文件
        tTorrentFile = os.path.join(QB_BACKUP_DIR,qb_torrent.hash+".torrent")
        tDestTorrentFile = os.path.join(QBTorrentsBackupDir,qb_torrent.hash+".torrent")
        tResumeFile  = os.path.join(QB_BACKUP_DIR,qb_torrent.hash+".fastresume")
        tDestResumeFile  = os.path.join(QBTorrentsBackupDir,qb_torrent.hash+".fastresume")
        try:
            shutil.copyfile(tTorrentFile,tDestTorrentFile)
            shutil.copyfile(tResumeFile ,tDestResumeFile)
        except:
            #Print(tTorrentFile)
            #Print(tResumeFile)
            #Print(tDestTorrentFile)
            ErrorLog("failed to copy torrent and resume file:"+gTorrentList[i].HASH)
            return False
        else: ExecLog("success backup torrent file to :"+QB_BACKUP_DIR)


        #Print(str(gTorrentList[i].IsRootFolder)+'|'+gTorrentList[i].SavedPath+'|'+gTorrentList[i].RootFolder+'|'+gTorrentList[i].DirName)
        #for file in gTorrentList[i].FileName: Print(file)
        tNoOfList = FindTorrent(QB,qb_torrent.hash)
        if tNoOfList < 0 : ErrorLog("not find in torent list:"+qb_torrent.hash); return False

        Print(gTorrentList[tNoOfList].IsRootFolder)
        Print(gTorrentList[tNoOfList].RootFolder)
        Print(gTorrentList[tNoOfList].SavedPath)
        if gTorrentList[tNoOfList].IsRootFolder == True :   tDestSavedPath = os.path.realpath(gTorrentList[tNoOfList].SavedPath)
        else :   #为TR的保存路径创建链接
            if gTorrentList[tNoOfList].Name[-4:] == '.mkv' : gTorrentList[tNoOfList].Name = gTorrentList[tNoOfList].Name[:-4] #移除.mkv
            tLink = os.path.join(TRSeedFolderList[0],gTorrentList[tNoOfList].Name) 
            try:    
                if not os.path.exists(tLink) : os.symlink(os.path.realpath(gTorrentList[tNoOfList].SavedPath),tLink)
            except:
                ErrorLog("failed create link:ln -s "+os.path.realpath(gTorrentList[tNoOfList].SavedPath)+" "+tLink)
                return False            
            tDestSavedPath = TRSeedFolderList[0]
        #TR加入种子
        try:
            tr_client = transmissionrpc.Client(TR_IP, port=TR_PORT,user=TR_USER,password=TR_PWD)
            tr_torrent = tr_client.add_torrent(torrent=tTorrentFile,download_dir=tDestSavedPath,paused=True)
        except ValueError as err:
            Print(err)
            ErrorLog("failed to add torrent:"+tTorrentFile)
            return False
        except  transmissionrpc.TransmissionError as err:
            Print(err)
            ErrorLog("failed to add torrent:"+tTorrentFile)
            return False            
        except transmissionrpc.HTTPHandlerError as err:
            Print(err)
            ErrorLog("failed to add torrent:"+tTorrentFile)
            return False               
        else:
            ExecLog("move torrent to tr:"+tr_torrent.name+'::'+tr_torrent.hashString)
        #QB设置类别为""
        try: qb_torrent.set_category("")
        except: ErrorLog("failed to set category:"+gTorrentList[tNoOfList].Name)
        else: gTorrentList[tNoOfList].Category = ""

        return True

    def copy_info(self,tInfo):
        self.douban_id = tInfo.douban_id
        self.imdb_id = tInfo.imdb_id
        self.douban_score = tInfo.douban_score
        self.imdb_score = tInfo.imdb_score
        self.douban_link = tInfo.douban_link
        self.imdb_link = tInfo.imdb_link
        self.movie_name = tInfo.movie_name
        self.foreign_name = tInfo.foreign_name
        self.other_names = tInfo.other_names
        self.type = tInfo.type     
        self.nation = tInfo.nation
        self.year = tInfo.year
        self.director = tInfo.director
        self.actors = tInfo.actors
        self.poster = tInfo.poster
        self.episodes = tInfo.episodes
        self.genre = tInfo.genre

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

        fo = open(fullFileName,"w+")
        fo.write(self.hash+"|"+self.download_link)
        fo.close()
        return True

    def insert_download(self,mNumber,mCopy):
        
        tSelectResult = select("select downloadlink,number,copy from download where hash=%s",(self.hash,))
        if tSelectResult == None:
            ErrorLog("failed to exec select download")
            return False

        if len(tSelectResult) > 0:
            DebugLog("download exists:"+self.hash)
            
            up_sql = "update download set downloadlink=%s,number=%s,copy=%s where hash=%s"
            up_val = (self.download_link,mNumber,mCopy,self.hash)
            if update(up_sql,up_val):
                DebugLog("update download success")
                return True
            else:
                ErrorLog("error:"+up_sql+"::"+self.hash)
                return False
        else:
            in_sql = "insert into download(downloadlink,number,copy,hash) values(%s,%s,%s,%s)"
            in_val = (self.download_link,mNumber,mCopy,self.hash)
            if insert(in_sql,in_val):
                DebugLog("insert download success")
                return True
            else:
                ErrorLog("error:"+up_sql+"::"+self.hash)
                return False



