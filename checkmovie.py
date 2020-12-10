#!/usr/bin/python3
# coding=utf-8
import os
import sys
import shutil
import re
import datetime
from movie import *
import mysql.connector
import config

CHECKERROR = -1
CHECKNORMAL = 0
g_CheckDiskPath = ""
g_CheckDisk = ""


def check_movies(disk_path, t_disk_name):
    """
    对DiskPath下的每一个DirName加入对象实体到MyMovies[]并调用movie.CheckMovie()进行检查和处理，包括
    1)检查目录名称(CheckDirName)
    2)检查内容(CheckDirCont)
    3)进行目录重命名(RenameDirName)
    """
    if not os.path.isdir(disk_path):
        debug_log(disk_path + "is not  a dir")
        return -1
    for file in os.listdir(disk_path):
        fullpathfile = os.path.join(disk_path, file)
        if os.path.isdir(fullpathfile):
            # 一些特殊文件夹忽略
            if file == 'lost+found' or \
                    file[0:6] == '.Trash' or \
                    file[0:8] == '$RECYCLE' or \
                    file[0:6] == 'System' or \
                    file[0:5] == 'cover' or \
                    file[0:4] == '0000':
                print("ignore some dir:" + file)
                debug_log("ignore some dir:" + file)
                continue

            t_movie = Movie(disk_path, file, t_disk_name)
            if not t_movie.check_movie():
                exec_log("CheckMovie error:" + t_movie.dir_name)
                debug_log("")
                debug_log("")
            else:
                debug_log("correct movie:" + t_movie.dir_name)

    return 1


def check_disk(disk_path, t_disk_name):
    if not update("update movies set checked=0 where disk=%s", (t_disk_name,)):
        return False

    if check_movies(disk_path, t_disk_name) == -1:
        return -1

    # 对Disk=Disk，CheckTime != gCheckTime的所有记录进行set Delete=1
    up_sql = "UPDATE movies set Deleted = 1 ,CheckTime = %s where Disk = %s and checked=0  and Deleted = 0"
    up_val = (gCheckTime, t_disk_name)
    if not update(up_sql, up_val):
        return CHECKERROR

    # 找出所有刚被置位的记录，记录日志
    # select from movies where number == tMovie.number and Copy == tMovie.Copy
    se_sql = "select dir_name from movies where Deleted = 1 and Disk = %s and CheckTime >= %s"
    se_val = (t_disk_name, gCheckTime)
    t_select_result = select(se_sql, se_val)
    for tSelect in t_select_result:
        error_log("warning:set deleted=1:" + tSelect[0])
    debug_log(str(len(t_select_result)) + " records deleted:" + t_disk_name)

    # 找出所有重复的imdbid和doubanid
    se_sql = "select imdbid,doubanid,dirname,number from movies where deleted=0"
    t_select_result = select(se_sql, None)

    i = 0
    while i < len(t_select_result):
        imdb_id = t_select_result[i][0]
        douban_id = t_select_result[i][1]
        dir_name = t_select_result[i][2]
        number = t_select_result[i][3]
        # if imdb_id == "":  i+=1 ; continue
        j = i
        while j < len(t_select_result):
            imdb_id2 = t_select_result[i][0]
            douban_id2 = t_select_result[i][1]
            dir_name2 = t_select_result[i][2]
            number2 = t_select_result[i][3]
            if ((imdb_id != "" and imdb_id == imdb_id2) or (
                    douban_id != "" and douban_id == douban_id2)) and number != number2:
                print("duplicate :" + dir_name)
                print("           " + dir_name2)
            j += 1
        i += 1


if __name__ == '__main__':
    global gCheckTime

    Choise = None
    if len(sys.argv) == 1:
        print("please choose the diskpath:")
        print("0       == /media/root/BT/movies")
        print("bt      == /media/root/BT/movies")
        print("1       == /media/root/wd4t")
        print("wd4t    == /media/root/wd4t")
        print("2       == /media/root/wd2t")
        print("wd2t    == /media/root/wd2t")
        print("3       == /media/root/wd2t-2")
        print("wd2t-2  == /media/root/wd2t-2")
        print("4       == /media/root/sg3t")
        print("sg3t    == /media/root/sg3t")
        print("5       == /media/root/sg3t-2")
        print("sg3t-2  == /media/root/sg3t-2")
        print("6       == /media/root/SG8T")
        print("sg8t    == /media/root/SG8T")
        print("7       == /media/root/BT/tobe")
        print("tobe    == /media/root/BT/tobe")
        print("8       == /media/root/WD12T")
        print("wd12t   == /media/root/WD12T")
        Choise = input("your choise is :")
        print(Choise)
    elif len(sys.argv) == 2:
        Choise = sys.argv[1]
    else:
        print("too many argv:")
        exit()

    disk_pash = disk_name = ""
    if Choise == "0" or Choise.lower() == "bt":
        disk_pash = "/media/root/BT/movies"
        disk_name = "BT"
    elif Choise == "1" or Choise.lower() == "wd4t":
        disk_pash = "/media/root/wd4t"
        disk_name = "wd4t"
    elif Choise == "2" or Choise.lower() == "wd2t":
        disk_pash = "/media/root/WD2T"
        disk_name = "wd2t"
    elif Choise == "3" or Choise.lower() == "wd2t-2":
        disk_pash = "/media/root/WD2T-2"
        disk_name = "wd2t-2"
    elif Choise == "4" or Choise.lower() == "sg3t":
        disk_pash = "/media/root/SG3T"
        disk_name = "sg3t"
    elif Choise == "5" or Choise.lower() == "sg3t-2":
        disk_pash = "/media/root/sg3t-2"
        disk_name = "sg3t-2"
    elif Choise == "6" or Choise.lower() == "sg8t":
        disk_pash = "/media/root/SG8T"
        disk_name = "sg8t"
    elif Choise == '7' or Choise.lower() == 'tobe':
        disk_pash = "/media/root/BT/tobe"
        disk_name = "tobe"
    elif Choise == '8' or Choise.lower() == 'wd12t':
        disk_pash = "/media/root/WD12T"
        disk_name = "wd12t"
    else:
        print("your choise is invalid:" + Choise)
        exit()

    print("begin check " + disk_name + " in table_movies")
    # 获取CheckTime为当前时间
    tCurrentTime = datetime.datetime.now()
    gCheckTime = tCurrentTime.strftime('%Y-%m-%d %H:%M:%S')
    g_MyMovies = []
    g_Count = 0
    check_disk(disk_pash, disk_name)
    print("complete check " + disk_name + " in table_movies")
