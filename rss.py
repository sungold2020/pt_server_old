#!/usr/bin/python3
# coding=utf-8

import requests
import re
from bs4 import BeautifulSoup

from database import *
from ptsite import *
import torrentool.api


class RSS:
    def __init__(self, HASH='', rss_name='', download_link='', detail_url='', title='', douban_id="", imdb_id="",
                 add_datetime="", total_size=0, id_status=RETRY):
        self._HASH = HASH
        self.rss_name = rss_name
        self._download_link = download_link
        self._detail_url = detail_url
        self.title = title
        self._add_datetime = add_datetime if add_datetime != "" else datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self._total_size = total_size

        self.error_string = ""
        self.downloaded = 0
        self.torrent_id = self.get_torrent_id(download_link)

        self.info = None
        douban_id = Info.check_douban_id(douban_id)
        imdb_id = Info.check_imdb_id(imdb_id)
        self._id_status = id_status
        self.id_from_detail = self._id_status
        self.retry_times = 0

        self._torrent_name = ""
        self._files = []

        # (verify id_status)
        if (douban_id == "" and imdb_id == "") and self._id_status == OK:
            self.id_status = RETRY
            error_log("id is empty,but id_status is ok:" + self.title)
        if (douban_id != "" or imdb_id != "") and self._id_status != OK:
            self._id_status = OK
            error_log("id is not empty,but id_status is not ok:" + self.title)
        # get id
        if douban_id == "" and imdb_id == "":
            if self.id_status == RETRY:
                self.get_id_from_detail()
        else:  # get douban_info
            self.info = Info(douban_id, imdb_id)

            # 如果HASH或者total_size为空就通过下载种子文件并获取相关信息
        if self._total_size == 0 or self._HASH == "":
            self.get_torrent_info()

        # 如果rss_name空，尝试读取rss表获取记录
        if self.rss_name == "":
            self.select_by_hash()

    @property
    def download_link(self):
        # pthome的downloadlink是临时链接，转换为带passkey的下载链接
        if self.rss_name.lower().startswith("pthome"):
            return NexusPage.get_download_link(self.rss_name, self.torrent_id)
        return self._download_link

    @download_link.setter
    def download_link(self, download_link):
        self._download_link = download_link

    @property
    def detail_url(self):
        """
        两种情况：
        1、detail_url为空，根据torrent_id去组装detail_url;
        2、detail_url缺网站名(例如:details?id=xxx),则需要补充完整detail_url
        """
        if self._detail_url == "":
            self._detail_url = NexusPage.get_detail_url(self.rss_name, self.torrent_id)
        if not self._detail_url.startswith("http"):
            self._detail_url = NexusPage.complete_detail_url(self.rss_name, self._detail_url)
        return self._detail_url

    @detail_url.setter
    def detail_url(self, detail_url):
        self._detail_url = detail_url

    @property
    def HASH(self):
        if self._HASH == "":
            error_log("error:_HASH is null:" + self.name)
        return self._HASH

    @HASH.setter
    def HASH(self, HASH):
        if HASH == "":
            error_log("error:HASH is null:" + self.name)
        self._HASH = HASH

    @property
    def douban_id(self):
        return self.info.douban_id if self.info is not None else ""

    @property
    def imdb_id(self):
        return self.info.imdb_id if self.info is not None else ""

    @property
    def total_size(self):
        return self._total_size

    @total_size.setter
    def total_size(self, total_size):
        self._total_size = total_size

    @property
    def torrent_name(self):
        if self._torrent_name == "": self.get_torrent_info()
        return self._torrent_name

    @property
    def name(self):  # 中文电影名+torrent_name
        if self.torrent_name == "":
            return self.title
        if self.movie_name == "":
            return self.torrent_name
        # 如果torrent_name前10个字符中包含了中文，就认为包含了中文电影名，否则认为未包含
        return self.torrent_name if re.search(u"[\u4e00-\u9f50]+",
                                              self.torrent_name[:10]) is not None else self.movie_name + self.torrent_name

    @property
    def files(self):
        if self._files == "":
            self.get_torrent_info()
        return self._files

    @property
    def add_datetime(self):
        return self._add_datetime
    @add_datetime.setter
    def add_datetime(self, add_datetime):
        self._add_datetime = add_datetime

    @property
    def id_status(self):
        return self._id_status

    @id_status.setter
    def id_status(self, id_status):
        debug_log(f"set id_status:{id_status}|{self.title}")
        self._id_status = id_status

    @property
    def douban_status(self):
        return self.info.douban_status if self.info is not None else RETRY

    @douban_status.setter
    def douban_status(self, douban_status):
        if self.info is not None:
            self.info.douban_status = douban_status

    @property
    def douban_score(self):
        return self.info.douban_score if self.info is not None else ""

    @douban_score.setter
    def douban_score(self, douban_score):
        if self.info is not None:
            self.info.douban_score = douban_score

    @property
    def imdb_score(self):
        return self.info.imdb_score if self.info is not None else ""

    @imdb_score.setter
    def imdb_score(self, imdb_score):
        if self.info is not None:
            self.info.imdb_score = imdb_score

    @property
    def director(self):
        return self.info.director if self.info is not None else ""

    @property
    def actors(self):
        return self.info.actors if self.info is not None else ""

    @property
    def type(self):
        return self.info.type if self.info is not None else MOVIE

    @property
    def poster(self):
        return self.info.poster if self.info is not None else ""

    @property
    def nation(self):
        return self.info.nation if self.info is not None else ""

    @property
    def movie_name(self):
        return self.info.movie_name if self.info is not None else ""

    def download_poster(self, save_path):
        return self.info.download_poster(save_path) if self.info is not None else False

    def spider_douban(self):
        if self.info is None:
            error_log("spider douban,info is null:" + self.name)
            return False
        return_code = self.info.spider_douban()
        if return_code == NOK:
            self.error_string = self.info.error_string
        return return_code

    def print(self):
        print(self.get_hash())
        print(self.name)
        print(self.rss_name)
        print(self.title)
        print(self.download_link)
        print(self.add_status)
        print(self.total_size)
        print(self.ad_datetime)
        print(self.douban_id)
        print(self.imdb_id)
        print(self.id_status)
        print(self.douban_status)
        print(self.douban_score)
        print(self.imdb_score)
        print(self.error_code)
        print(self.error_string)
    def select(self, assign_value=True):
        if self.rss_name == "":
            return False
        if self._HASH != "":  # 通过免费种子加入时，有torrent_id，无HASH
            sel_sql = "select title,downloadlink,detailurl,doubanid,imdbid,downloaded,torrentid,datetime,size from rss where rssname=%s and HASH=%s"
            sel_val = (self.rss_name, self.HASH)
            t_select_result = select(sel_sql, sel_val)
            t_sql = "select title,downloadlink,detailurl,torrentid,downloaded,datetime,size from rss where rssname={} and HASH={}".format(
                self.rss_name, self.HASH)
            if t_select_result is None:
                error_log("failed to exec :" + t_sql)
                return False
            if len(t_select_result) == 0:
                return False
            elif len(t_select_result) > 1:
                error_log("find 2+record:" + t_sql)
                return False
            else:
                pass
            if assign_value:
                self.title = t_select_result[0][0]
                self.download_link = t_select_result[0][1]
                self.detail_url = t_select_result[0][2]
                douban_id = t_select_result[0][3]
                imdb_id = t_select_result[0][4]
                self.downloaded = t_select_result[0][5]
                self.torrent_id = t_select_result[0][6]
                self.add_datetime = t_select_result[0][7] if t_select_result[0][7] is not None else ""
                self.total_size = t_select_result[0][8]
                if douban_id != "" or imdb_id != "":
                    self.info = Info(douban_id, imdb_id)
            return True
        elif self.torrent_id != "":
            sel_sql = "select title,downloadlink,detailurl,doubanid,imdbid,HASH,downloaded,datetime,size from rss where rssname=%s and torrentid=%s"
            sel_val = (self.rss_name, self.torrent_id)
            t_select_result = select(sel_sql, sel_val)
            t_sql = "select title,download_link,detailurl,HASH,downloaded,datetime,size from rss where rssname={} and torrentid={}".format(
                self.rss_name, self.torrent_id)
            if t_select_result is None:
                error_log("failed to exec :" + t_sql)
                return False
            if len(t_select_result) == 0:
                return False
            elif len(t_select_result) > 1:
                error_log("find 2+record:" + t_sql)
                return False
            else:
                pass
            if assign_value:
                self.title = t_select_result[0][0]
                self.download_link = t_select_result[0][1]
                self.detail_url = t_select_result[0][2]
                douban_id = t_select_result[0][3]
                imdb_id = t_select_result[0][4]
                self.HASH = t_select_result[0][5]
                self.downloaded = t_select_result[0][6]
                self.add_datetime = t_select_result[0][7]
                self.total_size = t_select_result[0][8]
                if douban_id != "" or imdb_id != "":
                    self.info = Info(douban_id, imdb_id)
            return True
        else:
            return False

    def select_by_hash(self, assign_value=True):
        if self._HASH == "":
            return False
        sel_sql = "select title,downloadlink,detailurl,doubanid,imdbid,downloaded,torrentid,datetime,size from rss where HASH=%s"
        sel_val = (self.HASH,)
        t_select_result = select(sel_sql, sel_val)
        t_sql = "select title,downloadlink,detailurl,torrentid,downloaded,datetime,size from rss where HASH={}".format(
            self.HASH)
        if t_select_result is None:
            error_log("failed to exec :" + t_sql)
            return False
        if len(t_select_result) == 0:
            return False
        if len(t_select_result) > 1:
            exec_log("find 2+record:" + t_sql)
        if assign_value:
            self.title = t_select_result[0][0]
            self.download_link = t_select_result[0][1]
            self.detail_url = t_select_result[0][2]
            douban_id = t_select_result[0][3]
            imdb_id = t_select_result[0][4]
            self.downloaded = t_select_result[0][5]
            self.torrent_id = t_select_result[0][6]
            self.add_datetime = t_select_result[0][7]
            self.total_size = t_select_result[0][8]
            if douban_id != "" or imdb_id != "":
                self.info = Info(douban_id, imdb_id)
        return True

    def insert(self):
        if self.HASH == "" or self.rss_name == "":
            return None

        in_sql = "insert into rss(rssname,HASH,title,downloadlink,detailurl,torrentid,doubanid,imdbid,datetime,downloaded,size) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
        in_val = (self.rss_name, self.HASH, self.title, self.download_link, self.detail_url, self.torrent_id,
                  self.douban_id, self.imdb_id, self.add_datetime, self.downloaded, self.total_size)
        return insert(in_sql, in_val)

    def update(self):
        if self.rss_name == "":
            exec_log("rss_name is null:" + self.name)
            return False
        if self._HASH != "":
            up_sql = "update rss set title=%s,downloadlink=%s,detailurl=%s,torrentid=%s,doubanid=%s,imdbid=%s,downloaded=%s,datetime=%s,size=%s where rssname=%s and HASH=%s"
            up_val = (self.title, self.download_link, self.detail_url, self.torrent_id, self.douban_id, self.imdb_id,
                      self.downloaded, self.add_datetime, self.total_size, self.rss_name, self.HASH)
        elif self.torrent_id != "":
            up_sql = "update rss set title=%s,downloadlink=%s,detailurl=%s,torrentid=%s,doubanid=%s,imdbid=%s,downloaded=%s,datetime=%s,size=%s where rssname=%s and torrentid=%s"
            up_val = (self.title, self.download_link, self.detail_url, self.torrent_id, self.douban_id, self.imdb_id,
                      self.downloaded, self.add_datetime, self.total_size, self.rss_name, self.torrent_id)
        else:
            error_log("HASH and torrent_id is null to update:" + self.title)
            return False
        return update(up_sql, up_val)

    def update_or_insert(self):
        if self.HASH == "" or self.rss_name == "":
            return None

        if self.select(assign_value=False):
            return self.update()
        else:
            return self.insert()

    def update_downloaded(self):
        if self.downloaded != 1:
            self.downloaded = 1
            exec_log("update rsstable:" + self.name)
            return self.update()
        return True

    def get_torrent_info(self):
        if self.download_link == "":
            return False

        torrent_info = RSS.download_torrent_file(self.download_link, self._HASH)
        if torrent_info is None:
            error_log("failed to get info:" + self.download_link)
            return False

        self._HASH = torrent_info.info_hash
        self._total_size = torrent_info.total_size
        self._torrent_name = torrent_info.name
        self._files = torrent_info.files
        debug_log(f"_HASH      :{self._HASH}")
        debug_log(f"_name      :{self._torrent_name}")
        debug_log(f"_total_size:{self._total_size}")
        return True

    def get_id_from_detail(self):
        """
        从pt详情页获取douban_id/imdb_id
        :return:
        """
        if self.id_from_detail == NOK:
            return NOK

        if self.douban_id != "" or self.imdb_id != "":
            return OK
        # TODO to delete
        if self.rss_name == "" or self.torrent_id == "":
            return NOK

        if self.retry_times >= 2:
            exec_log("2 times for get id from detail:" + self.name)
            self.id_from_detail = NOK
            return NOK

        if self.id_from_detail != RETRY:
            return self.id_from_detail

        return_dict = NexusPage.get_id_from_detail(self.rss_name, self.detail_url)
        if return_dict['return_code'] == NOK:
            exec_log("can't find id from detail:" + self.name)
            exec_log("                         :" + self.detail_url)
            self.error_string = return_dict['error_string']
            self.id_from_detail = NOK
            return NOK  # 不在这里设id_status为NOK，还有可能从nfo获取
        if return_dict['return_code'] == RETRY:
            self.retry_times += 1
            return RETRY
        debug_log("find id from detail:{}|{}|{}".format(return_dict['douban_id'], return_dict['imdb_id'], self.title))
        self.set_id(return_dict['douban_id'], return_dict['imdb_id'])
        self.id_from_detail = OK
        return OK

    def set_id(self, douban_id, imdb_id):
        if douban_id == "" and imdb_id == "":
            return False
        self.info = Info(douban_id, imdb_id)

        #
        self.info.spider_douban()

        # 写入id到数据库
        self.id_status = OK
        if not self.update():
            exec_log("failed to update rss:" + self.name)
            return False

        return True

    @staticmethod
    def get_torrent_id(download_link):
        if download_link is None or download_link == "":
            return ""
        t_index = download_link.find("id=")
        if t_index == -1:
            debug_log("failed to find torrentid starttag(id=):" + download_link)
            return ""
        t_torrent_id = download_link[t_index + 3:]
        t_index = t_torrent_id.find("&")
        if t_index == -1:
            debug_log("failed to find torrentid endtag(&):" + download_link)
            return ""
        return t_torrent_id[:t_index]

    @staticmethod
    def old_rss(HASH, rss_name):
        t_return = select('select title from rss where rssname=%s and hash=%s', (rss_name, HASH))
        return False if t_return is None or len(t_return) == 0 else True

    @staticmethod
    def old_free(torrent_id, rss_name):
        t_return = select('select title from rss where rssname=%s and torrentid=%s', (rss_name, torrent_id))
        return False if t_return is None or len(t_return) == 0 else True



    @staticmethod
    def download_torrent_file(download_link, HASH=""):
        """
        根据下载链接，下载种子文件，获取hash值，并按照hash.torrent名称保存到配置给定的目录
        返回值: torrent_info 失败返回None
        """

        torrent_file = os.path.join(os.path.abspath(g_config.TORRENTS_DIR), HASH + '.torrent')
        if HASH != "" and os.path.exists(torrent_file):
            debug_log(f"hash对应的种子已经存在:{torrent_file}")
            torrent_info = torrentool.api.Torrent.from_file(torrent_file)
            if torrent_info.info_hash is None:
                error_log(f"获取到的hash为空:{torrent_file}")
                return None
            return torrent_info

            # 下载种子文件
        temp_torrent_file = os.path.join(os.path.abspath(g_config.TORRENTS_DIR), 'temp.torrent')
        try:
            f = requests.get(download_link, timeout=120)
            with open(temp_torrent_file, "wb") as code:
                code.write(f.content)
        except Exception as err:
            log_print(err)
            debug_log("failed to download torrent file from:" + download_link)
            return None
        else:
            debug_log("success download torrent file from:" + download_link)

        # 获取torrent（包含hash等信息）
        try:
            torrent_info = torrentool.api.Torrent.from_file(temp_torrent_file)
        except Exception as err:
            print(err)
            exec_log(f"can't get torrent_info from {temp_torrent_file}")
            return None
        if torrent_info is None or torrent_info.info_hash is None:
            return None

        # 改名hash.torrent
        torrent_file = os.path.join(os.path.abspath(g_config.TORRENTS_DIR), torrent_info.info_hash + '.torrent')
        try:
            os.rename(temp_torrent_file, torrent_file)
        except Exception as err:
            print(err)
            error_log("error: rename {} to {}".format(temp_torrent_file, torrent_file))
            return ""
        return torrent_info
