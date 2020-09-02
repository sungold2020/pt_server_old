#!/usr/bin/python3
import re
#from ptsite import *

"""
tSite = None
for site in NexusPage.site_list:
    if 'FRDS' == site['name']: 
        tSite = site
        break
print("find site:{}".format(tSite['name']))
            
tPage = NexusPage(tSite)
if not tPage.request_detail_page('11252'):
    print("failed to request detail")
"""


string='你好,，。'
#string2 = re.sub(u"[\u4e00-\u9f50]+","",string) #去掉name中的中文字符
#print(len(string2))
#print(len(string))
string = re.sub("[,。，]+","",string)       #去掉特殊标点符号
print(string)

from client import PTClient
#from torrent import Torrent
global gQBClient
global gTRClient
gQBClient=PTClient("QB")
gQBClient.connect()
gTRClient = PTClient("TR")
gTRClient.connect()
for torrent in gQBClient.get_all_torrents():
    for tracker in torrent.trackers:
        if tracker['url'].find("http") >= 0 and tracker["status"] != 2:
            print(torrent.name)
            print(tracker)
