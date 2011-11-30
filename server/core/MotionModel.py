"""Motion Model

Reactor Motion Model Class
"""

# Imports
import sys
sys.path.append("../hardware/")
from HardwareComm import HardwareComm
from ComponentModel import ComponentModel

# Reactor motion model
class MotionModel(ComponentModel):
  def __init__(self, name, reactor, hardwareComm, modelLock):
    """Reactor motion model constructor"""
    ComponentModel.__init__(self, name, hardwareComm, modelLock)
    self.reactor = reactor
    self.setPosition = ""
    self.currentPosition = ""
    self.setPositionRaw = 0
    self.currentPositionRaw = 0
    self.setReactorUp = False
    self.setReactorDown = False
    self.currentReactorUp = False
    self.currentReactorDown = False
    self.robotStatus = 0
    self.robotControlWord = 0
    self.robotCheckWord = 0

  def getAllowedPositions(self):
    """Return a list of allowed reactor positions"""
    return ["Install", "Transfer", "React1", "Add", "React2", "Evaporate"]

  def getSetPosition(self, bLockModel = True):
    """Return the set named reactor position"""
    if bLockModel:
      return self.protectedReturn1(self.getSetPosition)
    else:
      return self.setPosition
    
  def getCurrentPosition(self, bLockModel = True):
    """Return the current named reactor position"""
    if bLockModel:
      return self.protectedReturn1(self.getCurrentPosition)
    else:
      return self.currentPosition
    
  def getSetPositionRaw(self, bLockModel = True):
    """Return the set raw reactor position"""
    if bLockModel:
      return self.protectedReturn1(self.getSetPositionRaw)
    else:
      return self.setPositionRaw

  def getCurrentPositionRaw(self, bLockModel = True):
    """Return the current raw reactor position"""
    if bLockModel:
      return self.protectedReturn1(self.getCurrentPositionRaw)
    else:
      return self.currentPositionRaw
    
  def getSetReactorUp(self, bLockModel = True):
    """Returns True if the reactor is set to up, False otherwise"""
    if bLockModel:
      return self.protectedReturn1(self.getSetReactorUp)
    else:
      return self.setReactorUp
    
  def getSetReactorDown(self, bLockModel = True):
    """Returns True if the reactor is set to down, False otherwise"""
    if bLockModel:
      return self.protectedReturn1(self.getSetReactorDown)
    else:
      return self.setReactorDown

  def getCurrentReactorUp(self, bLockModel = True):
    """Returns True if the reactor is currently up, False otherwise"""
    if bLockModel:
      return self.protectedReturn1(self.getCurrentReactorUp)
    else:
      return self.currentReactorUp
    
  def getCurrentReactorDown(self, bLockModel = True):
    """Returns True if the reactor is currently down, False otherwise"""
    if bLockModel:
      return self.protectedReturn1(self.getCurrentReactorDown)
    else:
      return self.currentReactorDown
  
  def getCurrentRobotStatus(self, bLockModel = True):
    """Returns the robot status"""
    if bLockModel:
      return self.protectedReturn1(self.getCurrentRobotStatus)
    else:
      return self.robotStatus

  def getCurrentRobotControlWords(self, bLockModel = True):
    """Returns the robot control word"""
    if bLockModel:
      return self.protectedReturn2(self.getCurrentRobotControlWords)
    else:
      return self.robotControlWord, self.robotCheckWord

  def setDisableReactorRobot(self):
    """Disables the reactor robot"""
    self.hardwareComm.DisableReactorRobot(self.reactor)

  def setEnableReactorRobot(self):
    """Enables the reactor robot"""
    self.hardwareComm.EnableReactorRobot(self.reactor)

  def moveReactorDown(self):
    """Moves the reactor down"""
    self.hardwareComm.ReactorDown(self.reactor)
    
  def moveReactorUp(self):
    """Moves the reactor up"""
    self.hardwareComm.ReactorUp(self.reactor)
    
  def moveToPosition(self, sPosition):
    """Moves the reactor to the given position"""
    self.hardwareComm.MoveReactor(self.reactor, sPosition)
  
  def moveHomeRobots(self):
    self.hardwareComm.HomeRobots()
    
  def updateState(self, sSetPosition, sCurrentPosition, nSetPositionRaw, nCurrentPositionRaw, bSetReactorUp, bSetReactorDown, bCurrentReactorUp, bCurrentReactorDown, 
      nRobotStatus, nRobotControlWord, nRobotCheckWord):
    """Updates the internal state"""
    self.setPosition = sSetPosition
    self.currentPosition = sCurrentPosition
    self.setPositionRaw = nSetPositionRaw
    self.currentPositionRaw = nCurrentPositionRaw
    self.setReactorUp = bSetReactorUp
    self.setReactorDown = bSetReactorDown
    self.currentReactorUp = bCurrentReactorUp
    self.currentReactorDown = bCurrentReactorDown
    self.robotStatus = nRobotStatus
    self.robotControlWord = nRobotControlWord
    self.robotCheckWord = nRobotCheckWord

