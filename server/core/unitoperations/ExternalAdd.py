# ExternalAdd unit operation

# Imports
from UnitOperation import *

# Component type
componentType = "EXTERNALADD"

# Create a unit operation from a component object
def createFromComponent(nSequenceID, pComponent, username, database, systemModel):
  pParams = {}
  pParams["ReactorID"] = "Reactor" + str(pComponent["reactor"])
  pParams["externalReagentName"] = pComponent["reagentname"]
  pExternalAdd = ExternalAdd(systemModel, pParams, username, nSequenceID, pComponent["id"], database)
  pExternalAdd.initializeComponent(pComponent)
  return pExternalAdd

# Updates a component object based on a unit operation
def updateToComponent(pUnitOperation, nSequenceID, pComponent, username, database, systemModel):
  pass

# ExternalAdd class
class ExternalAdd(UnitOperation):
  def __init__(self,systemModel,params,username = "",sequenceID = 0, componentID = 0, database = None):
    UnitOperation.__init__(self,systemModel,username,sequenceID,componentID,database)
    expectedParams = {REACTORID:STR,EXTERNALREAGENTNAME:STR}
    paramError = self.validateParams(params,expectedParams)
    if self.paramsValid:
      self.setParams(params)
    else:
      raise UnitOpError(paramError)
    self.description = "Externally adding " + str(self.externalReagentName) + " to reactor " + str(self.ReactorID[-1]) + "."

    #Should have parameters listed below: 
    #self.ReactorID
    #self.externalReagentName

  def run(self):
    try:
      self.setStatus("Moving reactor")
      self.setReactorPosition(ADDREAGENT)             #Move reactor to position
      self.setStatus("Waiting for user input")
      self.waitForUserInput()                         #Wait until user delivers reagent
      self.setStatus("Complete")
    except Exception as e:
      self.abortOperation(str(e), False)
  
  def initializeComponent(self, pComponent):
    """Initializes the component validation fields"""
    self.component = pComponent
    if not self.component.has_key("reactorvalidation"):
      self.component.update({"reactorvalidation":""})
    if not self.component.has_key("reagentnamevalidation"):
      self.component.update({"reagentnamevalidation":""})
    self.addComponentDetails()

  def validateFull(self, pAvailableReagents):
    """Performs a full validation on the component"""
    self.component["note"] = ""
    self.component["reactorvalidation"] = "type=enum-number; values=1,2,3; required=true"
    self.component["reagentnamevalidation"] = "type=string; required=true"
    return self.validateQuick()

  def validateQuick(self):
    """Performs a quick validation on the component"""
    #Validate all fields
    bValidationError = False
    if not self.validateComponentField(self.component["reactor"], self.component["reactorvalidation"]) or \
       not self.validateComponentField(self.component["reagentname"], self.component["reagentnamevalidation"]):
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
    pDBComponent["reagentnamevalidation"] = self.component["reagentnamevalidation"]
    pDBComponent["validationerror"] = self.component["validationerror"]

    # Set the note
    pDBComponent["note"] = self.component["reagentname"]

    # Save the component
    self.database.UpdateComponent(self.username, self.component["id"], pDBComponent["componenttype"], self.component["note"], json.dumps(pDBComponent))

  def updateComponentDetails(self, pTargetComponent):
    """Strips a component down to only the details we want to save in the database"""
    # Call the base handler
    UnitOperation.updateComponentDetails(self, pTargetComponent)

    # Update the fields we want to save
    pTargetComponent["reactor"] = self.component["reactor"]
    pTargetComponent["reagentname"] = self.component["reagentname"]
    pTargetComponent["message"] = "Externally add " + self.component["reagentname"] + " to reactor " + str(self.component["reactor"]) + "."

