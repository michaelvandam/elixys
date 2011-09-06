"""Unit operations
Elixys Unit Operations
"""
## TO DO:
## MAKE list of all private variables
## UPDATE list of constants
##
import time
import threading

#Reactor X Positions
REACT_A    = 'React1'
REACT_B    = 'React2'
INSTALL    = 'Install'
TRANSFER   = 'Transfer'
RADIATION  = 'Radation'
EVAPORATE  = 'Evaporate'
ADDREAGENT = 'Add'
ENABLED    = 'Enabled'
DISABLED   = 'Disabled'
HOME = (3,3)
F18TRAP = (2,1,0)
#Set Stopcock 1 to Position 2
#Set Stopcock 2 to Position 1
F18ELUTE = (1,2,0)
#Set Stopcock 1 to Position 1
#Set Stopcock 2 to Position 2

ON = True
OFF = False

EVAPTEMP  = 'evapTemp'
EVAPTIME  = 'evapTime'
REACTORID = 'ReactorID'
REACTTEMP = 'reactTemp'
REACTTIME = 'reactTime'
COOLTEMP  = 'coolTemp'
STIRSPEED = 'stirSpeed'
REACTPOSITION = 'reactPosition'
REAGENTPOSITION = 'ReagentPosition'
REAGENTREACTORID = 'ReagentReactorID'
REAGENTLOADPOSITION = 'reagentLoadPosition'

STR   = 'str'
INT   = 'int'
FLOAT = 'float'

#Robot ReagentPosition positions:
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
EQUAL    = "="
NOTEQUAL = "!="
GREATER  = ">"
LESS     = "<"

class UnitOpError(Exception):
  def __init__(self, value):
    self.value = value
  def __str__(self):
    return repr(self.value)

    
class UnitOperation(threading.Thread):
  def __init__(self,systemModel):
    threading.Thread.__init__(self)
    self.time = time.time()
    self.params = {}
    self.paramsValidated = False
    self.paramsValid = False
    self.systemModel = systemModel.model
    self.currentStepNumber = 0
    self.currentStepDescription = ""
    self.delay = 50#50ms delay
    self.isRunning = False
    self.paused = False
    self.abort = False
    self.pausedLock = threading.Lock()

  def setParams(self,params): #Params come in as Dict, we can loop through and assign each 'key' to a variable. Eg. self.'key' = 'value'
    for paramname in params.keys():
      #print "\n%s:\n%s" % (paramname,params[paramname])
      if (paramname=="reactTemp"):
        self.reactTemp = params['reactTemp']
      if (paramname=="reactTime"):
        self.reactTime = params['reactTime']
      if (paramname=="evapTemp"):
        self.reactTemp = params['evapTemp']
      if (paramname=="evapTime"):
        self.reactTime = params['evapTime']
      if paramname=="coolTemp":
        self.coolTemp = params['coolTemp']
      if paramname=="ReactorID":
        self.ReactorID = params['ReactorID']
      if paramname=="ReagentReactorID":
        self.ReagentReactorID = params['ReagentReactorID']
      if paramname=="stirSpeed":
        self.stirSpeed = params['stirSpeed']
      if paramname=="isCheckbox":
        self.isCheckbox = params['isCheckbox']
      if paramname=="userMessage":
        self.userMessage = params['userMessage']
      if paramname=="description":
        self.description = params['description']
      if paramname=="stopcockPosition":
        self.stopcockPosition = params['stopcockPosition']
      if paramname=="transferReactorID":
        self.transferReactorID = params['transferReactorID']
      if paramname=="reagentLoadPosition":
        self.reagentLoadPosition = params['reagentLoadPosition']
      if paramname=="reactPosition":
        self.reactPosition = params['reactPosition']
      if paramname=="ReagentPosition":
        self.reagentPosition = params['ReagentPosition']
      if paramname=="trapTime":
        self.trapTime = params['trapTime']
      if paramname=="trapPressure":
        self.trapPressure = params['trapPressure']
      if paramname=="eluteTime":
        self.eluteTime = params['eluteTime']
      if paramname=="elutePressure":
        self.elutePressure = params['elutePressure']
  
  """def validateParams(self,currentParams,expectedParams):
    errorMessage = ""
    self.paramsValid = True
    for parameter in expectedParams:
      if not(parameter in currentParams):
        self.paramsValid = False
        errorMessage += "Parameter: \'%s\' was not set." % parameter
      else:
        if not(currentParams[parameter]):
          self.paramsValid = False
          errorMessage += "Parameter: \'%s\' was set to invalid value: \'%s\'." % (parameter,currentParams[parameter])
    self.paramsValidated = True
    return errorMessage"""
    
  def logError(self,error):
    """Logs an error."""
    print error
    
  def validateParams(self,userSetParams,expectedParamDict):
    """Validates parameters before starting unit operation"""
    errorMessage = ""
    self.paramsValid = True
    paramTypeInt = ""
    for parameter in expectedParamDict.keys():
      try:
        paramType = userSetParams[parameter].__class__.__name__
      except:
        pass
      if not(parameter in userSetParams): #Parameter not entered in CLI
        self.paramsValid = False
        errorMessage += "Parameter: \'%s\' was not set." % parameter
      elif (not((paramType) in (STR,INT,FLOAT)) and (userSetParams[parameter])): #Check for invalid value -- Including none and empty strings.
        self.paramsValid = False
        errorMessage += "Parameter: \'%s\' was set to invalid value: \'%s\'." % (parameter,userSetParams[parameter])
      else:
        if not(paramType == expectedParamDict[parameter]):
          valid = False
          if not(paramType == STR): #As long as it's not a string, check if float/int were mixed up.
            if (int(userSetParams[parameter]) == userSetParams[parameter]) and (expectedParamDict[parameter] == INT):
              valid = True
            if (float(userSetParams[parameter]) == userSetParams[parameter]) and (expectedParamDict[parameter] == FLOAT):
              valid = True
          if not(valid):
            self.paramsValid=False
            errorMessage += "Parameter: \'%s\' was set to invalid value: \'%s\'." % (parameter,userSetParams[parameter])
        if (paramType == STR):
          try:
            if (int(userSetParams[parameter])) and (expectedParamDict[parameter] == STR):
              self.paramsValid=False
              errorMessage += "Parameter: \'%s\' was set to invalid value: \'%s\'." % (parameter,userSetParams[parameter])
          except ValueError:
            pass    
    return errorMessage
    
  def beginNextStep(self,nextStepText = ""):
    #print nextStepText
    if self.paused:
      self.paused()
    if self.abort:
      self.abortOperation()
    if nextStepText:
      self.stepDescription = nextStepText
    self.currentStepNumber+=1
    self.setDescription()
  
  def setDescription(self,newDescription = ""):
    if newDescription:
      self.currentStepDescription = self.stepDescription+":"+newDescription
    else:
      self.currentStepDescription = self.stepDescription
  
  def setReactorPosition(self,reactorPosition,ReactorID=255):
    motionTimeout = 10 #How long to wait before erroring out.
    if (ReactorID==255):
      ReactorID = self.ReactorID
    if not(self.checkForCondition(self.systemModel[ReactorID]['Motion'].getCurrentRobotStatus,ENABLED,EQUAL)):
      self.systemModel[ReactorID]['Motion'].setEnableReactorRobot()      
      self.waitForCondition(self.systemModel[ReactorID]['Motion'].getCurrentRobotStatus,ENABLED,EQUAL,3)
    if not(self.checkForCondition(self.systemModel[ReactorID]['Motion'].getCurrentPosition,reactorPosition,EQUAL)):
      self.setDescription("Moving Reactor%s down." % ReactorID)
      self.systemModel[ReactorID]['Motion'].moveReactorDown()
      self.waitForCondition(self.systemModel[ReactorID]['Motion'].getCurrentReactorDown,True,EQUAL,motionTimeout)
      self.setDescription("Moving Reactor%s to position %s." % (ReactorID,reactorPosition))
      self.systemModel[ReactorID]['Motion'].moveToPosition(reactorPosition)
      self.waitForCondition(self.systemModel[ReactorID]['Motion'].getCurrentPosition,reactorPosition,EQUAL,motionTimeout)
      if not(reactorPosition==INSTALL):
        self.setDescription("Moving Reactor%s up." % ReactorID)
        self.systemModel[ReactorID]['Motion'].moveReactorUp()
        self.waitForCondition(self.systemModel[ReactorID]['Motion'].getCurrentReactorUp,True,EQUAL,motionTimeout)
      #Removed 'else' with duplicated code, this will work because we want it to disable regardless of position.
      self.systemModel[ReactorID]['Motion'].setDisableReactorRobot()
      self.waitForCondition(self.systemModel[ReactorID]['Motion'].getCurrentRobotStatus,DISABLED,EQUAL,3)

    else: #We're in the right position, check if we're sealed.
      if not(self.checkForCondition(self.systemModel[ReactorID]['Motion'].getCurrentReactorUp,True,EQUAL)):
        if not(reactorPosition==INSTALL):
          self.setDescription("Moving Reactor%s up." % ReactorID)
          self.systemModel[ReactorID]['Motion'].moveReactorUp()
          self.waitForCondition(self.systemModel[ReactorID]['Motion'].getCurrentReactorUp,True,EQUAL,motionTimeout)
          self.systemModel[ReactorID]['Motion'].setDisableReactorRobot()
          self.waitForCondition(self.systemModel[ReactorID]['Motion'].getCurrentRobotStatus,DISABLED,EQUAL,3)
        else:
          self.setDescription("Reactor%s in position %s." % (ReactorID,reactorPosition))
      else:
        self.setDescription("Reactor%s already in position %s." % (ReactorID,reactorPosition))
    
  def waitForCondition(self,function,condition,comparator,timeout): #Timeout in seconds, default to 3.
    startTime = time.time()
    self.delay = 500
    if comparator == EQUAL:
      while not(function() == condition):
        #print "%s Function %s == %s, expected %s" % (self.curTime(),str(function.__name__),str(function()),str(condition))
        self.stateCheckInterval(self.delay)
        if not(timeout == 65535):
          if self.isTimerExpired(startTime,timeout):
            print ("ERROR: waitForCondition call timed out on function:%s class:%s" % (function.__name__,function.im_class))
            break
    elif comparator == NOTEQUAL:
      while (function() == condition):
        #print "%s Function %s == %s, expected %s" % (self.curTime(),str(function.__name__),str(function()),str(condition))
        self.stateCheckInterval(self.delay)
        if not(timeout == 65535):
          if self.isTimerExpired(startTime,timeout):
            print ("ERROR: waitForCondition call timed out on function:%s class:%s" % (function.__name__,function.im_class))
            break
    elif comparator == GREATER:
      while not(function() >= condition):
        #print "%s Function %s == %s, expected %s" % (self.curTime(),str(function.__name__),str(function()),str(condition))
        self.stateCheckInterval(self.delay)
        if not(timeout == 65535):
          if self.isTimerExpired(startTime,timeout):
            print ("ERROR: waitForCondition call timed out on function:%s class:%s" % (function.__name__,function.im_class))
            break            
    elif comparator == LESS:
      while not(function() <=condition):
        #print "%s Function %s == %s, expected %s" % (self.curTime(),str(function.__name__),str(function()),str(condition))
        self.stateCheckInterval(self.delay)
        if not(timeout == 65535):
          if self.isTimerExpired(startTime,timeout):
            print ("ERROR: waitForCondition call timed out on function:%s class:%s" % (function.__name__,function.im_class))
            break
    else:
      print ("Error: Invalid comparator.")
    #print "%s Function %s == %s, expected %s" % (self.curTime(),str(function.__name__),str(function()),str(condition))
    
  def checkForCondition(self,function,condition,comparator):
    ret = False #Default False
    if comparator == EQUAL:
      if (function() == condition):
        ret=True
        #return True  #Changed for debug purposes
    elif comparator == GREATER:
      if (function() >= condition):
        ret=True
    elif comparator == LESS:
      if (function() <= condition):
        ret=True
    else:
      print ("Error: Invalid comparator.")
      ret=False
    #print "Function %s == %s, expected %s" % (str(function.__name__),str(function()),str(condition))  
    return ret
    
  def startTimer(self,timerLength): #In seconds
    print "%s Timer set to: %s" % (self.curTime(),self.formatTime(timerLength))
    timerStartTime = time.time()  #Create a time
    while not(self.isTimerExpired(timerStartTime,timerLength)):
      self.setDescription("Time remaining:%s" % self.formatTime(timerLength-(time.time()-timerStartTime)))
      self.stateCheckInterval(50) #Sleep 50ms between checks
    print "%s Timer finished." % (self.curTime())
    
  def isTimerExpired(self,startTime,length):
    if (length == 65535):
      return False
    if (time.time()-startTime >= length):
      return True
    return False
    
  def curTime(self):
    return time.strftime("%H:%M:%S", time.localtime())
    
  def formatTime(self,timeValue):
    hours = 0
    minutes = 0
    seconds = 0
    if timeValue >= 3600:
      hours = int(timeValue/3600)
      timeValue = timeValue % 3600 
    if timeValue >= 60:
      minutes = int(timeValue/60)
      seconds = timeValue % 60 
    if timeValue < 60:
      seconds = int(timeValue)
    if hours:
      return("%.2d:%.2d:%.2d" % (hours,minutes,seconds))
    elif minutes:
      return("00:%.2d:%.2d" % (minutes,seconds))
    else:
      return("00:00:%.2d" % seconds)
    
  def stateCheckInterval(self,interval): #interval = time in milliseconds, default to 50ms
    if interval:
      time.sleep(interval/1000.00) #If a value is set, use it, otherwise default. Divide by 1000.00 to get ms as a float.
    else:
      time.sleep(0.05)#default if delay = None or delay = 0

  def setPaused():
   # Acquire the lock, set the variable and release the lock
   self.pausedLock.acquire()
   self.paused = True
   self.pausedLock.release()

  def paused():
   # Acquire the lock before reading the variable
   self.pausedLock.acquire()

   # Pausing loop
   while self.paused:
    # Release the lock before sleeping and acquire again before reading the variable
    self.pausedLock.release()
    time.sleep(0.05)
    self.pausedLock.acquire()

   # Release the lock before returning
   self.pausedLock.release()

  def setUnpaused():
   # Acquire the lock, clear the variable and release the lock
   self.pausedLock.acquire()
   self.paused = False
   self.pausedLock.release()  
      
  def abortOperation(self,error):
    #Safely abort -> Do not move, turn off heaters, turn set points to zero.
    self.systemModel[self.ReactorID]['Thermocouple'].setSetPoint(OFF)
    self.setHeater(OFF)
    raise UnitOpError(error)
    
    
  def getTotalSteps(self):
    return self.steps #Integer
    
  def isRunning(self):
    return self.isRunning
    
  def getCurrentStepNumber(self):
    return self.currentStepNumber

  def getCurrentStep(self):
    return self.currentStepDescription

  def setStopcockPosition(self,stopcockPositions):
    for stopcock in range(1,(len(stopcockPositions)+1)):
      if (stopcockPositions[stopcock-1]==1) or (stopcockPositions[stopcock-1]==2):
        self.systemModel[self.ReactorID]['Stopcock'+str(stopcock)].setPosition(stopcockPositions[stopcock-1])       
        self.waitForCondition(self.systemModel[self.ReactorID]['Stopcock'+str(stopcock)].getPosition,stopcockPositions[stopcock-1],EQUAL,3) 

  def setHeater(self,heaterState):
    if heaterState == ON:
      self.systemModel[self.ReactorID]['Thermocouple'].setHeaterOn()
      self.waitForCondition(self.systemModel[self.ReactorID]['Thermocouple'].getHeaterOn,True,EQUAL,3)
      self.waitForCondition(self.systemModel[self.ReactorID]['Thermocouple'].getCurrentTemperature,self.reactTemp,GREATER,65535)
    elif heaterState == OFF:
      self.systemModel[self.ReactorID]['Thermocouple'].setHeaterOff()
      self.waitForCondition(self.systemModel[self.ReactorID]['Thermocouple'].getHeaterOn,False,EQUAL,3)
      

  def setTemp(self):
    self.systemModel[self.ReactorID]['Thermocouple'].setSetPoint(self.reactTemp)
    self.waitForCondition(self.systemModel[self.ReactorID]['Thermocouple'].getSetTemperature,self.reactTemp,EQUAL,3)

  def setCool(self):
    self.systemModel[self.ReactorID]['Thermocouple'].setHeaterOff()
    self.waitForCondition(self.systemModel[self.ReactorID]['Thermocouple'].getHeaterOn,False,EQUAL,3)
    self.systemModel['CoolingSystem'].setCoolingSystemOn(ON)
    self.waitForCondition(self.systemModel['CoolingSystem'].getCoolingSystemOn,ON,EQUAL,3)
    self.waitForCondition(self.systemModel[self.ReactorID]['Thermocouple'].getCurrentTemperature,self.coolTemp,LESS,65535) 
    self.systemModel['CoolingSystem'].setCoolingSystemOn(OFF)
    self.waitForCondition(self.systemModel['CoolingSystem'].getCoolingSystemOn,OFF,EQUAL,3)
    
  def setStirSpeed(self,stirSpeed):
    if (stirSpeed == OFF): #Fix issue with False being misinterpreted.
      stirSpeed = 0
    self.systemModel[self.ReactorID]['Stir'].setSpeed(stirSpeed) #Set analog value on PLC
    self.waitForCondition(self.systemModel[self.ReactorID]['Stir'].getCurrentSpeed,stirSpeed,EQUAL,10) #Read value from PLC memory... should be equal

  def setEvapValves(self,evapValvesSetting):
    if (evapValvesSetting):
      self.systemModel[self.ReactorID]['Valves'].setEvaporationValvesOpen(ON)
      self.waitForCondition(self.systemModel[self.ReactorID]['Valves'].getSetEvaporationValvesOpen,True,EQUAL,3)     
    else:
      self.systemModel[self.ReactorID]['Valves'].setEvaporationValvesOpen(OFF)
      self.waitForCondition(self.systemModel[self.ReactorID]['Valves'].getSetEvaporationValvesOpen,False,EQUAL,3)      
  
  def setReagentTransferValves(self,transferValvesSetting):
    if (transferValvesSetting):
      self.systemModel[self.ReactorID]['Valves'].setReagentTransferValve(self.reagentLoadPosition,ON) #set pressure on
      self.waitForCondition(self.systemModel[self.ReactorID]['Valves'].getSetReagentTransferValve,True,EQUAL,2)
    else:
      self.systemModel[self.ReactorID]['Valves'].setReagentTransferValve(self.reagentLoadPosition,OFF) #set pressure off
      self.waitForCondition(self.systemModel[self.ReactorID]['Valves'].getSetReagentTransferValve,False,EQUAL,2)
  
  def setPressureRegulator(self,regulator,pressureSetPoint,rampTime=0): #Time in seconds
    if (str(regulator) == '1') or (str(regulator) == 'PressureRegulator1'):
      self.pressureRegulator = 'PressureRegulator1'
    elif (str(regulator) == '2') or (str(regulator) == 'PressureRegulator2'):
      self.pressureRegulator = 'PressureRegulator2'
    if rampTime:
      currentPressure = self.systemModel[self.pressureRegulator].getSetPressure()
      rampPressure = currentPressure
      if (int(currentPressure/rampTime)>1):
        pressureStep = int(currentPressure/rampTime)
      else:
        pressureStep=1
      
      while (rampPressure<pressureSetPoint):
        rampPressure += pressureStep
        self.systemModel[self.pressureRegulator].setRegulatorPressure(rampPressure) #Set analog value on PLC
        self.waitForCondition(self.systemModel[self.pressureRegulator].getCurrentPressure,rampPressure,GREATER,3) #Read value from sensor... should be greater or equal   
      if (rampPressure >= pressureSetPoint):
        self.systemModel[self.pressureRegulator].setRegulatorPressure(pressureSetPoint)
        self.waitForCondition(self.systemModel[self.pressureRegulator].getSetPressure,pressureSetPoint-1,GREATER,3)
        #self.waitForCondition(self.systemModel[self.pressureRegulator].getCurrentPressure,pressureSetPoint,GREATER,3)
    else:
      self.systemModel[self.pressureRegulator].setRegulatorPressure(pressureSetPoint)
      self.waitForCondition(self.systemModel[self.pressureRegulator].getSetPressure,(pressureSetPoint-1),GREATER,3)
      #self.waitForCondition(self.systemModel[self.pressureRegulator].getCurrentPressure,pressureSetPoint,GREATER,3)
      
class React(UnitOperation):
  def __init__(self,systemModel,params):
    UnitOperation.__init__(self,systemModel)
    
    expectedParams = {REACTORID:STR,REACTTEMP:FLOAT,REACTTIME:INT,COOLTEMP:INT,REACTPOSITION:STR,STIRSPEED:INT}
    paramError = self.validateParams(params,expectedParams)
    if self.paramsValid:
      self.setParams(params)
    else:
      raise UnitOpError(paramError)
    #Should have parameters listed below:
    #self.ReactorID
    #self.reactTemp
    #self.reactTime
    #self.coolTemp
    #self.reactPosition
    #self.stirSpeed
  def run(self):
    try:
      self.beginNextStep("Starting React Operation")
      self.beginNextStep("Moving to position")
      self.setReactorPosition(self.reactPosition)#REACTA OR REACTB
      self.beginNextStep("Setting reactor Temperature")
      self.setTemp()
      self.beginNextStep("Starting stir motor")
      self.beginNextStep("Starting heater")
      self.setStirSpeed(self.stirSpeed)
      self.setHeater(ON)
      self.setDescription("Starting reaction timer")
      self.startTimer(self.reactTime)
      self.beginNextStep("Starting cooling")
      self.setHeater(OFF)
      self.setCool()
      self.setStirSpeed(OFF)
      self.beginNextStep("React Operation Complete")
    except Exception as e:
      print type(e)
      print e
      
"""
  def setParams(self,currentParams):
    expectedParams = ['ReactorID','reactTemp','reactTime','coolTemp','reactPosition','stirSpeed']
    self.paramsValid = True
    for parameter in expectedParams:
      if not(parameter in currentParams):
        self.paramsValid = False
        #Log Error
      self.paramsValidated = True
"""
    
class Move(UnitOperation):
  def __init__(self,systemModel,params):
    UnitOperation.__init__(self,systemModel)
    
    expectedParams = {REACTORID:STR,REACTPOSITION:STR}
    paramError = self.validateParams(params,expectedParams)
    if self.paramsValid:
      self.setParams(params)
    else:
      raise UnitOpError(paramError)
    #Should have parameters listed below:
    #self.ReactorID
    #self.reactPosition
  def run(self):
    try:
      self.beginNextStep("Starting Move Operation")
      self.beginNextStep("Moving to position")
      self.setReactorPosition(self.reactPosition)#REACTA OR REACTB
      self.beginNextStep("Move Operation Complete")
    except Exception as e:
      print type(e)
      print e
    
    
class AddReagent(UnitOperation):
  def __init__(self,systemModel,params):
    UnitOperation.__init__(self,systemModel)
    expectedParams = {REACTORID:STR,REAGENTREACTORID:STR,REAGENTPOSITION:INT,REAGENTLOADPOSITION:INT}
    paramError = self.validateParams(params,expectedParams)
    if self.paramsValid:
      self.setParams(params)
    else:
      raise UnitOpError(paramError)
		#Should have parameters listed below: 
    #self.ReactorID
    #self.ReagentReactorID
    #self.ReagentPosition
    #self.reagentLoadPosition

  def run(self):
    try:
      self.beginNextStep("Starting Add Reagent Operation")
      self.setPressureRegulator(2,5)
      self.beginNextStep("Moving to position")
      self.setReactorPosition(ADDREAGENT)
      self.beginNextStep("Moving vial to addition position")
      self.setReagentTransferValves(ON)# Turn on valves
      self.setGripperPlace()#Move reagent from it's home position to the addition position.
      self.setDescription("Adding reagent")
      time.sleep(10)#Dispense reagent
      self.beginNextStep("Removing vial from addition position")
      self.setGripperRemove()
      self.setReagentTransferValves(OFF)#Turn off valves
      self.beginNextStep("Add Reagent Operation Complete")
    except Exception as e:
      print type(e)
      print e
  
  """def setParams(self,currentParams):
    expectedParams = ['ReactorID','ReagentPosition','reagentLoadPosition']
    self.paramsValid = True
    for parameter in expectedParams:
      if not(parameter in currentParams):
        self.paramsValid = False
        #Log Error
      self.paramsValidated = True"""
    
  def setGripperPlace(self):
    if self.checkForCondition(self.systemModel['ReagentDelivery'].getSetGripperOpen,False,EQUAL):
      #we are not open. Error state.
      self.abortOperation("ERROR: setGripperPlace called while gripper was Closed. Operation aborted.") #Tell thread to kill itself in event of major error
    if self.checkForCondition(self.systemModel['ReagentDelivery'].getSetGripperUp,False,EQUAL):
      self.abortOperation("ERROR: setGripperPlace called while gripper was down. Operation aborted.") 
    
    #If we make it here, we are up and open. We want to move to ReagentPosition, then down, then close.
    self.systemModel['ReagentDelivery'].moveToReagentPosition(int(self.ReagentReactorID[-1]),self.reagentPosition) #Move Reagent Robot to position
    time.sleep(2)
    self.waitForCondition(self.systemModel['ReagentDelivery'].getCurrentPosition,(int(self.ReagentReactorID[-1]), self.reagentPosition, 0),EQUAL,5)
    self.systemModel['ReagentDelivery'].setMoveGripperDown() #Move Gripper down
    self.waitForCondition(self.systemModel['ReagentDelivery'].getSetGripperDown,True,EQUAL,2)
    time.sleep(2)#**Need sensor here
    self.systemModel['ReagentDelivery'].setMoveGripperClose() #Close Gripper
    self.waitForCondition(self.systemModel['ReagentDelivery'].getSetGripperClose,True,EQUAL,2)        
    time.sleep(2)#**Need sensor here
    
    #If we make it here, we want to move up and over to the Delivery Position,
    self.systemModel['ReagentDelivery'].setMoveGripperUp()
    self.waitForCondition(self.systemModel['ReagentDelivery'].getSetGripperUp,True,EQUAL,3)
    time.sleep(2)#**Need sensor here
    self.systemModel['ReagentDelivery'].moveToDeliveryPosition(int(self.ReactorID[-1]),self.reagentLoadPosition)
    self.waitForCondition(self.systemModel['ReagentDelivery'].getCurrentPosition,(int(self.ReactorID[-1]), 0, self.reagentLoadPosition),EQUAL,5)
    self.systemModel['ReagentDelivery'].setMoveGripperDown()
    self.waitForCondition(self.systemModel['ReagentDelivery'].getSetGripperDown,True,EQUAL,3)
    time.sleep(2)#**Need sensor here
    
  def setGripperRemove(self):
    if self.checkForCondition(self.systemModel['ReagentDelivery'].getCurrentPosition,(int(self.ReactorID[-1]), 0, self.reagentLoadPosition),EQUAL):
      #We are in position
      if self.checkForCondition(self.systemModel['ReagentDelivery'].getSetGripperDown,True,EQUAL):
        #We are down
        self.systemModel['ReagentDelivery'].setMoveGripperClose() #Make sure gripper is closed.
        self.waitForCondition(self.systemModel['ReagentDelivery'].getSetGripperClose,True,EQUAL,2)    
        time.sleep(2)#**Need sensor here
        self.systemModel['ReagentDelivery'].setMoveGripperUp()
        self.waitForCondition(self.systemModel['ReagentDelivery'].getSetGripperUp,True,EQUAL,3)
        time.sleep(2)#**Need sensor here
        self.systemModel['ReagentDelivery'].moveToReagentPosition(int(self.ReagentReactorID[-1]),self.reagentPosition)
        self.waitForCondition(self.systemModel['ReagentDelivery'].getCurrentPosition,(int(self.ReagentReactorID[-1]), self.reagentPosition, 0),EQUAL,5)
        self.systemModel['ReagentDelivery'].setMoveGripperDown()
        self.waitForCondition(self.systemModel['ReagentDelivery'].getSetGripperDown,True,EQUAL,3)
        time.sleep(2)#**Need sensor here
        self.systemModel['ReagentDelivery'].setMoveGripperOpen()
        self.waitForCondition(self.systemModel['ReagentDelivery'].getSetGripperOpen,True,EQUAL,2)   
        time.sleep(2)#**Need sensor here
        self.systemModel['ReagentDelivery'].setMoveGripperUp()
        self.waitForCondition(self.systemModel['ReagentDelivery'].getSetGripperUp,True,EQUAL,3)
        time.sleep(2)#**Need sensor here
        self.systemModel['ReagentDelivery'].moveToReagentPosition(*HOME)
        self.waitForCondition(self.systemModel['ReagentDelivery'].getCurrentPosition,(3,3,0),EQUAL,5)

        
      else:
        print("Gripper in correct position for removal, but not in down position.")
    else:
      print("Gripper not in correct position for removal when setGripperRemove() called.")

class Evaporate(UnitOperation):
  def __init__(self,systemModel,params):
    UnitOperation.__init__(self,systemModel)
    expectedParams = {REACTORID:STR,EVAPTEMP:FLOAT,EVAPTIME:INT,COOLTEMP:INT,STIRSPEED:INT}
    paramError = self.validateParams(params,expectedParams)
    if self.paramsValid:
      self.setParams(params)
    else:
      raise UnitOpError(paramError)
		#Should have parameters listed below:
    #self.ReactorID
    #self.evapTemp
    self.evapTemp = self.reactTemp
    #self.evapTime
    self.evapTime = self.reactTime
    #self.coolTemp
    #self.stirSpeed
    
  def run(self):
    try:
      self.beginNextStep("Starting Evaporate Operation")
      self.setPressureRegulator(2,15)
      self.beginNextStep("Moving to position")
      self.setReactorPosition(EVAPORATE)
      self.beginNextStep("Setting evaporation Temperature")
      self.setTemp()
      self.setDescription("Starting vacuum and nitrogen")
      self.setEvapValves(ON)
      self.setDescription("Starting stir motor")    
      self.setStirSpeed(self.stirSpeed)
      self.setDescription("Starting heaters")
      self.setHeater(ON)
      self.setDescription("Starting evaporation timer")
      self.startTimer(self.evapTime)
      self.beginNextStep("Starting cooling")
      self.setHeater(OFF)
      self.setCool()
      self.setDescription("Stopping stir motor")    
      self.setStirSpeed(OFF)
      self.setDescription("Stopping vacuum and nitrogen")    
      self.setEvapValves(OFF)
      self.beginNextStep("Evaporation Operation Complete")
    except Exception as e:
      print type(e)
      print e
  
  """def setParams(self,currentParams):
    expectedParams = ['ReactorID','evapTime','evapTemp','coolTemp','stirSpeed']
    self.paramsValid = True
    for parameter in expectedParams:
      if not(parameter in currentParams):
        self.paramsValid = False
        #Log Error
      self.paramsValidated = True"""
      

class InstallVial(UnitOperation):
  def __init__(self,systemModel,params):
    UnitOperation.__init__(self,systemModel)
    self.setParams(params)
		#Should have parameters listed below:
    #self.ReactorID
    
  def run(self):
    try:
      self.beginNextStep("Starting Install Vial Operation")
      self.beginNextStep("Moving to vial install position")
      self.setReactorPosition(INSTALL)
      self.beginNextStep("Install Vial Operation Complete")
    except Exception as e:
      print type(e)
      print e
      
  """def setParams(self,currentParams):
    expectedParams = ['ReactorID']
    self.paramsValid = True
    for parameter in expectedParams:
      if not(parameter in currentParams):
        self.paramsValid = False
        #Log Error
      self.paramsValidated = True"""
      
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
      print type(e)
      print e
      
  """def setParams(self,currentParams):
    expectedParams = ['ReactorID','stopcockPosition']
    self.paramsValid = True
    for parameter in expectedParams:
      if not(parameter in currentParams):
        self.paramsValid = False
        #Log Error
      self.paramsValidated = True"""
      
  def setTransfer(self):
    self.systemModel[self.ReactorID]['transfer'].setTransfer(HPLC)
    self.waitForCondition(self.systemModel[self.ReactorID]['transfer'].getTransfer(),HPLC,EQUAL,3)
    
  def setHPLCValve(self):
    self.systemModel[self.ReactorID]['transfer'].setHPLC(INJECT)       
    self.waitForCondition(self.systemModel[self.ReactorID]['transfer'].getHPLC(),INJECT,EQUAL,3) 
  
class TransferElute(UnitOperation):
  def __init__(self,systemModel,params):
    UnitOperation.__init__(self,systemModel)
    self.setParams(params)
		#Should have parameters listed below:
    #self.ReactorID
    #self.stopcockPosition
    
  def run(self):
    try:
      self.beginNextStep("Starting Transfer Elution Operation")
      self.abortOperation()
      self.beginNextStep("Moving to transfer position")
      self.setReactorPosition(TRANSFER)
      self.beginNextStep("Moving receiving reactor to position")
      self.setTransferReactorPosition(ADDREAGENT)
      self.beginNextStep("Moving stopcocks to position")
      self.setStopcock()
      self.beginNextStep("Beginning elution")
      self.setTransfer()
      self.beginNextStep("Transfer Elution Operation Complete")
    except Exception as e:
      print type(e)
      print e
      
  """def setParams(self,currentParams):
    expectedParams = ['ReactorID','stopcockPosition']
    self.paramsValid = True
    for parameter in expectedParams:
      if not(parameter in currentParams):
        self.paramsValid = False
        #Log Error
      self.paramsValidated = True"""
  
  def setTransfer(self):
    self.systemModel[self.ReactorID]['transfer'].setTransfer(self.transferPosition)
    self.waitForCondition(self.systemModel[self.ReactorID]['transfer'].getTransfer(),self.transferPosition,EQUAL,3)
   
class Transfer(UnitOperation):
  def __init__(self,systemModel,params):
    UnitOperation.__init__(self,systemModel)
    self.setParams(params) 
    #Should have parameters listed below:
    #self.ReactorID
    #self.stopcockPosition
    #self.transferReactorID
    
  def run(self):
    try:
      self.beginNextStep("Starting Transfer Operation")
      self.abortOperation()
      self.beginNextStep("Moving to position")
      self.setReactorPosition(TRANSFER)
      self.beginNextStep("Moving recieving reactor to position")
      self.setReactorPosition(ADDREAGENT,self.transferReactorID)
      self.beginNextStep("Starting transfer")
      self.startTransfer()
      self.beginNextStep("Transfer Operation Complete")
    except Exception as e:
      print type(e)
      print e
      
  """def setParams(self,currentParams):
    expectedParams = ['ReactorID','transferReactorID','stopcockPosition']
    self.paramsValid = True
    for parameter in expectedParams:
      if not(parameter in currentParams):
        self.paramsValid = False
        #Log Error
      self.paramsValidated = True"""
  
  def startTransfer(self):
    self.systemModel[self.ReactorID]['transfer'].setTransfer(self.transferPosition)
    self.waitForCondition(self.systemModel[self.ReactorID]['transfer'].getTransfer,self.transferPosition,EQUAL,3)
 
class UserInput(UnitOperation):
  def __init__(self,systemModel,params):
    UnitOperation.__init__(self,systemModel)
    self.setParams(params)
		#Should have parameters listed below:
    #self.userMessage
    #self.isCheckbox
    #self.description
    
  def run(self):
    try:
      self.beginNextStep("Starting User Input Operation")
      self.abortOperation()
      self.beginNextStep("Waiting for user input")
      self.setMessageBox()
      self.beginNextStep("User input recieved")
      self.beginNextStep("User Input Operation Complete")
    except Exception as e:
      print type(e)
      print e
      
  """def setParams(self,currentParams):
    expectedParams = ['userMessage','isCheckbox','description']
    self.paramsValid = True
    for parameter in expectedParams:
      if not(parameter in currentParams):
        self.paramsValid = False
        #Log Error
      self.paramsValidated = True"""
  
  def setMessageBox(self):
    self.setDescription("Waiting for user input")
    self.waitForUser = True
    self.waitForCondition(self.getUserInput,True,EQUAL,65535) #timeout = Infinite
    self.setDescription()
    
  def getUserInput(self):
    return not(self.waitForUser)
    
class DeliverF18(UnitOperation):
  def __init__(self,systemModel,params):
    UnitOperation.__init__(self,systemModel)
    self.setParams(params)
    self.ReactorID='Reactor1'
    #Should have parameters listed below:
    #self.trapTime
    #self.trapPressure
    #self.eluteTime
    #self.elutePressure
    
  def run(self):
    try:
      self.beginNextStep("Starting F18 Delivery Operation")
      self.setPressureRegulator(2,0) #Vent pressure to avoid delivery issues
      self.beginNextStep("Moving to Reactor1 to Add position")
      self.setReactorPosition(ADDREAGENT)
      self.beginNextStep("Setting stopcock positions for trapping")
      self.setStopcockPosition(F18TRAP)
      self.beginNextStep("Starting F18 trapping")
      self.F18Trap(self.trapTime,self.trapPressure)
      self.beginNextStep("Trap complete")
      self.setPressureRegulator(2,0) #Vent pressure to avoid delivery issues
      self.beginNextStep("Setting stopcock positions for elution")
      self.setStopcockPosition(F18ELUTE)
      self.beginNextStep("Starting F18 Elute")
      self.F18Elute(self.eluteTime,self.elutePressure)
      self.beginNextStep("Elution complete")
      self.beginNextStep("F18 Delivery Operation complete")
    except Exception as e:
      print type(e)
      print e
      
  def F18Trap(self,time,pressure):
    self.systemModel['ExternalSystems'].setF18LoadValveOpen(ON)  
    self.waitForCondition(self.systemModel['ExternalSystems'].getF18LoadValveOpen,ON,EQUAL,5)
    self.setPressureRegulator(2,pressure) #Set pressure after valve is opened
    self.startTimer(time)
    self.beginNextStep("Stopping F18 trapping")
    self.systemModel['ExternalSystems'].setF18LoadValveOpen(OFF)
    self.waitForCondition(self.systemModel['ExternalSystems'].getF18LoadValveOpen,OFF,EQUAL,5)
    
  def F18Elute(self,time,pressure):
    self.systemModel['ExternalSystems'].setF18EluteValveOpen(ON)
    self.waitForCondition(self.systemModel['ExternalSystems'].getF18EluteValveOpen,ON,EQUAL,5)
    self.setPressureRegulator(2,pressure)
    self.startTimer(time)
    self.beginNextStep("Stopping F18 elution")
    self.systemModel['ExternalSystems'].setF18EluteValveOpen(OFF)
    self.waitForCondition(self.systemModel['ExternalSystems'].getF18EluteValveOpen,OFF,EQUAL,5)
        

  
    
class DetectRadiation(UnitOperation):
  def __init__(self,systemModel,params):
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
      print type(e)
      print e
      
  """def setParams(self,currentParams):
    expectedParams = ['ReactorID']
    self.paramsValid = True
    for parameter in expectedParams:
      if not(parameter in currentParams):
        self.paramsValid = False
        #Log Error
      self.paramsValidated = True"""
    
  def getRadiation(self):
    self.systemModel[self.ReactorID]['radiation_detector'].getCalibratedReading()
    self.waitForCondition(self.systemModel[self.ReactorID]['radiation_detector'].getCalibratedReading,self.calibrationCoefficient,GREATER,3)

class Initialize(UnitOperation):
  def __init__(self,systemModel):
    UnitOperation.__init__(self,systemModel)
    self.ReactorTuple=('Reactor1','Reactor2','Reactor3')
    self.reagentLoadPositionTuple=(1,2)
    
  def run(self):
    self.stepDescription = "Starting Initialize Operation"
    #Close all valves (set state)
    for self.ReactorID in self.ReactorTuple:
      self.setEvapValves(OFF)
      self.systemModel[self.ReactorID]['Thermocouple'].setHeaterOff()
      for self.reagentLoadPosition in self.reagentLoadPositionTuple:
        self.setReagentTransferValves(OFF)
      self.systemModel[self.ReactorID]['Motion'].moveReactorDown()
    
    #Set pressures
    self.setPressureRegulator(2,5)
    self.setPressureRegulator(1,59)
    
    #Home robots
    for self.ReactorID in self.ReactorTuple:
      self.systemModel[self.ReactorID]['Motion'].setEnableReactorRobot()
    self.systemModel['ReagentDelivery'].setMoveGripperUp()
    self.waitForCondition(self.systemModel['ReagentDelivery'].getSetGripperUp,True,EQUAL,2)
    self.systemModel['ReagentDelivery'].setMoveGripperOpen()
    self.waitForCondition(self.systemModel['ReagentDelivery'].getSetGripperOpen,True,EQUAL,2) 
    self.systemModel[self.ReactorID]['Motion'].moveHomeRobots()
    time.sleep(5)
    self.waitForCondition(self.areRobotsHomed,True,EQUAL,10)
    for self.ReactorID in self.ReactorTuple:
      self.setReactorPosition(INSTALL)
    print "System Initialized.\n"
  
  def areRobotsHomed(self):
    self.robotsHomed=True
    for self.ReactorID in self.ReactorTuple:
      if not(self.checkForCondition(self.systemModel[self.ReactorID]['Motion'].getCurrentRobotStatus,ENABLED,EQUAL)):
        self.robotsHomed=False
    if not(self.checkForCondition(self.systemModel['ReagentDelivery'].getRobotStatus,(ENABLED,ENABLED),EQUAL)):
      self.robotsHomed=False
    return self.robotsHomed

    
class TempProfile(UnitOperation):
  def __init__(self,systemModel,params):
    UnitOperation.__init__(self,systemModel)
    self.setParams(params)
    #Should have parameters listed below:
    #self.ReactorID
    #self.reactTemp
    self.reactTime = 900
  def run(self):
    try:
      self.beginNextStep("Starting TempProfile Operation")
      self.beginNextStep("Moving to position")
      self.setReactorPosition(TRANSFER)
      self.beginNextStep("Setting reactor Temperature")
      self.setTemp()
      self.beginNextStep("Starting heater")
      self.setHeater(ON)
      self.setDescription("Starting reaction timer")
      self.startTimer(self.reactTime)
      self.beginNextStep("Starting cooling")
      self.setHeater(OFF)
      self.systemModel['CoolingSystem'].setCoolingSystemOn(True)
      self.beginNextStep("TempProfile Operation Complete")
    except Exception as e:
      print type(e)
      print e
      
"""
  def setParams(self,currentParams):
    expectedParams = ['ReactorID','reactTemp','reactTime','coolTemp','reactPosition','stirSpeed']
    self.paramsValid = True
    for parameter in expectedParams:
      if not(parameter in currentParams):
        self.paramsValid = False
        #Log Error
      self.paramsValidated = True
      
class ParamTest(UnitOperation):
  def __init__(self,systemModel,params):
    UnitOperation.__init__(self,systemModel)


    expectedParams = {REACTORID:STR,REACTTEMP:FLOAT,PARAMTEST:STR}
    paramError = self.validateParamsTest(params,expectedParams)
    if self.paramsValid:
      self.setParams(params)
    else:
      raise UnitOpError(paramError)
    #Should have parameters listed below:
    #self.ReactorID
    #self.reactTemp
    #self.paramTest

    self.paramsValidated = True
    return errorMessage
"""

class fakeSystem():
  def __init__(self):
    self.model = "winner"

def test():
  sysModel = fakeSystem()
  reactParams = {'ReactorID':'Reactor1','reactTemp':30,'reactTime':10,'coolTemp':30,'reactPosition':'React2','stirSpeed':500}
  react1 = React(sysModel,reactParams)
  react1.setDaemon(True)
  #react1.run()
  addParams = {'ReactorID':'Reactor1','ReagentReactorID':'Reactor1','ReagentPosition':1,'reagentLoadPosition':1}
  add1 = AddReagent(sysModel,addParams)
  add1.setDaemon(True)
  #add1.run()
  evapParams = {'ReactorID':'Reactor1','evapTemp':30,'evapTime':10,'coolTemp':30,'stirSpeed':500}
  evap1 = Evaporate(sysModel,evapParams)
  evap1.setDaemon(True)
  #evap1.run()
  #myParams = {'ReactorID':'Reactor1','reactTemp':25,'paramTest':'False'}
  #pTest = ParamTest(sysModel,myParams)
    
if __name__=="__main__":
    test()
