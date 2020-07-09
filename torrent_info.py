#import libtorrent as lt
import os
import hashlib
import bencode
import requests

from log import *

"""
从link下载种子文件，解析种子文件，获取种子信息
"""


class TorrentInfo:
    def __init__(self,download_link="",torrent_file=""):
        self.torrent_file = torrent_file
        self.download_link = download_link

        self.hash = ""
        self.name = ""
        #self.total_size = 0
        self.files = []
         

    def get_info(self):
        if self.torrent_file == "":
            if self.download_link == "": return False
            DestFullFile="temp.torrent"
            try:
                f=requests.get(self.download_link)
                with open(DestFullFile,"wb") as code:
                    code.write(f.content)
            except Exception as err:
                Print(err)
                DebugLog("failed to download torrent file from:"+self.download_link)
                return False
            else : 
                DebugLog("success download torrent file from:"+self.download_link)
                self.torrent_file = DestFullFile

        #filename is the torrent file name
        with open(self.torrent_file,'rb') as f:
             torrent_data = f.read()
             if -1 != torrent_data.find(b"nodes"):
                info_data = torrent_data[torrent_data.find(b"info")+4:torrent_data.find(b"nodes")-2]
             else:
                info_data = torrent_data[torrent_data.find(b"info")+4:len(torrent_data) - 1]
             self.hash = hashlib.sha1(info_data).hexdigest()
             #print(self.hash)

        torrent_file = open(self.torrent_file,"rb")
        try :
            metainfo = bencode.bdecode(torrent_file.read())
        except Exception as err:
            print(err)
            return True

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


    @property
    def total_size(self):
        total_size = 0
        for tFile in self.files:
            total_size += tFile['size']

        return total_size
