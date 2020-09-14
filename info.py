import re
import requests
from bs4 import BeautifulSoup
import json

from gen import Gen
from log import *
from database import *

DOUBAN_URL = 'https://movie.douban.com/subject/'
DOUBAN_SEARCH_URL="https://m.douban.com/search/?query="
DOUBAN_VIEWED_URL = 'https://movie.douban.com/people/69057957/collect?start=0&sort=time&rating=all&filter=all&mode=grid'
DOUBAN_COOKIE='ll="118282"; bid=p0dhpEfEV-4; __utmc=30149280; __utmc=223695111; __yadk_uid=zONgmuQAhUz48FScpbbLwlyp9sWgxc8m; _vwo_uuid_v2=DB07B9A9429A767628851B0838F87F143|70668c6e9c14c93aa7249d070dc6cf07; push_doumail_num=0; __utmv=30149280.21843; __gads=ID=af7d0ac47d706c3b:T=1592790195:S=ALNI_MZPqMSCLzv4tlBWoABDl8fGGwGUBQ; douban-profile-remind=1; ck=ysVQ; __utmz=30149280.1594774078.8.3.utmcsr=accounts.douban.com|utmccn=(referral)|utmcmd=referral|utmcct=/passport/login; __utmz=223695111.1594774078.7.2.utmcsr=accounts.douban.com|utmccn=(referral)|utmcmd=referral|utmcct=/passport/login; push_noty_num=0; ap_v=0,6.0; _pk_ref.100001.4cf6=%5B%22%22%2C%22%22%2C1594944611%2C%22https%3A%2F%2Fwww.douban.com%2Fpeople%2F218434462%2F%22%5D; _pk_id.100001.4cf6=e6366f0e1d0169b1.1586329544.8.1594944611.1594774103.; _pk_ses.100001.4cf6=*; __utma=30149280.531319256.1586329544.1594774078.1594944611.9; __utmb=30149280.0.10.1594944611; __utma=223695111.1308861375.1586329544.1594774078.1594944612.8; __utmb=223695111.0.10.1594944612; dbcl2="69057957:e5cX8VrtPiw"'
DOUBAN_COOKIE='"118282"; bid=p0dhpEfEV-4; __utmc=30149280; __utmc=223695111; __yadk_uid=zONgmuQAhUz48FScpbbLwlyp9sWgxc8m; _vwo_uuid_v2=DB07B9A9429A767628851B0838F87F143|70668c6e9c14c93aa7249d070dc6cf07; __utmv=30149280.21843; __gads=ID=af7d0ac47d706c3b:T=1592790195:S=ALNI_MZPqMSCLzv4tlBWoABDl8fGGwGUBQ; douban-profile-remind=1; __utmz=30149280.1594774078.8.3.utmcsr=accounts.douban.com|utmccn=(referral)|utmcmd=referral|utmcct=/passport/login; __utmz=223695111.1594774078.7.2.utmcsr=accounts.douban.com|utmccn=(referral)|utmcmd=referral|utmcct=/passport/login; __utma=30149280.531319256.1586329544.1594944611.1598777833.10; __utmb=30149280.0.10.1598777833; __utma=223695111.1308861375.1586329544.1594944612.1598777833.9; __utmb=223695111.0.10.1598777833; ap_v=0,6.0; _pk_ref.100001.4cf6=%5B%22%22%2C%22%22%2C1598777833%2C%22https%3A%2F%2Fwww.douban.com%2Fpeople%2F218434462%2F%22%5D; _pk_ses.100001.4cf6=*; dbcl2="69057957:QCb/tdaIW6s"; ck=S20Y; push_noty_num=0; push_doumail_num=0; _pk_id.100001.4cf6=e6366f0e1d0169b1.1586329544.9.1598777855.1594944644.'
USER_AGENT = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.122 Safari/537.36"

MOVIE =  0
TV    =  1
RECORD=  2

OK    =  1
NOK  =  -1
RETRY =  0
MAX_DOUBAN_RETRY_TIMES= 3

DOUBAN = 1
IMDB = 2

class Info:
    def __init__(self,douban_id="",imdb_id="",spider_status=RETRY):
        self._douban_id = douban_id
        self._imdb_id = imdb_id
        self.spider_status = spider_status

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

        
        self.douban_status = RETRY        # 0 RETRY,1 OK, -1 NOK
        self.douban_retry_times = 0 

        self.select()

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

    def insert(self):
        if self.imdb_id == "" and self.douban_id == "": return False

        #查看数据库是否已经存在记录
        if self.select(False): return False

        in_sql = ("insert into info"
        "(doubanid,imdbid,doubanscore,imdbscore,doubanlink,imdblink,name,foreignname,othernames,type,nation,year,director,actors,poster,episodes,genre,spiderstatus,doubanstatus)"
        "values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)" )
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
                self.spider_status,
                self.douban_status)
        return insert(in_sql,in_val)

    def update(self):
        if self.imdb_id == "" and self.douban_id == "": info_log("empty id for update info");return False

        if self.imdb_id != "" and self.douban_id != "":
            up_sql = ("update info set " 
                    "doubanid=%s,"
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
                    "spiderstatus=%s,"
                    "doubanstatus=%s"
                    " where doubanid=%s or imdbid=%s")
            up_val = (
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
                    self.spider_status,
                    self.douban_status,
                    self.douban_id,
                    self.imdb_id)
        elif self.imdb_id != "":
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
                    "spiderstatus=%s,"
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
                    self.spider_status,
                    self.douban_status,
                    self.imdb_id)
        else:
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
                    "spiderstatus=%s,"
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
                    self.spider_status,
                    self.douban_status,
                    self.douban_id)
        return update(up_sql,up_val)

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
                "spiderstatus,"
                "doubanstatus,"
                "year"
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
            if tSelectResult[0][15] != -2: self.spider_status = tSelectResult[0][15]
            if tSelectResult[0][16] != -2: self.douban_status = tSelectResult[0][16]
            if tSelectResult[0][17] != 0 : self.year          = tSelectResult[0][17]
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
                "spiderstatus,"
                "doubanstatus,"
                "year"
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
            if tSelectResult[0][15] != -2: self.spider_status = tSelectResult[0][15]
            if tSelectResult[0][16] != -2: self.douban_status = tSelectResult[0][16]
            if tSelectResult[0][17] != 0 : self.year          = tSelectResult[0][17]
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

        if self.douban_id == "":
            if not self.get_douban_id_by_imdb_id():
                ErrorLog("failed to find douban_id from imdb_id:"+self.imdb_id)
                self.douban_status == NOK
                return self.douban_status

        if self.douban_detail(self.douban_id):
            ExecLog("douban   detail:{}|{}|{}|{}|{}|{}/{}|".format(
                self.movie_name,self.nation,self.douban_id,self.imdb_id,self.director,self.douban_score,self.imdb_score))
            self.douban_status = OK
            self.spider_status = OK
            return self.douban_status
        self.douban_retry_times += 1
        if self.douban_retry_times >= MAX_DOUBAN_RETRY_TIMES:
            self.douban_status = NOK
        return self.douban_status

        """
        tMovieInfo = {"success":False,"error":""}
        if self.douban_id != "" :   tMovieInfo = Gen({'site':'douban','sid':self.douban_id}).gen(_debug=True)
        elif self.imdb_id != "" :   tMovieInfo = Gen({'site':'douban','sid':self.imdb_id  }).gen(_debug=True)
        else :  
            ExecLog("empty link:"+self.title) 
            self.douban_status = NOK
            return self.douban_status
        if tMovieInfo["success"]: 
            self.nation       = (tMovieInfo['region'][0]).strip() if tMovieInfo.get('region') else ""
            self.year         = tMovieInfo['year']                if tMovieInfo.get('year') else ""
            self.douban_id    = tMovieInfo['sid']                 if tMovieInfo.get('sid') else ""
            self.imdb_id      = tMovieInfo['imdb_id']             if tMovieInfo.get('imdb_id') else ""
            self.movie_name   = tMovieInfo['chinese_title']       if tMovieInfo.get('chinese_title') else ""
            self.foreign_name = tMovieInfo['foreign_title']       if tMovieInfo.get('foreign_title') else ""
            self.director     = ','.join(tMovieInfo['director'])  if tMovieInfo.get('director') else ""
            self.actors       = ','.join(tMovieInfo['cast'])      if tMovieInfo.get('cast') else ""
            self.episodes     = tMovieInfo['episodes']            if tMovieInfo.get('episodes') else ""
            self.poster       = tMovieInfo['poster']              if tMovieInfo.get('poster') else ""
            self.douban_score = tMovieInfo['douban_rating_average'] if tMovieInfo.get('douban_rating_average') else ""
            self.imdb_score   = tMovieInfo['imdb_rating']         if tMovieInfo.get('imdb_rating') else ""
            self.other_names  = ','.join(tMovieInfo['aka'])       if tMovieInfo.get('aka') else ""
            self.genre        = ','.join(tMovieInfo['genre'])     if tMovieInfo.get('genre') else ""
            if self.episodes == "": self.episodes = 0
            else                  : self.episodes = int(self.episodes)
            if self.year == ""    : self.year = 0
            else                  : self.year = int(self.year)
            
            self.nation = trans_nation(self.nation)

            tIndex = self.imdb_score.find('/')
            if tIndex > 0: self.imdb_score = self.imdb_score[:tIndex]
            else:          self.imdb_score = ""

            #判断类型，纪录片，电视剧，电影
            if self.genre.find('纪录') >= 0 :self.type = RECORD
            elif self.episodes > 0          :self.type = TV
            else                            :self.type = MOVIE            

            self.remove_special_char()
            ExecLog("spider   douban:{}|{}|{}|{}|{}|{}/{}|".format(
                self.movie_name,self.nation,self.douban_id,self.imdb_id,self.director,self.douban_score,self.imdb_score))
            self.douban_status = OK
            self.spider_status = OK
            return self.douban_status
        else:
            DebugLog("gen error:"+tMovieInfo['error'])
            #if tMovieInfo['error'].find("The corresponding resource does not exist") >= 0 or tMovieInfo['error'].find("Can't find this imdb_id") >= 0:
            #    self.douban_status = NOK
            #    return self.douban_status
            if self.douban_detail(self.douban_id):
                ExecLog("douban   detail:{}|{}|{}|{}|{}|{}/{}|".format(
                    self.movie_name,self.nation,self.douban_id,self.imdb_id,self.director,self.douban_score,self.imdb_score))
                self.douban_status = OK
                self.spider_status = OK
                return self.douban_status
            self.douban_retry_times += 1
            if self.douban_retry_times >= MAX_DOUBAN_RETRY_TIMES:
                self.douban_status = NOK
        return self.douban_status
        # TODO 如果有doubanid，尝试自己爬取
        """

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


    def get_from_summary(self,mSummary):

        Type = -1
        Nation = Name = Director = Actors = DoubanScore = DoubanID = DoubanLink = IMDBLink = IMDBScore = IMDBID = ""
        #mSummary = re.sub(u'\u3000',u' ',mSummary)    #全角空白字符替换为半角空白字符
        #mSummary = re.sub(u'\xa0', u' ', mSummary)    #
        mSummary = mSummary.replace('　',' ')
        mSummary = mSummary.lower()
        #info_log(mSummary)
        #print(mSummary)
                
        if   mSummary.find("国  家")    >= 0: tIndex = mSummary.find("国  家")
        elif mSummary.find("产  地")    >= 0: tIndex = mSummary.find("产  地")
        else                                  : tIndex = -1
        if tIndex >= 0 :
            Nation = mSummary[tIndex+5:tIndex+20]
            if Nation.find('\n') >= 0: Nation = Nation[:Nation.find('\n')]
            if Nation.find('/')  >= 0: Nation = Nation[ :Nation.find('/') ]  #多个国家,以/区隔,取第一个
            Nation = Nation.strip()
            Nation = trans_nation(Nation)
            info_log("Nation:"+Nation)
        else: info_log("failed find nation")
        self.nation = Nation

        if Nation == '港' or Nation == '国' or Nation == '台' : tIndex = mSummary.find("片  名")
        else                                                  : tIndex = mSummary.find("译  名")
        if tIndex >= 0 :
            Name = mSummary[tIndex+5:tIndex+100]
            if Name.find("/")  >= 0 : Name = (Name[ :Name.find("/") ]).strip() 
            if Name.find('\n') >= 0 : Name = (Name[ :Name.find('\n') ]).strip()
        else: info_log("failed find name"); Name = ""
        info_log("name:"+Name)
        self.movie_name = Name

        tIndex = mSummary.find("豆瓣链接")
        if tIndex >= 0 :
            DoubanLink = mSummary[tIndex+4:]
            if DoubanLink.find('\n') >= 0 : DoubanLink = (DoubanLink[ :DoubanLink.find('\n') ]).strip()
            DoubanLink = DoubanLink.strip()
            if not DoubanLink.startswith('http'): 
                info_log("invalid doubanlink:"+DoubanLink)
                DoubanLink = ""
        else: info_log("douban link:not find")
        DoubanID = get_id_from_link(DoubanLink, DOUBAN)
        info_log("DoubanLink:"+DoubanLink)
        self.douban_id = DoubanID
        self.douban_link = DoubanLink

        tIndex = mSummary.find("豆瓣链接")
        if tIndex >= 0 :
            DoubanLink = mSummary[tIndex+4:]
            if DoubanLink.find('\n') >= 0 : DoubanLink = (DoubanLink[ :DoubanLink.find('\n') ]).strip()
            DoubanLink = DoubanLink.strip()
            if not DoubanLink.startswith('http'): 
                info_log("invalid doubanlink:"+DoubanLink)
                DoubanLink = ""
        else: info_log("douban link:not find")
        DoubanID = get_id_from_link(DoubanLink, DOUBAN)
        info_log("DoubanLink:"+DoubanLink)
        self.douban_id = DoubanID
        self.douban_link = DoubanLink

        if   mSummary.find("imdb链接")    >= 0: tIndex = mSummary.find("imdb链接")
        elif mSummary.find('imdb.link')   >= 0: tIndex = mSummary.find("imdb.link")
        elif mSummary.find('imdb link')   >= 0: tIndex = mSummary.find("imdb link")
        elif mSummary.find('imdb url')    >= 0: tIndex = mSummary.find('idmb url')           
        else                                  : tIndex = -1            
        if tIndex >= 0 :
            tempstr = mSummary[tIndex:tIndex+200]
            tIndex = tempstr.find("http")
            if tIndex >= 0:
                tempstr = tempstr[tIndex:]
                if tempstr.find('\n') >= 0 : IMDBLink = (tempstr[ :tempstr.find('\n') ]).strip()
        IMDBID = get_id_from_link(IMDBLink, IMDB)
        info_log("imdb link:"+IMDBLink)
        self.imdb_link = IMDBLink
        self.imdb_id = IMDBID

        tIndex = mSummary.find("豆瓣评分")
        if tIndex >= 0 :
            tempstr = mSummary[tIndex+5:tIndex+16]
            tSearch = re.search("[0-9]\.[0-9]",tempstr)
            if tSearch : DoubanScore = tSearch.group()
            else:        DoubanScore = ""
            info_log("douban score:"+DoubanScore)
        else: info_log("douban score:not find")
        self.douban_score = DoubanScore

        if   mSummary.find("imdb评分")    >= 0: tIndex = mSummary.find("imdb评分")           
        elif mSummary.find('imdb.rating') >= 0: tIndex = mSummary.find('imdb.rating')
        elif mSummary.find('imdb rating') >= 0: tIndex = mSummary.find('imdb rating')            
        else: tIndex = -1               
        if tIndex >= 0 :
            tempstr = mSummary[tIndex+6:tIndex+36]
            tSearch = re.search("[0-9]\.[0-9]",tempstr)
            if tSearch :  IMDBScore = tSearch.group()
        info_log("imdb score:"+IMDBScore)
        self.imdb_score = IMDBScore

        tIndex = mSummary.find("类  别") 
        if tIndex >= 0 and mSummary[tIndex:tIndex+100].find("纪录") >= 0 : Type = RECORD
        elif mSummary.find("集  数") >= 0                                : Type = TV
        else                                                               : Type = MOVIE
        info_log("type:"+str(Type))
        self.type = Type

        tIndex = mSummary.find("导  演")
        if tIndex >= 0 :
            Director = mSummary[tIndex+5:tIndex+100]
            tEndIndex = Director.find('\n')
            if tEndIndex >= 0 : Director = Director[:tEndIndex]
            else : Director = ""
        else :Director = ""
        Director = Director.strip()
        info_log("director:"+Director)
        self.director = Director

        self.remove_special_char()
        return
    
    def get_douban_id_by_imdb_id(self,mIMDBID=""):
        if mIMDBID == "": 
            if self.imdb_id == "":
                return False
            else:
                mIMDBID = self.imdb_id

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
            return False
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
                tDoubanID2 = get_id_from_link(item['href'],DOUBAN)
                if tDoubanID == "": 
                    tDoubanID = tDoubanID2
                elif tDoubanID2 != tDoubanID:
                    ErrorLog("find different douban_id:{}|{}".format(tDoubanID,tDoubanID2))
                    return False
                else: pass
        if tDoubanID != "": self.douban_id = tDoubanID; return True
        else              : return False

    def douban_detail(self,mDoubanID=""):
        if mDoubanID == "": 
            if self.douban_id == "":
                return False
            else:
                mDoubanID = self.douban_id

        cookie_dict = {"cookie":DOUBAN_COOKIE}
        s = requests.Session()
        s.cookies.update(cookie_dict)

        tUrl = DOUBAN_URL + mDoubanID
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
            ErrorLog("the douban id does not exist:"+mDoubanID)
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
        self.nation = nation_anchor.next_element.next_element
        if self.nation.find('/') >= 0: self.nation = (self.nation[:self.nation.find('/')]).strip()
        self.nation = trans_nation(self.nation)
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
        json_string = json_anchor.string.replace('\n',' ') if json_anchor else ""

        #json_string = "".join(i  for i in json_string if 31<ord(i)<127)
        json_string = "".join(i  for i in json_string if 31<ord(i))
         
        #json_string = json_string.replace('\t','')
        #json_string = re.sub('[\x00-\x09|\x0b-\x0c|\x0e-\x1f]','',json_string)
        info_log(json_string)
        data = json.loads(json_string) 
        #print(data)
        if data == None:  ExecLog('not find json data'); return False

        tType = data['@type']
        info_log (str(tType))

        #self.movie_name = data['name']
        #print(self.movie_name)

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
            self.douban_status = OK
            self.spider_status = OK
            return True
        else:
            self.douban_status = NOK
            return False
    
    def get_from_detail(self,soup):
        """
        FRDS网站的电影信息不同于其他站，不能从电影简介中获取信息，而需要从html中获取链接
        """
        kdouban_anchor = soup.find('div',id='kdouban')
        site_log("kdouban:{}".format(kdouban_anchor))
        if kdouban_anchor:
            douban_link_anchor = kdouban_anchor.find('a',class_='imdbwp__link') 
            self.douban_link = douban_link_anchor['href']
        site_log(self.douban_link)

        kimdb_anchor = soup.find('div',id='kimdb')
        site_log("kimdb:{}".format(kimdb_anchor))
        if kimdb_anchor:
            imdb_link_anchor = kimdb_anchor.find('a',class_='imdbwp__link') 
            self.imdb_link = imdb_link_anchor['href']
        site_log(self.imdb_link)
        
        self.douban_id = get_id_from_link(self.douban_link,DOUBAN)
        self.imdb_id   = get_id_from_link(self.imdb_link  ,IMDB)

        if self.douban_id != "" or self.imdb_id != "": return True
        else                                         : return False

def trans_imdb_id(mIMDBID):
    if mIMDBID == "": return ""
    tNewIMDBID = mIMDBID.lower().strip()
    if not tNewIMDBID.startswith('tt'): ErrorLog("invalid imdb_id:"+mIMDBID); return ""
    if not tNewIMDBID[2:].isdigit(): ErrorLog("invalid imdb_id:"+mIMDBID); return ""
    #if len(tNewIMDBID) <= 8: ErrorLog("invalid imdb_id:"+mIMDBID); return ""
    tID = tNewIMDBID[2:]
    #if len(tID) >= 8: 
    tNumber = int(tID) 
    tID = str(tNumber)
    if len(tID) < 7: tID = tID.zfill(7)
    tNewIMDBID = 'tt'+tID
    if tNewIMDBID != mIMDBID: ExecLog("warning:diff imdb_id after trans:{}|{}".format(mIMDBID,tNewIMDBID)) 
    return tNewIMDBID

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
        return tempstr[:tIndex2]
    else : 
        tIndex = mLink.find("imdb.com/title/")
        if tIndex == -1 : return ""
        tIndex = tIndex + len("imdb.com/title/")
        tempstr = tempstr[tIndex:]
        tIndex2 = tempstr.find('/')
        return tempstr[:tIndex2]


def find_end_number(mString):
    #  1-15 / 374
    mString = mString.strip('\n')
    mString = mString.strip()
    #print('-----------------')
    info_log(mString)
    #print('-----------------')
    
    tIndex = mString.find('-')
    if tIndex == -1: 
        ExecLog("can't find -:"+mString)
        return -1
    tStartNumber = mString[:tIndex]
    if not tStartNumber.isdigit():
        ExecLog("invalid start number:"+mString)
        return -1

    mString = mString[tIndex+1:]
    tIndex = mString.find('/')
    if tIndex == -1: 
        ExecLog("can't find /:"+mString)
        return -1
    tEndNumber = mString[:tIndex].strip()
    if not tEndNumber.isdigit():
        ExecLog("invalid end number:"+mString)
        return "error"
    
    tTotal = mString[tIndex+1:].strip()
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
            tDoubanID =  get_id_from_link(a['href'],DOUBAN)
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
    tUrl = DOUBAN_VIEWED_URL
    while True:
        try:
            res = s.get(tUrl, headers=my_headers,timeout=120)
            soup = BeautifulSoup(res.text,'lxml')
        except Exception as err:
            print(err)
            ExecLog("except at get url")
            return False
        """
        text = open("viewed2.log").read()
        soup = BeautifulSoup(text,'lxml')
        #print(soup)
        """

        try:
            tSubjectNum = soup.find('span',class_="subject-num").get_text()
        except Exception as err:
            print(err)
            print(soup)
            ExecLog("except at find subject-num")
            return False
        #print(num)
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

        if mOnlyFirstPage :  return True
        if tNextStartNum <= 0: return True   
        tNextStartString = 'start='+str(tNextStartNum)
        tUrl = site_url.replace('start=0',tNextStartString)
        info_log(tUrl)
        time.sleep(10)
        
    return True

