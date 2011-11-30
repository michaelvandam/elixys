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
    self.valveCW = False
    self.valveCCW = False

  def getPosition(self, bLockModel = True):
    """Returns the current stopcock position"""
    if bLockModel:
      return self.protectedReturn1(self.getPosition)
    else:
      if self.valveCW and not self.valveCCW:
        return "CW"
      elif not self.valveCW and self.valveCCW:
        return "CCW"
      else:
        return "Unk"

  def getCW(self, bLockModel = True):
    """Returns the current clockwise stopcock position"""
    if bLockModel:
      return self.protectedReturn1(self.getCW)
    else:
      return self.valveCW
     
  def getCCW(self, bLockModel = True):
    """Returns the current clockwise stopcock position"""
    if bLockModel:
      return self.protectedReturn1(self.getCCW)
    else:
      return self.valveCCW

  def setCW(self):
    """Sets the stopcock to the clockwise position"""
    self.hardwareComm.ReactorStopcockCW(self.reactor, self.stopcock)

  def setCCW(self):
    """Sets the stopcock to the counterclockwise position"""
    self.hardwareComm.ReactorStopcockCCW(self.reactor, self.stopcock)
    
  def updateState(self, bValveCW, bValveCCW):
    """Update the internal state"""
    self.valveCW = bValveCW
    self.valveCCW = bValveCCW
