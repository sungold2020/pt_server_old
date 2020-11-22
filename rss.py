#!/usr/bin/python3
# coding=utf-8
import traceback
import requests
import re
import codecs 
from bs4 import BeautifulSoup

from database import *
from log import *
from info import *
from torrent_info import *
from ptsite import *
class RSS:
    def __init__(self,HASH='',rss_name='',download_link='',detail_url='',title='',douban_id="",imdb_id="",add_datetime="",total_size=0,id_status=RETRY):
        self._HASH         = HASH
        self.rss_name      = rss_name
        self._download_link = download_link
        self._detail_url   = detail_url
        self.title         = title
        self._add_datetime = add_datetime if add_datetime != "" else datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self._total_size   = total_size

        self.downloaded = 0
        self.torrent_id = self.get_torrent_id(download_link)

        self.info = None
        douban_id    = Info.check_douban_id(douban_id)
        imdb_id      = Info.check_imdb_id(imdb_id)
        self._id_status    = id_status
        self.id_from_detail = self._id_status
        self.retry_times   = 0    

        self._torrent_name = ""
        self._files = []

        #(verify id_status)
        if (douban_id == "" and imdb_id == "") and self._id_status == OK: self.id_status = RETRY; ErrorLog("id is empty,but id_status is ok:"+self.title);
        if (douban_id != "" or  imdb_id != "") and self._id_status != OK: self._id_status = OK; ErrorLog("id is not empty,but id_status is not ok:"+self.title);
        #get id
        if douban_id == "" and imdb_id == "": 
            if self.id_status == RETRY:  self.get_id_from_detail()
        else:  #get douban_info
            self.info = Info(douban_id,imdb_id)    

        #如果HASH或者total_size为空就通过下载种子文件并获取相关信息
        if self._total_size == 0 or self._HASH == "": self.get_torrent_info()

        #如果rss_name空，尝试读取rss表获取记录
        if self.rss_name == "": self.select_by_hash()


    @property
    def download_link(self):
        #pthome的downloadlink是临时链接，转换为带passkey的下载链接
        if self.rss_name.lower().startswith("pthome"): return NexusPage.get_download_link(self.rss_name,self.torrent_id)
        return self._download_link
    @download_link.setter
    def download_link(self,download_link):
        self._download_link = download_link

    @property
    def detail_url(self):
        """
        两种情况：
        1、detail_url为空，根据torrent_id去组装detail_url;
        2、detail_url缺网站名(例如:details?id=xxx),则需要补充完整detail_url
        """
        if self._detail_url == "": self._detail_url =  NexusPage.get_detail_url(self.rss_name,self.torrent_id) 
        if not self._detail_url.startswith("http"): 
            self._detail_url = NexusPage.complete_detail_url(self.rss_name,self._detail_url)
        return self._detail_url
    @detail_url.setter
    def detail_url(self,detail_url):
        self._detail_url = detail_url

    @property
    def HASH(self):
        if self._HASH == "": ErrorLog("error:_HASH is null:"+self.name)
        return self._HASH
    @HASH.setter
    def HASH(self,HASH):
        if HASH == "": ErrorLog("error:HASH is null:"+self.name)
        self._HASH = HASH

    @property
    def douban_id(self):
        return self.info.douban_id if self.info != None else ""
    @property
    def imdb_id(self):
        return self.info.imdb_id if self.info != None else ""

    @property
    def total_size(self):
        return self._total_size
    @total_size.setter
    def total_size(self,total_size):
        self._total_size = total_size
    @property
    def torrent_name(self):
        if self._torrent_name == "": self.get_torrent_info()
        return self._torrent_name
    @property
    def name(self): #中文电影名+torrent_name
        if self.torrent_name == "": return self.title
        if self.movie_name == ""  : return self.torrent_name
        #如果torrent_name前10个字符中包含了中文，就认为包含了中文电影名，否则认为未包含
        return self.torrent_name  if re.search(u"[\u4e00-\u9f50]+",self.torrent_name[:10]) != None else self.movie_name+self.torrent_name

    @property
    def files(self):
        if self._files == "": self.get_torrent_info()
        return self._files
    @property
    def add_datetime(self):
        return self._add_datetime
    @property
    def id_status(self):
        return self._id_status
    @id_status.setter
    def id_status(self,id_status):
        DebugLog(f"set id_status:{id_status}|{self.title}")
        self._id_status = id_status


    @property
    def douban_status(self):
        return self.info.douban_status if self.info != None else RETRY
    @douban_status.setter
    def douban_status(self,douban_status):
        if self.info != None : self.info.douban_status = douban_status
    @property
    def douban_score(self):
        return self.info.douban_score if self.info != None else ""
    @douban_score.setter
    def douban_score(self,douban_score):
        if self.info != None : self.info.douban_score = douban_score
    @property
    def imdb_score(self):
        return self.info.imdb_score if self.info != None else ""
    @imdb_score.setter
    def imdb_score(self,imdb_score):
        if self.info != None : self.info.imdb_score = imdb_score
    @property
    def director(self):
        return self.info.director if self.info != None else ""
    @property
    def actors(self):
        return self.info.actors if self.info != None else ""
    @property
    def type(self):
        return self.info.type if self.info != None else MOVIE
    @property
    def poster(self):
        return self.info.poster if self.info != None else ""
    @property
    def nation(self):
        return self.info.nation if self.info != None else ""
    @property
    def movie_name(self):
        return self.info.movie_name if self.info != None else ""

    def download_poster(self,mPath):
        return self.info.download_poster(mPath) if self.info != None else False

    def spider_douban(self):
        if self.info == None: ErrorLog("spider douban,info is null:"+self.name); return False
        return self.info.spider_douban()
        
    def select(self,assign_value=True):
        if self.rss_name == "": return False
        if self._HASH != "":  #通过免费种子加入时，有torrent_id，无HASH
            sel_sql = "select title,downloadlink,detailurl,doubanid,imdbid,downloaded,torrentid,datetime,size from rss where rssname=%s and HASH=%s"
            sel_val = (self.rss_name,self.HASH)
            tSelectResult =  select(sel_sql,sel_val)
            tSQL = "select title,downloadlink,detailurl,torrentid,downloaded,datetime,size from rss where rssname={} and HASH={}".format(self.rss_name,self.HASH)
            if tSelectResult == None:
                ErrorLog("failed to exec :"+tSQL)
                return False
            if len(tSelectResult) == 0: return False
            elif len(tSelectResult) > 1: ErrorLog("find 2+record:"+tSQL); return False
            else: pass
            if assign_value == True:
                self.title         = tSelectResult[0][0]
                self.download_link = tSelectResult[0][1]
                self.detail_url    = tSelectResult[0][2]
                douban_id          = tSelectResult[0][3]
                imdb_id            = tSelectResult[0][4]
                self.downloaded    = tSelectResult[0][5]
                self.torrent_id    = tSelectResult[0][6]
                self.add_datettime = tSelectResult[0][7]
                self.total_size    = tSelectResult[0][8]
                if douban_id != "" or imdb_id != "": self.info = Info(douban_id,imdb_id)
            return True
        elif self.torrent_id != "":
            sel_sql = "select title,downloadlink,detailurl,doubanid,imdbid,HASH,downloaded,datetime,size from rss where rssname=%s and torrentid=%s"
            sel_val = (self.rss_name,self.torrent_id)
            tSelectResult =  select(sel_sql,sel_val)
            tSQL = "select title,download_link,detailurl,HASH,downloaded,datetime,size from rss where rssname={} and torrentid={}".format(self.rss_name,self.torrent_id)
            if tSelectResult == None:
                ErrorLog("failed to exec :"+tSQL)
                return False
            if len(tSelectResult) == 0: return False
            elif len(tSelectResult) > 1: ErrorLog("find 2+record:"+tSQL); return False
            else: pass
            if assign_value == True:
                self.title         = tSelectResult[0][0]
                self.download_link = tSelectResult[0][1]
                self.detail_url    = tSelectResult[0][2]
                douban_id          = tSelectResult[0][3]
                imdb_id            = tSelectResult[0][4]
                self.HASH          = tSelectResult[0][5]
                self.downloaded    = tSelectResult[0][6]
                self.add_datettime = tSelectResult[0][7]
                self.total_size    = tSelectResult[0][8]
                if douban_id != "" or imdb_id != "": self.info = Info(douban_id,imdb_id)
            return True
        else: return False
               
    def select_by_hash(self,assign_value=True):
        if self._HASH == "": return False 
        sel_sql = "select title,downloadlink,detailurl,doubanid,imdbid,downloaded,torrentid,datetime,size from rss where HASH=%s"
        sel_val = (self.HASH,)
        tSelectResult =  select(sel_sql,sel_val)
        tSQL = "select title,downloadlink,detailurl,torrentid,downloaded,datetime,size from rss where HASH={}".format(self.HASH)
        if tSelectResult == None:
            ErrorLog("failed to exec :"+tSQL)
            return False
        if len(tSelectResult) == 0: return False
        if len(tSelectResult) > 1: ExecLog("find 2+record:"+tSQL)
        if assign_value == True:
            self.title         = tSelectResult[0][0]
            self.download_link = tSelectResult[0][1]
            self.detail_url    = tSelectResult[0][2]
            douban_id          = tSelectResult[0][3]
            imdb_id            = tSelectResult[0][4]
            self.downloaded    = tSelectResult[0][5]
            self.torrent_id    = tSelectResult[0][6]
            self.add_datettime = tSelectResult[0][7]
            self.total_size    = tSelectResult[0][8]
            if douban_id != "" or imdb_id != "": self.info = Info(douban_id,imdb_id)
        return True

    def insert(self):
        if self.HASH == "" or self.rss_name == "": return None

        in_sql = "insert into rss(rssname,HASH,title,downloadlink,detailurl,torrentid,doubanid,imdbid,datetime,downloaded,size) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
        in_val = (self.rss_name,self.HASH,self.title,self.download_link,self.detail_url,self.torrent_id,self.douban_id,self.imdb_id,self.add_datetime,self.downloaded,self.total_size)
        return insert(in_sql,in_val)

    def update(self):
        if self.rss_name == "": ExecLog("rss_name is null:"+self.name); return False
        if self._HASH != "":
            up_sql = "update rss set title=%s,downloadlink=%s,detailurl=%s,torrentid=%s,doubanid=%s,imdbid=%s,downloaded=%s,datetime=%s,size=%s where rssname=%s and HASH=%s"
            up_val = (self.title,self.download_link,self.detail_url,self.torrent_id,self.douban_id,self.imdb_id,self.downloaded,self.add_datetime,self.total_size,self.rss_name,self.HASH)
        elif self.torrent_id != "":
            up_sql = "update rss set title=%s,downloadlink=%s,detailurl=%s,torrentid=%s,doubanid=%s,imdbid=%s,downloaded=%s,datetime=%s,size=%s where rssname=%s and torrentid=%s"
            up_val = (self.title,self.download_link,self.detail_url,self.torrent_id,self.douban_id,self.imdb_id,self.downloaded,self.add_datetime,self.total_size,self.rss_name,self.torrent_id)
        else:
            ErrorLog("HASH and torrent_id is null to update:"+self.title)
            return False
        return update(up_sql,up_val)

    def update_or_insert(self):
        if self.HASH == "" or self.rss_name == "": return None

        if self.select(assign_value=False): return self.update()
        else            : return self.insert()

    def update_downloaded(self):
        if self.downloaded != 1:
            self.downloaded = 1
            ExecLog("update rsstable:"+self.name)
            return self.update()
        return True


    def get_torrent_info(self):
        if self.download_link == "": return False

        torrent_info = RSS.download_torrent_file(self.download_link,self._HASH)
        if torrent_info == None:
            ErrorLog("failed to get info:"+self.download_link)
            return False

        self._HASH         = torrent_info.info_hash
        self._total_size   = torrent_info.total_size
        self._torrent_name = torrent_info.name
        self._files        = torrent_info.files
        DebugLog(f"_HASH      :{self._HASH}")
        DebugLog(f"_name      :{self._torrent_name}")
        DebugLog(f"_total_size:{self._total_size}")
        return True

    def get_id_from_detail(self):
        """
        从
        :return:
        """
        if self.id_from_detail == NOK: return NOK

        if self.douban_id != "" or self.imdb_id != "": return OK
        #TODO to delete
        if self.rss_name == "" or self.torrent_id == "": return NOK

        if self.retry_times >= 2: 
            ExecLog("2 times for get id from detail:"+self.name)
            self.id_from_detail = NOK; return NOK
        
        if self.id_from_detail != RETRY: return self.id_from_detail

        return_code,douban_id,imdb_id = NexusPage.get_id_from_detail(self.rss_name,self.detail_url)
        if return_code == NOK :  
            ExecLog("can't find id from detail:"+self.name)
            ExecLog("                         :"+self.detail_url)
            self.id_from_detail = NOK
            return NOK #不在这里设id_status为NOK，还有可能从nfo获取
        if return_code == RETRY: self.retry_times += 1; return RETRY
        DebugLog("find id from detail:{}|{}|{}".format(douban_id,imdb_id,self.title))
        self.set_id(douban_id,imdb_id)
        self.id_from_detail = OK
        return OK
        
    def set_id(self,douban_id,imdb_id):
        if douban_id == "" and imdb_id == "": return False
        self.info = Info(douban_id,imdb_id)
        # 写入id到数据库
        self.id_status = OK
        if not self.update(): ExecLog("failed to update rss:"+self.name); return False
        return True
        

    @staticmethod
    def get_torrent_id(mDownloadLink):
        tTorrentID = ""
        if mDownloadLink == "": return ""
        tIndex = mDownloadLink.find("id=")
        if tIndex == -1: DebugLog("failed to find torrentid starttag(id=):"+mDownloadLink) ;return ""
        tTorrentID = mDownloadLink[tIndex+3:]
        tIndex = tTorrentID.find("&")
        if tIndex == -1: DebugLog("failed to find torrentid endtag(&):"+mDownloadLink); return ""
        return tTorrentID[:tIndex]


    @staticmethod
    def old_rss(HASH,rss_name):
        tReturn = select('select title from rss where rssname=%s and hash=%s',(rss_name,HASH))
        return False if tReturn == None or len(tReturn) == 0 else True

    @staticmethod
    def old_free(torrent_id,rss_name):
        tReturn = select('select title from rss where rssname=%s and torrentid=%s',(rss_name,torrent_id))
        return False if tReturn == None or len(tReturn) == 0 else True


    @staticmethod
    def download_torrent_file(download_link,HASH=""):
        """
        根据下载链接，下载种子文件，获取hash值，并按照hash.torrent名称保存到配置给定的目录
        返回值: torrent_info 失败返回None
        """

        torrent_file = os.path.join(os.path.abspath(TORRENTS_DIR),HASH+'.torrent')
        if HASH != "" and os.path.exists(torrent_file):
            DebugLog(f"hash对应的种子已经存在:{torrent_file}")
            torrent_info = torrentool.api.Torrent.from_file(torrent_file)
            if torrent_info.info_hash == None: 
                ErrorLog(f"获取到的hash为空:{torrent_file}")
                return None
            return torrent_info   

        #下载种子文件
        temp_torrent_file =os.path.join(os.path.abspath(TORRENTS_DIR),'temp.torrent')
        try:
            f=requests.get(download_link,timeout=120)
            with open(temp_torrent_file ,"wb") as code:
                code.write(f.content)
        except Exception as err:
            Print(err)
            DebugLog("failed to download torrent file from:"+download_link)
            return None
        else : 
            DebugLog("success download torrent file from:"+download_link)

        #获取torrent（包含hash等信息）
        try:
            torrent_info = torrentool.api.Torrent.from_file(temp_torrent_file)
        except Exception as err:
            print(err)
            ExecLog(f"can't get torrent_info from {temp_torrent_file}")
            return None
        if torrent_info == None or torrent_info.info_hash == None: return None

        #改名hash.torrent
        torrent_file = os.path.join(os.path.abspath(TORRENTS_DIR),torrent_info.info_hash+'.torrent')
        try:
            os.rename(temp_torrent_file,torrent_file)
        except Exception as err:
            print(err)
            ErrorLog("error: rename {} to {}".format(temp_torrent_file,torrent_file))
            return ""
        return torrent_info
