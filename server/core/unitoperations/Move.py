# Move unit operation

# Imports
from UnitOperation import *

# Component type
componentType = "MOVE"

# Create a unit operation from a component object
def createFromComponent(nSequenceID, pComponent, username, database, systemModel):
  pParams = {}
  pParams["ReactorID"] = "Reactor" + str(pComponent["reactor"])
  pParams["reactPosition"] = str(pComponent["position"])
  pMove = Move(systemModel, pParams, username, nSequenceID, pComponent["id"], database)
  pMove.initializeComponent(pComponent)
  return pMove

# Updates a component object based on a unit operation
def updateToComponent(pUnitOperation, nSequenceID, pComponent, username, database, systemModel):
  pass

# Move class
class Move(UnitOperation):
  def __init__(self,systemModel,params,username = "",sequenceID = 0, componentID = 0, database = None):
    UnitOperation.__init__(self,systemModel,username,sequenceID,componentID,database)
    expectedParams = {REACTORID:STR,REACTPOSITION:STR}
    paramError = self.validateParams(params,expectedParams)
    if self.paramsValid:
      self.setParams(params)
    else:
      raise UnitOpError(paramError)
    self.description = "Moving reactor " + str(self.ReactorID[-1]) + " to the " + str(self.reactPosition) + " position."

  def run(self):
    try:
      self.setStatus("Moving")
      self.setReactorPosition(self.reactPosition)
      self.setStatus("Complete")
    except Exception as e:
      self.abortOperation(str(e), False)
    
  def initializeComponent(self, pComponent):
    """Initializes the component validation fields"""
    self.component = pComponent
    if not self.component.has_key("reactorvalidation"):
      self.component.update({"reactorvalidation":""})
    if not self.component.has_key("positionvalidation"):
      self.component.update({"positionvalidation":""})
    self.addComponentDetails()

  def validateFull(self, pAvailableReagents):
    """Performs a full validation on the component"""
    self.component["note"] = ""
    self.component["reactorvalidation"] = "type=enum-number; values=1,2,3; required=true"
    self.component["positionvalidation"] = "type=enum-string; values=" + (",").join(self.database.GetReactorPositions(self.username)) + "; required=true"
    return self.validateQuick()

  def validateQuick(self):
    """Performs a quick validation on the component"""
    #Validate all fields
    bValidationError = False
    if not self.validateComponentField(self.component["reactor"], self.component["reactorvalidation"]) or \
       not self.validateComponentField(self.component["position"], self.component["positionvalidation"]):
      bValidationError = True

    # Set the validation error field
    self.component.update({"validationerror":bValidationError})
    return not bValidationError

  def saveValidation(self):
    """Saves validation-specific fields back to the database"""
    # Pull the original component from the database
    pDBComponent = self.database.GetComponent(self.username, self.component["id"])

    # Copy the validation fields
    pDBComponent["reactorvalidation"] = self.component["reactorvalidation"]
    pDBComponent["positionvalidation"] = self.component["positionvalidation"]
    pDBComponent["validationerror"] = self.component["validationerror"]

    # Save the component
    self.database.UpdateComponent(self.username, self.component["id"], pDBComponent["componenttype"], self.component["note"], json.dumps(pDBComponent))

  def updateComponentDetails(self, pTargetComponent):
    """Strips a component down to only the details we want to save in the database"""
    # Call the base handler
    UnitOperation.updateComponentDetails(self, pTargetComponent)

    # Update the fields we want to save
    pTargetComponent["reactor"] = self.component["reactor"]
    pTargetComponent["position"] = self.component["position"]
