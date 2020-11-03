#!/usr/bin/python3

import base64   # Encoding binary data
import json     # Creating JSON file
import os       # File path manipluation
import socket   # Creating websocket
import sys      # Reading program arguments

BUFFER_SIZE = 4096  # send BUFFER_SIZE bytes each time step
HOST = "localhost"  # host of webserver (spectrumobservatory.wpi.edu)
PORT = 8080         # port the server is listening on (80)

BINNAME  = "sample.dat"     # name of the input file  TODO: standardize
JSONNAME = "sample.json"    # name of file being sent TODO: standardize


def main():
    # Setup websocket
    s = socket.socket()
    s.connect((HOST, PORT))

    # Read in bin file (in demo the headers will be prompted for user input)
    # TODO: replace this with proper header parsing from bin file
    print("Enter header metadata info")
    time        = int(input("Time: "))
    sampleRate  = int(input("Sample rate: "))
    radio       = int(input("Radio number: "))

    # Encode data payload from bin file into base64 ascii characters
    inputFile   = open(BINNAME, "rb")
    inputBinary = inputFile.read()
    encodedData = (base64.b64encode(inputBinary)).decode('ascii')

    # Create JSON file using encoded payload and header metadata
    jsonFormat = {"metadata":[{"rx_time" : time, "rx_sample" : sampleRate, "radio_num" : radio}], "payload" : encodedData}
    with open(JSONNAME, 'w') as outfile:
        json.dump(jsonFormat, outfile, indent=4)

    # Send this JSON file to the WebServer over a websocket connection
    s.send(f"{JSONNAME}".encode())

    with open(JSONNAME, "rb") as f:
        while(True):
            bytesRead = f.read(BUFFER_SIZE)

            if not bytesRead:
                break

            s.sendall(bytesRead)

    s.close()

    os.remove(JSONNAME)
    
if __name__ == '__main__':
    main()