# -*- coding: utf-8 -*-
"""

@author: José Trigueiro 58119
"""

import socket
import sys
import os
import select
import pickle
import random 
import math


PAYLOAD_SIZE = 1024
sock = 0

WAITING_ACKS = 0
SENDING = 1

def waitForReply( sock ):
    rx, tx, er = select.select([sock], [], [], 1)
    # waits for data or timeout after 1 second
    if rx==[]:
        return False
    else:
        return True
    
def sendDatagram (msg, sock, address):
    # msg is a byte array ready to be sent
    # Generate random number in the range of 1 to 10
    rand = random.randint(1, 10)
    # If rand is less is than 3, do not respond (20% of loss probability)
    if rand >= 3:
     sock.sendto(msg, address)
 
def main():
    
    global sock
    
    senderIP = sys.argv[1]
    senderPort = int(sys.argv[2])
    
    senderAddress = (senderIP, senderPort)
    
    receiverIP = sys.argv[3]
    receiverPort = int(sys.argv[4])
    
    receiverAddress = (receiverIP, receiverPort)
    
    fileName = sys.argv[5]
    
    windowSizeInBlocks = int(sys.argv[6])
    
    if not os.path.isfile("./"+fileName) :
        exit("File does not exist!")
    
    # Create a datagram socket
    sock = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
    
    # Bind to address and ip
    sock.bind(senderAddress)
    print("Sender is ok\n")
    
    #execute actions in the edge conducting to the initial state
    
    blocks = []
    blocks.append("a")
    #meter os pacotes numa lista
    file = open(fileName, "rb")
    offset = 0
    i = 1
    
    nBlocks = math.ceil(os.path.getsize(fileName) / PAYLOAD_SIZE) #numero de blocos a enviar
    
    # criar vetor com os pacotes
    while offset <= os.path.getsize(fileName):
        file.seek(offset)
        data = file.read(PAYLOAD_SIZE)
        if i == nBlocks:    #se é o ultimo bloco
            block = (1, i, data)
        else:
            block = (0, i, data)
        
        blocks.append(block)
        offset += PAYLOAD_SIZE
        i += 1
        
    print("sending..")
    base = 1
    seqN = 1
    error= False
    while True:  #termina quando chegar ao final do array dos blocos ou seja uma posicao sem nada
        #enviar valores da janela
        while seqN < base+windowSizeInBlocks and seqN <= nBlocks:
            packet = pickle.dumps(blocks[seqN])
            try:
                sendDatagram(packet, sock, receiverAddress)
            except:
                error = True
                break
            seqN += 1
            
        if error : # termino do sender quando o ack do ultimo bloco vindo do receiver se perde, ou seja da erro a enviar porque o receiver ja fechou
            break
            
        if waitForReply(sock):  # recebeu um ack de um pacote
            try:
                request, address = sock.recvfrom(PAYLOAD_SIZE*2)
            except:
                break
            block = pickle.loads(request)
            #status = block[0]
            cSeqN = block[1]
            if cSeqN == base:  # receiver recebeu na ordem certa, anda a janela um para a frente
                print(".")
                base += 1
                if nBlocks == cSeqN : # recebeu o ack de como o receiver recebeu o ultimo bloco
                    break
            elif cSeqN < base :# sender recebeu ack repetido(pacote perdeu-se, nao chegou ao receiver), reenvia tudo a partir do que falhou
                seqN = base
                while True: #limpar o socket dos acks repetidos
                    rx, tx, er = select.select([sock], [], [], 0)
                    if len(rx) == 0:
                        break
                    for i in rx:
                        i.recv(PAYLOAD_SIZE*2)
            else:   # acks perderam-se mas sender recebeu um mais à frente e então salta a janela para o ultimo que recebeu
                base = cSeqN
        else:   #tempo esgotou se e entao reenvia se tudo de novo dentro da janela
            seqN = base
                
       
            
      
           
    print("File Sent!")     
    file.close()       
    sock.close()
    
main()