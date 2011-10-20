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
F18TRAP = (2,1,0)  #Set Stopcock 1 to Position 2, Stopcock 2 to Position 1
F18ELUTE = (1,2,0) #Set Stopcock 1 to Position 1, Stopcock 2 to Position 2

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
PRESSUREREGULATOR = 'pressureRegulator'
PRESSURE = 'pressure'
DURATION = 'duration'

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
    return str(self.value)

class UnitOperation(threading.Thread):
  def __init__(self,systemModel,username = "", database = None):
    threading.Thread.__init__(self)
    self.time = time.time()
    self.params = {}
    self.paramsValidated = False
    self.paramsValid = False
    self.systemModel = systemModel.model
    self.username = username
    self.database = database
    self.status = ""
    self.delay = 50#50ms delay
    self.isRunning = False
    self.paused = False
    self.abort = False
    self.pausedLock = threading.Lock()
    self.timerStartTime = 0
    self.timerLength = 0
    self.timerShowInStatus = False

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
      if paramname=="pressureRegulator":
        self.pressureRegulator = params['pressureRegulator']
      if paramname=="pressure":
        self.pressure = params['pressure']
      if paramname=="duration":
        self.duration = params['duration']
  
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
    if self.database != None:
      self.database.Log(self.username, error)
    else:
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
      
  def setStatus(self,status):
    print "Temp: " + status
    self.status = status

  def updateStatus(self,status):
    statusComponents = self.status.split(", ")
    if len(statusComponents) > 0:
       self.setStatus(statusComponents[0] + ", " + status)
    else:
       self.setStatus(status)
    
  def checkAbort(self):
    if self.abort:
      self.abortOperation("Operation aborted")

  def setReactorPosition(self,reactorPosition,ReactorID=255):
    motionTimeout = 10 #How long to wait before erroring out.
    if (ReactorID==255):
      ReactorID = self.ReactorID
    if not(self.checkForCondition(self.systemModel[ReactorID]['Motion'].getCurrentRobotStatus,ENABLED,EQUAL)):
      self.systemModel[ReactorID]['Motion'].setEnableReactorRobot()      
      self.waitForCondition(self.systemModel[ReactorID]['Motion'].getCurrentRobotStatus,ENABLED,EQUAL,3)
    if not(self.checkForCondition(self.systemModel[ReactorID]['Motion'].getCurrentPosition,reactorPosition,EQUAL)):
      self.systemModel[ReactorID]['Motion'].moveReactorDown()
      self.waitForCondition(self.systemModel[ReactorID]['Motion'].getCurrentReactorDown,True,EQUAL,motionTimeout)
      self.systemModel[ReactorID]['Motion'].moveToPosition(reactorPosition)
      self.waitForCondition(self.systemModel[ReactorID]['Motion'].getCurrentPosition,reactorPosition,EQUAL,motionTimeout)
      if not reactorPosition == INSTALL:
        self.systemModel[ReactorID]['Motion'].moveReactorUp()
        self.waitForCondition(self.systemModel[ReactorID]['Motion'].getCurrentReactorUp,True,EQUAL,motionTimeout)
      self.systemModel[ReactorID]['Motion'].setDisableReactorRobot()
      self.waitForCondition(self.systemModel[ReactorID]['Motion'].getCurrentRobotStatus,DISABLED,EQUAL,3)
    else: #We're in the right position, check if we're sealed.
      if not(self.checkForCondition(self.systemModel[ReactorID]['Motion'].getCurrentReactorUp,True,EQUAL)):
        if not(reactorPosition==INSTALL):
          self.systemModel[ReactorID]['Motion'].moveReactorUp()
          self.waitForCondition(self.systemModel[ReactorID]['Motion'].getCurrentReactorUp,True,EQUAL,motionTimeout)
          self.systemModel[ReactorID]['Motion'].setDisableReactorRobot()
          self.waitForCondition(self.systemModel[ReactorID]['Motion'].getCurrentRobotStatus,DISABLED,EQUAL,3)
    
  def waitForCondition(self,function,condition,comparator,timeout): #Timeout in seconds, default to 3.
    startTime = time.time()
    self.delay = 500
    self.checkAbort()
    if comparator == EQUAL:
      while not(function() == condition):
        #print "%s Function %s == %s, expected %s" % (self.curTime(),str(function.__name__),str(function()),str(condition))
        self.stateCheckInterval(self.delay)
        if not(timeout == 65535):
          if self.isTimerExpired(startTime,timeout):
            self.logError("waitForCondition call timed out on function:%s class:%s" % (function.__name__,function.im_class))
            self.abortOperation("Function %s == %s, expected %s" % (str(function.__name__),str(function()),str(condition)))
            break
        self.checkAbort()
    elif comparator == NOTEQUAL:
      while (function() == condition):
        #print "%s Function %s == %s, expected %s" % (self.curTime(),str(function.__name__),str(function()),str(condition))
        self.stateCheckInterval(self.delay)
        if not(timeout == 65535):
          if self.isTimerExpired(startTime,timeout):
            self.logError("waitForCondition call timed out on function:%s class:%s" % (function.__name__,function.im_class))
            self.abortOperation("Function %s == %s, expected %s" % (str(function.__name__),str(function()),str(condition)))
            break
        self.checkAbort()
    elif comparator == GREATER:
      while not(function() >= condition):
        #print "%s Function %s == %s, expected %s" % (self.curTime(),str(function.__name__),str(function()),str(condition))
        self.stateCheckInterval(self.delay)
        if not(timeout == 65535):
          if self.isTimerExpired(startTime,timeout):
            self.logError("waitForCondition call timed out on function:%s class:%s" % (function.__name__,function.im_class))
            self.abortOperation("Function %s == %s, expected %s" % (str(function.__name__),str(function()),str(condition)))
            break            
        self.checkAbort()
    elif comparator == LESS:
      while not(function() <=condition):
        #print "%s Function %s == %s, expected %s" % (self.curTime(),str(function.__name__),str(function()),str(condition))
        self.stateCheckInterval(self.delay)
        if not(timeout == 65535):
          if self.isTimerExpired(startTime,timeout):
            self.logError("waitForCondition call timed out on function:%s class:%s" % (function.__name__,function.im_class))
            self.abortOperation("Function %s == %s, expected %s" % (str(function.__name__),str(function()),str(condition)))
            break
        self.checkAbort()
    else:
      self.logError("Invalid comparator: " + comparator)
      self.abortOperation("Invalid comparator: " + comparator)
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
      self.logError("Invalid comparator: " + comparator)
      ret=False
    #print "Function %s == %s, expected %s" % (str(function.__name__),str(function()),str(condition))  
    return ret
    
  def startTimer(self,timerLength,showInStatus=True):  #In seconds
    #Remember the start time and length
    self.timerStartTime = time.time()
    self.timerLength = timerLength
    self.timerShowInStatus = showInStatus
    
  def waitForTimer(self):
    while not(self.isTimerExpired(self.timerStartTime,self.timerLength)):
      self.updateTimer()
      self.checkAbort()
      self.stateCheckInterval(50) #Sleep 50ms between checks

  def updateTimer(self):
    if self.timerShowInStatus:
      self.updateStatus("%s remaining" % self.formatTime(self.timerLength-(time.time()-self.timerStartTime)))
      
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
    if hours != 0:
      return("%.2d:%.2d:%.2d" % (hours,minutes,seconds))
    else:
      return("%.2d:%.2d" % (minutes,seconds))
    
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
    for nReactor in range(1, 4):
      sReactor = "Reactor" + str(nReactor)
      self.systemModel[sReactor]['Thermocouple'].setSetPoint(OFF)
      self.systemModel[sReactor]['Thermocouple'].setHeaterOff()
    self.systemModel['CoolingSystem'].setCoolingSystemOn(OFF)
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
      nRefreshFrequency = 5  # Update pressure this number of times per second
      currentPressure = float(self.systemModel[self.pressureRegulator].getSetPressure())
      rampRate = (float(pressureSetPoint) - float(currentPressure)) / float(rampTime) / float(nRefreshFrequency)
      nElapsedTime = 0
      while nElapsedTime < rampTime:
        time.sleep(1 / float(nRefreshFrequency))
        nElapsedTime += 1 / float(nRefreshFrequency)
        currentPressure += rampRate
        self.systemModel[self.pressureRegulator].setRegulatorPressure(currentPressure) #Set analog value on PLC
        self.updateTimer()
        self.checkAbort()
    self.systemModel[self.pressureRegulator].setRegulatorPressure(pressureSetPoint)
    self.pressureSetPoint = pressureSetPoint
    self.waitForCondition(self.pressureSet,True,EQUAL,3)

  def pressureSet(self):
    return (self.checkForCondition(self.systemModel[self.pressureRegulator].getCurrentPressure,self.pressureSetPoint - 1,GREATER) and
      self.checkForCondition(self.systemModel[self.pressureRegulator].getCurrentPressure,self.pressureSetPoint + 1,LESS))
   
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
      self.setStatus("Moving reactor")
      self.setReactorPosition(self.reactPosition)#REACTA OR REACTB
      self.setStatus("Starting motor")
      self.setStirSpeed(self.stirSpeed)
      self.setStatus("Heating")
      self.setTemp()
      self.setHeater(ON)
      self.setStatus("Reacting")
      self.startTimer(self.reactTime)
      self.waitForTimer()
      self.setStatus("Cooling")
      self.setHeater(OFF)
      self.setCool()
      self.setStatus("Completing") 
      self.setStirSpeed(OFF)
      self.setStatus("Complete")
    except Exception as e:
      self.abortOperation(e)
      
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
      self.setStatus("Moving")
      self.setReactorPosition(self.reactPosition)
      self.setStatus("Complete")
    except Exception as e:
      self.abortOperation(e)
    
    
class Add(UnitOperation):
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
      self.setStatus("Adjusting pressure")
      self.setPressureRegulator(2,5)      #Set delivery pressure to 5psi
      self.setStatus("Moving reactor")
      self.setReactorPosition(ADDREAGENT) #Move reactor to position
      self.setStatus("Picking up reagent")
      self.setGripperPlace()              #Move reagent to the addition position.
      self.setStatus("Delivering reagent")
      self.startTimer(10,False)           #In seconds, don't show in status
      self.waitForTimer()                 #Wait for Dispense reagent
      self.setStatus("Returning reagent")
      self.setGripperRemove()             #Return vial to its starting location
      self.setStatus("Complete")
    except Exception as e:
      self.abortOperation(e)
  
  """def setParams(self,currentParams):
    expectedParams = ['ReactorID','ReagentPosition','reagentLoadPosition']
    self.paramsValid = True
    for parameter in expectedParams:
      if not(parameter in currentParams):
        self.paramsValid = False
        #Log Error
      self.paramsValidated = True"""
    
  def setGripperPlace(self):
    #Make sure we are open and up
    if not self.checkForCondition(self.systemModel['ReagentDelivery'].getCurrentGripperOpen,True,EQUAL):
      self.abortOperation("ERROR: setGripperPlace called while gripper was not open. Operation aborted.")
    if not self.checkForCondition(self.systemModel['ReagentDelivery'].getCurrentGripperUp,True,EQUAL):
      self.abortOperation("ERROR: setGripperPlace called while gripper was not up. Operation aborted.") 
    
    #Move to ReagentPosition, then down and close
    self.systemModel['ReagentDelivery'].moveToReagentPosition(int(self.ReagentReactorID[-1]),self.reagentPosition) #Move Reagent Robot to position
    self.waitForCondition(self.systemModel['ReagentDelivery'].getCurrentPosition,(int(self.ReagentReactorID[-1]), self.reagentPosition, 0),EQUAL,5)
    self.systemModel['ReagentDelivery'].setMoveGripperDown() #Move Gripper down
    self.waitForCondition(self.systemModel['ReagentDelivery'].getCurrentGripperDown,True,EQUAL,2)
    self.systemModel['ReagentDelivery'].setMoveGripperClose() #Close Gripper
    self.waitForCondition(self.systemModel['ReagentDelivery'].getCurrentGripperClose,True,EQUAL,2)
    
    #Move up and over to the Delivery Position
    self.systemModel['ReagentDelivery'].setMoveGripperUp()
    self.waitForCondition(self.systemModel['ReagentDelivery'].getCurrentGripperUp,True,EQUAL,3)
    self.systemModel['ReagentDelivery'].moveToDeliveryPosition(int(self.ReactorID[-1]),self.reagentLoadPosition)
    self.waitForCondition(self.systemModel['ReagentDelivery'].getCurrentPosition,(int(self.ReactorID[-1]), 0, self.reagentLoadPosition),EQUAL,5)

    #Turn the transfer gas on and move the vial down    
    self.setReagentTransferValves(ON)
    time.sleep(0.5)
    self.systemModel['ReagentDelivery'].setMoveGripperDown()
    self.waitForCondition(self.systemModel['ReagentDelivery'].getCurrentGripperDown,True,EQUAL,3)
    
  def setGripperRemove(self):
    #Make sure we are closed, down and in position
    if not self.checkForCondition(self.systemModel['ReagentDelivery'].getCurrentGripperClose,True,EQUAL):
      self.abortOperation("ERROR: setGripperRemove called while gripper was not closed. Operation aborted.")
    if not self.checkForCondition(self.systemModel['ReagentDelivery'].getCurrentGripperDown,True,EQUAL):
      self.abortOperation("ERROR: setGripperRemove called while gripper was not up. Operation aborted.")
    if not self.checkForCondition(self.systemModel['ReagentDelivery'].getCurrentPosition,(int(self.ReactorID[-1]), 0, self.reagentLoadPosition),EQUAL):
      self.abortOperation("ERROR: setGripperRemove called while gripper was not in the target position. Operation aborted.")

    #Move up and turn off the transfer gas
    self.systemModel['ReagentDelivery'].setMoveGripperUp()
    self.waitForCondition(self.systemModel['ReagentDelivery'].getCurrentGripperUp,True,EQUAL,3)
    self.setReagentTransferValves(OFF)

    #Move to ReagentPosition, then down and open
    self.systemModel['ReagentDelivery'].moveToReagentPosition(int(self.ReagentReactorID[-1]),self.reagentPosition)
    self.waitForCondition(self.systemModel['ReagentDelivery'].getCurrentPosition,(int(self.ReagentReactorID[-1]), self.reagentPosition, 0),EQUAL,5)
    self.systemModel['ReagentDelivery'].setMoveGripperDown()
    self.waitForCondition(self.systemModel['ReagentDelivery'].getCurrentGripperDown,True,EQUAL,3)
    self.systemModel['ReagentDelivery'].setMoveGripperOpen()
    self.waitForCondition(self.systemModel['ReagentDelivery'].getCurrentGripperOpen,True,EQUAL,2)
    
    #Move up and to home
    self.systemModel['ReagentDelivery'].setMoveGripperUp()
    self.waitForCondition(self.systemModel['ReagentDelivery'].getCurrentGripperUp,True,EQUAL,3)
    self.systemModel['ReagentDelivery'].moveToHome()
    self.waitForCondition(self.systemModel['ReagentDelivery'].getCurrentPosition,(0,0,0),EQUAL,5)

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
      self.setStatus("Adjusting pressure")
      self.setPressureRegulator(2,5)
      self.setStatus("Moving reactor")
      self.setReactorPosition(EVAPORATE)
      self.setStatus("Starting motor")
      self.setStirSpeed(self.stirSpeed)
      self.setStatus("Heating")
      self.setEvapValves(ON)
      self.setTemp()
      self.setHeater(ON)
      self.setStatus("Evaporating")
      self.startTimer(self.evapTime)
      self.setPressureRegulator(2,15,self.evapTime/2) #Ramp pressure over the first half of the evaporation
      self.waitForTimer() #Now wait until the rest of the time elapses
      self.setStatus("Cooling")
      self.setHeater(OFF)
      self.setCool()
      self.setStatus("Completing") 
      self.setStirSpeed(OFF)
      self.setEvapValves(OFF)
      self.setStatus("Complete")
    except Exception as e:
      self.abortOperation(e)
  
  """def setParams(self,currentParams):
    expectedParams = ['ReactorID','evapTime','evapTemp','coolTemp','stirSpeed']
    self.paramsValid = True
    for parameter in expectedParams:
      if not(parameter in currentParams):
        self.paramsValid = False
        #Log Error
      self.paramsValidated = True"""
      

class Install(UnitOperation):
  def __init__(self,systemModel,params):
    UnitOperation.__init__(self,systemModel)
    self.setParams(params)
		#Should have parameters listed below:
    #self.ReactorID
    
  def run(self):
    try:
      self.setStatus("Moving reactor")
      self.setReactorPosition(INSTALL)
      self.setStatus("Complete")
    except Exception as e:
      self.abortOperation(e)
      
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
      self.abortOperation(e)
      
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
      self.abortOperation(e)
      
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
      self.abortOperation(e)
      
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
      self.abortOperation(e)
      
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
      self.setStatus("Starting F18 Delivery Operation")
      self.setPressureRegulator(2,0) #Vent pressure to avoid delivery issues
      self.setStatus("Moving to Reactor1 to Add position")
      self.setReactorPosition(ADDREAGENT)
      self.setStatus("Setting stopcock positions for trapping")
      self.setStopcockPosition(F18TRAP)
      self.setStatus("Starting F18 trapping")
      self.F18Trap(self.trapTime,self.trapPressure)
      self.setStatus("Trap complete")
      self.setPressureRegulator(2,0) #Vent pressure to avoid delivery issues
      self.setStatus("Setting stopcock positions for elution")
      self.setStopcockPosition(F18ELUTE)
      self.setStatus("Starting F18 Elute")
      self.F18Elute(self.eluteTime,self.elutePressure)
      self.setStatus("Elution complete")
      self.setStatus("F18 Delivery Operation complete")
    except Exception as e:
      self.abortOperation(e)
      
  def F18Trap(self,time,pressure):
    self.systemModel['ExternalSystems'].setF18LoadValveOpen(ON)  
    self.waitForCondition(self.systemModel['ExternalSystems'].getF18LoadValveOpen,ON,EQUAL,5)
    self.timerShowInStatus = False
    self.setPressureRegulator(2,pressure,5) #Set pressure after valve is opened
    self.startTimer(time)
    self.waitForTimer()
    self.setStatus("Stopping F18 trapping")
    self.systemModel['ExternalSystems'].setF18LoadValveOpen(OFF)
    self.waitForCondition(self.systemModel['ExternalSystems'].getF18LoadValveOpen,OFF,EQUAL,5)
    
  def F18Elute(self,time,pressure):
    self.systemModel['ExternalSystems'].setF18EluteValveOpen(ON)
    self.waitForCondition(self.systemModel['ExternalSystems'].getF18EluteValveOpen,ON,EQUAL,5)
    self.timerShowInStatus = False
    self.setPressureRegulator(2,pressure,5)
    self.startTimer(time)
    self.waitForTimer()
    self.setStatus("Stopping F18 elution")
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
      self.abortOperation(e)
      
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
    try:
      #Close all valves (set state)
      self.setStatus("Initializing valves")
      for self.ReactorID in self.ReactorTuple:
        self.setEvapValves(OFF)
        self.systemModel[self.ReactorID]['Thermocouple'].setHeaterOff()
        for self.reagentLoadPosition in self.reagentLoadPositionTuple:
          self.setReagentTransferValves(OFF)
        self.systemModel[self.ReactorID]['Motion'].moveReactorDown()
      
      #Set pressures
      self.setStatus("Initializing pressures")
      self.setPressureRegulator(2,5)
      self.setPressureRegulator(1,60)

      #Raise and open gripper    
      self.setStatus("Initializing robots")
      self.systemModel['ReagentDelivery'].setMoveGripperUp()
      self.waitForCondition(self.systemModel['ReagentDelivery'].getCurrentGripperUp,True,EQUAL,2)
      self.systemModel['ReagentDelivery'].setMoveGripperOpen()
      self.waitForCondition(self.systemModel['ReagentDelivery'].getCurrentGripperOpen,True,EQUAL,2) 

      #Home robots
      self.systemModel[self.ReactorID]['Motion'].moveHomeRobots()
      time.sleep(2)
      self.waitForCondition(self.areRobotsHomed,True,EQUAL,10)
      for self.ReactorID in self.ReactorTuple:
        self.setReactorPosition(INSTALL)
      self.setStatus("Complete")
    except Exception as e:
      self.abortOperation(e)
  
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
      self.setStatus("Moving to position")
      self.setReactorPosition(TRANSFER)
      self.setStatus("Heating")
      self.setTemp()
      self.setHeater(ON)
      self.setStatus("Profiling")
      self.startTimer(self.reactTime)
      self.setStatus("Cooling")
      self.setHeater(OFF)
      self.setCool()
      self.setStatus("Complete")
    except Exception as e:
      self.abortOperation(e)
      
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
      self.beginNextStep("Ramping pressure")
      self.setPressureRegulator(str(self.pressureRegulator),self.pressure,self.duration)
      self.beginNextStep("Pressure ramp complete")
    except Exception as e:
      self.abortOperation(e)
      
class Mix(UnitOperation):
  def __init__(self,systemModel,params):
    UnitOperation.__init__(self,systemModel)
    expectedParams = {REACTORID:STR,STIRSPEED:INT,DURATION:INT}
    self.validateParams(params,expectedParams)
    if self.paramsValid:
      self.setParams(params)
    else:
      raise UnitOpError(paramError)
    # Should have the params listed below:
    # self.ReactorID
    # self.stirSpeed
    # self.duration
  def run(self):
    try:
      self.setStatus("Mixing")
      self.setStirSpeed(self.stirSpeed)
      self.startTimer(self.duration)
      self.waitForTimer()
      self.setStirSpeed(OFF)
      self.setStatus("Complete")
    except Exception as e:
      self.abortOperation(e)

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
