#!/usr/bin/python3
# coding=utf-8
import re
import requests
from bs4 import BeautifulSoup
import json
import time

from database import *

global g_config
MAX_DOUBAN_RETRY_TIMES = 3

MOVIE = 0
TV = 1
RECORD = 2

OK = 1
NOK = -1
RETRY = 0

DOUBAN = 1
IMDB = 2


class Info:
    def __init__(self, douban_id="", imdb_id="", douban_status=RETRY):
        self._douban_id = douban_id
        self._imdb_id = imdb_id
        self.douban_status = douban_status  # 0 RETRY,1 OK, -1 NOK
        self.douban_retry_times = 0

        self.douban_score = ""
        self.imdb_score = ""
        self.douban_link = ""
        self.imdb_link = ""
        self.movie_name = ""
        self.foreign_name = ""
        self.other_names = ""
        self.type = MOVIE  # 0 movie,1 TV,2 RECORD
        self.nation = ""
        self.year = 0
        self.director = ""
        self.actors = ""
        self.poster = ""
        self.episodes = 0
        self.genre = ""
        self.viewed = 0

        if self.douban_id == "" and self.imdb_id == "":
            error_log("Info.init():id is null")

        self.error_string = ""

        self.select()

    @property
    def douban_id(self):
        return self._douban_id

    @douban_id.setter
    def douban_id(self, douban_id):
        self._douban_id = Info.check_douban_id(douban_id)

    @property
    def imdb_id(self):
        return self._imdb_id

    @imdb_id.setter
    def imdb_id(self, imdb_id):
        self._imdb_id = Info.check_imdb_id(imdb_id)

    def insert(self):
        if self.imdb_id == "" and self.douban_id == "":
            return False

        # 查看数据库是否已经存在记录
        if self.select(False):
            return False
        debug_log("插入info表记录:{}|{}".format(self.douban_id, self.imdb_id))

        in_sql = ("insert into info"
                  "(doubanid,imdbid,doubanscore,imdbscore,doubanlink,imdblink,name,foreignname,othernames,type,nation,year,director,actors,poster,episodes,genre,doubanstatus)"
                  "values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)")
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
        return insert(in_sql, in_val)

    def update(self):
        if self.imdb_id == "" and self.douban_id == "":
            info_log("empty id for update info")
            return False

        debug_log("更新info表记录:{}|{}".format(self.douban_id, self.imdb_id))
        # douban_id first
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
        if not update(up_sql, up_val):
            return False

        # 单独更新viewed，避免被内存中错误的标记更新。只有内存中的viewed=1才更新数据库
        if self.viewed == 1:
            if self.douban_id != "":
                return update("update info set viewed=1 where doubanid = %s", (self.douban_id,))
            else:
                return update("update info set viewed=1 where imdbid = %s", (self.imdb_id,))
        return True

    def select(self, assign_value=True):
        if self.imdb_id == "" and self.douban_id == "":
            return False
        return self.select_by_douban_id(assign_value) or self.select_by_imdb_id(assign_value)

    def select_by_imdb_id(self, assign_value=True):
        if self.imdb_id == "":
            return False
        debug_log("select from info:" + self.imdb_id)
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
        t_select_result = select(sel_sql, sel_val)
        if t_select_result is None:
            error_log("error to select from nfo{}::{}".format(self.imdb_id, sel_sql))
            return False
        elif len(t_select_result) == 0:
            # print("not find nfo in table:"+self.imdb_id)
            return False
        elif len(t_select_result) >= 2:
            error_log("2+ record select_by_imdb_id from nfo:{}".format(self.imdb_id))
            return False
        else:
            pass
        if assign_value:
            if t_select_result[0][0] != "": self.douban_id = t_select_result[0][0]
            if t_select_result[0][1] != "": self.douban_score = t_select_result[0][1]
            if t_select_result[0][2] != "": self.imdb_score = t_select_result[0][2]
            if t_select_result[0][3] != "": self.douban_link = t_select_result[0][3]
            if t_select_result[0][4] != "": self.imdb_link = t_select_result[0][4]
            if t_select_result[0][5] != "": self.movie_name = t_select_result[0][5]
            if t_select_result[0][6] != "": self.foreign_name = t_select_result[0][6]
            if t_select_result[0][7] != "": self.other_names = t_select_result[0][7]
            if t_select_result[0][8] != -1: self.type = t_select_result[0][8]
            if t_select_result[0][9] != "": self.nation = t_select_result[0][9]
            if t_select_result[0][10] != "": self.director = t_select_result[0][10]
            if t_select_result[0][11] != "": self.actors = t_select_result[0][11]
            if t_select_result[0][12] != "": self.poster = t_select_result[0][12]
            if t_select_result[0][13] != -1: self.episodes = t_select_result[0][13]
            if t_select_result[0][14] != "": self.genre = t_select_result[0][14]
            if t_select_result[0][15] != -2: self.douban_status = t_select_result[0][15]
            if t_select_result[0][16] != 0: self.year = t_select_result[0][16]
            if t_select_result[0][17] != -1: self.viewed = t_select_result[0][17]
        return True

    def select_by_douban_id(self, assign_value=True):
        if self.douban_id == "": return False
        debug_log("select from info:" + self.douban_id)
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
        t_select_result = select(sel_sql, sel_val)
        if t_select_result is None:
            info_log("error to select from nfo{}::{}".format(self.douban_id, sel_sql))
            return False
        elif len(t_select_result) == 0:
            # print("not find nfo in table:"+self.imdb_id)
            return False
        elif len(t_select_result) >= 2:
            error_log("2+ record select_by_douban_id from nfo:{}".format(self.douban_id))
            return False
        else:
            pass
        if assign_value:
            if t_select_result[0][0] != "": self.imdb_id = t_select_result[0][0]
            if t_select_result[0][1] != "": self.douban_score = t_select_result[0][1]
            if t_select_result[0][2] != "": self.imdb_score = t_select_result[0][2]
            if t_select_result[0][3] != "": self.douban_link = t_select_result[0][3]
            if t_select_result[0][4] != "": self.imdb_link = t_select_result[0][4]
            if t_select_result[0][5] != "": self.movie_name = t_select_result[0][5]
            if t_select_result[0][6] != "": self.foreign_name = t_select_result[0][6]
            if t_select_result[0][7] != "": self.other_names = t_select_result[0][7]
            if t_select_result[0][8] != -1: self.type = t_select_result[0][8]
            if t_select_result[0][9] != "": self.nation = t_select_result[0][9]
            if t_select_result[0][10] != "": self.director = t_select_result[0][10]
            if t_select_result[0][11] != "": self.actors = t_select_result[0][11]
            if t_select_result[0][12] != "": self.poster = t_select_result[0][12]
            if t_select_result[0][13] != -1: self.episodes = t_select_result[0][13]
            if t_select_result[0][14] != "": self.genre = t_select_result[0][14]
            if t_select_result[0][15] != -2: self.douban_status = t_select_result[0][15]
            if t_select_result[0][16] != 0: self.year = t_select_result[0][16]
            if t_select_result[0][17] != -1: self.viewed = t_select_result[0][17]
        return True

    def update_or_insert(self):
        if self.imdb_id == "" and self.douban_id == "":
            return False

        if self.select(assign_value=False):
            return self.update()
        else:
            return self.insert()

    def remove_special_char(self):
        self.director = self.director.replace('|', ',')
        self.actors = self.actors.replace('|', ',')
        self.movie_name = self.movie_name.replace('|', ',')
        self.other_names = self.other_names.replace('|', ',')
        self.foreign_name = self.foreign_name.replace('|', ',')
        self.genre = self.genre.replace('|', ',')

    def spider_douban(self):
        if self.douban_status != RETRY: 
            return self.douban_status

        # 如果douban_id为空，尝试通过imdb_id获取douban_id
        if self.douban_id == "":
            self.douban_id = Info.get_douban_id_by_imdb_id(self.imdb_id)
            if self.douban_id == "":
                error_log("failed to find douban_id from imdb_id:" + self.imdb_id)
                self.error_string = f"failed to find douban_id from imdb_id:{self.imdb_id}"
                self.douban_status = NOK
                return self.douban_status

        if self.douban_detail():
            exec_log("  豆瓣详情:{}|{}|{}|{}|{}|{}/{}|".format(
                self.movie_name, self.nation, self.douban_id, self.imdb_id, self.director, self.douban_score,
                self.imdb_score))
            self.douban_status = OK
            return self.douban_status

        self.douban_retry_times += 1
        if self.douban_retry_times >= MAX_DOUBAN_RETRY_TIMES:
            self.douban_status = NOK
        return self.douban_status

    def download_poster(self, save_path):
        if self.poster == "":
            return False

        dest_full_file = os.path.join(save_path, "poster.jpg")
        try:
            f = requests.get(self.poster, timeout=120)
            with open(dest_full_file, "wb") as code:
                code.write(f.content)
        except Exception as err:
            log_print(err)
            error_log("failed to download poster.jpg from:" + self.poster)
            return False
        return True

    def to_dict(self):
        info_dict = {
            "douban_id": self.douban_id,
            "imdb_id": self.imdb_id,
            "douban_score": self.douban_score,
            "imdb_score": self.imdb_score,
            "movie_name": self.movie_name,
            "director": self.director,
            "actors": self.actors,
            "nation": self.nation,
            "type": self.type,
            "genre": self.genre,
            "poster": self.poster,
            "viewed": self.viewed
        }
        return info_dict

    @staticmethod
    def from_json_string(json_string):
        try:
            dict_info = json.loads(json_string)
        except Exception as err:
            print(err)
            return None
        return Info.from_dict(dict_info)

    @staticmethod
    def from_dict(dict_info):
        douban_id = dict_info.get('douban_id')
        if douban_id is None:
            exec_log(f"json douban_id error:{dict_info}")
            return None
        imdb_id = dict_info.get('imdb_id')
        if douban_id is None:
            exec_log(f"json imdb_id error:{dict_info}")
            return None
        info = Info(douban_id, imdb_id)

        if dict_info.get('douban_score', "") != "":
            info.douban_score = dict_info.get('douban_score')
        if dict_info.get('imdb_score', "") != "": 
            info.imdb_score = dict_info.get('imdb_score')
        if dict_info.get('movie_name', "") != "":
            info.movie_name = dict_info.get('movie_name')
        if dict_info.get('nation', "") != "": 
            info.nation = dict_info.get('nation')
        if dict_info.get('director', "") != "":
            info.director = dict_info.get('director')
        if dict_info.get('actors', "") != "": 
            info.actors = dict_info.get('actors')
        if dict_info.get('type', -1) != "": 
            info.type = dict_info.get('type')
        if dict_info.get('genre', "") != "":
            info.genre = dict_info.get('genre')
        if dict_info.get('poster', "") != "":
            info.poster = dict_info.get('poster')
        if dict_info.get('viewed', -1) != "": 
            info.viewed = dict_info.get('viewed')
        return info

    @staticmethod
    def get_douban_id_by_imdb_id(imdb_id=""):
        if imdb_id == "":
            return False

        cookie_dict = {"cookie": g_config.DOUBAN_COOKIE}
        s = requests.Session()
        s.cookies.update(cookie_dict)

        t_url = g_config.DOUBAN_SEARCH_URL + imdb_id
        my_headers = {'User-Agent': g_config.USER_AGENT}
        try:
            res = s.get(t_url, headers=my_headers, timeout=120)
            time.sleep(60)  # 休眠1分钟，避免连续请求豆瓣被禁
            soup = BeautifulSoup(res.text, 'lxml')
        except Exception as err:
            print(err)
            error_log("except at get url:" + t_url)
            return ""
        """
        text = open("detail2.log").read()
        soup = BeautifulSoup(text,'lxml')
        """
        # print(soup)

        if str(soup).find("异常请求") >= 0:
            error_log("failed to request douban search")
            error_log(res.text)
            return False

        t_douban_id = ""
        for item in soup.find_all('a'):
            if item["href"].find("movie/subject") >= 0:
                t_douban_id2 = Info.get_id_from_link(item['href'], DOUBAN)
                if t_douban_id == "":
                    t_douban_id = t_douban_id2
                elif t_douban_id2 != t_douban_id:
                    error_log("find different douban_id:{}|{}".format(t_douban_id, t_douban_id2))
                    return False
                else:
                    pass
        return t_douban_id

    def douban_detail(self):
        """
        
        """
        if self.douban_id == "":
            return False

        cookie_dict = {"cookie": g_config.DOUBAN_COOKIE}
        s = requests.Session()
        s.cookies.update(cookie_dict)

        t_url = g_config.DOUBAN_URL + self.douban_id
        my_headers = {'User-Agent': g_config.USER_AGENT}
        try:
            res = s.get(t_url, headers=my_headers, timeout=120)
            time.sleep(60)  # 休眠1分钟，避免连续请求豆瓣被禁
            soup = BeautifulSoup(res.text, 'lxml')
        except Exception as err:
            print(err)
            error_log("except at get url:" + t_url)
            self.error_string = str(err)
            return False
        """
        text = open("detail2.log").read()
        soup = BeautifulSoup(text,'lxml')
        """
        # print(soup)

        if str(soup).find("异常请求") >= 0:
            error_log("failed to request douban detail")
            self.error_string = "failed to request douban detail"
            error_log(res.text)
            return False
        if "页面不存在" in soup.title.text:
            error_log("the douban id does not exist:" + self.douban_id)
            error_log(res.text)
            self.error_string = f"the douban_id does not exist:{self.douban_id}"
            return False

        # 名称/外国名称
        self.movie_name = soup.title.text.replace("(豆瓣)", "").strip()
        foreign_name_item = soup.find('span', property="v:itemreviewed")
        self.foreign_name = foreign_name_item.text.replace(self.movie_name, '').strip() if foreign_name_item is not None else ""
        info_log(self.movie_name)
        info_log(self.foreign_name)

        # 年代
        year_anchor = soup.find('span', class_='year')
        self.year = int(year_anchor.text[1:-1]) if year_anchor else 0
        info_log(str(self.year))

        info = soup.find('div', id='info')
        # print (info)

        # 其他电影名
        other_names_anchor = info.find('span', class_='pl', text=re.compile('又名'))
        self.other_names = other_names_anchor.next_element.next_element if other_names_anchor else ""
        info_log(self.other_names)

        # 国家/地区
        nation_anchor = info.find('span', class_='pl', text=re.compile('制片国家/地区'))
        self.nation = nation_anchor.next_element.next_element if nation_anchor else ""
        if self.nation.find('/') >= 0:
            self.nation = (self.nation[:self.nation.find('/')]).strip()
        self.nation = self.trans_nation(self.nation)
        info_log(self.nation)

        # imdb链接和imdb_id
        imdb_anchor = info.find('a', text=re.compile("tt\d+"))
        # info_log (imdb_anchor)
        self.imdb_id = imdb_anchor.text if imdb_anchor else ""
        self.imdb_link = imdb_anchor['href'] if imdb_anchor else ""
        info_log(self.imdb_id)
        info_log(self.imdb_link)

        # 类型
        genre_anchor = info.find_all('span', property='v:genre')
        # print(genre_anchor)
        genre_list = []
        for genre in genre_anchor:
            genre_list.append(genre.get_text())
        self.genre = '/'.join(genre_list)
        info_log(self.genre)

        # 集数
        episodes_anchor = info.find("span", class_="pl", text=re.compile("集数"))
        self.episodes = int(episodes_anchor.next_element.next_element) if episodes_anchor else 0  # 集数
        # print(episodes_anchor)
        info_log(str(self.episodes))

        # type
        if self.genre.find('纪录') >= 0:
            self.type = RECORD
        elif self.episodes > 1:
            self.type = TV
        else:
            self.type = MOVIE
        info_log(str(self.type))

        json_anchor = soup.find('script', type="application/ld+json")
        # print('-------------------------')
        # print (json_anchor.string)
        # 部分时候解析json失败，发现错误分行导致，因此删除换行字符\n后再去解析
        json_string = json_anchor.string.replace('\n', ' ') if json_anchor else ""

        # json_string = "".join(i  for i in json_string if 31<ord(i)<127)
        json_string = "".join(i for i in json_string if 31 < ord(i))  # 根据ascii码去除特殊字符
        json_string = json_string.replace('\\', '\\\\')

        # json_string = json_string.replace('\t','')
        # json_string = re.sub('[\x00-\x09|\x0b-\x0c|\x0e-\x1f]','',json_string)
        info_log(json_string)
        try:
            data = json.loads(json_string, strict=False)
        except Exception as err:
            print(err)
            exec_log(f"解析json出现错误：{self.douban_id}")
            self.error_string = f"解析json出现错误：{self.douban_id}"
            return False
        # print(data)
        if data is None:
            exec_log('爬取豆瓣详情出现错误:没有找到"json "')
            self.error_string = f"豆瓣详情页没有找到json：{self.douban_id}"
            return False

        t_type = data['@type']
        info_log(str(t_type))

        # 海报
        self.poster = data['image']
        info_log(self.poster)

        # 豆瓣评分
        self.douban_score = data['aggregateRating']['ratingValue']
        info_log(self.douban_score)

        # 导演和演员
        def data_join(t_data, t_key):
            t_list = []
            for t_data in t_data:
                t_list.append(t_data.get(t_key))
            return '/'.join(t_list)

        self.director = data_join(data['director'], 'name')
        self.actors = data_join(data['actor'], 'name')
        info_log(self.director)
        info_log(self.actors)

        self.remove_special_char()
        if self.nation != '' and self.movie_name != "":
            if not self.update_or_insert(): 
                exec_log(f"插入/更新表info出现错误:{self.douban_id}|{self.imdb_id}|{self.movie_name}")
            self.douban_status = OK
            # self.spider_status = OK
            return True
        else:
            self.douban_status = NOK
            self.error_string = f"爬取豆瓣详情页，没有找到影片名或者产地:{self.douban_id}"
            return False

    @staticmethod
    def get_from_detail(soup):
        """
        FRDS网站的电影信息不同于其他站，不能从电影简介中获取信息，而需要从html中获取链接
        """
        douban_id = imdb_id = ""
        kdouban_anchor = soup.find('div', id='kdouban')
        site_log("kdouban:{}".format(kdouban_anchor))
        if kdouban_anchor:
            douban_link_anchor = kdouban_anchor.find('a', class_='imdbwp__link')
            douban_link = douban_link_anchor['href']
            douban_id = Info.get_id_from_link(douban_link, DOUBAN)
            site_log(douban_link)

        kimdb_anchor = soup.find('div', id='kimdb')
        site_log("kimdb:{}".format(kimdb_anchor))
        if kimdb_anchor:
            imdb_link_anchor = kimdb_anchor.find('a', class_='imdbwp__link')
            imdb_link = imdb_link_anchor['href']
            imdb_id = Info.get_id_from_link(imdb_link, IMDB)
            site_log(imdb_link)

        if douban_id != "" or imdb_id != "":
            return True, douban_id, imdb_id
        else:
            return False, douban_id, imdb_id

    @staticmethod
    def get_from_summary(summary):
        douban_id = imdb_id = ""
        summary = summary.replace('　', ' ')
        summary = summary.lower()

        t_result = re.search("douban\.com/subject/\d+", summary)
        if t_result is not None:
            douban_link = "https://movie." + t_result.group()
            douban_id = Info.get_id_from_link(douban_link, DOUBAN)
        else:
            t_result = re.search("douban\.com/movie/subject/\d+", summary)
            if t_result is not None:
                douban_link = "https://www." + t_result.group()
                douban_id = Info.get_id_from_link(douban_link, DOUBAN)

        t_result = re.search("imdb\.com/title/tt\d+", summary)
        if t_result is not None:
            imdb_link = "https://www." + t_result.group()
            imdb_id = Info.get_id_from_link(imdb_link, IMDB)
        else:
            t_result = re.search("tt[0-9][0-9][0-9][0-9][0-9]+ ", summary)
            if t_result is not None:
                imdb_id = Info.check_imdb_id(t_result.group())
            else:
                t_result = re.search("tt[0-9][0-9][0-9][0-9][0-9]+\n", summary)
                if t_result is not None:
                    imdb_id = t_result.group()
                    if imdb_id[-1:] == '\n': 
                        imdb_id = imdb_id[:-1]

        if douban_id != "" or imdb_id != "":
            return True, douban_id, imdb_id
        else:
            return False, douban_id, imdb_id

    @staticmethod
    def check_douban_id(douban_id):
        douban_id = douban_id.strip()
        if douban_id != "" and not douban_id.isdigit(): 
            error_log("invalid doubanid:" + douban_id) 
            return ""
        return douban_id

    @staticmethod
    def check_imdb_id(imdb_id):
        imdb_id = imdb_id.lower().strip()
        if imdb_id == "":
            return ""
        if not (imdb_id.startswith('tt') and imdb_id[2:].isdigit()): 
            error_log("invalid imdb_id:" + imdb_id)
            return ""

        # 不允许tt以后的数字大于等于7位数，前面还加0
        number = int(imdb_id[2:])
        t_id = str(number) if len(str(number)) >= 7 else str(number).zfill(7)
        return 'tt' + t_id

    @staticmethod
    def trans_nation(nation):
        t_nation = nation.strip()
        if t_nation[-1:] == '国':
            t_nation = t_nation[:-1]  # 去除国家最后的国字
        elif t_nation == '香港':
            t_nation = '港'
        elif t_nation == '中国香港':
            t_nation = '港'
        elif t_nation == '中国大陆':
            t_nation = '国'
        elif t_nation == '中国台湾':
            t_nation = '台'
        elif t_nation == '日本':
            t_nation = '日'
        else:
            pass
        return t_nation

    @staticmethod
    def get_id_from_link(link, tag):
        """
        https://movie.douban.com/subject/1233445/***
        https://www.douban.com/movie/subject/1233445/***
        https://www.imdb.com/title/123455/***
        """
        if link == "":
            return ""
        temp_str = link.strip(' ')
        temp_str = temp_str.replace("\r", "")
        if temp_str[-1:] != '/':
            temp_str = temp_str + '/'
        if tag == DOUBAN:
            if link.find("douban.com/subject/") >= 0:
                t_index = link.find("douban.com/subject/") + len("douban.com/subject/")
            elif link.find("movie/subject/") >= 0:
                t_index = link.find("movie/subject/") + len("movie/subject/")
            else:
                return ""
            temp_str = temp_str[t_index:]
            t_index2 = temp_str.find('/')
            return Info.check_douban_id(temp_str[:t_index2])
        else:
            t_index = link.find("imdb.com/title/")
            if t_index == -1:
                return ""
            t_index = t_index + len("imdb.com/title/")
            temp_str = temp_str[t_index:]
            t_index2 = temp_str.find('/')
            return Info.check_imdb_id(temp_str[:t_index2])


def find_end_number(string):
    """
    输入格式举例：  "1-15 / 374"
    return:
        -1       : 解析出错
        0        : 已经到达最后一页
        endnumber: 本页的结束number，例如15
    """

    string = string.strip('\n')
    string = string.strip()
    # print('-----------------')
    info_log(string)
    # print('-----------------')

    t_index = string.find('-')
    if t_index == -1:
        exec_log("can't find -:" + string)
        return -1
    t_start_number = string[:t_index]  # 本页起始number, 如1
    if not t_start_number.isdigit():
        exec_log("invalid start number:" + string)
        return -1

    string = string[t_index + 1:]
    t_index = string.find('/')
    if t_index == -1:
        exec_log("can't find /:" + string)
        return -1
    t_end_number = string[:t_index].strip()  # 本页结束number，如15
    if not t_end_number.isdigit():
        exec_log("invalid end number:" + string)
        return "error"

    t_total = string[t_index + 1:].strip()  # 总数
    if not t_end_number.isdigit():
        exec_log("invalid total number:" + string)
        return -1

    if int(t_end_number) != int(t_total):
        return int(t_end_number)
    else:
        return 0


def find_douban_id(item):
    try:
        for a in item.find_all('a'):
            # print(a)
            # print(a['href'])
            t_douban_id = Info.get_id_from_link(a['href'], DOUBAN)
            if t_douban_id.isdigit():
                return t_douban_id
    except Exception as err:
        print(item)
        print(err)
        exec_log("exception at find_douban_id")
        return ""
    return ""


def update_viewed(only_first_page=True):
    cookie_dict = {"cookie": g_config.DOUBAN_COOKIE}
    s = requests.Session()
    s.cookies.update(cookie_dict)

    my_headers = {'User-Agent': g_config.USER_AGENT}
    t_url = g_config.DOUBAN_VIEWED_URL  # 观影记录首页
    while True:
        try:
            res = s.get(t_url, headers=my_headers, timeout=120)
            soup = BeautifulSoup(res.text, 'lxml')
        except Exception as err:
            print(err)
            exec_log("except at get url")
            return False

        try:
            t_subject_num = soup.find('span', class_="subject-num").get_text()  # 举例 1-15 / 374
        except Exception as err:
            print(err)
            print(soup)
            exec_log("except at find subject-num")
            return False

        # 获取下一页开始number
        # 因url中的编号是从0开始的，而显示记录是从1开始的。下一页的开始number就是本页中的endnumber
        t_next_start_num = find_end_number(t_subject_num)
        # print(tNextStartNum)

        try:
            t_viewed = soup.find('div', class_="grid-view")
            t_items = t_viewed.find_all('div', class_="item")
        except Exception as err:
            print(err)
            print(soup)
            exec_log("except at find grid-view")
            return False
        # print(viewed)
        for item in t_items:
            # print('----------------------------------------')
            # print(item)
            # print('----------------------------------------')
            try:
                t_title = item.find('em').get_text()
            except Exception as err:
                print(err)
                print(item)
                exec_log("except at find em")
                return False
            t_douban_id = find_douban_id(item)
            if t_douban_id == "":
                exec_log("can't find douban_id:" + t_title)
                continue
            # print("{}:{}".format(tTitle,tDoubanID))

            # 更新info表中的viewed标志
            record = select("select viewed,name from info where doubanid=%s ", (t_douban_id,))
            if record is None:
                error_log("error:执行数据库select错误")
                return False
            if len(record) == 0:
                exec_log(f"{t_douban_id} does not exist in table info")
            elif len(record) > 1:
                exec_log(f"{t_douban_id} have more than 1 record in table info")
            else:
                viewed = record[0][0]
                name = record[0][1]
                if viewed == 0:
                    if update("update info set viewed = 1 where doubanid=%s ", (t_douban_id,)):
                        exec_log(f"更新info表观影记录：{name}")
                    else:
                        error_log(f"更新info表出错:{t_douban_id}")
                else:
                    debug_log(f"{name} 已经更新过viewed=1")

        if only_first_page:
            return True  # 如果仅更新第一页，就返回，否则继续获取下一页
        if t_next_start_num <= 0:
            return True
        t_next_start_string = 'start=' + str(t_next_start_num)
        t_url = g_config.DOUBAN_VIEWED_URL.replace('start=0', t_next_start_string)
        info_log(t_url)
        time.sleep(30)
