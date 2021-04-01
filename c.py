#!/usr/bin/python3
# coding=utf-8
import sys

from connect import *

SysConfig.load_sys_config("config/sys.json")

sys_argv = sys.argv
del sys_argv[0]
Task = sys.argv[0]
command = ' '.join(sys_argv)

gSocket = Socket(socket_type=CLIENT)
if not gSocket.init():
    print("failed to connect")
    exit()
print(gSocket.host)
print(gSocket.port)

# 发送请求
if gSocket.send(command):
    print("send:")
    print("     "+command)
    pass
else:
    exit()

# 接收返回
reply = gSocket.receive()
print("recv:")
print("     "+reply)


if Task == 'spider':
    if reply == "2+ matching torrent":
        while True:
            receive = gSocket.receive()
            if receive == 'end':
                exit()
            choose = input(receive)
            gSocket.send(choose)
