# TrapF18 unit operation

# Imports
from UnitOperation import *

# Component type
componentType = "TRAPF18"

# Create a unit operation from a component object
def createFromComponent(nSequenceID, pComponent, username, database, systemModel):
  pParams = {}
  pParams["ReactorID"] =  "Reactor" + str(pComponent["reactor"])
  pParams["cyclotronFlag"] = pComponent["cyclotronflag"]
  pParams["trapTime"] = pComponent["traptime"]
  pParams["trapPressure"] = pComponent["trappressure"]
  pTrapF18 = TrapF18(systemModel, pParams, username, nSequenceID, pComponent["id"], database)
  pTrapF18.initializeComponent(pComponent)
  return pTrapF18

# Updates a component object based on a unit operation
def updateToComponent(pUnitOperation, nSequenceID, pComponent, username, database, systemModel):
  pComponent["traptime"] = int(pUnitOperation.trapTime)

# TrapF18 class
class TrapF18(UnitOperation):
  def __init__(self,systemModel,params,username = "",sequenceID = 0, componentID = 0, database = None):
    UnitOperation.__init__(self,systemModel,username,sequenceID,componentID,database)
    expectedParams = {REACTORID:STR,CYCLOTRONFLAG:INT,TRAPTIME:INT,TRAPPRESSURE:FLOAT}
    paramError = self.validateParams(params,expectedParams)
    if self.paramsValid:
      self.setParams(params)
    else:
      raise UnitOpError(paramError)
    if (self.cyclotronFlag):
      self.description = "Cyclotron will push the F18 solution to trap on the QMA cartridge attached to reactor " + \
        str(self.ReactorID[-1]) + "."
    else:
      self.description = "Trapping F18 on the QMA cartridge attached to reactor " + str(self.ReactorID[-1]) + \
        " for " + str(self.trapTime) + " seconds using " + str(self.trapPressure) + " psi nitrogen."

  def run(self):
    try:
      self.setStatus("Adjusting pressure")
      self.setPressureRegulator(1,0) #Vent pressure to avoid delivery issues
      self.setStatus("Moving reactor")
      self.setReactorPosition(ADDREAGENT)
      self.setStatus("Preparing to trap")
      self.setStopcockPosition(F18TRAP)
      if (self.cyclotronFlag):
        self.setStatus("Waiting for the user to deliver F18 from the external source")
        self.waitForUserInput()
      else:
        self.setStatus("Trapping")
        self.doStep(self.trapF18_Step1, "Failed to turn on F18 load valve")
        self.timerShowInStatus = False
        self.setPressureRegulator(1,self.trapPressure,5) #Set pressure after valve is opened
        self.startTimer(self.trapTime)
        self.trapTime = self.waitForTimer()
        self.doStep(self.trapF18_Step2, "Failed to turn off F18 load valve")
      self.setStatus("Completing")
      self.setStopcockPosition(F18DEFAULT)
      self.setStatus("Complete")
    except Exception as e:
      self.abortOperation(str(e), False)

  def trapF18_Step1(self):
    self.systemModel['Valves'].setF18LoadValveOpen(ON)
    self.waitForCondition(self.systemModel['Valves'].getF18LoadValveOpen,ON,EQUAL,5)

  def trapF18_Step2(self):
    self.systemModel['Valves'].setF18LoadValveOpen(OFF)
    self.waitForCondition(self.systemModel['Valves'].getF18LoadValveOpen,OFF,EQUAL,5)

  def initializeComponent(self, pComponent):
    """Initializes the component validation fields"""
    self.component = pComponent
    if not self.component.has_key("reactorvalidation"):
      self.component.update({"reactorvalidation":""})
    if not self.component.has_key("cyclotronflagvalidation"):
      self.component.update({"cyclotronflagvalidation":""})
    if not self.component.has_key("traptimevalidation"):
      self.component.update({"traptimevalidation":""})
    if not self.component.has_key("trappressurevalidation"):
      self.component.update({"trappressurevalidation":""})
    self.addComponentDetails()

  def validateFull(self, pAvailableReagents):
    """Performs a full validation on the component"""
    self.component["note"] = ""
    self.component["reactorvalidation"] = "type=enum-number; values=1,2,3; required=true"
    self.component["cyclotronflagvalidation"] = "type=enum-number; values=0,1; required=true"
    self.component["traptimevalidation"] = "type=number; min=0; max=7200; required=true"
    self.component["trappressurevalidation"] = "type=number; min=0; max=25"
    return self.validateQuick()

  def validateQuick(self):
    """Performs a quick validation on the component"""
    #Validate all fields
    bValidationError = False
    if not self.validateComponentField(self.component["reactor"], self.component["reactorvalidation"]) or \
       not self.validateComponentField(self.component["cyclotronflag"], self.component["cyclotronflagvalidation"]) or \
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
    pDBComponent["reactorvalidation"] = self.component["reactorvalidation"]
    pDBComponent["cyclotronflagvalidation"] = self.component["cyclotronflagvalidation"]
    pDBComponent["traptimevalidation"] = self.component["traptimevalidation"]
    pDBComponent["trappressurevalidation"] = self.component["trappressurevalidation"]
    pDBComponent["validationerror"] = self.component["validationerror"]

    # Save the component
    self.database.UpdateComponent(self.username, self.component["id"], pDBComponent["componenttype"], \
      self.component["note"], json.dumps(pDBComponent))

  def updateComponentDetails(self, pTargetComponent):
    """Strips a component down to only the details we want to save in the database"""
    # Call the base handler
    UnitOperation.updateComponentDetails(self, pTargetComponent)

    # Update the fields we want to save
    pTargetComponent["reactor"] = self.component["reactor"]
    pTargetComponent["cyclotronflag"] = self.component["cyclotronflag"]
    pTargetComponent["traptime"] = self.component["traptime"]
    pTargetComponent["trappressure"] = self.component["trappressure"]

