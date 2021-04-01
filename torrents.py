#!/usr/bin/python3
# coding=utf-8

from mylib import *
from rss import *
from mytorrent import *
from client import PTClient
import threading 
from sites import *


class Torrents:
    keep_no_limit_trackers = ['hdsky']  # 保留不上传限制的trackers

    def __init__(self):
        self.upload_limit_state = False   # 当前是上传限制状态

        self.torrent_list = []
        self.lock = threading.RLock()
        self.tracker_data_list = [
                {'name': 'FRDS',      'keyword': 'frds',      'date_data': []},
                {'name': 'MTeam',     'keyword': 'm-team',    'date_data': []},
                {'name': 'HDHome',    'keyword': 'hdhome',    'date_data': []},
                {'name': 'BeiTai',    'keyword': 'beitai',    'date_data': []},
                {'name': 'JoyHD',     'keyword': 'joyhd',     'date_data': []},
                {'name': 'SoulVoice', 'keyword': 'soulvoice', 'date_data': []},
                {'name': 'PTHome',    'keyword': 'pthome',    'date_data': []},
                {'name': 'LeagueHD',  'keyword': 'leaguehd',  'date_data': []},
                {'name': 'HDArea',    'keyword': 'hdarea',    'date_data': []},
                {'name': 'PTSBao',    'keyword': 'ptsbao',    'date_data': []},
                {'name': 'AVGV',      'keyword': 'avgv',      'date_data': []},
                {'name': 'HDSky',     'keyword': 'hdsky',     'date_data': []}]
        self.last_check_date = "1970-01-01"
        
        # 读取IGNORE_FILE
        self.ignore_list = []
        if os.path.isfile(SysConfig.IGNORE_FILE):
            for line in open(SysConfig.IGNORE_FILE, encoding='UTF-8'):
                ignore_path, ignore_name = line.split('|', 1)
                ignore_path = ignore_path.strip()
                ignore_name = ignore_name.strip()
                if ignore_name[-1:] == '\n':
                    ignore_name = ignore_name[:-1]
                self.ignore_list.append({'Path': ignore_path, 'Name': ignore_name})
            Log.exec_log(f"read ignore from {SysConfig.IGNORE_FILE}")
        else:
            Log.exec_log(f"ignore_file:{SysConfig.IGNORE_FILE} does not exist")
        
        if self.read_pt_backup():
            Log.exec_log(f"read pt backup from {SysConfig.TORRENT_LIST_BACKUP}")
            Log.exec_log(f"last_check_date = {self.last_check_date}")
        if self.read_tracker_backup():
            Log.exec_log(f"read tracker backup from {SysConfig.TRACKER_LIST_BACKUP}")

    def get_torrent_index(self, client, torrent_hash):
        for i in range(len(self.torrent_list)):
            if self.torrent_list[i].client == client \
                    and (torrent_hash == self.torrent_list[i].hash or torrent_hash == self.torrent_list[i].HASH):
                return i
        return -1   

    def get_torrent(self, client, torrent_hash):
        for i in range(len(self.torrent_list)):
            if self.torrent_list[i].client == client \
                    and (torrent_hash == self.torrent_list[i].hash or torrent_hash == self.torrent_list[i].HASH):
                return self.torrent_list[i]
        return None

    def add_torrent(self, torrent: MyTorrent) -> bool:
        """
        将torrent加入torrent_list
        """
        if self.get_torrent_index(torrent.client, torrent.get_hash()) >= 0:
            Log.exec_log(f"torrent exists:{torrent.get_compiled_name()}")
            return False
        self.lock.acquire() 
        self.torrent_list.append(torrent)
        self.lock.release()
        self.write_pt_backup()
        return True

    def add_torrent_from_bookmark(self, torrent_hash: str) -> bool:
        rss = RSS.select_from_bookmarks_by_hash(torrent_hash)
        if rss is None:
            return False
        my_torrent = MyTorrent(None, rss, TO_BE_ADD)
        return self.add_torrent(my_torrent)

    def add_torrent_from_rss(self, rss_torrent: dict) -> bool:
        rss_name = rss_torrent.get('rss_name')
        torrent_hash = rss_torrent.get('hash')
        add_status = TO_BE_ADD if rss_torrent.get('auto') else MANUAL
        title = rss_torrent.get('title')
        if RSS.is_old_rss_torrent(torrent_hash, rss_name):
            Log.rss_log("old   :" + title)
            return False

        if rss_torrent.get('wait_free'):
            Log.rss_log(f'wait  :{title}')
        else:
            auto = 'auto  ' if rss_torrent.get('auto') else 'manual'
            Log.rss_log(f"{auto}:{title}")

        rss = RSS.from_rss_torrent(rss_torrent)
        if rss is None:
            return False
        if not rss.insert():  # 记录插入rss数据库
            Log.error_log("failed to insert into rss:{}|{}".format(rss_name, torrent_hash))
            return False
        t_torrent = MyTorrent(None, rss, add_status)

        if not rss_torrent.get('wait_free'):
            Log.exec_log("new rss tobeadd:" + t_torrent.get_compiled_name())
            Log.exec_log("               :" + rss.detail_url)
            Log.exec_log("               :{}/{}|{}/{}|{}|{}|{}|{}".format(rss.douban_id,
                                                                          rss.imdb_id,
                                                                          rss.douban_score,
                                                                          rss.imdb_score,
                                                                          rss.type,
                                                                          rss.nation,
                                                                          rss.movie_name,
                                                                          rss.director))
            self.add_torrent(t_torrent)
        else:
            Log.rss_log("               :{}/{}|{}/{}|{}|{}|{}|{}".format(rss.douban_id,
                                                                         rss.imdb_id,
                                                                         rss.douban_score,
                                                                         rss.imdb_score,
                                                                         rss.type,
                                                                         rss.nation,
                                                                         rss.movie_name,
                                                                         rss.director))

    def add_torrent_from_page(self, page_torrent: dict) -> bool:
        """

        :param page_torrent:
        :return:
        """

        site_name = page_torrent['site_name']
        torrent_id = page_torrent['torrent_id']
        title = page_torrent['title']

        if RSS.is_old_page_torrent(torrent_id, site_name):
            Log.page_log(f"old   :{title}")
            return False

        if page_torrent['auto']:
            Log.page_log(f"auto  :{title}")
        else:
            Log.page_log(f"manual:{title}")

        rss = RSS.from_page_torrent(page_torrent)
        if rss is None:
            Log.exec_log("failed to build rss:" + title)
            return False
        if not rss.insert():
            Log.exec_log("failed to insert rss:{}|{}|{}".format(rss.HASH, rss.site_name, rss.title))
            return False

        add_status = TO_BE_ADD if page_torrent['auto'] else MANUAL
        torrent = MyTorrent(torrent=None, rss=rss, add_status=add_status)
        Log.debug_log("page   torrent:" + torrent.HASH)
        Log.exec_log("page    torrent:" + title)
        return self.add_torrent(torrent)

    def del_list(self, client, torrent_hash):
        """
        从list中删除torrent
        """
        self.lock.acquire()
        for i in range(len(self.torrent_list)):
            if self.torrent_list[i].get_hash() == torrent_hash and self.torrent_list[i].client == client:
                del self.torrent_list[i]
                self.write_pt_backup()
                self.lock.release()
                return True
        self.lock.release()
        return False

    def add_torrent_to_client(self, client, torrent_hash):
        """
        从torrent_list中找出对应种子，并加入到client中
        :param client: client类型qb/tr
        :param torrent_hash:
        :return: string "Success" or 错误信息
        """
        self.lock.acquire()
        i = self.get_torrent_index(client, torrent_hash)
        if i == -1: 
            self.lock.release()
            return "not find matched torrent"
        t_pt_client = PTClient(client)
        if not t_pt_client.connect():
            return "failed to connect " + client
        if t_pt_client.add_torrent(torrent_hash=torrent_hash,
                                    download_link=self.torrent_list[i].download_link,
                                    download_dir=SysConfig.DOWNLOAD_FOLDER,
                                    is_paused=True):
            Log.exec_log("add new torrent:" + self.torrent_list[i].get_compiled_name())
            self.torrent_list[i].add_status = TO_BE_START
            self.lock.release()
            self.write_pt_backup()
            return "Success"
        else:
            self.torrent_list[i].add_status = MANUAL
            self.torrent_list[i].error_code = ERROR_FAILED_TO_ADD
            self.torrent_list[i].error_string = t_pt_client.error_string
            Log.error_log("failed to add torrent:" + self.torrent_list[i].get_compiled_name())
            self.lock.release()
            return "failed to add torrent"

    def del_torrent_from_client(self, client, torrent_hash, is_delete_file=True):
        """
        从torrent_list找出相应种子，从client中删除
        :param client:
        :param torrent_hash:
        :param is_delete_file:
        :return:"Success" or 错误信息
        """
        index = self.get_torrent_index(client, torrent_hash)
        if index == -1:
            return "False, not find matched torrent"
        add_status = self.torrent_list[index].add_status
        title = self.torrent_list[index].get_compiled_name()
        if not self.del_list(client, torrent_hash):
            return "False, failed to del_list"
        if add_status != TO_BE_ADD and add_status != MANUAL:
            t_pt_client = PTClient(client)
            if not t_pt_client.connect():
                return "False, failed to connect " + client
            if not t_pt_client.del_torrent(torrent_hash, is_delete_file=is_delete_file):
                return "False, can't delete torrent in " + client
        Log.exec_log("del  torrent:" + title)
        return "Success"

    @staticmethod
    def is_no_limit_tracker(torrent_tracker):
        # tracker是否属于keep_no_limit_trackers
        for tracker in Torrents.keep_no_limit_trackers:
            if torrent_tracker.find(tracker) >= 0:
                return True
        return False

    def set_upload_limit(self, upload_limit):
        """
        将keep_no_limit_trackers以外的torrent设置上传限制为upload_limit(KB/S)
        """
        for torrent in self.torrent_list:
            if Torrents.is_no_limit_tracker(torrent.tracker):
                torrent.set_upload_limit(-1)
            else:
                torrent.set_upload_limit(upload_limit)

    def reset_checked(self, client, pt_client):
        t_number_of_added = 0
        self.lock.acquire()
        for i in range(len(self.torrent_list)):
            if self.torrent_list[i].client == client:
                self.torrent_list[i].checked = 0
                if self.torrent_list[i].add_status == TO_BE_ADD: 
                    self.torrent_list[i].checked = 1
                    if pt_client.add_torrent(torrent_hash=self.torrent_list[i].HASH,
                                             download_link=self.torrent_list[i].download_link,
                                             is_paused=True):
                        t_number_of_added += 1
                        Log.exec_log("add new torrent:" + self.torrent_list[i].get_compiled_name())
                        self.torrent_list[i].add_status = TO_BE_START
                        if self.torrent_list[i].error_code == ERROR_FAILED_TO_ADD:
                            self.torrent_list[i].error_code = ERROR_NONE
                        self.write_pt_backup()
                        # time.sleep(60)
                    else:
                        self.torrent_list[i].add_status = MANUAL   # 出现错误，改成待确认状态
                        self.torrent_list[i].error_code = ERROR_FAILED_TO_ADD
                        self.torrent_list[i].error_string = pt_client.error_string
                        Log.error_log("failed to add torrent:" + self.torrent_list[i].get_compiled_name())
                elif self.torrent_list[i].add_status == MANUAL:
                    self.torrent_list[i].check_movie_info()
                else:
                    pass
                    
        self.lock.release()
        return t_number_of_added
            
    def read_pt_backup(self):
        """
        读取备份目录下的pt.txt，用于恢复种子记录数据，仅当初始化启动时调用
        """
        t_date = "1979-01-01"
        if not os.path.isfile(SysConfig.TORRENT_LIST_BACKUP):
            Log.exec_log(f"torrent_list_backup:{SysConfig.TORRENT_LIST_BACKUP} does not exist")
            return False
        for line in open(SysConfig.TORRENT_LIST_BACKUP, encoding='UTF-8'):
            # TODO jianrong
            try:
                client, torrent_hash, name, site_name, rss_name, title, download_link, detail_url, add_status_str, total_size_str, \
                    add_date_time, douban_id, imdb_id, id_status_str, douban_status_str, douban_score, imdb_score, \
                    error_code, error_string, t_date_data_str = line.split('|', 19)
            except Exception as error:
                client, torrent_hash, name, rss_name, title, download_link, detail_url, add_status_str, total_size_str, \
                add_date_time, douban_id, imdb_id, id_status_str, douban_status_str, douban_score, imdb_score, \
                error_code, error_string, t_date_data_str = line.split('|', 18)
                site_name = ""

            if t_date_data_str[-1:] == '\n':
                t_date_data_str = t_date_data_str[:-1]  # remove '\n'
            t_date_data_list = t_date_data_str.split(',')
            date_data = []
            try:
                for i in range(len(t_date_data_list)):
                    if t_date_data_list[i] == "":
                        break      # 最后一个可能为空就退出循环
                    t_date = (t_date_data_list[i])[:10]
                    t_data = int(t_date_data_list[i][11:])
                    date_data.append({'date': t_date, 'data': t_data})
            except Exception as err:
                print(err)
                print(f"{name}|{torrent_hash}")
                exit()

            t_torrent = Torrent(client, None)
            t_torrent.date_data = date_data
            if site_name == "":
                site_name = get_site_name_from_rss_name(rss_name)
            if site_name == "":
                print(f"{torrent_hash}:{rss_name}")
                exit()
            t_rss = RSS.from_pt_backup(torrent_hash,
                                       site_name,
                                       rss_name,
                                       download_link,
                                       detail_url,
                                       title,
                                       douban_id,
                                       imdb_id,
                                       add_date_time,
                                       int(total_size_str),
                                       int(id_status_str),
                                       int(douban_status_str),
                                       douban_score,
                                       imdb_score)
            my_torrent = MyTorrent(t_torrent, t_rss, int(add_status_str))
            my_torrent.error_code = int(error_code)
            my_torrent.error_string = error_string
            self.torrent_list.append(my_torrent)  # init, can't use add_torrent

        self.last_check_date = t_date
        return True

    def write_pt_backup(self):
        """
        把当前RSS列表写入备份文件
        """
        t_today = datetime.datetime.now().strftime('%Y-%m-%d')
        if t_today != self.last_check_date:
            t_is_new_day = True
        else:
            t_is_new_day = False
        if t_is_new_day:
            Log.debug_log("new day is :" + t_today)
            t_this_month = t_today[0:7]
            t_this_year = t_today[0:4]
            if t_this_month[5:7] == "01":
                t_last_month = str(int(t_this_year)-1)+"-"+"12"
            else:
                t_last_month = t_this_year+"-"+str(int(t_this_month[5:7])-1).zfill(2)
            
            t_file_name = os.path.basename(SysConfig.TORRENT_LIST_BACKUP)
            t_length = len(t_file_name)
            t_dir_name = os.path.dirname(SysConfig.TORRENT_LIST_BACKUP)
            for file in os.listdir(t_dir_name):
                if file[:t_length] == t_file_name and len(file) == t_length+11:  # 说明是TORRENT_LIST_BACKUP的每天备份文件
                    if file[t_length+1:t_length+8] != t_last_month and file[t_length+1:t_length+8] != t_this_month:
                        # 仅保留这个月和上月的备份文件
                        try:
                            os.remove(os.path.join(t_dir_name, file))
                        except Exception as err:
                            print(err)
                            Log.error_log("failed to  file:" + os.path.join(t_dir_name, file))
            
            # 把旧文件备份成昨天日期的文件,后缀+"."+gLastCheckDate
            t_last_day_file_name = SysConfig.TORRENT_LIST_BACKUP+"."+self.last_check_date
            if os.path.isfile(SysConfig.TORRENT_LIST_BACKUP):
                if os.path.isfile(t_last_day_file_name):
                    os.remove(t_last_day_file_name)
                os.rename(SysConfig.TORRENT_LIST_BACKUP, t_last_day_file_name)
                Log.debug_log("backup pt file:" + t_last_day_file_name)
        else:
            Log.log_clear(SysConfig.TORRENT_LIST_BACKUP)

        self.lock.acquire()
        try:
            fo = open(SysConfig.TORRENT_LIST_BACKUP, "w", encoding='UTF-8')
        except Exception as err:
            print(err)
            Log.error_log("Error:open ptbackup file to write：" + SysConfig.TORRENT_LIST_BACKUP)
            self.lock.release()
            return False
            
        for i in range(len(self.torrent_list)):
            my_torrent = self.torrent_list[i]
            t_date_data_list_str = ""
            for j in range(len(self.torrent_list[i].date_data)):
                t_date_data_str = self.torrent_list[i].date_data[j]['date']\
                                  + ":" \
                                  + str(self.torrent_list[i].date_data[j]['data'])
                t_date_data_list_str += t_date_data_str+','
            if t_date_data_list_str[-1:] == ',':
                t_date_data_list_str = t_date_data_list_str[:-1]  # 去掉最后一个','
            if self.torrent_list[i].rss_name == "":
                if self.torrent_list[i].tracker != "":
                    if self.torrent_list[i].tracker.find("hdsky") >= 0:
                        self.torrent_list[i].rss_name = "HDSky"
                        Log.debug_log(f"set {self.torrent_list[i].name} rss:HDSKy")
                    elif self.torrent_list[i].tracker.find("keepfrds") >= 0:
                        self.torrent_list[i].rss_name = "FRDS"
                        Log.debug_log(f"set {self.torrent_list[i].name} rss:FRDS")
                    elif self.torrent_list[i].tracker.find("m-team") >= 0:
                        self.torrent_list[i].rss_name = "MTeam"
                        Log.debug_log(f"set {self.torrent_list[i].name} rss:MTeam")
                    elif self.torrent_list[i].tracker.find("hdhome") >= 0:
                        self.torrent_list[i].rss_name = "HDHome"
                        Log.debug_log(f"set {self.torrent_list[i].name} rss:HDHome")
                    elif self.torrent_list[i].tracker.find("pthome") >= 0:
                        self.torrent_list[i].rss_name = "PTHome"
                        Log.debug_log(f"set {self.torrent_list[i].name} rss:PTHome")
                    elif self.torrent_list[i].tracker.find("soulvoice") >= 0:
                        self.torrent_list[i].rss_name = "SoulVoice"
                        Log.debug_log(f"set {self.torrent_list[i].name} rss:SoulVoice")
                    else:
                        Log.debug_log(f"{self.torrent_list[i].name}:not find tracker:{self.torrent_list[i].tracker}")
                else:
                    Log.debug_log(f"{self.torrent_list[i].name}:tracker is null")
            if my_torrent.site_name == "":
                print(f"no site_name:{my_torrent.get_hash()}|{my_torrent.name}|{my_torrent.rss_name}")
            try:
                t_str  =     self.torrent_list[i].client+'|'
                t_str +=     self.torrent_list[i].get_hash()+'|'
                t_str +=     self.torrent_list[i].name.replace('|', '')+'|'
                t_str +=     self.torrent_list[i].site_name + '|'
                t_str +=     self.torrent_list[i].rss_name+'|'
                t_str +=     self.torrent_list[i].title.replace('|', '')+'|'
                t_str +=     self.torrent_list[i].download_link+'|'
                t_str +=     self.torrent_list[i].detail_url+'|'
                t_str += str(self.torrent_list[i].add_status)+'|'
                t_str += str(self.torrent_list[i].total_size)+'|'
                t_str +=     self.torrent_list[i].add_datetime+'|'
                t_str +=     self.torrent_list[i].douban_id+'|'
                t_str +=     self.torrent_list[i].imdb_id+'|'
                t_str += str(self.torrent_list[i].id_status)+'|'
                t_str += str(self.torrent_list[i].douban_status)+'|'
                t_str +=     self.torrent_list[i].douban_score+'|'
                t_str +=     self.torrent_list[i].imdb_score+'|'
                t_str += str(self.torrent_list[i].error_code)+'|'
                t_str +=     self.torrent_list[i].error_string+'|'
                t_str +=     t_date_data_list_str+'\n'
            except Exception as err:
                print(err)
                self.torrent_list[i].print()
                continue
            fo.write(t_str)
      
        fo.close()
        Log.debug_log(f"{len(self.torrent_list)} torrents writed")
        self.lock.release()
        return True    
       
    def check_torrents(self, client):
        """
        进行TR/QB的所有种子进行检查和分析，并更新列表
        返回值：-1:错误，0:无更新，1:有更新 ，用于指示是否需要备份文件
        """
        t_number_of_added = t_number_of_deleted = t_number_of_updated = 0
        t_today = datetime.datetime.now().strftime('%Y-%m-%d')
        if t_today != self.last_check_date:
            t_is_new_day = True
        else:
            t_is_new_day = False
        # 连接Client并获取TorrentList列表
        t_pt_client = PTClient(client)
        if not t_pt_client.connect():
            Log.error_log("failed to connect to " + client)
            return -1

        # 先把检查标志复位,并对待加入的种子进行加入
        t_number_of_added += self.reset_checked(client, t_pt_client)

        # 开始逐个获取torrent并检查
        for torrent in t_pt_client.get_all_torrents():
            index = self.get_torrent_index(client, torrent.hash)
            if index == -1:
                Log.exec_log("findnew torrent:" + torrent.name)
                t_rss = RSS(torrent.hash, "", '', "", torrent.name, "", "", "", torrent.total_size, RETRY)
                self.add_torrent(MyTorrent(torrent, t_rss, STARTED))
                # index = -1                   #指向刚加入的种子
                t_number_of_added += 1
            self.torrent_list[index].checked = 1
            self.torrent_list[index].torrent.torrent = torrent.torrent  # 刷新种子信息
            t_torrent = self.torrent_list[index]

            # check addStatus
            if t_torrent.status == 'GOING' and (t_torrent.add_status == MANUAL or t_torrent.add_status == TO_BE_START):
                Log.exec_log(f"set STARTED:{t_torrent.name}:because it's status is GOING")
                t_torrent.add_status = STARTED
            if t_torrent.status == 'STOP' and t_torrent.add_status == MANUAL:
                Log.exec_log(f"set TO_BE_START:{t_torrent.name}:because it's status is STOP")
                t_torrent.add_status = TO_BE_START

            # 检查并设置标签
            t_torrent.set_tag()
                
            # 检查文件
            if t_torrent.progress == 100:
                if not t_torrent.check_files(t_is_new_day):
                    t_torrent.error_string = t_torrent.torrent.error_string
                    t_torrent.error_code = ERROR_CHECK_FILES
                    Log.exec_log(f"error::{t_torrent.name}:{t_torrent.error_string}")
                    t_torrent.stop()

            # mteam部分免费种，免费一天，但下载完成率很低
            if t_torrent.status != "STOP" and t_torrent.category == '下载' and t_torrent.progress <= 95:
                t_start_time = datetime.datetime.strptime(t_torrent.add_datetime, "%Y-%m-%d %H:%M:%S")
                t_seconds = (datetime.datetime.now()-t_start_time).total_seconds()
                if t_seconds >= 24*3600:
                    t_torrent.stop()
                    Log.exec_log(t_torrent.name + " have not done more than 1 day")
                    t_torrent.error_code = ERROR_MORE_THAN_1_DAY
                            
            # 如果种子状态不是STARTED，启动它
            if t_torrent.add_status == TO_BE_START and t_torrent.status == "STOP":
                if t_torrent.start_download():
                    Log.exec_log("start   torrent:" + t_torrent.name)
                    t_number_of_updated += 1
                    self.torrent_list[index].add_status = STARTED
                else:
                    Log.exec_log("failed to start_download:" + self.torrent_list[index].name)
                    continue

            # check movie_info
            t_torrent.check_movie_info()

            # 保存电影
            if t_torrent.category == "save":
                if t_torrent.save_movie():
                    # ExecLog("delete  torrent:"+tTorrent.get_compiled_name())
                    self.del_torrent_from_client(t_torrent.client, t_torrent.get_hash(), False)
            if t_torrent.category == "转移":
                t_torrent.move_to_tr()
        # end for torrents
        
        # 最后，找出没有Checked标志的种子列表
        for torrent in self.torrent_list:
            if torrent.checked == 0 and torrent.client == client:
                if torrent.add_status != MANUAL and torrent.add_status != TO_BE_ADD:
                    t_number_of_deleted += 1
                    Log.exec_log("delete  torrent:" + torrent.get_compiled_name())
                    self.del_list(torrent.client, torrent.get_hash())

        Log.debug_log("complete check_torrents  from " + client)
        if t_number_of_added > 0:
            Log.debug_log(str(t_number_of_added).zfill(4) + " torrents added")
        if t_number_of_deleted > 0:
            Log.debug_log(str(t_number_of_deleted).zfill(4) + " torrents deleted")
        if t_number_of_added >= 1 or t_number_of_deleted >= 1 or t_number_of_updated >= 1:
            return 1
        else:
            return 0
        
    def count_upload(self, client):
        """每天调用一次，进行统计上传量"""
        t_today = datetime.datetime.now().strftime('%Y-%m-%d')
        t_pt_client = PTClient(client)
        if not t_pt_client.connect():
            Log.exec_log("failed to connect " + client)
            return False
            
        for t_torrent in t_pt_client.get_all_torrents():
            t_index = self.get_torrent_index(client, t_torrent.hash)
            if t_index < 0:
                continue
            
            # 新的一天，更新记录每天的上传量（绝对值）
            self.torrent_list[t_index].date_data.append({'date': t_today, 'data': self.torrent_list[t_index].uploaded})
            if len(self.torrent_list[t_index].date_data) >= SysConfig.NUMBEROFDAYS+3:
                del self.torrent_list[t_index].date_data[0]  # 删除前面旧的数据
            
            # QB的下载类种子，如果上传量低于阀值，置类别为“低上传”
            if self.torrent_list[t_index].client == "QB" and self.torrent_list[t_index].category == '下载':
                if self.torrent_list[t_index].is_low_upload(SysConfig.NUMBEROFDAYS, SysConfig.UPLOADTHRESHOLD):
                    self.torrent_list[t_index].set_category("低上传")
                    Log.exec_log("low upload:" + self.torrent_list[t_index].get_compiled_name())
                    
    def tracker_data(self):
        """
        统计各站点的上传量
        """
        t_today = datetime.datetime.now().strftime('%Y-%m-%d')
        for i in range(len(self.tracker_data_list)):
            self.tracker_data_list[i]['date_data'].append({'date': t_today, 'data': 0})
            if len(self.tracker_data_list[i]['date_data']) >= 30:
                del self.tracker_data_list[i]['date_data'][0]

        for i in range(len(self.torrent_list)):
            if self.torrent_list[i].add_status == MANUAL or self.torrent_list[i].add_status == TO_BE_ADD:
                continue
            if len(self.torrent_list[i].date_data) == 0:
                Log.error_log("date_data is null:" + self.torrent_list[i].HASH)
                continue
            elif len(self.torrent_list[i].date_data) == 1:
                t_data = self.torrent_list[i].date_data[0]['data']
            else:
                t_data = self.torrent_list[i].date_data[-1]['data'] - self.torrent_list[i].date_data[-2]['data']
        
            tracker = self.torrent_list[i].tracker
            is_find = False
            for j in range(len(self.tracker_data_list)):
                if tracker.find(self.tracker_data_list[j]['keyword']) >= 0:
                    self.tracker_data_list[j]['date_data'][-1]['data'] += t_data
                    is_find = True
                    break
            if not is_find:
                Log.error_log(f"unknown tracker:{tracker} for torrent:{self.torrent_list[i].name}:")

        total_upload = 0
        for i in range(len(self.tracker_data_list)):
            t_upload = self.tracker_data_list[i]['date_data'][-1]['data']
            total_upload += t_upload
            Log.exec_log(f"{self.tracker_data_list[i]['name'].ljust(10)} upload(G):{round(t_upload/(1024*1024*1024), 3)}")
        Log.exec_log(f"total       upload(G):{round(total_upload / (1024 * 1024 * 1024), 3)}")
        Log.exec_log(f"average upload radio :{round(total_upload / (1024 * 1024 * 24 * 3600), 2)}M/s")
            
        for i in range(len(self.tracker_data_list)):
            t_date_data = self.tracker_data_list[i]['date_data']
            j = len(t_date_data)-1
            number_of_days = 0
            while j >= 0:
                if t_date_data[j]['data'] == 0:
                    number_of_days += 1
                else:
                    break
                j -= 1
            Log.exec_log(f"{self.tracker_data_list[i]['name'].ljust(10)} {str(number_of_days).zfill(2)} days no upload")
        
        self.write_tracker_backup()
        return 1

    def count_upload_traffic(self):
        """
        统计各站点的上传量,并写入备份
        :return:
        """
        t_today = datetime.datetime.now().strftime('%Y-%m-%d')
        for site in Sites.site_list:
            site.append_data({'date': t_today, 'data': 0})

        # 统计每一个种子的上传量到Sites.site_list
        for torrent in self.torrent_list:
            if torrent.add_status <= TO_BE_ADD:     #
                continue

            is_find = False
            for site in Sites.site_list:
                if torrent.site_name == site.site_name:
                    site.upload_traffic_list[-1]['data'] += torrent.get_last_day_upload_traffic()
                    is_find = True
                    break
            if not is_find:
                Log.error_log(f"unknown site_name for torrent:{torrent.name}:")

        # 打印各站点的上传量及总上传量等
        Sites.count_last_day_upload_traffic()
        # TODO 调测用traffic.txt，同步tracker_list运行一段时间
        Sites.write_tracker_data_backup("data/traffic.txt")

    # replaced by Sites.read_date_data_backup() soon
    def read_tracker_backup(self):
        """
        读取TrackerList的备份文件，用于各个Tracker的上传数据
        """ 
        if not os.path.isfile(SysConfig.TRACKER_LIST_BACKUP):
            Log.exec_log(f"tracker_list_backup:{SysConfig.TRACKER_LIST_BACKUP} does not exist")
            return False
            
        for line in open(SysConfig.TRACKER_LIST_BACKUP, encoding='UTF-8'):
            tracker, t_date_data_str = line.split('|', 1)
            if t_date_data_str[-1:] == '\n':
                t_date_data_str = t_date_data_str[:-1]  # remove '\n'
            t_date_data_list = t_date_data_str.split(',')
            date_data = []
            for i in range(len(t_date_data_list)):
                if t_date_data_list[i] == "":
                    break      # 最后一个可能为空就退出循环
                t_date = (t_date_data_list[i])[:10]
                t_data = int((t_date_data_list[i])[11:])
                date_data.append({'date': t_date, 'data': t_data})

            is_find = False
            for i in range(len(self.tracker_data_list)):
                if tracker == self.tracker_data_list[i]['name']:
                    self.tracker_data_list[i]['date_data'] = date_data
                    is_find = True
            if not is_find:
                Log.error_log("unknown tracker in TrackerBackup:" + tracker)
        return True

    # replaced by Sites.write_date_data_backup() soon
    def write_tracker_backup(self):
        t_today = datetime.datetime.now().strftime('%Y-%m-%d')
        if t_today != self.last_check_date:
            t_is_new_day = True
        else:
            t_is_new_day = False
        if t_is_new_day:
            t_this_month = t_today[0:7]
            t_this_year = t_today[0:4]
            if t_this_month[5:7] == "01":
                t_last_month = str(int(t_this_year)-1)+"-"+"12"
            else:
                t_last_month = t_this_year+"-"+str(int(t_this_month[5:7])-1).zfill(2)
            
            t_file_name = os.path.basename(SysConfig.TRACKER_LIST_BACKUP)
            t_length = len(t_file_name)
            t_dir_name = os.path.dirname(SysConfig.TRACKER_LIST_BACKUP)
            for file in os.listdir(t_dir_name):
                if file[:t_length] == t_file_name and len(file) == t_length+11:  # 说明是TorrentListBackup的每天备份文件
                    if file[t_length+1:t_length+8] != t_last_month \
                            and file[t_length+1:t_length+8] != t_this_month:  # 仅保留这个月和上月的备份文件
                        try:
                            os.remove(os.path.join(t_dir_name, file))
                        except Exception as err:
                            print(err)
                            Log.error_log("failed to delete file:" + os.path.join(t_dir_name, file))
            
            # 把旧文件备份成昨天日期的文件,后缀+"."+gLastCheckDate
            t_last_day_file_name = SysConfig.TRACKER_LIST_BACKUP+"."+self.last_check_date
            if os.path.isfile(SysConfig.TRACKER_LIST_BACKUP):
                if os.path.isfile(t_last_day_file_name):
                    os.remove(t_last_day_file_name)
                os.rename(SysConfig.TRACKER_LIST_BACKUP, t_last_day_file_name)
        else:
            Log.log_clear(SysConfig.TRACKER_LIST_BACKUP)

        try:
            fo = open(SysConfig.TRACKER_LIST_BACKUP, "w", encoding='UTF-8')
        except Exception as err:
            print(err)
            Log.error_log("Error:open ptbackup file to write：" + SysConfig.TRACKER_LIST_BACKUP)
            return -1

        for i in range(len(self.tracker_data_list)):
            t_date_data_list = self.tracker_data_list[i]['date_data']
            t_date_data_list_str = ""
            for j in range(len(t_date_data_list)):
                t_date_data_str = t_date_data_list[j]['date'] + ":" + str(t_date_data_list[j]['data'])
                t_date_data_list_str += t_date_data_str + ','
            if t_date_data_list_str[-1:] == ',':
                t_date_data_list_str = t_date_data_list_str[:-1]  # 去掉最后一个','
            t_str = self.tracker_data_list[i]['name'] + '|' + t_date_data_list_str + '\n'
            fo.write(t_str)
                 
        fo.close()
        Log.exec_log("success write tracklist")
        return 1

    def in_torrent_list(self, saved_path, dir_name):
        """
        判断SavedPath+DirName在不在TorrentList
        """
        for i in range(len(self.torrent_list)):
            t_src_dir_name = os.path.join(saved_path, dir_name)
            if len(self.torrent_list[i].files) == 0:
                continue
            first_file = os.path.realpath(os.path.join(self.torrent_list[i].save_path,
                                                       self.torrent_list[i].files[0]['name']))
            if t_src_dir_name in first_file:
                return True
            """
            for tFile in self.torrent_list[i].files:
                FirstFile = os.path.join(self.torrent_list[i].save_path,tFile['name'])
                tDestFile = os.path.realpath(FirstFile)
                if tSrcDirName in tDestFile: return True
            """
        return False

    def check_disk(self, check_disk_list):
        """
        对Path下的目录及文件逐个对比TorrentList，并进行标记。
        """
        def in_ignore_list(saved_path, dir_name):
            if saved_path[-1:] == '/':
                saved_path = saved_path[:-1]
            for i in range(len(self.ignore_list)):
                if (self.ignore_list[i])['Path'] == saved_path and (self.ignore_list[i])['Name'] == dir_name:
                    return True
            return False
            
        t_dir_name_list = []
        for disk_path in check_disk_list:
            Log.debug_log("begin check:" + disk_path)
            for file in os.listdir(disk_path):
                fullpathfile = os.path.join(disk_path, file)
                if os.path.isdir(fullpathfile) or os.path.isfile(fullpathfile):
                    # 一些特殊文件夹忽略
                    if file == 'lost+found' or file[0:6] == '.Trash' or file[0:4] == '0000':
                        Log.debug_log("ignore some dir:" + file)
                        continue 
                
                    if in_ignore_list(disk_path, file):
                        Log.debug_log("in Ignore List:" + disk_path + "::" + file)
                        continue
                    
                    # 合集
                    if os.path.isdir(fullpathfile) and len(file) >= 9 \
                            and re.match("[0-9][0-9][0-9][0-9]-[0-9][0-9][0-9][0-9]", file[:9]):
                        for file2 in os.listdir(fullpathfile):
                            fullpathfile2 = os.path.join(fullpathfile, file2)
                            if os.path.isfile(fullpathfile2):
                                continue
                            if in_ignore_list(fullpathfile, file2):
                                Log.debug_log("in Ignore List:" + fullpathfile2)
                                continue
                            if self.in_torrent_list(fullpathfile, file2):
                                Log.debug_log(file2 + ":: find in torrent list")
                            else:
                                Log.exec_log(file2 + ":: not find in torrent list")
                                t_dir_name_list.append({'DirPath': fullpathfile, 'DirName': fullpathfile2})
                    else:
                        if self.in_torrent_list(disk_path, file):
                            Log.debug_log(file + "::find in torrent list:")
                        else:
                            Log.exec_log(file + "::not find in torrent list:")
                            t_dir_name_list.append({'DirPath': disk_path, 'DirName': file})
                else:
                    Log.exec_log("Error：not file or dir")
        return t_dir_name_list

    def request_torrents_from_page_by_name(self, site_name: str) -> bool:
        """
        1,根据站点名称site_name找出符合条件的site
        2,访问site指定的torrents_page，获取满足筛选条件的种子信息
        3，补全种子信息，加入torrent_list
        :param site_name:
        :return:
        """
        Log.debug_log(f"request torrents_page_by_name:{site_name}")
        for site in Sites.site_list:
            if not site_name.lower() == site.site_name.lower():
                continue

            page_torrents = site.request_torrents_from_page()
            if page_torrents is None:
                return False
            Log.page_log(f'------ {site.site_name} -------')
            for page_torrent in page_torrents:
                self.add_torrent_from_page(page_torrent)
        return True

    def request_torrents_from_page_by_time(self, loop_times: int):
        """
        1,根据loop_times找出符合条件的site
        2,访问site指定的torrents_page，获取满足筛选条件的种子信息
        3，补全种子信息，加入torrent_list
        :param loop_times:
        :return:
        """
        Log.debug_log(f"request torrents_page_by_time:{loop_times}")
        for site in Sites.site_list:
            if site.time_interval == 0 or loop_times % site.time_interval != 0:
                continue

            page_torrents = site.request_torrents_from_page()
            if page_torrents is None:
                Log.error_log(f"error:{site.site_name} request torrents_page failed({site.error_string})")
                continue
            Log.page_log(f'------ {site.site_name} -------')
            for page_torrent in page_torrents:
                self.add_torrent_from_page(page_torrent)

    def request_torrents_from_rss_by_name(self, rss_name) -> bool:
        """

        :param rss_name:
        :return:
        """
        for site in Sites.site_list:
            rss_torrents = site.request_torrents_from_rss_by_name(rss_name)
            if rss_torrents is None:
                return False
            Log.rss_log(f'------ {rss_name} -------')
            for rss_torrent in rss_torrents:
                self.add_torrent_from_rss(rss_torrent)
        return True

    def request_torrents_from_rss_by_time(self, loop_times):
        """

        :param loop_times:
        :return:
        """
        for site in Sites.site_list:
            rss_torrents = site.request_torrents_from_rss_by_time(loop_times)
            if rss_torrents is None:
                Log.error_log(f"error:{site.site_name} request_torrents_from_rss_by_time failed({site.error_string})")
                continue
            Log.rss_log(f'------ {site.site_name} -------')
            for rss_torrent in rss_torrents:
                self.add_torrent_from_rss(rss_torrent)

    def print_low_upload(self):
        reply = ""
        for i in range(len(self.torrent_list)):
            if self.torrent_list[i].category == '低上传':
                t_torrent = self.torrent_list[i]
                reply += t_torrent.get_compiled_name()+'\n'
                reply += '    {}|{}/{} \n'.format(t_torrent.info.movie_name,
                                                  t_torrent.info.douban_score,
                                                  t_torrent.info.imdb_score)
        return reply

    def query_torrents(self, m_list=None):
        """
        根据mList请求，组装成json数组发出
        mList =
        []   : default qb+null
        qb   : qb
        all  : all
        tr   : tr
        null : null
        """
        if m_list is None or len(m_list) == 0:
            t_client_list = ['QB', '']
        elif len(m_list) >= 2:
            Log.error_log("invalid arg mList=" + ' '.join(m_list))
            return ""
        else:  # len(mList) == 1
            if m_list[0].lower() == 'qb':
                t_client_list = ['QB']
            elif m_list[0].lower() == 'tr':
                t_client_list = ['TR']
            elif m_list[0].lower() == 'all':
                t_client_list = ['QB', 'TR', '']
            elif m_list[0].lower() == 'null':
                t_client_list = ['']
            elif m_list[0].lower() == 'default':
                t_client_list = ['QB', '']
            else:
                Log.error_log("invalid arg mList=" + m_list[0])
                return ""

        # qb，返回前刷新下状态
        # if m_list[0].lower() == 'qb':
        #    self.check_torrents("QB")

        temp_list = []
        for i in range(len(self.torrent_list)):
            if self.torrent_list[i].client in t_client_list:
                torrent = self.torrent_list[i]
                temp_list.append(torrent.to_dict())
        return json.dumps(temp_list)

    def handle_bookmark(self, request):
        action = request.get("action")
        if action is None:
            return "failed, no action"
        if action == "query":
            return Torrents.query_all_bookmarks()
        elif action == "save":
            HASH = request.get("hash")
            if HASH is None:
                return "failed, no hash"
            my_torrent = self.get_torrent("QB",HASH)
            reply = my_torrent.save_bookmark()
            if reply == "Success":
                self.del_torrent_from_client("QB", HASH)
            return reply
        elif action == "search":
            return Torrents.search_bookmarks(request)

    @staticmethod
    def query_all_bookmarks():
        temp_list = []
        results = select("select hash,sitename,rssname,title,downloadlink,detailurl,size,adddatetime,doubanid,imdbid "
                         "from bookmarks", None)
        for result in results:
            HASH = result[0]
            site_name = result[1]
            rss_name = result[2]
            title = result[3]
            download_url = result[4]
            detail_url = result[5]
            size = result[6]
            add_datetime = result[7]
            douban_id = result[8]
            imdb_id = result[9]
            id_status = OK if douban_id != "" or imdb_id != "" else RETRY
            rss = RSS(HASH, site_name, rss_name, download_url, detail_url, title, douban_id, imdb_id, add_datetime, size, id_status)
            my_torrent = MyTorrent(None, rss, BOOKMARK)
            temp_list.append(my_torrent.to_dict())
        return json.dumps(temp_list)

    @staticmethod
    def search_bookmarks(request):
        # by douban_id and imdb_id
        douban_id = request.get("douban_id", "")
        imdb_id = request.get("imdb_id", "")
        temp_list = []
        if douban_id != "":
            sql = "select hash,sitename,rssname,title,downloadlink,detailurl,size,adddatetime,doubanid,imdbid,torrentid " \
                  "from bookmarks where doubanid=%s"
            results = select(sql, (douban_id,))
            if results is not None:
                for result in results:
                    HASH = result[0]
                    site_name = result[1]
                    rss_name = result[2]
                    title = result[3]
                    download_link = result[4]
                    detail_url = result[5]
                    size = result[6]
                    add_datetime = result[7]
                    douban_id = result[8]
                    imdb_id = result[9]
                    torrent_id = result[10]
                    id_status = OK if douban_id != "" or imdb_id != "" else RETRY
                    rss = RSS(HASH, site_name, rss_name, download_link, detail_url, title, douban_id, imdb_id, add_datetime, size, id_status)
                    my_torrent = MyTorrent(None, rss, BOOKMARK)
                    temp_list.append(my_torrent.to_dict())
        elif imdb_id != "":
            sql = "select hash,name,rssname,title,downloadlink,detailurl,size,adddatetime,doubanid,imdbid,torrentid " \
                  "from bookmarks where imdbid=%s"
            results = select(sql, (imdb_id,))
            if results is not None:
                for result in results:
                    HASH = result[0]
                    site_name = result[1]
                    rss_name = result[2]
                    title = result[3]
                    download_link = result[4]
                    detail_url = result[5]
                    size = result[6]
                    add_datetime = result[7]
                    douban_id = result[8]
                    imdb_id = result[9]
                    torrent_id = result[10]
                    id_status = OK if douban_id != "" or imdb_id != "" else RETRY
                    rss = RSS(HASH, site_name, rss_name, download_link, detail_url, title, douban_id, imdb_id, add_datetime, size, id_status)
                    my_torrent = MyTorrent(None, rss, BOOKMARK)
                    temp_list.append(my_torrent.to_dict())
        else:
            return "failed, there is no douban_id or imdb_id"
        return json.dumps(temp_list)

    def request_set_id(self, request_str):
        """
        client|hash|doubanid|imdbid
        """
        t_client, t_hash, t_douban_id, t_imdbid = request_str.split('|', 3)
        if t_hash == "" or (t_imdbid == "" and t_douban_id == ""):
            return "False,empty hash or empty id"
        for i in range(len(self.torrent_list)):
            if t_client == self.torrent_list[i].client and t_hash == self.torrent_list[i].get_hash():
                if self.torrent_list[i].set_id(t_douban_id, t_imdbid):
                    self.torrent_list[i].error_code = ERROR_NONE
                    self.write_pt_backup()
                    return "Success"
                else:
                    return "False,failed set id"
        return "False, not find matched torrent"

    def set_info(self, douban_id, imdb_id):
        """
        刷新torrent的info信息 in memory，清除error_code
        """
        for torrent in self.torrent_list:
            if torrent.douban_id != douban_id and torrent.imdb_id != imdb_id:
                continue
            if torrent.rss is not None and torrent.rss.info is not None:
                if torrent.rss.info.select():  # refresh from db
                    if torrent.error_code == ERROR_DOUBAN_DETAIL:
                        torrent.error_code = ERROR_NONE
                else:
                    Log.error_log(f"set_info之后，仍查询不到info表信息:{torrent.name}|{douban_id}|{imdb_id}")
                    torrent.error_code = ERROR_DOUBAN_DETAIL
                    torrent.error_string = "set_info之后，仍查询不到info表信息"

    def request_set_category(self, request_str):
        """
        client|hash|category
        """
        try:
            t_client, t_hash, t_category = request_str.split('|', 2)
        except Exception as err:
            print(err)
            Log.exec_log("failed to split:" + request_str)
            return "error requeststr:" + request_str
        Log.debug_log("to set_cateory {}|{}|{}".format(t_client, t_hash, t_category))
        client = PTClient(t_client)
        if not client.connect():
            Log.exec_log("failed to connect " + t_client)
            return "failed to connect "+t_client
        if client.set_category(t_hash, t_category):
            mytorrent = self.get_torrent(t_client, t_hash)
            compiled_name = mytorrent.get_compiled_name() if mytorrent is not None else "未找到torrent"
            Log.exec_log(f"set_category:{compiled_name}|{t_category}")
            return "Success"
        else:
            return "failed to set category"

    def request_del_torrent(self, request_str):
        """
        client|hash|is_delete_file
        """
        try:
            t_client, t_hash, t_is_delete_file_str = request_str.split('|', 2)
        except Exception as err:
            print(err)
            Log.exec_log("failed to split:" + request_str)
            return "error requeststr:" + request_str
        Log.debug_log("to del {}|{}".format(t_client, t_hash))
        t_is_delete_file = (t_is_delete_file_str.lower() == "true")
        if self.get_torrent("QB", t_hash) is not None:
            return self.del_torrent_from_client(t_client, t_hash, t_is_delete_file)
        # 尝试从bookmarks表中删除
        if delete("delete from bookmarks where hash=%s", (t_hash,)):
            return "Success"
        else:
            return "failed, not found in bookmarks"

    def request_act_torrent(self, request_str):
        """
        client|hash|action
        """
        try:
            t_client, t_hash, t_action = request_str.split('|', 2)
        except Exception as err:
            print(err)
            Log.exec_log("failed to split:" + request_str)
            return "error requeststr:" + request_str
        Log.debug_log("to act {}|{}|{}".format(t_client, t_hash, t_action))
        
        if t_action == "add":
            return self.add_torrent_to_client(t_client, t_hash)

        # TODO
        index = self.get_torrent_index(t_client, t_hash)
        if index == -1:
            return "not find match torrent"
        if t_action == "start":
            self.torrent_list[index].start()
        elif t_action == "stop":
            self.torrent_list[index].stop()
        Log.exec_log(f"{t_action} :{self.torrent_list[index].get_compiled_name()}")
        return "Success"

    def request_torrent_act(self, request: dict) -> str:
        """

        :param request:
            'action': str = add/start/stop/delete
            'hash': str
            'client': str
            'is_bookmark': 0/1
            'is_delete_file': 0/1
        :return:
        """
        client = request.get('client')
        torrent_hash = request.get('hash')
        index = self.get_torrent_index(client, torrent_hash)
        action = request.get('action', "")
        if action == "add":
            if request.get('is_bookmark', 0) == 1:
                self.add_torrent_from_bookmark(torrent_hash)
            return self.add_torrent_to_client(client, torrent_hash)
        elif action == 'delete':
            if request.get('is_bookmark', 0) == 1:
                if RSS.delete_from_bookmarks_by_hash(torrent_hash):
                    return "Success"
                else:
                    return "failed: delete from bookmarks"
            else:
                is_delete_file = True if request.get('is_delete_file', 0) == 1 else False
                if index == -1:
                    return "not find matched torrent"
                return self.del_torrent_from_client(client, hash, is_delete_file)
        elif action == "start":
            if index == -1:
                return "not find matched torrent"
            if self.torrent_list[index].start():
                return "Success"
            else:
                return f"failed:{self.torrent_list[index].error_string}"
        elif action == "stop":
            if index == -1:
                return "not find matched torrent"
            if self.torrent_list[index].stop():
                return "Success"
            else:
                return f"failed:{self.torrent_list[index].error_string}"
        else:
            return f"failed: unknown action({action})"

    @staticmethod
    def request_saved_movie(request_str):
        """
        request:
            movie doubanid|imdbid
        reply:
            dirname|disk|deleted\n
            dirname|disk|deleted\n
        """
        try:
            douban_id, imdb_id = request_str.split('|', 1)
        except Exception as err:
            print(err)
            Log.exec_log("failed to split:" + request_str)
            return "failed:error requeststr:" + request_str
        Log.debug_log("to movie {}|{}".format(douban_id, imdb_id))
        
        if douban_id != "":
            sel_sql = 'select dirname,disk,deleted from movies where doubanid = %s'
            sel_val = (douban_id,)
        else:
            sel_sql = 'select dirname,disk,deleted from movies where imdbid = %s'
            sel_val = (imdb_id,)
        select_result = select(sel_sql, sel_val)
        if select_result is None or len(select_result) == 0:
            return "failed: no record"
        reply = ""
        for t_select in select_result:
            reply += t_select[0]+'|'   # dirname
            reply += t_select[1]+'|'   # disk
            reply += str(t_select[2])+'|'+'\n'  # deleted
        return reply

    def request_tracker_message(self, request_str):
        """
        废弃
        client|hash
        """
        try:
            t_client, t_hash = request_str.split('|', 1)
        except Exception as err:
            print(err)
            Log.exec_log("failed to split:" + request_str)
            return "error requeststr:" + request_str
        Log.debug_log("get_tracker_message {}|{}".format(t_client, t_hash))
        
        torrent = self.get_torrent(t_client, t_hash)
        return torrent.tracker_message if torrent is not None else "failed"
