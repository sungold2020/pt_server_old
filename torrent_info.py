#import libtorrent as lt
import os
# import hashlib
# import bencode
import requests

from log import *
import torrentool.api

"""
已废弃
从link下载种子文件，解析种子文件，获取种子信息 
"""

TORRENTS_DIR = 'data/torrents/'


class TorrentInfo:
    def __init__(self,download_link=None,torrent_file=None):
        self.torrent_file = torrent_file
        self.download_link = download_link

        #self.name = ""
        #self.total_size = 0
        #self.files = []
         

    def get_info(self):
        if self.torrent_file == None:
            if self.download_link == None: return False
            DestFullFile="data/temp.torrent"
            try:
                f=requests.get(self.download_link)
                with open(DestFullFile,"wb") as code:
                    code.write(f.content)
            except Exception as err:
                log_print(err)
                debug_log("failed to download torrent file from:" + self.download_link)
                return False
            else : 
                debug_log("success download torrent file from:" + self.download_link)
                self.torrent_file = DestFullFile

        self.torrent = torrentool.api.Torrent.from_file(self.torrent_file)
        return True
    '''
        #filename is the torrent file name
        with open(self.torrent_file,'rb') as f:
             torrent_data = f.read()
             if -1 != torrent_data.find(b"nodes"):
                info_data = torrent_data[torrent_data.find(b"info")+4:torrent_data.find(b"nodes")-2]
             else:
                info_data = torrent_data[torrent_data.find(b"info")+4:len(torrent_data) - 1]
             self.hash = hashlib.sha1(info_data).hexdigest()
             #print(self.hash)
        """
        tTRClient = PTClient("TR")
        if not tTRClient.connect(): ExecLog("failed to connect tr"); return False
        torrent_file = os.path.join(os.getcwd(),'data/temp.torrent')
        tr_torrent = tTRClient.add_torrent(torrent_file=torrent_file,download_dir="/dev/null",is_paused=True)
        if tr_torrent == None : return False
        self.hash = tr_torrent.hashString
        if tTRClient.del_torrent(self.hash) == False: ExecLog("faild to delete torrent:"+tr_torrent.name)
        """
        torrent_file = open(self.torrent_file,"rb")
        try :
            metainfo = bencode.bdecode(torrent_file.read())
        except Exception as err:
            print(err)
            return False

        info = metainfo[b'info']
        #print(info)
        #self.hash2 = hashlib.sha1(bencode.bencode(info)).hexdigest()
        #print ("hash:"+self.hash2)
        self.name = str(info[b'name'],encoding='utf8')
        #print (self.name)
        try:
            tFiles = info[b'files']
        except Exception as err:
            print (err)
            return False
        else:
            for tFile in info[b'files']:
                tSize = tFile[b'length']

                tPathList = []
                for tPath in tFile[b'path']:
                    tPathList.append(str(tPath,encoding='utf8'))
                tName = '/'.join(tPathList)
                    
                self.files.append({'name':tName,'size':tSize})

        #    print(tFile)
        return True
    '''

    @property
    def total_size(self):
        return self.torrent.total_size if self.torrent != None else 0
    @property
    def hash(self):
        return self.torrent.info_hash  if self.torrent != None else ""
    @property
    def name(self):
        return self.torrent.name       if self.torrent != None else ""
    @property
    def files(self):
        return self.torrent.files      if self.torrent != None else ""


    @staticmethod
    def download_torrent_file(download_link):
        """
        根据下载链接，下载种子文件，获取hash值，并按照hash.torrent名称保存到配置给定的目录
        返回值: hash值 失败返回""
        """
        #下载种子文件
        temp_torrent_file =os.path.join(os.path.abspath(TORRENTS_DIR),'temp.torrent')
        try:
            f=requests.get(download_link,timeout=120)
            with open(temp_torrent_file ,"wb") as code:
                code.write(f.content)
        except Exception as err:
            log_print(err)
            debug_log("failed to download torrent file from:" + download_link)
            return ""
        else : 
            debug_log("success download torrent file from:" + download_link)

        #获取torrent（包含hash等信息）
        torrent = torrentool.api.Torrent.from_file(temp_torrent_file)
        if torrent == None or torrent.info_hash == None: return "" 

        #改名hash.torrent
        torrent_file = os.path.join(os.path.abspath(TORRENTS_DIR),torrent.info_hash+'.torrent')
        try:
            os.rename(temp_torrent_file,torrent_file)
        except Exception as err:
            print(err)
            error_log("error: rename {} to {}".format(temp_torrent_file, torrent_file))
            return ""
        return torrent.info_hash



    @staticmethod
    def get_hash(torrent_file=None,download_link=None):
        if torrent_file == None: torrent_file = TorrentInfo.download_torrent_file(download_link)
        torrent = torrentool.api.Torrent.from_file(torrent_file)
        return torrent.info_hash if torrent != None else ""

    @staticmethod
    def build_torrent_info(torrent_file,download_link):
        if torrent_file == None: torrent_file = TorrentInfo.download_torrent_file(download_link)
        torrent = torrentool.api.Torrent.from_file(torrent_file)
        return torrent

    
