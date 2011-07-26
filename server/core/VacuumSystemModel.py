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
  def __init__(self, name, hardwareComm):
    """Vacuum system model constructor"""
    ComponentModel.__init__(self, name, hardwareComm)
    self.vacuumSystemOn = False
    self.vacuumSystemPressure = 0

  def getVacuumSystemOn(self):
    """Returns True if the vacuum system is on, False otherwise"""
    return self.vacuumSystemOn

  def getVacuumSystemPressure(self):
    """Returns the vacuum system pressure"""
    return self.vacuumSystemPressure
    
  def setVacuumSystemOn(self, bVacuumSystemOn):
    """Turns the vacuum system on and off"""
    if bVacuumSystemOn:
      self.hardwareComm.VacuumSystemOn()
    else:
      self.hardwareComm.VacuumSystemOff()

  def updateState(self, bVacuumSystemOn, fVacuumSystemPressure):
    """Update the internal state"""
    self.vacuumSystemOn = bVacuumSystemOn
    self.vacuumSystemPressure = fVacuumSystemPressure
    