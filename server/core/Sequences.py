"""Sequences

Elixys Sequences
"""

import sys
sys.path.append("/opt/elixys/core")
sys.path.append("/opt/elixys/core/unitoperations")
import UnitOperations
import Cassette
import Summary
from threading import Thread 
import time
from DBComm import *
import json
from SequenceManager import SequenceManager
from Messaging import Messaging

import logging
log = logging.getLogger("elixys.core")

class Sequence(Thread):
  def __init__(self, sRemoteUser, nSourceSequenceID, pSystemModel):
    """Constructor"""

    # Call base class init
    Thread.__init__(self)

    # Initialize variables
    self.username = sRemoteUser
    self.sourceSequenceID = nSourceSequenceID
    self.sourceComponentID = 0
    self.runSequenceID = 0
    self.runComponentID = 0
    self.systemModel = pSystemModel
    self.initializing = True
    self.running = False
    self.startComponentID = 0
    self.userSourceIDs = True
    self.runWillPause = False
    self.runIsPaused = False
    self.runAborted = False
    self.showAbortPrompt = False

    # Create database connection and sequence manager
    self.database = DBComm()
    self.database.Connect()
    self.sequenceManager = SequenceManager(self.database)

    # Create messaging object
    self.messaging = Messaging(self.username, self.database)

    # Fetch the sequence from the database and make sure it is valid
    self.sourceSequence = self.sequenceManager.GetSequence(self.username, self.sourceSequenceID)
    if not self.sourceSequence["metadata"]["valid"]:
      raise Exceptions("Cannot run an invalid sequence (" + self.sourceSequenceID + ")")

    # Create a new sequence in the run history
    self.database.RunLog(LOG_INFO, self.username, self.runSequenceID, 0, "Starting run of sequence " + str(self.sourceSequenceID) + " (" + self.sourceSequence["metadata"]["name"] + ")")
    pConfiguration = self.database.GetConfiguration(self.username)
    self.runSequenceID = self.database.CreateSequence(self.username, self.sourceSequence["metadata"]["name"], self.sourceSequence["metadata"]["comment"], "History", 
      pConfiguration["reactors"], pConfiguration["reagentsperreactor"])

    # Copy the cassettes
    for pComponent in self.sourceSequence["components"]:
      if pComponent["componenttype"] == Cassette.componentType:
        pUnitOperation = UnitOperations.createFromComponent(self.sourceSequenceID, pComponent, self.username, self.database)
        pUnitOperation.copyComponent(self.sourceSequenceID, self.runSequenceID)

  def setStartComponent(self, nComponentID):
    """Sets the first component of the run"""
    self.startComponentID = nComponentID

  def getIDs(self):
    """Return the appropriate sequence and component IDs"""
    if self.userSourceIDs:
      return (self.sourceSequenceID, self.sourceComponentID)
    else:
      return (self.runSequenceID, self.runComponentID)

  def pauseRun(self):
    """Flags the running sequence to pause at the start of the next unit operation"""
    if not self.running:
      raise Exception("Sequence not running, cannot pause")
    if self.runWillPause:
      raise Exception("Sequence already will pause, cannot pause")
    if self.runIsPaused:
      raise Exception("Sequence is already paused, cannot pause")
    self.runWillPause = True

  def continueRun(self):
    """Continues a paused sequence"""
    if not self.running:
      raise Exception("Sequence not running, cannot continue")
    if not self.runWillPause and not self.runIsPaused:
      raise Exception("Sequence run not paused, cannot continue")
    self.runWillPause = False
    self.runIsPaused = False

  def willRunPause(self):
    """Returns true if the sequence run is flagged to pause, false otherwise"""
    return self.runWillPause

  def isRunPaused(self):
    """Returns true if the sequence run is paused, false otherwise"""
    return self.runIsPaused

  def abortRun(self):
    """Aborts the current sequence run"""
    self.runAborted = True
    self.showAbortPrompt = False

  def isRunComplete(self):
    """Returns true if the sequence run has completed and is waiting at the summary unit operation, false otherwise"""
    return not self.userSourceIDs

  def setShowAbortPrompt(self, bShowAbortPrompt):
    """Sets the flag that indicates if the abort sequence run prompt should be set in the run state"""
    self.showAbortPrompt = bShowAbortPrompt

  def getShowAbortPrompt(self):
    """Returns the flag that indicates if the abort sequence run prompt should be set in the run state"""
    return self.showAbortPrompt

  def run(self):
    """Thread entry point"""
    sRunError = ""
    self.userSourceIDs = True
    try:
      # Main sequence run loop
      sMessage = "Run of sequence \"" + self.sourceSequence["metadata"]["name"] + "\" started."
      self.database.RunLog(LOG_INFO, self.username, self.runSequenceID, self.runComponentID, sMessage)
      self.messaging.broadcastMessage(sMessage)

      nComponentCount = len(self.sourceSequence["components"])
      nCurrentComponent = 0
      while nCurrentComponent < nComponentCount:
        # Get the next component
        pSourceComponent = self.sourceSequence["components"][nCurrentComponent]

        # Skip components until we find our start component
        self.sourceComponentID = pSourceComponent["id"]
        if self.initializing and (self.startComponentID != 0) and (self.sourceComponentID != self.startComponentID):
          self.database.RunLog(LOG_INFO, self.username, self.runSequenceID, self.sourceComponentID, "Skipping unit operation (" + pSourceComponent["componenttype"] + ")")
          nCurrentComponent += 1
          continue

        # Update our initializing and running flags
        self.initializing = False
        self.running = True

        # Ignore any previous summary component
        if pSourceComponent["componenttype"] == Summary.componentType:
          self.database.RunLog(LOG_INFO, self.username, self.runSequenceID, self.sourceComponentID, "Skipping unit operation (" + pSourceComponent["componenttype"] + ")")
          nCurrentComponent += 1
          continue

        # Create and run the next unit operation
        self.database.RunLog(LOG_INFO, self.username, self.runSequenceID, self.runComponentID, "Starting unit operation " + str(self.sourceComponentID) + " (" + 
          pSourceComponent["componenttype"] + ")")
        pSourceUnitOperation = UnitOperations.createFromComponent(self.sourceSequenceID, pSourceComponent, self.username, self.sequenceManager.database, self.systemModel)
        self.runComponentID = pSourceUnitOperation.copyComponent(self.sourceSequenceID, self.runSequenceID)
        pRunComponent = self.sequenceManager.GetComponent(self.username, self.runComponentID, self.runSequenceID)
        pRunUnitOperation = UnitOperations.createFromComponent(self.runSequenceID, pRunComponent, self.username, self.sequenceManager.database, self.systemModel)
        pRunUnitOperation.setDaemon(True)
        pRunUnitOperation.start()
        self.systemModel.SetUnitOperation(pRunUnitOperation)

        # Wait until the operation completes or we receive an abort signal
        while pRunUnitOperation.is_alive() and not self.runAborted:
          time.sleep(0.25)
        self.systemModel.SetUnitOperation(None)
        if self.runAborted:
          pRunUnitOperation.setAbort()
          raise Exception("Run aborted")

        # Check for unit operation error
        sError = pRunUnitOperation.getError()
        if sError != "":
          self.database.RunLog(LOG_INFO, self.username, self.runSequenceID, self.runComponentID, "Unit operation failed: " + sError)
          raise Exception(sError)

        # Update the unit operation details in the database
        UnitOperations.updateToComponent(pRunUnitOperation, self.runSequenceID, pRunComponent, self.username, self.sequenceManager.database, self.systemModel)
        self.sequenceManager.UpdateComponent(self.username, self.runSequenceID, self.runComponentID, None, pRunComponent)
        self.database.RunLog(LOG_INFO, self.username, self.runSequenceID, self.runComponentID, "Completed unit operation (" + pRunComponent["componenttype"] + ")")
        self.sourceComponentID = 0
        self.runComponentID = 0

        # Check if the user paused the sequence for editing
        if self.runWillPause:
          # Pause until editing is complete
          self.database.RunLog(LOG_INFO, self.username, self.runSequenceID, self.runComponentID, "Pausing run for editing")
          self.runWillPause = False
          self.runIsPaused = True
          while self.runIsPaused and not self.runAborted:
            time.sleep(0.25)
          if self.runAborted:
            raise Exception("Sequence aborted")
          self.database.RunLog(LOG_INFO, self.username, self.runSequenceID, self.runComponentID, "Continuing paused run")

          # Reload the sequence and make sure it is still valid
          self.sourceSequence = self.sequenceManager.GetSequence(self.username, self.sourceSequenceID)
          if not self.sourceSequence["metadata"]["valid"]:
            raise Exceptions("Edited sequence is no longer valid (" + self.sourceSequenceID + ")")

          # Scan until we find the unit operation we just executed
          nComponentCount = len(self.sourceSequence["components"])
          nCurrentComponent = 0
          while nCurrentComponent < nComponentCount:
            if self.sourceSequence["components"][nCurrentComponent]["id"] == pSourceComponent["id"]:
              break
            nCurrentComponent += 1
          if nCurrentComponent == nComponentCount:
            raise Exception("Failed to find previous component in edited sequence")

        # Advance to the next component
        nCurrentComponent += 1
    except Exception as ex:
      log.error("Sequence run failed: " + str(ex))
      sRunError = str(ex)

    # Add the Summary unit operation to the sequence
    pSummaryComponent = Summary.createNewComponent(sRunError)
    self.runComponentID = self.database.CreateComponent(self.username, self.runSequenceID, pSummaryComponent["type"], pSummaryComponent["note"], json.dumps(pSummaryComponent))

    # Fully validate the run sequence
    self.sequenceManager.ValidateSequenceFull(self.username, self.runSequenceID)

    # Switch to using the run IDs rather than the source because the summary unit operation only exists in the run sequence
    self.userSourceIDs = False

    # Instantiate and start the summary unit operation
    self.database.RunLog(LOG_INFO, self.username, self.runSequenceID, self.runComponentID, "Starting summary unit operation")
    pSummaryComponent = self.sequenceManager.GetComponent(self.username, self.runComponentID, self.runSequenceID)
    pSummaryUnitOperation = UnitOperations.createFromComponent(self.runSequenceID, pSummaryComponent, self.username, self.sequenceManager.database, self.systemModel)
    pSummaryUnitOperation.setDaemon(True)
    pSummaryUnitOperation.start()
    self.systemModel.SetUnitOperation(pSummaryUnitOperation)

    # Broadcast the summary unit operation message
    self.messaging.broadcastMessage(pSummaryComponent["message"])

    # Wait until the operation completes
    while pSummaryUnitOperation.is_alive():
      time.sleep(0.25)
    self.database.RunLog(LOG_INFO, self.username, self.runSequenceID, self.runComponentID, "Summary unit operation complete")
    self.runComponentID = 0

    # Run complete
    self.database.RunLog(LOG_INFO, self.username, self.runSequenceID, 0, "Run stopped")
    self.running = False

