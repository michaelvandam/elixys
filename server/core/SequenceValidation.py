"""SequenceValidation

Validates synthesis sequences
"""

import json
import UnitOperations

class SequenceValidation:

  def __init__(self, pDatabase, pSequenceManager):
    """Constructor"""
    self.database = pDatabase
    self.sequenceManager = pSequenceManager

  ### Validation functions ###

  def ValidateSequenceFull(self, sRemoteUser, nSequenceID):
    """Performs a full validation of the sequence"""
    # Load the sequence and all of the reagents
    pSequence = self.sequenceManager.GetSequence(sRemoteUser, nSequenceID)
    pAllReagents = self.database.GetReagentsBySequence(sRemoteUser, nSequenceID)

    # Filter reagents to keep only those that are available
    pAvailableReagents = []
    for pReagent in pAllReagents:
      if pReagent["available"]:
        pAvailableReagents.append(pReagent)

    # Do a full validation of each component
    bValid = True
    for pComponent in pSequence["components"]:
      pUnitOperation = UnitOperations.createFromComponent(pComponent, sRemoteUser, self.database)
      if not pUnitOperation.validateFull(pAvailableReagents):
        bValid = False
      pUnitOperation.saveValidation()

    # Update the valid flag in the database and return
    self.database.UpdateSequence(sRemoteUser, nSequenceID, pSequence["metadata"]["name"], pSequence["metadata"]["comment"], bValid)
    self.database.UpdateSequenceDirtyFlag(sRemoteUser, nSequenceID, False)
    return bValid

  def InitializeComponent(self, sRemoteUser, nSequenceID, nComponentID):
    """Initializes the validation fields of a newly added component"""
    # Initialize the validation fields of the raw component
    pComponent = self.database.GetComponent(sRemoteUser, nComponentID)
    pUnitOperation = UnitOperations.createFromComponent(pComponent, sRemoteUser, self.database)
    self.database.UpdateComponent(sRemoteUser, nComponentID, pComponent["componenttype"], pUnitOperation.component["name"], json.dumps(pUnitOperation.component))

    # Flag the sequence validation as dirty
    self.database.UpdateSequenceDirtyFlag(sRemoteUser, nSequenceID, True)

  def ValidateComponent(self, sRemoteUser, nSequenceID, nComponentID):
    """Performs a quick validation of the given component"""
    # Load the component and do a quick validation
    pComponent = self.sequenceManager.GetComponent(sRemoteUser, nComponentID, nSequenceID)
    pUnitOperation = UnitOperations.createFromComponent(pComponent, sRemoteUser, self.database)
    pUnitOperation.validateQuick()

    # Load the raw component and update just the validation field
    pDBComponent = self.database.GetComponent(sRemoteUser, nComponentID)
    pDBComponent["validationerror"] = pUnitOperation.component["validationerror"]
    self.database.UpdateComponent(sRemoteUser, nComponentID, pDBComponent["componenttype"], pDBComponent["name"], json.dumps(pDBComponent))

    # Flag the sequence validation as dirty
    self.database.UpdateSequenceDirtyFlag(sRemoteUser, nSequenceID, True)

