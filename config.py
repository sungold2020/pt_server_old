import json
import platform
from log import *


class Config:
    def __init__(self):
        self.sys_config = None    # 系统配置
        self.site_config = None   # pt-site
        self.rss_config = None
        self.os_type = platform.system()

    @property
    def CHECK_DISK_LIST(self):
        return self.sys_config.get("CHECK_DISK_LIST", []) if self.sys_config is not None else []
    @property
    def NUMBEROFDAYS(self):  # default 3
        return self.sys_config.get("NUMBEROFDAYS", 3) if self.sys_config is not None else 3
    @property
    def UPLOADTHRESHOLD(self):  # default 0.03
        return self.sys_config.get("UPLOADTHRESHOLD", 0.03) if self.sys_config is not None else 0.03
    @property
    def TORRENT_LIST_BACKUP(self):
        return self.sys_config.get("TORRENT_LIST_BACKUP", "") if self.sys_config is not None else ""
    @property
    def TRACKER_LIST_BACKUP(self):
        return self.sys_config.get("TRACKER_LIST_BACKUP", "") if self.sys_config is not None else ""
    @property
    def IGNORE_FILE(self):
        return self.sys_config.get("IGNORE_FILE", "") if self.sys_config is not None else ""
    @property
    def TR_LOGIN(self):
        return self.sys_config.get("TR_LOGIN", None) if self.sys_config is not None else None
    @property
    def QB_LOGIN(self):
        return self.sys_config.get("QB_LOGIN", None) if self.sys_config is not None else None
    @property
    def PTPORT(self):  # default 12345
        return self.sys_config.get("PTPORT", 12345) if self.sys_config is not None else 12345
    @property
    def DB_LOGIN(self):
        return self.sys_config.get("DB_LOGIN", None) if self.sys_config is not None else None
    @property
    def DOUBAN_URL(self):
        return self.sys_config.get("DOUBAN_URL", "") if self.sys_config is not None else ""
    @property
    def DOUBAN_SEARCH_URL(self):
        return self.sys_config.get("DOUBAN_SEARCH_URL", "") if self.sys_config is not None else ""
    @property
    def DOUBAN_VIEWED_URL(self):
        return self.sys_config.get("DOUBAN_VIEWED_URL", "") if self.sys_config is not None else ""
    @property
    def DOUBAN_COOKIE(self):
        return self.sys_config.get("DOUBAN_COOKIE", "") if self.sys_config is not None else ""
    @property
    def USER_AGENT(self):
        return self.sys_config.get("USER_AGENT", "") if self.sys_config is not None else ""
    @property
    def ExecLogFile(self):
        return self.sys_config.get("ExecLogFile", "") if self.sys_config is not None else ""
    @property
    def DebugLogFile(self):
        return self.sys_config.get("DebugLogFile", "") if self.sys_config is not None else ""
    @property
    def ErrorLogFile(self):
        return self.sys_config.get("ErrorLogFile", "") if self.sys_config is not None else ""
    @property
    def INFO_LOG_FILE(self):
        return self.sys_config.get("INFO_LOG_FILE", "") if self.sys_config is not None else ""
    @property
    def RSS_LOG_FILE(self):
        return self.sys_config.get("RSS_LOG_FILE", "") if self.sys_config is not None else ""
    @property
    def DATABASE_LOG_FILE(self):
        return self.sys_config.get("DATABASE_LOG_FILE", "") if self.sys_config is not None else ""
    @property
    def PTSITE_LOG_FILE(self):
        return self.sys_config.get("PTSITE_LOG_FILE", "") if self.sys_config is not None else ""
    @property
    def MOVIE_LOG_FILE(self):
        return self.sys_config.get("MOVIE_LOG_FILE", "") if self.sys_config is not None else ""
    @property
    def SOCKET_LOG_FILE(self):
        return self.sys_config.get("SOCKET_LOG_FILE", "") if self.sys_config is not None else ""
    @property
    def DOWNLOAD_FOLDER(self):
        return self.sys_config.get("DOWNLOAD_FOLDER", "") if self.sys_config is not None else ""
    @DOWNLOAD_FOLDER.setter
    def DOWNLOAD_FOLDER(self, download_folder):
        if self.sys_config is not None:
            self.sys_config['DOWNLOAD_FOLDER'] = download_folder
    @property
    def TO_BE_PATH(self):
        return self.sys_config.get("TO_BE_PATH", "") if self.sys_config is not None else ""
    @TO_BE_PATH.setter
    def TO_BE_PATH(self, TO_BE_PATH):
        if self.sys_config is not None:
            self.sys_config['DOWNLOAD_FOLDER'] = TO_BE_PATH
    @property
    def TR_KEEP_DIR(self):
        return self.sys_config.get("TR_KEEP_DIR", "") if self.sys_config is not None else ""
    @TR_KEEP_DIR.setter
    def TR_KEEP_DIR(self, TR_KEEP_DIR):
        if self.sys_config is not None:
            self.sys_config['TR_KEEP_DIR'] = TR_KEEP_DIR
    @property
    def QB_BACKUP_DIR(self):
        return self.sys_config.get("QB_BACKUP_DIR", "") if self.sys_config is not None else ""
    @QB_BACKUP_DIR.setter
    def QB_BACKUP_DIR(self, QB_BACKUP_DIR):
        if self.sys_config is not None:
            self.sys_config['QB_BACKUP_DIR'] = QB_BACKUP_DIR
    @property
    def TR_BACKUP_DIR(self):
        return self.sys_config.get("TR_BACKUP_DIR", "") if self.sys_config is not None else ""
    @property
    def QB_TORRENTS_BACKUP_DIR(self):
        return self.sys_config.get("QB_TORRENTS_BACKUP_DIR", "") if self.sys_config is not None else ""
    @QB_TORRENTS_BACKUP_DIR.setter
    def QB_TORRENTS_BACKUP_DIR(self, QB_TORRENTS_BACKUP_DIR):
        if self.sys_config is not None:
            self.sys_config['QB_TORRENTS_BACKUP_DIR'] = QB_TORRENTS_BACKUP_DIR
    @property
    def TR_TORRENTS_BACKUP_DIR(self):
        return self.sys_config.get("TR_TORRENTS_BACKUP_DIR", "") if self.sys_config is not None else ""
    @TR_TORRENTS_BACKUP_DIR.setter
    def TR_TORRENTS_BACKUP_DIR(self, TR_TORRENTS_BACKUP_DIR):
        if self.sys_config is not None:
            self.sys_config['TR_TORRENTS_BACKUP_DIR'] = TR_TORRENTS_BACKUP_DIR
    @property
    def TORRENTS_DIR(self):
        return self.sys_config.get("TORRENTS_DIR","") if self.sys_config is not None else ""
    @TORRENTS_DIR.setter
    def TORRENTS_DIR(self, TORRENTS_DIR):
        if self.sys_config is not None:
            self.sys_config['TORRENTS_DIR'] = TORRENTS_DIR
    @property
    def BACKUP_DAILY_SHELL(self):
        return self.sys_config.get("BACKUP_DAILY_SHELL","") if self.sys_config is not None else ""
    @property
    def BACKUP_MONTHLY_SHELL(self):
        return self.sys_config.get("BACKUP_MONTHLY_SHELL","") if self.sys_config is not None else ""
    @property
    def rss_list(self):
        return self.rss_config
    @property
    def site_list(self):
        return self.site_config

    def read_sys_config(self, sys_config_file):
        fo = open(sys_config_file)
        try:
            self.sys_config = json.load(fo)
        except Exception as err:
            print(err)
            error_log(f"failed to read sys_config from {sys_config_file}")
            return False

        return True

    def read_site_config(self, site_config_file):
        fo = open(site_config_file)
        try:
            self.site_config = json.load(fo)
        except Exception as err:
            print(err)
            error_log(f"failed to read sys_config from {site_config_file}")
            return False
        for site in self.site_list:
            if site.get('auto', None) is not None:
                site.get('auto')['free'] = True if site.get('auto').get('free', 0) == 1 else False
            if site.get('manual', None) is not None:
                site.get('manual')['free'] = True if site.get('manual').get('free', 0) == 1 else False

        return True

    def read_rss_config(self, rss_config_file):
        fo = open(rss_config_file)
        try:
            self.rss_config = json.load(fo)
        except Exception as err:
            print(err)
            error_log(f"failed to read sys_config from {rss_config_file}")
            return False
        for site in self.rss_config:
            site['wait_free'] = True if site.get('wait_free', 0) == 1 else False

        return True

    def load_sys_config(self):
        if g_config.read_sys_config("config/sys.json"):
            return "Success"
        else:
            return "failed"

    def load_rss_config(self):
        if g_config.read_rss_config("config/rss.json"):
            return "Success"
        else:
            return "failed"

    def load_site_config(self):
        if g_config.read_site_config("config/site.json"):
            return "Success"
        else:
            return "failed"

    def rss_site(self, rss_name):
        for site in self.rss_list:
            if rss_name.lower() == site.get("name").lower():
                return site
        return None



g_config = Config()
if not (g_config.read_sys_config("config/sys.json")
        and g_config.read_rss_config("config/rss.json")
        and g_config.read_site_config("config/site.json")):
    print("error")
    exit()

