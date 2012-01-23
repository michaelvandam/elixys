# Transfer unit operation

# Imports
from UnitOperation import *

# Component type
componentType = "TRANSFER"

# Create a unit operation from a component object
def createFromComponent(nSequenceID, pComponent, username, database, systemModel):
  pParams = {}
  pParams["ReactorID"] = "Reactor" + str(pComponent["sourcereactor"])
  pParams["transferReactorID"] = "Reactor" + str(pComponent["targetreactor"])
  pParams["transferType"] = str(pComponent["mode"])
  pParams["transferTimer"] = pComponent["duration"]
  pParams["transferPressure"] = pComponent["pressure"]
  pTransfer = Transfer(systemModel, pParams, username, nSequenceID, pComponent["id"], database)
  pTransfer.initializeComponent(pComponent)
  return pTransfer

# Updates a component object based on a unit operation
def updateToComponent(pUnitOperation, nSequenceID, pComponent, username, database, systemModel):
  pComponent["duration"] = pUnitOperations.transferTimer

# Transfer class
class Transfer(UnitOperation):
  def __init__(self,systemModel,params,username = "",sequenceID = 0, componentID = 0, database = None):
    UnitOperation.__init__(self,systemModel,username,sequenceID,componentID,database)
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
      self.setStatus("Moving robot")
      self.setRobotPosition()
      self.setStatus("Transferring")
      if (self.transferType == "Trap"):
        self.setStopcockPosition(TRANSFERTRAP)
      elif (self.transferType == "Elute"):
        self.setStopcockPosition(TRANSFERELUTE)
      else:
        raise Exception("Unknown transfer type")
      time.sleep(0.5)
      self.setPressureRegulator(1,self.transferPressure)
      self.setGasTransferValve(ON)
      self.startTimer(self.transferTimer)
      self.transferTimer = self.waitForTimer()
      self.setGasTransferValve(OFF)
      self.setStopcockPosition(TRANSFERDEFAULT)
      self.setStatus("Moving robot")
      self.removeRobotPosition()
      self.setStatus("Complete")
    except Exception as e:
      self.abortOperation(str(e), False)
      
  def setRobotPosition(self):
    #Make sure the reagent robot is up
    if not self.checkForCondition(self.systemModel['ReagentDelivery'].getCurrentGripperUp,True,EQUAL):
      self.abortOperation("ERROR: setRobotPosition called while gripper was not up. Operation aborted.") 
    if not self.checkForCondition(self.systemModel['ReagentDelivery'].getCurrentGasTransferUp,True,EQUAL):
      self.abortOperation("ERROR: setRobotPosition called while gas transfer was not up. Operation aborted.") 

    #Make sure the robots are enabled
    if not(self.checkForCondition(self.systemModel['ReagentDelivery'].getRobotStatus,(ENABLED,ENABLED),EQUAL)):
      self.systemModel['ReagentDelivery'].setEnableRobots()
      self.waitForCondition(self.systemModel['ReagentDelivery'].getRobotStatus,(ENABLED,ENABLED),EQUAL,3)

    #Move to the transfer position
    self.systemModel['ReagentDelivery'].moveToReagentPosition(int(self.ReactorID[-1]),TRANSFERPOSITION)
    self.waitForCondition(self.systemModel['ReagentDelivery'].getCurrentPosition,(int(self.ReactorID[-1]),
      TRANSFERPOSITION, 0, 0),EQUAL,5)

    #Lower the gas transfer
    self.systemModel['ReagentDelivery'].setMoveGasTransferDown()
    self.waitForCondition(self.systemModel['ReagentDelivery'].getCurrentGasTransferDown,True,EQUAL,2)

  def removeRobotPosition(self):
    #Make sure we are down (this is causing problems due to actuator sinking)
    #if not self.checkForCondition(self.systemModel['ReagentDelivery'].getCurrentGasTransferDown,True,EQUAL):
    #  self.abortOperation("ERROR: removeRobotPosition called while gas transfer was not down. Operation aborted.")

    #Raise the gas transfer
    self.setGasTransferValve(OFF)
    self.systemModel['ReagentDelivery'].setMoveGasTransferUp()
    self.waitForCondition(self.systemModel['ReagentDelivery'].getCurrentGasTransferUp,True,EQUAL,2)

    #Move to home
    self.systemModel['ReagentDelivery'].moveToHomeFast()
    self.waitForCondition(self.systemModel['ReagentDelivery'].getCurrentPosition,(0,0,0,0),EQUAL,5)

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

  def addComponentDetails(self):
    """Adds details to the component after retrieving it from the database and prior to sending it to the client"""
    # Set the default transfer pressure and time
    if self.component["pressure"] == 0:
      self.component["pressure"] = DEFAULT_TRANSFER_PRESSURE
    if self.component["duration"] == 0:
      self.component["duration"] = DEFAULT_TRANSFER_DURATION

  def updateComponentDetails(self, pTargetComponent):
    """Strips a component down to only the details we want to save in the database"""
    # Call the base handler
    UnitOperation.updateComponentDetails(self, pTargetComponent)

    # Update the fields we want to save
    pTargetComponent["name"] = self.component["name"]
    pTargetComponent["sourcereactor"] = self.component["sourcereactor"]
    pTargetComponent["targetreactor"] = self.component["targetreactor"]
    pTargetComponent["pressure"] = self.component["pressure"]
    pTargetComponent["mode"] = self.component["mode"]
    pTargetComponent["duration"] = self.component["duration"]

