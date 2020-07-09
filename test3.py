#!/usr/bin/python3

import qbittorrentapi
from my_torrent import *

QB_LOGIN = {'host_port':'localhost:8989', 'username':'admin', 'password':'moonbeam' }
qb_client = qbittorrentapi.Client(host=QB_LOGIN['host_port'], username=QB_LOGIN['username'], password=QB_LOGIN['password'])            
qb_client.auth_log_in()

for torrent in qb_client.torrents_info():
    tTorrent = MyTorrent(Torrent("QB",torrent),None,None)
    print(tTorrent.status)
    break
