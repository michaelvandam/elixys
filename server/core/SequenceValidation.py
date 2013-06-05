"""SequenceValidation

Validates synthesis sequences
"""

### Imports
import json
import sys
sys.path.append("/opt/elixys/core/unitoperations")
sys.path.append("/opt/elixys/database")
import UnitOperations
import threading
from DBComm import *
import SequenceManager
import time
from daemon import daemon
import signal
import logging

log = logging.getLogger("elixys.validation")

# Sequence validation daemon exit function
gSequenceValidationDaemon = None
def OnExit(pSequenceValidationDaemon, signal, func=None):
    global gSequenceValidationDaemon
    if gSequenceValidationDaemon != None:
        gSequenceValidationDaemon.bTerminate = True

# Sequence validation daemon
class SequenceValidationDaemon(daemon):
    def __init__(self, sPidFile):
        """Initializes the sequence validation daemon"""
        global gSequenceValidationDaemon
        daemon.__init__(self, sPidFile, "/opt/elixys/logs/SequenceValidation.log")
        self.bTerminate = False
        gSequenceValidationDaemon = self

    def run(self):
        """Runs the sequence validation daemon"""
        global gSequenceValidationDaemon
        pDatabase = None
        pSequenceManager = None
        while not self.bTerminate:
            try:
                # Connect to the database
                pDatabase = DBComm()
                pDatabase.Connect()
                log.info("Validation process starting")


                # Create the sequence manager
                pSequenceManager = SequenceManager.SequenceManager(pDatabase)

                # Install the kill signal handler
                signal.signal(signal.SIGTERM, OnExit)
                log.info("Validation process started")

                # Run until we get the signal to stop
                while not self.bTerminate:
                    # Iterate through all the saved sequences in the database and see if any are marked as dirty
                    bAllSequencesClean = True
                    pSequences = pDatabase.GetAllSequences("System", "Saved")
                    for pSequence in pSequences:
                       if pSequence["dirty"]:
                           # Perform a full validation on the sequence
                           log.info("Performing full validation on sequence " + str(pSequence["id"]))
                           pSequenceManager.ValidateSequenceFull("System", pSequence["id"])
                           bAllSequencesClean = False

                    # Nap for a bit if we didn't find any work to do
                    if bAllSequencesClean:
                        time.sleep(0.5)
                log.info("Validation process received quit signal")
            except Exception as ex:
                # Log the error
                log.info("Validation process failed: " + str(ex))
            finally:
                if pSequenceManager != None:
                    pSequenceManager = SequenceManager.SequenceManager(pDatabase)
                    pSequenceManager = None
                if pDatabase != None:
                    log.info("Validation process exiting")
                    pDatabase.Disconnect()
                    pDatabase = None

            # Sleep for a second before we respawn
            if not self.bTerminate:
                time.sleep(1)
        gSequenceValidationDaemon = None

# Main function
if __name__ == "__main__":
    if len(sys.argv) == 3:
        pDaemon = SequenceValidationDaemon(sys.argv[2])
        if 'start' == sys.argv[1]:
            pDaemon.start()
        elif 'stop' == sys.argv[1]:
            pDaemon.stop()
        elif 'restart' == sys.argv[1]:
            pDaemon.restart()
        else:
            print "Unknown command"
            sys.exit(2)
        sys.exit(0)
    else:
        print "usage: %s start|stop|restart pidfile" % sys.argv[0]
        sys.exit(2)

