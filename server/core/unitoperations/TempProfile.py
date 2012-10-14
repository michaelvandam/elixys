# TempProfile unit operation

# Imports
from UnitOperation import *

class TempProfile(UnitOperation):
  def __init__(self,systemModel,params):
    UnitOperation.__init__(self,systemModel)
    expectedParams = {REACTORID:STR,REACTTEMP:FLOAT,REACTTIME:INT,COOLTEMP:INT,LIQUIDTCREACTOR:INT,LIQUIDTCCOLLET:INT,STIRSPEED:INT}
    paramError = self.validateParams(params,expectedParams)
    if self.paramsValid:
      self.setParams(params)
    else:
      raise UnitOpError(paramError)

  def run(self):
    try:
      self.setStatus("Moving to position")
      self.setReactorPosition(TRANSFER)
      self.setStatus("Heating")
      self.setStirSpeed(self.stirSpeed)
      self.setTemp()
      self.setHeater(ON)
      self.setStatus("Profiling")
      self.startTimer(self.reactTime)
      self.waitForTimer()
      self.setStatus("Cooling")
      self.setHeater(OFF)
      self.setCoolLiquid()
      self.setStirSpeed(OFF)
      self.setStatus("Complete")
    except Exception as e:
      self.abortOperation(str(e), False)

  def setCoolLiquid(self):
    self.systemModel[self.ReactorID]['Thermocouple'].setHeaterOff()
    self.waitForCondition(self.systemModel[self.ReactorID]['Thermocouple'].getHeaterOn,False,EQUAL,3)
    self.systemModel['CoolingSystem'].setCoolingSystemOn(ON)
    self.waitForCondition(self.systemModel['CoolingSystem'].getCoolingSystemOn,ON,EQUAL,3)
    if self.liquidTCCollet == 1:
      self.waitForCondition(self.systemModel['Reactor' + str(self.liquidTCReactor)]['Thermocouple'].getHeater1CurrentTemperature,self.coolTemp,LESS,65535)
    elif self.liquidTCCollet == 2:
      self.waitForCondition(self.systemModel['Reactor' + str(self.liquidTCReactor)]['Thermocouple'].getHeater2CurrentTemperature,self.coolTemp,LESS,65535)
    elif self.liquidTCCollet == 3:
      self.waitForCondition(self.systemModel['Reactor' + str(self.liquidTCReactor)]['Thermocouple'].getHeater3CurrentTemperature,self.coolTemp,LESS,65535)
    else:
      raise Exception("Unknown collet number")
    self.systemModel['CoolingSystem'].setCoolingSystemOn(OFF)
    self.waitForCondition(self.systemModel['CoolingSystem'].getCoolingSystemOn,OFF,EQUAL,3)
