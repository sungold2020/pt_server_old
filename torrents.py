#!/usr/bin/python3
# coding=utf-8

import feedparser


from rss import *
from mytorrent import *
from ptsite import *
from client import PTClient
from rsssite import *
import threading 

global g_config

# 连续NUMBEROFDAYS上传低于UPLOADTHRESHOLD，并且类别不属于'保种'的种子，会自动停止。
# NUMBEROFDAYS = 1                           #连续多少天低于阈值
# UPLOADTHRESHOLD = 0.03                    #阈值，上传/种子大小的比例

# TORRENT_LIST_BACKUP = "data/pt.txt"  #种子信息备份目录（重要的是每天的上传量）
# TRACKER_LIST_BACKUP = "data/tracker.txt"
# IGNORE_FILE = "data/ignore.txt"

# TR_KEEP_DIR='/media/root/BT/keep/'   #TR种子缺省保存路径


class Torrents:
    def __init__(self):
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
        if os.path.isfile(g_config.IGNORE_FILE):
            for line in open(g_config.IGNORE_FILE):
                ignore_path, ignore_name = line.split('|', 1)
                ignore_path = ignore_path.strip()
                ignore_name = ignore_name.strip()
                if ignore_name[-1:] == '\n':
                    ignore_name = ignore_name[:-1]
                self.ignore_list.append({'Path': ignore_path, 'Name': ignore_name})
            exec_log(f"read ignore from {g_config.IGNORE_FILE}")
        else:
            exec_log(f"ignore_file:{g_config.IGNORE_FILE} does not exist")
        
        if self.read_pt_backup():
            exec_log(f"read pt backup from {g_config.TORRENT_LIST_BACKUP}")
            exec_log(f"last_check_date = {self.last_check_date}")
        if self.read_tracker_backup():
            exec_log(f"read tracker backup from {g_config.TRACKER_LIST_BACKUP}")

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

    def append_list(self, torrent):
        if self.get_torrent_index(torrent.client, torrent.get_hash()) >= 0:
            exec_log(f"torrent exists:{torrent.get_compiled_name()}")
            return False
        self.lock.acquire() 
        self.torrent_list.append(torrent)
        self.lock.release()
        self.write_pt_backup()
        return True

    def del_list(self, client, torrent_hash):
        self.lock.acquire()
        for i in range(len(self.torrent_list)):
            if self.torrent_list[i].get_hash() == torrent_hash and self.torrent_list[i].client == client:
                del self.torrent_list[i]
                self.write_pt_backup()
                self.lock.release()
                return True
        self.lock.release()
        return False

    def add_torrent(self, client, torrent_hash):
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
                                   is_paused=True):
            exec_log("add new torrent:" + self.torrent_list[i].get_compiled_name())
            self.torrent_list[i].add_status = TO_BE_START
            self.lock.release()
            self.write_pt_backup()
            return "Success"
        else:
            self.torrent_list[i].add_status = MANUAL
            self.torrent_list[i].error_code = ERROR_FAILED_TO_ADD
            self.torrent_list[i].error_string = t_pt_client.error_string
            error_log("failed to add torrent:" + self.torrent_list[i].get_compiled_name())
            self.lock.release()
            return "failed to add torrent"

    def del_torrent(self, client, torrent_hash, is_delete_file=True):
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
        exec_log("del  torrent:" + title)
        return "Success"

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
                        exec_log("add new torrent:" + self.torrent_list[i].get_compiled_name())
                        self.torrent_list[i].add_status = TO_BE_START
                        if self.torrent_list[i].error_code == ERROR_FAILED_TO_ADD:
                            self.torrent_list[i].error_code = ERROR_NONE
                        self.write_pt_backup()
                        # time.sleep(60)
                    else:
                        self.torrent_list[i].add_status = MANUAL   # 出现错误，改成待确认状态
                        self.torrent_list[i].error_code = ERROR_FAILED_TO_ADD
                        self.torrent_list[i].error_string = pt_client.error_string
                        error_log("failed to add torrent:" + self.torrent_list[i].get_compiled_name())
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
        if not os.path.isfile(g_config.TORRENT_LIST_BACKUP):
            exec_log(f"torrent_list_backup:{g_config.TORRENT_LIST_BACKUP} does not exist")
            return False
        for line in open(g_config.TORRENT_LIST_BACKUP):
            client, torrent_hash, name, site_name, title, download_link, detail_url, add_status_str, total_size_str, \
                add_date_time, douban_id, imdb_id, id_status_str, douban_status_str, douban_score, imdb_score, \
                error_code, error_string, t_date_data_str = line.split('|', 18)
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
            t_rss = RSS(torrent_hash,
                        site_name,
                        download_link,
                        detail_url,
                        title,
                        douban_id,
                        imdb_id,
                        add_date_time,
                        int(total_size_str),
                        int(id_status_str))
            if t_rss.douban_status == RETRY:
                t_rss.douban_status = int(douban_status_str)
            if t_rss.douban_score == "":
                t_rss.douban_score = douban_score
            if t_rss.imdb_score == "":
                t_rss.imdb_score = imdb_score
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
            debug_log("new day is :" + t_today)
            t_this_month = t_today[0:7]
            t_this_year = t_today[0:4]
            if t_this_month[5:7] == "01":
                t_last_month = str(int(t_this_year)-1)+"-"+"12"
            else:
                t_last_month = t_this_year+"-"+str(int(t_this_month[5:7])-1).zfill(2)
            
            t_file_name = os.path.basename(g_config.TORRENT_LIST_BACKUP)
            t_length = len(t_file_name)
            t_dir_name = os.path.dirname(g_config.TORRENT_LIST_BACKUP)
            for file in os.listdir(t_dir_name):
                if file[:t_length] == t_file_name and len(file) == t_length+11:  # 说明是TORRENT_LIST_BACKUP的每天备份文件
                    if file[t_length+1:t_length+8] != t_last_month and file[t_length+1:t_length+8] != t_this_month:
                        # 仅保留这个月和上月的备份文件
                        try:
                            os.remove(os.path.join(t_dir_name, file))
                        except Exception as err:
                            print(err)
                            error_log("failed to  file:" + os.path.join(t_dir_name, file))
            
            # 把旧文件备份成昨天日期的文件,后缀+"."+gLastCheckDate
            t_last_day_file_name = g_config.TORRENT_LIST_BACKUP+"."+self.last_check_date
            if os.path.isfile(g_config.TORRENT_LIST_BACKUP):
                if os.path.isfile(t_last_day_file_name):
                    os.remove(t_last_day_file_name)
                os.rename(g_config.TORRENT_LIST_BACKUP, t_last_day_file_name)
                debug_log("backup pt file:" + t_last_day_file_name)
        else:
            log_clear(g_config.TORRENT_LIST_BACKUP)

        self.lock.acquire()
        try:
            fo = open(g_config.TORRENT_LIST_BACKUP, "w")
        except Exception as err:
            print(err)
            error_log("Error:open ptbackup file to write：" + g_config.TORRENT_LIST_BACKUP)
            self.lock.release()
            return False
            
        for i in range(len(self.torrent_list)):
            t_date_data_list_str = ""
            for j in range(len(self.torrent_list[i].date_data)):
                t_date_data_str = self.torrent_list[i].date_data[j]['date']\
                                  + ":" \
                                  + str(self.torrent_list[i].date_data[j]['data'])
                t_date_data_list_str += t_date_data_str+','
            if t_date_data_list_str[-1:] == ',':
                t_date_data_list_str = t_date_data_list_str[:-1]  # 去掉最后一个','
            try:
                t_str  =     self.torrent_list[i].client+'|'
                t_str +=     self.torrent_list[i].get_hash()+'|'
                t_str +=     self.torrent_list[i].name.replace('|', '')+'|'
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
        debug_log(f"{len(self.torrent_list)} torrents writed")
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
            error_log("failed to connect to " + client)
            return -1

        # 先把检查标志复位,并对待加入的种子进行加入
        t_number_of_added += self.reset_checked(client, t_pt_client)

        # 开始逐个获取torrent并检查
        for torrent in t_pt_client.get_all_torrents():
            index = self.get_torrent_index(client, torrent.hash)
            if index == -1:
                exec_log("findnew torrent:" + torrent.name)
                t_rss = RSS(torrent.hash, "", '', "", torrent.name, "", "", "", torrent.total_size, RETRY)
                self.append_list(MyTorrent(torrent, t_rss, STARTED))
                # index = -1                   #指向刚加入的种子
                t_number_of_added += 1
            self.torrent_list[index].checked = 1
            self.torrent_list[index].torrent.torrent = torrent.torrent  # 刷新种子信息
            t_torrent = self.torrent_list[index]

            # check addStatus
            if t_torrent.status == 'GOING' and (t_torrent.add_status == MANUAL or t_torrent.add_status == TO_BE_START):
                t_torrent.add_status = STARTED
            if t_torrent.status == 'STOP' and t_torrent.add_status == MANUAL:
                t_torrent.add_status = TO_BE_START

            # 检查并设置标签
            t_torrent.set_tag()
                
            # 检查文件
            if t_torrent.progress == 100:
                if not t_torrent.check_files(t_is_new_day):
                    t_torrent.error_string = t_torrent.torrent.error_string
                    t_torrent.error_code = ERROR_CHECK_FILES
                    exec_log(f"error::{t_torrent.name}:self.error_string")
                    t_torrent.stop()

            # mteam部分免费种，免费一天，但下载完成率很低
            if t_torrent.status != "STOP" and t_torrent.category == '下载' and t_torrent.progress <= 95:
                t_start_time = datetime.datetime.strptime(t_torrent.add_datetime, "%Y-%m-%d %H:%M:%S")
                t_seconds = (datetime.datetime.now()-t_start_time).total_seconds()
                if t_seconds >= 24*3600:
                    t_torrent.stop()
                    exec_log(t_torrent.name + " have not done more than 1 day")
                    t_torrent.error_code = ERROR_MORE_THAN_1_DAY
                            
            # 如果种子状态不是STARTED，启动它
            if t_torrent.add_status == TO_BE_START and t_torrent.status == "STOP":
                if t_torrent.start_download():
                    exec_log("start   torrent:" + t_torrent.name)
                    t_number_of_updated += 1
                    self.torrent_list[index].add_status = STARTED
                else:
                    exec_log("failed to start_download:" + self.torrent_list[index].name)
                    continue

            # check movie_info
            t_torrent.check_movie_info()

            # 保存电影
            if t_torrent.category == "save":
                if t_torrent.save_movie():
                    # ExecLog("delete  torrent:"+tTorrent.get_compiled_name())
                    self.del_torrent(t_torrent.client, t_torrent.get_hash(), False)
            if t_torrent.category == "转移":
                t_torrent.move_to_tr()
        # end for torrents
        
        # 最后，找出没有Checked标志的种子列表
        for torrent in self.torrent_list:
            if torrent.checked == 0 and torrent.client == client:
                if torrent.add_status != MANUAL and torrent.add_status != TO_BE_ADD:
                    t_number_of_deleted += 1
                    exec_log("delete  torrent:" + torrent.get_compiled_name())
                    self.del_list(torrent.client, torrent.get_hash())

        debug_log("complete check_torrents  from " + client)
        if t_number_of_added > 0:
            debug_log(str(t_number_of_added).zfill(4) + " torrents added")
        if t_number_of_deleted > 0:
            debug_log(str(t_number_of_deleted).zfill(4) + " torrents deleted")
        if t_number_of_added >= 1 or t_number_of_deleted >= 1 or t_number_of_updated >= 1:
            return 1
        else:
            return 0
        
    def count_upload(self, client):
        """每天调用一次，进行统计上传量"""
        t_today = datetime.datetime.now().strftime('%Y-%m-%d')
        t_pt_client = PTClient(client)
        if not t_pt_client.connect():
            exec_log("failed to connect " + client)
            return False
            
        for t_torrent in t_pt_client.get_all_torrents():
            t_index = self.get_torrent_index(client, t_torrent.hash)
            if t_index < 0:
                continue
            
            # 新的一天，更新记录每天的上传量（绝对值）
            self.torrent_list[t_index].date_data.append({'date': t_today, 'data': self.torrent_list[t_index].uploaded})
            if len(self.torrent_list[t_index].date_data) >= g_config.NUMBEROFDAYS+3:
                del self.torrent_list[t_index].date_data[0]  # 删除前面旧的数据
            
            # QB的下载类种子，如果上传量低于阀值，置类别为“低上传”
            if self.torrent_list[t_index].client == "QB" and self.torrent_list[t_index].category == '下载':
                if self.torrent_list[t_index].is_low_upload(g_config.NUMBEROFDAYS, g_config.UPLOADTHRESHOLD):
                    self.torrent_list[t_index].set_category("低上传")
                    exec_log("low upload:" + self.torrent_list[t_index].get_compiled_name())
                    
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
                error_log("date_data is null:" + self.torrent_list[i].HASH)
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
                error_log(f"unknown tracker:{tracker} for torrent:{self.torrent_list[i].name}:")

        total_upload = 0
        for i in range(len(self.tracker_data_list)):
            t_upload = self.tracker_data_list[i]['date_data'][-1]['data']
            total_upload += t_upload
            exec_log(f"{self.tracker_data_list[i]['name'].ljust(10)} upload(G):{round(t_upload/(1024*1024*1024), 3)}")
        exec_log(f"total       upload(G):{round(total_upload / (1024 * 1024 * 1024), 3)}")
        exec_log(f"average upload radio :{round(total_upload / (1024 * 1024 * 24 * 3600), 2)}M/s")
            
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
            exec_log(f"{self.tracker_data_list[i]['name'].ljust(10)} {str(number_of_days).zfill(2)} days no upload")
        
        self.write_tracker_backup()
        return 1
        
    def read_tracker_backup(self):
        """
        读取TrackerList的备份文件，用于各个Tracker的上传数据
        """ 
        if not os.path.isfile(g_config.TRACKER_LIST_BACKUP):
            exec_log(f"tracker_list_backup:{g_config.TRACKER_LIST_BACKUP} does not exist")
            return False
            
        for line in open(g_config.TRACKER_LIST_BACKUP):
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
                error_log("unknown tracker in TrackerBackup:" + tracker)
        return True
            
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
            
            t_file_name = os.path.basename(g_config.TRACKER_LIST_BACKUP)
            t_length = len(t_file_name)
            t_dir_name = os.path.dirname(g_config.TRACKER_LIST_BACKUP)
            for file in os.listdir(t_dir_name):
                if file[:t_length] == t_file_name and len(file) == t_length+11:  # 说明是TorrentListBackup的每天备份文件
                    if file[t_length+1:t_length+8] != t_last_month \
                            and file[t_length+1:t_length+8] != t_this_month:  # 仅保留这个月和上月的备份文件
                        try:
                            os.remove(os.path.join(t_dir_name, file))
                        except Exception as err:
                            print(err)
                            error_log("failed to delete file:" + os.path.join(t_dir_name, file))
            
            # 把旧文件备份成昨天日期的文件,后缀+"."+gLastCheckDate
            t_last_day_file_name = g_config.TRACKER_LIST_BACKUP+"."+self.last_check_date
            if os.path.isfile(g_config.TRACKER_LIST_BACKUP):
                if os.path.isfile(t_last_day_file_name):
                    os.remove(t_last_day_file_name)
                os.rename(g_config.TRACKER_LIST_BACKUP, t_last_day_file_name)
        else:
            log_clear(g_config.TRACKER_LIST_BACKUP)

        try:
            fo = open(g_config.TRACKER_LIST_BACKUP, "w")
        except Exception as err:
            print(err)
            error_log("Error:open ptbackup file to write：" + g_config.TRACKER_LIST_BACKUP)
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
        exec_log("success write tracklist")
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
            debug_log("begin check:" + disk_path)
            for file in os.listdir(disk_path):
                fullpathfile = os.path.join(disk_path, file)
                if os.path.isdir(fullpathfile) or os.path.isfile(fullpathfile):
                    # 一些特殊文件夹忽略
                    if file == 'lost+found' or file[0:6] == '.Trash' or file[0:4] == '0000':
                        debug_log("ignore some dir:" + file)
                        continue 
                
                    if in_ignore_list(disk_path, file):
                        debug_log("in Ignore List:" + disk_path + "::" + file)
                        continue
                    
                    # 合集
                    if os.path.isdir(fullpathfile) and len(file) >= 9 \
                            and re.match("[0-9][0-9][0-9][0-9]-[0-9][0-9][0-9][0-9]", file[:9]):
                        for file2 in os.listdir(fullpathfile):
                            fullpathfile2 = os.path.join(fullpathfile, file2)
                            if os.path.isfile(fullpathfile2):
                                continue
                            if in_ignore_list(fullpathfile, file2):
                                debug_log("in Ignore List:" + fullpathfile2)
                                continue
                            if self.in_torrent_list(fullpathfile, file2):
                                debug_log(file2 + ":: find in torrent list")
                            else:
                                exec_log(file2 + ":: not find in torrent list")
                                t_dir_name_list.append({'DirPath': fullpathfile, 'DirName': fullpathfile2})
                    else:
                        if self.in_torrent_list(disk_path, file):
                            debug_log(file + "::find in torrent list:")
                        else:
                            exec_log(file + "::not find in torrent list:")
                            t_dir_name_list.append({'DirPath': disk_path, 'DirName': file})
                else:
                    exec_log("Error：not file or dir")
        return t_dir_name_list

    def request_free(self, site_name="", time_interval=-1):
        debug_log(f"request free:{site_name}::{time_interval}")
        for site in g_config.site_list:
            if site_name.lower() == site['name'].lower()\
                    or (site['time_interval'] != 0 and time_interval % site['time_interval'] == 0):
                t_site = site
            else:
                continue
            site_log("begin request free:"+t_site['name'])
            t_page = NexusPage(t_site)
            if not t_page.request_free_page():
                continue

            for task in t_page.find_free_torrents():
                site_log(f"{task['auto']}|{task['title']}|{task['torrent_id']}|{task['douban_id']}|{task['imdb_id']}")
                # if t_task['free'] == False: continue
                torrent_id = task['torrent_id']
                title = task['title']
                details = task['details']

                download_link = task['download_link']
                if RSS.old_free(torrent_id, site['name']):
                    debug_log("old free torrents,ignore it:" + title)
                    continue

                id_status = RETRY if task['douban_id'] == "" and task['imdb_id'] == "" else OK
                t_rss = RSS("", t_page.site['name'], download_link,
                            details, title, task['douban_id'], task['imdb_id'], "", 0, id_status)
                if t_rss.HASH == "":
                    exec_log("cann't get hash,ignore it:" + title)
                    continue
                if not t_rss.insert():
                    exec_log("failed to insert rss:{}|{}|{}".format(t_rss.HASH, t_rss.rss_name, t_rss.name))
                    continue
                    
                add_status = TO_BE_ADD if task['auto'] else MANUAL
                t_torrent = MyTorrent(torrent=None, rss=t_rss, add_status=add_status)

                if task['douban_link'] != "":
                    t_torrent.douban_link = task['douban_link']
                if task['douban_score'] != "":
                    t_torrent.douban_score = task['douban_score']
                if task['imdb_link'] != "":
                    t_torrent.imdb_link = task['imdb_link']
                if task['imdb_score'] != "":
                    t_torrent.imdb_score = task['imdb_score']

                debug_log("free   torrent:" + t_torrent.HASH)
                exec_log("free    torrent:" + title)
                self.append_list(t_torrent)
        return True

    def request_rss(self, rss_name="", time_interval=-2):
        
        debug_log("request rss:{}::{}".format(rss_name, time_interval))
        for site in g_config.rss_list:
            if rss_name.lower() == site.get("name").lower() \
                    or (site.get('time_interval') != 0 and time_interval % site.get('time_interval') == 0):
                rss_name = site.get('name')
                wait_free = True if site.get('wait_free') == 1 else False
                rss_url = site.get('url')
            else:
                continue

            rss_log("==========begin {}==============".format(rss_name.ljust(10, ' ')))
            parser = None
            try:
                parser = feedparser.parse(rss_url)
                t_entries = parser.entries
            except Exception as err:
                print(err)
                print(parser)
                exec_log("failed to feedparser:" + rss_url)
                return False
            for t_entry in t_entries:
                try:
                    title = t_entry.title
                    torrent_hash = t_entry.id
                    detail = t_entry.links[0].href
                    download_link = t_entry.links[1].href
                except Exception as err:
                    print(err)
                    print(t_entry)
                    error_log("error to get entry:")
                    continue

                rss_log(f"{title}")

                if RSS.old_rss(torrent_hash, rss_name):
                    rss_log("old rss:"+title)
                    continue
                # if not t_rss.filter_by_keywords(): continue
                to_be_downloaded_flag = to_be_downloaded(rss_name, title)
                if to_be_downloaded_flag == IGNORE_DOWNLOAD:
                    rss_log("ignore it:"+title)
                    continue
                add_status = TO_BE_ADD if to_be_downloaded_flag == AUTO_DOWNLOAD else MANUAL

                t_summary = ""
                try:
                    t_summary = BeautifulSoup(t_entry.summary, 'lxml').get_text()
                except Exception as err:
                    print(f"{title}:")
                    print(err)
                    pass
                return_code, douban_id, imdb_id = Info.get_from_summary(t_summary)

                title = title.replace('|', '')
                id_status = OK if douban_id != "" or imdb_id != "" else RETRY
                t_rss = RSS(torrent_hash, rss_name, download_link, detail, title, douban_id, imdb_id, "", 0, id_status)
                
                if not t_rss.insert():  # 记录插入rss数据库
                    error_log("failed to insert into rss:{}|{}".format(rss_name, torrent_hash))
                    continue
                t_torrent = MyTorrent(None, t_rss, add_status)

                if not wait_free:
                    exec_log("new rss tobeadd:" + t_torrent.get_compiled_name())
                    exec_log("               :" + detail)
                    exec_log("               :{}/{}|{}/{}|{}|{}|{}|{}".format(t_rss.douban_id,
                                                                              t_rss.imdb_id,
                                                                              t_rss.douban_score,
                                                                              t_rss.imdb_score,
                                                                              t_rss.type,
                                                                              t_rss.nation,
                                                                              t_rss.movie_name,
                                                                              t_rss.director))
                    self.append_list(t_torrent)
                else:
                    rss_log("               :{}/{}|{}/{}|{}|{}|{}|{}".format(t_rss.douban_id,
                                                                             t_rss.imdb_id,
                                                                             t_rss.douban_score,
                                                                             t_rss.imdb_score,
                                                                             t_rss.type,
                                                                             t_rss.nation,
                                                                             t_rss.movie_name,
                                                                             t_rss.director))

            # end for Items
        return True
            
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
            error_log("invalid arg mList=" + ' '.join(m_list))
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
                error_log("invalid arg mList=" + m_list[0])
                return ""

        # qb，返回前刷新下状态
        if m_list[0].lower() == 'qb':
            self.check_torrents("QB")

        temp_list = []
        for i in range(len(self.torrent_list)):
            if self.torrent_list[i].client in t_client_list:
                torrent = self.torrent_list[i]
                temp_list.append(torrent.to_dict())
        return json.dumps(temp_list)


    def handle_bookmark(self,request):
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
                self.del_torrent("QB",HASH)
            return reply
        elif action == "search":
            reply = Torrents.search_bookmarks(request)
            

    @staticmethod
    def query_all_bookmarks():
        temp_list = []
        results = select("select hash,name,rssname,title,downloadlink,detailurl,size,adddatetime,doubanid,imdbid,torrentid from bookmarks", None)
        for result in results:
            HASH = result[0]
            name = result[1]
            rss_name = result[2]
            title = result[3]
            download_link = result[4]
            detail_url = result[5]
            size = result[6]
            add_datetime = result[7]
            douban_id = result[8]
            imdb_id = result[9]
            torrent_id = result[10]
            if douban_id == "" and imdb_id == "":
                rss = RSS(HASH,rss_name,download_link,detail_url,title,douban_id,imdb_id,add_datetime,size)
            else:
                rss = RSS(HASH,rss_name,download_link,detail_url,title,douban_id,imdb_id,add_datetime,size,OK)
            my_torrent = MyTorrent(None,rss,BOOKMARK)
            temp_list.append(my_torrent.to_dict())
        return json.dumps(temp_list)

    @staticmethod
    def search_bookmarks(request):
        # by douban_id and imdb_id
        douban_id = request.get("douban_id", "")
        imdb_id = request.get("imdb_id", "")
        temp_list = []
        if douban_id != "":
            sql = "select hash,name,rssname,title,downloadlink,detailurl,size,adddatetime,doubanid,imdbid,torrentid from bookmarks where doubanid=%s"
            results = select(sql, (douban_id,))
            if results is not None:
                for result in results:
                    HASH = result[0]
                    name = result[1]
                    rss_name = result[2]
                    title = result[3]
                    download_link = result[4]
                    detail_url = result[5]
                    size = result[6]
                    add_datetime = result[7]
                    douban_id = result[8]
                    imdb_id = result[9]
                    torrent_id = result[10]
                    rss = RSS(HASH,rss_name,download_link,detail_url,title,douban_id,imdb_id,add_datetime,size,OK)
                    my_torrent = MyTorrent(None,rss,BOOKMARK)
                    temp_list.append(my_torrent.to_dict())
        elif imdb_id != "":
            sql = "select hash,name,rssname,title,downloadlink,detailurl,size,adddatetime,doubanid,imdbid,torrentid from bookmarks where imdbid=%s"
            results = select(sql, (imdb_id,))
            if results is not None:
                for result in results:
                    HASH = result[0]
                    name = result[1]
                    rss_name = result[2]
                    title = result[3]
                    download_link = result[4]
                    detail_url = result[5]
                    size = result[6]
                    add_datetime = result[7]
                    douban_id = result[8]
                    imdb_id = result[9]
                    torrent_id = result[10]
                    rss = RSS(HASH,rss_name,download_link,detail_url,title,douban_id,imdb_id,add_datetime,size,OK)
                    my_torrent = MyTorrent(None,rss,BOOKMARK)
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
                    error_log(f"set_info之后，仍查询不到info表信息:{torrent.name}|{douban_id}|{imdb_id}")
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
            exec_log("failed to split:" + request_str)
            return "error requeststr:" + request_str
        debug_log("to set_cateory {}|{}|{}".format(t_client, t_hash, t_category))
        client = PTClient(t_client)
        if not client.connect():
            exec_log("failed to connect " + t_client)
            return "failed to connect "+t_client
        if client.set_category(t_hash, t_category):
            mytorrent = self.get_torrent(t_client, t_hash)
            compiled_name = mytorrent.get_compiled_name() if mytorrent is not None else "未找到torrent"
            exec_log(f"set_category:{compiled_name}|{t_category}")
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
            exec_log("failed to split:" + request_str)
            return "error requeststr:" + request_str
        debug_log("to del {}|{}".format(t_client, t_hash))
        t_is_delete_file = (t_is_delete_file_str.lower() == "true")
        if self.get_torrent("QB", t_hash) != None:
            return self.del_torrent(t_client, t_hash, t_is_delete_file)
        # 尝试从bookmarks表中删除
        if delete("delete from bookmarks where hash=%s",(t_hash,)):
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
            exec_log("failed to split:" + request_str)
            return "error requeststr:" + request_str
        debug_log("to act {}|{}|{}".format(t_client, t_hash, t_action))
        
        if t_action == "add":
            return self.add_torrent(t_client, t_hash)

        # TODO
        index = self.get_torrent_index(t_client, t_hash)
        if index == -1:
            return "not find match torrent"
        if t_action == "start":
            self.torrent_list[index].start()
        elif t_action == "stop":
            self.torrent_list[index].stop()
        exec_log(f"{t_action} :{self.torrent_list[index].get_compiled_name()}")
        return "Success"

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
            exec_log("failed to split:" + request_str)
            return "failed:error requeststr:" + request_str
        debug_log("to movie {}|{}".format(douban_id, imdb_id))
        
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
        client|hash
        """
        try:
            t_client, t_hash = request_str.split('|', 1)
        except Exception as err:
            print(err)
            exec_log("failed to split:" + request_str)
            return "error requeststr:" + request_str
        debug_log("get_tracker_message {}|{}".format(t_client, t_hash))
        
        torrent = self.get_torrent(t_client, t_hash)
        return torrent.tracker_message if torrent is not None else "failed"
