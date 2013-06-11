# Initialize unit operation

# Imports
from UnitOperation import *
import logging
log = logging.getLogger("elixys.unitop")

# Component type
componentType = "INITIALIZE"

# Create a unit operation from a component object
def createFromComponent(nSequenceID, pComponent, username, database, systemModel):
  pInitialize = Initialize(systemModel, {}, username, nSequenceID, pComponent["id"], database)
  pInitialize.initializeComponent(pComponent)
  return pInitialize

# Updates a component object based on a unit operation
def updateToComponent(pUnitOperation, nSequenceID, pComponent, username, database, systemModel):
  pass

# Initialize class
class Initialize(UnitOperation):
  def __init__(self,systemModel,params,username = "",sequenceID = 0, componentID = 0, database = None):
    UnitOperation.__init__(self,systemModel,username,sequenceID,componentID,database)
    log.debug("Initialize initialize")
    self.ReactorTuple=('Reactor1','Reactor2','Reactor3')
    self.reagentLoadPositionTuple=(1,2)
    self.description = "Initializing the system hardware."
    
  def run(self):
    log.debug("Run initialize")
    try:
      #Close all valves (set state)
      self.setStatus("Initializing valves")
      self.ReactorID = ""
      self.setGasTransferValve(OFF)
      for self.ReactorID in self.ReactorTuple:
        self.systemModel[self.ReactorID]['Motion'].moveReactorDown()
        self.setStopcockPosition(TRANSFERDEFAULT,self.ReactorID)
        self.setStopcockPosition(F18DEFAULT,self.ReactorID)
      self.systemModel['Valves'].setF18LoadValveOpen(OFF)

      log.debug("After stopcocks")

      #Initialize cooling, vacuum, heaters and stir motors
      self.setCoolingSystem(OFF)
      self.setVacuumSystem(OFF)
      for self.ReactorID in self.ReactorTuple:
        self.systemModel[self.ReactorID]['Thermocouple'].setHeaterOff()
        self.systemModel[self.ReactorID]['Stir'].setSpeed(0)

      #Set pressures
      self.setStatus("Initializing pressures")
      self.setPressureRegulator(1,GAS_TRANSFER_PRESSURE)
      #log.error("Break0")
      self.setPressureRegulator(2,PNEUMATIC_PRESSURE)

      #Raise and open gripper
      self.setStatus("Initializing robots")
      self.doStep(self.initialize_Step1, "Failed to move gripper up")
      self.doStep(self.initialize_Step2, "Failed to open gripper")
      self.doStep(self.initialize_Step3, "Failed to move gas transfer up")
 
      # Wait for the reactors to reach the down position
      self.doStep(self.initialize_Step4, "Reactors failed to reach down positions")

      #Home the robots once but don't check if it happens
      self.systemModel['ReagentDelivery'].moveToHome()
      for self.ReactorID in self.ReactorTuple:
        self.systemModel[self.ReactorID]['Motion'].moveToHome()
      time.sleep(2)

      #Home the robots again and wait for them to arrive
      self.doStep(self.initialize_Step5, "Reactors failed to home")

      #Raise the robots to the install position
      for self.ReactorID in self.ReactorTuple:
        self.setReactorPosition(INSTALL)
      self.setStatus("Complete")
    except Exception as e:
      log.error("Trackback \n\r%s\n\r" % traceback.format_exc())
      self.abortOperation(str(e), False)
  
  def initialize_Step1(self):
    self.systemModel['ReagentDelivery'].setMoveGripperUp()
    self.waitForCondition(self.systemModel['ReagentDelivery'].getCurrentGripperUp,True,EQUAL,2)

  def initialize_Step2(self):
    self.systemModel['ReagentDelivery'].setMoveGripperOpen()
    self.waitForCondition(self.systemModel['ReagentDelivery'].getCurrentGripperOpen,True,EQUAL,2) 

  def initialize_Step3(self):
    self.systemModel['ReagentDelivery'].setMoveGasTransferUp()
    self.waitForCondition(self.systemModel['ReagentDelivery'].getCurrentGasTransferUp,True,EQUAL,2)

  def initialize_Step4(self):
    for self.ReactorID in self.ReactorTuple:
      self.waitForCondition(self.systemModel[self.ReactorID]['Motion'].getCurrentReactorDown,True,EQUAL,3)

  def initialize_Step5(self):
    self.systemModel['ReagentDelivery'].moveToHome()
    for self.ReactorID in self.ReactorTuple:
      self.systemModel[self.ReactorID]['Motion'].moveToHome()
    time.sleep(2)
    self.waitForCondition(self.areRobotsHomed,True,EQUAL,25)

  def areRobotsHomed(self):
    self.robotsHomed=True
    for self.ReactorID in self.ReactorTuple:
      if not(self.checkForCondition(self.systemModel[self.ReactorID]['Motion'].getCurrentRobotStatus,ENABLED,EQUAL)):
        self.robotsHomed=False
    if not(self.checkForCondition(self.systemModel['ReagentDelivery'].getRobotStatus,(ENABLED,ENABLED),EQUAL)):
      self.robotsHomed=False
    return self.robotsHomed
      
  def initializeComponent(self, pComponent):
    """Initializes the component validation fields"""
    self.component = pComponent
    self.addComponentDetails()

  def validateFull(self, pAvailableReagents):
    """Performs a full validation on the component"""
    self.component["note"] = ""
    return self.validateQuick()

  def validateQuick(self):
    """Performs a quick validation on the component"""
    self.component.update({"validationerror":False})
    return True

  def saveValidation(self):
    """Saves validation-specific fields back to the database"""
    # Pull the original component from the database
    pDBComponent = self.database.GetComponent(self.username, self.component["id"])

    # Copy the validation fields
    pDBComponent["validationerror"] = self.component["validationerror"]

    # Save the component
    self.database.UpdateComponent(self.username, self.component["id"], pDBComponent["componenttype"], self.component["note"], json.dumps(pDBComponent))

  def updateComponentDetails(self, pTargetComponent):
    """Strips a component down to only the details we want to save in the database"""
    # Call the base handler
    UnitOperation.updateComponentDetails(self, pTargetComponent)

