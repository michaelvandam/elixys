"""Sequences

Elixys Sequences
"""

import sys
sys.path.append("/opt/elixys/core/unitoperations")
import UnitOperations
import CoreServer
from threading import Thread 
import time
from DBComm import *

class Sequence(Thread):
  def __init__(self, sRemoteUser, nSequenceID, pSequenceManager, pSystemModel):
    """Constructor"""
    # Call base class init
    Thread.__init__(self)

    # Initialize variables
    self.username = sRemoteUser
    self.sequenceID = nSequenceID
    self.sequenceManager = pSequenceManager
    self.systemModel = pSystemModel
    self.componentID = 0
    self.running = False
    self.startComponentID = 0

    # Fetch the sequence from the database
    self.sequence = self.sequenceManager.GetSequence(sRemoteUser, nSequenceID)

    # Make sure the sequence is valid
    if not self.sequence["metadata"]["valid"]:
      raise Exception("Cannot run an invalid sequence")

  def setStartComponent(self, nComponentID):
    self.startComponentID = nComponentID

  def run(self):
    """Thread entry point"""
    try:
      # Create a new sequence in the run history

      # Main sequence run loop
      for pComponent in self.sequence["components"]:
        # Skip components until we find our start component
        if not self.running and (self.startComponentID != 0) and (pComponent["id"] != self.startComponentID):
          continue
        self.running = True

        # Create and run the next unit operation
        self.componentID = pComponent["id"]
        pUnitOperation = UnitOperations.createFromComponent(self.sequenceID, pComponent, self.username, self.sequenceManager.database, self.systemModel)
        pUnitOperation.setDaemon(True)
        pUnitOperation.start()
        self.systemModel.SetUnitOperation(pUnitOperation)

        # Wait until the operation completes
        while pUnitOperation.is_alive():
          time.sleep(0.25)

        # Check for unit operation error
        sError = pUnitOperation.getError()
        if sError != "":
          raise Exception(sError)
    except Exception as ex:
        self.sequenceManager.database.SystemLog(LOG_ERROR, self.username, "Sequence run failed: " + str(ex))

    # Run complete
    self.running = False

