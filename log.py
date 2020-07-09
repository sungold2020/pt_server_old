#!/usr/bin/python3
# coding=utf-8
import datetime
import time
import os


ExecLogFile  = "log/pt.log"               #运行日志
DebugLogFile = "log/pt.debug"             #调试日志，可以是相对路径，也可以是绝对路径
ErrorLogFile = "log/pt.error"             #错误日志

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
