# Cassette unit operation

# Imports
from UnitOperation import *

# Component type
componentType = "CASSETTE"

# Create a unit operation from a component object
def createFromComponent(nSequenceID, pComponent, username, database, systemModel):
  pCassette = Cassette(systemModel, {}, username, nSequenceID, pComponent["id"], database)
  pCassette.initializeComponent(pComponent)
  return pCassette

# Updates a component object based on a unit operation
def updateToComponent(pUnitOperation, nSequenceID, pComponent, username, database, systemModel):
  pass

# Cassette class
class Cassette(UnitOperation):
  def __init__(self,systemModel,params,username = "",sequenceID = 0, componentID = 0, database = None):
    UnitOperation.__init__(self,systemModel,username,sequenceID,componentID,database)

  def run(self):
    #This unit operation doesn't do anything when run
    pass
  
  def initializeComponent(self, pComponent):
    """Initializes the component validation fields"""
    self.component = pComponent
    self.addComponentDetails()

  def validateFull(self, pAvailableReagents):
    """Performs a full validation on the component"""
    self.component["note"] = ""
    return self.validateQuick()

  def validateQuick(self):
    """Performs a quick validation on the component"""
    # Cassettes are always valid
    self.component.update({"validationerror":False})
    return True

  def saveValidation(self):
    """Saves validation-specific fields back to the database"""
    # Pull the original component from the database
    pDBComponent = self.database.GetComponent(self.username, self.component["id"])

    # Copy the validation fields
    pDBComponent["validationerror"] = self.component["validationerror"]

    # Save the component
    self.database.UpdateComponent(self.username, self.component["id"], pDBComponent["componenttype"], self.component["note"], json.dumps(pDBComponent))

  def addComponentDetails(self):
    """Adds details to the component after retrieving it from the database and prior to sending it to the client"""
    # Skip if we've already updated the reagents
    if self.component.has_key("reagents") or not self.component.has_key("reagentids"):
      return

    # Look up each reagent in this cassette
    pReagentIDs = self.component["reagentids"]
    pReagents = []
    for nReagentID in pReagentIDs:
      pReagents.append(self.database.GetReagent(self.username, nReagentID))

    del self.component["reagentids"]
    self.component["reagents"] = pReagents

  def copyComponent(self, nSourceSequenceID, nTargetSequenceID):
    """Creates a copy of the component in the database"""
    # Cassettes can only be copied by the database which needs to be done before this function is called.  Locate the cassette in the
    # new sequence which corresponds to this one
    pNewCassette = self.database.GetCassette(self.username, nTargetSequenceID, self.component["reactor"] - 1)

    # Update the cassette details
    self.updateComponentDetails(pNewCassette)
    self.database.UpdateComponent(self.username, pNewCassette["id"], pNewCassette["componenttype"], pNewCassette["note"], json.dumps(pNewCassette))

    # Copy the reagent details
    pConfiguration = self.database.GetConfiguration(self.username)
    for nReagent in range(1, pConfiguration["reagentsperreactor"] + 1):
      pReagent = self.database.GetReagentByPosition(self.username, self.component["sequenceid"], self.component["reactor"], str(nReagent))
      self.database.UpdateReagentByPosition(self.username, nTargetSequenceID, self.component["reactor"], str(nReagent), pReagent["name"], pReagent["description"])

    # Return the cassette ID
    return pNewCassette["id"]

