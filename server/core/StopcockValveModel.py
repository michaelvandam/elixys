"""Stopcock Valve Model

Stopcock Valve Model Class
"""

# Imports
import sys
sys.path.append("../hardware/")
from HardwareComm import HardwareComm
from ComponentModel import ComponentModel
    
# Stopcock valve model
class StopcockValveModel(ComponentModel):
  def __init__(self, name, reactor, stopcock, hardwareComm, modelLock):
    """Stopcock valve model constructor"""
    ComponentModel.__init__(self, name, hardwareComm, modelLock)
    self.reactor = reactor
    self.stopcock = stopcock
    self.valvePosition = 0

  def getAllowedPositions(self):
    """Returns the allowed stopcock positions"""
    return [1, 2]
     
  def getPosition(self, bLockModel = True):
    """Returns the current stopcock position"""
    return self.protectedReturn(self.valvePosition, bLockModel)
     
  def setPosition(self, nPosition):
    """Sets the stopcock position"""
    self.hardwareComm.ReactorStopcockPosition(self.reactor, self.stopcock, nPosition)

  def updateState(self, nValvePosition1, nValvePosition2):
    """Update the internal state"""
    if (nValvePosition1 == True) and (nValvePosition2 == False):
      self.valvePosition = 1
    elif (nValvePosition1 == False) and (nValvePosition2 == True):
      self.valvePosition = 2
    else:
      self.valvePosition = 0
