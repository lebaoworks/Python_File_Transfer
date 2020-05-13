import socket
import sys
import os
import json

class FTP:
    PORT = 15535
    PACKET_SIZE = 4294967296
    def __init__(self, sock):
        self.sock = sock
    
    #> Signal <#
    def send_signal(self,is_file=1):
        self.sock.send(is_file.to_bytes(1,'big'))
    def recv_signal(self):
        return self.sock.recv(1)
    
    #> Header <#
    def send_size(self, size):
        self.sock.send(size.to_bytes(8,'big'))
        self.recv_signal()
    def recv_size(self):
        recv = b''
        while len(recv) < 8:
            recv += self.sock.recv(8-len(recv))
        self.send_signal()
        return int.from_bytes(recv,'big')

    #> Data <#
    def send_data(self, data):
        #send size
        self.send_size(len(data))
        #send data
        self.sock.send(data)
        self.recv_signal()
    def recv_data(self, progress=False):
        #recv size
        length = self.recv_size()
        #recv data
        recv = b''
        while len(recv) < length:
            recv += self.sock.recv(min(FTP.PACKET_SIZE,length-len(recv)))
            if progress:
                self.__progress(len(recv),length) 
        if progress:
            print()
        self.send_signal()
        return recv

    #> File <#
    def send_file(self, path):
        name = os.path.basename(path).encode('utf-8')
        self.send_data(name)
        self.send_data(open(path,'rb').read())
    def recv_file(self):
        name = self.recv_data().decode('utf-8')
        open(name,'wb').write(self.recv_data())

    #> Folder <#
    def send_folder(self, path):
        path = os.path.abspath(path).replace('\\','/')
        directory = os.path.dirname(path)
        for root, _, filenames in os.walk(path): 
            current_path = root.replace('\\','/')
            self.send_signal(0)
            self.send_data(current_path[len(directory)+1:].encode('utf-8'))
            for filename in filenames:
                self.send_signal(1)
                name = current_path[len(directory)+1:]+'/'+filename
                self.send_data(name.encode('utf-8'))
                self.send_data(open(current_path+'/'+filename,'rb').read())
        self.send_signal(2)
    def recv_folder(self):
        signal = self.recv_signal()
        while signal != b'\02':
            if signal == b'\00':
                name = self.recv_data().decode('utf-8')
                print("[+] Folder: ",name)
                os.mkdir(name)
            if signal == b'\01':
                name = self.recv_data().decode('utf-8')
                print("[+] Get file: ",name)
                open(name,'wb').write(self.recv_data(progress=True))
            signal = self.recv_signal()
            


    def __progress(self,count,total):
        bar_len = 60
        filled_len = int(round(bar_len * count / float(total)))
        percents = round(100.0 * count / float(total), 1)
        bar = '+' * filled_len + '-' * (bar_len - filled_len)
        sys.stdout.write('\r[%s] [%3d%s] ' % (bar, percents,'%'))
        sys.stdout.flush()