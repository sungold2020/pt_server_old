#!/usr/bin/python3
# coding=utf-8
import requests
import re
import codecs 
from bs4 import BeautifulSoup


from log import *

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
    {    #mteam在free种有订阅，这里就不需要了
        'name':'MTeam', 
        'wait_free':False,   
        'time_interval':0,   
        'manual':{'includes':['x265',],'excludes':['HDSWEB','HDSPad','HDSTV','FRDS','HDS','PTH','HDH','BeiTai']},
        'url':'https://pt.m-team.cc/torrentrss.php?https=1&rows=30&cat401=1&cat419=1&cat420=1&cat421=1&cat439=1&cat403=1&cat402=1&cat435=1&cat438=1&cat404=1&cat409=1&icat=1&ismalldescr=1&isize=1&linktype=dl&passkey=7044b36a9057090e36138df761ddfc5d'
        },
    {
        'name':'HDSky', 
        'wait_free':False,   
        'time_interval':10,
        'auto':{'includes':['x265','HDS'],'excludes':['HDSWEB','HDSPad','HDSTV']},
        'manual':{'includes':['x265',],'excludes':['HDSWEB','HDSPad','HDSTV','FRDS','PTH','HDH','BeiTai']},
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
        'time_interval':70,
        'manual':{'includes':['265',],'excludes':['HDS','FRDS']},
        'url':'https://www.beitai.pt/torrentrss.php?rows=10&ismalldescr=1&linktype=dl&passkey=e193420544db01e767e2a214f30ec049'
        },
    {
        'name':'LeagueHD', 
        'wait_free':False,   
        'time_interval':119,
        'url':'https://leaguehd.com/torrentrss.php?rows=30&linktype=dl&passkey=dfab9bb8e00a9445760abb17ec2fa772&inclbookmarked=1'
        }, 
    {
        'name':'LeagueHDAll', 
        'wait_free':False,   
        'time_interval':30,
        'manual':{'includes':['265',],'excludes':['HDS','FRDS','PTHome','HDHome','BeiTai','HDH','PTH']},
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
        'time_interval':119,
        'url':'https://www.hdarea.co/cartrss.php?rows=50&linktype=dl&passkey=cd27426c9894a4c182eb99521afd6f38&inclcarted=1'
        },
    {
        'name':'HDAreaALL',   
        'wait_free':False,   
        'time_interval':50,
        'manual':{'includes':['265',],'excludes':['HDS','FRDS','PTHome','HDHome','BeiTai','HDH','PTH']},
        'url':'https://www.hdarea.co/torrentrss.php?rows=20&linktype=dl&passkey=cd27426c9894a4c182eb99521afd6f38'
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
        'time_interval':119,
        'url':'https://ptsbao.club/pushrss.php?pushkey=HvBtGW1jKCijeZMC7IPOkJaOweULzAwK2nffSx3Akw3Jb-fL0ZgHEhNVONhMiEmHD_lHAR4BwM5FDMvGRRgIhuB'
        },
    {
        'name':'PTSBaoAll',   
        'wait_free':False,   
        'time_interval':30,
        'manual':{'includes':['265',],'excludes':['HDS','FRDS','BeiTai','HDH','PTH']},
        'url':'https://ptsbao.club/torrentrss.php?rows=10&size=0&cat401=1&ismalldescr=1&linktype=dl&passkey=1764d8ff48dac52c90de4d8c58d47ee2'
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
        'manual':{'includes':['265',],'excludes':['HDS','FRDS','BeiTai','HDH']},
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

def filter_by_keywords(title,keywords):
    """
    根据includes,excludes关键字过滤来判断是否满足过滤条件
    如果整个keywords为空，则缺省认为不满足过滤条件
    如果includes/excludes单个关键字为空，则认为该单个条件无过滤，例如includes为空，也就是任何title都满足includes条件
    """
    if keywords == None: return False

    title = title.lower()
    tIncludes = keywords.get('includes')   if keywords.get('includes') else []
    for tInclude in tIncludes:
        tInclude = tInclude.lower()
        if title.find(tInclude) <= 0: 
            rss_log('not include {},ignore it:{}'.format(tInclude,title))
            return False

    tExcludes = keywords.get('excludes')   if keywords.get('excludes') else []
    for tExclude in tExcludes:
        tExclude = tExclude.lower()
        if title.find(tExclude) >= 0: 
            rss_log('endswith {},ignore it:{}'.format(tExclude,title))
            return False
    return True

def to_be_downloaded(rss_name,title):
    tSite = None
    for tRSS in RSS_LIST:
        if tRSS['name'] == rss_name:
            tSite = tRSS
            break
    if tSite == None: ErrorLog("unknown rss name:"+rss_name); return IGNORE_DOWNLOAD
    
    #
    if tSite.get('auto') == None and tSite.get('manual') == None: return AUTO_DOWNLOAD

    #AUTO
    if filter_by_keywords(title,tSite.get('auto')): return AUTO_DOWNLOAD
    if filter_by_keywords(title,tSite.get('manual')): return MANUAL_DOWNLOAD
    return IGNORE_DOWNLOAD

'''
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
'''
