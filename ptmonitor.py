#!/usr/bin/python3
# coding=utf-8
import datetime
import time
import os
#import requests
#import feedparser
import re
import psutil
#import codecs 
#from bs4 import BeautifulSoup
#import transmissionrpc
#import qbittorrentapi

#import movie
#from rss import *
#from info import Info
#from torrent import Torrent
#from mytorrent import *
#from log import *
#from ptsite import *
#from torrent_info import TorrentInfo
from connect import *
from torrents import *

#配置自己要检查的磁盘/保存路径，看下面是否有文件夹/文件已经不在种子列表，这样就可以转移或者删除了。
CHECK_DISK_LIST = ["/media/root/BT/movies"]

global gSocket
gSocket = None
#global gTorrents
#gTorrents = None


def handle_task(Request,mConnect=None):
    global gTorrents

    socket_log("accept request:"+Request)
    RequestList = Request.split()
    Task = RequestList[0].lower(); del RequestList[0]
    if   Task == 'checkdisk': 
        if len(RequestList) > 0 : gTorrents.check_disk(RequestList)
        else                    : gTorrents.check_disk(CHECK_DISK_LIST)
    elif Task == 'rss'      : 
        for RSSName in RequestList: gTorrents.request_rss(RSSName,-1)
    elif Task == 'free'     :
        if len(RequestList) > 0 : gTorrents.request_free(RequestList[0])
        else                    : gTorrents.request_free('MTeam')
    elif Task == 'checkqb'      : gTorrents.check_torrents("QB") 
    elif Task == 'checktr'      : gTorrents.check_torrents("TR") 
    elif Task == 'backuptorrent': gTorrents.backup_torrents()
    elif Task == 'keep'         : gTorrents.keep_torrents( check_disk(RequestList) )
    elif Task == 'set_id'       : return gTorrents.request_set_id(RequestList[0] if len(RequestList) == 1 else "")
    elif Task == 'set_category' : return gTorrents.request_set_category(RequestList[0] if len(RequestList) == 1 else "")
    elif Task == 'view'         : 
        if len(RequestList) == 1 and RequestList[0] == 'all': return str(update_viewed(False))
        else                                                : return str(update_viewed(True))
    #elif Task == 'tobeadd'      : to_be_add_torrents(mConnect)
    elif Task == 'lowupload'    : return gTorrents.print_low_upload()
    elif Task == 'torrents'     : return gTorrents.query_torrents(RequestList)
    elif Task == "del"          : return gTorrents.request_del_torrent(RequestList[0] if len(RequestList) == 1 else "")
    elif Task == "act_torrent"  : return gTorrents.request_act_torrent(RequestList[0] if len(RequestList) == 1 else "")
    elif Task == "movie"        : return gTorrents.request_saved_movie(RequestList[0] if len(RequestList) == 1 else "")
    elif Task == 'log'          : return get_log()
    else                        : socket_log("unknown request task:"+Task) ; return "unknown request task"     
    
    return "completed"

def get_log():
    Command = "tail -n 500 /root/pt/log/pt.log > log/temp.log"
    #ExecLog("exec:"+QBCopyCommand)
    if os.system(Command) == 0 : socket_log ("success exec:"+Command)
    with open('log/temp.log', 'r') as f1:
        logStr  = f1.read()
    return ''.join(logStr)
     
def backup_torrents():
    """
    把QB和TR的torrents备份到相应目录
    """

    global QB_BACKUP_DIR
    global TR_BACKUP_DIR
    global QB_TORRENTS_BACKUP_DIR
    global TR_TORRENTS_BACKUP_DIR

    if QB_BACKUP_DIR[-1:] != '/' : QB_BACKUP_DIR = QB_BACKUP_DIR+'/'
    if TR_BACKUP_DIR[-1:] != '/' : TR_BACKUP_DIR = TR_BACKUP_DIR+'/'
    if QB_TORRENTS_BACKUP_DIR[-1:] != '/' : QB_TORRENTS_BACKUP_DIR = QB_TORRENTS_BACKUP_DIR+'/'
    if TR_TORRENTS_BACKUP_DIR[-1:] != '/' : TR_TORRENTS_BACKUP_DIR = TR_TORRENTS_BACKUP_DIR+'/'

    QBCopyCommand = "cp -n "+QB_BACKUP_DIR+"* "+QB_TORRENTS_BACKUP_DIR
    #ExecLog("exec:"+QBCopyCommand)
    if os.system(QBCopyCommand) == 0 : ExecLog ("success exec:"+QBCopyCommand)
    else : ExecLog("failed to exec:"+QBCopyCommand); return False

    TRCopyCommand1 = "cp -n "+TR_BACKUP_DIR+"torrents/* "+TR_TORRENTS_BACKUP_DIR
    #ExecLog("exec:"+TRCopyCommand1)
    if os.system(TRCopyCommand1) == 0 : ExecLog ("success exec:"+TRCopyCommand1)
    else : ExecLog("failed to exec:"+TRCopyCommand1); return False
    TRCopyCommand2 = "cp -n "+TR_BACKUP_DIR+"resume/* "+TR_TORRENTS_BACKUP_DIR
    #ExecLog("exec:"+TRCopyCommand2)
    if os.system(TRCopyCommand2) == 0 : ExecLog ("success exec:"+TRCopyCommand2)
    else : ExecLog("failed to exec:"+TRCopyCommand2); return False

def listen_socket():
    while True:
        #监听Client是否有任务请求
        if not gSocket.accept(): continue

        Request = gSocket.receive()
        if Request == "": socket_log("empty request"); continue
        socket_log("recv:"+Request)

        Reply = handle_task(Request,gSocket)
        #Print("begin send")
        gSocket.send(Reply)
        socket_log("send:"+Reply)
        gSocket.close()

if __name__ == '__main__' :
    global gTorrents

    LogClear()
    
    #初始化，建立torrents对象
    gTorrents = Torrents()
    if  gTorrents.check_torrents("QB") == -1: exit()
    if  gTorrents.check_torrents("TR") == -1: exit()
    gTorrents.write_pt_backup()
    
    #初始化Socket对象
    socket.setdefaulttimeout(60)
    gSocket = Socket()
    if not gSocket.init(): exit()
   
    gLastCheckDate = gTorrents.last_check_date

    
    thread_socket = threading.Thread(target=listen_socket)
    thread_socket.start()

    LoopTimes = 0
    while True:
        LoopTimes += 1
        Print("loop times :"+str(LoopTimes%120) )

        gToday = datetime.datetime.now().strftime('%Y-%m-%d')

        #RSS和FREE种子订阅及查找
        gTorrents.request_rss("",LoopTimes)
        gTorrents.request_free("",LoopTimes)

        if gToday != gLastCheckDate :  #new day
            gTorrents.count_upload("QB") 
            gTorrents.count_upload("TR")
            gTorrents.write_pt_backup()
            gTorrents.tracker_data()                   #tracker_data执行要在count_upload()之后，这样才有新的记录
            gTorrents.check_disk(CHECK_DISK_LIST)
            backup_torrents()
            #一月备份一次qb，tr,data
            if gToday[8:10] == '01' : os.system("/root/backup.sh"); ExecLog("exec:/root/backup.sh")
            if gToday[8:10] == '01' or gToday[8:10] == '15': update_viewed(True)    #半月更新一次viewed
        else:
            if LoopTimes % 5 == 0 : gTorrents.check_torrents("QB") 
        
        #gLastCheckDate = datetime.datetime.now().strftime("%Y-%m-%d")
        gLastCheckDate = gToday
        gTorrents.last_check_date = gLastCheckDate
        DebugLog("update gLastCheckDate="+gLastCheckDate)        

        #检查一下内存占用
        tMem = psutil.virtual_memory()
        DebugLog("memory percent used:"+str(tMem.percent))
        if tMem.percent >= 92: ExecLog("memory percent used:"+str(tMem.percent)); PTClient("QB").restart()

        time.sleep(60)

        """
        #监听Client是否有任务请求
        if not gSocket.accept(): continue

        Request = gSocket.receive()
        if Request == "": Print("empty request"); continue
        Print("recv:"+Request)

        Reply = handle_task(Request,gSocket)
        #Print("begin send")
        gSocket.send(Reply)
        Print("send:"+Reply)
        gSocket.close()
        """
