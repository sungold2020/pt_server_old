#!/usr/bin/python3
# coding=utf-8
import transmissionrpc
import qbittorrentapi
import time
import requests
from torrent import Torrent
from log import *
#from torrent_info import *

TR_LOGIN = {'host':"localhost", 'port':9091, 'username':'dummy', 'password':'moonbeam' }
QB_LOGIN = {'host_port':'localhost:8989', 'username':'admin', 'password':'moonbeam' }
class PTClient:
    def __init__(self,mType=""):
        self._type = mType
        self.client = None
    
    @property
    def type(self):
        return self._type
    @type.setter
    def type(self,mType):
        if mType != "QB" and mType == "TR": ErrorLog("unknown type:"+mType); return
        self._type == mType

    def connect(self):
        try:
            if   self.type == "TR" :
                self.client = transmissionrpc.Client(TR_LOGIN['host'], port=TR_LOGIN['port'],user=TR_LOGIN['username'],password=TR_LOGIN['password'])
            elif self.type == "QB":
                self.client = qbittorrentapi.Client(host=QB_LOGIN['host_port'], username=QB_LOGIN['username'], password=QB_LOGIN['password'])            
                self.client.auth_log_in()
            else:
                return False
        except Exception as err:
            print(err)
            ErrorLog("failed to connect to "+self.type)
            return False
        else:
            DebugLog("connect to  "+self.type)
            return True

    def get_all_torrents(self):
        try:
            if   self.type == "QB": 
                return map(lambda x:Torrent(self.type,x),self.client.torrents_info())
            elif self.type == "TR": 
                return map(lambda x:Torrent(self.type,x),self.client.get_torrents())
            else                  : return []
        except Exception as err:
            print(err)
            return []

    def get_torrent(self,mhash=None):
        if mhash == None or mhash == "": 
            ErrorLog("hash is none or empty")
            return None
        try:
            if   self.type == "QB": 
                for torrent in self.client.torrents_info() :
                    if torrent.hash == mhash: return Torrent(self.type,torrent)
                return None
            elif self.type == "TR":
                #TODO
                pass
            else: return None
        except Exception as err:
            print(err)
            return None

    def add_torrent(self,download_link=None,torrent_file=None,download_dir=None,is_paused=True,is_root_folder=True,is_skip_checking=False,category=None):
        if download_link == None and torrent_file == None: ErrorLog("empty download link or torrent"); return None
        if torrent_file == None: torrent_file = download_torrent_file(download_link)
        if torrent_file == "": return None
        try:
            if   self.type == "TR":  
                DebugLog("add torrent_file to tr:"+torrent_file)
                return Torrent(self.type,self.client.add_torrent(torrent_file,download_dir=download_dir,paused=is_paused))
            elif self.type == "QB":
                tReturn = self.client.torrents_add(urls=download_link,torrent_files=torrent_file,save_path=download_dir,paused=is_paused,category=category,is_skip_checking=is_skip_checking,is_root_folder=is_root_folder) 
                if tReturn != "Ok.": return None
                time.sleep(10)
                tHASH = get_hash(torrent_file=torrent_file,download_link=download_link)
                if tHASH == "": return None
                else          : return self.get_torrent(tHASH)
            else                  : 
                return None
        except Exception as err:
            print(err)
            return None

    def del_torrent(self,mHASH,is_delete_file=False):
        print(self.type+'|'+mHASH)
        if mHASH == None or mHASH == "": return False
        if mHASH == "": return False
        try:
            if   self.type == "TR": return self.client.remove_torrent(mHASH,delete_data=is_delete_file)
            elif self.type == "QB": self.client.torrents_delete(is_delete_file,mHASH)
            else                  : return False
        except Exception as err:
            print(err)
            print("error:delete torrent")
            return False
        else:
            return True

    def shutdown(self):
        try:
            if   self.type == "QB": self.client.app_shutdown()
            elif self.type == "TR": return False                #TODO
            else                  : return False
            return True
        except Exception as err:
            print(err)
            ErrorLog("failed to shutdown "+self.type)
            return False

    def start(self):
        if   self.type == "QB":
            if os.system("/usr/bin/qbittorrent &") == 0 : ExecLog ("success to start qb"); return True
            else                                        : ExecLog("failed to start qb"); return False
        elif self.type == "TR":
            #TODO
            pass
        else: pass

    def restart(self):
        if not (self.connect() and self.shutdown()): return False
        time.sleep(300)
        if not self.start(): return False
        return True

    def set_category(self,mHASH,mCategory):
        if   self.type == "QB":
            try:
                self.client.torrents_setCategory(mCategory,mHASH)
            except Exception as err:
                print(err)
                return False
            else:
                return True
        elif self.type == "TR":
            return False
        else:
            return False
        

def get_hash(torrent_file=None,download_link=None):
    tTRClient = PTClient("TR")
    if not tTRClient.connect(): ExecLog("failed to connect tr"); return ""
    print("begin add tr")
    tTorrent = tTRClient.add_torrent(torrent_file=torrent_file,download_link=download_link,download_dir="/dev/null",is_paused=True)
    if tTorrent == None : return ""
    tHASH = tTorrent.hash
    time.sleep(5)
    print("begin delete tr")
    if tTRClient.del_torrent(tHASH) == False: ExecLog("faild to delete torrent:"+tTorrent.name)
    return tHASH

def download_torrent_file(download_link):
    DestFullFile=os.path.abspath("data/temp.torrent")
    try:
        f=requests.get(download_link,timeout=120)
        with open(DestFullFile,"wb") as code:
            code.write(f.content)
    except Exception as err:
        Print(err)
        DebugLog("failed to download torrent file from:"+download_link)
        return ""
    else : 
        DebugLog("success download torrent file from:"+download_link)
        return DestFullFile

