"""Valves Model

Valves Model Class
"""

# Imports
import sys
sys.path.append("/opt/elixys/hardware/")
from HardwareComm import HardwareComm
from ComponentModel import ComponentModel
    
# Valves model
class ValvesModel(ComponentModel):
  def __init__(self, name, hardwareComm, modelLock):
    """Valves model constructor"""
    ComponentModel.__init__(self, name, hardwareComm, modelLock)
    self.gasTransferValveOpen = False
    self.f18LoadValveOpen = False
    self.hplcLoadValveOpen  = False

  def getGasTransferValveOpen(self, bLockModel = True):
    """Returns True if the gas transfer valve is open, False otherwise"""
    if bLockModel:
      return self.protectedReturn1(self.getGasTransferValveOpen)
    else:
      return self.gasTransferValveOpen
     
  def getF18LoadValveOpen(self, bLockModel = True):
    """Returns True if the F18 load valve is open, False otherwise"""
    if bLockModel:
      return self.protectedReturn1(self.getF18LoadValveOpen)
    else:
      return self.f18LoadValveOpen

  def getHPLCLoadValveOpen(self, bLockModel = True):
    """Returns True if the HPLC load valve is open, False otherwise"""
    if bLockModel:
      return self.protectedReturn1(self.getHPLCLoadValveOpen)
    else:
      return self.hplcLoadValveOpen

  def setGasTransferValveOpen(self, bValveOpen):
    """Opens or closes the gas transfer valve"""
    if bValveOpen:
      self.hardwareComm.GasTransferStart()
    else:
      self.hardwareComm.GasTransferStop()

  def setF18LoadValveOpen(self, bValveOpen):
    """Opens or closes the F18 load valve"""
    if bValveOpen:
      self.hardwareComm.LoadF18Start()
    else:
      self.hardwareComm.LoadF18Stop()

  def setHPLCLoadValveOpen(self, nReagent, bValveOpen):
    """Opens or closes the HPLC load value"""
    if bValveOpen:
      self.hardwareComm.LoadHPLCStart()
    else:
      self.hardwareComm.LoadHPLCStop()

  def updateState(self, bGasTransferValveOpen, bF18LoadValveOpen, bHPLCLoadValveOpen):
    """Update the internal state"""
    self.gasTransferValveOpen = bGasTransferValveOpen
    self.f18LoadValveOpen = bF18LoadValveOpen
    self.hplcLoadValveOpen  = bHPLCLoadValveOpen
