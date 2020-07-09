#!/usr/bin/python3
# coding=utf-8
import os
import re
import sys
import shutil
import datetime
import socket


#command="hello world2"
del sys.argv[0]
command=' '.join(sys.argv)

s = socket.socket()
host = socket.gethostname()
port = 12346
try:
    s.connect((host,port))
except Exception as err:
    print(err)
    exit()
print("connect success")

# 发送请求
try:
    s.send(bytes(command,encoding="utf-8"))
except Exception as err:
    print(err)
    exit()
else:
    print("send:")
    print("     "+command)

#接收返回
try:
    data = s.recv(1024)
except Exception as err:
    print("recv error")
    print(err)
else:
    string = str(data,encoding="utf8")
    print("recv:")
    print("     "+string)

s.close()
