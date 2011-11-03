# Move unit operation

# Imports
from UnitOperations import *

class Move(UnitOperation):
  def __init__(self,systemModel,params,username = "", database = None):
    UnitOperation.__init__(self,systemModel,username,database)
    expectedParams = {REACTORID:STR,REACTPOSITION:STR}
    paramError = self.validateParams(params,expectedParams)
    if self.paramsValid:
      self.setParams(params)
    else:
      raise UnitOpError(paramError)
    #Should have parameters listed below:
    #self.ReactorID
    #self.reactPosition
  def run(self):
    try:
      self.setStatus("Moving")
      self.setReactorPosition(self.reactPosition)
      self.setStatus("Complete")
    except Exception as e:
      self.abortOperation(e)
    
  def initializeComponent(self, pComponent):
    """Initializes the component validation fields"""
    self.component = pComponent
    if not self.component.has_key("reactorvalidation"):
      self.component.update({"reactorvalidationvalidation":""})
    if not self.component.has_key("positionvalidation"):
      self.component.update({"positionvalidation":""})
    self.addComponentDetails()

  def validateFull(self, pAvailableReagents):
    """Performs a full validation on the component"""
    self.component["name"] = "Move"
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
    pDBComponent["name"] = self.component["name"]
    pDBComponent["reactorvalidation"] = self.component["reactorvalidation"]
    pDBComponent["positionvalidation"] = self.component["positionvalidation"]
    pDBComponent["validationerror"] = self.component["validationerror"]

    # Save the component
    self.database.UpdateComponent(self.username, self.component["id"], pDBComponent["componenttype"], pDBComponent["name"], json.dumps(pDBComponent))

  def updateComponentDetails(self, pTargetComponent):
    """Strips a component down to only the details we want to save in the database"""
    # Call the base handler
    UnitOperation.updateComponentDetails(pTargetComponent)

    # Update the fields we want to save
    pTargetComponent["reactor"] = self.component["reactor"]
    pTargetComponent["position"] = self.component["position"]
