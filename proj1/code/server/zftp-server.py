# -*- coding: utf-8 -*-
"""

@author: José Trigueiro 58119
"""

import socket
import sys
from os.path import exists

a = "a"
localIP = "localhost"
error1 = "nack 1"
error2 = "nack 2"
error3 = "nack 3"
success = "ack 0"
bufferSize= 2048
UDP_Sport = 0
TCP_Port = 0
UDPServerSocket = 0
hasClient = False


def s_open(tcpPort, address):
    global UDPServerSocket, hasClient, TCP_Port
    if len(tcpPort) != 5:
        UDPServerSocket.sendto(error1.encode(), address)
    elif int(tcpPort) < 49152 or int(tcpPort) > 65535:
        UDPServerSocket.sendto(error2.encode(), address)
    elif hasClient:
        UDPServerSocket.sendto(error3.encode(), address)
    else:
        UDPServerSocket.sendto(success.encode(), address)
        TCP_Port = int(tcpPort)
        hasClient = True
        

def s_close(address):
    global UDPServerSocket, hasClient
    if hasClient:
        UDPServerSocket.sendto(success.encode(), address)
        hasClient = False
    else:
        UDPServerSocket.sendto(error1.encode(), address)
            

def s_get(remote_filename, local_filename, address):
    global UDPServerSocket
    if not exists(remote_filename):
        UDPServerSocket.sendto(error1.encode(), address)
        return
    elif not hasClient:
        UDPServerSocket.sendto(error2.encode(), address)
        return
    else:
        UDPServerSocket.sendto(success.encode(), address)
    
    TCPServerSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)# create TCP socket
    TCPServerSocket.connect((localIP,TCP_Port))
    print("TCP connection open!")
    
    file = open(remote_filename, "rb")
    data = file.read()
    TCPServerSocket.sendall(data)   #send file
    print("File sent!")
    file.close()
    TCPServerSocket.close()
    print("TCP connection closed!\n")


def s_put(remote_filename, local_filename, address):
    global UDPServerSocket
    if exists(remote_filename):
       UDPServerSocket.sendto(error1.encode(), address)
       return
    elif not hasClient:
        UDPServerSocket.sendto(error2.encode(), address)
        return
    else:
        UDPServerSocket.sendto(success.encode(), address)

    TCPServerSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)         # create TCP socket
    TCPServerSocket.connect((localIP, TCP_Port))
    print("TCP connection open!")

    file = open(remote_filename, "wb")
    data = -1
    print("receiving file...")
    while (data != b''):
        data = TCPServerSocket.recv(bufferSize)
        file.write(data)
    print("file received!")
    file.close()
    TCPServerSocket.close()
    print("TCP connection closed!\n")
    
    
    
def main():
    global UDP_Sport, UDPServerSocket
    UDP_Sport = int(sys.argv[1])
    
    
    # Create a datagram socket
    UDPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

    # Bind to address and ip
    UDPServerSocket.bind((localIP, UDP_Sport))
    print("server up and ready!\n")
    
    while (True):
            
        udpMsg = UDPServerSocket.recvfrom(bufferSize)  # [[comando, argumentos)], endereço]
        msg = udpMsg[0].decode().split(" ") # [comando, argumentos]
        address = udpMsg[1]
        command = msg[0]
        
        if command == "open":
            s_open(msg[1], address)
        elif command == "close":
            s_close(address)
        elif command == "get":
            s_get(msg[1], msg[2], address)
        elif command == "put":
            s_put(msg[1], msg[2], address)
        else:
            print("Command does not exist, try again!")
        
             
    UDPServerSocket.close()
main()
