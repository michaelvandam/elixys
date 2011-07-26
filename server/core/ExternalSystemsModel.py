"""External Systems Model

Externals Systems Model Class
"""

# Imports
import sys
sys.path.append("../hardware/")
from HardwareComm import HardwareComm
from ComponentModel import ComponentModel
    
# External systems model
class ExternalSystemsModel(ComponentModel):
  def __init__(self, name, hardwareComm):
    """External systems model constructor"""
    ComponentModel.__init__(self, name, hardwareComm)
    self.f18LoadValveOpen = False
    self.f18EluteValveOpen = False
    self.hplcLoadValveOpen  = False

  def getF18LoadValveOpen(self):
     """Returns True if the F18 load valve is open, False otherwise"""
     return self.f18LoadValveOpen

  def getF18EluteValveOpen(self):
     """Returns True if the F18 elute valve is open, False otherwise"""
     return self.f18EluteValveOpen
     
  def getHPLCLoadValveOpen(self):
     """Returns True if the HPLC load valve is open, False otherwise"""
     return self.hplcLoadValveOpen

  def setF18LoadValveOpen(self, bValveOpen):
     """Opens or closes the F18 load valve"""
     if bValveOpen:
       self.hardwareComm.LoadF18Start()
     else:
       self.hardwareComm.LoadF18Stop()

  def setF18EluteValveOpen(self, bValveOpen):
     """Opens or closes the F18 elute valve"""
     if bValveOpen:
       self.hardwareComm.EluteF18Start()
     else:
       self.hardwareComm.EluteF18Stop()

  def setHPLCLoadValveOpen(self, nReagent, bValveOpen):
     """Opens or closes the HPLC load value"""
     if bValveOpen:
       self.hardwareComm.LoadHPLCStart()
     else:
       self.hardwareComm.LoadHPLCStop()

  def updateState(self, bF18LoadValveOpen, bF18EluteValveOpen, bHPLCLoadValveOpen):
    """Update the internal state"""
    self.f18LoadValveOpen = bF18LoadValveOpen
    self.f18EluteValveOpen = bF18EluteValveOpen
    self.hplcLoadValveOpen  = bHPLCLoadValveOpen