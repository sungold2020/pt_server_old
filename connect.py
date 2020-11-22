import socket

from log import *

PTPORT = 30227
SERVER = 1
CLIENT = 0
class Socket:
    def __init__(self,port=PTPORT,host="",socket_type=SERVER):
        #self.host = host if host != "" else socket.gethostname()
        self.host = "192.168.31.45"
        print(host)
        self.port = port
        self.type = socket_type

        self.socket = socket.socket()
        #self.connect = self.socket    if self.type == CLIENT else None
        self.connect = None
        self.address = None
    
    def init(self):
        if self.type == SERVER:
            try:
                self.socket.bind((self.host,self.port))
                self.socket.listen(5)
                self.socket.settimeout(60)
            except Exception as err:
                Print("fail to make socket")
                Print(err)
                return False
            else:
                return True
        else:
            try:
                self.socket.connect((self.host,self.port))
            except Exception as err:
                Print(err)
                return False
            else:
                self.connect = self.socket
                Print("connect success")
                return True

    def accept(self):
        try:
            self.connect,self.address = self.socket.accept()
            ExecLog("IP:"+self.address[0])
            Print(self.address)
        except socket.timeout:
            #Print("accept timeout")
            return False
        except Exception as err:
            Print(err)
            return False
        else:
            return True

    def receive(self):
        try:
            tData = self.connect.recv(100000)
            Request = str(tData, encoding="utf-8")
        except socket.timeout:
            Print("recv timeout")
            return ""
        except Exception as err:
            ErrorLog("recv error")
            Print(err)
            return ""
        else:
            #Print("recv:"+Request)
            socket_log("recv:"+Request)
            return Request

    def send(self,Reply):
        try:
            self.connect.sendall( bytes(Reply,encoding="utf-8") )
        except socket.timeout:
            Print("send timeout")
            return False
        except Exception as err:
            Print(err)
            return False
        else:
            #Print("send success:"+Reply)
            return True

    def close(self):
        return self.connect.close()
