#!/usr/bin/python3
# coding=utf-8
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
    def __init__(self,HASH='',rss_name='',download_link='',title='',douban_id="",imdb_id="",add_datetime="",total_size=0,id_status=RETRY):
        self._HASH         = HASH
        self.rss_name      = rss_name
        self.download_link = download_link
        self.title         = title
        self._add_datetime = add_datetime if add_datetime != "" else datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self._total_size   = total_size

        self.torrent_id    = self.get_torrent_id(self.download_link)
        if rss_name.lower().startswith("pthome"): self.download_link = NexusPage.get_download_link(self.rss_name,self.torrent_id)
        self.downloaded = 0


        self.info = None
        douban_id    = Info.check_douban_id(douban_id)
        imdb_id      = Info.check_imdb_id(imdb_id)
        self._id_status    = id_status
        self.retry_times   = 0    

        #(verify id_status)
        if (douban_id == "" and imdb_id == "") and self._id_status == OK: self.id_status = RETRY; ErrorLog("id is empty,but id_status is ok:"+self.title);
        if (douban_id != "" or  imdb_id != "") and self._id_status != OK: self._id_status = OK; ErrorLog("id is not empty,but id_status is not ok:"+self.title);
        #get id
        if douban_id == "" and imdb_id == "": 
            if self.id_status == RETRY:  self.get_id_from_detail()
        else:  #get douban_info
            self.info = Info(douban_id,imdb_id)    

        if self._total_size == 0: self.get_torrent_info()
        self._name = ""
        self._files = []

    @property
    def HASH(self):
        if self._HASH == "": ErrorLog("error:_HASH is null:"+self.title)
        return self._HASH
    @HASH.setter
    def HASH(self,HASH):
        if HASH == "": ErrorLog("error:HASH is null:"+self.title)
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
    def name(self):
        if self._name == "": self.get_torrent_info()
        return self._name
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
        DebugLog("set id_status:{}|{}".format(id_status,self.title));
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
    def nation(self):
        return self.info.nation if self.info != None else ""
    @property
    def movie_name(self):
        return self.info.movie_name if self.info != None else ""

    def download_poster(self,mPath):
        return self.info.download_poster(mPath) if self.info != None else False

    def spider_douban(self):
        if self.info == None: ErrorLog("spider douban,info is null:"+self.title); return False
        return self.info.spider_douban()
        
    def select(self,assign_value=True):
        if self.rss_name == "": return False
        if self._HASH != "":  #通过免费种子加入时，有torrent_id，无HASH
            sel_sql = "select title,downloadlink,doubanid,imdbid,downloaded,torrentid,datetime,size from rss where rssname=%s and HASH=%s"
            sel_val = (self.rss_name,self.HASH)
            tSelectResult =  select(sel_sql,sel_val)
            tSQL = "select title,downloadlink,torrentid,downloaded,datetime,size from rss where rssname={} and HASH={}".format(self.rss_name,self.HASH)
            if tSelectResult == None:
                ErrorLog("failed to exec :"+tSQL)
                return False
            if len(tSelectResult) == 0: return False
            elif len(tSelectResult) > 1: ErrorLog("find 2+record:"+tSQL); return False
            else: pass
            if assign_value == True:
                self.title = tSelectResult[0][0]
                self.download_link = tSelectResult[0][1]
                douban_id = tSelectResult[0][2]
                imdb_id = tSelectResult[0][3]
                self.torrent_id = tSelectResult[0][4]
                self.downloaded = tSelectResult[0][5]
                self.add_datettime = tSelectResult[0][6]
                self.total_size = tSelectResult[0][7]
                if douban_id != "" or imdb_id != "": self.info = Info(douban_id,imdb_id)
            return True
        elif self.torrent_id != "":
            sel_sql = "select title,downloadlink,doubanid,imdbid,HASH,downloaded,datetime,size from rss where rssname=%s and torrentid=%s"
            sel_val = (self.rss_name,self.torrent_id)
            tSelectResult =  select(sel_sql,sel_val)
            tSQL = "select title,download_link,HASH,downloaded,datetime,size from rss where rssname={} and torrentid={}".format(self.rss_name,self.torrent_id)
            if tSelectResult == None:
                ErrorLog("failed to exec :"+tSQL)
                return False
            if len(tSelectResult) == 0: return False
            elif len(tSelectResult) > 1: ErrorLog("find 2+record:"+tSQL); return False
            else: pass
            if assign_value == True:
                self.title = tSelectResult[0][0]
                self.download_link = tSelectResult[0][1]
                douban_id = tSelectResult[0][2]
                imdb_id = tSelectResult[0][3]
                self.HASH = tSelectResult[0][4]
                self.downloaded = tSelectResult[0][5]
                self.add_datettime = tSelectResult[0][6]
                self.total_size = tSelectResult[0][7]
                if douban_id != "" or imdb_id != "": self.info = Info(douban_id,imdb_id)
            return True
        else: return False
               
    def insert(self):
        if self.HASH == "" or self.rss_name == "": return None
        
        in_sql = "insert into rss(rssname,HASH,title,downloadlink,torrentid,doubanid,imdbid,datetime,downloaded,size) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
        in_val = (self.rss_name,self.HASH,self.title,self.download_link,self.torrent_id,self.douban_id,self.imdb_id,self.add_datetime,self.downloaded,self.total_size)
        return insert(in_sql,in_val)

    def update(self):
        if self.rss_name == "": ExecLog("rss_name is null:"+self.title); return False
        if self._HASH != "":
            up_sql = "update rss set title=%s,downloadlink=%s,torrentid=%s,doubanid=%s,imdbid=%s,downloaded=%s,datetime=%s,size=%s where rssname=%s and HASH=%s"
            up_val = (self.title,self.download_link,self.torrent_id,self.douban_id,self.imdb_id,self.downloaded,self.add_datetime,self.total_size,self.rss_name,self.HASH)
        elif self.torrent_id != "":
            up_sql = "update rss set title=%s,downloadlink=%s,torrentid=%s,doubanid=%s,imdbid=%s,downloaded=%s,datetime=%s,size=%s where rssname=%s and torrentid=%s"
            up_val = (self.title,self.download_link,self.torrent_id,self.douban_id,self.imdb_id,self.downloaded,self.add_datetime,self.total_size,self.rss_name,self.torrent_id)
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

        torrent = TorrentInfo(download_link=self.download_link)
        if not torrent.get_info(): 
            ExecLog("failed to get info:"+self.download_link); 
            return False
        self._total_size = torrent.total_size;
        self._name = torrent.name
        self._files = torrent.files
        return True

    def get_id_from_detail(self):
        if self.douban_id != "" or self.imdb_id != "": return OK
        #TODO to delete
        if self.rss_name == "" or self.torrent_id == "": return NOK

        if self.retry_times >= 3: ExecLog("3 times for get id from detail:"+self.title); return NOK
        
        return_code,douban_id,imdb_id = NexusPage.get_id_from_detail(self.rss_name,self.torrent_id)
        if return_code == NOK :  ExecLog("can't find id from detail:"+self.title); return NOK #不在这里设id_status为NOK，还有可能从nfo获取
        if return_code == RETRY: self.retry_times += 1; return RETRY
        DebugLog("find id from detail:{}|{}|{}".format(douban_id,imdb_id,self.title))
        self.set_id(douban_id,imdb_id)
        return OK
        
    def set_id(self,douban_id,imdb_id):
        if douban_id == "" and imdb_id == "": return False
        self.info = Info(douban_id,imdb_id)
        # 写入id到数据库
        self.id_status = OK
        if not self.update(): ExecLog("failed to update rss:"+self.title); return False
        return True
        

    '''
    def update_id(self,douban_id="",imdb_id=""):
        """
        根据输入的id和self的id进行比较更新
        """
        tToDoUpdate = False
        if self.douban_id == "" and douban_id != "":
            self.douban_id = douban_id
            tToDoUpdate = True
        if self.douban_id != "" and douban_id != "" and self.douban_id != douban_id:
            ErrorLog("error:diff douban_id to update:{}|{}".format(self.douban_id,douban_id))
            tToDoUpdate = True
            #return False
        imdb_id = trans_imdb_id(imdb_id)
        if self.imdb_id == "" and imdb_id != "":
            self.imdb_id = imdb_id
            tToDoUpdate = True
        if self.imdb_id != "" and imdb_id != "" and self.imdb_id != imdb_id:
            ErrorLog("error:diff imdb_id to update:{}|{}".format(self.imdb_id,imdb_id))
            tToDoUpdate = True
            #return False

        if tToDoUpdate == True: return self.update()
        else                  : return True
    '''

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
