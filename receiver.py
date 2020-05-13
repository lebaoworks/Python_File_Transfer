from ftp import FTP
import socket

sock = socket.socket()
sock.connect(('192.168.1.122',FTP.PORT))
print("Connected to server")

#####################################################################################
ftp = FTP(sock)
recv = ftp.recv_folder()


#####################################################################################
sock.close()
print('connection closed')