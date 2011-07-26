"""Cooling System Model

Cooling System Model Class
"""

# Imports
import sys
sys.path.append("../hardware/")
from HardwareComm import HardwareComm
from ComponentModel import ComponentModel

# Cooling system model
class CoolingSystemModel(ComponentModel):
  def __init__(self, name, hardwareComm, modelLock):
    """Cooling system model constructor"""
    ComponentModel.__init__(self, name, hardwareComm, modelLock)     
    self.coolingSystemOn = False
    
  def getCoolingSystemOn(self, bLockModel = True):
    """Returns True if the cooling system is on, False otherwise"""
    return self.protectedReturn(self.coolingSystemOn, bLockModel)

  def setCoolingSystemOn(self, bCoolingSystemOn):
    """Turns the cooling system on and off"""
    if bCoolingSystemOn:
      self.hardwareComm.CoolingSystemOn()
    else:
      self.hardwareComm.CoolingSystemOff()

  def updateState(self, bCoolingSystemOn):
    """Update the internal state"""
    self.coolingSystemOn = bCoolingSystemOn
