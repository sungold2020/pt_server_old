#!/usr/bin/python3
import bs4
import requests
import os
import lxml
import re
import datetime
import mysql.connector

from info import *
from log import *

class NexusPage():
    #user_agent = "Mozilla/5.0 (X11; Ubuntu; Linux x86_64) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0 Safari/605.1.15 Epiphany/605.1.15"
    user_agent ="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.122 Safari/537.36"
    site_list = [
        {
            'name':'HDSky',    
            'error_count':0,
            'time_interval':0,
            'url':'https://hdsky.me/torrents.php',
            'first_url':'https://hdsky.me/',
            'last_url':'&passkey=c8c158c14e1762b0c93c91ab2ddc689a',
            'cookie':'_cfduid=db2b415ee08bcfffe3cf8cce295391efd1593000122; c_secure_uid=OTI5OTY%3D; c_secure_pass=d6d578d9961e551a990a652eff203fea; c_secure_ssl=eWVhaA%3D%3D; c_secure_tracker_ssl=eWVhaA%3D%3D; c_secure_login=bm9wZQ%3D%3D; UM_distinctid=172f345ce002c-0d1dbc47b6f2a1-317c0e5e-ffc00-172f345ce090; CNZZDATA5476511=cnzz_eid%3D830024714-1593216097-https%253A%252F%252Fhdsky.me%252F%26ntime%3D1593692147'
            },
        {
            'name':'MTeam',    
            'error_count':0,
            'time_interval':10,
            'url':'https://pt.m-team.cc/movie.php',
            'first_url':'https://pt.m-team.cc/',
            'last_url':'&passkey=7044b36a9057090e36138df761ddfc5d&https=1',
            'cookie':'__cfduid=d03b414d2c913ba7f7c4ea7b1ef754edf1592635299; tp=YTM4ZDNjNWZhN2Y1YjNhMmUzZDNmYTJhNTdjZTgwYjlhNTdmNmQyMw%3D%3D'
            },
        {
            'name':'PTHome',   
            'error_count':0,
            'time_interval':0,
            'url':'https://pthome.net/torrents.php',
            'first_url':'https://pthome.net/',
            'last_url':'&passkey=c8b0815aa8bf6f1502260a11f8ed2ed7',
            'cookie':'UM_distinctid=16fdd772e20298-0ffecec8f400d-7a0a2812-afc80-16fdd772e21126; c_secure_uid=MTE2NjI2; c_secure_pass=fa2f1a45c5b35cbc66c8f55c51dc4e42; c_secure_ssl=eWVhaA%3D%3D; c_secure_tracker_ssl=eWVhaA%3D%3D; c_secure_login=bm9wZQ%3D%3D; CNZZDATA1275677506=695846621-1579964786-https%253A%252F%252Fpthome.net%252F%7C1592560734'
            },
        {
            'name':'LeagueHD', 
            'error_count':0,
            'time_interval':0,
            'url':'https://leaguehd.com/torrents.php',
            'first_url':'https://leaguehd.com/',
            'last_url':'&passkey=dfab9bb8e00a9445760abb17ec2fa772',
            'cookie':'c_secure_ssl=eWVhaA%3D%3D; __cfduid=d4246542612e038a805e33a9f1f028ccb1592576107; c_secure_uid=MTI5NjQ%3D; c_secure_pass=31ba18ffe0b9f74be2c1b76065a600ef; c_secure_tracker_ssl=eWVhaA%3D%3D; c_secure_login=bm9wZQ%3D%3D'
            },
        {
            'name':'PTSBao',   
            'error_count':0,
            'time_interval':0,
            'url':'https://ptsbao.club/torrents.php',
            'first_url':'https://ptsbao.club/',
            'last_url':'&passkey=1764d8ff48dac52c90de4d8c58d47ee2',
            'cookie':'PHPSESSID=3dle0n7eunsn3eqciqff3jqbf6; __cfduid=db8181b2bd7a42f348e9cd3e46bb868321592710911; c_secure_uid=MzUyOA%3D%3D; c_secure_pass=01c383f2a4331d4ba4973c3882a3f7c3; c_secure_ssl=eWVhaA%3D%3D; c_secure_tracker_ssl=bm9wZQ%3D%3D; c_secure_login=bm9wZQ%3D%3D'
            },
        {
            'name':'HDHome',   
            'error_count':0,
            'time_interval':0,
            'url':'https://hdhome.org/torrents.php',
            'first_url':'https://hdhome.org/',
            'last_url':'&passkey=93581f449716e0adedc71620f78513d2',
            'cookie':'PHPSESSID=0sggs2m8trecpdgfdvt1v0p0c7; c_secure_uid=NzQxMjk%3D; c_secure_pass=469cd91be00b025b82d53080d2c56108; c_secure_ssl=bm9wZQ%3D%3D; c_secure_tracker_ssl=bm9wZQ%3D%3D; c_secure_login=bm9wZQ%3D%3D'
            },
        {
            'name':'SoulVoice',
            'error_count':0,
            'time_interval':0,
            'url':'https://pt.soulvoice.club/torrents.php',
            'first_url':'https://pt.soulvoice.club/',
            'last_url':'&passkey=2e96eb27f1e14173af82b06fecfd767d',
            'cookie':'_secure_ssl=eWVhaA%3D%3D; c_secure_uid=OTEwMDc%3D; c_secure_pass=918e7ff98811aa657b94cbf82e537d99; c_secure_tracker_ssl=eWVhaA%3D%3D; c_secure_login=bm9wZQ%3D%3D'
            },
        {
            'name':'AVGV',     
            'error_count':0,
            'time_interval':0,
            'url':'https://avgv.cc/AV.php?cat403=1&cat404=1&cat405=1&cat406=1&cat407=1&cat408=1&cat409=1&cat410=1&cat411=1&cat412=1&processing3=1&processing4=1&processing5=1',
            'first_url':'http://avgv.cc/',
            'last_url':'&passkey=9a269ba45540e516cbf15ebf6dd815b8',
            'cookie':'__cfduid=d5cdd3e7a7b537620160c0b18803939ab1592711298; c_secure_uid=MTY0OQ%3D%3D; c_secure_pass=36fa07318c21ad12b814d1419d6a501b; c_secure_ssl=bm9wZQ%3D%3D; c_secure_tracker_ssl=bm9wZQ%3D%3D; c_secure_login=bm9wZQ%3D%3D'
            },
        {
            'name':'HDArea',   
            'error_count':0,
            'time_interval':0,
            'url':'https://www.hdarea.co/torrents.php',
            'first_url':'https://www.hdarea.co/',
            'last_url':'&passkey=cd27426c9894a4c182eb99521afd6f38',
            'cookie':'c_secure_uid=NTQ0MDM%3D; c_secure_pass=181c47511db42b7996a545e29457502c; c_secure_ssl=eWVhaA%3D%3D; c_secure_tracker_ssl=eWVhaA%3D%3D; c_secure_login=bm9wZQ%3D%3D; UM_distinctid=17086af741f12a-0ec862596a110f-317c0e5e-ffc00-17086af742235a; __gads=ID=d7b74ac08f1307af:T=1582807610:S=ALNI_Mb-QC2hrpkf03uuQm5RFQtt-pyD8g; Hm_lvt_04584756b6df0223a0a33332be422d74=1592642754; _ga=GA1.2.1017807653.1592711567; _gid=GA1.2.1648118811.1592711568; _gat_gtag_UA_129091596_1=1; CNZZDATA1275308543=114681054-1582802454-%7C1592711696; Hm_lpvt_04584756b6df0223a0a33332be422d74=1592711838'
            },
        {
            'name':'JoyHD',    
            'error_count':0,
            'time_interval':0,
            'url':'https://www.joyhd.net/torrents.php',
            'first_url':'https://www.joyhd.net/',
            'last_url':'&passkey=a770594966a29653632f94dce676f3b8',
            'cookie':'PHPSESSID=1b4ngj5fbahu34998vc6jqcl93; t-se=1; login-se=1; c_secure_uid=MTgzOTQ%3D; c_secure_pass=1e9bf921616e2c4680cb2bf8950ccf69; c_secure_ssl=eWVhaA%3D%3D; c_secure_tracker_ssl=eWVhaA%3D%3D; c_secure_login=bm9wZQ%3D%3D'
            }
    ]

    free_tag = 'pro_free'
    free_tag2 = 'pro_free2up'
    torrents_class_name = '.torrentname'
    FreeDebugFile = "log/free.debug"

    max_error_count = 5

    def __init__(self,mSite):
        self.site = mSite
        #self.error_string = ""
        self.detail_url = ""
        self.info = None

    def request_detail_page(self,mTorrentID):
        if not self.site : return False
            
        self.detail_url = self.site['first_url']+'details.php?id='+mTorrentID+'&hit=1'
        self.Print(self.detail_url)

        if self.get_error_count() >= NexusPage.max_error_count:
            ExecLog("reach max error count:"+self.detail_url)
            #self.Print("error:"+self.error_string)
            return False
        
        # Using Session to keep cookie
        cookie_dict = {"cookie":self.site['cookie']}
        s = requests.Session()
        s.cookies.update(cookie_dict)
    
        try:
            if NexusPage.user_agent: 
                res = s.get(self.detail_url, headers={'User-Agent':NexusPage.user_agent})
            else:
                res = s.get(self.detail_url)
        except Exception as err:
            print(err)
            ExecLog("failed to request from "+self.detail_url)
            #self.Print("error:"+self.error_string)
            self.set_error_count(False)
            return False
        else:
            self.set_error_count(True)

        #self.soup = bs4.BeautifulSoup(res.text,'lxml')
        SummaryStr = res.text

        tInfo = Info()
        SummaryStr = re.sub(u'\u3000',u' ',SummaryStr)
        SummaryStr = re.sub(u'\xa0', u' ', SummaryStr)
        SummaryStr = re.sub('&nbsp;',' ',  SummaryStr)
        SummaryStr = SummaryStr.lower()
        DebugLog(SummaryStr)
                
        tIndex = SummaryStr.find("豆瓣评分")
        if tIndex >= 0 :
            tempstr = SummaryStr[tIndex+5:tIndex+16]
            tSearch = re.search("[0-9]\.[0-9]",tempstr)
            if tSearch : tInfo.douban_score = tSearch.group()
            else:        tInfo.douban_score = ""
            DebugLog("douban score:"+tInfo.douban_score)
        else: DebugLog("douban score:not find")
        
        tIndex = SummaryStr.find("豆瓣链接")
        if tIndex >= 0 :
            tempstr = SummaryStr[tIndex:]
            tIndex = tempstr.find("href=")
            if tIndex >= 0:
                tempstr = tempstr[tIndex+6:]
                tIndex = tempstr.find('\"')
                if tIndex >= 0 : tInfo.douban_link = tempstr[:tIndex]; DebugLog("douban link:"+tInfo.douban_link)
                else: DebugLog("douban link:error:not find \"")
            else: DebugLog("douban link:error:not find href=")
        else: DebugLog("douban link:not find")
        tInfo.douban_id = get_id_from_link(tInfo.douban_link, DOUBAN)
        DebugLog("DoubanLink:"+tInfo.douban_link)

        if   SummaryStr.find("imdb评分")    >= 0: tIndex = SummaryStr.find("imdb评分")           
        elif SummaryStr.find('imdb.rating') >= 0: tIndex = SummaryStr.find('imdb.rating')
        elif SummaryStr.find('imdb rating') >= 0: tIndex = SummaryStr.find('imdb rating')            
        else: tIndex = -1               
        if tIndex >= 0 :
            tempstr = SummaryStr[tIndex+6:tIndex+36]
            tSearch = re.search("[0-9]\.[0-9]",tempstr)
            if tSearch :  tInfo.imdb_score = tSearch.group()
        DebugLog("imdb score:"+tInfo.imdb_score)
        
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
                if tIndex >= 0 : tInfo.imdb_link = tempstr[:tIndex]
                else:  DebugLog("imdb link:error:not find \"")
            else:
                tIndex = tempstr.find('http')
                if tIndex >= 0:
                    tempstr = tempstr[tIndex:]
                    tIndex = tempstr.find('<')
                    if tIndex >= 0 : tInfo.imdb_link = tempstr[:tIndex] 
        tInfo.imdb_id = get_id_from_link(tInfo.imdb_link, IMDB)
        DebugLog("imdb link:"+tInfo.imdb_link)

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
            tInfo.nation = Nation
            DebugLog("Nation:"+tInfo.nation)
        else: DebugLog("failed find nation")

        tIndex = SummaryStr.find("类  别") 
        if tIndex >= 0 and SummaryStr[tIndex:tIndex+100].find("纪录") >= 0 : tInfo.type = RECORD
        elif SummaryStr.find("集  数") >= 0                                : tInfo.type = TV
        else                                                               : tInfo.type = MOVIE
        DebugLog("type:"+str(tInfo.type))

        if tInfo.nation == '港' or tInfo.nation == '国' or tInfo.nation == '台' : tIndex = SummaryStr.find("片  名")
        else                                                  : tIndex = SummaryStr.find("译  名")
        if tIndex >= 0 :
            Name = SummaryStr[tIndex+5:tIndex+100]
            if   Name.find("/")  >= 0 : Name = (Name[ :Name.find("/") ]).strip() 
            elif Name.find("<")  >= 0 : Name = (Name[ :Name.find("<") ]).strip() 
            elif Name.find('\n') >= 0 : Name = (Name[ :Name.find('\n') ]).strip()
            else: DebugLog("failed find name"); Name = ""
        else: DebugLog("failed find name"); Name = ""
        #ExecLog("name:"+Name)
        if Name.find('<') >= 0 : Name = Name[:Name.find('<')]
        tInfo.movie_name = Name
        DebugLog("name:"+tInfo.movie_name)
        
        tIndex = SummaryStr.find("导  演")
        if tIndex >= 0 :
            Director = SummaryStr[tIndex+5:tIndex+100]
            tEndIndex = Director.find('\n')
            if tEndIndex >= 0 : Director = Director[:tEndIndex]
            else : Director = ""
            if Director.find("/")  >= 0 : Director = (Director[ :Director.find("/") ]).strip() 
            if Director.find("<")  >= 0 : Director = (Director[ :Director.find("<") ]).strip() 
        DebugLog("director:"+Director)
        tInfo.director = Director
      
        if tInfo.douban_id != "" or tInfo.imdb_id != "": 
            self.info = tInfo
            return True
        else : 
            return False

    def set_error_count(self,is_success):
        for i in range(len(NexusPage.site_list)):
            if NexusPage.site_list[i]['name'] == self.site['name']:
                if is_success: NexusPage.site_list[i]['error_count']  = 0
                else         : NexusPage.site_list[i]['error_count'] += 1
                return True
        ExecLog("not find site name in site_list:"+self.site['name'])
        #self.Print("error:"+self.error_string)
        return False
    def get_error_count(self):
        for i in range(len(NexusPage.site_list)):
            if NexusPage.site_list[i]['name'] == self.site['name']: 
                return NexusPage.site_list[i]['error_count']
        ExecLog("not find site name in site_list:"+self.site['name'])
        #self.Print("error:"+self.error_string)
        return -1

    def request_free_page(self):

        if not self.site : return False

        if self.get_error_count() >= NexusPage.max_error_count:
            ExecLog("reach max error count:"+self.site['name'])
            #self.Print("error:"+self.error_string)
            return False

        self.processed_list = []
        
        # Using Session to keep cookie
        cookie_dict = {"cookie":self.site['cookie']}
        s = requests.Session()
        s.cookies.update(cookie_dict)
    
        try:
            if NexusPage.user_agent: 
                res = s.get(self.site['url'], headers={'User-Agent':NexusPage.user_agent})
            else:
                res = s.get(self.site['url'])
        except Exception as err:
            print(err)
            ExecLog("failed to request from "+self.site['url'])
            #self.Print("error:"+self.error_string)
            self.set_error_count(False)
            return False

        self.soup = bs4.BeautifulSoup(res.text,'lxml')

        #self.Print(res.text)
        self.processed_list = self.soup.select(NexusPage.torrents_class_name)
        if len(self.processed_list) == 0: 
            ExecLog("can not find processed_list "+self.site['name'])
            self.set_error_count(False)
            return False
        else:
            self.set_error_count(True)
            return True

    def find_free_torrents(self):
        pattern = r'id=(\d+)'
        self.free_torrents = []
        # Check free and add states
        for entry in self.processed_list:            
            details = entry.a['href']
            torrent_id = re.search(pattern, details).group(1)
            title = (entry.get_text()).strip()
            if title[-1:] == '\n': title = title[:-1] #删除\n
            download_url = self.site['first_url']+'download.php?id='+torrent_id+self.site['last_url']

            #if torrent is free:
            if entry.find(class_=NexusPage.free_tag) or entry.find(class_=NexusPage.free_tag2):
                self.free_torrents.append((True , torrent_id, title, details, download_url))
            else:
                self.free_torrents.append((False, torrent_id, title, details, download_url))
        for free_torrent in self.free_torrents:
            self.Print("{} {} {} ".format(str(free_torrent[0]).ljust(5),free_torrent[1],free_torrent[2]))

        return self.free_torrents

    def Print(self,Str):
        fo = open(NexusPage.FreeDebugFile,"a+")
        tCurrentTime = datetime.datetime.now()
        fo.write(tCurrentTime.strftime('%Y-%m-%d %H:%M:%S')+"::")
        fo.write(Str+'\n')
        fo.close()


