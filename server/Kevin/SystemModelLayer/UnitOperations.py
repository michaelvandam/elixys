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
    self.pause = False

  def logError():
    """Get current error from hardware comm."""
    #error.log("error")
    pass
  def doNext(self):
    if self.pause:
      self.pause()
    elif self.steps:
      try:
        self.currentStep = self.steps.pop(0) #Removes step from list, sets next step.
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
    self.pause = True
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
    
    

   
class React(UnitOperation):
  def __init__(self,systemModel,params):
    UnitOperation.__init__(self,systemModel)
    self.params = params #Should have parameters listed below
    #self.ReactorID
    #self.Temp
    #self.Time
    #self.coolTemp
    #self.positionName
  def run(self):
    self.steps=["Starting react operation","Moving to reaction position","Heating reactor","Waiting for reaction","Cooling reactor"]
    self.doNext()
    self.setReactorPosition()
    self.doNext()
    self.setTemp()
    self.doNext()
    self.startTimer()
    self.doNext()
    self.setCool()
    self.doNext()
  
  def setReactorPosition(self):
    self.systemModel[self.ReactorID]['motion'].setPosition(self.positionName)
    self.waitForCondition(self.systemModel[self.ReactorID]['motion'].getPosition(),self.positionName)

  def getTemperatureController(): #Not sure why we need this?
    return self.systemModel[self.ReactorID]['temperature_controller']
    
  def setTemp(self):
    self.systemModel[self.ReactorID]['temperature_controller'].setTemperature(self.Temp)
    self.waitForCondition(self.systemModel[self.ReactorID]['temperature_controller'].getTemperature(),self.Temp)
    
  def getTemp(self):
    self.systemModel[self.ReactorID]['temperature_controller'].getCurrentTemperature()
    
  def startTimer(self):
    self.startTimer(self.Time)
  
  def setCool(self):
    self.systemModel[self.ReactorID]['temperature_controller'].setCool(self.coolTemp)       
    self.waitForCondition(self.systemModel[self.ReactorID]['temperature_controller'].getTemperature(),self.coolTemp)

class AddReagent(UnitOperation):
  def __init__(self,systemModel,params):
    UnitOperation.__init__(self,systemModel)
    self.params = params #Should have parameters listed below
    #self.ReactorID
    #self.ReagentID(or Position)

  def run(self):
    self.steps=["Starting add reagent operation","Moving to addition position","Adding reagent","Removing empty vial"]
    self.doNext()
    self.setReactorPosition()
    self.doNext()
    self.setGripperPlace()
    self.startTimer()
    self.doNext()
    self.setGripperRemove()
    self.doNext()
  
  def setReactorPosition(self):
    self.systemModel[self.ReactorID]['motion'].setPosition(REAGENT)
    self.waitForCondition(self.systemModel[self.ReactorID]['motion'].getPosition(),REAGENT)

  def setGripperPlace():
    self.systemModel[self.Gripper].setPosition(self.ReagentID)
    self.waitForCondition( self.systemModel[self.Gripper].getPosition(),self.ReagentID)
    
  def setGripperPlace():
    self.systemModel[self.Gripper].setRemovePosition(self.ReagentID)
    self.waitForCondition( self.systemModel[self.Gripper].getRemovePosition(),self.ReagentID)

class Evaporate(UnitOperation):
  def __init__(self,systemModel,params):
    UnitOperation.__init__(self,systemModel)
    self.params = params #Should have parameters listed below
    #self.ReactorID
    #self.Temp
    #self.Time
    #self.coolTemp
  def run(self):
    self.steps=["Starting evaporate operation","Moving to evaporation position","Heating reactor","Waiting for evaporation","Cooling reactor"]
    self.doNext()
    self.setReactorPosition()
    self.doNext()
    self.setTemp()
    self.doNext()
    self.startTimer()
    self.doNext()
    self.setCool()
    self.doNext()
  
  def setReactorPosition(self):
    self.systemModel[self.ReactorID]['motion'].setPosition(EVAPORATE)
    self.waitForCondition(self.systemModel[self.ReactorID]['motion'].getPosition(),EVAPORATE)

  def getTemperatureController(): #Not sure why we need this?
    return self.systemModel[self.ReactorID]['temperature_controller']
    
  def setTemp(self):
    self.systemModel[self.ReactorID]['temperature_controller'].setTemperature(self.Temp)
    self.waitForCondition(self.systemModel[self.ReactorID]['temperature_controller'].getTemperature(),self.Temp)
    
  def getTemp(self):
    self.systemModel[self.ReactorID]['temperature_controller'].getCurrentTemperature()
    
  def startTimer(self):
    self.startTimer(self.Time)
  
  def setCool(self):
    self.systemModel[self.ReactorID]['temperature_controller'].setCool(self.coolTemp)       
    self.waitForCondition(self.systemModel[self.ReactorID]['temperature_controller'].getTemperature(),self.coolTemp) 
    
class InstallVial(UnitOperation):
  def __init__(self,systemModel,params):
    UnitOperation.__init__(self,systemModel)
    self.params = params #Should have parameters listed below
    #self.ReactorID
  def run(self):
    self.steps=["Starting install vial operation","Moving to vial installation position"]
    self.doNext()
    self.setReactorPosition()
    self.doNext()
  
  def setReactorPosition(self):
    self.systemModel[self.ReactorID]['motion'].setPosition(INSTALL)
    self.waitForCondition(self.systemModel[self.ReactorID]['motion'].getPosition(),INSTALL)
    
class TransferToHPLC(UnitOperation):
  def __init__(self,systemModel,params):
    UnitOperation.__init__(self,systemModel)
    self.params = params #Should have parameters listed below
    #self.ReactorID
    
  def run(self):
    self.steps=["Starting HPLC Transfer operation","Moving to transfer position","Transferring product to HPLC","Switching injection valve"]
    self.doNext()
    self.setReactorPosition()
    self.doNext()
    self.setTransfer()
    self.doNext()
    self.setHPLC()
    self.doNext()
  
  def setReactorPosition(self):
    self.systemModel[self.ReactorID]['motion'].setPosition(TRANSFER)
    self.waitForCondition(self.systemModel[self.ReactorID]['motion'].getPosition(),TRANSFER)

  def setTransfer(self):
    self.systemModel[self.ReactorID]['transfer'].setTransfer(HPLC)
    self.waitForCondition(self.systemModel[self.ReactorID]['transfer'].getTransfer(),HPLC)
    
  def setHPLC(self):
    self.systemModel[self.ReactorID]['transfer'].setHPLC(INJECT)       
    self.waitForCondition(self.systemModel[self.ReactorID]['transfer'].getHPLC(),INJECT) 
  
class TransferElute(UnitOperation):
  def __init__(self,systemModel,params):
    UnitOperation.__init__(self,systemModel)
    self.params = params #Should have parameters listed below
    #self.ReactorID
    #self.stopcockPosition
    
  def run(self):
    self.steps=["Starting Transfer operation","Moving to transfer position","Setting stopcock position","Beginning transfer"]
    self.doNext()
    self.setReactorPosition()
    self.doNext()
    self.setStopcock()
    self.doNext()
    self.setTransfer()
    self.doNext()
  
  def setReactorPosition(self):
    self.systemModel[self.ReactorID]['motion'].setPosition(TRANSFER)
    self.waitForCondition(self.systemModel[self.ReactorID]['motion'].getPosition(),TRANSFER)
  
  def setStopcock(self):
    self.systemModel[self.ReactorID]['stopcock'].setStopcock(self.stopcockPosition)       
    self.waitForCondition(self.systemModel[self.ReactorID]['stopcock'].getStopcock(),self.stopcockPosition) 
    
  def setTransfer(self):
    self.systemModel[self.ReactorID]['transfer'].setTransfer(self.transferPosition)
    self.waitForCondition(self.systemModel[self.ReactorID]['transfer'].getTransfer(),self.transferPosition)
   
class Transfer(UnitOperation):
  def __init__(self,systemModel,params):
    UnitOperation.__init__(self,systemModel)
    self.params = params #Should have parameters listed below
    #self.ReactorID
    #self.transferPosition
    
  def run(self):
    self.steps=["Starting Transfer operation","Moving to transfer position","Transferring product"]
    self.doNext()
    self.setReactorPosition()
    self.doNext()
    self.setTransfer()
    self.doNext()
  
  def setReactorPosition(self):
    self.systemModel[self.ReactorID]['motion'].setPosition(TRANSFER)
    self.waitForCondition(self.systemModel[self.ReactorID]['motion'].getPosition(),TRANSFER)

  def setTransfer(self):
    self.systemModel[self.ReactorID]['transfer'].setTransfer(self.transferPosition)
    self.waitForCondition(self.systemModel[self.ReactorID]['transfer'].getTransfer(),self.transferPosition)
 
class UserInput(UnitOperation):
  def __init__(self,systemModel,params):
    UnitOperation.__init__(self,systemModel)
    self.params = params #Should have parameters listed below
    #self.userMessage
    #self.isCheckbox
    
  def run(self):
    self.steps=["Starting Transfer operation","Moving to transfer position","Transferring product"]
    self.doNext()
    self.setReactorPosition()
    self.doNext()
    self.setTransfer()
    self.doNext()
  
  def setReactorPosition(self):
    self.systemModel[self.ReactorID]['motion'].setPosition(self.positionName)
    self.waitForCondition(self.systemModel[self.ReactorID]['motion'].getPosition(),self.positionName)

  def setTransfer(self):
    self.systemModel[self.ReactorID]['transfer'].setTransfer(self.transferPosition)
    self.waitForCondition(self.systemModel[self.ReactorID]['transfer'].getTransfer(),self.transferPosition)
    
class DetectRadiation(UnitOperation):
  def __init__(self,systemModel,params):
    UnitOperation.__init__(self,systemModel)
    self.params = params #Should have parameters listed below
    #self.ReactorID
    
  def run(self):
    self.steps=["Starting radiation detector operation","Moving to radiation detector position","Detecting radiation"]
    self.doNext()
    self.setReactorPosition()
    self.doNext()
    self.getRadiation()
    self.doNext()
  
  def setReactorPosition(self):
    self.systemModel[self.ReactorID]['motion'].setPosition(RADIATION)
    self.waitForCondition(self.systemModel[self.ReactorID]['motion'].getPosition(),RADIATION)

  def getRadiation(self):
    self.systemModel[self.ReactorID]['radiation_detector'].getCalibratedReading()
    
def test():
  react1 = React()
  react1.run()

    
if __name__=="__main__":
    test()