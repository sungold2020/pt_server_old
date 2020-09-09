#!/usr/bin/python3
# coding=utf-8
import os
import re
import sys
import shutil
import datetime
from connect import *

sys_argv = sys.argv
del sys_argv[0]
Task = sys.argv[0]
command=' '.join(sys_argv)

#gSocket = Socket(12346,"192.168.31.45",socket_type=CLIENT)
gSocket = Socket(socket_type=CLIENT)
if not gSocket.init(): print("failed to connect"); exit()
print(gSocket.host)
print(gSocket.port)

# 发送请求
if gSocket.send(command):
    print("send:")
    print("     "+command)
    pass
else:
    exit()

#接收返回
reply = gSocket.receive()
print("recv:")
print("     "+reply)


if Task == 'spider':
    if reply == "2+ matching torrent":
        while True:
            receive = gSocket.receive()
            if receive == 'end': exit()
            choose = input(receive)
            gSocket.send(choose)
