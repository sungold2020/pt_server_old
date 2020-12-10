import socket

from log import *
global g_config

SERVER = 1
CLIENT = 0


class Socket:
    def __init__(self, port=g_config.PTPORT, host="192.168.31.45", socket_type=SERVER):
        # self.host = host if host != "" else socket.gethostname()
        self.host = host
        print(host)
        self.port = port
        self.type = socket_type
        self.socket = socket.socket()
        # self.connect = self.socket    if self.type == CLIENT else None
        self.connect = None
        self.address = None
    
    def init(self):
        if self.type == SERVER:
            try:
                self.socket.bind((self.host, self.port))
                self.socket.listen(5)
                self.socket.settimeout(60)
            except Exception as err:
                log_print("fail to make socket")
                log_print(err)
                return False
            else:
                return True
        else:
            try:
                self.socket.connect((self.host, self.port))
            except Exception as err:
                log_print(err)
                return False
            else:
                self.connect = self.socket
                log_print("connect success")
                return True

    def accept(self):
        try:
            self.connect, self.address = self.socket.accept()
            exec_log("IP:" + self.address[0])
            log_print(self.address)
        except socket.timeout:
            # Print("accept timeout")
            return False
        except Exception as err:
            log_print(err)
            return False
        else:
            return True

    def receive(self):
        try:
            t_data = self.connect.recv(100000)
            request = str(t_data, encoding="utf-8")
        except socket.timeout:
            log_print("recv timeout")
            return ""
        except Exception as err:
            error_log("recv error")
            log_print(err)
            return ""
        else:
            # Print("recv:"+Request)
            socket_log("recv:"+request)
            return request

    def send(self, reply):
        try:
            self.connect.sendall(bytes(reply, encoding="utf-8"))
        except socket.timeout:
            log_print("send timeout")
            return False
        except Exception as err:
            log_print(err)
            return False
        else:
            # Print("send success:"+Reply)
            return True

    def close(self):
        return self.connect.close()
