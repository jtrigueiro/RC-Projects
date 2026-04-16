# -*- coding: utf-8 -*-
"""

@author: José Trigueiro 58119
"""

import socket
import sys
import os
import random
import pickle
import select

sock = 0
PAYLOAD_SIZE = 1024


def sendDatagram (msg, sock, address):
    # msg is a byte array ready to be sent
    # Generate random number in the range of 1 to 10
    rand = random.randint(1, 10)
    # If rand is less is than 3, do not respond
    if rand >= 3:
        sock.sendto(msg, address)
    return

    
def main():
    global sock
    
    receiverIP = sys.argv[1]
    receiverPort = int(sys.argv[2])
    
    receiverAddress = (receiverIP, receiverPort)
    
    fileNameInReceiver = sys.argv[3]
    
    # Create a datagram socket
    sock = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

    # Bind to address and ip
    sock.bind(receiverAddress)
    print("Receiver up and running!\n")   
    

    file = open(fileNameInReceiver, "wb")
    cSeqN = 1
    
    print("receiving..")
    while True:
        packet, senderAddress = sock.recvfrom(PAYLOAD_SIZE*2)
        
        block = pickle.loads(packet)
        status = block[0]
        seqN = block[1]
        data = block[2]
        
        if cSeqN == seqN:
            print(".")
            file.write(data)
            ack = (1, cSeqN)
            packet = pickle.dumps(ack)
            sendDatagram(packet, sock, senderAddress)
            cSeqN += 1
            if status == 1:
                break
        else:
            ack = (1, cSeqN-1)
            packet = pickle.dumps(ack)
            sendDatagram(packet, sock, senderAddress)
                   
            
    print("File received!")   
    file.close()       
    sock.close()
main()
