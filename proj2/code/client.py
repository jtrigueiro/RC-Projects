# -*- coding: utf-8 -*-
"""

@author: José Trigueiro 58119
"""

import socket
import sys
import os
import select
import pickle


localHost = "localhost"
UDPClientSocket = 0
UDP_Sport = 0
UDP_Cport = 49500
serverAddress = 0
suc_ok = 0
er_fileNotFound = 1
er_invalidOffset = 2
validFile = True

def waitForReply( uSocket ):
    rx, tx, er = select.select([UDPClientSocket], [], [], 1)
    # waits for data or timeout after 1 second
    if rx==[]:
        return False
    else:
        return True

def main():
    
    global UDPClientSocket, UDP_Sport, validFile
    #serverName = sys.argv[1]
    UDP_Sport = int(sys.argv[2])
    if len(str(UDP_Sport)) != 5:
        exit("Invalid port length");
    elif UDP_Sport < 49152 or UDP_Sport > 65535:
        exit("Invalid port number");
    serverAddress = (localHost, UDP_Sport)
    
    fileName = sys.argv[3]
    chunkSize = int(sys.argv[4])
    if chunkSize > 65482:
        exit("Ivalind chunk size, maximum UDP datagram data size allowed is 65482 bytes")
        
        
        
    # Create a UDP socket at client side
    UDPClientSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
    UDPClientSocket.bind((localHost, UDP_Cport))
    print("Client is ok\n")
    
    file = open(fileName, "wb")
    offset = 0
    while True:
        request = (fileName, offset, chunkSize)
        req = pickle.dumps(request)
        UDPClientSocket.sendto(req, serverAddress)
        
        if not waitForReply(UDPClientSocket):
            print("Data loss :(")
            continue
           
        try:
            message, address = UDPClientSocket.recvfrom(chunkSize*2)
        except:
            break
        
        request = pickle.loads(message)
        status = request[0]
        dataSent = request[1]
        data = request[2]
        if status == er_fileNotFound:
            validFile = False
            print("File not found!")
            break
        
        if dataSent == 0 :
            break
        else:
            file.write(data)
            offset = offset + dataSent
               
    if validFile:
        file.close()
    else:
        file.close()
        os.remove(fileName)
    
    UDPClientSocket.close()
main()