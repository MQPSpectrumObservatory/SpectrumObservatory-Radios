#!/usr/bin/env python3

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
BINNAME     = "sample.dat"                                                  # name of the input file
HEADERS     = {'Content-type': 'application/json', 'Accept': 'text/plain'}  # Headers for POST request
NITEMS      = 300000                                                        # Number of samples per header (match to GNURadio)

# Test Constants -> (can be used to test locally)
TEST = 0
if(TEST):
    HOST = 'http://localhost:3000/data'
    BINNAME = 'sample.dat'


## This will be called to parse header data out of the dat file
# Takes in an open file descriptor and returns a python dictionary
# NOTE: This function is built on the gr_read_file_metadata program from GNURadio
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

    ## Initialize loop control variables
    isComplete = False
    headerNum = 0

    ## Main loop: 
    # 1. Read GNURadio output file
    # 2. Parse header info
    # 3. Check if final segment
    # 4. Encode payload
    # 5. Create JSON
    # 6. Send JSON with HTTP POST
    while(not isComplete): # Loop until all headers and subsequent data is read

        # Read in bin file to parse header metadata
        headerData = parseHeaders(inputFile)
        headerNum += 1
        print(f"Header Number: {headerNum}")

        # Size of each data segment
        ITEM_SIZE   = headerData["nitems"]
        SEG_SIZE    = headerData["nbytes"]

        # Check if we read the final header in the file (if there are less samples than expected for a full segment)
        if ITEM_SIZE < NITEMS:
            isComplete = True

        # Pull out relevant header info
        rx_time     = headerData["rx_time"]
        rx_rate     = headerData["rx_rate"]
        num_samples = headerData["nitems"]
        radio       = 1 # TODO: set up custom header to indentify which radio data is from?

        # Encode data payload from bin file into base64 ascii characters
        inputBinary = inputFile.read(SEG_SIZE)
        encodedData = (base64.b64encode(inputBinary)).decode('ascii')

        # Create JSON file using encoded payload and header metadata
        jsonFormat = {"metadata":{"rx_time" : rx_time, "rx_sample" : rx_rate, "num_samples" : num_samples, "radio_num" : radio}, "payload" : encodedData}
        jsonFile = json.dumps(jsonFormat, indent=4)

        # Send this JSON file to the WebServer with an HTTP POST
        r = requests.post(url=HOST, data=jsonFile, headers=HEADERS)
        print("[+] Response from server: %s" %r)
        
        # Wait to send next segment (segments are generated at a rate of 1 per second)
        print("[+] Sleeping for 1 seconds\n")
        time.sleep(1)


    ## Any remaining cleanup
    print("[o] Sent all data, cleaning up\n")
    inputFile.close()
    os.remove("sample.dat")

if __name__ == "__main__":
    main()
