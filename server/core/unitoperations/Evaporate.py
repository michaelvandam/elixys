# Evaporate unit operation

# Imports
from UnitOperation import *
import time

# Component type
componentType = "EVAPORATE"

# Create a unit operation from a component object
def createFromComponent(nSequenceID, pComponent, username, database, systemModel):
  pParams = {}
  pParams["ReactorID"] =  "Reactor" + str(pComponent["reactor"])
  pParams["evapTemp"] = pComponent["evaporationtemperature"]
  pParams["pressure"] = pComponent["evaporationpressure"]
  pParams["evapTime"] = pComponent["duration"]
  pParams["coolTemp"] = pComponent["finaltemperature"]
  pParams["stirSpeed"] = pComponent["stirspeed"]
  pParams["stopAtTemperature"] = pComponent["stopattemperature"]
  pEvaporate = Evaporate(systemModel, pParams, username, nSequenceID, pComponent["id"], database)
  pEvaporate.initializeComponent(pComponent)
  return pEvaporate

# Updates a component object based on a unit operation
def updateToComponent(pUnitOperation, nSequenceID, pComponent, username, database, systemModel):
  pComponent["duration"] = int(pUnitOperation.evapTime)

# Evaporate class
class Evaporate(UnitOperation):
  def __init__(self,systemModel,params,username = "",sequenceID = 0, componentID = 0, database = None):
    UnitOperation.__init__(self,systemModel,username,sequenceID,componentID,database)
    expectedParams = {REACTORID:STR,EVAPTEMP:FLOAT,PRESSURE:FLOAT,EVAPTIME:INT,COOLTEMP:INT,STIRSPEED:INT,STOPATTEMPERATURE:INT}
    paramError = self.validateParams(params,expectedParams)
    if self.paramsValid:
      self.setParams(params)
    else:
      raise UnitOpError(paramError)
    self.evapTemp = self.reactTemp
    self.evapTime = self.reactTime
    self.description = "Evaporating the contents of reactor " + str(self.ReactorID[-1]) + " at " + str(self.evapTemp) + " degrees Celsius for " + str(self.evapTime) + \
      " seconds.  Stirring at " + str(self.stirSpeed) + " and cooling to a final temperature of " + str(self.coolTemp) + " degrees Celsius."
    if self.stopAtTemperature:
      self.description += "  Stirring will stop once temperature is reached."

  def run(self):
    try:
      self.setStatus("Adjusting pressure")
      self.setPressureRegulator(1,self.pressure/3)
      self.setStatus("Moving reactor")
      self.setReactorPosition(EVAPORATE)
      self.setStatus("Starting motor")
      self.setStirSpeed(self.stirSpeed)
      self.setStatus("Moving robot")
      self.setRobotPosition()
      self.setStatus("Heating")
      self.setGasTransferValve(ON)
      self.setVacuumSystem(ON)
      self.setTemp()
      self.setHeater(ON)
      if self.stopAtTemperature > 0:
        self.setStirSpeed(OFF)
      self.setStatus("Evaporating")
      self.startTimer(self.evapTime)
      self.setPressureRegulator(1,self.pressure,self.evapTime/2) #Ramp pressure over the first half of the evaporation
      self.evapTime = self.waitForTimer() #Now wait until the rest of the time elapses
      self.setStatus("Cooling")
      self.setHeater(OFF)
      self.setCool()
      if self.stopAtTemperature == 0:
        self.setStirSpeed(OFF)
      self.setStatus("Completing")
      self.doStep(self.evaporate_Step1, "Failed to lower reactor")
      self.setStatus("Moving robot")
      self.setGasTransferValve(OFF)
      self.setVacuumSystem(OFF)
      self.removeRobotPosition()
      self.setStatus("Complete")
    except Exception as e:
      self.abortOperation(str(e), False)
  
  def setRobotPosition(self):
    #Make sure we are up
    if not self.checkForCondition(self.systemModel['ReagentDelivery'].getCurrentGripperUp,True,EQUAL):
      self.doStep(self.evaporate_Step2, "Failed to raise gripper")
    if not self.checkForCondition(self.systemModel['ReagentDelivery'].getCurrentGasTransferUp,True,EQUAL):
      self.doStep(self.evaporate_Step3, "Failed to raise gas transfer")

    #Make sure the robots are enabled
    if not(self.checkForCondition(self.systemModel['ReagentDelivery'].getRobotStatus,(ENABLED,ENABLED),EQUAL)):
      self.doStep(self.evaporate_Step4, "Failed to enable robots")

    #Move to the evaporate position and lower the gas transfer
    self.doStep(self.evaporate_Step5, "Failed to move robot to evaporate position")
    self.doStep(self.evaporate_Step6, "Failed to lower gas transfer")

  def removeRobotPosition(self):
    #This function only makes sense if we are in the down position
    #Temporarily disabled until the gas transfer down Hall effect sensor has been adjusted
    #if not self.checkForCondition(self.systemModel['ReagentDelivery'].getCurrentGasTransferDown,True,EQUAL):
    #  self.abortOperation("ERROR: removeRobotPosition called while gas transfer was not down. Operation aborted.")

    #Raise the gas transfer
    self.setGasTransferValve(OFF)
    self.doStep(self.evaporate_Step7, "Failed to raise gas transfer")

    #Move to home
    self.doStep(self.evaporate_Step8, "Failed to move to home")

  def evaporate_Step1(self):
    self.systemModel[self.ReactorID]['Motion'].moveReactorDown()
    self.waitForCondition(self.systemModel[self.ReactorID]['Motion'].getCurrentReactorDown,True,EQUAL,10)

  def evaporate_Step2(self):
    self.systemModel['ReagentDelivery'].setMoveGripperUp()
    self.waitForCondition(self.systemModel['ReagentDelivery'].getCurrentGripperUp,True,EQUAL,4)

  def evaporate_Step3(self):
    self.systemModel['ReagentDelivery'].setMoveGasTransferUp()
    self.waitForCondition(self.systemModel['ReagentDelivery'].getCurrentGasTransferUp,True,EQUAL,3)

  def evaporate_Step4(self):
    self.systemModel['ReagentDelivery'].setEnableRobots()
    self.waitForCondition(self.systemModel['ReagentDelivery'].getRobotStatus,(ENABLED,ENABLED),EQUAL,3)

  def evaporate_Step5(self):
    self.systemModel['ReagentDelivery'].moveToReagentPosition(int(self.ReactorID[-1]),EVAPORATEPOSITION)
    self.waitForCondition(self.systemModel['ReagentDelivery'].getCurrentPosition,(int(self.ReactorID[-1]),
      EVAPORATEPOSITION, 0, 0),EQUAL,5)

  def evaporate_Step6(self):
    self.systemModel['ReagentDelivery'].setMoveGasTransferDown()
    self.waitForCondition(self.systemModel['ReagentDelivery'].getCurrentGasTransferDown,True,EQUAL,2)

  def evaporate_Step7(self):
    self.systemModel['ReagentDelivery'].setMoveGasTransferUp()
    self.waitForCondition(self.systemModel['ReagentDelivery'].getCurrentGasTransferUp,True,EQUAL,2)

  def evaporate_Step8(self):
    self.systemModel['ReagentDelivery'].moveToHomeFast()
    self.waitForCondition(self.systemModel['ReagentDelivery'].getCurrentPosition,(0,0,0,0),EQUAL,5)

  def initializeComponent(self, pComponent):
    """Initializes the component validation fields"""
    self.component = pComponent
    if not self.component.has_key("reactorvalidation"):
      self.component.update({"reactorvalidation":""})
    if not self.component.has_key("durationvalidation"):
      self.component.update({"durationvalidation":""})
    if not self.component.has_key("evaporationtemperaturevalidation"):
      self.component.update({"evaporationtemperaturevalidation":""})
    if not self.component.has_key("finaltemperaturevalidation"):
      self.component.update({"finaltemperaturevalidation":""})
    if not self.component.has_key("stirspeedvalidation"):
      self.component.update({"stirspeedvalidation":""})
    if not self.component.has_key("stopattemperaturevalidation"):
      self.component.update({"stopattemperaturevalidation":""})
    if not self.component.has_key("evaporationpressurevalidation"):
      self.component.update({"evaporationpressurevalidation":""})
    self.addComponentDetails()

  def validateFull(self, pAvailableReagents):
    """Performs a full validation on the component"""
    self.component["note"] = ""
    self.component["reactorvalidation"] = "type=enum-number; values=1,2,3; required=true"
    self.component["durationvalidation"] = "type=number; min=0; max=7200; required=true"
    self.component["evaporationtemperaturevalidation"] = "type=number; min=20; max=200; required=true"
    self.component["finaltemperaturevalidation"] = "type=number; min=20; max=200; required=true"
    self.component["stirspeedvalidation"] = "type=number; min=0; max=5000; required=true"
    self.component["stopattemperaturevalidation"] = "type=enum-number; values=0,1; required=true"
    self.component["evaporationpressurevalidation"] = "type=number; min=0; max=25"
    return self.validateQuick()

  def validateQuick(self):
    """Performs a quick validation on the component"""
    #Validate all fields
    bValidationError = False
    if not self.validateComponentField(self.component["reactor"], self.component["reactorvalidation"]) or \
       not self.validateComponentField(self.component["duration"], self.component["durationvalidation"]) or \
       not self.validateComponentField(self.component["evaporationtemperature"], self.component["evaporationtemperaturevalidation"]) or \
       not self.validateComponentField(self.component["finaltemperature"], self.component["finaltemperaturevalidation"]) or \
       not self.validateComponentField(self.component["stirspeed"], self.component["stirspeedvalidation"]) or \
       not self.validateComponentField(self.component["stopattemperature"], self.component["stopattemperaturevalidation"]) or \
       not self.validateComponentField(self.component["evaporationpressure"], self.component["evaporationpressurevalidation"]):
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
    pDBComponent["durationvalidation"] = self.component["durationvalidation"]
    pDBComponent["evaporationtemperaturevalidation"] = self.component["evaporationtemperaturevalidation"]
    pDBComponent["finaltemperaturevalidation"] = self.component["finaltemperaturevalidation"]
    pDBComponent["stirspeedvalidation"] = self.component["stirspeedvalidation"]
    pDBComponent["stopattemperaturevalidation"] = self.component["stopattemperaturevalidation"]
    pDBComponent["evaporationpressurevalidation"] = self.component["evaporationpressurevalidation"]
    pDBComponent["evaporationpressure"] = self.component["evaporationpressure"]
    pDBComponent["validationerror"] = self.component["validationerror"]

    # Save the component
    self.database.UpdateComponent(self.username, self.component["id"], pDBComponent["componenttype"], self.component["note"], json.dumps(pDBComponent))

  def addComponentDetails(self):
    """Adds details to the component after retrieving it from the database and prior to sending it to the client"""
    # Set the default evaporation pressure and stir speed
    if self.component["evaporationpressure"] == 0:
      self.component["evaporationpressure"] = DEFAULT_EVAPORATE_PRESSURE
    if self.component["stirspeed"] == 0:
      self.component["stirspeed"] = DEFAULT_STIRSPEED

  def updateComponentDetails(self, pTargetComponent):
    """Strips a component down to only the details we want to save in the database"""
    # Call the base handler
    UnitOperation.updateComponentDetails(self, pTargetComponent)

    # Update the fields we want to save
    pTargetComponent["reactor"] = self.component["reactor"]
    pTargetComponent["duration"] = self.component["duration"]
    pTargetComponent["evaporationtemperature"] = self.component["evaporationtemperature"]
    pTargetComponent["finaltemperature"] = self.component["finaltemperature"]
    pTargetComponent["stirspeed"] = self.component["stirspeed"]
    pTargetComponent["stopattemperature"] = self.component["stopattemperature"]
    pTargetComponent["evaporationpressure"] = self.component["evaporationpressure"]

