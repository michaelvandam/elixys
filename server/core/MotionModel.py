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

  def getAllowedPositions(self):
    """Return a list of allowed reactor positions"""
    return ["Install", "Transfer", "React1", "Add", "React2", "Evaporate"]

  def getSetPosition(self, bLockModel = True):
    """Return the set named reactor position"""
    return self.protectedReturn(self.setPosition, bLockModel)
    
  def getCurrentPosition(self, bLockModel = True):
    """Return the current named reactor position"""
    return self.protectedReturn(self.currentPosition, bLockModel)
    
  def getSetPositionRaw(self, bLockModel = True):
    """Return the set raw reactor position"""
    return self.protectedReturn(self.setPositionRaw, bLockModel)

  def getCurrentPositionRaw(self, bLockModel = True):
    """Return the current raw reactor position"""
    return self.protectedReturn(self.currentPositionRaw, bLockModel)
    
  def getSetReactorUp(self, bLockModel = True):
    """Returns True if the reactor is set to up, False otherwise"""
    return self.protectedReturn(self.setReactorUp, bLockModel)
    
  def getSetReactorDown(self, bLockModel = True):
    """Returns True if the reactor is set to down, False otherwise"""
    return self.protectedReturn(self.setReactorDown, bLockModel)

  def getCurrentReactorUp(self, bLockModel = True):
    """Returns True if the reactor is currently up, False otherwise"""
    return self.protectedReturn(self.currentReactorUp, bLockModel)
    
  def getCurrentReactorDown(self, bLockModel = True):
    """Returns True if the reactor is currently down, False otherwise"""
    return self.protectedReturn(self.currentReactorDown, bLockModel)

  def moveToPosition(self, sPosition):
    """Moves the reactor to the given position"""
    self.hardwareComm.MoveReactor(self.reactor, sPosition)
    
  def updateState(self, sSetPosition, sCurrentPosition, nSetPositionRaw, nCurrentPositionRaw, bSetReactorUp, bSetReactorDown, bCurrentReactorUp, bCurrentReactorDown):
    """Updates the internal state"""
    self.setPosition = sSetPosition
    self.currentPosition = sCurrentPosition
    self.setPositionRaw = nSetPositionRaw
    self.currentPositionRaw = nCurrentPositionRaw
    self.setReactorUp = bSetReactorUp
    self.setReactorDown = bSetReactorDown
    self.currentReactorUp = bCurrentReactorUp
    self.currentReactorDown = bCurrentReactorDown
