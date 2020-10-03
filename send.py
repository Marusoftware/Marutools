#! /usr/bin/python3
import socket
import tkfilebrowser
import os
import time
from tkinter import simpledialog
import tkinter

tkinter.Tk().withdraw()
##name=simpledialog.askstring("name","name:")
##password=simpledialog.askstring("password","password:")
up_pbyte = 1024
file_name=tkfilebrowser.askopenfilename()
file_size = os.path.getsize(file_name)
version="b1.1"
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
print("connecting...",end='')
r = s.connect(('192.168.1.14', 50001))
print("connected")
s.send(b'upload_program')
while 1:
    data = s.recv(1024)
    print('Client recieved data :'+str(data))
##    if data == b"name:":
##        s.send(bytes("name="+str(name),"utf-8"))
##    elif data == b'password:':
##        s.send(bytes("password="+password,"utf-8"))
    if data == b'file_name:':
        s.send(bytes("file_name=maruediter/"+version+"/"+os.path.basename(file_name),"utf-8"))
    elif data == b'upload OK':
        while data != b'upload START':
            data = s.recv(1024)
            if data == b'file_size:':
                s.send(int(file_size).to_bytes(10, 'big'))
            elif data == b'speed:':
                s.send(int(up_pbyte).to_bytes(2, 'big'))
            else:
                break
        s.settimeout(None)
        f = open(file_name, "rb")
        uploaded = 0
        print("uploading...", end="")
        while 1:
            s.send(f.read(up_pbyte))
            uploaded = uploaded + up_pbyte
            if file_size <= uploaded:
                break
        break
    else:
        pass
print("completed!")
s.close()
