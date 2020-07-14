import re
from gen import Gen
from log import *
from database import *
MOVIE =  0
TV    =  1
RECORD=  2

OK    =  1
NOK  =  -1
RETRY =  0
MAX_DOUBAN_RETRY_TIMES= 3

DOUBAN = 1
IMDB = 2

def get_id_from_link(mLink,tag):
    """
    https://movie.douban.com/subject/1233445/***
    https://www.imdb.com/title/123455/***
    """
    if mLink == "": return ""
    tempstr = mLink.strip(' ')
    if tempstr[-1:] != '/': tempstr = tempstr+'/'
    if tag == DOUBAN: 
        tIndex = mLink.find("douban.com/subject/")
        if tIndex == -1 : return ""
        tIndex = tIndex + len("douban.com/subject/")
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

class Info:
    def __init__(self,mDoubanID="",mIMDBID="",mSpiderStatus=RETRY):
        self.douban_id = mDoubanID
        self.imdb_id = mIMDBID
        self.spider_status = mSpiderStatus

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

    def insert(self):
        if self.imdb_id == "": return False

        #查看数据库是否已经存在记录
        sel_sql = "select name from info where imdbid = %s"
        sel_val = (self.imdb_id,)
        tSelectResult = select(sel_sql,sel_val)
        if tSelectResult == None or len(tSelectResult) == 1: return False

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
        if self.imdb_id == "": print("empty imdb id for update info");return False

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
        return update(up_sql,up_val)

    def select(self,assign_value=True):
        if self.imdb_id == "": return False
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
                "doubanstatus"
                " from info where imdbid = %s")
        sel_val = (self.imdb_id,)
        tSelectResult = select(sel_sql,sel_val)
        if tSelectResult == None: 
            print("error to select from nfo{}::{}".format(self.imdb_id,sel_sql))
            return False
        elif len(tSelectResult) == 0:
            #print("not find nfo in table:"+self.imdb_id)
            return False
        else: pass
        if assign_value == True:
            self.douban_id = tSelectResult[0][0]
            self.douban_score = tSelectResult[0][1]
            self.imdb_score = tSelectResult[0][2]
            self.douban_link = tSelectResult[0][3]
            self.imdb_link = tSelectResult[0][4]
            self.movie_name = tSelectResult[0][5]
            self.foreign_name = tSelectResult[0][6]
            self.other_names = tSelectResult[0][7]
            self.type = tSelectResult[0][8]
            self.nation = tSelectResult[0][9]
            self.director = tSelectResult[0][10]
            self.actors = tSelectResult[0][11]
            self.poster = tSelectResult[0][12]
            self.episodes = tSelectResult[0][13]
            self.genre = tSelectResult[0][14]
            self.spider_status = tSelectResult[0][15]
            self.douban_status = tSelectResult[0][16]

        return True

    def update_or_insert(self):
        if self.imdb_id == "": return False

        if self.select(assign_value=False): return self.update()
        else                              : return self.insert()

    def spider_douban(self):
        if self.douban_status != RETRY  : return self.douban_status

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
            
            if   self.nation[-1:] == '国' : self.nation = self.nation[:-1]  #去除国家最后的国字
            elif self.nation == '香港'    : self.nation = '港'
            elif self.nation == '中国香港': self.nation = '港'
            elif self.nation == '中国大陆': self.nation = '国'
            elif self.nation == '中国台湾': self.nation = '台'
            elif self.nation == '日本'    : self.nation = '日'
            else : pass

            tIndex = self.imdb_score.find('/')
            if tIndex > 0: self.imdb_score = self.imdb_score[:tIndex]
            else:          self.imdb_score = ""

            #判断类型，纪录片，电视剧，电影
            if self.genre.find('纪录') >= 0 :self.type = RECORD
            elif self.episodes > 0          :self.type = TV
            else                            :self.type = MOVIE            

            ExecLog("spider douban:|name:{}|nation:{}|doubanid:{}|imdbid:{}|director:{}|score:{}/{}|".format(
                self.movie_name,self.nation,self.douban_id,self.imdb_id,self.director,self.douban_score,self.imdb_score))
            self.douban_status = OK
            self.spider_status = OK
            return self.douban_status
        else: 
            # TODO 根据错误的不同
            ExecLog("gen error:"+tMovieInfo['error'])
            if tMovieInfo['error'].find("The corresponding resource does not exist") >= 0 or tMovieInfo['error'].find("Can't find this imdb_id") >= 0:
                self.douban_status = NOK
                return self.douban_status
            self.douban_retry_times += 1
            if self.douban_retry_times >= MAX_DOUBAN_RETRY_TIMES:
                self.douban_status = NOK
        return self.douban_status
        # TODO 如果有doubanid，尝试自己爬取

    def spider_detail(self):
        # TODO
        pass

    def get_from_summary(self,mSummary):

        Type = -1
        Nation = Name = Director = Actors = DoubanScore = DoubanID = DoubanLink = IMDBLink = IMDBScore = IMDBID = ""
        #mSummary = re.sub(u'\u3000',u' ',mSummary)    #全角空白字符替换为半角空白字符
        #mSummary = re.sub(u'\xa0', u' ', mSummary)    #
        mSummary = mSummary.replace('　',' ')
        mSummary = mSummary.lower()
        #DebugLog(mSummary)
        #print(mSummary)
                
        if   mSummary.find("国  家")    >= 0: tIndex = mSummary.find("国  家")
        elif mSummary.find("产  地")    >= 0: tIndex = mSummary.find("产  地")
        else                                  : tIndex = -1
        if tIndex >= 0 :
            Nation = mSummary[tIndex+5:tIndex+20]
            if Nation.find('\n') >= 0: Nation = Nation[:Nation.find('\n')]
            if Nation.find('/')  >= 0: Nation = Nation[ :Nation.find('/') ]  #多个国家,以/区隔,取第一个
            Nation = Nation.strip()
            if   Nation[-1:] == '国' : Nation = Nation[:-1]  #去除国家最后的国字
            elif Nation == '香港'    : Nation = '港'
            elif Nation == '中国香港': Nation = '港'
            elif Nation == '中国大陆': Nation = '国'
            elif Nation == '中国台湾': Nation = '台'
            elif Nation == '日本'    : Nation = '日'
            else : pass
            DebugLog("Nation:"+Nation)
        else: DebugLog("failed find nation")
        self.nation = Nation

        if Nation == '港' or Nation == '国' or Nation == '台' : tIndex = mSummary.find("片  名")
        else                                                  : tIndex = mSummary.find("译  名")
        if tIndex >= 0 :
            Name = mSummary[tIndex+5:tIndex+100]
            if Name.find("/")  >= 0 : Name = (Name[ :Name.find("/") ]).strip() 
            if Name.find('\n') >= 0 : Name = (Name[ :Name.find('\n') ]).strip()
        else: DebugLog("failed find name"); Name = ""
        DebugLog("name:"+Name)
        self.movie_name = Name

        tIndex = mSummary.find("豆瓣链接")
        if tIndex >= 0 :
            DoubanLink = mSummary[tIndex+4:]
            if DoubanLink.find('\n') >= 0 : DoubanLink = (DoubanLink[ :DoubanLink.find('\n') ]).strip()
            DoubanLink = DoubanLink.strip()
            if not DoubanLink.startswith('http'): 
                DebugLog("invalid doubanlink:"+DoubanLink)
                DoubanLink = ""
        else: DebugLog("douban link:not find")
        DoubanID = get_id_from_link(DoubanLink, DOUBAN)
        DebugLog("DoubanLink:"+DoubanLink)
        self.douban_id = DoubanID
        self.douban_link = DoubanLink

        tIndex = mSummary.find("豆瓣链接")
        if tIndex >= 0 :
            DoubanLink = mSummary[tIndex+4:]
            if DoubanLink.find('\n') >= 0 : DoubanLink = (DoubanLink[ :DoubanLink.find('\n') ]).strip()
            DoubanLink = DoubanLink.strip()
            if not DoubanLink.startswith('http'): 
                DebugLog("invalid doubanlink:"+DoubanLink)
                DoubanLink = ""
        else: DebugLog("douban link:not find")
        DoubanID = get_id_from_link(DoubanLink, DOUBAN)
        DebugLog("DoubanLink:"+DoubanLink)
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
        DebugLog("imdb link:"+IMDBLink)
        self.imdb_link = IMDBLink
        self.imdb_id = IMDBID

        tIndex = mSummary.find("豆瓣评分")
        if tIndex >= 0 :
            tempstr = mSummary[tIndex+5:tIndex+16]
            tSearch = re.search("[0-9]\.[0-9]",tempstr)
            if tSearch : DoubanScore = tSearch.group()
            else:        DoubanScore = ""
            DebugLog("douban score:"+DoubanScore)
        else: DebugLog("douban score:not find")
        self.douban_score = DoubanScore

        if   mSummary.find("imdb评分")    >= 0: tIndex = mSummary.find("imdb评分")           
        elif mSummary.find('imdb.rating') >= 0: tIndex = mSummary.find('imdb.rating')
        elif mSummary.find('imdb rating') >= 0: tIndex = mSummary.find('imdb rating')            
        else: tIndex = -1               
        if tIndex >= 0 :
            tempstr = mSummary[tIndex+6:tIndex+36]
            tSearch = re.search("[0-9]\.[0-9]",tempstr)
            if tSearch :  IMDBScore = tSearch.group()
        DebugLog("imdb score:"+IMDBScore)
        self.imdb_score = IMDBScore

        tIndex = mSummary.find("类  别") 
        if tIndex >= 0 and mSummary[tIndex:tIndex+100].find("纪录") >= 0 : Type = RECORD
        elif mSummary.find("集  数") >= 0                                : Type = TV
        else                                                               : Type = MOVIE
        DebugLog("type:"+str(Type))
        self.type = Type

        tIndex = mSummary.find("导  演")
        if tIndex >= 0 :
            Director = mSummary[tIndex+5:tIndex+100]
            tEndIndex = Director.find('\n')
            if tEndIndex >= 0 : Director = Director[:tEndIndex]
            else : Director = ""
        else :Director = ""
        Director = Director.strip()
        DebugLog("director:"+Director)
        self.director = Director
