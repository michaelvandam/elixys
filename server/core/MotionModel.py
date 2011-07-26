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
  def __init__(self, name, reactor, hardwareComm):
    """Reactor motion model constructor"""
    ComponentModel.__init__(self, name, hardwareComm)
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

  def getSetPosition(self):
    """Return the set named reactor position"""
    return self.setPosition
    
  def getCurrentPosition(self):
    """Return the current named reactor position"""
    return self.currentPosition
    
  def getSetPositionRaw(self):
    """Return the set raw reactor position"""
    return self.setPositionRaw

  def getCurrentPositionRaw(self):
    """Return the current raw reactor position"""
    return self.currentPositionRaw
    
  def getSetReactorUp(self):
    """Returns True if the reactor is set to up, False otherwise"""
    return self.setReactorUp
    
  def getSetReactorDown(self):
    """Returns True if the reactor is set to down, False otherwise"""
    return self.setReactorDown

  def getCurrentReactorUp(self):
    """Returns True if the reactor is currently up, False otherwise"""
    return self.currentReactorUp
    
  def getCurrentReactorDown(self):
    """Returns True if the reactor is currently down, False otherwise"""
    return self.currentReactorDown

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
