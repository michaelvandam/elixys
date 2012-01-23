"""Sequences

Elixys Sequences
"""

import sys
sys.path.append("/opt/elixys/core/unitoperations")
import UnitOperations
import Cassette
import Summary
import CoreServer
from threading import Thread 
import time
from DBComm import *
import json

class Sequence(Thread):
  def __init__(self, sRemoteUser, nSourceSequenceID, pSequenceManager, pSystemModel):
    """Constructor"""
    # Call base class init
    Thread.__init__(self)

    # Initialize variables
    self.username = sRemoteUser
    self.sourceSequenceID = nSourceSequenceID
    self.sourceComponentID = 0
    self.runSequenceID = 0
    self.runComponentID = 0
    self.sequenceManager = pSequenceManager
    self.database = self.sequenceManager.database
    self.systemModel = pSystemModel
    self.running = False
    self.startComponentID = 0
    self.userSourceIDs = True

    # Fetch the sequence from the database
    self.sourceSequence = self.sequenceManager.GetSequence(sRemoteUser, nSourceSequenceID)

    # Make sure the sequence is valid
    if not self.sourceSequence["metadata"]["valid"]:
      raise Exception("Cannot run an invalid sequence")

    # Create a new sequence in the run history
    self.database.RunLog(LOG_INFO, self.username, self.runSequenceID, 0, "Starting run of sequence " + str(self.sourceSequenceID) + " (" + self.sourceSequence["metadata"]["name"] + ")")
    pConfiguration = self.database.GetConfiguration(self.username)
    self.runSequenceID = self.database.CreateSequence(self.username, self.sourceSequence["metadata"]["name"], self.sourceSequence["metadata"]["comment"], "History", 
      pConfiguration["reactors"], pConfiguration["reagentsperreactor"], pConfiguration["columnsperreactor"])

    # Copy the cassettes
    for pComponent in self.sourceSequence["components"]:
      if pComponent["componenttype"] == Cassette.componentType:
        pUnitOperation = UnitOperations.createFromComponent(self.sourceSequenceID, pComponent, self.username, self.database)
        pUnitOperation.copyComponent(self.runSequenceID)

  def setStartComponent(self, nComponentID):
    self.startComponentID = nComponentID

  def getIDs(self):
    # Return either the source or run sequence and component IDs
    if self.userSourceIDs:
      return (self.sourceSequenceID, self.sourceComponentID)
    else:
      return (self.runSequenceID, self.runComponentID)

  def run(self):
    """Thread entry point"""
    sRunError = ""
    self.userSourceIDs = True
    try:
      # Main sequence run loop
      self.database.RunLog(LOG_INFO, self.username, self.runSequenceID, self.runComponentID, "Run started")
      for pSourceComponent in self.sourceSequence["components"]:
        # Skip components until we find our start component
        self.sourceComponentID = pSourceComponent["id"]
        if not self.running and (self.startComponentID != 0) and (self.sourceComponentID != self.startComponentID):
          self.database.RunLog(LOG_INFO, self.username, self.runSequenceID, self.sourceComponentID, "Skipping unit operation (" + pSourceComponent["name"] + ")")
          continue
        self.running = True

        # Skip any previous summary component
        if pSourceComponent["componenttype"] == Summary.componentType:
          self.database.RunLog(LOG_INFO, self.username, self.runSequenceID, self.sourceComponentID, "Skipping unit operation (" + pSourceComponent["name"] + ")")
          continue

        # Create and run the next unit operation
        self.database.RunLog(LOG_INFO, self.username, self.runSequenceID, self.runComponentID, "Starting unit operation " + str(self.sourceComponentID) + " (" + 
          pSourceComponent["name"] + ")")
        pSourceUnitOperation = UnitOperations.createFromComponent(self.sourceSequenceID, pSourceComponent, self.username, self.sequenceManager.database, self.systemModel)
        self.runComponentID = pSourceUnitOperation.copyComponent(self.runSequenceID)
        pRunComponent = self.sequenceManager.GetComponent(self.username, self.runComponentID, self.runSequenceID)
        pRunUnitOperation = UnitOperations.createFromComponent(self.runSequenceID, pRunComponent, self.username, self.sequenceManager.database, self.systemModel)
        pRunUnitOperation.setDaemon(True)
        pRunUnitOperation.start()
        self.systemModel.SetUnitOperation(pRunUnitOperation)

        # Wait until the operation completes
        while pRunUnitOperation.is_alive():
          time.sleep(0.25)

        # Check for unit operation error
        sError = pRunUnitOperation.getError()
        if sError != "":
          self.database.RunLog(LOG_INFO, self.username, self.runSequenceID, self.runComponentID, "Unit operation failed: " + sError)
          raise Exception(sError)

        # Update the unit operation details in the database
        UnitOperations.updateToComponent(pRunUnitOperation, self.runSequenceID, pRunComponent, self.username, self.sequenceManager.database, self.systemModel)
        self.sequenceManager.UpdateComponent(self.username, self.runSequenceID, self.runComponentID, None, pRunComponent)
        self.database.RunLog(LOG_INFO, self.username, self.runSequenceID, self.runComponentID, "Completed unit operation (" + pRunComponent["name"] + ")")
        self.sourceComponentID = 0
        self.runComponentID = 0
    except Exception as ex:
      self.database.SystemLog(LOG_ERROR, self.username, "Sequence run failed: " + str(ex))
      sRunError = str(ex)

    # Add the Summary unit operation to the sequence
    pSummaryComponent = Summary.createNewComponent(sRunError)
    self.runComponentID = self.database.CreateComponent(self.username, self.runSequenceID, pSummaryComponent["type"], pSummaryComponent["name"], json.dumps(pSummaryComponent))

    # Switch to using the run IDs rather than the source because the summary unit operation only exists in the run sequence
    self.userSourceIDs = False

    # Instantiate and start the summary unit operation
    self.database.RunLog(LOG_INFO, self.username, self.runSequenceID, self.runComponentID, "Starting summary unit operation")
    pSummaryComponent = self.sequenceManager.GetComponent(self.username, self.runComponentID, self.runSequenceID)
    pSummaryUnitOperation = UnitOperations.createFromComponent(self.runSequenceID, pSummaryComponent, self.username, self.sequenceManager.database, self.systemModel)
    pSummaryUnitOperation.setDaemon(True)
    pSummaryUnitOperation.start()
    self.systemModel.SetUnitOperation(pSummaryUnitOperation)

    # Wait until the operation completes
    while pSummaryUnitOperation.is_alive():
      time.sleep(0.25)
    self.database.RunLog(LOG_INFO, self.username, self.runSequenceID, self.runComponentID, "Summary unit operation complete")
    self.runComponentID = 0

    # Run complete
    self.database.RunLog(LOG_INFO, self.username, self.runSequenceID, 0, "Run stopped")
    self.running = False

