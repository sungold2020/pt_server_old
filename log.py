#!/usr/bin/python3
# coding=utf-8
import datetime
import time
import os


ExecLogFile  = "log/pt.log"               #运行日志
DebugLogFile = "log/pt.debug"             #调试日志，可以是相对路径，也可以是绝对路径
ErrorLogFile = "log/pt.error"             #错误日志

INFO_LOG_FILE='log/info.log'
RSS_LOG_FILE='log/rss.log'
DATABASE_LOG_FILE = 'log/database.log'
PTSITE_LOG_FILE ='log/site.log'

def info_log(tStr):
    Log(INFO_LOG_FILE,tStr)

def rss_log(tStr):
    Log(RSS_LOG_FILE,tStr)

def database_log(tStr):
    Log(DATABASE_LOG_FILE,tStr)

def site_log(tStr):
    Log(PTSITE_LOG_FILE,tStr)

def Print(Str):
    tCurrentTime = datetime.datetime.now()
    print(tCurrentTime.strftime('%Y-%m-%d %H:%M:%S')+"::" , end='')
    print(Str)

def LogClear(FileName) :
    if os.path.isfile(FileName):
        if os.path.isfile(FileName+".old"):    os.remove(FileName+".old")
        os.rename(FileName,FileName+".old")
      
def Log(FileName,Str) :
    fo = open(FileName,"a+")
    tCurrentTime = datetime.datetime.now()
    fo.write(tCurrentTime.strftime('%Y-%m-%d %H:%M:%S')+"::")
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
