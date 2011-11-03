# TransferToHPLC unit operation

# Imports
from UnitOperations import *

class TransferToHPLC(UnitOperation):
  def __init__(self,systemModel,params):
    UnitOperation.__init__(self,systemModel)
    self.setParams(params)
		#Should have parameters listed below:
    #self.ReactorID
    #self.stopcockPosition
  def run(self):
    try:
      self.beginNextStep("Starting HPLC Operation")
      self.abortOperation()
      self.beginNextStep("Moving to transfer position")
      self.setReactorPosition(TRANSFER)
      self.beginNextStep("Moving stopcocks to transfer position")
      self.setStopcockPosition(TRANSFER)
      self.beginNextStep("Moving HPLC valve to transfer position")
      self.setHPLCValve()
      self.beginNextStep("Starting transfer")
      self.setTransfer()
      self.beginNextStep()
      ###
      #Need more here? Liquid sensors, pressure regulator, etc?
      ###
      self.beginNextStep("HPLC Transfer Operation Complete")
    except Exception as e:
      self.abortOperation(e)
      
  """def setParams(self,currentParams):
    expectedParams = ['ReactorID','stopcockPosition']
    self.paramsValid = True
    for parameter in expectedParams:
      if not(parameter in currentParams):
        self.paramsValid = False
        #Log Error
      self.paramsValidated = True"""
      
  def setHPLCValve(self):
    self.systemModel[self.ReactorID]['transfer'].setHPLC(INJECT)       
    self.waitForCondition(self.systemModel[self.ReactorID]['transfer'].getHPLC(),INJECT,EQUAL,3) 
