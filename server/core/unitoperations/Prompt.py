# Prompt unit operation

# Imports
from UnitOperation import *

# Component type
componentType = "PROMPT"

# Create a unit operation from a component object
def createFromComponent(nSequenceID, pComponent, username, database, systemModel):
  pParams = {}
  pParams["userMessage"] = str(pComponent["message"])
  pPrompt = Prompt(systemModel, pParams, username, nSequenceID, pComponent["id"], database)
  pPrompt.initializeComponent(pComponent)
  return pPrompt

# Updates a component object based on a unit operation
def updateToComponent(pUnitOperation, nSequenceID, pComponent, username, database, systemModel):
  pass

# Prompt class
class Prompt(UnitOperation):
  def __init__(self,systemModel,params,username = "",sequenceID = 0, componentID = 0, database = None):
    UnitOperation.__init__(self,systemModel,username,sequenceID,componentID,database)
    expectedParams = {USERMESSAGE:STR}
    paramError = self.validateParams(params,expectedParams)
    if self.paramsValid:
      self.setParams(params)
    else:
      raise UnitOpError(paramError)
    self.description = "Prompting the user."

  def run(self):
    try:
      # Wait for user input
      self.setStatus("Waiting for user input")
      self.waitForUserInput()
      self.setStatus("Complete")
    except Exception as e:
      self.abortOperation(str(e), False)
  
  def initializeComponent(self, pComponent):
    """Initializes the component validation fields"""
    self.component = pComponent
    if not self.component.has_key("messagevalidation"):
      self.component.update({"messagevalidation":""})
    self.addComponentDetails()

  def validateFull(self, pAvailableReagents):
    """Performs a full validation on the component"""
    self.component["note"] = ""
    self.component["messagevalidation"] = "type=string; required=true"
    return self.validateQuick()

  def validateQuick(self):
    """Performs a quick validation on the component"""
    #Validate all fields
    bValidationError = not self.validateComponentField(self.component["message"], self.component["messagevalidation"])

    # Set the validation error field
    self.component.update({"validationerror":bValidationError})
    return not bValidationError

  def saveValidation(self):
    """Saves validation-specific fields back to the database"""
    # Pull the original component from the database
    pDBComponent = self.database.GetComponent(self.username, self.component["id"])

    # Copy the validation fields
    pDBComponent["messagevalidation"] = self.component["messagevalidation"]
    pDBComponent["validationerror"] = self.component["validationerror"]

    # Save the component
    self.database.UpdateComponent(self.username, self.component["id"], pDBComponent["componenttype"], self.component["note"], json.dumps(pDBComponent))

  def updateComponentDetails(self, pTargetComponent):
    """Strips a component down to only the details we want to save in the database"""
    # Call the base handler
    UnitOperation.updateComponentDetails(self, pTargetComponent)

    # Update the field we want to save
    pTargetComponent["message"] = self.component["message"]
