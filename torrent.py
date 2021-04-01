
import time
import os

TRACKER_UNKNOWN = -2
TRACKER_ERROR = -1
TRACKER_NOT_WORK = 0
TRACKER_WORKING = 1


class Torrent:
    def __init__(self, client="QB", torrent=None):
        self.client = client
        self.torrent = torrent

        self.date_data = []
        # tCurrentTime = datetime.datetime.now()
        # tToday = tCurrentTime.strftime('%Y-%m-%d')
        # self.date_data.append({'date':tToday,'data':self.uploaded})

        # tFiles = []            #存储文件的数组,#名字,大小，完成率
        self.dir_name = ""  # 种子目录名称
        self.root_folder = ""  # 种子保存的路径所在根目录

        self.error_string = ""

    def print(self):
        print(self.hash)
        print(self.name)
        print(self.progress)
        print(self.status)
        print(self.category)
        print(self.tags)
        print(self.save_path)
        print(self.add_datetime)
        print(self.tracker)
        print(self.uploaded)
        print(self.total_size)
        print(self.tracker_status)
        print(self.torrent_status)

    def update(self) -> bool:
        """

        :return:
        """
        self.torrent.update()

    @property
    def hash(self):
        if self.torrent is None:
            return ""
        if self.client == "TR":
            return self.torrent.hashString
        elif self.client == "QB":
            return self.torrent.hash
        else:
            return ""

    @property
    def name(self):
        if self.torrent is None:
            return ""
        return self.torrent.name

    @property
    def progress(self):
        if self.torrent is None:
            return 0
        if self.client == "TR":
            return int(self.torrent.percentDone * 100)
        elif self.client == "QB":
            return int(self.torrent.progress * 100)
        else:
            return 0

    @property
    def status(self):
        if self.torrent is None:
            return ""
        if self.client == "TR":
            if self.torrent.status[0:4].lower() == "stop":
                return "STOP"
            else:
                return "GOING"
        elif self.client == "QB":
            if self.torrent.state[0:5].lower() == "pause":
                return "STOP"
            else:
                return "GOING"
        else:
            return "error"

    @property
    def category(self):
        if self.torrent is None:
            return ""
        if self.client == "TR":
            return ""
        elif self.client == "QB":
            return self.torrent.category
        else:
            return ""

    @property
    def tags(self):
        if self.torrent is None:
            return ""
        if self.client == "TR":
            return ""
        elif self.client == "QB":
            return self.torrent.tags
        else:
            return ""

    @property
    def save_path(self):
        if self.torrent is None:
            return ""
        if self.client == "TR":
            return self.torrent.downloadDir
        elif self.client == "QB":
            return self.torrent.save_path
        else:
            return ""

    @property
    def add_datetime(self):
        if self.torrent is None:
            return ""
        if self.client == "TR":
            return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(self.torrent.addedDate))
        elif self.client == "QB":
            return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(self.torrent.added_on))
        else:
            return ""

    @property
    def tracker(self):
        if self.torrent is None:
            return ""
        if self.client == "TR":
            return self.torrent.trackers[0]['announce']
        elif self.client == "QB":
            return self.torrent.tracker
        else:
            return ""

    @property
    def uploaded(self):
        if self.torrent is None:
            return 0
        if self.client == "TR":
            return self.torrent.uploadedEver
        elif self.client == "QB":
            return self.torrent.uploaded
        else:
            return 0

    @property
    def total_size(self):
        if self.torrent is None:
            return 0
        if self.client == "TR":
            return self.torrent.totalSize
        elif self.client == "QB":
            return self.torrent.total_size
        else:
            return 0

    @property
    def tracker_status(self):
        if self.torrent is None:
            return TRACKER_UNKNOWN
        if self.client == "QB":
            try:
                trackers = self.torrent.trackers
            except Exception as err:
                print(err)
                return TRACKER_ERROR
            else:
                for tracker in trackers:
                    if tracker.get('url').startswith('http'):
                        if tracker.get('status') != 2:
                            return TRACKER_NOT_WORK
                        else:
                            return TRACKER_WORKING
                return TRACKER_NOT_WORK
        elif self.client == "TR":
            # TODO
            return TRACKER_NOT_WORK
        else:
            return TRACKER_NOT_WORK

    @property
    def tracker_message(self):
        if self.torrent is None:
            return ""
        if self.client == "QB":
            try:
                for tracker in self.torrent.trackers:
                    if tracker.get('url').startswith('http'):
                        return tracker.get('msg')
            except Exception as err:
                print(err)
                return ""
        elif self.client == "TR":
            # TODO
            return ""
        else:
            return ""

    @property
    def torrent_status(self):
        if self.torrent is None:
            return "N/A"
        if self.status == "STOP":
            return "STOP"
        elif self.tracker_status == TRACKER_WORKING:
            return "GOING"
        else:
            return "ERROR"

    @property
    def files(self):
        if self.torrent is None:
            return []
        t_files = []
        if self.client == "TR":
            t_torrent_files = self.torrent.files()
            for i in range(len(t_torrent_files)):
                t_name = t_torrent_files[i]['name']
                t_size = t_torrent_files[i]['size']
                t_progress = int((t_torrent_files[i]['completed'] / t_torrent_files[i]['size']) * 100)
                t_files.append({'name': t_name, 'size': t_size, 'progress': t_progress})
        elif self.client == "QB":
            try:
                t_torrent_files = self.torrent.files
            except Exception as err:
                print(err)
                return []
            for i in range(len(t_torrent_files)):
                t_name = t_torrent_files[i].name
                t_size = t_torrent_files[i].size
                t_progress = int(t_torrent_files[i].progress * 100)
                t_files.append({'name': t_name, 'size': t_size, 'progress': t_progress})
        else:
            pass
        return t_files

    @property
    def upload_limit(self):
        if self.torrent is None:
            return 0
        if self.client == "TR":
            return self.torrent.uploadLimit
        elif self.client == "QB":
            return self.torrent.up_limit
        else:
            self.error_string = "unknown client type"
            return -1

    @upload_limit.setter
    def upload_limit(self, upload_limit):
        self.set_upload_limit(upload_limit)

    def set_upload_limit(self, upload_limit):
        """
        -1或者None代表解除限制，其他设为具体的限制值(Unit:KB/S)
        """
        if self.torrent is None:
            self.error_string = "torrent is None"
            return False
        if self.client == "TR":
            if upload_limit == -1:  # TR中None代表解除限制，所以要把-1转换为None 
                upload_limit = None
            self.torrent.upload_limit = upload_limit
            return True
        elif self.client == "QB":   # QB中-1代表解除限制，所以要把None转换为-1
            if upload_limit is None:
                upload_limit = -1
            self.torrent.set_upload_limit(upload_limit*1024)
            return True
        else:
            self.error_string = "unknown client type"
            return False

    def stop(self):
        if self.torrent is None:
            self.error_string = "torrent does not exist"
            return False
        if self.client == "TR":
            try:
                self.torrent.stop()
            except Exception as err:
                print(err)
                return False
            else:
                return True
        elif self.client == "QB":
            try:
                self.torrent.pause()
            except Exception as err:
                print(err)
                return False
            else:
                return True
        else:
            return False

    def pause(self):
        if self.torrent is None:
            self.error_string = "torrent does not exist"
            return False
        try:
            if self.client == "QB":
                self.torrent.pause()
            else:
                self.torrent.stop()
        except Exception as err:
            print(err)
            return False
        else:
            return True

    def resume(self):
        if self.torrent is None:
            self.error_string = "torrent does not exist"
            return False
        try:
            if self.client == "QB":
                self.torrent.resume()
            else:
                self.torrent.start()
        except Exception as err:
            print(err)
            return False
        else:
            return True

    def set_category(self, category=""):
        if self.torrent is None:
            return False
        if self.client == "TR":
            return False
        elif self.client == "QB":
            try:
                self.torrent.set_category(category)
            except Exception as err:
                print(err)
                return False
            else:
                return True
        else:
            return False

    def set_tags(self, tags):
        if self.torrent is None:
            return False
        if self.client == "TR":
            return False
        elif self.client == "QB":
            try:
                self.torrent.remove_tags()
                self.torrent.add_tags(tags)
            except Exception as err:
                print(err)
                return False
            else:
                return True
        else:
            return False

    def set_save_path(self, save_path):
        if self.torrent is None:
            self.error_string = "torrent is None"
            return False
        if self.client == "TR":
            try:
                self.torrent.locate_data(save_path)
                return True
            except Exception as err:
                print(err)
                return False
        elif self.client == "QB":
            # TODO   QB待实现
            self.error_string = "QB未实现该接口"
            return False
        else:
            self.error_string = "unknown client type"
            return False

    def check_files(self, is_new_day):
        """
        检查文件是否存在及大小是否一致。
        mIsNewDay的话，完整检查。否则仅检查QB的类别为"下载"及"刷上传"的种子的第一个文件
        """
        if self.torrent is None:
            self.error_string = "torrent does not exist"
            return False
        t_files = self.files
        if is_new_day:
            for i in range(len(t_files)):
                if t_files[i]['progress'] != 100:
                    continue
                t_full_file_name = os.path.join(self.save_path, t_files[i]['name'])
                if not os.path.isfile(t_full_file_name):
                    self.error_string = f"file:{t_full_file_name} does not exist"
                    return False
                if t_files[i]['size'] != os.path.getsize(t_full_file_name):
                    self.error_string = (t_full_file_name + " file size error. torrent size:" + str(t_files[i]['size']))
                    return False
        else:  # 不是新的一天，对于非转移/保种/低上传分类的种子，仅检查第一个下载完成的文件是否存在
            if self.client == "TR":
                pass
            if self.category == "下载" or self.category == "刷上传":
                # DebugLog("check torrent file:"+self.Name+"::"+self.save_path)
                for i in range(len(t_files)):
                    if t_files[i]['progress'] != 100:
                        continue
                    t_full_file_name = os.path.join(self.save_path, t_files[0]['name'])
                    if not os.path.isfile(t_full_file_name):
                        self.error_string = (t_full_file_name + " does not exist")
                        return False
                    else:
                        break
        return True

    def is_low_upload(self, number_of_days, upload_threshold):
        # 包括今天在内，至少要有NUMBEROFDAYS+1天数据
        t_length = len(self.date_data)
        if t_length < number_of_days + 1:
            return False

        # 从尾部开始循环，尾部日期是最新的
        i = t_length - 1
        t_days = 0
        while i > 1 and t_days < number_of_days:
            t_delta_data = (self.date_data[i])['data'] - (self.date_data[i - 1])['data']
            if t_delta_data / self.total_size < upload_threshold:
                t_days += 1
            else:
                return False  # 有一天高于阈值就退出
            i -= 1

        return True

    def is_root_folder(self):
        t_files = self.files

        # 如何判断是否创建了子文件夹IsRootFolder，所有的文件都包含了目录，而且是一致的。
        t_sub_dir_name = ""
        for i in range(len(t_files)):
            t_index = (t_files[i]['name']).find('/')
            if t_index == -1:
                return False
            if t_sub_dir_name == "":
                t_sub_dir_name = (t_files[i]['name'])[0:t_index]
            else:
                if (t_files[i]['name'])[0:t_index] != t_sub_dir_name:
                    return False

        return True

    def get_last_day_upload_traffic(self) -> int:
        """
        获取最后一天的上传数据
        :return:
        """
        if len(self.date_data) == 0:
            return 0

        elif len(self.date_data) == 1:
            return self.date_data[0]['data']
        else:
            return self.date_data[-1]['data'] - self.date_data[-2]['data']
