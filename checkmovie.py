#!/usr/bin/python3
# coding=utf-8
import os
import sys
import shutil
import re
import datetime
from movie import *
import config

DISK_LIST = [
        {"path": "/media/root/BT/tobe", "name": "tobe"},
        {"path": "/media/root/wd2t", "name": "wd2t"},
        {"path": "/media/root/wd2t-2", "name": "wd2t-2"},
        {"path": "/media/root/sg3t", "name": "sg3t"},
        {"path": "/media/root/sg3t-2", "name": "sg3t-2"},
        {"path": "/media/root/wd4t", "name": "wd4t"},
        {"path": "/media/root/SG8T", "name": "sg8t"},
        {"path": "/media/root/WD12T", "name": "wd12t"}
        ]


CHECKERROR = -1
CHECKNORMAL = 0
g_CheckDiskPath = ""
g_CheckDisk = ""


def check_movies(t_disk_path, t_disk_name):
    """
    对DiskPath下的每一个DirName加入对象实体到MyMovies[]并调用movie.CheckMovie()进行检查和处理，包括
    1)检查目录名称(CheckDirName)
    2)检查内容(CheckDirCont)
    3)进行目录重命名(RenameDirName)
    """
    if not os.path.isdir(t_disk_path):
        debug_log(t_disk_path + "is not  a dir")
        return -1
    for file in os.listdir(t_disk_path):
        fullpathfile = os.path.join(t_disk_path, file)
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

            t_movie = Movie(t_disk_path, file, t_disk_name)
            if not t_movie.check_movie():
                exec_log("CheckMovie error:" + t_movie.dir_name)
                debug_log("")
                debug_log("")
            else:
                debug_log("correct movie:" + t_movie.dir_name)

    return 1


def check_disk(t_disk_path, t_disk_name):
    if not update("update movies set checked=0 where disk=%s", (t_disk_name,)):
        return False

    if check_movies(t_disk_path, t_disk_name) == -1:
        return -1

    # 对Disk=Disk，CheckTime != gCheckTime的所有记录进行set Delete=1
    up_sql = "UPDATE movies set Deleted = 1 ,CheckTime = %s where Disk = %s and checked=0  and Deleted = 0"
    up_val = (gCheckTime, t_disk_name)
    if not update(up_sql, up_val):
        return CHECKERROR

    # 找出所有刚被置位的记录，记录日志
    # select from movies where number == tMovie.number and Copy == tMovie.Copy
    se_sql = "select dirname from movies where Deleted = 1 and Disk = %s and CheckTime >= %s"
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

    choise = None
    if len(sys.argv) == 1:
        print("please choose the disk:")
        for i in range(len(DISK_LIST)):
            disk = DISK_LIST[i]
            print(disk['name'].ljust(6)+str(i)+' -----> '+disk['path']+"\n")
        choise = input("your choise is :")
        print(choise)
    elif len(sys.argv) == 2:
        choise = sys.argv[1]
    else:
        print("too many argv:")
        exit()

    disk_path = disk_name = ""
    if choise.isdigit():
        index = int(choise)
        if index >= len(DISK_LIST):
            print(f"序号{index}越界了")
            exit()
        disk_path = DISK_LIST[index]['path']
        disk_name = DISK_LIST[index]['name']
    else:
        for disk in DISK_LIST:
            if disk['name'] == choise.lower():
                disk_path = disk['path']
                disk_name = disk['name']
        if disk_path == "":
            print(f"没有找到对应名称为{choise}的disk")
            exit()
    print("your choise is:" + choise)

    print("begin check " + disk_name + " in table_movies")
    # 获取CheckTime为当前时间
    tCurrentTime = datetime.datetime.now()
    gCheckTime = tCurrentTime.strftime('%Y-%m-%d %H:%M:%S')
    g_MyMovies = []
    g_Count = 0
    check_disk(disk_path, disk_name)
    print("complete check " + disk_name + " in table_movies")
