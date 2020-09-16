#!/usr/bin/python3
# coding=utf-8
import datetime
import traceback
import time
import os


ExecLogFile  = "log/pt.log"               #运行日志
DebugLogFile = "log/pt.debug"             #调试日志，可以是相对路径，也可以是绝对路径
ErrorLogFile = "log/pt.error"             #错误日志

INFO_LOG_FILE='log/info.log'
RSS_LOG_FILE='log/rss.log'
DATABASE_LOG_FILE = 'log/database.log'
PTSITE_LOG_FILE ='log/site.log'
MOVIE_LOG_FILE ='log/movie.log'
SOCKET_LOG_FILE='log/socket.log'

def info_log(tStr):
    Log(INFO_LOG_FILE,tStr)

def rss_log(tStr):
    Log(RSS_LOG_FILE,tStr)

def database_log(tStr):
    Log(DATABASE_LOG_FILE,tStr)

def site_log(tStr):
    Log(PTSITE_LOG_FILE,tStr)

def movie_log(tStr):
    Log(MOVIE_LOG_FILE,tStr)

def socket_log(tStr):
    Log(SOCKET_LOG_FILE,tStr)

def Print(Str):
    tCurrentTime = datetime.datetime.now()
    print(tCurrentTime.strftime('%Y-%m-%d %H:%M:%S')+"::" , end='')
    print(Str)

def LogClear(FileName="") :
    if FileName == "":
        if os.path.isfile(INFO_LOG_FILE+".old"):    os.remove(INFO_LOG_FILE+".old")
        if os.path.isfile(INFO_LOG_FILE)       :    os.rename(INFO_LOG_FILE,INFO_LOG_FILE+".old")
        if os.path.isfile(RSS_LOG_FILE+".old"):     os.remove(RSS_LOG_FILE+".old")
        if os.path.isfile(RSS_LOG_FILE)       :     os.rename(RSS_LOG_FILE,RSS_LOG_FILE+".old")
        if os.path.isfile(PTSITE_LOG_FILE+".old"):  os.remove(PTSITE_LOG_FILE+".old")
        if os.path.isfile(PTSITE_LOG_FILE)       :  os.rename(PTSITE_LOG_FILE,PTSITE_LOG_FILE+".old")
        if os.path.isfile(SOCKET_LOG_FILE+".old"):  os.remove(SOCKET_LOG_FILE+".old")
        if os.path.isfile(SOCKET_LOG_FILE)       :  os.rename(SOCKET_LOG_FILE,SOCKET_LOG_FILE+".old")

def Print(Str):
    tCurrentTime = datetime.datetime.now()
    print(tCurrentTime.strftime('%Y-%m-%d %H:%M:%S')+"::" , end='')
    print(Str)

def LogClear(FileName="") :
    if FileName == "":
        if os.path.isfile(INFO_LOG_FILE+".old"):    os.remove(INFO_LOG_FILE+".old")
        if os.path.isfile(INFO_LOG_FILE)       :    os.rename(INFO_LOG_FILE,INFO_LOG_FILE+".old")
        if os.path.isfile(RSS_LOG_FILE+".old"):     os.remove(RSS_LOG_FILE+".old")
        if os.path.isfile(RSS_LOG_FILE)       :     os.rename(RSS_LOG_FILE,RSS_LOG_FILE+".old")
        if os.path.isfile(PTSITE_LOG_FILE+".old"):  os.remove(PTSITE_LOG_FILE+".old")
        if os.path.isfile(PTSITE_LOG_FILE)       :  os.rename(PTSITE_LOG_FILE,PTSITE_LOG_FILE+".old")

    if os.path.isfile(FileName):
        if os.path.isfile(FileName+".old"):    os.remove(FileName+".old")
        os.rename(FileName,FileName+".old")
      
def Log(FileName,Str,time_flag=True) :
    fo = open(FileName,"a+")
    tCurrentTime = datetime.datetime.now()
    if time_flag == True: fo.write(tCurrentTime.strftime('%Y-%m-%d %H:%M:%S')+"::")
    fo.write(Str+'\n')
    fo.close()

def DebugLog( Str, Mode = "np"):    
    Log(DebugLogFile,Str)
    if Mode == "p": Print(Str)

def ExecLog(Str):
    Print(Str)
    DebugLog(Str)
    Log(ExecLogFile,Str)    
    
def ErrorLog(Str):
    Print(Str)
    ExecLog(Str)
    Log(ErrorLogFile,Str)
    traceback.print_stack()
