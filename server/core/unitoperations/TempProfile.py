# TempProfile unit operation

# Imports
from UnitOperation import *

class TempProfile(UnitOperation):
  def __init__(self,systemModel,params):
    UnitOperation.__init__(self,systemModel)
    self.setParams(params)
    #Should have parameters listed below:
    #self.ReactorID
    #self.reactTemp
    #self.reactTime
    #self.coolTemp
  def run(self):
    try:
      self.setStatus("Moving to position")
      self.setReactorPosition(TRANSFER)
      self.setStatus("Heating")
      self.setTemp()
      self.setHeater(ON)
      self.setStatus("Profiling")
      self.startTimer(self.reactTime)
      self.waitForTimer()
      self.setStatus("Cooling")
      self.setHeater(OFF)
      self.setCool()
      self.setStatus("Complete")
    except Exception as e:
      self.abortOperation(e)
