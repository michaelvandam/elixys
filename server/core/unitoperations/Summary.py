# Summary unit operation

# Imports
from UnitOperation import *

# Component type
componentType = "SUMMARY"

# Create a unit operation from scratch
def createNewComponent(sRunError):
  pComponent = {}
  pComponent["type"] = "component"
  pComponent["componenttype"] = "SUMMARY"
  pComponent["note"] = ""
  if sRunError == "":
    pComponent["successflag"] = 1
  else:
    pComponent["successflag"] = 0
  pComponent["message"] = sRunError
  return pComponent

# Create a unit operation from a component object
def createFromComponent(nSequenceID, pComponent, username, database, systemModel):
  pParams = {}
  pParams["summaryFlag"] = pComponent["successflag"]
  pParams["summaryMessage"] = pComponent["message"]
  pSummary = Summary(systemModel, pParams, username, nSequenceID, pComponent["id"], database)
  pSummary.initializeComponent(pComponent)
  return pSummary

# Updates a component object based on a unit operation
def updateToComponent(pUnitOperation, nSequenceID, pComponent, username, database, systemModel):
  pass

# Summary class
class Summary(UnitOperation):
  def __init__(self,systemModel,params,username = "",sequenceID = 0, componentID = 0, database = None):
    UnitOperation.__init__(self,systemModel,username,sequenceID,componentID,database)
    expectedParams = {SUMMARYFLAG:INT,SUMMARYMESSAGE:STR}
    paramError = self.validateParams(params,expectedParams)
    if self.paramsValid:
      self.setParams(params)
    else:
      raise UnitOpError(paramError)

    #Should have parameters listed below:
    #self.summaryFlag
    #self.summaryMessage
    
  def run(self):
    try:
      self.setStatus("Waiting for user input")
      self.waitForUserInput()
      self.setStatus("Complete")
    except Exception as e:
      self.abortOperation(str(e), False)
      
  def initializeComponent(self, pComponent):
    """Initializes the component validation fields"""
    self.component = pComponent
    if not self.component.has_key("sucessflagvalidation"):
      self.component.update({"successflagvalidation":""})
    if not self.component.has_key("messagevalidation"):
      self.component.update({"messagevalidation":""})
    self.addComponentDetails()

  def validateFull(self, pAvailableReagents):
    """Performs a full validation on the component"""
    self.component["note"] = ""
    self.component["successflagvalidation"] = "type=enum-number; values=0,1; required=true"
    self.component["messagevalidation"] = "type=string"
    return self.validateQuick()

  def validateQuick(self):
    """Performs a quick validation on the component"""
    #Validate all fields
    bValidationError = False
    if not self.validateComponentField(self.component["successflag"], self.component["successflagvalidation"]) or \
       not self.validateComponentField(self.component["message"], self.component["messagevalidation"]):
      bValidationError = True

    # Set the validation error field
    self.component.update({"validationerror":bValidationError})
    return not bValidationError

  def saveValidation(self):
    """Saves validation-specific fields back to the database"""
    # Pull the original component from the database
    pDBComponent = self.database.GetComponent(self.username, self.component["id"])

    # Copy the validation fields
    pDBComponent["successflagvalidation"] = self.component["successflagvalidation"]
    pDBComponent["messagevalidation"] = self.component["messagevalidation"]
    pDBComponent["validationerror"] = self.component["validationerror"]

    # Save the component
    self.database.UpdateComponent(self.username, self.component["id"], pDBComponent["componenttype"], self.component["note"], json.dumps(pDBComponent))

  def updateComponentDetails(self, pTargetComponent):
    """Strips a component down to only the details we want to save in the database"""
    # Call the base handler
    UnitOperation.updateComponentDetails(self, pTargetComponent)

    # Update the fields we want to save
    pTargetComponent["successflag"] = self.component["successflag"]
    pTargetComponent["message"] = self.component["message"]

