#!/usr/bin/python3
# coding=utf-8
from sites import *
import torrentool.api


class RSS:
    def __init__(self,
                 torrent_hash: str,
                 site_name: str,
                 rss_name: str,
                 download_url: str,
                 detail_url: str,
                 title: str,
                 douban_id: str,
                 imdb_id: str,
                 add_datetime: str,
                 total_size: int,
                 id_status: int = RETRY,
                 douban_status: int = RETRY):
        self._HASH = torrent_hash   # TODO rename _HASH to torrent_hash
        self.site_name = site_name
        self.rss_name = rss_name
        self._download_url = download_url  # TODO rename _download_link to download_url
        self._detail_url = detail_url
        self.title = title
        self._add_datetime = add_datetime if add_datetime != "" else datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self._total_size = total_size

        # (verify id_status)
        self._id_status = id_status
        self.id_from_detail = self._id_status
        self.retry_times = 0
        if (douban_id == "" and imdb_id == "") and self._id_status == OK:
            self.id_status = RETRY
            Log.error_log("id is empty,but id_status is ok:" + self.title)
        if (douban_id != "" or imdb_id != "") and self._id_status != OK:
            self._id_status = OK
            Log.error_log("id is not empty,but id_status is not ok:" + self.title)
        self.info = Info(douban_id, imdb_id, douban_status) if douban_id != "" or imdb_id != "" else None

        self._torrent_name = ""
        self._files = []
        self.error_string = ""
        self.downloaded = 0
        self.torrent_id = self.get_torrent_id(download_url)

    @staticmethod
    def from_rss_torrent(rss_torrent: dict):
        torrent_hash = rss_torrent['hash']
        site_name = rss_torrent['site_name']
        rss_name = rss_torrent['rss_name']
        download_url = rss_torrent['download_url']
        detail_url = rss_torrent['detail_url']
        title = rss_torrent['title']
        douban_id = rss_torrent['douban_id']
        imdb_id = rss_torrent['imdb_id']
        add_datetime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        torrent_hash, name, total_size = RSS.torrent_info(torrent_hash, download_url)
        id_status = OK if douban_id != "" or imdb_id != "" else RETRY
        rss = RSS(torrent_hash, site_name, rss_name, download_url, detail_url, title, douban_id,
                  imdb_id, add_datetime, total_size, id_status)
        return rss

    @staticmethod
    def from_page_torrent(page_torrent: dict):
        site_name = page_torrent['site_name']
        title = page_torrent['title']
        detail_url = page_torrent['detail_url']
        download_url = page_torrent['download_url']
        douban_id = page_torrent['douban_id']
        imdb_id = page_torrent['imdb_id']
        douban_score = page_torrent['douban_score']
        imdb_score = page_torrent['imdb_score']
        add_datetime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        torrent_hash, name, total_size = RSS.torrent_info("", download_url)
        if torrent_hash == "" or total_size == 0:
            Log.exec_log(f"{title}:failed to get torrent_info from:{download_url}")
            return None
        id_status = OK if douban_id != "" or imdb_id != "" else RETRY
        rss = RSS(torrent_hash, site_name, site_name, download_url, detail_url, title, douban_id,
                  imdb_id, add_datetime, total_size, id_status)
        rss._torrent_name = name
        if douban_score != "" and rss.info is not None and rss.info.douban_score == "":
            rss.info.douban_score = douban_score
        if imdb_score != "" and rss.info is not None and rss.info.imdb_score == "":
            rss.info.imdb_score = imdb_score
        return rss

    @staticmethod
    def from_pt_backup(
            torrent_hash: str,
            site_name: str,
            rss_name: str,
            download_url: str,
            detail_url: str,
            title: str,
            douban_id: str,
            imdb_id: str,
            add_datetime: str,
            total_size: int,
            id_status: int,
            douban_status: int,
            douban_score: str,
            imdb_score: str):

        rss = RSS(torrent_hash,
                  site_name,
                  rss_name,
                  download_url,
                  detail_url,
                  title,
                  douban_id,
                  imdb_id,
                  add_datetime,
                  total_size,
                  id_status,
                  douban_status)
        if rss.douban_score == "":
            rss.douban_score = douban_score
        if rss.imdb_score == "":
            rss.imdb_score = imdb_score
        return rss

    @staticmethod
    def from_find_new_torrent(
            torrent_hash: str = "",
            name: str = "",
            total_size: int = 0,
            add_datetime: str = ""
            ):
        if torrent_hash == "":
            Log.exec_log(f"from_find_new_torrent:{torrent_hash}|{name}|{total_size}")
            return None
        # try to get rss by select from hash
        rss = RSS.select_from_rss_by_hash(torrent_hash)
        if rss is not None:
            rss.add_datetime = add_datetime
            rss.total_size = total_size
            rss.update()
            return rss
        else:
            rss = RSS(torrent_hash, "", "", "", "", name, "", "", add_datetime, total_size)
            return rss

    @staticmethod
    def select_from_rss_by_hash(torrent_hash):
        if torrent_hash == "":
            return False
        sel_sql = "select sitename,rssname,title,downloadlink,detailurl,doubanid,imdbid,adddatetime,size " \
                  "from rss where HASH=%s"
        sel_val = (torrent_hash,)
        t_select_result = select(sel_sql, sel_val)

        if t_select_result is None:
            Log.error_log(f"failed to exec :select_from_rss_by_hash({torrent_hash})")
            return None
        if len(t_select_result) == 0:
            return None
        if len(t_select_result) > 1:
            Log.exec_log(f"find 2+record:select_from_rss_by_hash({torrent_hash}), get the first record")

        site_name = t_select_result[0][0]
        rss_name = t_select_result[0][1]
        title = t_select_result[0][2]
        download_url = t_select_result[0][3]
        detail_url = t_select_result[0][4]
        douban_id = t_select_result[0][5]
        imdb_id = t_select_result[0][6]
        add_datetime = t_select_result[0][7]
        total_size = t_select_result[0][8]
        id_status = OK if douban_id != "" or imdb_id != "" else RETRY
        rss = RSS(torrent_hash, site_name, rss_name, download_url, detail_url, title, douban_id, 
                  imdb_id, add_datetime, total_size, id_status)
        return rss

    @staticmethod
    def select_from_bookmarks_by_hash(torrent_hash):
        if torrent_hash == "":
            return False
        sel_sql = "select sitename,rssname,title,downloadlink,detailurl,doubanid,imdbid,adddatetime,size " \
                  "from bookmarks where HASH=%s"
        sel_val = (torrent_hash,)
        t_select_result = select(sel_sql, sel_val)

        if t_select_result is None:
            Log.error_log(f"failed to exec :select_from_boomakrs_by_hash({torrent_hash})")
            return None
        if len(t_select_result) == 0:
            return None
        if len(t_select_result) > 1:
            Log.exec_log(f"find 2+record:select_from_bookmarks_by_hash({torrent_hash}), get the first record")

        site_name = t_select_result[0][0]
        rss_name = t_select_result[0][1]
        title = t_select_result[0][2]
        download_url = t_select_result[0][3]
        detail_url = t_select_result[0][4]
        douban_id = t_select_result[0][5]
        imdb_id = t_select_result[0][6]
        add_datetime = t_select_result[0][7]
        total_size = t_select_result[0][8]
        id_status = OK if douban_id != "" or imdb_id != "" else RETRY
        rss = RSS(torrent_hash, site_name, rss_name, download_url, detail_url, title, douban_id, 
                  imdb_id, add_datetime, total_size, id_status)
        return rss

    @staticmethod
    def delete_from_bookmarks_by_hash(torrent_hash) -> bool:
        return delete("delete from bookmarks where hash=%s", (torrent_hash, ))

    @staticmethod
    def torrent_info(torrent_hash="", download_url=""):
        """
        根据hash或者download_url获取torrent文件，解析后返回hash,name,total_size信息
        :param download_url:
        :param torrent_hash:
        :return:
            HASH:
            name:
            total_size:
        """
        name = ""
        total_size = 0
        torrent_info = RSS.download_torrent_file(download_url, torrent_hash)
        if torrent_info is None:
            Log.error_log("failed to get info:" + download_url)
            return torrent_hash, name, total_size
        # 如果输入torrent_hash非空，则比对一下torrent_info.info_hash
        if torrent_hash != "" and torrent_hash != torrent_info.info_hash:
            Log.error_log(f"error: different hash in get_torrent_info:{torrent_hash}|torrent_info.info_hash")
            # return torrent_hash, name, total_size
        torrent_hash = torrent_info.info_hash
        name = torrent_info.name
        total_size = torrent_info.total_size
        Log.debug_log(f"get_torrent_info:{torrent_hash}|{name}{total_size}")
        return torrent_hash, name, total_size

    @property
    def download_link(self):
        # pthome的downloadlink是临时链接，转换为带passkey的下载链接
        if self.site_name.lower().startswith("pthome"):
            site = Sites.get_site(self.site_name)
            return site.get_download_url(self.torrent_id)
        return self._download_url

    @download_link.setter
    def download_link(self, download_link):
        self._download_url = download_link

    @property
    def detail_url(self):
        """
        两种情况：
        1、detail_url为空，根据torrent_id去组装detail_url;
        2、detail_url缺网站名(例如:details?id=xxx),则需要补充完整detail_url
        """
        # TODO 03-27 detail_url will be build in _init_, so this method will not be needed
        site = Sites.get_site(self.site_name)
        if site is None:
            Log.exec_log(f"no site for:{self.title}|{self.site_name}:{self.rss_name}")
            return self._detail_url

        if self._detail_url == "":
            self._detail_url = site.get_detail_url(self.torrent_id)
        if not self._detail_url.startswith("http"):
            self._detail_url = site.complete_detail_url(self._detail_url)
        return self._detail_url

    @detail_url.setter
    def detail_url(self, detail_url):
        self._detail_url = detail_url

    @property
    def HASH(self):
        if self._HASH == "":
            Log.error_log("error:_HASH is null:" + self.name)
        return self._HASH

    @HASH.setter
    def HASH(self, HASH):
        if HASH == "":
            Log.error_log("error:HASH is null:" + self.name)
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
        if self._torrent_name == "":
            self.get_torrent_info()
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
        Log.error_log(f"rss.files will be abandoned soon")
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
        Log.debug_log(f"set id_status:{id_status}|{self.title}")
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
            Log.error_log("spider douban,info is null:" + self.name)
            return False
        return_code = self.info.spider_douban()
        if return_code == NOK:
            self.error_string = self.info.error_string
        return return_code

    def print(self):
        print(f"HASH:{self.HASH}")
        print(f"site_name:{self.site_name}")
        print(f"rss_name:{self.rss_name}")
        print(f"title:{self.title}")
        print(f"name:{self.name}")
        print(f"download_url:{self.download_link}")
        print(f"total_size:{self.total_size}")
        print(f"add_datetime:{self.add_datetime}")
        print(f"douban_id:{self.douban_id}")
        print(f"imdb_id:{self.imdb_id}")
        print(f"id_status:{self.id_status}")
        print(f"error_string:{self.error_string}")

    def select(self, assign_value=True):
        if self.rss_name == "":
            return False
        if self._HASH != "":  # 通过免费种子加入时，有torrent_id，无HASH
            sel_sql = "select title,downloadlink,detailurl,doubanid,imdbid,downloaded,torrentid,datetime,size,rssname " \
                      "from rss where sitename=%s and HASH=%s"
            sel_val = (self.site_name, self.HASH)
            t_select_result = select(sel_sql, sel_val)
            t_sql = "select title,downloadlink,detailurl,torrentid,downloaded,datetime,size " \
                    "from rss where sitename={} and HASH={}".format(self.site_name, self.HASH)
            if t_select_result is None:
                Log.error_log("failed to exec :" + t_sql)
                return False
            if len(t_select_result) == 0:
                return False
            elif len(t_select_result) > 1:
                Log.error_log("find 2+record:" + t_sql)
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
                self.rss_name = t_select_result[0][9]
                if douban_id != "" or imdb_id != "":
                    self.info = Info(douban_id, imdb_id)
            return True
        elif self.torrent_id != "":
            sel_sql = "select title,downloadlink,detailurl,doubanid,imdbid,HASH,downloaded,datetime,size,rssname " \
                      "from rss where sitename=%s and torrentid=%s"
            sel_val = (self.site_name, self.torrent_id)
            t_select_result = select(sel_sql, sel_val)
            t_sql = "select title,download_link,detailurl,HASH,downloaded,datetime,size from rss " \
                    "where sitename={} and torrentid={}".format(self.site_name, self.torrent_id)
            if t_select_result is None:
                Log.error_log("failed to exec :" + t_sql)
                return False
            if len(t_select_result) == 0:
                return False
            elif len(t_select_result) > 1:
                Log.error_log("find 2+record:" + t_sql)
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
                self.rss_name = t_select_result[0][9]
                if douban_id != "" or imdb_id != "":
                    self.info = Info(douban_id, imdb_id)
            return True
        else:
            return False

    def select_by_hash(self, assign_value=True):
        if self._HASH == "":
            return False
        sel_sql = "select rssname,title,downloadlink,detailurl,doubanid,imdbid,downloaded,torrentid,datetime,size,sitename " \
                  "from rss where HASH=%s"
        sel_val = (self.HASH,)
        t_select_result = select(sel_sql, sel_val)
        t_sql = "select rssname,title,downloadlink,detailurl,torrentid,downloaded,datetime,size from rss " \
                "where HASH={}".format(self.HASH)
        if t_select_result is None:
            Log.error_log("failed to exec :" + t_sql)
            return False
        if len(t_select_result) == 0:
            return False
        if len(t_select_result) > 1:
            Log.exec_log("find 2+record:" + t_sql)
        if assign_value:
            self.rss_name = t_select_result[0][0]
            self.title = t_select_result[0][1]
            self.download_link = t_select_result[0][2]
            self.detail_url = t_select_result[0][3]
            douban_id = t_select_result[0][4]
            imdb_id = t_select_result[0][5]
            self.downloaded = t_select_result[0][6]
            self.torrent_id = t_select_result[0][7]
            self.add_datetime = t_select_result[0][8]
            self.total_size = t_select_result[0][9]
            self.site_name = t_select_result[0][10]
            if (douban_id != "" or imdb_id != "") and self.info is None:
                self.info = Info(douban_id, imdb_id)
        return True

    def insert(self):
        if self.HASH == "" or self.rss_name == "":
            return None

        in_sql = "insert into rss" \
                 "(sitename,rssname,HASH,title,downloadlink,detailurl,torrentid,doubanid,imdbid,datetime,downloaded,size) " \
                 "values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
        in_val = (self.site_name, self.rss_name, self.HASH, self.title, self.download_link, self.detail_url, self.torrent_id,
                  self.douban_id, self.imdb_id, self.add_datetime, self.downloaded, self.total_size)
        Log.rss_log(f"insert:{self.title}")
        return insert(in_sql, in_val)

    def update(self):
        if self.rss_name == "":
            Log.exec_log("rss_name is null:" + self.name)
            return False
        if self._HASH != "":
            up_sql = "update rss set " \
                     "sitename=%s,rssname=%s,title=%s,downloadlink=%s,detailurl=%s,torrentid=%s,doubanid=%s,imdbid=%s," \
                     "downloaded=%s,datetime=%s,size=%s where rssname=%s and HASH=%s"
            up_val = (self.site_name, self.rss_name, self.title, self.download_link, self.detail_url, self.torrent_id,
                      self.douban_id, self.imdb_id, self.downloaded, self.add_datetime, self.total_size,
                      self.rss_name, self.HASH)
        elif self.torrent_id != "":
            up_sql = "update rss set " \
                     "sitename=%s,rssname=%s,title=%s,downloadlink=%s,detailurl=%s,torrentid=%s,doubanid=%s,imdbid=%s," \
                     "downloaded=%s,datetime=%s,size=%s where sitename=%s and torrentid=%s"
            up_val = (self.site_name, self.rss_name, self.title, self.download_link, self.detail_url, self.torrent_id,
                      self.douban_id, self.imdb_id, self.downloaded, self.add_datetime, self.total_size,
                      self.site_name, self.torrent_id)
        else:
            Log.error_log("HASH and torrent_id is null to update:" + self.title)
            return False
        Log.rss_log(f"update:{self.title}")
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
            Log.exec_log("update rsstable:" + self.name)
            return self.update()
        return True

    # todo abandoned soon
    def get_torrent_info(self):
        if self.download_link == "":
            return False

        torrent_info = RSS.download_torrent_file(self.download_link, self._HASH)
        if torrent_info is None:
            Log.error_log("failed to get info:" + self.download_link)
            return False

        self._HASH = torrent_info.info_hash
        self._total_size = torrent_info.total_size
        self._torrent_name = torrent_info.name
        self._files = torrent_info.files
        Log.debug_log(f"_HASH      :{self._HASH}")
        Log.debug_log(f"_name      :{self._torrent_name}")
        Log.debug_log(f"_total_size:{self._total_size}")
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
            Log.exec_log("2 times for get id from detail:" + self.name)
            self.id_from_detail = NOK
            return NOK

        if self.id_from_detail != RETRY:
            return self.id_from_detail

        self.print()
        site = Sites.get_site(self.site_name)
        is_success, douban_id, imdb_id = site.get_id_from_detail_url(self.detail_url)
        self.id_from_detail = OK if is_success else NOK
        if is_success:
            Log.debug_log("find id from detail:{}|{}|{}".format(douban_id, imdb_id, self.title))
            self.set_id(douban_id, imdb_id)
            return OK
        return NOK

    def set_id(self, douban_id, imdb_id):
        if douban_id == "" and imdb_id == "":
            return False
        self.info = Info(douban_id, imdb_id)

        #
        self.info.spider_douban()

        # 写入id到数据库
        self.id_status = OK
        if not self.update():
            Log.exec_log("failed to update rss:" + self.name)
            return False

        return True

    @staticmethod
    def get_torrent_id(download_link):
        if download_link is None or download_link == "":
            return ""
        t_index = download_link.find("id=")
        if t_index == -1:
            Log.debug_log("failed to find torrentid starttag(id=):" + download_link)
            return ""
        t_torrent_id = download_link[t_index + 3:]
        t_index = t_torrent_id.find("&")
        if t_index == -1:
            Log.debug_log("failed to find torrentid endtag(&):" + download_link)
            return ""
        return t_torrent_id[:t_index]

    @staticmethod
    def is_old_rss_torrent(torrent_hash: str, rss_name: str) -> bool:
        t_return = select('select title from rss where rssname=%s and hash=%s', (rss_name, torrent_hash))
        return False if t_return is None or len(t_return) == 0 else True

    @staticmethod
    def is_old_page_torrent(torrent_id: str, site_name: str):
        t_return = select('select title from rss where sitename=%s and torrentid=%s', (site_name, torrent_id))
        return False if t_return is None or len(t_return) == 0 else True

    @staticmethod
    def download_torrent_file(download_link, HASH=""):
        """
        根据下载链接，下载种子文件，获取hash值，并按照hash.torrent名称保存到配置给定的目录
        返回值: torrent_info 失败返回None
        """

        torrent_file = os.path.join(os.path.abspath(SysConfig.TORRENTS_DIR), HASH + '.torrent')
        if HASH != "" and os.path.exists(torrent_file):
            Log.debug_log(f"hash对应的种子已经存在:{torrent_file}")
            torrent_info = torrentool.api.Torrent.from_file(torrent_file)
            if torrent_info.info_hash is None:
                Log.error_log(f"获取到的hash为空:{torrent_file}")
                return None
            return torrent_info

            # 下载种子文件
        temp_torrent_file = os.path.join(os.path.abspath(SysConfig.TORRENTS_DIR), 'temp.torrent')
        try:
            f = requests.get(download_link, timeout=120)
            with open(temp_torrent_file, "wb") as code:
                code.write(f.content)
        except Exception as err:
            Log.log_print(err)
            Log.debug_log("failed to download torrent file from:" + download_link)
            return None
        else:
            Log.debug_log("success download torrent file from:" + download_link)

        # 获取torrent（包含hash等信息）
        try:
            torrent_info = torrentool.api.Torrent.from_file(temp_torrent_file)
        except Exception as err:
            print(err)
            Log.exec_log(f"can't get torrent_info from {temp_torrent_file}")
            return None
        if torrent_info is None or torrent_info.info_hash is None:
            return None

        # 改名hash.torrent
        torrent_file = os.path.join(os.path.abspath(SysConfig.TORRENTS_DIR), torrent_info.info_hash + '.torrent')
        try:
            os.rename(temp_torrent_file, torrent_file)
        except Exception as err:
            print(err)
            Log.error_log("error: rename {} to {}".format(temp_torrent_file, torrent_file))
            # return None
        return torrent_info
