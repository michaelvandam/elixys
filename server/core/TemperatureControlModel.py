"""Tempearature Control Model

Reactor Temperature Control Model Class
"""

# Imports
import sys
sys.path.append("../hardware/")
from HardwareComm import HardwareComm
from ComponentModel import ComponentModel

# Reactor temperature model
class TemperatureControlModel(ComponentModel):
  def __init__(self, name, reactor, hardwareComm, modelLock):
    """Reactor temperature control model constructor"""
    ComponentModel.__init__(self, name, hardwareComm, modelLock)
    self.reactor = reactor
    self.heaterOn = False
    self.setTemperature = 0
    self.currentTemperature = 0

  def getMinimumTemperature(self):
    """Returns the minimum reactor temperature"""
    return 25
    
  def getMaximumTemperature(self):
    """Returns the maximum reactor temperature"""
    return 180
  
  def getHeaterOn(self, bLockModel = True):
    """Returns the heater state"""
    if bLockModel:
      return self.protectedReturn1(self.getHeaterOn)
    else:
      return self.heaterOn

  def getSetTemperature(self, bLockModel = True):
    """Returns the heater set temperature"""
    if bLockModel:
      return self.protectedReturn1(self.getSetTemperature)
    else:
      return self.setTemperature
      
  def getCurrentTemperature(self, bLockModel = True):
    """Returns the heater current temperature"""
    if bLockModel:
      return self.protectedReturn1(self.getCurrentTemperature)
    else:
      return self.currentTemperature
  
  def setHeaterOn(self, bHeaterOn):
    """Sets the heater state"""
    if bHeaterOn:
      self.hardwareComm.HeaterOn(self.reactor)
      #self.hardwareComm.HeaterOn(self.reactor, 1)
      #self.hardwareComm.HeaterOn(self.reactor, 2)
      #self.hardwareComm.HeaterOn(self.reactor, 3)
    else:
      self.hardwareComm.HeaterOff(self.reactor)
      #self.hardwareComm.HeaterOff(self.reactor, 1)
      #self.hardwareComm.HeaterOff(self.reactor, 2)
      #self.hardwareComm.HeaterOff(self.reactor, 3)

  def setSetPoint(self, nSetTemperature):
    """Sets the heater set Set Point"""
    self.hardwareComm.SetHeater(self.reactor, nSetTemperature)
    #self.hardwareComm.SetHeater(self.reactor, 1, nSetTemperature)
    #self.hardwareComm.SetHeater(self.reactor, 2, nSetTemperature)
    #self.hardwareComm.SetHeater(self.reactor, 3, nSetTemperature)
  
  def updateState(self, nHeater1On, nHeater2On, nHeater3On, nHeater1SetTemperature, nHeater2SetTemperature, nHeater3SetTemperature, nHeater1CurrentTemperature,
                  nHeater2CurrentTemperature, nHeater3CurrentTemperature):
    """Updates the internal state"""
    self.heaterOn = nHeater1On or nHeater2On or nHeater3On
    self.setTemperature = (nHeater1SetTemperature + nHeater2SetTemperature + nHeater3SetTemperature) / 3
    self.currentTemperature = (nHeater1CurrentTemperature + nHeater2CurrentTemperature + nHeater3CurrentTemperature) / 3
