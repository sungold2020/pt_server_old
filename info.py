#!/usr/bin/python3
# coding=utf-8
import re
import requests
from bs4 import BeautifulSoup
import json

from log import *
from database import *

MAX_DOUBAN_RETRY_TIMES= 3
DOUBAN_URL = 'https://movie.douban.com/subject/'
DOUBAN_SEARCH_URL="https://m.douban.com/search/?query="
DOUBAN_VIEWED_URL = 'https://movie.douban.com/people/69057957/collect?start=0&sort=time&rating=all&filter=all&mode=grid'
#DOUBAN_COOKIE='ll="118282"; bid=p0dhpEfEV-4; __utmc=30149280; __utmc=223695111; __yadk_uid=zONgmuQAhUz48FScpbbLwlyp9sWgxc8m; _vwo_uuid_v2=DB07B9A9429A767628851B0838F87F143|70668c6e9c14c93aa7249d070dc6cf07; __gads=ID=af7d0ac47d706c3b:T=1592790195:S=ALNI_MZPqMSCLzv4tlBWoABDl8fGGwGUBQ; douban-profile-remind=1; __utmz=30149280.1594774078.8.3.utmcsr=accounts.douban.com|utmccn=(referral)|utmcmd=referral|utmcct=/passport/login; __utmz=223695111.1594774078.7.2.utmcsr=accounts.douban.com|utmccn=(referral)|utmcmd=referral|utmcct=/passport/login; __utmv=30149280.6905; _pk_ref.100001.4cf6=%5B%22%22%2C%22%22%2C1601810716%2C%22https%3A%2F%2Fwww.douban.com%2Fpeople%2F218434462%2F%22%5D; _pk_ses.100001.4cf6=*; __utma=30149280.531319256.1586329544.1598777833.1601810716.11; __utmb=30149280.0.10.1601810716; __utma=223695111.1308861375.1586329544.1598777833.1601810717.10; __utmb=223695111.0.10.1601810717; ap_v=0,6.0; dbcl2="69057957:K8+pPeX9x8g"; ck=0tvw; _pk_id.100001.4cf6=e6366f0e1d0169b1.1586329544.10.1601810724.1598778162.; push_noty_num=0; push_doumail_num=0'
DOUBAN_COOKIE='ll="118282"; bid=p0dhpEfEV-4; __utmc=30149280; __utmc=223695111; __yadk_uid=zONgmuQAhUz48FScpbbLwlyp9sWgxc8m; _vwo_uuid_v2=DB07B9A9429A767628851B0838F87F143|70668c6e9c14c93aa7249d070dc6cf07; __gads=ID=af7d0ac47d706c3b:T=1592790195:S=ALNI_MZPqMSCLzv4tlBWoABDl8fGGwGUBQ; douban-profile-remind=1; __utmz=30149280.1594774078.8.3.utmcsr=accounts.douban.com|utmccn=(referral)|utmcmd=referral|utmcct=/passport/login; __utmz=223695111.1594774078.7.2.utmcsr=accounts.douban.com|utmccn=(referral)|utmcmd=referral|utmcct=/passport/login; __utmv=30149280.6905; push_noty_num=0; push_doumail_num=0; ap_v=0,6.0; _pk_ref.100001.4cf6=%5B%22%22%2C%22%22%2C1605693970%2C%22https%3A%2F%2Fwww.douban.com%2Fpeople%2F218434462%2F%22%5D; _pk_ses.100001.4cf6=*; __utma=30149280.531319256.1586329544.1605575173.1605693970.16; __utmb=30149280.0.10.1605693970; __utma=223695111.1308861375.1586329544.1605575173.1605693970.15; __utmb=223695111.0.10.1605693970; dbcl2="69057957:YI95Z/Qbhkg"; ck=MoAu; _pk_id.100001.4cf6=e6366f0e1d0169b1.1586329544.15.1605693982.1605575173.'
USER_AGENT = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.122 Safari/537.36"

MOVIE =  0
TV    =  1
RECORD=  2

OK    =  1
NOK  =  -1
RETRY =  0

DOUBAN = 1
IMDB = 2

class Info:
    def __init__(self,douban_id="",imdb_id="",douban_status=RETRY):
        self._douban_id = douban_id
        self._imdb_id = imdb_id
        self.douban_status = douban_status        # 0 RETRY,1 OK, -1 NOK
        self.douban_retry_times = 0 

        self.douban_score = ""
        self.imdb_score = ""
        self.douban_link = ""
        self.imdb_link = ""
        self.movie_name = ""
        self.foreign_name = ""
        self.other_names = ""
        self.type = MOVIE     # 0 movie,1 TV,2 RECORD
        self.nation = ""
        self.year = 0
        self.director = ""
        self.actors = ""
        self.poster = ""
        self.episodes = 0
        self.genre = ""
        self.viewed = 0

        if self.douban_id == "" and self.imdb_id == "": ErrorLog("Info.init():id is null")
        
        self.select()

    @property
    def douban_id(self):
        return self._douban_id
    @douban_id.setter
    def douban_id(self,douban_id):
        self._douban_id = Info.check_douban_id(douban_id)
    @property
    def imdb_id(self):
        return self._imdb_id
    @imdb_id.setter
    def imdb_id(self,imdb_id):
        self._imdb_id = Info.check_imdb_id(imdb_id)

    def insert(self):
        if self.imdb_id == "" and self.douban_id == "": return False

        #查看数据库是否已经存在记录
        if self.select(False): return False
        DebugLog("插入info表记录:{}|{}".format(self.douban_id,self.imdb_id))

        in_sql = ("insert into info"
        "(doubanid,imdbid,doubanscore,imdbscore,doubanlink,imdblink,name,foreignname,othernames,type,nation,year,director,actors,poster,episodes,genre,doubanstatus)"
        "values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)" )
        in_val = (
                self.douban_id,
                self.imdb_id,
                self.douban_score,
                self.imdb_score,
                self.douban_link,
                self.imdb_link,
                self.movie_name,
                self.foreign_name,
                self.other_names,
                self.type,
                self.nation,
                self.year,
                self.director,
                self.actors,
                self.poster,
                self.episodes,
                self.genre,
                self.douban_status)
        return insert(in_sql,in_val)

    def update(self):
        if self.imdb_id == "" and self.douban_id == "": info_log("empty id for update info");return False

        DebugLog("更新info表记录:{}|{}".format(self.douban_id,self.imdb_id))
        #douban_id first
        if self.douban_id != "":
            up_sql = ("update info set " 
                    "imdbid=%s,"
                    "doubanscore=%s,"
                    "imdbscore=%s,"
                    "doubanlink=%s,"
                    "imdblink=%s,"
                    "name=%s,"
                    "foreignname=%s,"
                    "othernames=%s,"
                    "type=%s,"
                    "nation=%s,"
                    "year=%s,"
                    "director=%s,"
                    "actors=%s,"
                    "poster=%s,"
                    "episodes=%s,"
                    "genre=%s,"
                    "doubanstatus=%s"
                    " where doubanid=%s")
            up_val = (
                    self.imdb_id,
                    self.douban_score,
                    self.imdb_score,
                    self.douban_link,
                    self.imdb_link,
                    self.movie_name,
                    self.foreign_name,
                    self.other_names,
                    self.type,
                    self.nation,
                    self.year,
                    self.director,
                    self.actors,
                    self.poster,
                    self.episodes,
                    self.genre,
                    self.douban_status,
                    self.douban_id)
        else:
            up_sql = ("update info set " 
                    "doubanid=%s,"
                    "doubanscore=%s,"
                    "imdbscore=%s,"
                    "doubanlink=%s,"
                    "imdblink=%s,"
                    "name=%s,"
                    "foreignname=%s,"
                    "othernames=%s,"
                    "type=%s,"
                    "nation=%s,"
                    "year=%s,"
                    "director=%s,"
                    "actors=%s,"
                    "poster=%s,"
                    "episodes=%s,"
                    "genre=%s,"
                    "doubanstatus=%s"
                    " where imdbid=%s")
            up_val = (
                    self.douban_id,
                    self.douban_score,
                    self.imdb_score,
                    self.douban_link,
                    self.imdb_link,
                    self.movie_name,
                    self.foreign_name,
                    self.other_names,
                    self.type,
                    self.nation,
                    self.year,
                    self.director,
                    self.actors,
                    self.poster,
                    self.episodes,
                    self.genre,
                    self.douban_status,
                    self.imdb_id)
        if not update(up_sql,up_val): return False

        # 单独更新viewed，避免被内存中错误的标记更新。只有内存中的viewed=1才更新数据库
        if self.viewed == 1:
            if self.douban_id != "":
                return update("update info set viewed=1 where doubanid = %s", (self.douban_id,))
            else:
                return update("update info set viewed=1 where imdbid = %s", (self.imdb_id,))
        return True

    def select(self,assign_value=True):
        if self.imdb_id == "" and self.douban_id == "": return False
        return (self.select_by_douban_id(assign_value) or self.select_by_imdb_id(assign_value))

    def select_by_imdb_id(self,assign_value=True):
        if self.imdb_id == "": return False
        DebugLog("select from info:"+self.imdb_id);
        sel_sql = ("select  "
                "doubanid,"
                "doubanscore,"
                "imdbscore,"
                "doubanlink,"
                "imdblink,"
                "name,"
                "foreignname,"
                "othernames,"
                "type,"
                "nation,"
                "director,"
                "actors,"
                "poster,"
                "episodes,"
                "genre,"
                "doubanstatus,"
                "year,"
                "viewed"
                " from info where imdbid = %s")
        sel_val = (self.imdb_id,)
        tSelectResult = select(sel_sql,sel_val)
        if tSelectResult == None: 
            ErrorLog("error to select from nfo{}::{}".format(self.imdb_id,sel_sql))
            return False
        elif len(tSelectResult) == 0:
            #print("not find nfo in table:"+self.imdb_id)
            return False
        elif len(tSelectResult) >= 2: 
            ErrorLog("2+ record select_by_imdb_id from nfo:{}".format(self.imdb_id))
            return False
        else: pass
        if assign_value == True:
            if tSelectResult[0][0]  != "": self.douban_id     = tSelectResult[0][0]           
            if tSelectResult[0][1]  != "": self.douban_score  = tSelectResult[0][1]
            if tSelectResult[0][2]  != "": self.imdb_score    = tSelectResult[0][2]
            if tSelectResult[0][3]  != "": self.douban_link   = tSelectResult[0][3]
            if tSelectResult[0][4]  != "": self.imdb_link     = tSelectResult[0][4]
            if tSelectResult[0][5]  != "": self.movie_name    = tSelectResult[0][5]
            if tSelectResult[0][6]  != "": self.foreign_name  = tSelectResult[0][6]
            if tSelectResult[0][7]  != "": self.other_names   = tSelectResult[0][7]
            if tSelectResult[0][8]  != -1: self.type          = tSelectResult[0][8]
            if tSelectResult[0][9]  != "": self.nation        = tSelectResult[0][9]
            if tSelectResult[0][10] != "": self.director      = tSelectResult[0][10]
            if tSelectResult[0][11] != "": self.actors        = tSelectResult[0][11]
            if tSelectResult[0][12] != "": self.poster        = tSelectResult[0][12]
            if tSelectResult[0][13] != -1: self.episodes      = tSelectResult[0][13]
            if tSelectResult[0][14] != "": self.genre         = tSelectResult[0][14]
            if tSelectResult[0][15] != -2: self.douban_status = tSelectResult[0][15]
            if tSelectResult[0][16] != 0 : self.year          = tSelectResult[0][16]
            if tSelectResult[0][17] != -1: self.viewed        = tSelectResult[0][17]
        return True

    def select_by_douban_id(self,assign_value=True):
        if self.douban_id == "": return False
        DebugLog("select from info:"+self.douban_id);
        sel_sql = ("select  "
                "imdbid,"
                "doubanscore,"
                "imdbscore,"
                "doubanlink,"
                "imdblink,"
                "name,"
                "foreignname,"
                "othernames,"
                "type,"
                "nation,"
                "director,"
                "actors,"
                "poster,"
                "episodes,"
                "genre,"
                "doubanstatus,"
                "year,"
                "viewed"
                " from info where doubanid = %s")
        sel_val = (self.douban_id,)
        tSelectResult = select(sel_sql,sel_val)
        if tSelectResult == None: 
            info_log("error to select from nfo{}::{}".format(self.douban_id,sel_sql))
            return False
        elif len(tSelectResult) == 0:
            #print("not find nfo in table:"+self.imdb_id)
            return False
        elif len(tSelectResult) >= 2: 
            ErrorLog("2+ record select_by_douban_id from nfo:{}".format(self.douban_id))
            return False
        else: pass
        if assign_value == True:
            if tSelectResult[0][0]  != "": self.imdb_id       = tSelectResult[0][0]           
            if tSelectResult[0][1]  != "": self.douban_score  = tSelectResult[0][1]
            if tSelectResult[0][2]  != "": self.imdb_score    = tSelectResult[0][2]
            if tSelectResult[0][3]  != "": self.douban_link   = tSelectResult[0][3]
            if tSelectResult[0][4]  != "": self.imdb_link     = tSelectResult[0][4]
            if tSelectResult[0][5]  != "": self.movie_name    = tSelectResult[0][5]
            if tSelectResult[0][6]  != "": self.foreign_name  = tSelectResult[0][6]
            if tSelectResult[0][7]  != "": self.other_names   = tSelectResult[0][7]
            if tSelectResult[0][8]  != -1: self.type          = tSelectResult[0][8]
            if tSelectResult[0][9]  != "": self.nation        = tSelectResult[0][9]
            if tSelectResult[0][10] != "": self.director      = tSelectResult[0][10]
            if tSelectResult[0][11] != "": self.actors        = tSelectResult[0][11]
            if tSelectResult[0][12] != "": self.poster        = tSelectResult[0][12]
            if tSelectResult[0][13] != -1: self.episodes      = tSelectResult[0][13]
            if tSelectResult[0][14] != "": self.genre         = tSelectResult[0][14]
            if tSelectResult[0][15] != -2: self.douban_status = tSelectResult[0][15]
            if tSelectResult[0][16] != 0 : self.year          = tSelectResult[0][16]
            if tSelectResult[0][17] != -1: self.viewed        = tSelectResult[0][17]
        return True

    def update_or_insert(self):
        if self.imdb_id == "" and self.douban_id == "": return False

        if self.select(assign_value=False): return self.update()
        else                              : return self.insert()

    def remove_special_char(self):
        self.director = self.director.replace('|',',')
        self.actors = self.actors.replace('|',',')
        self.movie_name = self.movie_name.replace('|',',')
        self.other_names = self.other_names.replace('|',',')
        self.foreign_name = self.foreign_name.replace('|',',')
        self.genre = self.genre.replace('|',',')

    def spider_douban(self):
        if self.douban_status != RETRY  : return self.douban_status

        #如果douban_id为空，尝试通过imdb_id获取douban_id
        if self.douban_id == "": 
            self.douban_id = Info.get_douban_id_by_imdb_id(self.imdb_id)
            if self.douban_id == "":
                ErrorLog("failed to find douban_id from imdb_id:"+self.imdb_id)
                self.douban_status = NOK
                return self.douban_status

        if self.douban_detail():
            ExecLog("  豆瓣详情:{}|{}|{}|{}|{}|{}/{}|".format(
                self.movie_name,self.nation,self.douban_id,self.imdb_id,self.director,self.douban_score,self.imdb_score))
            self.douban_status = OK
            return self.douban_status

        self.douban_retry_times += 1
        if self.douban_retry_times >= MAX_DOUBAN_RETRY_TIMES : self.douban_status = NOK
        return self.douban_status

    def download_poster(self,mPath):
        if self.poster == "": return False

        DestFullFile=os.path.join(mPath,"poster.jpg")
        try:
            f=requests.get(self.poster,timeout=120)
            with open(DestFullFile,"wb") as code:
                code.write(f.content)
        except Exception as err:
            Print(err)
            ErrorLog("failed to download poster.jpg from:"+self.poster)
            return False
        return True
   
    @staticmethod
    def get_douban_id_by_imdb_id(mIMDBID=""):
        if mIMDBID == "":  return False

        cookie_dict = {"cookie":DOUBAN_COOKIE}
        s = requests.Session()
        s.cookies.update(cookie_dict)

        tUrl = DOUBAN_SEARCH_URL + mIMDBID
        my_headers = {}
        my_headers['User-Agent'] = USER_AGENT
        try:
            res = s.get(tUrl, headers=my_headers,timeout=120)
            soup = BeautifulSoup(res.text,'lxml')
        except Exception as err:
            print(err)
            ErrorLog("except at get url:"+tUrl)
            return ""
        """
        text = open("detail2.log").read()
        soup = BeautifulSoup(text,'lxml')
        """
        #print(soup)

        if str(soup).find("异常请求") >= 0: 
            ErrorLog("failed to request douban search")
            ErrorLog(res.text)
            return False
        
        tDoubanID = ""
        for item in  soup.find_all('a'):
            if item["href"].find("movie/subject") >= 0:
                tDoubanID2 = Info.get_id_from_link(item['href'],DOUBAN)
                if tDoubanID == "":  tDoubanID = tDoubanID2
                elif tDoubanID2 != tDoubanID: ErrorLog("find different douban_id:{}|{}".format(tDoubanID,tDoubanID2)); return False
                else: pass
        return tDoubanID

    def douban_detail(self):
        """
        
        """
        if self.douban_id == "": return False

        cookie_dict = {"cookie":DOUBAN_COOKIE}
        s = requests.Session()
        s.cookies.update(cookie_dict)

        tUrl = DOUBAN_URL + self.douban_id
        my_headers = {}
        my_headers['User-Agent'] = USER_AGENT
        try:
            res = s.get(tUrl, headers=my_headers,timeout=120)
            soup = BeautifulSoup(res.text,'lxml')
        except Exception as err:
            print(err)
            ErrorLog("except at get url:"+tUrl)
            return False
        """
        text = open("detail2.log").read()
        soup = BeautifulSoup(text,'lxml')
        """
        #print(soup)

        if str(soup).find("异常请求") >= 0: 
            ErrorLog("failed to request douban detail")
            ErrorLog(res.text)
            return False
        if "页面不存在" in soup.title.text:
            ErrorLog("the douban id does not exist:"+self.douban_id)
            ErrorLog(res.text)
            return False
        
        #名称/外国名称
        self.movie_name = soup.title.text.replace("(豆瓣)", "").strip()
        self.foreign_name = soup.find('span',property="v:itemreviewed").text.replace(self.movie_name, '').strip()
        info_log (self.movie_name)
        info_log (self.foreign_name)

        #年代
        year_anchor = soup.find('span',class_='year')
        self.year = int(year_anchor.text[1:-1]) if year_anchor else 0
        info_log (str(self.year))


        info = soup.find('div',id='info')
        #print (info)

        #其他电影名
        other_names_anchor = info.find('span',class_='pl',text=re.compile('又名'))
        self.other_names = other_names_anchor.next_element.next_element if other_names_anchor else ""
        info_log(self.other_names)

        #国家/地区
        nation_anchor = info.find('span',class_='pl',text=re.compile('制片国家/地区'))
        self.nation = nation_anchor.next_element.next_element if nation_anchor else ""
        if self.nation.find('/') >= 0: self.nation = (self.nation[:self.nation.find('/')]).strip()
        self.nation = self.trans_nation(self.nation)
        info_log(self.nation)

        #imdb链接和imdb_id
        imdb_anchor = info.find('a',text=re.compile("tt\d+"))
        #info_log (imdb_anchor)
        self.imdb_id = imdb_anchor.text if imdb_anchor else ""
        self.imdb_link = imdb_anchor['href'] if imdb_anchor else ""
        info_log(self.imdb_id)
        info_log(self.imdb_link)

        #类型
        genre_anchor = info.find_all('span',property='v:genre')
        #print(genre_anchor)
        genre_list = []
        for genre in genre_anchor:
            genre_list.append(genre.get_text())
        self.genre = '/'.join(genre_list)
        info_log(self.genre)

        #集数
        episodes_anchor = info.find("span", class_="pl", text=re.compile("集数"))
        self.episodes = int(episodes_anchor.next_element.next_element) if episodes_anchor else 0  # 集数
        #print(episodes_anchor)
        info_log(str(self.episodes))

        #type
        if self.genre.find('纪录') >= 0 : self.type = RECORD
        elif self.episodes > 1              : self.type = TV
        else                            : self.type = MOVIE
        info_log(str(self.type))

          
        json_anchor = soup.find('script',type="application/ld+json")
        #print('-------------------------')
        #print (json_anchor.string)
        #部分时候解析json失败，发现错误分行导致，因此删除换行字符\n后再去解析
        json_string = json_anchor.string.replace('\n',' ') if json_anchor else ""

        #json_string = "".join(i  for i in json_string if 31<ord(i)<127)
        json_string = "".join(i  for i in json_string if 31<ord(i))   #根据ascii码去除特殊字符
        json_string = json_string.replace('\\','\\\\')
         
        #json_string = json_string.replace('\t','')
        #json_string = re.sub('[\x00-\x09|\x0b-\x0c|\x0e-\x1f]','',json_string)
        info_log(json_string)
        try:
            data = json.loads(json_string,strict=False) 
        except Exception as err:
            print(err)
            ExecLog(f"解析json出现错误：{self.douban_id}")
            return False
        #print(data)
        if data == None:  ExecLog('爬取豆瓣详情出现错误:没有找到"json "'); return False

        tType = data['@type']
        info_log (str(tType))

        #海报
        self.poster = data['image']
        info_log(self.poster)

        #豆瓣评分
        self.douban_score = data['aggregateRating']['ratingValue']
        info_log(self.douban_score)

        #导演和演员
        def data_join(data,key):
            tList = []
            for tData in data:
                tList.append(tData.get(key))
            return '/'.join(tList)
        self.director = data_join(data['director'],'name')
        self.actors = data_join(data['actor'],'name')
        info_log(self.director)
        info_log(self.actors)
    
        self.remove_special_char()
        if self.nation != '' and self.movie_name != "" :
            if not self.update_or_insert(): ExecLog("插入/更新表info出现错误:{}|{}|{}".format(self.douban_id,self.imdb_id,self.movie_name))
            self.douban_status = OK
            #self.spider_status = OK
            return True
        else:
            self.douban_status = NOK
            return False
    
    @staticmethod
    def get_from_detail(soup):
        """
        FRDS网站的电影信息不同于其他站，不能从电影简介中获取信息，而需要从html中获取链接
        """
        douban_id = imdb_id = ""
        kdouban_anchor = soup.find('div',id='kdouban')
        site_log("kdouban:{}".format(kdouban_anchor))
        if kdouban_anchor:
            douban_link_anchor = kdouban_anchor.find('a',class_='imdbwp__link') 
            douban_link = douban_link_anchor['href']
            douban_id = Info.get_id_from_link(douban_link,DOUBAN)
            site_log(douban_link)

        kimdb_anchor = soup.find('div',id='kimdb')
        site_log("kimdb:{}".format(kimdb_anchor))
        if kimdb_anchor:
            imdb_link_anchor = kimdb_anchor.find('a',class_='imdbwp__link') 
            imdb_link = imdb_link_anchor['href']
            imdb_id   = Info.get_id_from_link(imdb_link  ,IMDB)
            site_log(imdb_link)
        
        if douban_id != "" or imdb_id != "": return True,douban_id,imdb_id
        else                               : return False,douban_id,imdb_id

    @staticmethod
    def get_from_summary(mSummary):
        douban_id = imdb_id = DoubanLink = IMDBLink = ""
        mSummary = mSummary.replace('　',' ')
        mSummary = mSummary.lower()

        tResult = re.search("douban\.com\/subject\/\d+",mSummary)
        if tResult != None: 
            DoubanLink = "https://movie."+tResult.group()
            douban_id = Info.get_id_from_link(DoubanLink,DOUBAN)
        else:
            tResult = re.search("douban\.com\/movie\/subject\/\d+",mSummary)
            if tResult != None:
                DoubanLink = "https://www."+tResult.group()
                douban_id = Info.get_id_from_link(DoubanLink,DOUBAN)

        tResult = re.search("imdb\.com\/title\/tt\d+",mSummary)
        if tResult != None: 
            IMDBLink = "https://www."+tResult.group()
            imdb_id = Info.get_id_from_link(IMDBLink,IMDB)
        else:
            tResult = re.search("tt[0-9][0-9][0-9][0-9][0-9]+ ",mSummary)
            if tResult != None:
                imdb_id = Info.check_imdb_id(tResult.group())
            else:
                tResult = re.search("tt[0-9][0-9][0-9][0-9][0-9]+\n",mSummary)
                if tResult != None:
                    imdb_id = tResult.group()
                    if imdb_id[-1:] == '\n':imdb_id = imdb_id[:-1]
            
        if douban_id != "" or imdb_id != "": return True,douban_id,imdb_id
        else                               : return False,douban_id,imdb_id
        
    @staticmethod
    def check_douban_id(douban_id):
        douban_id = douban_id.strip()
        if douban_id != "" and not douban_id.isdigit(): ErrorLog("invalid doubanid:"+douban_id); return ""
        return douban_id

    @staticmethod
    def check_imdb_id(imdb_id):
        imdb_id = imdb_id.lower().strip()
        if imdb_id == "": return ""
        if not (imdb_id.startswith('tt') and imdb_id[2:].isdigit()): ErrorLog("invalid imdb_id:"+imdb_id); return ""

        #不允许tt以后的数字大于等于7位数，前面还加0 
        Number = int(imdb_id[2:]) 
        ID = str(Number) if len(str(Number)) >= 7 else str(Number).zfill(7)
        return 'tt'+ID

    @staticmethod
    def trans_nation(mNation):
        tNation = mNation.strip()
        if   tNation[-1:] == '国' : tNation = tNation[:-1]  #去除国家最后的国字
        elif tNation == '香港'    : tNation = '港'
        elif tNation == '中国香港': tNation = '港'
        elif tNation == '中国大陆': tNation = '国'
        elif tNation == '中国台湾': tNation = '台'
        elif tNation == '日本'    : tNation = '日'
        else : pass

        return tNation

    @staticmethod
    def get_id_from_link(mLink,tag):
        """
        https://movie.douban.com/subject/1233445/***
        https://www.douban.com/movie/subject/1233445/***
        https://www.imdb.com/title/123455/***
        """
        if mLink == "": return ""
        tempstr = mLink.strip(' ')
        tempstr = tempstr.replace("\r","")
        if tempstr[-1:] != '/': tempstr = tempstr+'/'
        if tag == DOUBAN: 
            if   mLink.find("douban.com/subject/") >= 0:
                tIndex = mLink.find("douban.com/subject/") + len("douban.com/subject/")
            elif mLink.find("movie/subject/") >= 0:
                tIndex = mLink.find("movie/subject/") + len("movie/subject/")
            else:
                return ""
            tempstr = tempstr[tIndex:]
            tIndex2 = tempstr.find('/')
            return Info.check_douban_id(tempstr[:tIndex2])
        else : 
            tIndex = mLink.find("imdb.com/title/")
            if tIndex == -1 : return ""
            tIndex = tIndex + len("imdb.com/title/")
            tempstr = tempstr[tIndex:]
            tIndex2 = tempstr.find('/')
            return Info.check_imdb_id(tempstr[:tIndex2])


def find_end_number(mString):
    """
    输入格式举例：  "1-15 / 374"
    return:
        -1       : 解析出错
        0        : 已经到达最后一页
        endnumber: 本页的结束number，例如15
    """

    mString = mString.strip('\n')
    mString = mString.strip()
    #print('-----------------')
    info_log(mString)
    #print('-----------------')
    
    tIndex = mString.find('-')
    if tIndex == -1: 
        ExecLog("can't find -:"+mString)
        return -1
    tStartNumber = mString[:tIndex]    # 本页起始number, 如1
    if not tStartNumber.isdigit():
        ExecLog("invalid start number:"+mString)
        return -1

    mString = mString[tIndex+1:]
    tIndex = mString.find('/')
    if tIndex == -1: 
        ExecLog("can't find /:"+mString)
        return -1
    tEndNumber = mString[:tIndex].strip() # 本页结束number，如15
    if not tEndNumber.isdigit():
        ExecLog("invalid end number:"+mString)
        return "error"
    
    tTotal = mString[tIndex+1:].strip()  # 总数
    if not tEndNumber.isdigit():
        ExecLog("invalid total number:"+mString)
        return -1
    
    if int(tEndNumber) != int(tTotal): return int(tEndNumber)
    else                   : return 0

def find_douban_id(mItem):
    try:
        for a in mItem.find_all('a'):
            #print(a)
            #print(a['href'])
            tDoubanID =  Info.get_id_from_link(a['href'],DOUBAN)
            if tDoubanID.isdigit():
                return tDoubanID
    except Exception as err:
        print(mItem)
        print(err)
        ExecLog("exception at find_douban_id")
        return ""
    return ""

def update_viewed(mOnlyFirstPage=True):

    cookie_dict = {"cookie":DOUBAN_COOKIE}
    s = requests.Session()
    s.cookies.update(cookie_dict)

    my_headers = {}
    my_headers['User-Agent'] = USER_AGENT
    tUrl = DOUBAN_VIEWED_URL  # 观影记录首页
    while True:   
        try:
            res = s.get(tUrl, headers=my_headers,timeout=120)
            soup = BeautifulSoup(res.text,'lxml')
        except Exception as err:
            print(err)
            ExecLog("except at get url")
            return False

        try:
            tSubjectNum = soup.find('span',class_="subject-num").get_text() # 举例 1-15 / 374
        except Exception as err:
            print(err)
            print(soup)
            ExecLog("except at find subject-num")
            return False

        # 获取下一页开始number
        # 因url中的编号是从0开始的，而显示记录是从1开始的。下一页的开始number就是本页中的endnumber
        tNextStartNum = find_end_number(tSubjectNum)    
        #print(tNextStartNum)

        try:
            tViewed = soup.find('div',class_="grid-view")
            tItems = tViewed.find_all('div',class_="item")
        except Exception as err:
            print(err)
            print(soup)
            ExecLog("except at find grid-view")
            return False
        #print(viewed)
        for item in tItems:
            #print('----------------------------------------')
            #print(item)
            #print('----------------------------------------')
            try:
                tTitle = item.find('em').get_text()
            except Exception as err:
                print(err)
                print(item)
                ExecLog("except at find em")
                return False
            tDoubanID = find_douban_id(item)
            if tDoubanID == "":
                ExecLog("can't find douban_id:"+tTitle)
                continue
            #print("{}:{}".format(tTitle,tDoubanID))

            #更新info表中的viewed标志
            record = select("select viewed,name from info where doubanid=%s ", (tDoubanID,))
            if record == None:
                ErrorLog("error:执行数据库select错误")
                return False
            if len(record) == 0:
                ExecLog(f"{tDoubanID} does not exist in table info")
            elif len(record) > 1:
                ExecLog(f"{tDoubanID} have more than 1 record in table info")
            else:
                viewed = record[0][0] 
                name   = record[0][1]
                if viewed == 0:
                    if update("update info set viewed = 1 where doubanid=%s ", (tDoubanID,)):
                        ExecLog(f"更新info表观影记录：{name}")
                    else:
                        ErrorLog(f"更新info表出错:{tDoubanID}")
                else:
                    DebugLog(f"{name} 已经更新过viewed=1")

            """
            tReturn = select("select number,copy,dirname,viewed from movies where doubanid=%s",(tDoubanID,))
            if tReturn == None:
                ErrorLog("error exec:select number,copy,dirname,viewed from movies where doubanid="+tDoubanID)
                continue
            elif len(tReturn) == 0:
                ExecLog("no record in movies doubanid={}:{}".format(tDoubanID,tTitle))
                continue
            else:
                for tResult in tReturn:
                    Number = tResult[0]
                    Copy   = tResult[1]
                    DirName= tResult[2]
                    Viewed = tResult[3]
                    if Viewed == 1: 
                        info_log("viewed=1,ignore it:"+DirName)
                        continue
                    if update("update movies set viewed=1 where number=%s and copy=%s",(Number,Copy)):
                        ExecLog("set viewd=1:"+DirName)
                    else:
                        ErrorLog("error exec:update movies set viewed=1 where number={} and copy={}".format(Number,Copy))
            """

        if mOnlyFirstPage :  return True      # 如果仅更新第一页，就返回，否则继续获取下一页
        if tNextStartNum <= 0: return True   
        tNextStartString = 'start='+str(tNextStartNum)
        tUrl = site_url.replace('start=0',tNextStartString)
        info_log(tUrl)
        time.sleep(10)
        
    return True

