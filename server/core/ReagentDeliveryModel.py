"""Reagent Delivery Model

Reagent Delivery Model Class
"""

# Imports
import sys
sys.path.append("/opt/elixys/hardware/")
from HardwareComm import HardwareComm, ROBOT_POSITION_LIMIT
from ComponentModel import ComponentModel

# Reagent delivery model
class ReagentDeliveryModel(ComponentModel):
  def __init__(self, name, hardwareComm, modelLock):
    """Reagent delivery model constructor"""
    ComponentModel.__init__(self, name, hardwareComm, modelLock)
    self.setPositionReactor = 0
    self.setPositionReagent = 0
    self.setPositionDelivery = 0
    self.setPositionElute = 0
    self.currentPositionReactor = 0
    self.currentPositionReagent = 0
    self.currentPositionDelivery = 0
    self.currentPositionElute = 0
    self.setPositionRawX = 0
    self.setPositionRawY = 0
    self.currentPositionRawX = 0
    self.currentPositionRawY = 0
    self.setGripperUp = False
    self.setGripperDown = False
    self.setGripperOpen = False
    self.setGripperClose = False
    self.setGasTransferUp = False
    self.setGasTransferDown = False
    self.currentGripperUp = False
    self.currentGripperDown = False
    self.currentGripperOpen = False
    self.currentGripperClose = False
    self.currentGasTransferUp = False
    self.currentGasTransferDown = False
    self.robotXStatus = 0
    self.robotXError = 0
    self.robotXControlWord = 0
    self.robotXCheckWord = 0
    self.robotYStatus = 0
    self.robotYError = 0
    self.robotYControlWord = 0
    self.robotYCheckWord = 0

  def getAllowedReagentPositions(self):
    """Return a list of allowed reagent positions"""
    return [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

  def getAllowedDeliveryPositions(self):
    """Return a list of allowed delivery positions"""
    return [1, 2]

  def getSetPosition(self, bLockModel = True):
    """Return the set reagent robot position in the format (nReactor, nReagentPosition, nDeliveryPosition)"""
    if bLockModel:
      return self.protectedReturn4(self.getSetPosition)
    else:
      return self.setPositionReactor, self.setPositionReagent, self.setPositionDelivery, self.setPositionElute

  def getSetPositionRaw(self, bLockModel = True):
    """Return the set raw reactor position in the format (X, Y)"""
    if bLockModel:
      return self.protectedReturn2(self.getSetPositionRaw)
    else:
      return self.setPositionRawX, self.setPositionRawY

  def getSetPositionName(self, bLockModel = True):
    """Return the set reactor position name as a pair of strings"""
    if bLockModel:
      return self.protectedReturn2(self.getSetPositionName)
    else:
      return self.getPositionName(self.setPositionReactor, self.setPositionReagent, self.setPositionDelivery, self.setPositionElute, 
        self.setPositionRawX, self.setPositionRawY)

  def getCurrentPosition(self, bLockModel = True):
    """Return the current reagent robot position in the format (nReactor, nReagentPosition, nDeliveryPosition)"""
    if bLockModel:
      return self.protectedReturn4(self.getCurrentPosition)
    else:
      return self.currentPositionReactor, self.currentPositionReagent, self.currentPositionDelivery, self.currentPositionElute
    
  def getCurrentPositionRaw(self, bLockModel = True):
    """Return the current raw reactor position in the format (X, Y)"""
    if bLockModel:
      return self.protectedReturn2(self.getCurrentPositionRaw)
    else:
      return self.currentPositionRawX, self.currentPositionRawY

  def getCurrentPositionName(self, bLockModel = True):
    """Return the current reactor position name as a pair of strings"""
    if bLockModel:
      return self.protectedReturn2(self.getCurrentPositionName)
    else:
      return self.getPositionName(self.currentPositionReactor, self.currentPositionReagent, self.currentPositionDelivery, self.currentPositionElute,
        self.currentPositionRawX, self.currentPositionRawY)

  def getSetGripperUp(self, bLockModel = True):
    """Returns True if the gripper is set to up, False otherwise"""
    if bLockModel:
      return self.protectedReturn1(self.getSetGripperUp)
    else:
      return self.setGripperUp

  def getSetGripperDown(self, bLockModel = True):
    """Returns True if the gripper is set to down, False otherwise"""
    if bLockModel:
      return self.protectedReturn1(self.getSetGripperDown)
    else:
      return self.setGripperDown

  def getSetGripperOpen(self, bLockModel = True):
    """Returns True if the gripper is set to open, False otherwise"""
    if bLockModel:
      return self.protectedReturn1(self.getSetGripperOpen)
    else:
      return self.setGripperOpen

  def getSetGripperClose(self, bLockModel = True):
    """Returns True if the gripper is set to close, False otherwise"""
    if bLockModel:
      return self.protectedReturn1(self.getSetGripperClose)
    else:
      return self.setGripperClose

  def getSetGasTransferUp(self, bLockModel = True):
    """Returns True if the gas transfer is set to up, False otherwise"""
    if bLockModel:
      return self.protectedReturn1(self.getSetGasTransferUp)
    else:
      return self.setGasTransferUp

  def getSetGasTransferDown(self, bLockModel = True):
    """Returns True if the gas transfer is set to down, False otherwise"""
    if bLockModel:
      return self.protectedReturn1(self.getSetGasTransferDown)
    else:
      return self.setGasTransferDown

  def getCurrentGripperUp(self, bLockModel = True):
    """Returns True if the gripper is currently up, False otherwise"""
    if bLockModel:
      return self.protectedReturn1(self.getCurrentGripperUp)
    else:
      return self.currentGripperUp

  def getCurrentGripperDown(self, bLockModel = True):
    """Returns True if the gripper is currently down, False otherwise"""
    if bLockModel:
      return self.protectedReturn1(self.getCurrentGripperDown)
    else:
      return self.currentGripperDown

  def getCurrentGripperOpen(self, bLockModel = True):
    """Returns True if the gripper is currently open, False otherwise"""
    if bLockModel:
      return self.protectedReturn1(self.getCurrentGripperOpen)
    else:
      return self.currentGripperOpen

  def getCurrentGripperClose(self, bLockModel = True):
    """Returns True if the gripper is currently closed, False otherwise"""
    if bLockModel:
      return self.protectedReturn1(self.getCurrentGripperClose)
    else:
      return self.currentGripperClose
      
  def getCurrentGasTransferUp(self, bLockModel = True):
    """Returns True if the gas transfer is currently up, False otherwise"""
    if bLockModel:
      return self.protectedReturn1(self.getCurrentGasTransferUp)
    else:
      return self.currentGasTransferUp

  def getCurrentGasTransferDown(self, bLockModel = True):
    """Returns True if the gas transfer is currently down, False otherwise"""
    if bLockModel:
      return self.protectedReturn1(self.getCurrentGasTransferDown)
    else:
      return self.currentGasTransferDown
      
  def getRobotStatus(self, bLockModel = True):
    """Returns the robot axis status code"""
    if bLockModel:
      return self.protectedReturn2(self.getRobotStatus)
    else:
      return self.robotXStatus, self.robotYStatus

  def getRobotError(self, bLockModel = True):
    """Returns the robot axis status code"""
    if bLockModel:
      return self.protectedReturn2(self.getRobotError)
    else:
      return self.robotXError, self.robotYError
      
  def getRobotXControlWords(self, bLockModel = True):
    """Returns the robot X axis control words"""
    if bLockModel:
      return self.protectedReturn2(self.getRobotXControlWords)
    else:
      return self.robotXControlWord, self.robotXCheckWord

  def getRobotYControlWords(self, bLockModel = True):
    """Returns the robot Y axis control words"""
    if bLockModel:
      return self.protectedReturn2(self.getRobotYControlWords)
    else:
      return self.robotYControlWord, self.robotYCheckWord

  def moveToReagentPosition(self, nReactor, nReagentPosition):
    """Moves the reagent robot to the given reagent position"""
    self.hardwareComm.MoveRobotToReagent(nReactor, nReagentPosition)
    
  def moveToDeliveryPosition(self, nReactor, nDeliveryPosition):
    """Moves the reagent robot to the given delivery position"""
    self.hardwareComm.MoveRobotToDelivery(nReactor, nDeliveryPosition)

  def moveToElutePosition(self, nReactor):
    """Moves the reagent robot to the elute position"""
    self.hardwareComm.MoveRobotToElute(nReactor)

  def moveToHome(self):
    """Moves the reagent robot to the home position"""
    self.hardwareComm.HomeReagentRobots()

  def moveToHomeFast(self):
    """Moves the reagent robot to the home position"""
    self.hardwareComm.MoveRobotToHome()

  def setDisableRobots(self):
    """Disables the reagent robots"""
    self.hardwareComm.DisableReagentRobots()

  def setEnableRobots(self):
    """Enables the reagent robots"""
    self.hardwareComm.EnableReagentRobots()

  def setMoveGripperUp(self):
    """Raise the gripper"""
    self.hardwareComm.GripperUp()
    
  def setMoveGripperDown(self):
    """Lower the gripper"""
    self.hardwareComm.GripperDown()

  def setMoveGripperOpen(self):
    """Open the gripper"""
    self.hardwareComm.GripperOpen()

  def setMoveGripperClose(self):
    """Close the gripper"""
    self.hardwareComm.GripperClose()

  def setMoveGasTransferUp(self):
    """Raise the gas transfer actuator"""
    self.hardwareComm.GasTransferUp()

  def setMoveGasTransferDown(self):
    """Lower the gas transfer actuator"""
    self.hardwareComm.GasTransferDown()
    
  def updateState(self, nSetPositionReactor, nSetPositionReagent, nSetPositionDelivery, nSetPositionElute, nCurrentPositionReactor, nCurrentPositionReagent,
                  nCurrentPositionDelivery, nCurrentPositionElute, nSetPositionRawX, nSetPositionRawY, nCurrentPositionRawX, nCurrentPositionRawY, bSetGripperUp,
                  bSetGripperDown, bSetGripperOpen, bSetGripperClose, bSetGasTransferUp, bSetGasTransferDown, bCurrentGripperUp, 
                  bCurrentGripperDown, bCurrentGripperOpen, bCurrentGripperClose, bCurrentGasTransferUp, bCurrentGasTransferDown, 
                  sRobotXStatus, nRobotXError, nRobotXControlWord, nRobotXCheckWord, sRobotYStatus, nRobotYError, nRobotYControlWord, nRobotYCheckWord):
    """Updates the internal state"""
    self.setPositionReactor = nSetPositionReactor
    self.setPositionReagent = nSetPositionReagent
    self.setPositionDelivery = nSetPositionDelivery
    self.setPositionElute = nSetPositionElute
    self.currentPositionReactor = nCurrentPositionReactor
    self.currentPositionReagent = nCurrentPositionReagent
    self.currentPositionDelivery = nCurrentPositionDelivery
    self.currentPositionElute = nCurrentPositionElute
    self.setPositionRawX = nSetPositionRawX
    self.setPositionRawY = nSetPositionRawY
    self.currentPositionRawX = nCurrentPositionRawX
    self.currentPositionRawY = nCurrentPositionRawY
    self.setGripperUp = bSetGripperUp
    self.setGripperDown = bSetGripperDown
    self.setGripperOpen = bSetGripperOpen
    self.setGripperClose = bSetGripperClose
    self.setGasTransferUp = bSetGasTransferUp
    self.setGasTransferDown = bSetGasTransferDown
    self.currentGripperUp = bCurrentGripperUp
    self.currentGripperDown = bCurrentGripperDown
    self.currentGripperOpen = bCurrentGripperOpen
    self.currentGripperClose = bCurrentGripperClose
    self.currentGasTransferUp = bCurrentGasTransferUp
    self.currentGasTransferDown = bCurrentGasTransferDown
    self.robotXStatus = sRobotXStatus
    self.robotXError = nRobotXError
    self.robotXControlWord = nRobotXControlWord
    self.robotXCheckWord = nRobotXCheckWord
    self.robotYStatus = sRobotYStatus
    self.robotYError = nRobotYError
    self.robotYControlWord = nRobotYControlWord
    self.robotYCheckWord = nRobotYCheckWord

  def getPositionName(self, nReactor, nReagent, nDelivery, nElute, nRawX, nRawY):
    if (nReagent != 0) or (nDelivery != 0) or (nElute != 0):
      sName1 = "Reactor " + str(nReactor)
      if nReagent != 0:
        sName2 = "Reagent " + str(nReagent)
      elif nDelivery != 0:
        sName2 = "Delivery " + str(nDelivery)
      else:
        sName2 = "Elute"
    else:	
      if (nRawX > -ROBOT_POSITION_LIMIT) and (nRawX < ROBOT_POSITION_LIMIT) and \
         (nRawY > -ROBOT_POSITION_LIMIT) and (nRawY < ROBOT_POSITION_LIMIT):
        sName1 = "Home"
      else:
        sName1 = "Unknown"
      sName2 = ""
    return sName1, sName2

