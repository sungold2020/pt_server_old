#!/usr/bin/python3
import re
import os
from torrent_info import *
#Link = 'https://www.joyhd.net/download.php?id=71103&passkey=a770594966a29653632f94dce676f3b8'
Link = 'https://www.beitai.pt/download.php?id=2633&passkey=e193420544db01e767e2a214f30ec049'
#Link = 'https://hdsky.me/download.php?id=143140&passkey=c8c158c14e1762b0c93c91ab2ddc689a'
t_info = TorrentInfo(torrent_file="temp2.torrent")
#t_info = TorrentInfo(download_link=Link)
t_info.get_info()
print (t_info.total_size)
print(t_info.hash)
print(t_info.files)
