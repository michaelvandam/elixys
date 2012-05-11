# React unit operation

# Imports
from UnitOperation import *

# Component type
componentType = "REACT"

# Create a unit operation from a component object
def createFromComponent(nSequenceID, pComponent, username, database, systemModel):
  pParams = {}
  pParams["ReactorID"] = "Reactor" + str(pComponent["reactor"])
  pParams["reactTemp"] = pComponent["reactiontemperature"]
  pParams["reactTime"] = pComponent["duration"]
  pParams["coolTemp"] = pComponent["finaltemperature"]
  pParams["coolingDelay"] = pComponent["coolingdelay"]
  pParams["reactPosition"] = "React" + str(pComponent["position"])
  pParams["stirSpeed"] = pComponent["stirspeed"]
  pParams["stopAtTemperature"] = pComponent["stopattemperature"]
  pReact = React(systemModel, pParams, username, nSequenceID, pComponent["id"], database)
  pReact.initializeComponent(pComponent)
  return pReact

# Updates a component object based on a unit operation
def updateToComponent(pUnitOperation, nSequenceID, pComponent, username, database, systemModel):
  pComponent["duration"] = int(pUnitOperation.reactTime)

# React class
class React(UnitOperation):
  def __init__(self,systemModel,params,username = "",sequenceID = 0, componentID = 0, database = None):
    UnitOperation.__init__(self,systemModel,username,sequenceID,componentID,database)
    expectedParams = {REACTORID:STR,REACTTEMP:FLOAT,REACTTIME:INT,COOLTEMP:INT,COOLINGDELAY:INT,REACTPOSITION:STR,STIRSPEED:INT,STOPATTEMPERATURE:INT}
    paramError = self.validateParams(params,expectedParams)
    if self.paramsValid:
      self.setParams(params)
    else:
      raise UnitOpError(paramError)
    self.description = "Reacting reactor " + str(self.ReactorID[-1]) + " in position " + str(self.reactPosition) + " at " + str(self.reactTemp) + " degrees Celsius for " + \
      str(self.reactTime) + " seconds.  Stirring at " + str(self.stirSpeed) + " and cooling to " + str(self.coolTemp) + " degrees Celsius"
    if self.coolingDelay != 0:
      self.description += " with an additional delay of " + str(self.coolingDelay) + " seconds."
    else:
      self.description += "."
    if self.stopAtTemperature:
      self.description += "  Stirring will stop once temperature is reached."

    #Should have parameters listed below:
    #self.ReactorID
    #self.reactTemp
    #self.reactTime
    #self.coolTemp
    #self.coolingDelay
    #self.reactPosition
    #self.stirSpeed
    #self.stopAtTemperature

  def run(self):
    try:
      self.logInfo("###Temp### React stop at temperature: " + str(self.stopAtTemperature))    # Temp
      self.setStatus("Moving reactor")
      self.setReactorPosition(self.reactPosition)#REACTA OR REACTB
      self.setStatus("Starting motor")
      self.setStirSpeed(self.stirSpeed)
      self.setStatus("Heating")
      self.setTemp()
      self.setHeater(ON)
      if self.stopAtTemperature > 0:
        self.setStirSpeed(OFF)
        self.logInfo("###Temp### React stopping at temperature")    # Temp
      self.setStatus("Reacting")
      self.startTimer(self.reactTime)
      self.reactTime = self.waitForTimer()
      self.setStatus("Cooling")
      self.setHeater(OFF)
      self.setCool(self.coolingDelay)
      if self.stopAtTemperature == 0:
        self.setStirSpeed(OFF)
        self.logInfo("###Temp### React stopping after cooling")    # Temp
      self.setStatus("Completing") 
      self.setStatus("Complete")
    except Exception as e:
      self.abortOperation(str(e), False)

  def initializeComponent(self, pComponent):
    """Initializes the component validation fields"""
    self.component = pComponent
    if not self.component.has_key("reactorvalidation"):
      self.component.update({"reactorvalidation":""})
    if not self.component.has_key("positionvalidation"):
      self.component.update({"positionvalidation":""})
    if not self.component.has_key("durationvalidation"):
      self.component.update({"durationvalidation":""})
    if not self.component.has_key("reactiontemperaturevalidation"):
      self.component.update({"reactiontemperaturevalidation":""})
    if not self.component.has_key("finaltemperaturevalidation"):
      self.component.update({"finaltemperaturevalidation":""})
    if not self.component.has_key("coolingdelayvalidation"):
      self.component.update({"coolingdelayvalidation":""})
    if not self.component.has_key("stirspeedvalidation"):
      self.component.update({"stirspeedvalidation":""})
    if not self.component.has_key("stopattemperaturevalidation"):
      self.component.update({"stopattemperaturevalidation":""})
    self.addComponentDetails()

  def validateFull(self, pAvailableReagents):
    """Performs a full validation on the component"""
    self.component["note"] = ""
    self.component["reactorvalidation"] = "type=enum-number; values=1,2,3; required=true"
    self.component["positionvalidation"] = "type=enum-number; values=1,2; required=true"
    self.component["durationvalidation"] = "type=number; min=0; max=7200; required=true"
    self.component["reactiontemperaturevalidation"] = "type=number; min=20; max=200; required=true"
    self.component["finaltemperaturevalidation"] = "type=number; min=20; max=200; required=true"
    self.component["coolingdelayvalidation"] = "type=number; min=0; max=7200; required=true"
    self.component["stirspeedvalidation"] = "type=number; min=0; max=5000; required=true"
    self.component["stopattemperaturevalidation"] = "type=enum-number; values=0,1; required=true"

    #Do a quick validation
    return self.validateQuick()

  def validateQuick(self):
    """Performs a quick validation on the component"""
    #Validate all fields
    bValidationError = False
    if not self.validateComponentField(self.component["reactor"], self.component["reactorvalidation"]) or \
       not self.validateComponentField(self.component["position"], self.component["positionvalidation"]) or \
       not self.validateComponentField(self.component["duration"], self.component["durationvalidation"]) or \
       not self.validateComponentField(self.component["reactiontemperature"], self.component["reactiontemperaturevalidation"]) or \
       not self.validateComponentField(self.component["finaltemperature"], self.component["finaltemperaturevalidation"]) or \
       not self.validateComponentField(self.component["coolingdelay"], self.component["coolingdelayvalidation"]) or \
       not self.validateComponentField(self.component["stirspeed"], self.component["stirspeedvalidation"]) or \
       not self.validateComponentField(self.component["stopattemperature"], self.component["stopattemperaturevalidation"]):
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
    pDBComponent["positionvalidation"] = self.component["positionvalidation"]
    pDBComponent["durationvalidation"] = self.component["durationvalidation"]
    pDBComponent["reactiontemperaturevalidation"] = self.component["reactiontemperaturevalidation"]
    pDBComponent["finaltemperaturevalidation"] = self.component["finaltemperaturevalidation"]
    pDBComponent["coolingdelayvalidation"] = self.component["coolingdelayvalidation"]
    pDBComponent["stirspeedvalidation"] = self.component["stirspeedvalidation"]
    pDBComponent["stopattemperaturevalidation"] = self.component["stopattemperaturevalidation"]
    pDBComponent["validationerror"] = self.component["validationerror"]

    # Save the component
    self.database.UpdateComponent(self.username, self.component["id"], pDBComponent["componenttype"], self.component["note"], json.dumps(pDBComponent))
      
  def addComponentDetails(self):
    """Adds details to the component after retrieving it from the database and prior to sending it to the client"""
    # Set the default stir speed
    if self.component["stirspeed"] == 0:
      self.component["stirspeed"] = DEFAULT_STIRSPEED

  def updateComponentDetails(self, pTargetComponent):
    """Strips a component down to only the details we want to save in the database"""
    # Call the base handler
    UnitOperation.updateComponentDetails(self, pTargetComponent)

    # Update the fields we want to save
    pTargetComponent["reactor"] = self.component["reactor"]
    pTargetComponent["position"] = self.component["position"]
    pTargetComponent["duration"] = self.component["duration"]
    pTargetComponent["reactiontemperature"] = self.component["reactiontemperature"]
    pTargetComponent["finaltemperature"] = self.component["finaltemperature"]
    pTargetComponent["coolingdelay"] = self.component["coolingdelay"]
    pTargetComponent["stirspeed"] = self.component["stirspeed"]
    pTargetComponent["stopattemperature"] = self.component["stopattemperature"]

