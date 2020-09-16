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

IGNORE_DOWNLOAD = 0
MANUAL_DOWNLOAD = 1
AUTO_DOWNLOAD  = 2

RSS_LIST = [
    {
        'name':'FRDS',  
        'wait_free':False,   
        'time_interval':10,
        'url':'https://pt.keepfrds.com/torrentrss.php?rows=10&icat=1&ismalldescr=1&isize=1&linktype=dl&passkey=97f4eab2ad32ebf39ee4889f6328800b'
        },
    {
        'name':'MTeam', 
        'wait_free':True,   
        'time_interval':119,
        'url':'https://pt.m-team.cc/torrentrss.php?https=1&rows=30&cat401=1&cat419=1&cat420=1&cat421=1&cat439=1&cat403=1&cat402=1&cat435=1&cat438=1&cat404=1&cat409=1&icat=1&ismalldescr=1&isize=1&linktype=dl&passkey=7044b36a9057090e36138df761ddfc5d'
        },
    {
        'name':'HDSky', 
        'wait_free':False,   
        'time_interval':10,
        'auto':{'includes':['x265','HDS'],'excludes':['HDSWEB','HDSPad','HDSTV']},
        'manual':{'includes':['x265',],'excludes':['HDSWEB','HDSPad','HDSTV','FRDS','HDS','PTH','HDH']},
        'url':'https://hdsky.me/torrentrss.php?rows=10&tea1=1&tea28=1&ismalldescr=1&linktype=dl&passkey=c8c158c14e1762b0c93c91ab2ddc689a'
        },
    {
        'name':'BeiTai',   
        'wait_free':False,   
        'time_interval':119,
        'url':'https://www.beitai.pt/torrentrss.php?rows=20&icat=1&ismalldescr=1&isize=1&linktype=dl&passkey=e193420544db01e767e2a214f30ec049&inclbookmarked=1'
        },
    {
        'name':'BeiTaiAll',   
        'wait_free':False,   
        'time_interval':50,
        'manual':{'includes':['265',],'excludes':['HDS','FRDS']},
        'url':'https://www.beitai.pt/torrentrss.php?rows=10&cat401=1&ismalldescr=1&linktype=dl&passkey=e193420544db01e767e2a214f30ec049'
        },
    {
        'name':'LeagueHD', 
        'wait_free':False,   
        'time_interval':119,
        'url':'https://leaguehd.com/torrentrss.php?rows=20&icat=1&ismalldescr=1&isize=1&linktype=dl&passkey=dfab9bb8e00a9445760abb17ec2fa772&inclbookmarked=1'
        }, 
    {
        'name':'LeagueHDAll', 
        'wait_free':False,   
        'time_interval':50,
        'manual':{'includes':['265',],'excludes':['HDS','FRDS','PTHome','HDHome']},
        'url':'https://leaguehd.com/torrentrss.php?rows=20&ismalldescr=1&linktype=dl&passkey=dfab9bb8e00a9445760abb17ec2fa772'
        }, 
    {
        'name':'HDHome',   
        'wait_free':False,   
        'time_interval':119,
        'url':'http://hdhome.org/torrentrss.php?myrss=1&linktype=dl&uid=74129&passkey=93581f449716e0adedc71620f78513d2'
        },
    {
        'name':'HDArea',   
        'wait_free':False,   
        'time_interval':60,
        'url':'https://www.hdarea.co/cartrss.php?rows=50&linktype=dl&passkey=cd27426c9894a4c182eb99521afd6f38&inclcarted=1'
        },
    {
        'name':'JoyHD',    
        'wait_free':False,   
        'time_interval':60,
        'url':'https://www.joyhd.net/torrentrss.php?rows=20&icat=1&ismalldescr=1&isize=1&linktype=dl&passkey=a770594966a29653632f94dce676f3b8&inclbookmarked=1'
        },
    {
        'name':'SoulVoice',
        'wait_free':False,   
        'time_interval':60,
        'url':'http://pt.soulvoice.club/torrentrss.php?myrss=1&linktype=dl&uid=91007&passkey=2e96eb27f1e14173af82b06fecfd767d'
        },
    {
        'name':'PTSBao',   
        'wait_free':False,   
        'time_interval':60,
        'url':'https://ptsbao.club/pushrss.php?pushkey=HvBtGW1jKCijeZMC7IPOkJaOweULzAwK2nffSx3Akw3Jb-fL0ZgHEhNVONhMiEmHD_lHAR4BwM5FDMvGRRgIhuB'
        },
    {
        'name':'PTHome',   
        'wait_free':False,   
        'time_interval':119,
        'url':'http://pthome.net/torrentrss.php?myrss=1&linktype=dl&uid=116626&passkey=c8b0815aa8bf6f1502260a11f8ed2ed7'
        },
    {
        'name':'PTHomeAll',   
        'wait_free':False,   
        'time_interval':50,
        'manual':{'includes':['265',],'excludes':['HDS','FRDS','BeiTai']},
        'url':'https://pthome.net/torrentrss.php?rows=20&cat401=1&ismalldescr=1&linktype=dl&passkey=c8b0815aa8bf6f1502260a11f8ed2ed7'
        },
    {
        'name':'AVGV',     
        'wait_free':False,   
        'time_interval':60,
        'url':'http://avgv.cc/torrentrss.php?rows=20&icat=1&ismalldescr=1&isize=1&linktype=dl&passkey=9a269ba45540e516cbf15ebf6dd815b8&inclbookmarked=1'
        },
    {
        'name':'FRDSMark' ,
        'wait_free':False,   
        'time_interval':119,
        'url':'https://pt.keepfrds.com/torrentrss.php?rows=10&icat=1&isize=1&linktype=dl&passkey=97f4eab2ad32ebf39ee4889f6328800b&inclbookmarked=1'
        },
    {
        'name':'HDSkyMark',
        'wait_free':False,   
        'time_interval':0,
        'url':'https://hdsky.me/torrentrss.php?rows=10&icat=1&ismalldescr=1&isize=1&linktype=dl&passkey=c8c158c14e1762b0c93c91ab2ddc689a&inclbookmarked=1'
        },
    {
        'name':'HDSkyRSS',
        'wait_free':False,   
        'time_interval':119,
        'url':'https://hdsky.me/torrentrss.php?rows=50&linktype=dl&inclrssmarked=1&passkey=c8c158c14e1762b0c93c91ab2ddc689a'
        },
    {
        'name':'MTeamMark',
        'wait_free':False,   
        'time_interval':119,
        'url':'https://pt.m-team.cc/torrentrss.php?https=1&rows=20&icat=1&ismalldescr=1&isize=1&linktype=dl&passkey=7044b36a9057090e36138df761ddfc5d&inclbookmarked=1'
        }]

class RSS:
    def __init__(self,HASH='',rss_name='',download_link='',title='',douban_id="",imdb_id="",add_datetime=""):
        self._HASH          = HASH
        self.rss_name      = rss_name
        self.download_link = download_link
        self.title         = title
        self._douban_id = douban_id
        self._imdb_id = imdb_id
        
        self.torrent_id = self.get_torrent_id(self.download_link)
        self.add_date = datetime.datetime.now().strftime('%Y-%m-%d')
        self.downloaded = 0

        if add_datetime == "": self._add_datetime =  datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        else                 : self._add_datetime = add_datetime
        self._name = ""
        self._total_size = 0
        self._files = []
        #if self.add_status == TO_BE_ADD or selfself.get_torrent_info()
        if rss_name.lower().startswith("pthome"): self.convert_download_link()


    @property
    def HASH(self):
        if self._HASH == "": 
            ErrorLog("error:_HASH is null:"+self.title)
        return self._HASH
    @HASH.setter
    def HASH(self,HASH):
        if HASH == "": 
            ErrorLog("error:HASH is null:"+self.title)
        self._HASH = HASH

    @property
    def douban_id(self):
        return self._douban_id

    @douban_id.setter
    def douban_id(self,douban_id):
        douban_id = douban_id.strip()
        if douban_id != "" and not douban_id.isdigit(): ErrorLog("invalid doubanid:"+douban_id); return 
        self._douban_id = douban_id

    @property
    def imdb_id(self):
        return self._imdb_id
    @imdb_id.setter
    def imdb_id(self,imdb_id):
        self._imdb_id = trans_imdb_id(imdb_id)

    @property
    def total_size(self):
        return self._total_size
    @property
    def name(self):
        return self._name
    @property
    def files(self):
        return self._files
    @property
    def add_datetime(self):
        return self._add_datetime

    def get_torrent_info(self):
        torrent = TorrentInfo(download_link=self.download_link)
        if not torrent.get_info(): 
            ExecLog("failed to get info:"+self.download_link); 
            return False
        self._total_size = torrent.total_size;
        self._name = torrent.name
        self._files = torrent.files
        return True

    def select(self,assign_value=True):
        if self.rss_name == "": return False
        if self._HASH != "":  #通过免费种子加入时，有torrent_id，无HASH
            sel_sql = "select title,downloadlink,doubanid,imdbid,downloaded,torrentid,adddate from rss where rssname=%s and HASH=%s"
            sel_val = (self.rss_name,self.HASH)
            tSelectResult =  select(sel_sql,sel_val)
            tSQL = "select title,downloadlink,torrentid,downloaded,addate from rss where rssname={} and HASH={}".format(self.rss_name,self.HASH)
            if tSelectResult == None:
                ErrorLog("failed to exec :"+tSQL)
                return False
            if len(tSelectResult) == 0: return False
            elif len(tSelectResult) > 1: ErrorLog("find 2+record:"+tSQL); return False
            else: pass
            if assign_value == True:
                self.title = tSelectResult[0][0]
                self.download_link = tSelectResult[0][1]
                self.douban_id = tSelectResult[0][2]
                self.imdb_id = tSelectResult[0][3]
                self.torrent_id = tSelectResult[0][4]
                self.downloaded = tSelectResult[0][5]
                self.add_date = tSelectResult[0][6]
            return True
        elif self.torrent_id != "":
            sel_sql = "select title,downloadlink,doubanid,imdbid,HASH,downloaded,adddate from rss where rssname=%s and torrentid=%s"
            sel_val = (self.rss_name,self.torrent_id)
            tSelectResult =  select(sel_sql,sel_val)
            tSQL = "select title,download_link,HASH,downloaded,addate from rss where rssname={} and torrentid={}".format(self.rss_name,self.torrent_id)
            if tSelectResult == None:
                ErrorLog("failed to exec :"+tSQL)
                return False
            if len(tSelectResult) == 0: return False
            elif len(tSelectResult) > 1: ErrorLog("find 2+record:"+tSQL); return False
            else: pass
            if assign_value == True:
                self.title = tSelectResult[0][0]
                self.download_link = tSelectResult[0][1]
                self.douban_id = tSelectResult[0][2]
                self.imdb_id = tSelectResult[0][3]
                self.HASH = tSelectResult[0][4]
                self.downloaded = tSelectResult[0][5]
                self.add_date = tSelectResult[0][6]
            return True
        else: return False
               
    def insert(self):
        if self.HASH == "" or self.rss_name == "": return None
        
        in_sql = "insert into rss(rssname,HASH,title,downloadlink,torrentid,doubanid,imdbid,adddate,downloaded) values(%s,%s,%s,%s,%s,%s,%s,%s,%s)"
        in_val = (self.rss_name,self.HASH,self.title,self.download_link,self.torrent_id,self.douban_id,self.imdb_id,self.add_date,self.downloaded)
        return insert(in_sql,in_val)

    def update(self):
        if self.rss_name == "": return False
        if self._HASH != "":
            up_sql = "update rss set title=%s,downloadlink=%s,torrentid=%s,doubanid=%s,imdbid=%s,downloaded=%s,adddate=%s where rssname=%s and HASH=%s"
            up_val = (self.title,self.download_link,self.torrent_id,self.douban_id,self.imdb_id,self.downloaded,self.add_date,self.rss_name,self.HASH)
        elif self.torrent_id != "":
            up_sql = "update rss set title=%s,downloadlink=%s,torrentid=%s,doubanid=%s,imdbid=%s,downloaded=%s,adddate=%s where rssname=%s and torrentid=%s"
            up_val = (self.title,self.download_link,self.torrent_id,self.douban_id,self.imdb_id,self.downloaded,self.add_date,self.rss_name,self.torrent_id)
        else:
            ErrorLog("HASH and torrent_id is null to update:"+self.title)
            return False
        return update(up_sql,up_val)

    def update_or_insert(self):
        if self.HASH == "" or self.rss_name == "": return None

        if self.select(assign_value=False): return self.update()
        else            : return self.insert()

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


    def get_torrent_id(self,mDownloadLink):
        tTorrentID = ""
        if mDownloadLink == "": return ""
        tIndex = mDownloadLink.find("id=")
        if tIndex == -1: DebugLog("failed to find torrentid starttag(id=):"+mDownloadLink) ;return ""
        tTorrentID = mDownloadLink[tIndex+3:]
        tIndex = tTorrentID.find("&")
        if tIndex == -1: DebugLog("failed to find torrentid endtag(&):"+mDownloadLink); return ""
        return tTorrentID[:tIndex]

    def to_be_downloaded(self):
        tSite = None
        for tRSS in RSS_LIST:
            if tRSS['name'] == self.rss_name:
                tSite = tRSS
                break
        if tSite == None: ErrorLog("unknown rss name:"+self.rss_name); return IGNORE_DOWNLOAD
        
        #
        if tSite.get('auto') == None and tSite.get('manual') == None: return AUTO_DOWNLOAD

        #AUTO
        if filter_by_keywords(self.title,tSite.get('auto')): return AUTO_DOWNLOAD
        if filter_by_keywords(self.title,tSite.get('manual')): return MANUAL_DOWNLOAD
        return IGNORE_DOWNLOAD


    def filter_by_keywords(self):
        """
        根据auto/manual:includes/excludes关键字进行过滤:
        AUTO
        MANUAL
        REMOVE
        """
        tSite = None
        for tRSS in RSS_LIST:
            if tRSS['name'] == self.rss_name:
                tSite = tRSS
                break
        if tSite == None: ErrorLog("unknown rss name:"+self.rss_name); return False
        
        tIncludes = tSite.get('includes')   if tSite.get('includes') else []
        for tInclude in tIncludes:
            if self.title.find(tInclude) <= 0: 
                rss_log('not include {},ignore it:{}'.format(tInclude,self.title))
                return False

        tExcludes = tSite.get('excludes')   if tSite.get('excludes') else []
        for tExclude in tExcludes:
            if self.title.find(tExclude) >= 0: 
                rss_log('include {},ignore it:{}'.format(tExclude,self.title))
                return False
        return True

    def convert_download_link(self):
        for site in NexusPage.site_list:
            if site['name'].lower() in self.rss_name.lower():
                self.download_link = site['first_url']+'download.php?id='+self.torrent_id+site['last_url']

def filter_by_keywords(title,keywords):
    """

    """
    if keywords == None: return False

    tIncludes = keywords.get('includes')   if keywords.get('includes') else []
    for tInclude in tIncludes:
        if title.find(tInclude) <= 0: 
            rss_log('not include {},ignore it:{}'.format(tInclude,title))
            return False

    tExcludes = keywords.get('excludes')   if keywords.get('excludes') else []
    for tExclude in tExcludes:
        if title.find(tExclude) >= 0: 
            rss_log('include {},ignore it:{}'.format(tExclude,title))
            return False
    return True
