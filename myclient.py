#!/usr/bin/python3
# coding=utf-8
from client import PTClient
from mytorrent import MyTorrent

gQBClient = MyClient("QB")
gTRClient = MyClient("TR")
gTorrentList = []
class MyClient(PTClient):
    def __init__(self,mType=""):
        PTClient.__init__(mType)

    def check_torrents(self):
