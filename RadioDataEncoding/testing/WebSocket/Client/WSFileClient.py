import socket
import os

SEPARATOR = "<SEPARATOR>"
BUFFER_SIZE = 4096 # send 4096 bytes each time step

# the ip address and port of the server (receiver)
host = "localhost" # in production this will be spectrumobservatory.wpi.edu
port = 8080          # ws port is typically port 80

# the name and file being sent over the socket
filename = input("Enter the name of the file to transfer:")

# create the client socket
s = socket.socket()

# connect to the server
print(f"[+] Connecting to {host}:{port}")
s.connect((host, port))
print("[+] Connected")

# send the filename and filesize
s.send(f"{filename}".encode())

# start sending the file
with open(filename, "rb") as f:
    while(True):
        # read the bytes from the file
        bytes_read = f.read(BUFFER_SIZE)

        #file transmitting is done
        if not bytes_read:
            break

        #we use sendall to assure the transmission in busy networks
        s.sendall(bytes_read)

# close the socket
s.close()
