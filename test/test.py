#!/usr/bin/python3
# coding=utf-8
import sys
import os

from config import *
from ptsite2 import *
from sites import *
from use import *
SysConfig.load_sys_config("config/sys.json")
SysConfig.load_site_config("config/site.json")
Sites.load(SysConfig.SITE_LIST)
for site in Sites.site_list:
    site.print()
Use.run()
Sites.reload(SysConfig.SITE_LIST)
for site in Sites.site_list:
    site.print()

"""
from config import *

for site in g_site_list:
    print(f"----{site.site_name}")
    print(site.url)
    print(site.first_url)
    print(site.last_url)
    print(site.cookie)
    print(site.detail_url)
    print(site.download_url)
    print(site.referer)
    print(site.host)
    print(site.time_interval)
    print(site.auto)
    print(site.manual)
    print("  rss")
    for rss in site.rss_list:
        print(rss)

if len(sys.argv) == 2:
    input_name = sys.argv[1]
else:
    exit()
dir_name, file_name = mylib.split(input_name)
print(f"mylib.split:   {dir_name}, {file_name}")
dir_name, file_name = os.path.split(input_name)
print(f"os.path.split: {dir_name}, {file_name}")
import ptmonitor
ptmonitor.backup_daily()
from client import *

client = PTClient("TR")

client.connect()

torrents = client.get_all_torrents()
#print(len(torrents))

for torrent in torrents:
   #print(torrent.name)
   #print(torrent.save_path)
   #torrent.stop()
   torrent.torrent.locate_data("/media/root/BT")
   #print(torrent.save_path)


from client import *
from torrents import *


def in_torrent_list(saved_path, dir_name):

    for i in range(len(torrent_list)):
        t_src_dir_name = os.path.join(saved_path, dir_name)
        if len(torrent_list[i].files) == 0:
            continue
        first_file = os.path.realpath(os.path.join(torrent_list[i].save_path,
                                                   torrent_list[i].files[0]['name']))
        if t_src_dir_name in first_file:
            return True
    return False


client = PTClient("QB")
client.connect()
torrent_list = []
for torrent in client.get_all_torrents():
    torrent_list.append(MyTorrent(torrent,None))
    first_file = os.path.realpath(os.path.join(torrent.save_path, torrent.files[0]['name']))
    #print(first_file)

disk_path="E:\movies"
for file in os.listdir(disk_path):
    fullpathfile = os.path.join(disk_path, file)
    print(fullpathfile)
    if in_torrent_list(disk_path, file):
        #print(file + "::find in torrent list:")
        pass
    else:
        print(file + "::not find in torrent list:")


"""
