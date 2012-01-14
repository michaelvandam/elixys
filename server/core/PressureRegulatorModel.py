"""Pressure Regulator Model

Pressure Regulator Model Class
"""

# Imports
import sys
sys.path.append("/opt/elixys/hardware/")
from HardwareComm import HardwareComm
from ComponentModel import ComponentModel

# Pressure regulator model
class PressureRegulatorModel(ComponentModel):
  def __init__(self, name, pressureRegulator, hardwareComm, modelLock):
    """Pressure regulator model construction"""
    ComponentModel.__init__(self, name, hardwareComm, modelLock)
    self.pressureRegulator = pressureRegulator
    self.setPressure = 0
    self.currentPressure = 0

  def getMinimumPressure(self):
    """Returns the minimum pressure"""
    return 0
    
  def getMaximumPressure(self):
    """Returns the maximum pressure"""
    return 60
    
  def getSetPressure(self, bLockModel = True):
    """Returns the set pressure"""
    if bLockModel:
      return self.protectedReturn1(self.getSetPressure)
    else:
      return self.setPressure
  
  def getCurrentPressure(self, bLockModel = True):
    """Returns the current pressure"""
    if bLockModel:
      return self.protectedReturn1(self.getCurrentPressure)
    else:
      return self.currentPressure
  
  def setRegulatorPressure(self, nPressure):
    """Sets the set pressure"""
    self.hardwareComm.SetPressureRegulator(self.pressureRegulator, nPressure)

  def updateState(self, nSetPressure, nCurrentPressure):
    """Update the internal state"""
    self.setPressure = nSetPressure
    self.currentPressure = nCurrentPressure
