# Evaporate unit operation

# Imports
from UnitOperation import *

class Evaporate(UnitOperation):
  def __init__(self,systemModel,params,username = "", database = None):
    UnitOperation.__init__(self,systemModel,username,database)
    expectedParams = {REACTORID:STR,EVAPTEMP:FLOAT,PRESSURE:FLOAT,EVAPTIME:INT,COOLTEMP:INT,STIRSPEED:INT}
    paramError = self.validateParams(params,expectedParams)
    if self.paramsValid:
      self.setParams(params)
    else:
      raise UnitOpError(paramError)
		#Should have parameters listed below:
    #self.ReactorID
    #self.evapTemp
    self.evapTemp = self.reactTemp
    #self.evapTime
    self.evapTime = self.reactTime
    #self.coolTemp
    #self.stirSpeed
    
  def run(self):
    try:
      self.setStatus("Adjusting pressure")
      self.setPressureRegulator(1,self.pressure)
      self.setStatus("Moving reactor")
      self.setReactorPosition(EVAPORATE)
      self.setStatus("Starting motor")
      self.setStirSpeed(self.stirSpeed)
      self.setStatus("Moving robot")
      self.setRobotPosition()
      self.setGasTransferValve(ON)
      self.setVacuumSystem(ON)
      self.setStatus("Heating")
      self.setTemp()
      self.setHeater(ON)
      self.setStatus("Evaporating")
      self.startTimer(self.evapTime)
      #self.setPressureRegulator(1,self.pressure,self.evapTime/2) #Ramp pressure over the first half of the evaporation
      self.waitForTimer() #Now wait until the rest of the time elapses
      self.setStatus("Cooling")
      self.setHeater(OFF)
      self.setCool()
      self.setStatus("Completing") 
      self.setStirSpeed(OFF)
      self.setStatus("Moving robot")
      self.setGasTransferValve(OFF)
      self.setVacuumSystem(OFF)
      self.removeRobotPosition()
      self.setStatus("Complete")
    except Exception as e:
      self.abortOperation(e)
  
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

    #Move to the evaporate position
    self.systemModel['ReagentDelivery'].moveToReagentPosition(int(self.ReactorID[-1]),EVAPORATEPOSITION)
    self.waitForCondition(self.systemModel['ReagentDelivery'].getCurrentPosition,(int(self.ReactorID[-1]),
      EVAPORATEPOSITION, 0, 0),EQUAL,5)

    #Lower the gas transfer
    self.systemModel['ReagentDelivery'].setMoveGasTransferDown()
    self.waitForCondition(self.systemModel['ReagentDelivery'].getCurrentGasTransferDown,True,EQUAL,2)

  def removeRobotPosition(self):
    #Make sure we are down
    if not self.checkForCondition(self.systemModel['ReagentDelivery'].getCurrentGasTransferDown,True,EQUAL):
      self.abortOperation("ERROR: removeRobotPosition called while gas transfer was not down. Operation aborted.")

    #Raise the gas transfer
    self.setGasTransferValve(OFF)
    self.systemModel['ReagentDelivery'].setMoveGasTransferUp()
    self.waitForCondition(self.systemModel['ReagentDelivery'].getCurrentGasTransferUp,True,EQUAL,2)

    #Move to home
    self.systemModel['ReagentDelivery'].moveToHomeFast()
    self.waitForCondition(self.systemModel['ReagentDelivery'].getCurrentPosition,(0,0,0,0),EQUAL,5)

  """def setParams(self,currentParams):
    expectedParams = ['ReactorID','evapTime','evapTemp','coolTemp','stirSpeed']
    self.paramsValid = True
    for parameter in expectedParams:
      if not(parameter in currentParams):
        self.paramsValid = False
        #Log Error
      self.paramsValidated = True"""
      
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
    if not self.component.has_key("evaporationpressurevalidation"):
      self.component.update({"evaporationpressurevalidation":""})
    self.addComponentDetails()

  def validateFull(self, pAvailableReagents):
    """Performs a full validation on the component"""
    self.component["name"] = "Evaporate"
    self.component["reactorvalidation"] = "type=enum-number; values=1,2,3; required=true"
    self.component["durationvalidation"] = "type=number; min=0; max=7200; required=true"
    self.component["evaporationtemperaturevalidation"] = "type=number; min=20; max=200; required=true"
    self.component["finaltemperaturevalidation"] = "type=number; min=20; max=200; required=true"
    self.component["stirspeedvalidation"] = "type=number; min=0; max=5000; required=true"
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
    pDBComponent["name"] = self.component["name"]
    pDBComponent["reactorvalidation"] = self.component["reactorvalidation"]
    pDBComponent["durationvalidation"] = self.component["durationvalidation"]
    pDBComponent["evaporationtemperaturevalidation"] = self.component["evaporationtemperaturevalidation"]
    pDBComponent["finaltemperaturevalidation"] = self.component["finaltemperaturevalidation"]
    pDBComponent["stirspeedvalidation"] = self.component["stirspeedvalidation"]
    pDBComponent["evaporationpressurevalidation"] = self.component["evaporationpressurevalidation"]
    pDBComponent["evaporationpressure"] = self.component["evaporationpressure"]
    pDBComponent["validationerror"] = self.component["validationerror"]

    # Save the component
    self.database.UpdateComponent(self.username, self.component["id"], pDBComponent["componenttype"], pDBComponent["name"], json.dumps(pDBComponent))

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
    pTargetComponent["name"] = self.component["name"]
    pTargetComponent["reactor"] = self.component["reactor"]
    pTargetComponent["duration"] = self.component["duration"]
    pTargetComponent["evaporationtemperature"] = self.component["evaporationtemperature"]
    pTargetComponent["finaltemperature"] = self.component["finaltemperature"]
    pTargetComponent["stirspeed"] = self.component["stirspeed"]
    pTargetComponent["evaporationpressure"] = self.component["evaporationpressure"]

