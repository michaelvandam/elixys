"""Unit operations

Elixys Unit Operations
"""
import Thread from threading

#Z Positions
UP = "UP"
DOWN = "DOWN"

#Reactor X Positions
REACT_A = "REACTA"
REACT_B = "REACTB"
INSTALL = "INSTALL"
TRANSFER = "TRANSFER"
RADIATION = "RADIATION"
EVAPORATE = "EVAPORATE"
ADDREAGENT = "ADDREAGENT"
VIALREMOVE = "VIALREMOVE"
ON = 1
OFF = 0

#Robot Coordinate positions:
LOAD_A = "LOAD_A"
LOAD_B = "LOAD_B"
VAIL_1 = "VIAL_1"
VIAL_2 = "VIAL_2"
VIAL_3 = "VIAL_3"
VIAL_4 = "VIAL_4"
VIAL_5 = "VIAL_5"
VIAL_6 = "VIAL_6"
VIAL_7 = "VIAL_7"
VIAL_8 = "VIAL_8"

#Comparators for 'waitForCondition' function
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
      self.paused()
    elif self.steps:
      try:
        self.currentStep = self.steps.pop(0) #Removes step from list, sets next step.
        self.stepCounter += 1 
      except:
        print("Error setting next step in UnitOperations.run()") # This will be an error log
    elif self.steps == None:
      print("ERROR: Self.steps does not exist.")# This will be an error log
    elif len(self.steps)==0:
      self.isRunning = False
      print "unit operation complete"
    else:
      print("ERROR: Occurred in UnitOperation.doNext() call.")# This will be an error log
      
      
  def waitForCondition(function,condition,comparator):
    if comparator == EQUAL:
      if not(function() == condition):
        return False
    elif comparator == GREATER:
      if not(function() >= condition):
        return False
    elif comparator == LESS:
      if not(function() <= condition):
        return False
    else:
      print "Error"
        return False
    return True
    
  def timeDelay(self):
    time.sleep(self.Timer)
    
  def setUnpause(self):
    self.pause = False
  def setPause(self):
    self.pause = True
  def paused(self):
    while self.pause:
      pass
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
    self.setStirring()
    self.startHeating()
    self.timeDelay()
    self.doNext()
    self.setCool()
    self.doNext()

  def setStirring(self):
    self.systemModel[self.ReactorID]['stir_motor'].setSpeed(self.stirSpeed) #Set analog value on PLC
    self.waitForCondition(self.systemModel[self.ReactorID]['stir_motor'].getCurrentSpeed,self.stirSpeed,EQUAL) #Read analog value from PLC... should be equal
    
  def setReactorPosition(self):
    if not(self.waitForCondition(self.systemModel[self.ReactorID]['motion'].getCurrentXPosition,self.reactPosition,EQUAL)):
      self.systemModel[self.ReactorID]['motion'].setZPosition(DOWN)
      self.waitForCondition(self.systemModel[self.ReactorID]['motion'].getCurrentZPosition,DOWN,EQUAL)
      self.systemModel[self.ReactorID]['motion'].setXPosition(self.reactPosition)
      self.waitForCondition(self.systemModel[self.ReactorID]['motion'].getCurrentXPosition,self.reactPosition,EQUAL)
      self.systemModel[self.ReactorID]['motion'].setZPosition(UP)
      self.waitForCondition(self.systemModel[self.ReactorID]['motion'].getCurrentZPosition,UP,EQUAL)
    else: #We're in the right position, check if we're sealed.
      if not(self.waitForCondition(self.systemModel[self.ReactorID]['motion'].getCurrentZPosition,UP,EQUAL)):
        self.systemModel[self.ReactorID]['motion'].setZPosition(UP)
        self.waitForCondition(self.systemModel[self.ReactorID]['motion'].getCurrentZPosition,UP,EQUAL)
      else:
        pass #We're already in the right position and sealed.

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
    #self.reagentLoadPosition

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
    if not(self.waitForCondition(self.systemModel[self.ReactorID]['motion'].getCurrentXPosition,self.reagentPosition,EQUAL)):
      self.systemModel[self.ReactorID]['motion'].setZPosition(DOWN)
      self.waitForCondition(self.systemModel[self.ReactorID]['motion'].getCurrentZPosition,DOWN,EQUAL)
      self.systemModel[self.ReactorID]['motion'].setXPosition(self.reagentPosition)
      self.waitForCondition(self.systemModel[self.ReactorID]['motion'].getCurrentXPosition,self.reagentPosition,EQUAL)
      self.systemModel[self.ReactorID]['motion'].setZPosition(UP)
      self.waitForCondition(self.systemModel[self.ReactorID]['motion'].getCurrentZPosition,UP,EQUAL)
    else: #We're in the right position, check if we're sealed.
      if not(self.waitForCondition(self.systemModel[self.ReactorID]['motion'].getCurrentZPosition,UP,EQUAL)):
        self.systemModel[self.ReactorID]['motion'].setZPosition(UP)
        self.waitForCondition(self.systemModel[self.ReactorID]['motion'].getCurrentZPosition,UP,EQUAL)
      else:
        pass #We're already in the right position and sealed.

  def setGripperPlace():
    if self.waitForCondition(self.systemModel[self.Gripper].getGripperState,GRIP,EQUAL):
      if self.waitForCondition(self.systemModel[self.Gripper].getCurrentZPosition,DOWN,EQUAL):
        if (self.waitForCondition(self.systemModel[self.Gripper].getCoordinate,LOAD_A,EQUAL) OR self.waitForCondition(self.systemModel[self.Gripper].getCoordinate,LOAD_B,EQUAL):
          #We are in the load position, we should not be here. Error.
          print "ERROR: In load position, calling setGripperPlace()"
        else:
          #We are gripped and down, just ungrip?
          print "ERROR: setGripperPlace() called while already gripped in down position."
      else:
        #Error, why are we already gripped and not in a down position? 
        print "ERROR: setGripperPlace() called while already gripped in raised position."
    if not(self.waitForCondition(self.systemModel[self.Gripper].getCoordinate,self.ReagentID,EQUAL)):
      self.systemModel[self.Gripper].setZPosition(UP)
      self.waitForCondition(self.systemModel[self.Gripper].getCurrentZPosition,UP,EQUAL)
      self.systemModel[self.Gripper].setCoordinate(self.ReagentID)
      self.waitForCondition(self.systemModel[self.Gripper].getCoordinate,self.ReagentID,EQUAL)
      self.systemModel[self.Gripper].setZPosition(DOWN)
      self.waitForCondition(self.systemModel[self.Gripper].getCurrentZPosition,DOWN,EQUAL)
      self.systemModel[self.Gripper].setGripperState(GRIP)
      self.waitForCondition(self.systemModel[self.Gripper].getGripperState,GRIP,EQUAL)
    else: #We're in the right position, make sure we're down on the vial and grip it.
      self.systemModel[self.Gripper].setZPosition(DOWN)
      self.waitForCondition(self.systemModel[self.Gripper].getCurrentZPosition,DOWN,EQUAL)
      self.systemModel[self.Gripper].setGripperState(GRIP)
      self.waitForCondition(self.systemModel[self.Gripper].getGripperState,GRIP,EQUAL)
    #Regardless of above, when all is said and done, we want to move up and over to the position where the vial should go.
    self.systemModel[self.Gripper].setZPosition(UP)
    self.waitForCondition(self.systemModel[self.Gripper].getCurrentZPosition,UP,EQUAL)
    self.systemModel[self.Gripper].setCoordinate(self.reagentLoadPosition)
    self.waitForCondition(self.systemModel[self.Gripper].getCoordinate,self.reagentLoadPosition,EQUAL)
    self.systemModel[self.Gripper].setZPosition(DOWN)
    self.waitForCondition(self.systemModel[self.Gripper].getCurrentZPosition,DOWN,EQUAL)
    
  def setGripperRemove():
    if self.waitForCondition(self.systemModel[self.Gripper].getCoordinate,self.reagentLoadPosition,EQUAL):
      if self.waitForCondition(self.systemModel[self.Gripper].getCurrentZPosition,DOWN,EQUAL):
        self.systemModel[self.Gripper].setGripperState(GRIP)
        self.waitForCondition(self.systemModel[self.Gripper].getGripperState,GRIP,EQUAL)
        self.systemModel[self.Gripper].setZPosition(UP)
        self.waitForCondition(self.systemModel[self.Gripper].getCurrentZPosition,UP,EQUAL)
        self.systemModel[self.Gripper].setCoordinate(self.ReagentID)
        self.waitForCondition(self.systemModel[self.Gripper].getCoordinate,self.ReagentID,EQUAL)
        self.systemModel[self.Gripper].setZPosition(DOWN)
        self.waitForCondition(self.systemModel[self.Gripper].getCurrentZPosition,DOWN,EQUAL)
        self.systemModel[self.Gripper].setGripperState(UNGRIP)
        self.waitForCondition(self.systemModel[self.Gripper].getGripperState,UNGRIP,EQUAL)
        self.systemModel[self.Gripper].setZPosition(UP)
        self.waitForCondition(self.systemModel[self.Gripper].getCurrentZPosition,UP,EQUAL)
        self.systemModel[self.Gripper].setCoordinate(HOME)
        self.waitForCondition(self.systemModel[self.Gripper].getCoordinate,HOME,EQUAL)
      else:
        print "Gripper in correct position for removal, but not in down position."
    else:
      print "Gripper not in correct position for removal when setGripperRemove() called."

class Evaporate(UnitOperation):
  def __init__(self,systemModel,params):
    UnitOperation.__init__(self,systemModel)
    self.params = params #Should have parameters listed below
    #self.ReactorID
    #self.Temp
    #self.Timer
    #self.coolTemp
    #self.stirSpeed
    
  def run(self):
    self.doNext()
    self.setReactorPosition()
    self.doNext()
    self.setTemp()
    self.doNext()
    startVacuum()
    self.startStirring()
    self.startHeating()
    self.timeDelay()
    self.doNext()
    self.setCool()
    self.stopStirring()
    stopVacuum()
    self.doNext()
    
  def startStirring(self):
    self.systemModel[self.ReactorID]['stir_motor'].setSpeed(self.stirSpeed) #Set analog value on PLC
    self.waitForCondition(self.systemModel[self.ReactorID]['stir_motor'].getCurrentSpeed,self.stirSpeed,EQUAL) #Read analog value from PLC... should be equal
  
  def stopStirring(self):
    self.systemModel[self.ReactorID]['stir_motor'].setSpeed(OFF)
    self.waitForCondition(self.systemModel[self.ReactorID]['stir_motor'].getCurrentSpeed,OFF,EQUAL)
    
  def startVacuum(self):
    self.systemModel[self.ReactorID]['vacuum'].setVacuum(ON) #Set analog value on PLC
    self.waitForCondition(self.systemModel[self.ReactorID]['vacuum'].getVacuum,OFF,EQUAL) #Read analog value from PLC... should be equal
  
  def stopSVacuum(self):
    self.systemModel[self.ReactorID]['vacuum'].setVacuum(OFF)
    self.waitForCondition(self.systemModel[self.ReactorID]['vacuum'].getVacuum(OFF),ZERO,EQUAL)
  
  def setReactorPosition(self):
    if not(self.waitForCondition(self.systemModel[self.ReactorID]['motion'].getCurrentXPosition,EVAPORATE,EQUAL)):
      self.systemModel[self.ReactorID]['motion'].setZPosition(DOWN)
      self.waitForCondition(self.systemModel[self.ReactorID]['motion'].getCurrentXPosition,DOWN,EQUAL)
      self.systemModel[self.ReactorID]['motion'].setXPosition(EVAPORATE)
      self.waitForCondition(self.systemModel[self.ReactorID]['motion'].getCurrentXPosition,EVAPORATE,EQUAL)
      self.systemModel[self.ReactorID]['motion'].setZPosition(UP)
      self.waitForCondition(self.systemModel[self.ReactorID]['motion'].getCurrentZPosition,UP,EQUAL)
    else: #We're in the right position, check if we're sealed.
      if not(self.waitForCondition(self.systemModel[self.ReactorID]['motion'].getCurrentZPosition,UP,EQUAL)):
        self.systemModel[self.ReactorID]['motion'].setZPosition(UP)
        self.waitForCondition(self.systemModel[self.ReactorID]['motion'].getCurrentZPosition,UP,EQUAL)
      else:
        pass #We're already in the right position and sealed.

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
    if not(self.waitForCondition(self.systemModel[self.ReactorID]['motion'].getCurrentXPosition,INSTALL,EQUAL)):
      self.systemModel[self.ReactorID]['motion'].setZPosition(DOWN)
      self.waitForCondition(self.systemModel[self.ReactorID]['motion'].getCurrentZPosition,DOWN,EQUAL)
      self.systemModel[self.ReactorID]['motion'].setXPosition(INSTALL)
      self.waitForCondition(self.systemModel[self.ReactorID]['motion'].getCurrentXPosition,INSTALL,EQUAL)
      self.systemModel[self.ReactorID]['motion'].setZPosition(UP)
      self.waitForCondition(self.systemModel[self.ReactorID]['motion'].getCurrentZPosition,UP,EQUAL)
    else: #We're in the right position, check if we're sealed.
      if not(self.waitForCondition(self.systemModel[self.ReactorID]['motion'].getCurrentZPosition,UP,EQUAL)):
        self.systemModel[self.ReactorID]['motion'].setZPosition(UP)
        self.waitForCondition(self.systemModel[self.ReactorID]['motion'].getCurrentZPosition,UP,EQUAL)
      else:
        pass #We're already in the right position and sealed.
    
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
    if not( self.waitForCondition(self.systemModel[self.ReactorID]['motion'].getCurrentXPosition,TRANSFER,EQUAL)):
      self.systemModel[self.ReactorID]['motion'].setZPosition(DOWN)
      self.waitForCondition(self.systemModel[self.ReactorID]['motion'].getCurrentZPosition,DOWN,EQUAL)
      self.systemModel[self.ReactorID]['motion'].setXPosition(TRANSFER)
      self.waitForCondition(self.systemModel[self.ReactorID]['motion'].getCurrentXPosition,TRANSFER,EQUAL)
      self.systemModel[self.ReactorID]['motion'].setZPosition(UP)
      self.waitForCondition(self.systemModel[self.ReactorID]['motion'].getCurrentZPosition,UP,EQUAL)
    else: #We're in the right position, check if we're sealed.
      if not(self.waitForCondition(self.systemModel[self.ReactorID]['motion'].getCurrentZPosition,UP,EQUAL)):
        self.systemModel[self.ReactorID]['motion'].setZPosition(UP)
        self.waitForCondition(self.systemModel[self.ReactorID]['motion'].getCurrentZPosition,UP,EQUAL)
      else:
        pass #We're already in the right position and sealed.

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
    if not(self.waitForCondition(self.systemModel[self.ReactorID]['motion'].getCurrentXPosition,TRANSFER,EQUAL)):
      self.systemModel[self.ReactorID]['motion'].setZPosition(DOWN)
      self.waitForCondition(self.systemModel[self.ReactorID]['motion'].getCurrentZPosition,DOWN,EQUAL)
      self.systemModel[self.ReactorID]['motion'].setXPosition(TRANSFER)
      self.waitForCondition(self.systemModel[self.ReactorID]['motion'].getCurrentXPosition,TRANSFER,EQUAL)
      self.systemModel[self.ReactorID]['motion'].setZPosition(UP)
      self.waitForCondition(self.systemModel[self.ReactorID]['motion'].getCurrentZPosition,UP,EQUAL)
    else: #We're in the right position, check if we're sealed.
      if not(self.waitForCondition(self.systemModel[self.ReactorID]['motion'].getCurrentZPosition,UP,EQUAL)):
        self.systemModel[self.ReactorID]['motion'].setZPosition(UP)
        self.waitForCondition(self.systemModel[self.ReactorID]['motion'].getCurrentZPosition,UP,EQUAL)
      else:
        pass #We're already in the right position and sealed.
  
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
    if not(self.waitForCondition(self.systemModel[self.ReactorID]['motion'].getCurrentXPosition,TRANSFER,EQUAL)):
      self.systemModel[self.ReactorID]['motion'].setZPosition(DOWN)
      self.waitForCondition(self.systemModel[self.ReactorID]['motion'].getCurrentZPosition,DOWN,EQUAL)
      self.systemModel[self.ReactorID]['motion'].setXPosition(TRANSFER)
      self.waitForCondition(self.systemModel[self.ReactorID]['motion'].getCurrentXPosition,TRANSFER,EQUAL)
      self.systemModel[self.ReactorID]['motion'].setZPosition(UP)
      self.waitForCondition(self.systemModel[self.ReactorID]['motion'].getCurrentZPosition,UP,EQUAL)
    else: #We're in the right position, check if we're sealed.
      if not(self.waitForCondition(self.systemModel[self.ReactorID]['motion'].getCurrentZPosition,UP,EQUAL)):
        self.systemModel[self.ReactorID]['motion'].setZPosition(UP)
        self.waitForCondition(self.systemModel[self.ReactorID]['motion'].getCurrentZPosition,UP,EQUAL)
      else:
        pass #We're already in the right position and sealed.
    
  def setTransferReactorPosition(self):
    if not(self.waitForCondition(self.systemModel[self.transferReactorID]['motion'].getCurrentXPosition,ADDREAGENT,EQUAL)):
      self.systemModel[self.transferReactorID]['motion'].setZPosition(DOWN)
      self.waitForCondition(self.systemModel[self.transferReactorID]['motion'].getCurrentZPosition,DOWN,EQUAL)
      self.systemModel[self.transferReactorID]['motion'].setXPosition(ADDREAGENT)
      self.waitForCondition(self.systemModel[self.transferReactorID]['motion'].getCurrentXPosition,ADDREAGENT,EQUAL)
      self.systemModel[self.transferReactorID]['motion'].setZPosition(UP)
      self.waitForCondition(self.systemModel[self.transferReactorID]['motion'].getCurrentZPosition,UP,EQUAL)
    else: #We're in the right position, check if we're sealed.
      if not(self.waitForCondition(self.systemModel[self.ReactorID]['motion'].getCurrentZPosition,UP,EQUAL)):
        self.systemModel[self.ReactorID]['motion'].setZPosition(UP)
        self.waitForCondition(self.systemModel[self.ReactorID]['motion'].getCurrentZPosition,UP,EQUAL)
      else:
        pass #We're already in the right position and sealed.

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
    self.waitForCondition(self.getUserInput,True,EQUAL)
    
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
    if not(self.waitForCondition(self.systemModel[self.ReactorID]['motion'].getCurrentXPosition,RADIATION,EQUAL)):
      self.systemModel[self.ReactorID]['motion'].setZPosition(DOWN)
      self.waitForCondition(self.systemModel[self.ReactorID]['motion'].getCurrentZPosition,DOWN,EQUAL)
      self.systemModel[self.ReactorID]['motion'].setXPosition(RADIATION)
      self.waitForCondition(self.systemModel[self.ReactorID]['motion'].getCurrentXPosition,RADIATION,EQUAL)
      self.systemModel[self.ReactorID]['motion'].setZPosition(UP)
      self.waitForCondition(self.systemModel[self.ReactorID]['motion'].getCurrentZPosition,UP,EQUAL)
    else: #We're in the right position, check if we're sealed.
      if not(self.waitForCondition(self.systemModel[self.ReactorID]['motion'].getCurrentZPosition,UP,EQUAL)):
        self.systemModel[self.ReactorID]['motion'].setZPosition(UP)
        self.waitForCondition(self.systemModel[self.ReactorID]['motion'].getCurrentZPosition,UP,EQUAL)
      else:
        pass #We're already in the right position and sealed.

  def getRadiation(self):
    self.systemModel[self.ReactorID]['radiation_detector'].getCalibratedReading()
    self.waitForCondition(self.systemModel[self.ReactorID]['radiation_detector'].getCalibratedReading,self.calibrationCoefficient,GREATER)
    
def test():
  react1 = React()
  react1.run()

    
if __name__=="__main__":
    test()