"""Radiation Detector Model

Reactor Radiation Detector Base Class
"""

# Imports
import sys
sys.path.append("../hardware/")
from HardwareComm import HardwareComm
from ComponentModel import ComponentModel

# Radiation detector model
class RadiationDetectorModel(ComponentModel):
  def __init__(self, name, reactor, hardwareComm, modelLock):
    """Radiation detector model constructor"""
    ComponentModel.__init__(self, name, hardwareComm, modelLock)
    self.reactor = reactor
    self.radiation = 0

  def getRadiation(self, bLockModel = True):
    """Returns the current radiation reading"""
    return self.protectedReturn(self.radiation, bLockModel)
 
  def updateState(self, nRadiation):
    """Update the internal state"""
    self.radiation = nRadiation
