import daemon
import os
import EncodeTransfer

if __name__ == "__main__":
    workingDir = '/home/jrmurphy/dev/MQP/Testing/Daemon'
    logFile = open(workingDir+'/logA.log', 'w+')

    context = daemon.DaemonContext(
        working_directory=workingDir,
        stdout=logFile
    )

    with context:
        # do main program
        exit()