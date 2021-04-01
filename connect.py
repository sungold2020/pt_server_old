import socket
from config import *

SERVER = 1
CLIENT = 0


class Socket:
    def __init__(self, port=0, host="192.168.31.107", socket_type=SERVER):
        # self.host = host if host != "" else socket.gethostname()
        self.host = host
        print(host)
        self.port = port if port != 0 else SysConfig.PTPORT
        print(f"port:{self.port}")
        self.type = socket_type
        self.socket = socket.socket()
        # self.connect = self.socket    if self.type == CLIENT else None
        self.connect = None
        self.address = None
    
    def init(self):
        if self.type == SERVER:
            try:
                Log.debug_log(f"bind:{self.host}:{self.port}")
                self.socket.bind((self.host, self.port))
                self.socket.listen(5)
                self.socket.settimeout(60)
            except Exception as err:
                Log.log_print("fail to make socket")
                Log.log_print(err)
                return False
            else:
                return True
        else:
            try:
                self.socket.connect((self.host, self.port))
            except Exception as err:
                Log.log_print(err)
                return False
            else:
                self.connect = self.socket
                Log.log_print("connect success")
                return True

    def accept(self):
        try:
            self.connect, self.address = self.socket.accept()
            Log.exec_log("IP:" + self.address[0])
            Log.log_print(self.address)
        except socket.timeout:
            # Print("accept timeout")
            return False
        except Exception as err:
            Log.log_print(err)
            return False
        else:
            return True

    def receive(self):
        try:
            t_data = self.connect.recv(100000)
            request = str(t_data, encoding="utf-8")
        except socket.timeout:
            Log.log_print("recv timeout")
            return ""
        except Exception as err:
            Log.error_log("recv error")
            Log.log_print(err)
            return ""
        else:
            # Print("recv:"+Request)
            Log.socket_log("recv:"+request)
            return request

    def send(self, reply):
        try:
            self.connect.sendall(bytes(reply, encoding="utf-8"))
        except socket.timeout:
            Log.log_print("send timeout")
            return False
        except Exception as err:
            Log.log_print(err)
            return False
        else:
            # Print("send success:"+Reply)
            return True

    def close(self):
        return self.connect.close()
