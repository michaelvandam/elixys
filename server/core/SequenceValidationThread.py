""" SequenceValidationThread.py

Validates the given sequence on this thread's time"""

### Imports
import threading
import sys
sys.path.append("/opt/elixys/database")
from DBComm import *
import SequenceManager
import time

class SequenceValidationThread(threading.Thread):
    # Set parameters
    def SetParameters(self, pTerminateEvent):
        self.__pTerminateEvent = pTerminateEvent

    # Thread function
    def run(self):
        """Thread entry point"""
        # Connect to the database
        pDatabase = DBComm()
        pDatabase.Connect()
        pDatabase.SystemLog(LOG_INFO, "ValidationThread", "Validation thread starting")

        # Create the sequence manager
        pSequenceManager = SequenceManager.SequenceManager(pDatabase)

        # Loop until the terminate event is set
        while not self.__pTerminateEvent.is_set():
            # Iterate through all the sequences in the database and see if any are marked as dirty
            bAllSequencesClean = True
            pSequences = pDatabase.GetAllSequences("ValidationThread", "Saved")
            for pSequence in pSequences:
               if pSequence["dirty"]:
                   # Perform a full validation on the sequence
                   pDatabase.SystemLog(LOG_INFO, "ValidationThread", "Performing full validation on sequence " + str(pSequence["id"]))
                   pSequenceManager.validation.ValidateSequenceFull("ValidationThread", pSequence["id"])
                   bAllSequencesClean = False

            # Nap for a bit if we didn't find any work to do
            if bAllSequencesClean:
                time.sleep(1)

        # Shut down and exit
        pDatabase.SystemLog(LOG_INFO, "ValidationThread", "Validation thread exiting")
        pDatabase.Disconnect()

