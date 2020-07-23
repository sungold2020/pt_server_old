#!/usr/bin/python3
# coding=utf-8
from mytorrent import *
from rss import *
downloadlink='https://pt.keepfrds.com/download.php?id=11284&passkey=97f4eab2ad32ebf39ee4889f6328800b'
downloadlink='https://www.beitai.pt/download.php?id=2021&passkey=e193420544db01e767e2a214f30ec049'
downloadlink='https://hdhome.org/download.php?id=59181&passkey=93581f449716e0adedc71620f78513d2 '
downloadlink='https://hdsky.me/download.php?id=143622&passkey=c8c158c14e1762b0c93c91ab2ddc689a'
downloadlink='https://pt.keepfrds.com/download.php?id=11287&passkey=97f4eab2ad32ebf39ee4889f6328800b'
tRSS=RSS(rss_name='FRDS',download_link=downloadlink)
print(tRSS.rss_name)
print(tRSS.download_link)
print(tRSS.torrent_id)
mytorrent=MyTorrent(rss=tRSS)
print(mytorrent.torrent_id)
mytorrent.spider_detail()
print(mytorrent.douban_id)
print(mytorrent.imdb_id)
