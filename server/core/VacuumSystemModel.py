"""Vacuum System Model

Vacuum System Model Class
"""

# Imports
import sys
sys.path.append("../hardware/")
from HardwareComm import HardwareComm
from ComponentModel import ComponentModel

# Vacuum system model    
class VacuumSystemModel(ComponentModel):
  def __init__(self, name, hardwareComm, modelLock):
    """Vacuum system model constructor"""
    ComponentModel.__init__(self, name, hardwareComm, modelLock)
    self.vacuumSystemOn = False
    self.vacuumSystemPressure = 0

  def getVacuumSystemOn(self, bLockModel = True):
    """Returns True if the vacuum system is on, False otherwise"""
    if bLockModel:
      return self.protectedReturn1(self.getVacuumSystemOn)
    else:
      return self.vacuumSystemOn

  def getVacuumSystemPressure(self, bLockModel = True):
    """Returns the vacuum system pressure"""
    if bLockModel:
      return self.protectedReturn1(self.getVacuumSystemPressure)
    else:
      return self.vacuumSystemPressure
    
  def setVacuumSystemOn(self):
    """Turns the vacuum system on"""
    self.hardwareComm.VacuumSystemOn()
      
  def setVacuumSystemOff(self):
    """Turns the vacuum system on"""
    self.hardwareComm.VacuumSystemOff()

  def updateState(self, bVacuumSystemOn, fVacuumSystemPressure):
    """Update the internal state"""
    self.vacuumSystemOn = bVacuumSystemOn
    self.vacuumSystemPressure = fVacuumSystemPressure
    