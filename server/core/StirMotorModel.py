"""Stir Motor Model

Reactor Stir Motor Model Class
"""

# Imports
import sys
sys.path.append("/opt/elixys/hardware/")
from HardwareComm import HardwareComm
from ComponentModel import ComponentModel

# Reactor stir model
class StirMotorModel(ComponentModel):
  def __init__(self, name, reactor, hardwareComm, modelLock):
    """Reactor stir motor model construction"""
    ComponentModel.__init__(self, name, hardwareComm, modelLock)
    self.reactor = reactor
    self.stirSpeed = 0

  def getMinimumSpeed(self):
    """Returns the minimum stir motor speed"""
    return 0
    
  def getMaximumSpeed(self):
    """Returns the maximum stir motor speed"""
    return 800
    
  def getCurrentSpeed(self, bLockModel = True):
    """Returns the current stir motor speed"""
    if bLockModel:
      return self.protectedReturn1(self.getCurrentSpeed)
    else:
      return self.stirSpeed
  
  def setSpeed(self, nSpeed):
    """Sets the stir motor speed"""
    self.hardwareComm.SetMotorSpeed(self.reactor, nSpeed)
    
  def updateState(self, nStirMotorSpeed):
    """Update the internal state"""
    self.stirSpeed = nStirMotorSpeed
