#!/usr/bin/python3
# coding=utf-8
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
            'cookie':'__cfduid=d2ab7dcc493af25332ed9379243090f4e1595342947; tp=YTM4ZDNjNWZhN2Y1YjNhMmUzZDNmYTJhNTdjZTgwYjlhNTdmNmQyMw%3D%3D'
            },
        {
            'name':'FRDS',    
            'error_count':0,
            'time_interval':0,
            'url':'https://pt.keepfrds.com/torrents.php',
            'first_url':'https://pt.keepfrds.com/',
            'last_url':'&passkey=97f4eab2ad32ebf39ee4889f6328800b',
            'referer': 'https://pt.keepfrds.com/torrents.php',
            'host': 'pt.keepfrds.com',
            'cookie':'c_secure_uid=MzEzNDI%3D; c_secure_pass=23911bfa87853213d48cf9968963e4bf; c_secure_ssl=eWVhaA%3D%3D; c_secure_tracker_ssl=eWVhaA%3D%3D; c_secure_login=bm9wZQ%3D%3D; _ga=GA1.2.487776809.1582807782; __cfduid=dfb9be8b9ae90ac0ca0f5706d1b6654e71593262434'
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
        site_log(self.detail_url)

        if self.get_error_count() >= NexusPage.max_error_count:
            ExecLog("reach max error count:"+self.detail_url)
            return False
        
        # Using Session to keep cookie
        cookie_dict = {"cookie":self.site['cookie']}
        s = requests.Session()
        s.cookies.update(cookie_dict)
        
        myheaders={
            'cookie':self.site['cookie'],
            'user-agent': NexusPage.user_agent}
        if self.site.get('referer'): myheaders['referer'] = self.site.get('referer')
        if self.site.get('host')   : myheaders['host']    = self.site.get('host')
        #site_log(myheaders)

        try:
            res = s.get(self.detail_url, headers=myheaders)
            self.soup = bs4.BeautifulSoup(res.text,'lxml')
            #text = open('frds.log').read()
            #self.soup = bs4.BeautifulSoup(text,'lxml')
        except Exception as err:
            print(err)
            ExecLog("failed to request from "+self.detail_url)
            #self.Print("error:"+self.error_string)
            self.set_error_count(False)
            return False
        else:
            self.set_error_count(True)

        tInfo = Info()

        if self.site['name'] == 'FRDS': 
            tInfo.get_from_detail(self.soup)
        else:
            tSummary = ""
            summary_anchor = self.soup.find('div',id='kdescr')
            if summary_anchor : tSummary = summary_anchor.get_text()
            else : site_log("not find summary:"+self.detail_url); return False
            site_log(tSummary)
            tInfo.get_from_summary(tSummary)

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

        site_log(res.text)
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
                self.free_torrents.append((torrent_id, title, details, download_url))
        return self.free_torrents

    def Print(self,Str):
        fo = open(NexusPage.FreeDebugFile,"a+")
        tCurrentTime = datetime.datetime.now()
        fo.write(tCurrentTime.strftime('%Y-%m-%d %H:%M:%S')+"::")
        fo.write(Str+'\n')
        fo.close()


