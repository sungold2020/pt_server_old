#!/usr/bin/python3
# coding=utf-8
import datetime
import traceback
import os

from config import *

global lastLogDay
lastLogDay = "1970-01-01"


def info_log(log_str):
    pt_log(g_config.INFO_LOG_FILE, log_str)


def rss_log(log_str):
    pt_log(g_config.RSS_LOG_FILE, log_str)


def database_log(log_str):
    pt_log(g_config.DATABASE_LOG_FILE, log_str)


def site_log(log_str):
    pt_log(g_config.PTSITE_LOG_FILE, log_str)


def movie_log(log_str):
    pt_log(g_config.MOVIE_LOG_FILE, log_str)


def socket_log(log_str):
    pt_log(g_config.SOCKET_LOG_FILE, log_str)


def log_clear(file_name=""):
    if file_name == "":
        if os.path.isfile(g_config.INFO_LOG_FILE+".old"):
            os.remove(g_config.INFO_LOG_FILE+".old")
        if os.path.isfile(g_config.INFO_LOG_FILE):
            os.rename(g_config.INFO_LOG_FILE, g_config.INFO_LOG_FILE+".old")

        if os.path.isfile(g_config.RSS_LOG_FILE+".old"):
            os.remove(g_config.RSS_LOG_FILE+".old")
        if os.path.isfile(g_config.RSS_LOG_FILE):
            os.rename(g_config.RSS_LOG_FILE, g_config.RSS_LOG_FILE+".old")

        if os.path.isfile(g_config.PTSITE_LOG_FILE+".old"):
            os.remove(g_config.PTSITE_LOG_FILE+".old")
        if os.path.isfile(g_config.PTSITE_LOG_FILE):
            os.rename(g_config.PTSITE_LOG_FILE, g_config.PTSITE_LOG_FILE+".old")

        if os.path.isfile(g_config.SOCKET_LOG_FILE+".old"):
            os.remove(g_config.SOCKET_LOG_FILE+".old")
        if os.path.isfile(g_config.SOCKET_LOG_FILE):
            os.rename(g_config.SOCKET_LOG_FILE, g_config.SOCKET_LOG_FILE+".old")
    else:
        if os.path.isfile(file_name+".oid"):
            os.remove(file_name+".old")
        if os.path.isfile(file_name):
            os.rename(file_name, file_name + ".old")


def log_print(log_str):
    current_time = datetime.datetime.now()
    print(current_time.strftime('%Y-%m-%d %H:%M:%S') + "::", end='')
    print(log_str)


def pt_log(file_name, log_str, time_flag=True):
    fo = open(file_name, "a+")
    current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    if time_flag:
        fo.write(f"{current_time[11:]}: ")
    fo.write(log_str+'\n')
    fo.close()


def debug_log(log_str, mode="np"):
    pt_log(g_config.DebugLogFile, log_str)
    if mode == "p":
        log_print(log_str)


def exec_log(log_str):
    global lastLogDay

    log_print(log_str)
    current_day_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    if current_day_time[:10] != lastLogDay:
        lastLogDay = current_day_time[:10]
        exec_log(f"new day: ----------------------{lastLogDay}----------------------- ")
    debug_log(log_str)
    pt_log(g_config.ExecLogFile, log_str)


def error_log(log_str):
    log_print(log_str)
    exec_log(log_str)
    pt_log(g_config.ErrorLogFile, log_str)
    traceback.print_stack()
