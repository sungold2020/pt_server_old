#!/usr/bin/python3
# coding=utf-8
import datetime
import traceback
import os


class Log:

    INFO_LOG_FILE = "log/info.log"
    RSS_LOG_FILE = "log/rss.log"
    DATABASE_LOG_FILE = "log/database.log"
    PTSITE_LOG_FILE = "log/site.log"         # record request url
    PAGE_LOG_FILE = "log/page.log"           # record page_torrents
    DETAIL_LOG_FILE = "log/detail.log"       # record get download_url/id from detail_url
    MOVIE_LOG_FILE = "log/movie.log"
    SOCKET_LOG_FILE = "log/socket.log"

    EXEC_LOG_FILE = "log/pt.log"
    DEBUG_LOG_FILE = "log/pt.debug"
    ERROR_LOG_FILE = "log/pt.error"

    lastLogDay = "1970-01-01"

    @staticmethod
    def database_log(log_str):
        Log.pt_log(Log.DATABASE_LOG_FILE, log_str)

    @staticmethod
    def info_log(log_str):
        Log.pt_log(Log.INFO_LOG_FILE, log_str)

    @staticmethod
    def rss_log(log_str):
        Log.pt_log(Log.RSS_LOG_FILE, log_str)

    @staticmethod
    def page_log(log_str):
        Log.pt_log(Log.PAGE_LOG_FILE, log_str)

    @staticmethod
    def site_log(log_str):
        Log.pt_log(Log.PTSITE_LOG_FILE, log_str)

    @staticmethod
    def detail_log(log_str):
        Log.pt_log(Log.DETAIL_LOG_FILE, log_str)

    @staticmethod
    def movie_log(log_str):
        Log.pt_log(Log.MOVIE_LOG_FILE, log_str)

    @staticmethod
    def socket_log(log_str):
        Log.pt_log(Log.SOCKET_LOG_FILE, log_str)

    @staticmethod
    def log_clear(file_name=""):
        if file_name == "":
            if os.path.isfile(Log.INFO_LOG_FILE+".old"):
                os.remove(Log.INFO_LOG_FILE+".old")
            if os.path.isfile(Log.INFO_LOG_FILE):
                os.rename(Log.INFO_LOG_FILE, Log.INFO_LOG_FILE+".old")

            if os.path.isfile(Log.RSS_LOG_FILE+".old"):
                os.remove(Log.RSS_LOG_FILE+".old")
            if os.path.isfile(Log.RSS_LOG_FILE):
                os.rename(Log.RSS_LOG_FILE, Log.RSS_LOG_FILE+".old")

            if os.path.isfile(Log.PTSITE_LOG_FILE+".old"):
                os.remove(Log.PTSITE_LOG_FILE+".old")
            if os.path.isfile(Log.PTSITE_LOG_FILE):
                os.rename(Log.PTSITE_LOG_FILE, Log.PTSITE_LOG_FILE+".old")

            if os.path.isfile(Log.SOCKET_LOG_FILE+".old"):
                os.remove(Log.SOCKET_LOG_FILE+".old")
            if os.path.isfile(Log.SOCKET_LOG_FILE):
                os.rename(Log.SOCKET_LOG_FILE, Log.SOCKET_LOG_FILE+".old")
        else:
            if os.path.isfile(file_name+".old"):
                os.remove(file_name+".old")
            if os.path.isfile(file_name):
                os.rename(file_name, file_name + ".old")

    @staticmethod
    def log_print(log_str):
        current_time = datetime.datetime.now()
        print(current_time.strftime('%Y-%m-%d %H:%M:%S') + "::", end='')
        print(log_str)

    @staticmethod
    def pt_log(file_name, log_str, time_flag=True):
        fo = open(file_name, "a+", encoding='UTF-8')
        current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        if time_flag:
            fo.write(f"{current_time[11:]}: ")
        fo.write(log_str+'\n')
        fo.close()

    @staticmethod
    def debug_log(log_str, mode="np"):
        Log.pt_log(Log.DEBUG_LOG_FILE, log_str)
        if mode == "p":
            Log.log_print(log_str)

    @staticmethod
    def exec_log(log_str):
        Log.log_print(log_str)
        current_day_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        if current_day_time[:10] != Log.lastLogDay:
            Log.lastLogDay = current_day_time[:10]
            Log.exec_log(f"new day: ----------------------{Log.lastLogDay}----------------------- ")
        Log.debug_log(log_str)
        Log.pt_log(Log.EXEC_LOG_FILE, log_str)

    @staticmethod
    def error_log(log_str):
        Log.log_print(log_str)
        Log.exec_log(log_str)
        Log.pt_log(Log.ERROR_LOG_FILE, log_str)
        traceback.print_stack()
