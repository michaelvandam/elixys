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
      self.setPressureRegulator(2,self.pressure/3)
      self.setStatus("Moving reactor")
      self.setReactorPosition(EVAPORATE)
      self.setStatus("Starting motor")
      self.setStirSpeed(self.stirSpeed)
      self.setStatus("Heating")
      self.setEvapValves(ON)
      self.setTemp()
      self.setHeater(ON)
      self.setStatus("Evaporating")
      self.startTimer(self.evapTime)
      self.setPressureRegulator(2,self.pressure,self.evapTime/2) #Ramp pressure over the first half of the evaporation
      self.waitForTimer() #Now wait until the rest of the time elapses
      self.setStatus("Cooling")
      self.setHeater(OFF)
      self.setCool()
      self.setStatus("Completing") 
      self.setStirSpeed(OFF)
      self.setEvapValves(OFF)
      self.setStatus("Complete")
    except Exception as e:
      self.abortOperation(e)
  
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
    # Set the default evaporation pressure if the value is zero
    if self.component["evaporationpressure"] == 0:
      self.component["evaporationpressure"] = DEFAULT_EVAPORATE_PRESSURE

  def updateComponentDetails(self, pTargetComponent):
    """Strips a component down to only the details we want to save in the database"""
    # Call the base handler
    UnitOperation.updateComponentDetails(pTargetComponent)

    # Update the fields we want to save
    pTargetComponent["reactor"] = self.component["reactor"]
    pTargetComponent["duration"] = self.component["duration"]
    pTargetComponent["evaporationtemperature"] = self.component["evaporationtemperature"]
    pTargetComponent["finaltemperature"] = self.component["finaltemperature"]
    pTargetComponent["stirspeed"] = self.component["stirspeed"]
    pTargetComponent["evaporationpressure"] = self.component["evaporationpressure"]
