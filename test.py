#!/usr/bin/python3
# coding=utf-8
downloadlink='https://pt.keepfrds.com/download.php?id=11284&passkey=97f4eab2ad32ebf39ee4889f6328800b'
downloadlink='https://hdhome.org/download.php?id=59181&passkey=93581f449716e0adedc71620f78513d2 '
downloadlink='https://hdsky.me/download.php?id=143622&passkey=c8c158c14e1762b0c93c91ab2ddc689a'
downloadlink='https://pt.keepfrds.com/download.php?id=11287&passkey=97f4eab2ad32ebf39ee4889f6328800b'
downloadlink='https://www.beitai.pt/download.php?id=2021&passkey=e193420544db01e767e2a214f30ec049'

list = ["ddd"]
if "" in list:
    print("correct")
downloadlink='https://pt.keepfrds.com/download.php?id=11489&passkey=97f4eab2ad32ebf39ee4889f6328800b'
#tTorrent = TorrentInfo(torrent_file='/root/pt/data/temp.torrent')
#tTorrent = TorrentInfo(download_link = downloadlink)
#tTorrent.get_info()
#print(tTorrent.hash)
#print(tTorrent.files)
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

download_link=" https://pt.m-team.cc/download.php?id=427572&passkey=7044b36a9057090e36138df761ddfc5d&https=1"
download_link="https://pt.keepfrds.com/download.php?id=11509&passkey=97f4eab2ad32ebf39ee4889f6328800b"

"""
import qbittorrentapi

try:
    client = qbittorrentapi.Client(host='localhost:8989', username='admin', password='adminadmin')
    client.auth_log_in()
    client.torrents_delete(True,'d63b454fcdf172cf2e33f7847671f8418936d5dd');
except Exception as err:
    print(err)
else:
    print("success")
"""
import re
mSummary = "https://movie.douban.com/subject/123456   \nss"
tResult = re.search("movie\.douban\.com\/subject\/\d+",mSummary)
if tResult != None: DoubanLink = "https://"+tResult.group()
print(DoubanLink)
mSummary="dddd https://www.imdb.com/title/tt9894470/ ddd"
tResult = re.search("www\.imdb\.com\/title\/tt\d+",mSummary)
if tResult != None: IMDBLink = "https://"+tResult.group()
print(IMDBLink)

from torrent_info import *
torrent = TorrentInfo(torrent_file="data/temp.torrent")
torrent.get_info()
print(torrent.hash)
