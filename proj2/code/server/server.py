# -*- coding: utf-8 -*-
"""

@author: José Trigueiro 58119
"""

import socket
import sys
import os
import random
import pickle

localHost = "localhost"
UDP_Sport = 0
UDPServerSocket = 0
suc_ok = 0
er_fileNotFound = 1
er_invalidOffset = 2

def serverReply (msg, sock, address):
    # msg is a byte array ready to be sent
    # Generate random number in the range of 1 to 10
    rand = random.randint(1, 10)
    # If rand is less is than 3, do not respond
    if rand >= 3:
        sock.sendto(msg, address)
    return

    
def main():
    global UDP_Sport, UDPServerSocket
    UDP_Sport = int(sys.argv[1])
    
    
    # Create a datagram socket
    UDPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

    # Bind to address and ip
    UDPServerSocket.bind((localHost, UDP_Sport))
    print("Server up and running!\n")
    
    while True: 
        message, address = UDPServerSocket.recvfrom(1024)
        request = pickle.loads(message)
        fileName = request[0]
        offset = request[1]
        noBytes = request[2]
        
        try:
            file = open(fileName, "rb")
        except:
            request = (er_fileNotFound, 0, 0)
            req = pickle.dumps(request)
            serverReply(req, UDPServerSocket, address)
            break
        
        if offset == os.path.getsize(fileName) :
            break
        print(f'file= {fileName},offset={offset},noBytes={noBytes}')
        
        file.seek(offset)
        data = file.read(noBytes)
        dataLength = len(data)
        
        if offset > os.path.getsize(fileName):
            request = (er_invalidOffset, dataLength, data)
        else:     
            request = (suc_ok, dataLength, data)
            
        req = pickle.dumps(request)
        serverReply(req, UDPServerSocket, address)
        
        file.close()      
        
    UDPServerSocket.close()
main()
