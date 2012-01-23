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
    return self.validateQuick()

  def validateQuick(self):
    """Performs a quick validation on the component"""
    #Validate all reagents
    bValidationError = False
    for pReagent in self.component["reagents"]:
      if pReagent["available"]:
        if not self.validateComponentField(pReagent["name"], pReagent["namevalidation"]) or \
           not self.validateComponentField(pReagent["description"], pReagent["descriptionvalidation"]):
          bValidationError = True

    # Set the validation error field
    self.component.update({"validationerror":bValidationError})
    return not bValidationError

  def saveValidation(self):
    """Saves validation-specific fields back to the database"""
    # Pull the original component from the database
    pDBComponent = self.database.GetComponent(self.username, self.component["id"])

    # Copy the validation fields
    pDBComponent["name"] = self.component["name"]
    pDBComponent["validationerror"] = self.component["validationerror"]

    # Save the component
    self.database.UpdateComponent(self.username, self.component["id"], pDBComponent["componenttype"], pDBComponent["name"], json.dumps(pDBComponent))

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

  def updateComponentDetails(self, pTargetComponent):
    """Strips a component down to only the details we want to save in the database"""
    # Call the base handler
    UnitOperation.updateComponentDetails(self, pTargetComponent)

    # Update the field we want to save
    pTargetComponent["available"] = self.component["available"]

  def copyComponent(self, nSequenceID):
    """Creates a copy of the component in the database"""
    # Cassettes can only be copied by the database which needs to be done before this function is called.  Locate the cassette in the
    # new sequence which corresponds to this one
    pNewCassette = self.database.GetCassette(self.username, nSequenceID, self.component["reactor"] - 1)

    # Update the cassette details
    self.updateComponentDetails(pNewCassette)
    self.database.UpdateComponent(self.username, pNewCassette["id"], pNewCassette["componenttype"], pNewCassette["name"], json.dumps(pNewCassette))

    # Copy the reagent details
    pConfiguration = self.database.GetConfiguration(self.username)
    for nReagent in range(1, pConfiguration["reagentsperreactor"] + 1):
      pReagent = self.database.GetReagentByPosition(self.username, self.component["sequenceid"], self.component["reactor"], str(nReagent))
      self.database.UpdateReagentByPosition(self.username, nSequenceID, self.component["reactor"], str(nReagent), pReagent["available"], pReagent["name"], pReagent["description"])

    # Copy the column details
    for nColumn in range(0, pConfiguration["columnsperreactor"]):
      sPosition = chr(ord("A") + nColumn)
      pColumn = self.database.GetReagentByPosition(self.username, self.component["sequenceid"], self.component["reactor"], sPosition)
      self.database.UpdateReagentByPosition(self.username, nSequenceID, self.component["reactor"], sPosition, pColumn["available"], pColumn["name"], pColumn["description"])

    # Return the cassette ID
    return pNewCassette["id"]

