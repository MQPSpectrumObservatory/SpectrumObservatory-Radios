import daemon
import daemon.pidfile
import os
import signal
import EncodeTransfer

WORKDIR = '/home/jrmurphy/dev/MQP/SpectrumObservatory-Radios/RadioDataEncoding/src'
LOG = WORKDIR + '/WSDaemon.log'
PID = WORKDIR + '/WSDaemon.pid'

if __name__ == "__main__":
    logFile = open(LOG, 'w+')

    context = daemon.DaemonContext(
        working_directory=WORKDIR,
        stdout=logFile,
        stderr=logFile,
        pidfile=daemon.pidfile.PIDLockFile(PID)
    )

    context.signal_map = {
        signal.SIGTERM: EncodeTransfer.term,
        signal.SIGHUP: None,
    }

    
    with context:
        # main program loop
        EncodeTransfer.init()
        EncodeTransfer.main()
