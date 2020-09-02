#!/usr/bin/python3
# coding=utf-8
from mytorrent import *
from rss import *
downloadlink='https://pt.keepfrds.com/download.php?id=11284&passkey=97f4eab2ad32ebf39ee4889f6328800b'
downloadlink='https://hdhome.org/download.php?id=59181&passkey=93581f449716e0adedc71620f78513d2 '
downloadlink='https://hdsky.me/download.php?id=143622&passkey=c8c158c14e1762b0c93c91ab2ddc689a'
downloadlink='https://pt.keepfrds.com/download.php?id=11287&passkey=97f4eab2ad32ebf39ee4889f6328800b'
downloadlink='https://www.beitai.pt/download.php?id=2021&passkey=e193420544db01e767e2a214f30ec049'
tRSS=RSS(rss_name='BeiTai',download_link=downloadlink)
print(tRSS.rss_name)
print(tRSS.download_link)
print(tRSS.torrent_id)
mytorrent=MyTorrent(rss=tRSS)
print(mytorrent.torrent_id)
#mytorrent.spider_detail()
#print(mytorrent.douban_id)
#print(mytorrent.imdb_id)

list = ["ddd"]
if "" in list:
    print("correct")
from torrent_info import *
downloadlink='https://pt.keepfrds.com/download.php?id=11489&passkey=97f4eab2ad32ebf39ee4889f6328800b'
#tTorrent = TorrentInfo(torrent_file='/root/pt/data/temp.torrent')
#tTorrent = TorrentInfo(download_link = downloadlink)
#tTorrent.get_info()
#print(tTorrent.hash)
#print(tTorrent.files)
import client
tclient = PTClient("QB")
"""
tclient.connect()
download_link='https://www.beitai.pt/download.php?id=2890&passkey=e193420544db01e767e2a214f30ec049'
torrent = tclient.add_torrent(download_link=download_link,is_paused=True)
print(torrent.hash)
TR_LOGIN = {'host':"localhost", 'port':9091, 'username':'dummy', 'password':'moonbeam' }
client = transmissionrpc.Client(TR_LOGIN['host'], port=TR_LOGIN['port'],user=TR_LOGIN['username'],password=TR_LOGIN['password'])
torrent = client.add_torrent(download_link,download_dir='/dev/null',paused=True)
print (torrent)
"""
tclient.connect()
for torrent in tclient.get_all_torrents():
    print(torrent.client)
    print(torrent.name)
