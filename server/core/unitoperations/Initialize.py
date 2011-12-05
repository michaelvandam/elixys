# Initialize unit operation

# Imports
from UnitOperation import *

class Initialize(UnitOperation):
  def __init__(self,systemModel,params,username = "", database = None):
    UnitOperation.__init__(self,systemModel,username,database)
    self.ReactorTuple=('Reactor1','Reactor2','Reactor3')
    self.reagentLoadPositionTuple=(1,2)
    
  def run(self):
    try:
      #Close all valves (set state)
      self.setStatus("Initializing valves")
      self.ReactorID = ""
      self.setGasTransferValve(OFF)
      self.setVacuumSystem(OFF)
      for self.ReactorID in self.ReactorTuple:
        self.systemModel[self.ReactorID]['Thermocouple'].setHeaterOff()
        self.systemModel[self.ReactorID]['Motion'].moveReactorDown()
        self.setStopcockPosition(TRANSFERDEFAULT,self.ReactorID)
      self.setStopcockPosition(F18DEFAULT,"Reactor1")

      #Set pressures
      self.setStatus("Initializing pressures")
      self.setPressureRegulator(1,5)
      self.setPressureRegulator(2,60)

      #Raise and open gripper    
      self.setStatus("Initializing robots")
      self.systemModel['ReagentDelivery'].setMoveGripperUp()
      self.waitForCondition(self.systemModel['ReagentDelivery'].getCurrentGripperUp,True,EQUAL,2)
      self.systemModel['ReagentDelivery'].setMoveGripperOpen()
      self.waitForCondition(self.systemModel['ReagentDelivery'].getCurrentGripperOpen,True,EQUAL,2) 
      self.systemModel['ReagentDelivery'].setMoveGasTransferUp()
      self.waitForCondition(self.systemModel['ReagentDelivery'].getCurrentGasTransferUp,True,EQUAL,2)

      #Home the robot once but don't check if it happens
      self.systemModel['ReagentDelivery'].moveToHome()
      for self.ReactorID in self.ReactorTuple:
        self.systemModel[self.ReactorID]['Motion'].moveToHome()
      time.sleep(2)

      #Home the robot again and check for the proper state
      self.systemModel['ReagentDelivery'].moveToHome()
      for self.ReactorID in self.ReactorTuple:
        self.systemModel[self.ReactorID]['Motion'].moveToHome()
      time.sleep(2)
      self.waitForCondition(self.areRobotsHomed,True,EQUAL,25)
      for self.ReactorID in self.ReactorTuple:
        self.setReactorPosition(INSTALL)
      self.setStatus("Complete")
    except Exception as e:
      self.abortOperation(e)
  
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
    self.component["name"] = "Initialize"
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
    pDBComponent["name"] = self.component["name"]
    pDBComponent["validationerror"] = self.component["validationerror"]

    # Save the component
    self.database.UpdateComponent(self.username, self.component["id"], pDBComponent["componenttype"], pDBComponent["name"], json.dumps(pDBComponent))

  def updateComponentDetails(self, pTargetComponent):
    """Strips a component down to only the details we want to save in the database"""
    # Call the base handler
    UnitOperation.updateComponentDetails(self, pTargetComponent)

    # Update the fields we want to save
    pTargetComponent["name"] = self.component["name"]

