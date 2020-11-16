#!/usr/bin/python3

import base64   # Encoding binary data
import json     # Creating JSON file
import os       # File path manipluation
import socket   # Creating websocket
import sys      # Reading program arguments
from time import sleep


BUFFER_SIZE = 4096  # send BUFFER_SIZE bytes each time step
HOST = "192.168.1.9"  # host of webserver (spectrumobservatory.wpi.edu)
PORT = 8080         # port the server is listening on (80)

BINNAME  = "sample.dat"     # name of the input file  TODO: standardize
JSONNAME = "sample.json"    # name of file being sent TODO: standardize

def init():
    # Setup websocket
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((HOST, PORT))
    return s

def main():
    # Setup websocket
    s = init()

    # Read in bin file (in demo the headers will be prompted for user input)
    # TODO: replace this with proper header parsing from bin file
    time        = 1
    sampleRate  = 10000
    radio       = 1

    while(True):

        # Encode data payload from bin file into base64 ascii characters
        # TODO is this as simple as opening a file and reading? (Earlier parsing can split the headers into a seperate file?)
        inputFile   = open(BINNAME, "rb")
        inputBinary = inputFile.read()
        encodedData = (base64.b64encode(inputBinary)).decode('ascii')

        # Create JSON file using encoded payload and header metadata
        jsonFormat = {"metadata":[{"rx_time" : time, "rx_sample" : sampleRate, "radio_num" : radio}], "payload" : encodedData}
        with open(JSONNAME, 'w') as outfile:
            json.dump(jsonFormat, outfile, indent=4)

        # Send this JSON file to the WebServer over a websocket connection
        # s.send(f"{JSONNAME}".encode()) ** We do not need to send the file name

        with open(JSONNAME, "rb") as f:
            while(True):
                bytesRead = f.read(BUFFER_SIZE)

                if not bytesRead:
                    break

                s.sendall(bytesRead)

        time = time + 5
        os.remove(JSONNAME)
        print(f"[+] Sleeping for 5 seconds")
        sleep(5) # TODO this sleep amount will change based on GNURadio file creation timing
        
        # TODO add some sort of handling for signal interupts? (Safely terminate while process is running in background)

if __name__ == '__main__':
    main()
