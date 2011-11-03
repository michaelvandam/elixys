# Transfer unit operation

# Imports
from UnitOperations import *

class Transfer(UnitOperation):
  def __init__(self,systemModel,params,username = "", database = None):
    UnitOperation.__init__(self,systemModel,username,database)
    self.setParams(params) 
    #Should have parameters listed below:
    #self.ReactorID
    #self.transferReactorID
    #self.transferType
    #self.transferTimer
    #self.transferPressure
  def run(self):
    try:
      self.setStatus("Moving reactors")
      self.setReactorPosition(TRANSFER)
      self.setReactorPosition(ADDREAGENT,self.transferReactorID)
      self.setStatus("Transferring")
      if (self.transferType == "Trap"):
        self.setStopcockPosition(TRANSFERTRAP)
      elif (self.transferType == "Elute"):
        self.setStopcockPosition(TRANSFERELUTE)
      else:
        raise Exception("Unknown transfer type")
      time.sleep(0.5)
      self.startTransfer(ON)
      self.startTimer(self.transferTimer)
      self.waitForTimer()
      self.startTransfer(OFF)
      self.setStopcockPosition(TRANSFERDEFAULT)
      self.setStatus("Complete")
    except Exception as e:
      self.abortOperation(e)
      
  def initializeComponent(self, pComponent):
    """Initializes the component validation fields"""
    self.component = pComponent
    if not self.component.has_key("sourcereactorvalidation"):
      self.component.update({"sourcereactorvalidation":""})
    if not self.component.has_key("targetreactorvalidation"):
      self.component.update({"targetreactorvalidation":""})
    if not self.component.has_key("modevalidation"):
      self.component.update({"modevalidation":""})
    if not self.component.has_key("pressurevalidation"):
      self.component.update({"pressurevalidation":""})
    if not self.component.has_key("durationvalidation"):
      self.component.update({"durationvalidation":""})
    self.addComponentDetails()

  def validateFull(self, pAvailableReagents):
    """Performs a full validation on the component"""
    self.component["name"] = "Transfer"
    self.component["sourcereactorvalidation"] = "type=enum-number; values=1,2,3; required=true"
    self.component["targetreactorvalidation"] = "type=enum-number; values=1,2,3; required=true"
    self.component["modevalidation"] = "type=enum-string; values=Trap,Elute; required=true"
    self.component["pressurevalidation"] = "type=number; min=0; max=25"
    self.component["durationvalidation"] = "type=number; min=0; max=7200; required=true"
    return self.validateQuick()

  def validateQuick(self):
    """Performs a quick validation on the component"""
    #Validate all fields
    bValidationError = False
    if not self.validateComponentField(self.component["sourcereactor"], self.component["sourcereactorvalidation"]) or \
       not self.validateComponentField(self.component["targetreactor"], self.component["targetreactorvalidation"]) or \
       not self.validateComponentField(self.component["mode"], self.component["modevalidation"]) or \
       not self.validateComponentField(self.component["pressure"], self.component["pressurevalidation"]) or \
       not self.validateComponentField(self.component["duration"], self.component["durationvalidation"]):
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
    pDBComponent["sourcereactorvalidation"] = self.component["sourcereactorvalidation"]
    pDBComponent["targetreactorvalidation"] = self.component["targetreactorvalidation"]
    pDBComponent["pressurevalidation"] = self.component["pressurevalidation"]
    pDBComponent["modevalidation"] = self.component["modevalidation"]
    pDBComponent["durationvalidation"] = self.component["durationvalidation"]
    pDBComponent["validationerror"] = self.component["validationerror"]

    # Save the component
    self.database.UpdateComponent(self.username, self.component["id"], pDBComponent["componenttype"], pDBComponent["name"], json.dumps(pDBComponent))

  def updateComponentDetails(self, pTargetComponent):
    """Strips a component down to only the details we want to save in the database"""
    # Call the base handler
    UnitOperation.updateComponentDetails(pTargetComponent)

    # Update the fields we want to save
    pTargetComponent["sourcereactor"] = self.component["sourcereactor"]
    pTargetComponent["targetreactor"] = self.component["targetreactor"]
    pTargetComponent["pressure"] = self.component["pressure"]
    pTargetComponent["mode"] = self.component["mode"]
    pTargetComponent["duration"] = self.component["duration"]
