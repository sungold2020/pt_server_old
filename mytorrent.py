#!/usr/bin/python3
# coding=utf-8

import mylib
from movie import *

from torrent import *

from ptsite import *
from client import PTClient

BOOKMARK = -2
MANUAL = -1
TO_BE_ADD = 0
TO_BE_START = 1
STARTED = 2
MOVED = 3

ERROR_NONE = 0
ERROR_FAILED_TO_ADD = 1
ERROR_FAILED_TO_START = 2
ERROR_CHECK_FILES = 3
ERROR_MORE_THAN_1_DAY = 4
ERROR_ID_NOT_FOUND = 5
ERROR_DOUBAN_DETAIL = 6


class MyTorrent:

    def __init__(self, torrent=None, rss=None, add_status=TO_BE_ADD):
        self.torrent = torrent if torrent is not None else Torrent("QB", None)
        self.rss = rss
        # self.info = info    if info != None else Info()
        self.add_status = add_status
        self.checked = 1  # 每次检查时用于标记它是否标记到，检查结束后，如果发现Checked为0，说明种子已经被删除。
        # 新建对象时肯定Checked=1
        self.is_check_nfo = False
        self.error_code = ERROR_NONE
        self.error_string = ""

    # ------------- begin rss------------------------------
    @property
    def site_name(self):
        if self.rss is None:
            return ""
        else:
            return self.rss.site_name

    @property
    def rss_name(self):
        if self.rss is None:
            return ""
        else:
            return self.rss.rss_name

    @rss_name.setter
    def rss_name(self, rss_name):
        if self.rss is None:
            Log.error_log("set rss_name,but rss is none")
        else:
            self.rss.rss_name = rss_name

    @property
    def HASH(self):
        if self.rss is None:
            return ""
        else:
            return self.rss.HASH

    @HASH.setter
    def HASH(self, HASH):
        if self.rss is None:
            Log.error_log("set HASH,but rss is none")
        else:
            self.rss.HASH = HASH

    @property
    def download_link(self):
        if self.rss is None:
            return ""
        else:
            return self.rss.download_link

    @download_link.setter
    def download_link(self, download_link):
        if self.rss is None:
            Log.error_log("set download_link,but rss is none")
        else:
            self.rss.download_link = download_link

    @property
    def detail_url(self):
        if self.rss is None:
            return ""
        else:
            return self.rss.detail_url

    @detail_url.setter
    def detail_url(self, detail_url):
        if self.rss is None:
            Log.error_log("set detail_url,but rss is none")
        else:
            self.rss.detail_url = detail_url

    @property
    def title(self):
        if self.rss is None:
            return ""
        else:
            return self.rss.title

    @title.setter
    def title(self, title):
        if self.rss is None:
            Log.error_log("set title,but rss is none")
        else:
            self.rss.title = title

    @property
    def torrent_id(self):
        if self.rss is None:
            return ""
        else:
            return self.rss.torrent_id

    @torrent_id.setter
    def torrent_id(self, torrent_id):
        if self.rss is None:
            Log.error_log("set torrent_id,but rss is none")
        else:
            self.rss.torrent_id = torrent_id

    @property
    def total_size(self):
        return self.torrent.total_size if self.torrent.torrent is not None else self.rss.total_size

    @total_size.setter
    def total_size(self, total_size):
        if self.rss is None:
            Log.error_log("set total_size,but rss is none")
        else:
            self.rss.total_size = total_size

    @property
    def downloaded(self):
        if self.rss is None:
            return 0
        else:
            return self.rss.downloaded

    @downloaded.setter
    def downloaded(self, downloaded):
        if self.rss is None:
            Log.error_log("set downloaded,but rss is none")
        else:
            self.rss.downloaded = downloaded

    @property
    def id_status(self):
        return self.rss.id_status

    @id_status.setter
    def id_status(self, id_status):
        if self.rss is None:
            Log.error_log("set id_status,but rss is none")
        else:
            self.rss.id_status = id_status

    def set_id(self, douban_id, imdb_id):
        return self.rss.set_id(douban_id, imdb_id) if self.rss is not None else False

        # ------------------begin info-------------------

    @property
    def douban_id(self):
        return self.rss.douban_id if self.rss is not None else ""

    @douban_id.setter
    def douban_id(self, douban_id):
        self.rss.douban_id = douban_id

    @property
    def douban_score(self):
        return self.rss.douban_score if self.rss is not None else ""

    @douban_score.setter
    def douban_score(self, douban_score):
        self.rss.douban_score = douban_score

    @property
    def imdb_id(self):
        return self.rss.imdb_id if self.rss is not None else ""

    @imdb_id.setter
    def imdb_id(self, imdb_id):
        self.rss.imdb_id = imdb_id

    @property
    def imdb_score(self):
        return self.rss.imdb_score if self.rss is not None else ""

    @imdb_score.setter
    def imdb_score(self, imdb_score):
        self.rss.imdb_score = imdb_score

    @property
    def douban_link(self):
        return self.rss.douban_link if self.rss is not None else ""

    @douban_link.setter
    def douban_link(self, douban_link):
        self.rss.douban_link = douban_link

    @property
    def imdb_link(self):
        return self.rss.imdb_link if self.rss is not None else ""

    @imdb_link.setter
    def imdb_link(self, imdb_link):
        self.rss.imdb_link = imdb_link

    @property
    def movie_name(self):
        return self.rss.movie_name if self.rss is not None else ""

    @movie_name.setter
    def movie_name(self, movie_name):
        self.rss.movie_name = movie_name

    @property
    def type(self):
        return self.rss.type if self.rss is not None else ""

    @type.setter
    def type(self, m_type):
        self.rss.type = m_type

    @property
    def nation(self):
        return self.rss.nation if self.rss is not None else ""

    @nation.setter
    def nation(self, nation):
        self.rss.nation = nation

    @property
    def douban_status(self):
        return self.rss.douban_status

    @douban_status.setter
    def douban_status(self, douban_status):
        self.rss.douban_status = douban_status

    @property
    def douban_retry_times(self):
        return self.rss.douban_retry_times if self.rss is not None else ""

    @douban_retry_times.setter
    def douban_retry_times(self, douban_retry_times):
        self.rss.douban_retry_times = douban_retry_times

    @property
    def foreign_name(self):
        return self.rss.foreign_name if self.rss is not None else ""

    @property
    def other_names(self):
        return self.rss.other_names if self.rss is not None else ""

    @property
    def director(self):
        return self.rss.director if self.rss is not None else ""

    @property
    def actors(self):
        return self.rss.actors if self.rss is not None else ""

    @property
    def episodes(self):
        return self.rss.episodes if self.rss is not None else ""

    @property
    def poster(self):
        return self.rss.poster if self.rss is not None else ""

    @property
    def genre(self):
        return self.rss.genre if self.rss is not None else ""
        # ------------------end info---------------

    # -------------------end rss------------------------

    # ------------------begin torrent-------------------
    @property
    def client(self):
        if self.torrent is None:
            return ""
        else:
            return self.torrent.client

    @property
    def hash(self):
        if self.torrent is None:
            return ""
        else:
            return self.torrent.hash

    @property
    def name(self):
        if self.torrent is None:
            return ""
        else:
            return self.torrent.name

    @property
    def progress(self):
        if self.torrent is None:
            return 0
        else:
            return self.torrent.progress

    @property
    def status(self):
        if self.torrent is None:
            return "UNKNOWN"
        else:
            return self.torrent.status

    @property
    def tracker_status(self):
        if self.torrent is None:
            return TRACKER_UNKNOWN
        else:
            return self.torrent.tracker_status

    @property
    def torrent_status(self):
        if self.torrent is None:
            return "UNKNOWN"
        else:
            return self.torrent.torrent_status

    @property
    def tracker_message(self):
        return self.torrent.tracker_message if self.torrent is not None else ""

    @property
    def category(self):
        if self.torrent is None:
            return ""
        else:
            return self.torrent.category

    @property
    def tags(self):
        if self.torrent is None:
            return ""
        else:
            return self.torrent.tags

    @property
    def save_path(self):
        if self.torrent is None:
            return ""
        else:
            return self.torrent.save_path

    @property
    def add_datetime(self):
        if self.torrent.torrent is not None:
            return self.torrent.add_datetime if self.torrent.add_datetime is not None else ""
        else:
            return self.rss.add_datetime if self.rss.add_datetime is not None else ""

    @add_datetime.setter
    def add_datetime(self, add_datetime):
        if self.rss is None:
            Log.error_log("set add_datetime,but rss is none")
        else:
            self.rss.add_datetime = add_datetime

    @property
    def tracker(self):
        if self.torrent is None:
            return ""
        else:
            return self.torrent.tracker

    @property
    def uploaded(self):
        if self.torrent is None:
            return ""
        else:
            return self.torrent.uploaded

    # @property
    # def total_size(self):   defined in rss part
    @property
    def files(self):
        if self.torrent is None:
            return []
        else:
            return self.torrent.files

    @property
    def date_data(self):
        if self.torrent is None:
            return []
        else:
            return self.torrent.date_data

    @date_data.setter
    def date_data(self, date_data):
        self.torrent.date_data = date_data

    # 重定义函数
    def start(self):
        if self.torrent is None:
            return False
        if self.torrent.resume():
            Log.debug_log(f"start torrent:{self.name}|{self.hash}")
            return True
        else:
            self.error_string = self.torrent.error_string
            Log.debug_log(f"failed to start torrent:{self.name}|{self.hash}")
            return False

    def stop(self):
        if self.torrent is None:
            return False
        if self.torrent.stop():
            Log.debug_log(f"stop torrent:{self.name}|{self.hash}")
            return True
        else:
            Log.debug_log(f"failed to start torrent:{self.name}|{self.hash}")
            self.error_string = self.torrent.error_string
            return False

    def pause(self):
        return self.stop()

    def resume(self):
        return self.start()

    def set_save_path(self, save_path):
        if self.torrent is None:
            return False
        else:
            return self.torrent.set_save_path(save_path)

    def set_category(self, category=""):
        if self.torrent is None:
            return False
        else:
            return self.torrent.set_category(category)

    def set_tags(self, tags=""):
        if self.torrent is None:
            return False
        else:
            return self.torrent.set_tags(tags)
    
    def set_upload_limit(self, upload_limit):
        if self.torrent is None:
            return False
        else:
            return self.torrent.set_upload_limit(upload_limit)

    def is_root_folder(self):
        if self.torrent is None:
            return False
        else:
            return self.torrent.is_root_folder()

    def check_files(self, is_new_day):
        if self.torrent is None:
            return False
        else:
            return self.torrent.check_files(is_new_day)

    def is_low_upload(self, number_of_days, upload_threshold):
        if self.torrent is None:
            return False
        else:
            return self.torrent.is_low_upload(number_of_days, upload_threshold)

    def get_last_day_upload_traffic(self):
        return self.torrent.get_last_day_upload_traffic() if self.torrent is not None else 0
    # ------------------end torrent-------------------

    def get_name(self):
        # 优先获取torrent_name，然后title
        return self.name if self.name != "" else self.title

    def get_title(self):
        # 优先获取title，然后torrent_name
        return self.title if self.title != "" else self.name

    def get_compiled_name(self):
        # 优先获取rss.name(电影名+torrent_name)，否则torrent_name
        return self.rss.name if (self.rss is not None and self.rss.name != "") else self.name

    def get_hash(self):
        # 有限获取hash，其次HASH，两者不为空的情况下比较一致性
        if self.hash != self.HASH and self.hash != "" and self.HASH != "":
            Log.error_log("error:diff hash and HASH:{}|{}".format(self.hash, self.HASH))
        return self.hash if self.hash != "" else self.HASH

    def set_tag(self):
        """
        设置标签，仅对QB有效
        """
        if self.client == "QB":
            t_tracker = self.tracker
            if t_tracker.find("keepfrds") >= 0:
                if self.tags != 'frds':
                    self.set_tags('frds')
            elif t_tracker.find("m-team") >= 0:
                if self.tags != 'mteam':
                    self.set_tags('mteam')
            elif t_tracker.find("hdsky") >= 0:
                if self.tags != 'hdsky':
                    self.set_tags('hdsky')
            elif t_tracker == "":
                pass
            else:
                if self.tags != 'other':
                    self.set_tags('other')

    def start_download(self):
        """
        开始下载种子，首先判断磁盘空间是否足够
        """
        if self.torrent is None:
            Log.error_log("torrent does not exist")
            return False

        if not self.rss.update_downloaded():
            Log.error_log("failed to update rss:" + self.name + ':' + self.HASH)

        t_free_size = mylib.get_free_size(SysConfig.DOWNLOAD_FOLDER)
        # DebugLog("free size:"+str(tFreeSize))
        t_size = self.torrent.total_size / (1024 * 1024 * 1024)
        # DebugLog("Size:"+str(tSize))
        if t_free_size < t_size + 1:
            self.error_code = ERROR_FAILED_TO_START
            self.error_string = "diskspace is not enough"
            Log.exec_log(f"error::{self.name}:{self.error_string}")
            return False
        if self.resume() and self.set_category("下载"):
            Log.debug_log("start download:" + self.name)
            if self.error_code == ERROR_FAILED_TO_START:
                self.error_code = ERROR_NONE
            return True
        else:
            self.error_code = ERROR_FAILED_TO_START
            self.error_string = "failed to resume or set_category"
            Log.exec_log(f"error::{self.name}:{self.error_string}")
            return False

    def get_id_from_nfo(self):
        """
        尝试从*.nfo文件获取imdbid/doubanid
        """
        if self.progress != 100:
            Log.error_log("begin to get id from nfo,but torrent have not done.")
            return False

        # 如果已经检查过nfo了，就不用再检查了
        if self.is_check_nfo:
            return False
        self.is_check_nfo = True

        # 检查下有没有nfo文件
        t_nfo_file_name = ""
        t_files = self.files
        for t_file in t_files:
            if t_file['name'][-4:].lower() == '.nfo':
                t_nfo_file_name = os.path.join(self.save_path, t_file['name'])
                Log.debug_log("find  nfo  file:" + self.name)
                break
        if t_nfo_file_name == "":
            Log.exec_log("n_find nfo file:" + self.name)
            return False

        # 检索nfo文件内容是否包含
        imdb_link = douban_link = ""
        for line in open(t_nfo_file_name, "rb"):
            line = line.decode("utf8", "ignore")
            if line[-1:] == '\n':
                line = line[:-1]
            line = line.strip()  # 去除前后的空字符，换行符等
            line = line.lower()
            t_index = line.find("https://www.imdb.com/title")
            if t_index >= 0:
                imdb_link = line[t_index:]
            t_index = line.find("http://www.imdb.com/title")
            if t_index >= 0:
                imdb_link = line[t_index:]
            t_index = line.find("http://movie.douban.com/subject")
            if t_index >= 0:
                douban_link = line[t_index:1]
            t_index = line.find("https://movie.douban.com/subject")
            if t_index >= 0:
                douban_link = line[t_index:1]
        douban_id = Info.get_id_from_link(douban_link, DOUBAN)
        imdb_id = Info.get_id_from_link(imdb_link, IMDB)
        Log.debug_log("DoubanLink:{} :: IMDBLink:{}".format(douban_link, imdb_link))
        Log.debug_log("find DoubanID:{} :: IMDBID:{}".format(douban_id, imdb_id))

        if douban_id == "" and imdb_id == "":
            Log.exec_log("can't find id from nfo:" + self.get_name())
            return False
        Log.exec_log("get id from nfo:{}|{}{}".format(self.get_name(), douban_id, imdb_id))
        if not self.rss.set_id(douban_id, imdb_id):
            Log.exec_log("failed to set_id:{}|{}|{}".format(self.title, douban_id, imdb_id))
        return True

    def check_movie_info(self):
        """
        检查是否已经获取豆瓣详情：
        1、首先检查是否具备ID（获取ID后，会创建Info对象，并检索info表的数据）
        2、根据id爬取豆瓣详情页
        """
        # 检查id
        if self.id_status == NOK:
            return NOK
        elif self.id_status == RETRY:
            is_id_ok = self.rss.get_id_from_detail()
            if is_id_ok == NOK:
                self.error_code = ERROR_ID_NOT_FOUND
                self.error_string = self.rss.error_string
                # 尝试读取nfo文件找id
                if self.progress == 100:
                    if not self.get_id_from_nfo():
                        self.id_status = NOK
                        self.error_code = ERROR_ID_NOT_FOUND
                        self.error_string = self.rss.error_string
                        return NOK
                else:
                    return RETRY
            elif is_id_ok == RETRY:
                return RETRY
        else:
            pass  # ID is OK
        if self.error_code == ERROR_ID_NOT_FOUND:
            self.error_code = ERROR_NONE  # 复位

        if self.rss.info is None:
            Log.error_log("id is ok,but info is null")
        if self.douban_status == OK:
            if self.error_code == ERROR_DOUBAN_DETAIL:
                self.error_code = ERROR_NONE
            return self.douban_status
        elif self.douban_status == NOK:
            return NOK
        else:  # self.douban_status == RETRY
            return_code = self.rss.spider_douban()
            if return_code == NOK:
                Log.exec_log("can't find record for {}|{}".format(self.douban_id, self.imdb_id))
                self.error_code = ERROR_DOUBAN_DETAIL
                self.error_string = self.rss.error_string
            return return_code

    def save_movie(self):
        """
        0、暂停种子
        1、检查影片爬取信息
        2、移入或者更名至tobe目录下的目录文件夹
        3、保存种子文件到该目录，插入记录download表等
        4 下载poster.jpg文件    
        5、检查该目录并加入表
        6、更新豆瓣刮削信息到表movies
        7、把种子分类设为空  
        """

        Log.debug_log("begin save torrent:" + self.name)
        if not self.stop():
            Log.error_log("failed to stop torrent:" + self.name)
            return False

        # 1、检查影片信息爬取
        if self.douban_status != OK:
            self.douban_status = RETRY
            if not self.check_movie_info():
                Log.exec_log("failed to spider movie info")
                return False
        Log.debug_log("{}|{}|{}|{}".format(self.movie_name, self.nation, self.douban_id, self.imdb_id))
        if self.movie_name == "" or self.nation == "" or (self.douban_id == "" and self.imdb_id == ""):
            Log.exec_log(f"empty name or nation or id:{self.name}")
            return False

        # 2、移入或者更名至tobe目录下的目录文件夹
        # 2.1 组装目标文件夹名需要先获取Number和Copy
        copy = 0
        if self.douban_id != "":
            sel_sql = 'select number,copy from movies where doubanid = %s'
            sel_val = (self.douban_id,)
        else:
            sel_sql = 'select number,copy from movies where imdbid = %s'
            sel_val = (self.imdb_id,)
        select_result = select(sel_sql, sel_val)
        if select_result is None:
            Log.error_log("error:select from movies")
            return False
        elif len(select_result) == 0:  # 说明不存在，需要获取max(number)+1
            sel_sql = 'select max(number) from movies'
            select_result = select(sel_sql, None)
            number = select_result[0][0] + 1
        elif len(select_result) == 1:
            number = select_result[0][0]
            copy = select_result[0][1]
        else:
            # 多条记录，有可能是正常的，也可能是异常的。先取第一条记录的Number,记录下日志，待手工检查
            Log.exec_log("2+ record in movies where imdbid = " + self.imdb_id)
            number = select_result[0][0]
            for i in range(len(select_result)):
                if select_result[i][0] != number:
                    Log.error_log("diff number in case of same imdbid:" + self.imdb_id)
                    break

        # 2.2 组装新的目标文件夹名
        t_torrent_name = re.sub(u"[\u4e00-\u9f50]+", "", self.name)  # 去掉name中的中文字符
        t_torrent_name = re.sub("[,。，·]+", "", t_torrent_name)  # 去掉特殊标点符号
        t_torrent_name = t_torrent_name.strip()  # 去掉前后空格
        if t_torrent_name[:1] == '.':
            t_torrent_name = t_torrent_name[1:]  # 去掉第一个.
        t_torrent_name = re.sub(" ", ".", t_torrent_name)  # 空格替换为.
        # 部分种子只有一个视频文件，name会以.mkv类似格式结尾
        if t_torrent_name[-4:] == '.mp4' or t_torrent_name[-4:] == '.mkv' \
                or t_torrent_name[-4:] == 'avi' or t_torrent_name[-4:] == 'wmv':
            t_torrent_name = t_torrent_name[:-4]
        if copy > 0:
            dir_name = str(number).zfill(4) + '-' + str(copy) + '-' + self.nation
        else:
            dir_name = str(number).zfill(4) + '-' + self.nation
        if self.type == 0:
            dir_name += '-' + self.movie_name + ' ' + t_torrent_name
        elif self.type == 1:
            dir_name += '-' + '电视剧' + '-' + self.movie_name + ' ' + t_torrent_name
        elif self.type == 2:
            dir_name += '-' + '纪录片' + '-' + self.movie_name + ' ' + t_torrent_name
        else:
            Log.error_log("error type:" + self.type)

        # 2.3 移动或者更名至目标文件夹
        t_save_dir_name = os.path.join(self.save_path, self.name)
        t_to_be_dir_name = os.path.join(SysConfig.TO_BE_PATH, self.name)
        dest_dir_name = os.path.join(SysConfig.TO_BE_PATH, dir_name)
        if os.path.exists(dest_dir_name):
            Log.exec_log("dest dir exists:" + dest_dir_name)
        else:
            Log.debug_log("dest dir does not exists:" + dest_dir_name)
            if os.path.exists(t_to_be_dir_name):
                src_dir_name = t_to_be_dir_name  # 从tobe目录中去改名
            else:
                src_dir_name = t_save_dir_name  # 去原始保存目录移动到目标目录
            try:
                # 原种子没有目录只是一个文件，那就新建目标目录，move函数就会把这个文件移动到目标目录
                if os.path.isfile(src_dir_name):
                    os.mkdir(dest_dir_name)
                shutil.move(src_dir_name, dest_dir_name)
            except Exception as err:
                Log.error_log("failed to mv dir:" + dest_dir_name)
                Log.log_print(err)
                return False
            else:
                Log.exec_log("success mv dir to tobe:" + dest_dir_name)

        # 3、保存torrent和resume文件至该目录
        if not self.save_torrent_file(dest_dir_name):
            Log.exec_log("failed to save torrent file:" + dest_dir_name)
            return False

        # 4 下载poster.jpg文件
        if self.rss.download_poster(dest_dir_name):
            Log.exec_log("success download poster file")
        else:
            Log.error_log("failed to download poster.jpg from:" + self.poster)

        # 5 检查该目录并加入表
        t_movie = Movie(SysConfig.TO_BE_PATH, dir_name, "tobe")
        if t_movie.douban_id == "":
            t_movie.douban_id = self.douban_id
        if t_movie.imdb_id == "":
            t_movie.imdb_id = self.imdb_id
        # t_movie.douban_id = self.douban_id if t_movie.douban_id == "" else t_movie.douban_id
        t_movie.total_size = int(self.total_size / (1024 * 1024))
        if t_movie.save_movie() != 1:
            Log.error_log("failed to check:" + dir_name)
            return False
        else:
            Log.exec_log("success insert table movies")

        # 6 更新信息至表movies
        up_sql = "update movies set DoubanID=%s,IMDBID=%s,DownloadLink=%s,HASH=%s where number=%s and copy=%s"
        up_val = (self.douban_id, self.imdb_id, self.download_link, self.hash, number, copy)
        if update(up_sql, up_val):
            Log.exec_log("success update table:" + dir_name)
        else:
            Log.error_log("update error:" + dir_name + ":" + up_sql)
            return False

        # 7 插入download表
        if not self.insert_download(number, copy, t_movie.dir_name):
            Log.error_log("failed to insert table download:" + dest_dir_name)
            return False

        # 8 把种子分类设为空
        self.set_category("")
        return True

    def move_to_tr(self):
        """
        注：重新代码后未使用，未测试
        根据是否创建子文件夹(is_root_folder)分两种情况：
        一、创建了子文件夹：例如
            save_path = '2020-xx-xx xxx"
            files     =  xxxx.mkv
                         xxxx.nfo
            这个时候,在keep目录下创建链接到save_path,tr的save_path指向keep目录
        二、未创建子文件夹
            save_path = /BT/book"
            files     = kindle伴侣/xxx.txt
                        kindle伴侣/xxx.txt
            不创建链接，tr的save_path指向同一save_path即可
        """

        if not self.pause():
            Log.error_log("failed to stop torrent:" + self.name)
            return False

        t_torrent_file = os.path.join(SysConfig.QB_BACKUP_DIR, self.hash + ".torrent")
        if self.is_root_folder():
            t_dest_saved_path = self.save_path
        else:  # 为TR的保存路径创建链接
            if self.name[-4:] == '.mkv':
                t_link = os.path.join(SysConfig.TR_KEEP_DIR, self.name[:-4])  # 移除name中的.mkv后缀
            else:
                t_link = os.path.join(SysConfig.TR_KEEP_DIR, self.name)
            try:
                if not os.path.exists(t_link):
                    os.symlink(os.path.realpath(self.save_path), t_link)
            except Exception as err:
                print(err)
                Log.error_log("failed create link:ln -s " + os.path.realpath(self.save_path) + " " + t_link)
                return False
            t_dest_saved_path = SysConfig.TR_KEEP_DIR

        t_tr_client = PTClient("TR")
        if t_tr_client.connect() and t_tr_client.add_torrent(torrent_file=t_torrent_file,
                                                             download_dir=t_dest_saved_path,
                                                             is_paused=True):
            Log.error_log("failed to add torrent:" + t_torrent_file)
            return False
        else:
            Log.exec_log("move torrent to tr:" + self.name + '::' + self.hash)
            time.sleep(5)

        if not self.set_category(""):
            Log.error_log("failed to set category:" + self.name)
            return False
        return True

    def save_torrent_file(self, dest_dir, file_flag=0):
        """
        把torrent文件保存到指定目录,
        file_flag = 0: 文件格式为torrent_name+hash[:16].torrent
        file_flag = 1: 文件格式为hash.torrent
        """
        if self.client == 'QB':
            t_torrent_file = os.path.join(SysConfig.QB_BACKUP_DIR, self.hash + ".torrent")
            t_resume_file = os.path.join(SysConfig.QB_BACKUP_DIR, self.hash + ".fastresume")
        else:
            t_torrent_file = os.path.join(os.path.join(SysConfig.TR_BACKUP_DIR, 'torrents/'),
                                          self.name + '.' + self.hash[:16] + '.torrent')
            t_resume_file = os.path.join(os.path.join(SysConfig.TR_BACKUP_DIR, 'resume/'),
                                         self.name + '.' + self.hash[:16] + '.resume')
        if file_flag == 0:
            t_dest_torrent_file = os.path.join(dest_dir, self.name + '.' + self.hash[:16] + ".torrent")
            t_dest_resume_file = os.path.join(dest_dir, self.name + '.' + self.hash[:16] + ".resume")
        elif file_flag == 1:
            t_dest_torrent_file = os.path.join(dest_dir, self.hash + ".torrent")
            t_dest_resume_file = os.path.join(dest_dir, self.hash + ".resume")
        else:
            Log.error_log("invalid file_flag in save_torrent_file")
            return False

        try:
            shutil.copyfile(t_torrent_file, t_dest_torrent_file)
            shutil.copyfile(t_resume_file, t_dest_resume_file)
        except Exception as err:
            print(err)
            Log.error_log("failed to copy torrent and resume file:" + self.hash)
            return False

        # 创建download.txt，写入hash和download_link
        full_file_name = os.path.join(dest_dir, "download.txt")
        if os.path.isfile(full_file_name):
            try:
                os.remove(full_file_name)
            except Exception as err:
                print(err)
                print("failed to remove :" + full_file_name)
                return False
        fo = open(full_file_name, "a+")
        fo.write(self.hash + "|" + self.download_link)
        fo.close()
        return True

    def insert_download(self, number, copy, dir_name):
        """
        将download_link插入或者更新download表
        """
        t_select_result = select("select downloadlink,number,copy from download where hash=%s", (self.hash,))
        if t_select_result is None:
            Log.error_log("failed to exec select download")
            return False

        if len(t_select_result) > 0:
            Log.debug_log("download exists:" + self.hash)
            up_sql = "update download set downloadlink=%s,number=%s,copy=%s,dirname=%s where hash=%s"
            up_val = (self.download_link, number, copy, dir_name, self.hash)
            if update(up_sql, up_val):
                Log.debug_log("update download success")
                return True
            else:
                Log.error_log("error:" + up_sql + "::" + self.hash)
                return False
        else:
            in_sql = "insert into download(downloadlink,number,copy,dirname,hash) values(%s,%s,%s,%s,%s)"
            in_val = (self.download_link, number, copy, dir_name, self.hash)
            if insert(in_sql, in_val):
                Log.debug_log("insert download success")
                return True
            else:
                Log.error_log("error:" + in_sql + "::" + self.hash)
                return False

    def to_dict(self):
        temp_dict = {
                'client': self.client,
                'hash': self.get_hash(),
                'add_status': self.add_status,
                'name': self.get_compiled_name(),
                'rss_name': self.rss_name,
                'download_link': self.download_link,
                'detail_url': self.detail_url,
                'progress': self.progress,
                'torrent_status': self.torrent_status,
                'tracker_status': self.tracker_status,
                'tracker_message': self.tracker_message,
                'category': self.category,
                'tags': self.tags,
                'total_size': self.total_size,
                'add_datetime': self.add_datetime,
                'douban_id': self.douban_id,
                'imdb_id': self.imdb_id,
                'douban_score': self.douban_score if self.douban_score != "" else '-',
                'imdb_score': self.imdb_score if self.imdb_score != "" else '-',
                'movie_name': self.movie_name,
                'nation': self.nation,
                'poster': self.poster,
                'error_code': self.error_code,
                'error_string': self.error_string
            }
        return temp_dict

    def save_bookmark(self):
        # save to table bookmark 
        sql = "insert into bookmarks\
            (hash,name,rssname,title,downloadlink,detailurl,size,adddatetime,doubanid,imdbid,torrentid)\
             values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"

        val = (
                self.get_hash(),
                self.name,
                self.rss_name,
                self.title,
                self.download_link,
                self.detail_url,
                self.total_size,
                self.add_datetime,
                self.douban_id,
                self.imdb_id,
                self.torrent_id)
        if insert(sql, val):
            return "Success"
        else:
            return "failed to insert table"
