#!/usr/bin/python3
# coding=utf-8
from mytorrent import *
from rss import *
downloadlink='https://pt.keepfrds.com/download.php?id=11263&passkey=97f4eab2ad32ebf39ee4889f6328800b'
tRSS=RSS(rss_name='FRDS',download_link=downloadlink)
print(tRSS.rss_name)
print(tRSS.download_link)
print(tRSS.torrent_id)
mytorrent=MyTorrent(rss=tRSS)
print(mytorrent.torrent_id)
mytorrent.spider_detail()
print(mytorrent.douban_id)
print(mytorrent.imdb_id)
