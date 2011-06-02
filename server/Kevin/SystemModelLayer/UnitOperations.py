"""Unit operations

Elixys Unit Operations
"""
class UnitOperation():
  def __init__(self,systemModel):
    self.params = {"param":"value"}
    self.systemModel = systemModel
    self.steps = ("step1","step2")
    self.currentStep = "step1"
    self.stepCounter = 1
    self.isRunning = True

  def logError():
    """Get current error from hardware comm."""
    #error.log("error")
    pass
  def run(self):
    if self.steps:
      try:
        self.currentStep = self.steps.pop(0)
        self.stepCounter += 1
      except:
        print("Error setting next step in UnitOperations.run()") # This will be an error log
    elif len(self.steps)==0:
      self.isRunning = False
      print "unit operation complete"
    else:
      print("Self.steps does not exist")# This will be an error log
  def resume(self):
    pass
  def pause(self):
    pass
  def abort():
    pass
  def getTotalSteps(self):
    return self.steps #Integer

  def isRunning(self):
    return self.isRunning
    
  def getCurrentStepNumber(self):
    return self.stepCounter

  def getCurrentStepName(self):
    return self.currentStep

  def setParam(self,name,value): #(String,Any)
    self.params[name] = value
    
  def getParam(self,name): #String
    return self.params[name]
    
  def moveTo(self,position):
    print position
    
  def heat(self,temp,time,cooltemp):
    print temp,time,cooltemp
    
    
    
class Evaporate(UnitOperation):
  def __init__(self):
    UnitOperation.__init__(self)
    
    
    
    
class React(UnitOperation):
  def __init__(self,systemModel,params):
    UnitOperation.__init__(self,systemModel)
    self.params = params #Should have parameters listed below
    #self.ReactorID
    #self.Temp
    #self.Time
    #self.coolTemp
    #self.positionName
  def setReactorPosition(self):
    self.systemModel[self.ReactorID]['motion'].setPosition(self.positionName)

  def getTemperatureController():
    return self.systemModel[self.ReactorID]['temperature_controller']
    
  def setTemp(self):
    self.systemModel[self.ReactorID]['motion'].setTemperature(self.Temp)
    
  def getTemp(self):
    self.systemModel[self.ReactorID]['motion'].getCurrentTemperature(self.Temp)
    
  def startTimer(self):
    #Not sure how a timer is implemented yet, but need to pass in duration of reaction:
    self.startTimer(self.Time)
    
  def setCool(self):
  
    pass
  
    



def test():
  react1 = React()
  react1.run()

    
if __name__=="__main__":
    test()