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
    self.heater1On = False
    self.heater2On = False
    self.heater3On = False
    self.heaterOn = False
    self.heater1SetTemperature = 0
    self.heater2SetTemperature = 0
    self.heater3SetTemperature = 0
    self.setTemperature = 0
    self.heater1CurrentTemperature = 0
    self.heater2CurrentTemperature = 0
    self.heater3CurrentTemperature = 0
    self.currentTemperature = 0

  def getMinimumTemperature(self):
    """Returns the minimum reactor temperature"""
    return 25
    
  def getMaximumTemperature(self):
    """Returns the maximum reactor temperature"""
    return 180
  
  def getHeater1On(self, bLockModel = True):
    """Returns the heater state"""
    if bLockModel:
      return self.protectedReturn1(self.getHeater1On)
    else:
      return self.heater1On

  def getHeater2On(self, bLockModel = True):
    """Returns the heater state"""
    if bLockModel:
      return self.protectedReturn1(self.getHeater2On)
    else:
      return self.heater2On

  def getHeater3On(self, bLockModel = True):
    """Returns the heater state"""
    if bLockModel:
      return self.protectedReturn1(self.getHeater3On)
    else:
      return self.heater3On

  def getHeaterOn(self, bLockModel = True):
    """Returns the heater state"""
    if bLockModel:
      return self.protectedReturn1(self.getHeaterOn)
    else:
      return self.heaterOn

  def getHeater1SetTemperature(self, bLockModel = True):
    """Returns the heater set temperature"""
    if bLockModel:
      return self.protectedReturn1(self.getHeater1SetTemperature)
    else:
      return self.heater1SetTemperature

  def getHeater2SetTemperature(self, bLockModel = True):
    """Returns the heater set temperature"""
    if bLockModel:
      return self.protectedReturn1(self.getHeater2SetTemperature)
    else:
      return self.heater2SetTemperature

  def getHeater3SetTemperature(self, bLockModel = True):
    """Returns the heater set temperature"""
    if bLockModel:
      return self.protectedReturn1(self.getHeater3SetTemperature)
    else:
      return self.heater3SetTemperature

  def getSetTemperature(self, bLockModel = True):
    """Returns the heater set temperature"""
    if bLockModel:
      return self.protectedReturn1(self.getSetTemperature)
    else:
      return self.setTemperature
      
  def getHeater1CurrentTemperature(self, bLockModel = True):
    """Returns the heater current temperature"""
    if bLockModel:
      return self.protectedReturn1(self.getHeater1CurrentTemperature)
    else:
      return self.heater1CurrentTemperature
  
  def getHeater2CurrentTemperature(self, bLockModel = True):
    """Returns the heater current temperature"""
    if bLockModel:
      return self.protectedReturn1(self.getHeater2CurrentTemperature)
    else:
      return self.heater2CurrentTemperature
  
  def getHeater3CurrentTemperature(self, bLockModel = True):
    """Returns the heater current temperature"""
    if bLockModel:
      return self.protectedReturn1(self.getHeater3CurrentTemperature)
    else:
      return self.heater3CurrentTemperature
  
  def getCurrentTemperature(self, bLockModel = True):
    """Returns the heater current temperature"""
    if bLockModel:
      return self.protectedReturn1(self.getCurrentTemperature)
    else:
      return self.currentTemperature
  
  def setHeaterOn(self):
    """Sets the heater state"""
    self.hardwareComm.HeaterOn(self.reactor)
    
  def setHeaterOff(self):
    self.hardwareComm.HeaterOff(self.reactor)

  def setSetPoint(self, nSetTemperature):
    """Sets the heater set Set Point"""
    self.hardwareComm.SetHeaterTemp(self.reactor, nSetTemperature)

  def updateState(self, nHeater1On, nHeater2On, nHeater3On, nHeater1SetTemperature, nHeater2SetTemperature, nHeater3SetTemperature, nHeater1CurrentTemperature,
                  nHeater2CurrentTemperature, nHeater3CurrentTemperature):
    """Updates the internal state"""
    self.heater1On = nHeater1On
    self.heater2On = nHeater2On
    self.heater3On = nHeater3On
    self.heaterOn = nHeater1On or nHeater2On or nHeater3On
    self.heater1SetTemperature = nHeater1SetTemperature
    self.heater2SetTemperature = nHeater2SetTemperature
    self.heater3SetTemperature = nHeater3SetTemperature
    self.setTemperature = (nHeater1SetTemperature + nHeater2SetTemperature + nHeater3SetTemperature) / 3
    self.heater1CurrentTemperature = nHeater1CurrentTemperature
    self.heater2CurrentTemperature = nHeater2CurrentTemperature
    self.heater3CurrentTemperature = nHeater3CurrentTemperature
    self.currentTemperature = (nHeater1CurrentTemperature + nHeater2CurrentTemperature + nHeater3CurrentTemperature) / 3
