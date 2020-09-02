#!/usr/bin/python3
# coding=utf-8
import os
import sys
import shutil
import re
import datetime
from  movie import *
import mysql.connector

ToBeExecDirName = True     # DirName名称
ToBeExecRmdir   = False     # 从子文件夹将内容提上来 删除空子目录
DebugLogFile = "log/debug3.log"             #日志，可以是相对路径，也可以是绝对路径
ErrorLogFile = "log/error3.log"             #错误日志
ExecLogFile  = "log/exec3.log"
CHECKERROR = -1
CHECKNORMAL = 0
g_CheckDiskPath = ""
g_CheckDisk = ""

#记录日志用的函数############################################################
def LogClear(FileName) :
    if os.path.isfile(FileName):
        if os.path.isfile(FileName+".old"):    os.remove(FileName+".old")
        os.rename(FileName,FileName+".old")
      
def Log(FileName,Str) :
    fo = open(FileName,"a+")
    tCurrentTime = datetime.datetime.now()
    fo.write(tCurrentTime.strftime('%Y-%m-%d %H:%M:%S')+"::")
    fo.write(Str)
    fo.write('\n')
    fo.close()

def DebugLog( Str, Mode = "np"):    
    Log(DebugLogFile,Str)
    if Mode == "p": print(Str)
    
def ErrorLog(Str):
    print(Str)
    DebugLog(Str)
    Log(ErrorLogFile,Str)
################################################################################   

def CheckMovies(DiskPath,Disk):
    '''
    对DiskPath下的每一个DirName加入对象实体到MyMovies[]并调用movie.CheckMovie()进行检查和处理，包括
    1)检查目录名称(CheckDirName)
    2)检查内容(CheckDirCont)
    3)进行目录重命名(RenameDirName)
    '''
    if not os.path.isdir(DiskPath) :  DebugLog(DiskPath+"is not  a dir"); return -1
    for file in os.listdir(DiskPath):
        fullpathfile = os.path.join(DiskPath,file)
        if os.path.isdir(fullpathfile):
        
            #一些特殊文件夹忽略
            if file      == 'lost+found' or \
               file[0:6] == '.Trash' or \
               file[0:8] == '$RECYCLE' or\
               file[0:6] == 'System' or\
               file[0:5] == 'cover' or\
               file[0:4] == '0000':
                print ("ignore some dir:"+file)
                DebugLog ("ignore some dir:"+file)
                continue 

            tMovie = Movie(DiskPath,file,Disk)
            if tMovie.check_movie() != SUCCESS:
                ExecLog ("CheckMovie error:"+tMovie.dir_name)
                DebugLog ("")
                DebugLog ("")
            else:
                DebugLog ("correct movie:"+tMovie.dir_name)
        
    return 1


def CheckDisk(DiskPath,Disk):
    '''
    '''
    if not update("update movies set checked=0 where disk=%s",(Disk,)):
        return False

    if CheckMovies(DiskPath,Disk) == -1 : return -1
    
    #对Disk=Disk，CheckTime != gCheckTime的所有记录进行set Delete=1
    up_sql = "UPDATE movies set Deleted = 1 ,CheckTime = %s where Disk = %s and checked=0  and Deleted = 0"
    up_val = (gCheckTime,Disk)
    try:
        g_MyCursor.execute(up_sql,up_val)
        g_DB.commit()
    except:
        ErrorLog("update error:"+up_sql)
        return CHECKERROR
    
    #找出所有刚被置位的记录，记录日志
    #select from movies where Number == tMovie.Number and Copy == tMovie.Copy
    se_sql = "select DirName from movies where Deleted = 1 and Disk = %s and CheckTime >= %s"
    se_val = (Disk,gCheckTime)    
    g_MyCursor.execute(se_sql,se_val)
    tSelectResult = g_MyCursor.fetchall()    
    for tSelect in tSelectResult:
        ErrorLog("warning:set deleted=1:"+tSelect[0])
    DebugLog(str(len(tSelectResult))+" records deleted:"+Disk)
    
    #找出所有重复的imdbid和doubanid
    se_sql = "select imdbid,doubanid,dirname,number from movies where deleted=0"
    g_MyCursor.execute(se_sql)
    tSelectResult = g_MyCursor.fetchall()
    
    i = 0
    while i < len(tSelectResult):
        imdbID   = tSelectResult[i][0]
        DoubanID = tSelectResult[i][1]
        DirName  = tSelectResult[i][2]
        Number   = tSelectResult[i][3]
        #if imdbID == "":  i+=1 ; continue
        j=i
        while j < len(tSelectResult):
            imdbID2   = tSelectResult[i][0]
            DoubanID2 = tSelectResult[i][1]
            DirName2  = tSelectResult[i][2]
            Number2   = tSelectResult[i][3]
            if ((imdbID != "" and imdbID == imdbID2) or (DoubanID != "" and DoubanID == DoubanID2)) and Number != Number2 :
                print("duplicate :"+DirName)
                print("           "+DirName2)
            j+=1
        i+=1
        
if __name__ == '__main__' :
    global g_DB
    global g_MyCursor
    global gCheckTime

    #全局变量
    g_DB = mysql.connector.connect(
      host="localhost",      # 数据库主机地址
      user="dummy",    # 数据库用户名
      passwd="moonbeam" ,  # 数据库密码
      database="db_movies"
    )
    g_MyCursor = g_DB.cursor()
    
    LogClear(ErrorLogFile)  
    LogClear(DebugLogFile)  
    LogClear(ExecLogFile)  
    
    if len(sys.argv) == 1:
        print ("please choose the diskpath:")
        print ("0       == /media/root/BT/movies")
        print ("bt      == /media/root/BT/movies")
        print ("1       == /media/root/wd4t")
        print ("wd4t    == /media/root/wd4t")
        print ("2       == /media/root/wd2t")
        print ("wd2t    == /media/root/wd2t")
        print ("3       == /media/root/wd2t-2")
        print ("wd2t-2  == /media/root/wd2t-2")
        print ("4       == /media/root/sg3t")
        print ("sg3t    == /media/root/sg3t")
        print ("5       == /media/root/sg3t-2")
        print ("sg3t-2  == /media/root/sg3t-2")
        print ("6       == /media/root/SG8T")
        print ("sg8t    == /media/root/SG8T")
        print ("7       == /media/root/BT/tobe")
        print ("tobe    == /media/root/BT/tobe")
        Choise = input("your choise is :")
        print (Choise) 
    elif len(sys.argv) == 2:    
        Choise = sys.argv[1]
    else :
        print ("too many argv:")
        exit()
        
    if Choise == "0" or Choise.lower() == "bt":
        CheckDiskPath = "/media/root/BT/movies" ; disk = "BT"
    elif Choise == "1" or Choise.lower() == "wd4t" :
        CheckDiskPath = "/media/root/wd4t" ; Disk = "wd4t"
    elif Choise == "2" or Choise.lower() == "wd2t" :
        CheckDiskPath = "/media/root/WD2T" ; Disk = "wd2t"
    elif Choise == "3" or Choise.lower() == "wd2t-2" :
        CheckDiskPath = "/media/root/WD2T-2" ; Disk = "wd2t-2"
    elif Choise == "4" or Choise.lower() == "sg3t" :
        CheckDiskPath = "/media/root/SG3T" ; Disk = "sg3t"
    elif Choise == "5" or Choise.lower() == "sg3t-2" :
        CheckDiskPath = "/media/root/sg3t-2" ; Disk = "sg3t-2"
    elif Choise == "6" or Choise.lower() == "sg8t" :
        CheckDiskPath = "/media/root/SG8T" ; Disk = "sg8t"
    elif Choise == '7' or Choise.lower() == 'tobe' :
        CheckDiskPath = "/media/root/BT/tobe"; Disk = "tobe"
    else :
        print ("your choise is invalid:"+Choise)
        exit()
    
    Movie.ToBeExecDirName  =  ToBeExecDirName
    Movie.ToBeExecRmdir  =  ToBeExecRmdir
               
    print ("begin check "+Disk+" in table_movies")
    #获取CheckTime为当前时间
    tCurrentTime = datetime.datetime.now()
    gCheckTime=tCurrentTime.strftime('%Y-%m-%d %H:%M:%S')
    g_MyMovies = []; g_Count = 0
    CheckDisk(CheckDiskPath,Disk)
    print ("complete check "+Disk+" in table_movies")    
