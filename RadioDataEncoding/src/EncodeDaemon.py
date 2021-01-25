#!/usr/bin/env python3

## Imports
import daemon           # Creating daemon process (non-standard lib)
import daemon.pidfile   # Creating daemon pid file
import signal           # Kernel signal handling
import threading        # Seperate thread for GNURadio and EncodeTransfer
import time             # Program Sleep

from top_block import (
    top_block
) # GNURadio top block class

from EncodeTransfer import (
    main as EncodeMain
) # Transfer function


## Constants
WORKDIR = '/home/jrmurphy/dev/MQP/SpectrumObservatory-Radios/RadioDataEncoding/src'
LOG = WORKDIR + '/RadioDaemon.log'
PID = WORKDIR + '/RadioDaemon.pid'


## GNURadio job class
class GNURadioJob(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

        self.shutdown_flag = threading.Event()

    def run(self):
        tb = top_block()
        tb.start()

        # Spin until shutdown is signaled
        while not self.shutdown_flag.is_set():
            time.sleep(0.5)

        tb.stop()
        tb.wait()


## Encode and Transfer script job class
class EncodeTransferJob(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

        self.shutdown_flag = threading.Event()

    def run(self):
        EncodeMain()

        # Spin until shutdown is signaled
        while not self.shutdown_flag.is_set():
            time.sleep(0.5)


## Declare our custom exception
class ServiceExit(Exception):
    pass


## Call our custom exception when a job's shutdown flag is set by a SIGTERM
def service_shutdown(signum, frame):
    raise ServiceExit


## Main thread
def main():
    logFile = open(LOG, 'w+') # Open log file

    # Set up deamon context (process working dir and std i/o)
    context = daemon.DaemonContext(
        working_directory=WORKDIR,
        stdout=logFile,
        stderr=logFile,
        pidfile=daemon.pidfile.PIDLockFile(PID)
    )

    # Set up signal interupt handlers
    context.signal_map = {
        signal.SIGTERM: service_shutdown
    }

    # Set up threads
    t1 = GNURadioJob()
    t2 = EncodeTransferJob()

    with context:
        # Start the job threads
        try:
            print("\nStart GNURadio\n")
            t1.start()

            time.sleep(5)   # NOTE: need to wait for GNURadio to finish setting up the radio
                            # Can GNURadio signal this? This time is variable depending of if FPGA needs to be flashed

            print("\nStart Upload Script\n")
            t2.start()
 
            # Keep the main thread running, otherwise signals are ignored.
            while True:
                time.sleep(0.5)
 
        except ServiceExit:
            # Terminate the running threads.
            # Signal the GNURadio thread to stop
            t1.shutdown_flag.set()
            t2.shutdown_flag.set()

            # Wait for the threads to close...
            t1.join()
            t2.join()
 
    print('Exiting main program')

if __name__ == "__main__":
    main()