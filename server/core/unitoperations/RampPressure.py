# RampPressure unit operation

# Imports
from UnitOperations import *

class RampPressure(UnitOperation):
  def __init__(self,systemModel,params):
    UnitOperation.__init__(self,systemModel)
    expectedParams = {PRESSUREREGULATOR:INT,PRESSURE:FLOAT,DURATION:INT}
    self.validateParams(params,expectedParams)
    if self.paramsValid:
      self.setParams(params)
    else:
      raise UnitOpError(paramError)
    # Should have the params listed below:
    # self.pressureRegulator
    # self.pressure
    # self.duration
  def run(self):
    try:
      self.setStatus("Ramping pressure")
      self.startTimer(self.duration)
      self.setPressureRegulator(str(self.pressureRegulator),self.pressure,self.duration)
      self.setStatus("Complete")
    except Exception as e:
      self.abortOperation(e)
