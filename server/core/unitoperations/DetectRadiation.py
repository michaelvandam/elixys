# DetectRadiation unit operation

# Imports
from UnitOperations import *

class DetectRadiation(UnitOperation):
  def __init__(self,systemModel,params):
    raise Exception("Implement DetectRadiation")
    UnitOperation.__init__(self,systemModel)
    self.setParams(params)
		#Should have parameters listed below:
    #self.ReactorID #Not sure we even need this. We should get all three every time.
    
  def run(self):
    try:
      self.beginNextStep("Starting Detect Radiation Operation")
      
      self.beginNextStep("Moving to detection position")
      self.setReactorPosition(RADIATION,1)
      self.setReactorPosition(RADIATION,2)
      self.setReactorPosition(RADIATION,3)
      self.beginNextStep("Starting radiation detection")
      self.getRadiation()
      self.beginNextStep("Radiation Detection Operation Complete")
    except Exception as e:
      self.abortOperation(e)
      
  def getRadiation(self):
    self.systemModel[self.ReactorID]['radiation_detector'].getCalibratedReading()
    self.waitForCondition(self.systemModel[self.ReactorID]['radiation_detector'].getCalibratedReading,self.calibrationCoefficient,GREATER,3)
