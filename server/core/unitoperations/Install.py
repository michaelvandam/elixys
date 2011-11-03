# Install unit operation

# Imports
from UnitOperations import *

class Install(UnitOperation):
  def __init__(self,systemModel,params,username = "", database = None):
    UnitOperation.__init__(self,systemModel,username,database)
    self.setParams(params)
		#Should have parameters listed below:
    #self.ReactorID
    #self.userMessage
    
  def run(self):
    try:
      self.setStatus("Moving reactor")
      self.setReactorPosition(INSTALL)
      self.setStatus("Complete")
    except Exception as e:
      self.abortOperation(e)
      
  def initializeComponent(self, pComponent):
    """Initializes the component validation fields"""
    self.component = pComponent
    if not self.component.has_key("reactorvalidation"):
      self.component.update({"reactorvalidation":""})
    if not self.component.has_key("messagevalidation"):
      self.component.update({"messagevalidation":""})
    self.addComponentDetails()

  def validateFull(self, pAvailableReagents):
    """Performs a full validation on the component"""
    self.component["name"] = "Install"
    self.component["reactorvalidation"] = "type=enum-number; values=1,2,3; required=true"
    self.component["messagevalidation"] = "type=string; required=true"
    return self.validateQuick()

  def validateQuick(self):
    """Performs a quick validation on the component"""
    #Validate all fields
    bValidationError = False
    if not self.validateComponentField(self.component["reactor"], self.component["reactorvalidation"]) or \
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
    pDBComponent["name"] = self.component["name"]
    pDBComponent["reactorvalidation"] = self.component["reactorvalidation"]
    pDBComponent["messagevalidation"] = self.component["messagevalidation"]
    pDBComponent["validationerror"] = self.component["validationerror"]

    # Save the component
    self.database.UpdateComponent(self.username, self.component["id"], pDBComponent["componenttype"], pDBComponent["name"], json.dumps(pDBComponent))

  def updateComponentDetails(self, pTargetComponent):
    """Strips a component down to only the details we want to save in the database"""
    # Call the base handler
    UnitOperation.updateComponentDetails(pTargetComponent)

    # Update the fields we want to save
    pTargetComponent["reactor"] = self.component["reactor"]
    pTargetComponent["message"] = self.omponent["message"]

