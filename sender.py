from ftp import FTP
import socket
from datetime import datetime

serv_sock = socket.socket()
serv_sock.bind(('0.0.0.0', FTP.PORT))
serv_sock.listen(1)
print('Server listening...')

sock, addr = serv_sock.accept()
print('Got connection from: ', addr)

#####################################################################################
ftp = FTP(sock)
start=datetime.now()
ftp.send_folder('D:\\Games\\Ori')
print('Send done!')


#####################################################################################
sock.close()
serv_sock.close()
print('connection closed')
