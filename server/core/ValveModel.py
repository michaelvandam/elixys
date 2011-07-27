"""Valve Model

Valve Model Class
"""

# Imports
import sys
sys.path.append("../hardware/")
from HardwareComm import HardwareComm
from ComponentModel import ComponentModel
    
# Valve model
class ValveModel(ComponentModel):
  def __init__(self, name, reactor, hardwareComm, modelLock):
    """Valve model constructor"""
    ComponentModel.__init__(self, name, hardwareComm, modelLock)
    self.reactor = reactor
    self.evaporationNitrogenValveOpen = False
    self.evaporationVacuumValveOpen = False
    self.transferValveOpen = False
    self.reagent1TransferValveOpen = False
    self.reagent2TransferValveOpen = False

  def getEvaporationNitrogenValveOpen(self, bLockModel = True):
    """Returns True if the evaporation nitrogen valve is open, False otherwise"""
    if bLockModel:
      return self.protectedReturn1(getEvaporationNitrogenValveOpen)
    else:
      return self.evaporationNitrogenValveOpen

  def getEvaporationVacuumValveOpen(self, bLockModel = True):
    """Returns True if the evaporation vacuum valve is open, False otherwise"""
    if bLockModel:
      return self.protectedReturn1(getEvaporationVacuumValveOpen)
    else:
      return self.evaporationVacuumValveOpen
     
  def getTransferValveOpen(self, bLockModel = True):
    """Returns True if the transfer valve is open, False otherwise"""
    if bLockModel:
      return self.protectedReturn1(getTransferValveOpen)
    else:
      return self.transferValveOpen

  def getReagent1TransferValveOpen(self, bLockModel = True):
    """Returns True if the reagent 1 transfer valve is open, False otherwise"""
    if bLockModel:
      return self.protectedReturn1(getReagent1TransferValveOpen)
    else:
      return self.reagent1TransferValveOpen

  def getReagent2TransferValveOpen(self, bLockModel = True):
    """Returns True if the reagent 2 transfer valve is open, False otherwise"""
    if bLockModel:
      return self.protectedReturn1(getReagent2TransferValveOpen)
    else:
      return self.reagent2TransferValveOpen
     
  def setEvaporationValvesOpen(self, bValveOpen):
    """Opens or closes the evaporation nitrogen and vacuum valves"""
    if bValveOpen:
      self.hardwareComm.ReactorEvaporateStart(self.reactor)
    else:
      self.hardwareComm.ReactorEvaporateStop(self.reactor)

  def setTransferValveOpen(self, bValveOpen):
    """Returns True if the transfer valve is open, False otherwise"""
    if bValveOpen:
      self.hardwareComm.ReactorTransferStart(self.reactor)
    else:
      self.hardwareComm.ReactorTransferStop(self.reactor)

  def setReagentTransferValveOpen(self, nReagent, bValveOpen):
    """Returns True if the reagent transfer valve is open, False otherwise"""
    if bValveOpen:
      self.hardwareComm.ReactorReagentTransferStart(self.reactor, nReagent)
    else:
      self.hardwareComm.ReactorReagentTransferStop(self.reactor, nReagent)

  def updateState(self, bEvaporationNitrogenValveOpen, bEvaporationVacuumValveOpen, bTransferValveOpen, bReagent1TransferValveOpen, bReagent2TransferValveOpen):
    """Update the internal state"""
    self.evaporationNitrogenValveOpen = bEvaporationNitrogenValveOpen
    self.evaporationVacuumValveOpen = bEvaporationVacuumValveOpen
    self.transferValveOpen = bTransferValveOpen
    self.reagent1TransferValveOpen = bReagent1TransferValveOpen
    self.reagent2TransferValveOpen = bReagent2TransferValveOpen
