import json
from log import *


class SysConfig:
    CHECK_DISK_LIST = []
    NUMBEROFDAYS = 3
    UPLOADTHRESHOLD = 0.03
    TORRENT_LIST_BACKUP = ""
    TRACKER_LIST_BACKUP = ""
    IGNORE_FILE = ""
    TR_LOGIN = None
    QB_LOGIN = None
    PTPORT = 12345
    DB_LOGIN = {"username": "dummy", "password": "moonbeam", "db_name": "db_movies"}
    DOUBAN_URL = ""
    DOUBAN_SEARCH_URL = ""
    DOUBAN_VIEWED_URL = ""
    DOUBAN_COOKIE = ""
    USER_AGENT = ""
    DOWNLOAD_FOLDER = ""            # 支持setter
    TO_BE_PATH = ""                # 支持setter
    TR_KEEP_DIR = ""               # 支持setter
    QB_BACKUP_DIR = ""           # 支持setter
    TR_BACKUP_DIR = ""            # 支持setter
    QB_TORRENTS_BACKUP_DIR = ""    # 支持setter
    TR_TORRENTS_BACKUP_DIR = ""      # 支持setter
    TORRENTS_DIR = ""               # 支持setter
    BACKUP_DAILY_SHELL = ""
    BACKUP_MONTHLY_SHELL = ""
    SITE_LIST = []

    @staticmethod
    def load_sys_config(sys_config_file: str = "config/sys.json") -> bool:
        """

        :param sys_config_file:
        :return:
        """
        fo = open(sys_config_file)
        try:
            sys_config = json.load(fo)
        except Exception as err:
            print(err)
            Log.error_log(f"failed to read sys_config from {sys_config_file}")
            return False

        SysConfig.CHECK_DISK_LIST = sys_config.get('CHECK_DISK_LIST', [])
        if len(SysConfig.CHECK_DISK_LIST) == 0:
            Log.exec_log("CHECK_DISK_LIST is null")

        SysConfig.NUMBEROFDAYS = sys_config.get('NUMBEROFDAYS', 0)
        if SysConfig.NUMBEROFDAYS == 0:
            Log.exec_log("NUMBEROFDAYS is null, so set default 3")
        SysConfig.UPLOADTHRESHOLD = sys_config.get('UPLOADTHRESHOLD', 0)
        if SysConfig.UPLOADTHRESHOLD == 0:
            Log.exec_log("UPLOADTHRESHOLD is null, so set default 0.03")

        if sys_config.get('TORRENT_LIST_BACKUP', "") == "":
            Log.exec_log(f"TORRENT_LIST_BACKUP is null, keep no change:{SysConfig.TORRENT_LIST_BACKUP}")
        else:
            SysConfig.TORRENT_LIST_BACKUP = sys_config.get('TORRENT_LIST_BACKUP')

        if sys_config.get('TRACKER_LIST_BACKUP', "") == "":
            Log.exec_log(f"TRACKER_LIST_BACKUP is null, keep no change:{SysConfig.TRACKER_LIST_BACKUP}")
        else:
            SysConfig.TRACKER_LIST_BACKUP = sys_config.get('TRACKER_LIST_BACKUP')

        if sys_config.get('IGNORE_FILE', "") == "":
            Log.exec_log(f"IGNORE_FILE is null, keep no change:{SysConfig.IGNORE_FILE}")
        else:
            SysConfig.IGNORE_FILE = sys_config.get('IGNORE_FILE')

        if sys_config.get('TR_LOGIN', None) is None:
            Log.exec_log(f"TR_LOGIN is null, keep no change:{SysConfig.TR_LOGIN}")
        else:
            SysConfig.TR_LOGIN = sys_config.get('TR_LOGIN')

        if sys_config.get('QB_LOGIN', None) is None:
            Log.exec_log(f"QB_LOGIN is null, keep no change:{SysConfig.QB_LOGIN}")
        else:
            SysConfig.QB_LOGIN = sys_config.get('QB_LOGIN')

        if sys_config.get('DB_LOGIN', None) is None:
            Log.exec_log(f"DB_LOGIN is null, keep no change:{SysConfig.DB_LOGIN}")
        else:
            SysConfig.DB_LOGIN = sys_config.get('DB_LOGIN')

        if sys_config.get('PTPORT', 0) == 0:
            Log.exec_log(f"PTPORT is null, keep no change:{SysConfig.PTPORT}")
        else:
            SysConfig.PTPORT = sys_config.get('PTPORT')

        if sys_config.get('DOUBAN_URL', "") == "":
            Log.exec_log(f"DOUBAN_URL is null, keep no change:{SysConfig.DOUBAN_URL}")
        else:
            SysConfig.DOUBAN_URL = sys_config.get('DOUBAN_URL')

        if sys_config.get('DOUBAN_SEARCH_URL', "") == "":
            Log.exec_log(f"DOUBAN_SEARCH_URL is null, keep no change:{SysConfig.DOUBAN_SEARCH_URL}")
        else:
            SysConfig.DOUBAN_SEARCH_URL = sys_config.get('DOUBAN_SEARCH_URL')

        if sys_config.get('DOUBAN_VIEWED_URL', "") == "":
            Log.exec_log(f"DOUBAN_VIEWED_URL is null, keep no change:{SysConfig.DOUBAN_VIEWED_URL}")
        else:
            SysConfig.DOUBAN_VIEWED_URL = sys_config.get('DOUBAN_VIEWED_URL')

        if sys_config.get('DOUBAN_COOKIE', "") == "":
            Log.exec_log(f"DOUBAN_COOKIE is null, keep no change:{SysConfig.DOUBAN_COOKIE}")
        else:
            SysConfig.DOUBAN_COOKIE = sys_config.get('DOUBAN_COOKIE')

        if sys_config.get('USER_AGENT', "") == "":
            Log.exec_log(f"USER_AGENT is null, keep no change:{SysConfig.USER_AGENT}")
        else:
            SysConfig.USER_AGENT = sys_config.get('USER_AGENT')

        if sys_config.get('DOWNLOAD_FOLDER', "") == "":
            Log.exec_log(f"DOWNLOAD_FOLDER is null, keep no change:{SysConfig.DOWNLOAD_FOLDER}")
        else:
            SysConfig.DOWNLOAD_FOLDER = sys_config.get('DOWNLOAD_FOLDER')

        if sys_config.get('TO_BE_PATH', "") == "":
            Log.exec_log(f"TO_BE_PATH is null, keep no change:{SysConfig.TO_BE_PATH}")
        else:
            SysConfig.TO_BE_PATH = sys_config.get('TO_BE_PATH')

        if sys_config.get('TR_KEEP_DIR', "") == "":
            Log.exec_log(f"TR_KEEP_DIR is null, keep no change:{SysConfig.TR_KEEP_DIR}")
        else:
            SysConfig.TR_KEEP_DIR = sys_config.get('TR_KEEP_DIR')

        if sys_config.get('QB_BACKUP_DIR', "") == "":
            Log.exec_log(f"QB_BACKUP_DIR is null, keep no change:{SysConfig.QB_BACKUP_DIR}")
        else:
            SysConfig.QB_BACKUP_DIR = sys_config.get('QB_BACKUP_DIR')

        if sys_config.get('TR_BACKUP_DIR', "") == "":
            Log.exec_log(f"TR_BACKUP_DIR is null, keep no change:{SysConfig.TR_BACKUP_DIR}")
        else:
            SysConfig.TR_BACKUP_DIR = sys_config.get('TR_BACKUP_DIR')

        if sys_config.get('QB_TORRENTS_BACKUP_DIR', "") == "":
            Log.exec_log(f"QB_TORRENTS_BACKUP_DIR is null, keep no change:{SysConfig.QB_TORRENTS_BACKUP_DIR}")
        else:
            SysConfig.QB_TORRENTS_BACKUP_DIR = sys_config.get('QB_TORRENTS_BACKUP_DIR')

        if sys_config.get('TORRENTS_DIR', "") == "":
            Log.exec_log(f"TORRENTS_DIR is null, keep no change:{SysConfig.TORRENTS_DIR}")
        else:
            SysConfig.TORRENTS_DIR = sys_config.get('TORRENTS_DIR')

        if sys_config.get('BACKUP_DAILY_SHELL', "") == "":
            Log.exec_log(f"BACKUP_DAILY_SHELL is null, keep no change:{SysConfig.BACKUP_DAILY_SHELL}")
        else:
            SysConfig.BACKUP_DAILY_SHELL = sys_config.get('BACKUP_DAILY_SHELL')

            if sys_config.get('BACKUP_MONTHLY_SHELL', "") == "":
                Log.exec_log(f"BACKUP_MONTHLY_SHELL is null, keep no change:{SysConfig.BACKUP_MONTHLY_SHELL}")
            else:
                SysConfig.BACKUP_MONTHLY_SHELL = sys_config.get('BACKUP_MONTHLY_SHELL')
        return True

    @staticmethod
    def load_site_config(site_config_file: str = "config/site.json") -> bool:
        """

        :param site_config_file:
        :return:
        """
        fo = open(site_config_file)
        try:
            site_list = json.load(fo)
        except Exception as err:
            print(err)
            Log.error_log(f"failed to read sys_config from {site_config_file}")
            return False

        if len(site_list) is None:
            Log.error_log(f"there is no site")
            return False

        SysConfig.SITE_LIST = site_list
        return True
