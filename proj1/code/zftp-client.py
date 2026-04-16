# -*- coding: utf-8 -*-
"""

@author: José Trigueiro 58119
"""

import socket
import sys
from os.path import exists


bufferSize = 2048
serverName = "localhost"
UDPClientSocket = 0
UDP_Sport = 0
serverAddress = 0
TCP_Port = 0

# this command starts an interaction session, sending to the server the TCP port number
#where the client will be waiting for connections. 
def c_open(port):
    global UDPClientSocket, serverAddress, TCP_Port
    UDPClientSocket.sendto(("open "+port).encode(), serverAddress)
    recvMsg = UDPClientSocket.recvfrom(bufferSize) #[[ack/nack, errornumber], serverAddress]
    msg = recvMsg[0].decode().split(" ") # [ack/nack, erronumber]
    
    if msg[0] == "nack":
        if msg[1] == "1":
            print("invalid number of arguments")
        elif msg[1] == "2":
            print("invalid port number")
        else:
            print("server busy, come back later")
    else:
        TCP_Port = port
        print("interaction on!")

# this command ends an interaction session.
def c_close():
    global UDPClientSocket, TCP_Port
    UDPClientSocket.sendto("close".encode(), serverAddress)
    recvMsg = UDPClientSocket.recvfrom(bufferSize) #[[ack/nack, errornumber], serverAddress]
    msg = recvMsg[0].decode().split(" ") # [ack/nack, erronumber]
    if msg[0] == "nack":
        print("no interaction in progress")
    else:
        TCP_Port = 0
        print("interaction closed!")

# this command downloads a file from the server, this means to transfer a file from the
#server file system to the client´s file system. 
def c_get(remote_filename, local_filename):
    global UDPClientSocket, serverAddress
    if exists(local_filename):
        print("a file with the indicated name already exists on the client")
        return
    
    UDPClientSocket.sendto(("get "+remote_filename+" "+local_filename).encode(), serverAddress)
    recvMsg = UDPClientSocket.recvfrom(bufferSize)
    msg = recvMsg[0].decode().split(" ")
    if msg[0] == "nack":
        if msg[1] == "1":
            print("the indicated file does not exist on the server")
        elif msg[1] == "2":
            print("no server interaction, please open!")
    else:
        TCPClientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        TCPClientSocket.bind((serverName, int(TCP_Port)))
        TCPClientSocket.listen()
        conn, addr = TCPClientSocket.accept()
        file = open(local_filename, "wb")
        data = -1
        print("receiving file...")
        while data != b'':
            data = conn.recv(bufferSize)
            file.write(data)
        print("file received!")
        file.close()
        TCPClientSocket.close()
    
# this command uploads a file to the server, this means transfer a file in the client file
#system to the server´s file system. 
def c_put(remote_filename, local_filename):
    if not exists(local_filename):
       print("The indicated file does not exist on the client")
       return

    UDPClientSocket.sendto(("put " + remote_filename + " " + local_filename).encode(), serverAddress)
    recvMsg = UDPClientSocket.recvfrom(bufferSize)
    msg = recvMsg[0].decode().split()
    if msg[0] == "nack":
        if msg[1] == "1":
            print("a file with the indicated name already exists on the server")
        elif msg[1] == "2":
            print("no server interaction, please open!")    
    else:
        TCPClientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        TCPClientSocket.bind((serverName, int(TCP_Port)))
        TCPClientSocket.listen()
        conn, addr = TCPClientSocket.accept()

        file = open(local_filename, "rb")
        data = file.read()
        conn.sendall(data)

        file.close()
        TCPClientSocket.close()


def main():
    global UDPClientSocket, UDP_Sport, serverAddress, serverName
    #serverName = sys.argv[1]
    UDP_Sport = int(sys.argv[2])
    serverAddress = (serverName, UDP_Sport)
    
    # Create a UDP socket at client side
    UDPClientSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
    print("Client is ok")
    

    while True: 
        msg = input("> ").split()
        command = msg[0]
        if command == "open":
            c_open(msg[1])
        elif command == "close":
            c_close()
        elif command == "get":
           try:
               c_get(msg[1], msg[2])
           except:
               print("invalid number of arguments")
        elif command == "put":
            try:
                c_put(msg[1], msg[2])
            except:
                print("invalid number of arguments")
        else:
            print("Command does not exist, try again!")
            
    UDPClientSocket.close()
main()