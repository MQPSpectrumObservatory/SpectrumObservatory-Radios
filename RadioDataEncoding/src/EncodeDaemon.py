#!/usr/bin/python3

# Imports
import daemon           # Creating daemon process (non-standard lib)
import daemon.pidfile   # Creating daemon pid file 
import signal           # Kernel signal handling

from EncodeTransfer import (
    init,
    term,
    main
) # Transfer script

# Constants
WORKDIR = '/home/jrmurphy/dev/MQP/SpectrumObservatory-Radios/RadioDataEncoding/src'
LOG = WORKDIR + '/WSDaemon.log'
PID = WORKDIR + '/WSDaemon.pid'

if __name__ == "__main__":
    logFile = open(LOG, 'w+')   # Open log file

    # Set up deamon context (process working dir and std i/o)
    context = daemon.DaemonContext(
        working_directory=WORKDIR,
        stdout=logFile,
        stderr=logFile,
        pidfile=daemon.pidfile.PIDLockFile(PID)
    )

    # Set up signal interupt handlers
    context.signal_map = {
        signal.SIGTERM: term,
        signal.SIGHUP: None,
    }

    
    with context:
        # main program loop
        main()
