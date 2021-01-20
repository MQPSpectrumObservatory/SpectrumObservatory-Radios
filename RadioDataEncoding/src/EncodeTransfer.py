#!/usr/bin/python3

## Imports
import base64   # Encoding binary data
import json     # Creating JSON file
import os       # File path manipluation
import pmt      # GNURadio header parsing
import requests # Creating HTTP requests
import sys      # Reading program arguments
import time     # Program sleep

from gnuradio.blocks import parse_file_metadata # GNURadio header parsing

## Constants
HOST        = "http://spectrumobservatory.wpi.edu:5000/data1"               # host of webserver
BINNAME     = "sample_header.dat"                                          # name of the input file
HEADERS     = {'Content-type': 'application/json', 'Accept': 'text/plain'} # Headers for POST request
NITEMS      = 1000000                                                      # Number of samples per header (match to GNURadio)

# Test Constants -> (points to local test server)
TEST = 0
if(TEST):
    HOST = 'http://localhost:3000/data'
    BINNAME = 'sample_header.dat'


## Called if the program recieves a SIGTERM signal # NOTE: Invoked by daemon
# This handles any necessary cleanup
def term(signum, frame):
    print(f"[o] Signal number {signum} received")
    print("[o] Terminating the program")
    exit(1)


## This will be called to parse header data out of the dat file
# Takes in an open file descriptor and returns a python dictionary
def parseHeaders(file):

    # read out header bytes into a string
    header_str = file.read(parse_file_metadata.HEADER_LENGTH)

    # Convert from created string to PMT dict
    try:
        header = pmt.deserialize_str(header_str)
    except RuntimeError:
        sys.stderr.write("[x] Could not deserialize header: file may be invalid or corrupt\n")
        sys.exit(2)

    # Convert from PMT dict to Python dict
    info = parse_file_metadata.parse_header(header)

    # Extra header info
    if(info["extra_len"] > 0):
        extra_str = file.read(info["extra_len"])

    try:
        extra = pmt.deserialize_str(extra_str)
    except RuntimeError:
        sys.stderr.write("[x] Could not deserialize extra headers: invalid or corrupt data file.\n")
        sys.exit(2)

    info = parse_file_metadata.parse_extra_dict(extra, info)

    return info


## Main parent function
def main():

    ## Open the binary file
    inputFile = open(BINNAME, "rb")

    ## Loop control variables
    isComplete = False
    headerNum = 0

    ## Main loop: 
    # 1. Read GNURadio output file
    # 2. Parse header info
    # 3. Encode payload
    # 4. Create JSON
    # 5. Send JSON with HTTP POST
    while(not isComplete): # Loop until all headers and subsequent data is read

        ## Read in bin file to parse header metadata
        # NOTE: for now we just read in one segment of data
        headerData = parseHeaders(inputFile)
        headerNum += 1
        print(f"Header Number: {headerNum}")

        # Size of each data segment
        ITEM_SIZE   = headerData["nitems"]
        SEG_SIZE    = headerData["nbytes"]

        # Check if we read the final header
        if ITEM_SIZE < NITEMS:
            isComplete = True

        # Pull out relevant header info
        rx_time     = headerData["rx_time"]
        rx_rate     = headerData["rx_rate"]
        num_samples = headerData["nitems"]
        radio       = 1

        ## Encode data payload from bin file into base64 ascii characters
        inputBinary = inputFile.read(SEG_SIZE)
        encodedData = (base64.b64encode(inputBinary)).decode('ascii')

        ## Create JSON file using encoded payload and header metadata
        jsonFormat = {"metadata":[{"rx_time" : rx_time, "rx_sample" : rx_rate, "num_samples" : num_samples, "radio_num" : radio}], "payload" : encodedData}
        jsonFile = json.dumps(jsonFormat, indent=4)

        ## Send this JSON file to the WebServer with an HTTP POST
        r = requests.post(url=HOST, data=jsonFile, headers=HEADERS)
        print("[+] Response from server: %s" %r)

        ## Close, wait, and repeat process
        rx_time = rx_time + 5   # temporary time header increment
        
        # Wait to send next file (TODO: does this program need to do anything else in the meanwhile?)
        print("[+] Sleeping for 5 seconds\n")
        time.sleep(5) # TODO: sleep interval related to GNURadio file creation

if __name__ == "__main__":
    main()
