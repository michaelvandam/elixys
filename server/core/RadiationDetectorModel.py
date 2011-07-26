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
  def __init__(self, name, reactor, hardwareComm):
    """Radiation detector model constructor"""
    ComponentModel.__init__(self, name, hardwareComm)
    self.reactor = reactor
    self.radiation = 0
 
  def getRadiation(self):
    """Returns the current radiation reading"""
    return self.radiation
 
  def updateState(self, nRadiation):
    """Update the internal state"""
    self.radiation = nRadiation
