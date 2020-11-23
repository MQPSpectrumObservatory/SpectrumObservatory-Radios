#!/usr/bin/python3

# Imports
import base64   # Encoding binary data
import json     # Creating JSON file
import os       # File path manipluation
import pmt      # GNURadio header parsing
import socket   # Creating websocket
import sys      # Reading program arguments
import time     # Program sleep

from gnuradio.blocks import parse_file_metadata

# Constants
BUFFER_SIZE = 4096                      # send BUFFER_SIZE bytes each time step
HOST = "spectrumobservatory.wpi.edu"    # host of webserver
PORT = 5000                             # port the server is listening on

BINNAME  = "sample.dat"     # name of the input file  TODO: match GNURadio
JSONNAME = "sample.json"    # name of file being sent


# This is called once at the start of the program's execution
# Returns: the websocket descriptor
def init():
    # Setup websocket
    global s
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((HOST, PORT))
    print("[*] Connected to Server")
    return None


# This will be called if the program recieves a SIGTERM signal
# This closes the websocket and handles any other necessary cleanup
def term(signum, frame):
    print(f"Signal number {signum} received")
    print("Terminating the program")
    s.close()
    exit(1)


# Main parent function
def main():

    # TODO: temp values for the header fields
    rx_time     = 1
    sampleRate  = 10000
    radio       = 1

    ## Main loop: 
    # 0. Reconnect to socket (possible temporary measure)
    # 1. Read GNURadio output file
    # 2. Parse header info
    # 3. Encode payload
    # 4. Create JSON
    # 5. Send JSON
    # 6. Disconnect, wait, and repeat
    while(True):
        ## Create socket and connect to server
        init()

        ## Read in bin file (in demo the headers will be prompted for user input)
        # TODO: replace this with proper header parsing from bin file

        ## Encode data payload from bin file into base64 ascii characters
        inputFile   = open(BINNAME, "rb")
        inputBinary = inputFile.read()
        encodedData = (base64.b64encode(inputBinary)).decode('ascii')

        ## Create JSON file using encoded payload and header metadata
        jsonFormat = {"metadata":[{"rx_time" : rx_time, "rx_sample" : sampleRate, "radio_num" : radio}], "payload" : encodedData}
        with open(JSONNAME, 'w') as outfile:
            json.dump(jsonFormat, outfile, indent=4)

        ## Send this JSON file to the WebServer over a websocket connection
        with open(JSONNAME, "rb") as f:
            while(True):
                bytesRead = f.read(BUFFER_SIZE)

                # If no bytes were read in, EOF
                if not bytesRead:
                    break

                s.sendall(bytesRead)
        os.remove(JSONNAME)     # remove the transmitted json file

        ## Close, wait, and repeat process
        rx_time = rx_time + 5   # temporary time header increment
        
        s.close()

        # Wait to send next file (TODO: does this program need to do anything else in the meanwhile?)
        print("[+] Sleeping for 5 seconds")
        time.sleep(5) # TODO: sleep interval related to GNURadio file creation
