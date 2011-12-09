# TrapF18 unit operation

# Imports
from UnitOperation import *

class TrapF18(UnitOperation):
  def __init__(self,systemModel,params,username = "", database = None):
    UnitOperation.__init__(self,systemModel,username,database)
    expectedParams = {CYCLOTRONFLAG:INT,TRAPTIME:INT,TRAPPRESSURE:FLOAT}
    paramError = self.validateParams(params,expectedParams)
    if self.paramsValid:
      self.setParams(params)
      self.ReactorID='Reactor1'
    else:
      raise UnitOpError(paramError)

    #Should have parameters listed below:
    #self.cyclotronFlag
    #self.trapTime
    #self.trapPressure

  def run(self):
    try:
      self.setStatus("Adjusting pressure")
      self.setPressureRegulator(1,0) #Vent pressure to avoid delivery issues
      self.setStatus("Moving reactor")
      self.setReactorPosition(ADDREAGENT)
      self.setStatus("Trapping")
      self.setStopcockPosition(F18TRAP)
      if (self.cyclotronFlag):
        self.setStatus("Trapping, waiting for delivery")
        self.waitForUserInput("The system is ready for you to deliver F18 from your external source.\n\nClick OK once delivery is complete.")
      else:
        self.systemModel['Valves'].setF18LoadValveOpen(ON)  
        self.waitForCondition(self.systemModel['Valves'].getF18LoadValveOpen,ON,EQUAL,5)
        self.timerShowInStatus = False
        self.setPressureRegulator(1,self.trapPressure,5) #Set pressure after valve is opened
        self.startTimer(self.trapTime)
        self.waitForTimer()
        self.systemModel['Valves'].setF18LoadValveOpen(OFF)
        self.waitForCondition(self.systemModel['Valves'].getF18LoadValveOpen,OFF,EQUAL,5)
      self.setStopcockPosition(F18DEFAULT)
      self.setStatus("Complete")
    except Exception as e:
      self.abortOperation(e)

  def initializeComponent(self, pComponent):
    """Initializes the component validation fields"""
    self.component = pComponent
    if not self.component.has_key("cyclotronflagvalidation"):
      self.component.update({"cyclotronflagvalidation":""})
    if not self.component.has_key("traptimevalidation"):
      self.component.update({"traptimevalidation":""})
    if not self.component.has_key("trappressurevalidation"):
      self.component.update({"trappressurevalidation":""})
    self.addComponentDetails()

  def validateFull(self, pAvailableReagents):
    """Performs a full validation on the component"""
    self.component["name"] = "Trap F18"
    self.component["cyclotronflagvalidation"] = "type=enum-number; values=0,1; required=true"
    self.component["traptimevalidation"] = "type=number; min=0; max=7200; required=true"
    self.component["trappressurevalidation"] = "type=number; min=0; max=25"
    return self.validateQuick()

  def validateQuick(self):
    """Performs a quick validation on the component"""
    #Validate all fields
    bValidationError = False
    if not self.validateComponentField(self.component["cyclotronflag"], self.component["cyclotronflagvalidation"]) or \
       not self.validateComponentField(self.component["traptime"], self.component["traptimevalidation"]) or \
       not self.validateComponentField(self.component["trappressure"], self.component["trappressurevalidation"]):
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
    pDBComponent["cyclotronflagvalidation"] = self.component["cyclotronflagvalidation"]
    pDBComponent["traptimevalidation"] = self.component["traptimevalidation"]
    pDBComponent["trappressurevalidation"] = self.component["trappressurevalidation"]
    pDBComponent["validationerror"] = self.component["validationerror"]

    # Save the component
    self.database.UpdateComponent(self.username, self.component["id"], pDBComponent["componenttype"], pDBComponent["name"], json.dumps(pDBComponent))

  def updateComponentDetails(self, pTargetComponent):
    """Strips a component down to only the details we want to save in the database"""
    # Call the base handler
    UnitOperation.updateComponentDetails(self, pTargetComponent)

    # Update the fields we want to save
    pTargetComponent["name"] = self.component["name"]
    pTargetComponent["cyclotronflag"] = self.component["cyclotronflag"]
    pTargetComponent["traptime"] = self.component["traptime"]
    pTargetComponent["trappressure"] = self.component["trappressure"]

