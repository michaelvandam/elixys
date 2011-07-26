"""Stir Motor Model

Reactor Stir Motor Model Class
"""

# Imports
import sys
sys.path.append("../hardware/")
from HardwareComm import HardwareComm
from ComponentModel import ComponentModel

# Reactor stir model
class StirMotorModel(ComponentModel):
  def __init__(self, name, reactor, hardwareComm):
    """Reactor stir motor model construction"""
    ComponentModel.__init__(self, name, hardwareComm)
    self.reactor = reactor
    self.stirSpeed = 0

  def getMinimumSpeed(self):
    """Returns the minimum stir motor speed"""
    return 0
    
  def getMaximumSpeed(self):
    """Returns the maximum stir motor speed"""
    return 800
    
  def getCurrentSpeed(self):
    """Returns the current stir motor speed"""
    return self.stirSpeed
  
  def setSpeed(self, nSpeed):
    """Sets the stir motor speed"""
    self.hardwareComm.SetMotorSpeed(self.reactor, nSpeed)
    
  def updateState(self, nStirMotorSpeed):
    """Update the internal state"""
    self.stirSpeed = nStirMotorSpeed
