"""Liquid sensors Model

Liquid Sensors Model Class
"""

# Imports
import sys
sys.path.append("/opt/elixys/hardware/")
from HardwareComm import HardwareComm
from ComponentModel import ComponentModel
    
# Liquid sensors model
class LiquidSensorsModel(ComponentModel):
  def __init__(self, name, hardwareComm, modelLock):
    """Liquid sensors model constructor"""
    ComponentModel.__init__(self, name, hardwareComm, modelLock)
    self.liquidSensor1 = False
    self.liquidSensor2 = False
    self.liquidSensorRaw1 = 0
    self.liquidSensorRaw2 = 0

  def getLiquidSensor1(self, bLockModel = True):
    """Returns the value of liquid sensor 1"""
    if bLockModel:
      return self.protectedReturn1(self.liquidSensor1)
    else:
      return self.liquidSensor1
     
  def getLiquidSensor2(self, bLockModel = True):
    """Returns the value of liquid sensor 2"""
    if bLockModel:
      return self.protectedReturn1(self.liquidSensor2)
    else:
      return self.liquidSensor2

  def getLiquidSensorRaw1(self, bLockModel = True):
    """Returns the raw value of liquid sensor 1"""
    if bLockModel:
      return self.protectedReturn1(self.liquidSensorRaw1)
    else:
      return self.liquidSensorRaw1

  def getLiquidSensorRaw2(self, bLockModel = True):
    """Returns the raw value of liquid sensor 2"""
    if bLockModel:
      return self.protectedReturn1(self.liquidSensorRaw2)
    else:
      return self.liquidSensorRaw2

  def updateState(self, bLiquidSensor1, bLiquidSensor2, fLiquidSensorRaw1, fLiquidSensorRaw2):
    """Update the internal state"""
    self.liquidSensor1 = bLiquidSensor1
    self.liquidSensor2 = bLiquidSensor2
    self.liquidSensorRaw1 = fLiquidSensorRaw1
    self.liquidSensorRaw2 = fLiquidSensorRaw2

