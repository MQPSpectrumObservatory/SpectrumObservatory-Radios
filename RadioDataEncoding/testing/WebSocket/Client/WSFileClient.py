import socket
import tqdm # used for progress bars
import os

SEPARATOR = "<SEPARATOR>"
BUFFER_SIZE = 4096 # send 4096 bytes each time step

# the ip address and port of the server (receiver)
host = "192.168.1.9"
port = 8080

# the name and file being sent over the socket
filename = input("Enter the name of the file to transfer:")
filesize = os.path.getsize(filename)

# create the client socket
s = socket.socket()

# connect to the server
print(f"[+] Connecting to {host}:{port}")
s.connect((host, port))
print("[+] Connected")

# send the filename and filesize
s.send(f"{filename}{SEPARATOR}{filesize}".encode())

# start sending the file
progress = tqdm.tqdm(range(filesize), f"Sending {filename}", unit="B", unit_scale=True, unit_divisor=1024)

with open(filename, "rb") as f:
    for _ in progress:
        # read the bytes from the file
        bytes_read = f.read(BUFFER_SIZE)

        if not bytes_read:
            #file transmitting is done
            break

        #we use sendall to assure the transmission in busy networks
        s.sendall(bytes_read)

        # update progress bar
        progress.update(len(bytes_read))

# close the socket
s.close()
