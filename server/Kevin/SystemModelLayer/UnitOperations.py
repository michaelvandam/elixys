"""Unit operations

Elixys Unit Operations
"""
import Thread from threading

ZUP = "ZUP"
ZDOWN = "ZDOWN"
XEVAPORATE = "XEVAPORATE"
XREACTA = "XREACTA"
XREACTB = "XREACTB"
XADDREAGENT = "XADDREAGENT"
XTRANSFER = "XTRANSFER"
XVIALREMOVE = "XVIALREMOVE"
XRADIATION = "XRADIATION"
EQUAL = "="
GREATER = ">"
LESS = "<"

class UnitOperation(Thread):
  def __init__(self,systemModel):
    Thread.__init__(self)
    self.params = {"param":"value"}
    self.systemModel = systemModel
    self.steps = ("step1","step2")
    self.currentStep = "step1"
    self.stepCounter = 1
    self.isRunning = True
    self.pause = False
  def setParams(params):
    
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
  def waitForCondition(function,condition,comparator):
    if comparator == EQUAL:
      while not(function() == condition):
        pass
    elif comparator == GREATER:
      while not(function() >= condition):
        pass
    elif comparator == LESS:
        while not(function() <= condition):
        pass
    
  def timeDelay(self):
    time.sleep(self.Timer)
    
  def resume(self):
    self.pause = False
  def pause(self):
    self.pause = True
  def abort():
    #Safely abort -> Do not move, turn off heaters, turn set points to zero.
    self.systemModel[self.ReactorID]['temperature_controller'].setTemperature(0)
    
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
    #self.Timer
    #self.coolTemp
    #self.reactPosition
  def run(self):
    self.steps=["Starting react operation","Moving to reaction position","Heating reactor","Waiting for reaction","Cooling reactor"]
    self.doNext()
    self.setReactorPosition()
    self.doNext()
    self.setTemp()
    self.doNext()
    self.startHeating()
    self.timeDelay()
    self.doNext()
    self.setCool()
    self.doNext()
    
  def setReactorPosition(self):
    self.systemModel[self.ReactorID]['motion'].setPosition(ZDOWN)
    self.waitForCondition(self.systemModel[self.ReactorID]['motion'].getCurrentPosition,ZDOWN,EQUAL)
    self.systemModel[self.ReactorID]['motion'].setPosition(self.reactPosition)
    self.waitForCondition(self.systemModel[self.ReactorID]['motion'].getCurrentPosition,self.reactPosition,EQUAL)
    self.systemModel[self.ReactorID]['motion'].setPosition(ZUP)
    self.waitForCondition(self.systemModel[self.ReactorID]['motion'].getPosition,ZUP,EQUAL)

  def getTemperatureController(): #Do we need this if we have the entire system model at our disposal?
    return self.systemModel[self.ReactorID]['temperature_controller']
  
  def setTemp(self):
    self.systemModel[self.ReactorID]['temperature_controller'].setTemperature(self.Temp)
    self.waitForCondition(self.systemModel[self.ReactorID]['temperature_controller'].getCurrentTemperature,self.Temp,GREATER)
   
  def setCool(self):
    self.systemModel[self.ReactorID]['temperature_controller'].setHeaterState(OFF)
    self.waitForCondition(self.systemModel[self.ReactorID]['temperature_controller'].getHeaterState,OFF,EQUAL)
    self.systemModel[self.ReactorID]['cooling_system'].setCooling(ON)
    self.waitForCondition(self.systemModel[self.ReactorID]['cooling_system'].getCooling,ON,EQUAL)
    self.waitForCondition(self.systemModel[self.ReactorID]['temperature_controller'].getTemperature(),self.coolTemp) 
    self.systemModel[self.ReactorID]['cooling_system'].setCooling(OFF)
    self.waitForCondition(self.systemModel[self.ReactorID]['cooling_system'].getCooling,OFF,EQUAL)

class AddReagent(UnitOperation):
  def __init__(self,systemModel,params):
    UnitOperation.__init__(self,systemModel)
    self.params = params #Should have parameters listed below
    #self.ReactorID
    #self.ReagentID
    #self.reactPosition

  def run(self):
    self.steps=["Starting add reagent operation","Moving to addition position","Adding reagent","Removing empty vial"]
    self.doNext()
    self.setReactorPosition()
    self.doNext()
    self.setGripperPlace()
    self.timeDelay()
    self.doNext()
    self.setGripperRemove()
    self.doNext()
  
  def setReactorPosition(self):
    self.systemModel[self.ReactorID]['motion'].setPosition(ZDOWN)
    self.waitForCondition(self.systemModel[self.ReactorID]['motion'].getCurrentPosition,ZDOWN,EQUAL)
    self.systemModel[self.ReactorID]['motion'].setPosition(self.reagentPosition)
    self.waitForCondition(self.systemModel[self.ReactorID]['motion'].getCurrentPosition,self.reagentPosition,EQUAL)
    self.systemModel[self.ReactorID]['motion'].setPosition(ZUP)
    self.waitForCondition(self.systemModel[self.ReactorID]['motion'].getPosition,ZUP,EQUAL)

  def setGripperPlace():
    self.systemModel[self.Gripper].setPosition(ZUP)
    self.waitForCondition(self.systemModel[self.Gripper].getPosition,ZUP,EQUAL)
    self.systemModel[self.Gripper].setCoordinate(self.ReagentID)
    self.waitForCondition(self.systemModel[self.Gripper].getCoordinate,self.ReagentID,EQUAL)
    self.systemModel[self.Gripper].setPosition(ZDOWN)
    self.waitForCondition(self.systemModel[self.Gripper].getPosition,ZDOWN,EQUAL)
    self.systemModel[self.Gripper].setGripperState(GRIP)
    self.waitForCondition(self.systemModel[self.Gripper].getGripperState,GRIP,EQUAL)
    self.systemModel[self.Gripper].setPosition(ZUP)
    self.waitForCondition(self.systemModel[self.Gripper].getPosition,ZUP,EQUAL)
    self.systemModel[self.Gripper].setCoordinate(self.reactPosition)
    self.waitForCondition(self.systemModel[self.Gripper].getCoordinate,self.reactPosition,EQUAL)
    self.systemModel[self.Gripper].setPosition(ZDOWN)
    self.waitForCondition(self.systemModel[self.Gripper].getPosition,ZDOWN,EQUAL)
    
  def setGripperRemove():
    self.waitForCondition(self.systemModel[self.Gripper].getCoordinate,self.reactPosition,EQUAL)#Make sure we are in the right location.
    self.waitForCondition(self.systemModel[self.Gripper].getPosition,ZDOWN,EQUAL)#Make sure we are in the down position.
    self.systemModel[self.Gripper].setGripperState(GRIP)
    self.waitForCondition(self.systemModel[self.Gripper].getGripperState,GRIP,EQUAL)
    self.systemModel[self.Gripper].setPosition(ZUP)
    self.waitForCondition(self.systemModel[self.Gripper].getPosition,ZUP,EQUAL)
    self.systemModel[self.Gripper].setCoordinate(self.ReagentID)
    self.waitForCondition(self.systemModel[self.Gripper].getCoordinate,self.ReagentID,EQUAL)
    self.systemModel[self.Gripper].setPosition(ZDOWN)
    self.waitForCondition(self.systemModel[self.Gripper].getPosition,ZDOWN,EQUAL)
    self.systemModel[self.Gripper].setGripperState(UNGRIP)
    self.waitForCondition(self.systemModel[self.Gripper].getGripperState,UNGRIP,EQUAL)
    

class Evaporate(UnitOperation):
  def __init__(self,systemModel,params):
    UnitOperation.__init__(self,systemModel)
    self.params = params #Should have parameters listed below
    #self.ReactorID
    #self.Temp
    #self.Timer
    #self.coolTemp
  def run(self):
    self.steps=["Starting evaporate operation","Moving to evaporation position","Setting heater set point","Heating reactor","Waiting for evaporation","Cooling reactor"]
    self.doNext()
    self.setReactorPosition()
    self.doNext()
    self.setTemp()
    self.doNext()
    self.startHeating()
    self.timeDelay()
    self.doNext()
    self.setCool()
    self.doNext()
  
  def setReactorPosition(self):
    self.systemModel[self.ReactorID]['motion'].setPosition(ZDOWN)
    self.waitForCondition(self.systemModel[self.ReactorID]['motion'].getCurrentPosition,ZDOWN,EQUAL)
    self.systemModel[self.ReactorID]['motion'].setPosition(XEVAPORATE)
    self.waitForCondition(self.systemModel[self.ReactorID]['motion'].getCurrentPosition,XEVAPORATE,EQUAL)
    self.systemModel[self.ReactorID]['motion'].setPosition(ZUP)
    self.waitForCondition(self.systemModel[self.ReactorID]['motion'].getPosition,ZUP,EQUAL)

  def getTemperatureController(): #Not sure why we need this?
    return self.systemModel[self.ReactorID]['temperature_controller']
    
  def setTemp(self):
    self.systemModel[self.ReactorID]['temperature_controller'].setSetPoint(self.Temp)
    self.waitForCondition(self.systemModel[self.ReactorID]['temperature_controller'].getSetPoint,self.Temp,GREATER)
    
  def startHeating(self):
    self.systemModel[self.ReactorID]['temperature_controller'].setHeaterState(ON)
    self.waitForCondition(self.systemModel[self.ReactorID]['temperature_controller'].getHeaterState,ON,EQUAL)
    self.waitForCondition(self.systemModel[self.ReactorID]['temperature_controller'].getCurrentTemperature,self.Temp,GREATER)
  
  def setCool(self):
    self.systemModel[self.ReactorID]['temperature_controller'].setHeaterState(OFF)
    self.waitForCondition(self.systemModel[self.ReactorID]['temperature_controller'].getHeaterState,OFF,EQUAL)
    self.systemModel[self.ReactorID]['cooling_system'].setCooling(ON)
    self.waitForCondition(self.systemModel[self.ReactorID]['cooling_system'].getCooling,ON,EQUAL)
    self.waitForCondition(self.systemModel[self.ReactorID]['temperature_controller'].getTemperature(),self.coolTemp) 
    self.systemModel[self.ReactorID]['cooling_system'].setCooling(OFF)
    self.waitForCondition(self.systemModel[self.ReactorID]['cooling_system'].getCooling,OFF,EQUAL)
    
  def getTemp(self):
    self.systemModel[self.ReactorID]['temperature_controller'].getCurrentTemperature()
    
  def timeDelay(self):
    self.timeDelay(self.Time)
    
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
    self.systemModel[self.ReactorID]['motion'].setPosition(ZDOWN)
    self.waitForCondition(self.systemModel[self.ReactorID]['motion'].getCurrentPosition,ZDOWN,EQUAL)
    self.systemModel[self.ReactorID]['motion'].setPosition(XINSTALL)
    self.waitForCondition(self.systemModel[self.ReactorID]['motion'].getCurrentPosition,XINSTALL,EQUAL)
    self.systemModel[self.ReactorID]['motion'].setPosition(ZUP)
    self.waitForCondition(self.systemModel[self.ReactorID]['motion'].getPosition,ZUP,EQUAL)
    
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
    self.systemModel[self.ReactorID]['motion'].setPosition(ZDOWN)
    self.waitForCondition(self.systemModel[self.ReactorID]['motion'].getCurrentPosition,ZDOWN,EQUAL)
    self.systemModel[self.ReactorID]['motion'].setPosition(XTRANSFER)
    self.waitForCondition(self.systemModel[self.ReactorID]['motion'].getCurrentPosition,XTRANSFER,EQUAL)
    self.systemModel[self.ReactorID]['motion'].setPosition(ZUP)
    self.waitForCondition(self.systemModel[self.ReactorID]['motion'].getPosition,ZUP,EQUAL)
    

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
    self.systemModel[self.ReactorID]['motion'].setPosition(ZDOWN)
    self.waitForCondition(self.systemModel[self.ReactorID]['motion'].getCurrentPosition,ZDOWN,EQUAL)
    self.systemModel[self.ReactorID]['motion'].setPosition(XTRANSFER)
    self.waitForCondition(self.systemModel[self.ReactorID]['motion'].getCurrentPosition,XTRANSFER,EQUAL)
    self.systemModel[self.ReactorID]['motion'].setPosition(ZUP)
    self.waitForCondition(self.systemModel[self.ReactorID]['motion'].getPosition,ZUP,EQUAL)
  
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
    #self.transferReactorID
    
  def run(self):
    self.steps=["Starting Transfer operation","Moving to transfer position","Transferring product"]
    self.doNext()
    self.setReactorPosition()
    self.doNext()
    self.setTransferReactorPosition()
    self.startTransfer()
    self.doNext()
  
  def setReactorPosition(self):
    self.systemModel[self.ReactorID]['motion'].setPosition(ZDOWN)
    self.waitForCondition(self.systemModel[self.ReactorID]['motion'].getCurrentPosition,ZDOWN,EQUAL)
    self.systemModel[self.ReactorID]['motion'].setPosition(XTRANSFER)
    self.waitForCondition(self.systemModel[self.ReactorID]['motion'].getCurrentPosition,XTRANSFER,EQUAL)
    self.systemModel[self.ReactorID]['motion'].setPosition(ZUP)
    self.waitForCondition(self.systemModel[self.ReactorID]['motion'].getPosition,ZUP,EQUAL)
    
  def setTransferReactorPosition(self):
    self.systemModel[self.transferReactorID]['motion'].setPosition(ZDOWN)
    self.waitForCondition(self.systemModel[self.transferReactorID]['motion'].getCurrentPosition,ZDOWN,EQUAL)
    self.systemModel[self.transferReactorID]['motion'].setPosition(XADDREAGENT)
    self.waitForCondition(self.systemModel[self.transferReactorID]['motion'].getCurrentPosition,XADDREAGENT,EQUAL)
    self.systemModel[self.transferReactorID]['motion'].setPosition(ZUP)
    self.waitForCondition(self.systemModel[self.transferReactorID]['motion'].getPosition,ZUP,EQUAL)

  def startTransfer(self):
    self.systemModel[self.ReactorID]['transfer'].setTransfer(self.transferPosition)
    
    self.waitForCondition(self.systemModel[self.ReactorID]['transfer'].getTransfer,self.transferPosition,,EQAL)
 
class UserInput(UnitOperation):
  def __init__(self,systemModel,params):
    UnitOperation.__init__(self,systemModel)
    self.params = params #Should have parameters listed below
    #self.userMessage
    #self.isCheckbox
    
  def run(self):
    self.steps=["Starting User Input operation","Waiting for OK"]
    self.doNext()
    self.setMessageBox()
    self.doNext()
    
  def setMessageBox(self):
    self.waitForUser = True
    self.waitForCondition(self.getUserInput,True)
    
  def getUserInput(self):
    return not(self.waitForUser)
    
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
    self.systemModel[self.ReactorID]['motion'].setPosition(ZDOWN)
    self.waitForCondition(self.systemModel[self.ReactorID]['motion'].getCurrentPosition,ZDOWN,EQUAL)
    self.systemModel[self.ReactorID]['motion'].setPosition(XRADIATION)
    self.waitForCondition(self.systemModel[self.ReactorID]['motion'].getCurrentPosition,XRADIATION,EQUAL)
    self.systemModel[self.ReactorID]['motion'].setPosition(ZUP)
    self.waitForCondition(self.systemModel[self.ReactorID]['motion'].getPosition,ZUP,EQUAL)

  def getRadiation(self):
    self.systemModel[self.ReactorID]['radiation_detector'].getCalibratedReading()
    self.waitForCondition(self.systemModel[self.ReactorID]['radiation_detector'].getCalibratedReading,self.calibrationCoefficient,GREATER)
    
def test():
  react1 = React()
  react1.run()

    
if __name__=="__main__":
    test()