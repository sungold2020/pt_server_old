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

downloadlink='https://www.beitai.pt/download.php?id=2021&passkey=e193420544db01e767e2a214f30ec049'

string = "avgv"
print(f"{string.ljust(10)} ipload")

        #tTorrentName = re.sub(u"[\u4e00-\u9f50]+","",self.name) #去掉name中的中文字符
ch = '。'
if '\u4e00' <= ch <= '\u9fff':
    print("it is chinese")
import re
string = "hello world"
if re.search(u"[\u4e00-\u9f50]+",string) != None:
    print("contain chinese")


import json
text = open('info_json.txt').read()
text = text.replace('\\','\\\\')
print(text)
json_data = json.loads(text,strict=False)
print(json_data.get("genre"))
