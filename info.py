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
