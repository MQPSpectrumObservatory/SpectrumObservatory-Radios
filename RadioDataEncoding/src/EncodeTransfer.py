#!/usr/bin/python3

## Imports
import base64   # Encoding binary data
import json     # Creating JSON file
import os       # File path manipluation
# import pmt      # GNURadio header parsing
import requests # Creating HTTP requests
import sys      # Reading program arguments
import time     # Program sleep

# from gnuradio.blocks import parse_file_metadata


## Constants (!! CHANGE THESE TO REDIRECT TRAFFIC !!)
HOST = "http://spectrumobservatory.wpi.edu" # host of webserver
PORT = 5000                                 # port the server is listening on (should be 80)
BINNAME  = "sample.dat"                     # name of the input file  TODO: match GNURadio
HEADERS = {'Content-type': 'application/json', 'Accept': 'text/plain'}  # Headers for POST request

# Test Constants
TEST = 0 # If this variable equals 1, use test server and file (TODO: remove for production!)
if(TEST):
    HOST = 'http://ptsv2.com/t/aubib-1606831780/post'
    BINNAME = 'small.dat'
    # http://ptsv2.com/t/aubib-1606831780 go to this address to see test dumps (limited to 1.5KB)


## This will be called if the program recieves a SIGTERM signal
# This handles any necessary cleanup
def term(signum, frame):
    print(f"Signal number {signum} received")
    print("Terminating the program")
    exit(1)


## Main parent function
def main():

    # TODO: temp values for the header fields
    rx_time     = 1
    sampleRate  = 10000
    radio       = 1

    ## Main loop: 
    # 1. Read GNURadio output file
    # 2. Parse header info
    # 3. Encode payload
    # 4. Create JSON
    # 5. Send JSON with HTTP POST
    while(rx_time < 5):

        ## Read in bin file (in demo the headers will be prompted for user input)
        # TODO: replace this with proper header parsing from bin file

        ## Encode data payload from bin file into base64 ascii characters
        inputFile   = open(BINNAME, "rb")
        inputBinary = inputFile.read()
        encodedData = (base64.b64encode(inputBinary)).decode('ascii')

        ## Create JSON file using encoded payload and header metadata
        jsonFormat = {"metadata":[{"rx_time" : rx_time, "rx_sample" : sampleRate, "radio_num" : radio}], "payload" : encodedData}
        jsonFile = json.dumps(jsonFormat, indent=4)

        ## Send this JSON file to the WebServer with an HTTP POST
        r = requests.post(url=HOST, data=jsonFile, headers=HEADERS)
        print("[+] Response from server: %s" %r)

        ## Close, wait, and repeat process
        rx_time = rx_time + 5   # temporary time header increment
        
        # Wait to send next file (TODO: does this program need to do anything else in the meanwhile?)
        print("[+] Sleeping for 5 seconds")
        time.sleep(5) # TODO: sleep interval related to GNURadio file creation

if __name__ == "__main__":
    main()