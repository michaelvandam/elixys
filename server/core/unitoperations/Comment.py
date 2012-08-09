# Comment unit operation

# Imports
from UnitOperation import *
import sys
sys.path.append("/opt/elixys/core")
from Messaging import Messaging
import urllib

# Component type
componentType = "COMMENT"

# Create a unit operation from a component object
def createFromComponent(nSequenceID, pComponent, username, database, systemModel):
  pParams = {}
  pParams["userMessage"] = pComponent["comment"]
  pParams["broadcastFlag"] = pComponent["broadcastflag"]
  pComment = Comment(systemModel, pParams, username, nSequenceID, pComponent["id"], database)
  pComment.initializeComponent(pComponent)
  return pComment

# Updates a component object based on a unit operation
def updateToComponent(pUnitOperation, nSequenceID, pComponent, username, database, systemModel):
  pass

# Comment class
class Comment(UnitOperation):
  def __init__(self,systemModel,params,username = "",sequenceID = 0, componentID = 0, database = None):
    UnitOperation.__init__(self,systemModel,username,sequenceID,componentID,database)
    expectedParams = {USERMESSAGE:STR,BROADCASTFLAG:INT}
    paramError = self.validateParams(params,expectedParams)
    if self.paramsValid:
      self.setParams(params)
    else:
      raise UnitOpError(paramError)

  def run(self):
    if self.broadcastFlag:
      pMessaging = Messaging(self.username, self.database)
      pMessaging.broadcastMessage(urllib.unquote(self.userMessage))
  
  def initializeComponent(self, pComponent):
    """Initializes the component validation fields"""
    self.component = pComponent
    if not self.component.has_key("commentvalidation"):
      self.component.update({"commentvalidation":""})
    if not self.component.has_key("broadcastflagvalidation"):
      self.component.update({"broadcastflagvalidation":""})
    self.addComponentDetails()

  def validateFull(self, pAvailableReagents):
    """Performs a full validation on the component"""
    self.component["note"] = ""
    self.component["commentvalidation"] = "type=string"
    self.component["broadcastflagvalidation"] = "type=enum-number; values=0,1; required=true"
    return self.validateQuick()

  def validateQuick(self):
    """Performs a quick validation on the component"""
    #Validate all fields
    bValidationError = False
    if not self.validateComponentField(self.component["comment"], self.component["commentvalidation"]) or \
       not self.validateComponentField(self.component["broadcastflag"], self.component["broadcastflagvalidation"]):
      bValidationError = True

    # Set the validation error field
    self.component.update({"validationerror":bValidationError})
    return not bValidationError

  def saveValidation(self):
    """Saves validation-specific fields back to the database"""
    # Pull the original component from the database
    pDBComponent = self.database.GetComponent(self.username, self.component["id"])

    # Copy the validation fields
    pDBComponent["commentvalidation"] = self.component["commentvalidation"]
    pDBComponent["broadcastflagvalidation"] = self.component["broadcastflagvalidation"]
    pDBComponent["validationerror"] = self.component["validationerror"]

    # Save the component
    self.database.UpdateComponent(self.username, self.component["id"], pDBComponent["componenttype"], self.component["note"], json.dumps(pDBComponent))

  def updateComponentDetails(self, pTargetComponent):
    """Strips a component down to only the details we want to save in the database"""
    # Call the base handler
    UnitOperation.updateComponentDetails(self, pTargetComponent)

    # Update the field we want to save
    pTargetComponent["comment"] = self.component["comment"]
    pTargetComponent["broadcastflag"] = self.component["broadcastflag"]

