#!/usr/bin/python3
# coding=utf-8
import datetime
import time
import socket
import os
import transmissionrpc
import qbittorrentapi

import movie
from torrent import Torrent
from log import *
from rss import *
from pt_site import *

#运行设置############################################################################
#日志文件
PTPORT = 12346
#TR/QB的连接设置    
TR_LOGIN = {'host':"localhost", 'port':9091, 'username':'dummy', 'password':'moonbeam' }
QB_LOGIN = {'host_port':'localhost:8989', 'username':'admin', 'password':'moonbeam' }


#可变全局变量
gPTIgnoreList = []
gTorrentList = [] 
global gLastCheckDate
gLastCheckDate = "1970-01-01"
global gIsNewDay
gIsNewDay = False
global gToday
gToday = "1970-01-01"


def check_torrents(mClient):
    """
    进行TR/QB的所有种子进行检查和分析，并更新列表
    1、检查DIRName是否存在，否则暂停种子
    2、NEWDAY下：比对所有文件，大小，错误，暂停种子
    3、QB下，检查标签设置
    4、更新种子信息列表（增加，删除，更新）
    5、NEWDAY：计算DATA，低于阈值的暂停种子
    
    返回值：-1:错误，0:无更新，1:有更新 ，用于指示是否需要备份文件
    """
    global gTorrentList
    
    tNumberOfAdded = tNumberOfDeleted = tNumberOfUpdated = 0

    #连接Client并获取TorrentList列表
    try:
        if mClient == "TR" :
            tr_client = transmissionrpc.Client(TR_LOGIN['host'], port=TR_LOGIN['port'],user=TR_LOGIN['username'],password=TR_LOGIN['password'])
        else :
            qb_client = qbittorrentapi.Client(host=QB_LOGIN['host_port'], username=QB_LOGIN['username'], password=QB_LOGIN['password'])            
            qb_client.auth_log_in()
        DebugLog("connect to  "+mClient)
    except Exception as err:
        print(err)
        ErrorLog("failed to connect to "+mClient)
        return -1

    # 开始逐个获取torrent并检查
    if mClient == "QB":
        tTorrents = qb_client.torrents_info()            
    else:
        tTorrents = tr_client.get_torrents()
    for tOriginalTorrent in tTorrents: 
        
        tTorrent = Torrent(mClient,tOriginalTorrent)
        tDestDir = os.path.join(tTorrent.save_path,tTorrent.name)
        if not os.path.isdir(tDestDir):
            print("not dir:"+tDestDir)
            continue
        if  tTorrent.save_torrent_file(tDestDir):
            print("success:"+tTorrent.name)
        else:
            print("failed:"+tTorrent.name)
        

check_torrents("TR")
