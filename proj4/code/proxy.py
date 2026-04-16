
"""
@authors: Jose Trigueiro 58119
"""
#!/usr/bin/env python3

# Importing libraries
from socket import *
import sys
import queue
import threading
import requests
import os


playerName = "localhost"
playerPort = 8000
buffer = queue.Queue()
done = False #variable indicating the conclusion of the producer


def producer(buffer, baseURL, movieName, track):
    global done
    
    manifestFileName = "manifest.txt"
    manifestUrl = baseURL+movieName+"/manifest.txt"
    response = requests.get(manifestUrl)
    with open(manifestFileName, "wb") as file:
        file.write(response.content)
    file = open(manifestFileName, 'r')
    
    lines = file.read().splitlines() #array with lines of the file in each index (without \n)
    
    indexOfFileNameWithTrack = lines.index(movieName+"-"+track+".mp4") #index/line having the file name with track number requested to download 

    numberOfTracks = lines[indexOfFileNameWithTrack+4] #the number of tracks is always 4 lines bellow the file name

    #video = open("video.mp4", "wb") #for testing the arrival of the video to the proxy
    videoUrl = baseURL+movieName+"/"+movieName+"-"+track+".mp4"
    for i in lines[indexOfFileNameWithTrack+5:indexOfFileNameWithTrack+5+int(numberOfTracks)]:  #the segments always starts 5 lines bellow the file name
        line = i.split(" ") #removing the spacing between the numbers of the segments line = [offset, segmentSize]
        offset = line[0]
        #print("OFFSET", offset)
        segmentSize = line[1]
        #print("SEGMENT SIZE:", segmentSize)
        offsetEnd = str(int(offset) + int(segmentSize)-1) # -1 because it starts at 0 not 1
        #print("OFFSETEND: ",offsetEnd)
        headers = {"Range": "bytes="+offset+"-"+offsetEnd}
        videoSegment = requests.get(videoUrl, headers=headers)
        #video.write(videoSegment.content)
        buffer.put(videoSegment.content)
    #video.close()
    done = True
    file.close()
    os.remove(manifestFileName)
    

def consumer(buffer, TP): 
    global done
    
    while True:
        block = buffer.get()
        TP.sendall(block)
        if done and buffer.empty(): #succeeds if the producer has concluded and there is no more content in the buffer
            break

        
def main():
    global buffer, done
    
    print("started")
    baseURL = sys.argv[1]
    movieName = sys.argv[2]
    track = sys.argv[3]
    
    TP = socket(AF_INET,SOCK_STREAM) #producer socket as in the assignment
    TP.connect((playerName, playerPort))
    
    producer_thread = threading.Thread(target=producer, args=(buffer, baseURL, movieName, track,))
    producer_thread.start()
    
    consumer_thread = threading.Thread(target=consumer, args=(buffer, TP,))
    consumer_thread.start()
    
    producer_thread.join()
    consumer_thread.join()
    
    #print(list(buffer.queue)) #for reading the buffer content
 
    TP.close()
    
    print("ended")
    
main()
