#!/usr/bin/python3
# coding=utf-8
import transmissionrpc
import qbittorrentapi
from torrent import Torrent
from rss import *
from torrent_info import *


class PTClient:
    def __init__(self, client_type=""):
        self._type = client_type
        self.client = None
        self.error_string = ""

    @property
    def type(self):
        return self._type

    @type.setter
    def type(self, client_type):
        if client_type != "QB" and client_type == "TR":
            Log.error_log("unknown type:" + client_type)
            return
        self._type = client_type

    @property
    def down_speed(self):   # unit: KB/s
        if self.client is None:
            if not self.connect():
                return -1
        if self.type == "QB":
            return self.client.transfer.info['dl_info_speed'] / 1024
        elif self.type == "TR":
            return self.client.session_stats().downloadSpeed / 1024
        else:
            return -1

    @property
    def up_speed(self):   # unit: KB/s
        if self.client is None:
            if not self.connect():
                return -1
        if self.type == "QB":
            return self.client.transfer.info['up_info_speed'] / 1024
        elif self.type == "TR":
            return self.client.session_stats().uploadSpeed / 1024
        else:
            return -1

    def connect(self):
        try:
            if self.type == "TR":
                self.client = transmissionrpc.Client(SysConfig.TR_LOGIN['host'],
                                                     port=SysConfig.TR_LOGIN['port'],
                                                     user=SysConfig.TR_LOGIN['username'],
                                                     password=SysConfig.TR_LOGIN['password'])
            elif self.type == "QB":
                self.client = qbittorrentapi.Client(host=SysConfig.QB_LOGIN['host_port'],
                                                    username=SysConfig.QB_LOGIN['username'],
                                                    password=SysConfig.QB_LOGIN['password'])
                self.client.auth_log_in()
            else:
                return False
        except Exception as err:
            print(err)
            Log.error_log("failed to connect to " + self.type)
            return False
        else:
            Log.debug_log("connect to  " + self.type)
            return True

    def get_all_torrents(self):
        try:
            if self.type == "QB":
                return map(lambda x: Torrent(self.type, x), self.client.torrents_info())
            elif self.type == "TR":
                return map(lambda x: Torrent(self.type, x), self.client.get_torrents())
            else:
                return []
        except Exception as err:
            print(err)
            return []

    def get_torrent(self, torrent_hash=None):
        if torrent_hash is None or torrent_hash == "":
            Log.error_log("hash is none or empty")
            return None
        try:
            if self.type == "QB":
                for torrent in self.client.torrents_info():
                    if torrent.hash == torrent_hash:
                        return Torrent(self.type, torrent)
                return None
            elif self.type == "TR":
                # TODO
                return None
            else:
                return None
        except Exception as err:
            print(err)
            return None

    def add_torrent(self, torrent_hash="", download_link="", torrent_file="",
                    download_dir=None, is_paused=True, is_root_folder=True, is_skip_checking=False, category=None):
        """
        1,如果torrent_file为空，则根据hash寻找对应的文件或者根据download_link进行重新下载:w
            HASH为空，或者HASH对应的种子文件不存在，则重新下载
        2,加入pt客户端 
        """
        if download_link == "" and torrent_file == "" and torrent_hash == "":
            Log.error_log("empty download link or torrent file")
            self.error_string = "empty download link or torrent file"
            return None

        # 1，获取及校验torrent_file
        if torrent_file == "":
            torrent_file = os.path.join(TORRENTS_DIR, torrent_hash + '.torrent')
            if torrent_hash == "" or not os.path.exists(torrent_file):
                torrent_info = RSS.download_torrent_file(download_link)
                if torrent_info is None:
                    self.error_string = f"下载并获取种子信息失败:{download_link}"
                    Log.exec_log(self.error_string)
                    return None
                torrent_hash = torrent_info.info_hash
                torrent_file = os.path.join(TORRENTS_DIR, torrent_hash + '.torrent')
        if not os.path.exists(torrent_file):
            self.error_string = f"can't find torrent:{torrent_file}"
            Log.exec_log(self.error_string)
            return None

        torrent_file = os.path.abspath(torrent_file)  # TR需要绝对路径的torrent文件
        try:
            if self.type == "TR":
                Log.debug_log("add torrent_file to tr:" + torrent_file)
                return Torrent(self.type,
                               self.client.add_torrent(torrent_file,
                                                       download_dir=download_dir,
                                                       paused=is_paused))
            elif self.type == "QB":
                t_return = self.client.torrents_add(urls=download_link,
                                                    torrent_files=torrent_file,
                                                    save_path=download_dir,
                                                    paused=is_paused,
                                                    category=category,
                                                    is_skip_checking=is_skip_checking,
                                                    is_root_folder=is_root_folder)
                if t_return != "Ok.":
                    self.error_string = "failed to exec:torrents_add"
                    return None
                time.sleep(10)
                return self.get_torrent(torrent_hash)
            else:
                return None
        except Exception as err:
            print(err)
            self.error_string = str(err)
            return None

    def del_torrent(self, torrent_hash, is_delete_file=False):
        print(self.type + '|' + torrent_hash)
        if torrent_hash is None or torrent_hash == "":
            return False
        if torrent_hash == "":
            return False
        try:
            if self.type == "TR":
                return self.client.remove_torrent(torrent_hash, delete_data=is_delete_file)
            elif self.type == "QB":
                self.client.torrents_delete(is_delete_file, torrent_hash)
            else:
                return False
        except Exception as err:
            print(err)
            self.error_string = str(err)
            return False
        else:
            return True

    def shutdown(self):
        try:
            if self.type == "QB":
                self.client.app_shutdown()
            elif self.type == "TR":
                return False  # TODO
            else:
                return False
            return True
        except Exception as err:
            print(err)
            Log.error_log("failed to shutdown " + self.type)
            return False

    def start(self):
        if self.type == "QB":
            if os.system("/usr/bin/qbittorrent &") == 0:
                Log.exec_log("success to start qb")
                return True
            else:
                Log.exec_log("failed to start qb")
                return False
        elif self.type == "TR":
            # TODO
            pass
        else:
            pass

    def restart(self):
        if not (self.connect() and self.shutdown()):
            return False
        time.sleep(300)
        if not self.start():
            return False
        return True

    def set_category(self, torrent_hash, category):
        if self.type == "QB":
            try:
                self.client.torrents_setCategory(category, torrent_hash)
            except Exception as err:
                print(err)
                return False
            else:
                return True
        elif self.type == "TR":
            return False
        else:
            return False

    @staticmethod
    def get_up_speed(client_type):
        client = PTClient(client_type)
        if not client.connect():
            return -1
        return client.up_speed
