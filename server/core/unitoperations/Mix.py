# Mix unit operation

# Imports
from UnitOperation import *

# Component type
componentType = "MIX"

# Create a unit operation from a component object
def createFromComponent(nSequenceID, pComponent, username, database, systemModel):
  pParams = {}
  pParams["ReactorID"] = "Reactor" + str(pComponent["reactor"])
  pParams["stirSpeed"] = pComponent["stirspeed"]
  pParams["duration"] = pComponent["mixtime"]
  pMix = Mix(systemModel, pParams, username, nSequenceID, pComponent["id"], database)
  pMix.initializeComponent(pComponent)
  return pMix

# Updates a component object based on a unit operation
def updateToComponent(pUnitOperation, nSequenceID, pComponent, username, database, systemModel):
  pComponent["mixtime"] = int(pUnitOperation.duration)

# Mix class
class Mix(UnitOperation):
  def __init__(self,systemModel,params,username = "",sequenceID = 0, componentID = 0, database = None):
    UnitOperation.__init__(self,systemModel,username,sequenceID,componentID,database)
    expectedParams = {REACTORID:STR,STIRSPEED:INT,DURATION:INT}
    self.validateParams(params,expectedParams)
    if self.paramsValid:
      self.setParams(params)
    else:
      raise UnitOpError(paramError)
    self.description = "Mixing the contents of reactor " + str(self.ReactorID[-1]) + " for " + str(self.duration) + " seconds by stirring at " + str(self.stirSpeed) + ".";

    # Should have the params listed below:
    # self.ReactorID
    # self.stirSpeed
    # self.duration
  def run(self):
    try:
      self.setStatus("Mixing")
      self.setStirSpeed(self.stirSpeed)
      self.startTimer(self.duration)
      self.duration = self.waitForTimer()
      self.setStirSpeed(OFF)
      self.setStatus("Complete")
    except Exception as e:
      self.abortOperation(str(e), False)
  
  def initializeComponent(self, pComponent):
    """Initializes the component validation fields"""
    self.component = pComponent
    if not self.component.has_key("reactorvalidation"):
      self.component.update({"reactorvalidation":""})
    if not self.component.has_key("mixtimevalidation"):
      self.component.update({"mixtimevalidation":""})
    if not self.component.has_key("stirspeedvalidation"):
      self.component.update({"stirspeedvalidation":""})
    self.addComponentDetails()

  def validateFull(self, pAvailableReagents):
    """Performs a full validation on the component"""
    self.component["note"] = ""
    self.component["reactorvalidation"] = "type=enum-number; values=1,2,3; required=true"
    self.component["mixtimevalidation"] = "type=number; min=0; max=7200; required=true"
    self.component["stirspeedvalidation"] = "type=number; min=0; max=5000; required=true"
    return self.validateQuick()

  def validateQuick(self):
    """Performs a quick validation on the component"""
    #Validate all fields
    bValidationError = False
    if not self.validateComponentField(self.component["reactor"], self.component["reactorvalidation"]) or \
       not self.validateComponentField(self.component["mixtime"], self.component["mixtimevalidation"]) or \
       not self.validateComponentField(self.component["stirspeed"], self.component["stirspeedvalidation"]):
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
    pDBComponent["mixtimevalidation"] = self.component["mixtimevalidation"]
    pDBComponent["stirspeedvalidation"] = self.component["stirspeedvalidation"]
    pDBComponent["validationerror"] = self.component["validationerror"]

    # Save the component
    self.database.UpdateComponent(self.username, self.component["id"], pDBComponent["componenttype"], self.component["note"], json.dumps(pDBComponent))

  def addComponentDetails(self):
    """Adds details to the component after retrieving it from the database and prior to sending it to the client"""
    # Set the default stir speed
    if self.component["stirspeed"] == 0:
      self.component["stirspeed"] = DEFAULT_STIRSPEED

  def updateComponentDetails(self, pTargetComponent):
    """Strips a component down to only the details we want to save in the database"""
    # Call the base handler
    UnitOperation.updateComponentDetails(self, pTargetComponent)

    # Update the fields we want to save
    pTargetComponent["reactor"] = self.component["reactor"]
    pTargetComponent["mixtime"] = self.component["mixtime"]
    pTargetComponent["stirspeed"] = self.component["stirspeed"]

