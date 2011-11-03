# Add unit operation

# Imports
from UnitOperation import *

class Add(UnitOperation):
  def __init__(self,systemModel,params,username = "", database = None):
    UnitOperation.__init__(self,systemModel,username,database)
    expectedParams = {REACTORID:STR,REAGENTREACTORID:STR,REAGENTPOSITION:INT,REAGENTLOADPOSITION:INT,PRESSURE:FLOAT,DURATION:INT}
    paramError = self.validateParams(params,expectedParams)
    if self.paramsValid:
      self.setParams(params)
    else:
      raise UnitOpError(paramError)
	#Should have parameters listed below: 
    #self.ReactorID
    #self.ReagentReactorID
    #self.ReagentPosition
    #self.reagentLoadPosition
    #self.duration
    #self.pressure

  def run(self):
    try:
      self.setStatus("Adjusting pressure")
      self.setPressureRegulator(2,self.pressure)   #Set delivery pressure
      self.setStatus("Moving reactor")
      self.setReactorPosition(ADDREAGENT)          #Move reactor to position
      self.setStatus("Picking up reagent")
      self.setGripperPlace()                       #Move reagent to the addition position.
      self.setStatus("Delivering reagent")
      self.startTimer(self.duration)               #In seconds
      self.waitForTimer()                          #Wait for Dispense reagent
      self.setStatus("Returning reagent")
      self.setGripperRemove()                      #Return vial to its starting location
      self.setStatus("Complete")
    except Exception as e:
      self.abortOperation(e)
  
  """def setParams(self,currentParams):
    expectedParams = ['ReactorID','ReagentPosition','reagentLoadPosition']
    self.paramsValid = True
    for parameter in expectedParams:
      if not(parameter in currentParams):
        self.paramsValid = False
        #Log Error
      self.paramsValidated = True"""
    
  def setGripperPlace(self):
    #Make sure we are open and up
    if not self.checkForCondition(self.systemModel['ReagentDelivery'].getCurrentGripperOpen,True,EQUAL):
      self.abortOperation("ERROR: setGripperPlace called while gripper was not open. Operation aborted.")
    if not self.checkForCondition(self.systemModel['ReagentDelivery'].getCurrentGripperUp,True,EQUAL):
      self.abortOperation("ERROR: setGripperPlace called while gripper was not up. Operation aborted.") 

    #Make sure the reagent robots are enabled
    if not(self.checkForCondition(self.systemModel['ReagentDelivery'].getRobotStatus,(ENABLED,ENABLED),EQUAL)):
      self.systemModel['ReagentDelivery'].setEnableRobots()
      self.waitForCondition(self.systemModel['ReagentDelivery'].getRobotStatus,(ENABLED,ENABLED),EQUAL,3)

    #Move to ReagentPosition, then down and close
    self.systemModel['ReagentDelivery'].moveToReagentPosition(int(self.ReagentReactorID[-1]),self.reagentPosition) #Move Reagent Robot to position
    self.waitForCondition(self.systemModel['ReagentDelivery'].getCurrentPosition,(int(self.ReagentReactorID[-1]), self.reagentPosition, 0),EQUAL,5)
    self.systemModel['ReagentDelivery'].setMoveGripperDown() #Move Gripper down
    self.waitForCondition(self.systemModel['ReagentDelivery'].getCurrentGripperDown,True,EQUAL,2)
    self.systemModel['ReagentDelivery'].setMoveGripperClose() #Close Gripper
    self.waitForCondition(self.systemModel['ReagentDelivery'].getCurrentGripperClose,True,EQUAL,2)
    
    #Move up and over to the Delivery Position
    self.systemModel['ReagentDelivery'].setMoveGripperUp()
    self.waitForCondition(self.systemModel['ReagentDelivery'].getCurrentGripperUp,True,EQUAL,3)
    self.systemModel['ReagentDelivery'].moveToDeliveryPosition(int(self.ReactorID[-1]),self.reagentLoadPosition)
    self.waitForCondition(self.systemModel['ReagentDelivery'].getCurrentPosition,(int(self.ReactorID[-1]), 0, self.reagentLoadPosition),EQUAL,5)

    #Turn the transfer gas on and move the vial down    
    self.setReagentTransferValves(ON)
    time.sleep(0.5)
    self.systemModel['ReagentDelivery'].setMoveGripperDown()
    self.waitForCondition(self.systemModel['ReagentDelivery'].getCurrentGripperDown,True,EQUAL,3)
    
  def setGripperRemove(self):
    #Make sure we are closed, down and in position
    if not self.checkForCondition(self.systemModel['ReagentDelivery'].getCurrentGripperClose,True,EQUAL):
      self.abortOperation("ERROR: setGripperRemove called while gripper was not closed. Operation aborted.")
    if not self.checkForCondition(self.systemModel['ReagentDelivery'].getCurrentGripperDown,True,EQUAL):
      self.abortOperation("ERROR: setGripperRemove called while gripper was not up. Operation aborted.")
    if not self.checkForCondition(self.systemModel['ReagentDelivery'].getCurrentPosition,(int(self.ReactorID[-1]), 0, self.reagentLoadPosition),EQUAL):
      self.abortOperation("ERROR: setGripperRemove called while gripper was not in the target position. Operation aborted.")

    #Turn off the transfer gas and move up
    self.setReagentTransferValves(OFF)
    time.sleep(0.25)
    self.systemModel['ReagentDelivery'].setMoveGripperUp()
    self.waitForCondition(self.systemModel['ReagentDelivery'].getCurrentGripperUp,True,EQUAL,3)

    #Move to ReagentPosition, then down and open
    self.systemModel['ReagentDelivery'].moveToReagentPosition(int(self.ReagentReactorID[-1]),self.reagentPosition)
    self.waitForCondition(self.systemModel['ReagentDelivery'].getCurrentPosition,(int(self.ReagentReactorID[-1]), self.reagentPosition, 0),EQUAL,5)
    self.systemModel['ReagentDelivery'].setMoveGripperDown()
    self.waitForCondition(self.systemModel['ReagentDelivery'].getCurrentGripperDown,True,EQUAL,3)
    self.systemModel['ReagentDelivery'].setMoveGripperOpen()
    self.waitForCondition(self.systemModel['ReagentDelivery'].getCurrentGripperOpen,True,EQUAL,2)
    
    #Move up and to home
    self.systemModel['ReagentDelivery'].setMoveGripperUp()
    self.waitForCondition(self.systemModel['ReagentDelivery'].getCurrentGripperUp,True,EQUAL,3)
    self.systemModel['ReagentDelivery'].moveToHome()
    self.waitForCondition(self.systemModel['ReagentDelivery'].getCurrentPosition,(0,0,0),EQUAL,5)

  def initializeComponent(self, pComponent):
    """Initializes the component validation fields"""
    self.component = pComponent
    if not self.component.has_key("reactorvalidation"):
      self.component.update({"reactorvalidation":""})
    if not self.component.has_key("reagentreactorvalidation"):
      self.component.update({"reagentreactorvalidation":""})
    if not self.component.has_key("reagentvalidation"):
      self.component.update({"reagentvalidation":""})
    if not self.component.has_key("deliverypositionvalidation"):
      self.component.update({"deliverypositionvalidation":""})
    if not self.component.has_key("deliverytimevalidation"):
      self.component.update({"deliverytimevalidation":""})
    if not self.component.has_key("deliverypressurevalidation"):
      self.component.update({"deliverypressurevalidation":""})
    self.addComponentDetails()

  def validateFull(self, pAvailableReagents):
    """Performs a full validation on the component"""
    self.component["name"] = "Add"
    self.component["reactorvalidation"] = "type=enum-number; values=1,2,3; required=true"
    self.component["reagentreactorvalidation"] = "type=enum-number; values=1,2,3; required=true"
    self.component["reagentvalidation"] = "type=enum-reagent; values=" + self.listReagents(pAvailableReagents) + "; required=true"
    self.component["deliverypositionvalidation"] = "type=enum-number; values=1,2; required=true"
    self.component["deliverytimevalidation"] = "type=number; min=0; max=10"
    self.component["deliverypressurevalidation"] = "type=number; min=0; max=15"

    #Look up the reagent we are adding and remove it from the list of available reagents
    if self.component["reagent"].has_key("reagentid"):
      pReagent = self.getReagentByID(self.component["reagent"]["reagentid"], pAvailableReagents, True)
      if pReagent != None:
        #Set the component name
        self.component["name"] = "Add " + pReagent["name"]

    #Do a quick validation
    return self.validateQuick()

  def validateQuick(self):
    """Performs a quick validation on the component"""
    #Validate all fields
    bValidationError = False
    if not self.validateComponentField(self.component["reactor"], self.component["reactorvalidation"]) or \
       not self.validateComponentField(self.component["reagentreactor"], self.component["reagentreactorvalidation"]) or \
       not self.validateComponentField(self.component["reagent"], self.component["reagentvalidation"]) or \
       not self.validateComponentField(self.component["deliveryposition"], self.component["deliverypositionvalidation"]) or \
       not self.validateComponentField(self.component["deliverytime"], self.component["deliverytimevalidation"]) or \
       not self.validateComponentField(self.component["deliverypressure"], self.component["deliverypressurevalidation"]):
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
    pDBComponent["reagentreactorvalidation"] = self.component["reagentreactorvalidation"]
    pDBComponent["reagentvalidation"] = self.component["reagentvalidation"]
    pDBComponent["deliverypositionvalidation"] = self.component["deliverypositionvalidation"]
    pDBComponent["deliverytimevalidation"] = self.component["deliverytimevalidation"]
    pDBComponent["deliverypressurevalidation"] = self.component["deliverypressurevalidation"]
    pDBComponent["deliverytime"] = self.component["deliverytime"]
    pDBComponent["deliverypressure"] = self.component["deliverypressure"]
    pDBComponent["validationerror"] = self.component["validationerror"]

    # Save the component
    self.database.UpdateComponent(self.username, self.component["id"], pDBComponent["componenttype"], pDBComponent["name"], json.dumps(pDBComponent))

  def addComponentDetails(self):
    """Adds details to the component after retrieving it from the database and prior to sending it to the client"""
    # Skip if we've already updated the reagent
    try:
      int(self.component["reagent"])
    except TypeError:
      return

    # Look up the reagent we are adding
    pAddReagent = {}
    if self.component["reagent"] != 0:
      pAddReagent = self.database.GetReagent(self.username, self.component["reagent"])

    # Replace the reagent
    del self.component["reagent"]
    self.component["reagent"] = pAddReagent

    # Set the default delivery time and pressure
    if self.component["deliverytime"] == 0:
      self.component["deliverytime"] = DEFAULT_ADD_DELIVERYTIME
    if self.component["deliverypressure"] == 0:
      self.component["deliverypressure"]= DEFAULT_ADD_DELIVERYPRESSURE

  def updateComponentDetails(self, pTargetComponent):
    """Strips a component down to only the details we want to save in the database"""
    # Call the base handler
    UnitOperation.updateComponentDetails(pTargetComponent)

    # Update the fields we want to save
    pTargetComponent["reactor"] = self.component["reactor"]
    pTargetComponent["reagentreactor"] = self.component["reagentreactor"]
    pTargetComponent["deliveryposition"] = self.component["deliveryposition"]
    pTargetComponent["deliverytime"] = self.component["deliverytime"]
    pTargetComponent["deliverypressure"] = self.component["deliverypressure"]
    pTargetComponent["reagent"] = self.component["reagent"]
    if pTargetComponent["reagent"] != 0:
      pReagent = self.database.GetReagent(self.username, pTargetComponent["reagent"])
      pTargetComponent.update({"name":"Add " + pReagent["name"]})
    else:
      pTargetComponent.update({"name":"Add"})

  def copyComponentImpl(self, nSequenceID, pComponentCopy):
    """Performs unit-operation specific copying"""
    print "### Implement Add.copyComponent"
