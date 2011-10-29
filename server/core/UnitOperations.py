"""Unit operations
Elixys Unit Operations
"""
## TO DO:
## MAKE list of all private variables
## UPDATE list of constants
##
import time
import threading
import json
import copy

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

#Stopcock positions
F18DEFAULT = (0,2,1)
F18TRAP = (0,2,2)
F18ELUTE = (0,1,1)
TRANSFERDEFAULT = (1,0,0)
TRANSFERTRAP = (2,0,0)
TRANSFERELUTE = (1,0,0)

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

# Default component values
DEFAULT_ADD_DELIVERYTIME = 10
DEFAULT_ADD_DELIVERYPRESSURE = 5
DEFAULT_EVAPORATE_PRESSURE = 10

#Create a unit operation from a component object
def createFromComponent(pComponent, username, database, systemModel = None):
  if pComponent["componenttype"] == "CASSETTE":
    pCassette = Cassette(systemModel, {}, username, database)
    pCassette.initializeComponent(pComponent)
    return pCassette
  elif pComponent["componenttype"] == "ADD":
    pParams = {}
    pParams["ReactorID"] = "Reactor" + str(pComponent["reactor"])
    pParams["ReagentReactorID"] = "Reactor" + str(pComponent["reagentreactor"])
    pParams["ReagentPosition"] = 1  #We'll get the actual value once we initialize the component
    pParams["reagentLoadPosition"] = pComponent["deliveryposition"]
    pParams["duration"] = pComponent["deliverytime"]
    pParams["pressure"] = pComponent["deliverypressure"]
    pAdd = Add(systemModel, pParams, username, database)
    pAdd.initializeComponent(pComponent)
    pAdd.reagentPosition = pComponent["reagent"]["position"]
    return pAdd
  elif pComponent["componenttype"] == "EVAPORATE":
    pParams = {}
    pParams["ReactorID"] =  "Reactor" + str(pComponent["reactor"])
    pParams["evapTemp"] = pComponent["evaporationtemperature"]
    pParams["pressure"] = pComponent["evaporationpressure"]
    pParams["evapTime"] = pComponent["duration"]
    pParams["coolTemp"] = pComponent["finaltemperature"]
    pParams["stirSpeed"] = pComponent["stirspeed"]
    pEvaporate = Evaporate(systemModel, pParams, username, database)
    pEvaporate.initializeComponent(pComponent)
    return pEvaporate
  elif pComponent["componenttype"] == "TRANSFER":
    pParams = {}
    pParams["ReactorID"] = "Reactor" + str(pComponent["sourcereactor"])
    pParams["transferReactorID"] = "Reactor" + str(pComponent["targetreactor"])
    pParams["transferType"] = str(pComponent["mode"])
    pParams["transferTimer"] = pComponent["duration"]
    pParams["transferPressure"] = pComponent["pressure"]
    pTransfer = Transfer(systemModel, pParams, username, database)
    pTransfer.initializeComponent(pComponent)
    return pTransfer
  elif pComponent["componenttype"] == "REACT":
    pParams = {}
    pParams["ReactorID"] = "Reactor" + str(pComponent["reactor"])
    pParams["reactTemp"] = pComponent["reactiontemperature"]
    pParams["reactTime"] = pComponent["duration"]
    pParams["coolTemp"] = pComponent["finaltemperature"]
    pParams["reactPosition"] = "React" + str(pComponent["position"])
    pParams["stirSpeed"] = pComponent["stirspeed"]
    pReact = React(systemModel, pParams, username, database)
    pReact.initializeComponent(pComponent)
    return pReact
  elif pComponent["componenttype"] == "PROMPT":
    pParams = {}
    pParams["userMessage"] = pComponent["message"]
    pPrompt = Prompt(systemModel, pParams, username, database)
    pPrompt.initializeComponent(pComponent)
    return pPrompt
  elif pComponent["componenttype"] == "INSTALL":
    pParams = {}
    pParams["ReactorID"] = "Reactor" + str(pComponent["reactor"])
    pParams["userMessage"] = pComponent["message"]
    pInstall = Install(systemModel, pParams, username, database)
    pInstall.initializeComponent(pComponent)
    return pInstall
  elif pComponent["componenttype"] == "COMMENT":
    pParams = {}
    pParams["userMessage"] = pComponent["comment"]
    pComment = Comment(systemModel, pParams, username, database)
    pComment.initializeComponent(pComponent)
    return pComment
  elif pComponent["componenttype"] == "DELIVERF18":
    pParams = {}
    pParams["trapTime"] = pComponent["traptime"]
    pParams["trapPressure"] = pComponent["trappressure"]
    pParams["eluteTime"] = pComponent["elutetime"]
    pParams["elutePressure"] = pComponent["elutepressure"]
    pDeliverF18 = DeliverF18(systemModel, pParams, username, database)
    pDeliverF18.initializeComponent(pComponent)
    return pDeliverF18
  elif pComponent["componenttype"] == "INITIALIZE":
    pInitialize = Initialize(systemModel, {}, username, database)
    pInitialize.initializeComponent(pComponent)
    return pInitialize
  elif pComponent["componenttype"] == "MIX":
    pParams = {}
    pParams["ReactorID"] = "Reactor" + str(pComponent["reactor"])
    pParams["stirSpeed"] = pComponent["stirspeed"]
    pParams["duration"] = pComponent["mixtime"]
    pMix = Mix(systemModel, pParams, username, database)
    pMix.initializeComponent(pComponent)
    return pMix
  elif pComponent["componenttype"] == "MOVE":
    pParams = {}
    pParams["ReactorID"] = "Reactor" + str(pComponent["reactor"])
    pParams["reactPosition"] = str(pComponent["position"])
    pMove = Move(systemModel, pParams, username, database)
    pMove.initializeComponent(pComponent)
    return pMove
  else:
    raise Exception("Unknown component type: " + pComponent["componenttype"])

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
    if systemModel != None:
      self.systemModel = systemModel.model
    else:
      self.systemModel = None
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
      if paramname=="cyclotronFlag":
        self.cyclotronFlag = params['cyclotronFlag']
      if paramname=="transferType":
        self.transferType = params['transferType']
      if paramname=="transferTimer":
        self.transferTimer = params['transferTimer']
      if paramname=="transferPressure":
        self.transferPressure = params['transferPressure']      

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
    #if not(self.checkForCondition(self.systemModel[ReactorID]['Motion'].getCurrentPosition,reactorPosition,EQUAL)):
    self.systemModel[ReactorID]['Motion'].moveReactorDown()
    self.waitForCondition(self.systemModel[ReactorID]['Motion'].getCurrentReactorDown,True,EQUAL,motionTimeout)
    self.systemModel[ReactorID]['Motion'].moveToPosition(reactorPosition)
    self.waitForCondition(self.systemModel[ReactorID]['Motion'].getCurrentPosition,reactorPosition,EQUAL,motionTimeout)
    if not reactorPosition == INSTALL:
      self.systemModel[ReactorID]['Motion'].moveReactorUp()
      self.waitForCondition(self.systemModel[ReactorID]['Motion'].getCurrentReactorUp,True,EQUAL,motionTimeout)
    self.systemModel[ReactorID]['Motion'].setDisableReactorRobot()
    self.waitForCondition(self.systemModel[ReactorID]['Motion'].getCurrentRobotStatus,DISABLED,EQUAL,3)
    #else: #We're in the right position, check if we're sealed.
    #  if not(self.checkForCondition(self.systemModel[ReactorID]['Motion'].getCurrentReactorUp,True,EQUAL)):
    #    if not(reactorPosition==INSTALL):
    #      self.systemModel[ReactorID]['Motion'].moveReactorUp()
    #      self.waitForCondition(self.systemModel[ReactorID]['Motion'].getCurrentReactorUp,True,EQUAL,motionTimeout)
    #      self.systemModel[ReactorID]['Motion'].setDisableReactorRobot()
    #      self.waitForCondition(self.systemModel[ReactorID]['Motion'].getCurrentRobotStatus,DISABLED,EQUAL,3)
    
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

  def setStopcockPosition(self,stopcockPositions,ReactorID=255):
    if (ReactorID==255):
      ReactorID = self.ReactorID
    for stopcock in range(1,(len(stopcockPositions)+1)):
      if not stopcockPositions[stopcock-1] == 0:
        self.systemModel[ReactorID]['Stopcock'+str(stopcock)].setPosition(stopcockPositions[stopcock-1])
        self.waitForCondition(self.systemModel[ReactorID]['Stopcock'+str(stopcock)].getPosition,stopcockPositions[stopcock-1],EQUAL,3) 
 
  def startTransfer(self,state):
    self.systemModel[self.ReactorID]['Valves'].setTransferValveOpen(state)
    self.waitForCondition(self.systemModel[self.ReactorID]['Valves'].getTransferValveOpen,state,EQUAL,3)
 
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

  def validateComponentField(self, pValue, sValidation):
    """ Validates the field using the validation string """
    #Skip empty validation fields
    if sValidation == "":
      return True

    #Create a dictionary from the validation string
    pValidation = {}
    pKeyValues = sValidation.split(";")
    for sKeyValue in pKeyValues:
      pComponents = sKeyValue.split("=")
      pValidation[pComponents[0].strip()] = pComponents[1].strip()

    #Call the appropriate validation function
    if pValidation["type"] == "enum-number":
      return self.validateEnumNumber(pValue, pValidation)
    elif pValidation["type"] == "enum-reagent":
      return self.validateEnumReagent(pValue, pValidation)
    elif pValidation["type"] == "enum-string":
      return self.validateEnumString(pValue, pValidation)
    elif pValidation["type"] == "number":
      return self.validateNumber(pValue, pValidation)
    elif pValidation["type"] == "string":
      return self.validateString(pValue, pValidation)
    else:
      raise Exception("Unknown validation type")

  def validateEnumNumber(self, nValue, pValidation):
    """ Validates an enumeration of numbers"""
    #Is the value set?
    if nValue == 0:
      #No, so check if it is required
      if pValidation.has_key("required"):
        if pValidation["required"]:
          return False

      #Valid
      return True
    else:
      #Yes, so make sure it is set to one of the allowed values
      pValues = pValidation["values"].split(",")
      for nValidValue in pValues:
        if float(nValue) == float(nValidValue):
          #Found it
          return True

      #Invalid
      return False

  def validateEnumReagent(self, pReagent, pValidation):
    """ Validates an enumeration of reagents """
    #Is the value set?
    if not pReagent.has_key("reagentid"):
      #No, so check if it is required
      if pValidation.has_key("required"):
        if pValidation["required"]:
          return False

      #Valid
      return True
    else:
      #Yes, so validate the reagent ID
      return self.validateEnumNumber(pReagent["reagentid"], pValidation)

  def validateEnumString(self, sValue, pValidation):
    """ Validates an enumeration of strings"""
    #Is the value set?
    if sValue == "":
      #No, so check if it is required
      if pValidation.has_key("required"):
        if pValidation["required"]:
          return False

      #Valid
      return True
    else:
      #Yes, so make sure it is set to one of the allowed values
      pValues = pValidation["values"].split(",")
      for sValidValue in pValues:
        if sValue == sValidValue:
          #Found it
          return True

      #Invalid
      return False

  def validateNumber(self, nValue, pValidation):
    """ Validates a number """
    #Is the value set?
    if nValue == 0:
      #No, so check if it is required
      if pValidation.has_key("required"):
        if pValidation["required"]:
          return False

      #Valid
      return True
    else:
      #Yes, so make sure it within the acceptable range
      if (float(nValue) >= float(pValidation["min"])) and (float(nValue) <= float(pValidation["max"])):
        return True
      else:
        return False

  def validateString(self, sValue, pValidation):
    """ Validates a string """
    #Is the value set?
    if sValue == "":
      #No, so check if it is required
      if pValidation.has_key("required"):
        if pValidation["required"]:
          return False

    #Valid
    return True

  def getReagentByID(self, nReagentID, pReagents, bPopReagent):
    """ Locates the next reagent that matches the ID and returns it, optionally popping it off the list """
    nIndex = 0
    for pReagent in pReagents:
      if pReagent["reagentid"] == nReagentID:
        if bPopReagent:
          return pReagents.pop(nIndex)
        else:
          return pReagents[nIndex]
      nIndex += 1
    return None

  def listReagents(self, pReagents):
    """ Formats a list of reagent IDs """
    sReagentIDs = ""
    pUsedNames = {}
    for pReagent in pReagents:
      #Skip columns
      if not self.isNumber(pReagent["position"]):
        continue

      #Skip duplicate reagent names
      if pUsedNames.has_key(pReagent["name"]):
        continue
      else:
        pUsedNames[pReagent["name"]] = ""

      #Append the reagent ID
      if sReagentIDs != "":
        sReagentIDs += ","
      sReagentIDs += str(pReagent["reagentid"])
    return sReagentIDs

  def isNumber(self, sValue):
    """ Check if the string contains a number """
    try:
      int(sValue)
      return True
    except ValueError:
      return False

  def addComponentDetails(self):
    """Adds details to the component after retrieving it from the database and prior to sending it to the client"""
    # Base handler does nothing
    pass

  def updateComponentDetails(self, pTargetComponent):
    """Strips a component down to only the details we want to save in the database"""
    # Base handler updates the type and componenttype if they don't exist in the target component
    if not pTargetComponent.has_key("type"):
      pTargetComponent["type"] = self.component["type"]
      pTargetComponent["componenttype"] = self.component["componenttype"]

  def copyComponent(self, nSequenceID):
    """Creates a copy of the component in the database"""
    # Pull the original component from the database and create a deep copy
    pDBComponent = self.database.GetComponent(self.username, self.component["id"])
    pComponentCopy = copy.deepcopy(pDBComponent)

    # Allow the derived class a chance to alter the component copy
    self.copyComponentImpl(nSequenceID, pComponentCopy)

    # Add the component to the database and return the ID
    nComponentCopyID = self.database.CreateComponent(self.username, nSequenceID, pComponentCopy["componenttype"], pComponentCopy["name"], 
      json.dumps(pComponentCopy))
    print "### Copied " + str(pComponentCopy) + " to " + str(nComponentCopyID)
    return nComponentCopyID

  def copyComponentImpl(self, nSequenceID, pComponentCopy):
    """Performs unit-operation specific copying"""
    pass

class Initialize(UnitOperation):
  def __init__(self,systemModel,params,username = "", database = None):
    UnitOperation.__init__(self,systemModel,username,database)
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
        self.setStopcockPosition(TRANSFERDEFAULT,self.ReactorID)
      self.setStopcockPosition(F18DEFAULT,"Reactor1")

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
      
  def initializeComponent(self, pComponent):
    """Initializes the component validation fields"""
    self.component = pComponent
    self.addComponentDetails()

  def validateFull(self, pAvailableReagents):
    """Performs a full validation on the component"""
    self.component["name"] = "Initialize"
    return self.validateQuick()

  def validateQuick(self):
    """Performs a quick validation on the component"""
    self.component.update({"validationerror":False})
    return True

  def saveValidation(self):
    """Saves validation-specific fields back to the database"""
    # Pull the original component from the database
    pDBComponent = self.database.GetComponent(self.username, self.component["id"])

    # Copy the validation fields
    pDBComponent["name"] = self.component["name"]
    pDBComponent["validationerror"] = self.component["validationerror"]

    # Save the component
    self.database.UpdateComponent(self.username, self.component["id"], pDBComponent["componenttype"], pDBComponent["name"], json.dumps(pDBComponent))

class React(UnitOperation):
  def __init__(self,systemModel,params,username = "", database = None):
    UnitOperation.__init__(self,systemModel,username,database)
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

  def initializeComponent(self, pComponent):
    """Initializes the component validation fields"""
    self.component = pComponent
    if not self.component.has_key("reactorvalidation"):
      self.component.update({"reactorvalidation":""})
    if not self.component.has_key("positionvalidation"):
      self.component.update({"positionvalidation":""})
    if not self.component.has_key("durationvalidation"):
      self.component.update({"durationvalidation":""})
    if not self.component.has_key("reactiontemperaturevalidation"):
      self.component.update({"reactiontemperaturevalidation":""})
    if not self.component.has_key("finaltemperaturevalidation"):
      self.component.update({"finaltemperaturevalidation":""})
    if not self.component.has_key("stirspeedvalidation"):
      self.component.update({"stirspeedvalidation":""})
    self.addComponentDetails()

  def validateFull(self, pAvailableReagents):
    """Performs a full validation on the component"""
    self.component["name"] = "React"
    self.component["reactorvalidation"] = "type=enum-number; values=1,2,3; required=true"
    self.component["positionvalidation"] = "type=enum-number; values=1,2; required=true"
    self.component["durationvalidation"] = "type=number; min=0; max=7200; required=true"
    self.component["reactiontemperaturevalidation"] = "type=number; min=20; max=200; required=true"
    self.component["finaltemperaturevalidation"] = "type=number; min=20; max=200; required=true"
    self.component["stirspeedvalidation"] = "type=number; min=0; max=5000; required=true"

    #Do a quick validation
    return self.validateQuick()

  def validateQuick(self):
    """Performs a quick validation on the component"""
    #Validate all fields
    bValidationError = False
    if not self.validateComponentField(self.component["reactor"], self.component["reactorvalidation"]) or \
       not self.validateComponentField(self.component["position"], self.component["positionvalidation"]) or \
       not self.validateComponentField(self.component["duration"], self.component["durationvalidation"]) or \
       not self.validateComponentField(self.component["reactiontemperature"], self.component["reactiontemperaturevalidation"]) or \
       not self.validateComponentField(self.component["finaltemperature"], self.component["finaltemperaturevalidation"]) or \
       not self.validateComponentField(self.component["stirspeed"], self.component["stirspeedvalidation"]):
      bValidationError = True

    # Set the validation error field
    self.component.update({"validationerror":bValidationError})
    return not bValidationError

  def saveValidation(self):
    """Saves validation-specific fields back to the database"""
    # Pull the original component from the database
    pDBComponent = self.database.GetComponent(self.username, self.component["id"])

    # Copy the validation fields
    pDBComponent["name"] = self.component["name"]
    pDBComponent["reactorvalidation"] = self.component["reactorvalidation"]
    pDBComponent["positionvalidation"] = self.component["positionvalidation"]
    pDBComponent["durationvalidation"] = self.component["durationvalidation"]
    pDBComponent["reactiontemperaturevalidation"] = self.component["reactiontemperaturevalidation"]
    pDBComponent["finaltemperaturevalidation"] = self.component["finaltemperaturevalidation"]
    pDBComponent["stirspeedvalidation"] = self.component["stirspeedvalidation"]
    pDBComponent["validationerror"] = self.component["validationerror"]

    # Save the component
    self.database.UpdateComponent(self.username, self.component["id"], pDBComponent["componenttype"], pDBComponent["name"], json.dumps(pDBComponent))
      
  def updateComponentDetails(self, pTargetComponent):
    """Strips a component down to only the details we want to save in the database"""
    # Call the base handler
    UnitOperation.updateComponentDetails(pTargetComponent)

    # Update the fields we want to save
    pTargetComponent["reactor"] = self.component["reactor"]
    pTargetComponent["position"] = self.component["position"]
    pTargetComponent["duration"] = self.component["duration"]
    pTargetComponent["reactiontemperature"] = self.component["reactiontemperature"]
    pTargetComponent["finaltemperature"] = self.component["finaltemperature"]
    pTargetComponent["stirspeed"] = self.component["stirspeed"]

class Move(UnitOperation):
  def __init__(self,systemModel,params,username = "", database = None):
    UnitOperation.__init__(self,systemModel,username,database)
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
    
  def initializeComponent(self, pComponent):
    """Initializes the component validation fields"""
    self.component = pComponent
    if not self.component.has_key("reactorvalidation"):
      self.component.update({"reactorvalidationvalidation":""})
    if not self.component.has_key("positionvalidation"):
      self.component.update({"positionvalidation":""})
    self.addComponentDetails()

  def validateFull(self, pAvailableReagents):
    """Performs a full validation on the component"""
    self.component["name"] = "Move"
    self.component["reactorvalidation"] = "type=enum-number; values=1,2,3; required=true"
    self.component["positionvalidation"] = "type=enum-string; values=" + (",").join(self.database.GetReactorPositions(self.username)) + "; required=true"
    return self.validateQuick()

  def validateQuick(self):
    """Performs a quick validation on the component"""
    #Validate all fields
    bValidationError = False
    if not self.validateComponentField(self.component["reactor"], self.component["reactorvalidation"]) or \
       not self.validateComponentField(self.component["position"], self.component["positionvalidation"]):
      bValidationError = True

    # Set the validation error field
    self.component.update({"validationerror":bValidationError})
    return not bValidationError

  def saveValidation(self):
    """Saves validation-specific fields back to the database"""
    # Pull the original component from the database
    pDBComponent = self.database.GetComponent(self.username, self.component["id"])

    # Copy the validation fields
    pDBComponent["name"] = self.component["name"]
    pDBComponent["reactorvalidation"] = self.component["reactorvalidation"]
    pDBComponent["positionvalidation"] = self.component["positionvalidation"]
    pDBComponent["validationerror"] = self.component["validationerror"]

    # Save the component
    self.database.UpdateComponent(self.username, self.component["id"], pDBComponent["componenttype"], pDBComponent["name"], json.dumps(pDBComponent))

  def updateComponentDetails(self, pTargetComponent):
    """Strips a component down to only the details we want to save in the database"""
    # Call the base handler
    UnitOperation.updateComponentDetails(pTargetComponent)

    # Update the fields we want to save
    pTargetComponent["reactor"] = self.component["reactor"]
    pTargetComponent["position"] = self.component["position"]

class Add(UnitOperation):
  def __init__(self,systemModel,params,username = "", database = None):
    UnitOperation.__init__(self,systemModel,username,database)
    expectedParams = {REACTORID:STR,REAGENTREACTORID:STR,REAGENTPOSITION:INT,REAGENTLOADPOSITION:INT,PRESSURE:FLOAT,DURATION:INT}
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
    #self.duration
    #self.pressure

  def run(self):
    try:
      self.setStatus("Adjusting pressure")
      self.setPressureRegulator(2,self.pressure)   #Set delivery pressure
      self.setStatus("Moving reactor")
      self.setReactorPosition(ADDREAGENT)          #Move reactor to position
      self.setStatus("Picking up reagent")
      self.setGripperPlace()                       #Move reagent to the addition position.
      self.setStatus("Delivering reagent")
      self.startTimer(self.duration)               #In seconds
      self.waitForTimer()                          #Wait for Dispense reagent
      self.setStatus("Returning reagent")
      self.setGripperRemove()                      #Return vial to its starting location
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

    #Make sure the reagent robots are enabled
    if not(self.checkForCondition(self.systemModel['ReagentDelivery'].getRobotStatus,(ENABLED,ENABLED),EQUAL)):
      self.systemModel['ReagentDelivery'].setEnableRobots()
      self.waitForCondition(self.systemModel['ReagentDelivery'].getRobotStatus,(ENABLED,ENABLED),EQUAL,3)

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

    #Turn off the transfer gas and move up
    self.setReagentTransferValves(OFF)
    time.sleep(0.25)
    self.systemModel['ReagentDelivery'].setMoveGripperUp()
    self.waitForCondition(self.systemModel['ReagentDelivery'].getCurrentGripperUp,True,EQUAL,3)

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

  def initializeComponent(self, pComponent):
    """Initializes the component validation fields"""
    self.component = pComponent
    if not self.component.has_key("reactorvalidation"):
      self.component.update({"reactorvalidation":""})
    if not self.component.has_key("reagentreactorvalidation"):
      self.component.update({"reagentreactorvalidation":""})
    if not self.component.has_key("reagentvalidation"):
      self.component.update({"reagentvalidation":""})
    if not self.component.has_key("deliverypositionvalidation"):
      self.component.update({"deliverypositionvalidation":""})
    if not self.component.has_key("deliverytimevalidation"):
      self.component.update({"deliverytimevalidation":""})
    if not self.component.has_key("deliverypressurevalidation"):
      self.component.update({"deliverypressurevalidation":""})
    self.addComponentDetails()

  def validateFull(self, pAvailableReagents):
    """Performs a full validation on the component"""
    self.component["name"] = "Add"
    self.component["reactorvalidation"] = "type=enum-number; values=1,2,3; required=true"
    self.component["reagentreactorvalidation"] = "type=enum-number; values=1,2,3; required=true"
    self.component["reagentvalidation"] = "type=enum-reagent; values=" + self.listReagents(pAvailableReagents) + "; required=true"
    self.component["deliverypositionvalidation"] = "type=enum-number; values=1,2; required=true"
    self.component["deliverytimevalidation"] = "type=number; min=0; max=10"
    self.component["deliverypressurevalidation"] = "type=number; min=0; max=15"

    #Look up the reagent we are adding and remove it from the list of available reagents
    if self.component["reagent"].has_key("reagentid"):
      pReagent = self.getReagentByID(self.component["reagent"]["reagentid"], pAvailableReagents, True)
      if pReagent != None:
        #Set the component name
        self.component["name"] = "Add " + pReagent["name"]

    #Do a quick validation
    return self.validateQuick()

  def validateQuick(self):
    """Performs a quick validation on the component"""
    #Validate all fields
    bValidationError = False
    if not self.validateComponentField(self.component["reactor"], self.component["reactorvalidation"]) or \
       not self.validateComponentField(self.component["reagentreactor"], self.component["reagentreactorvalidation"]) or \
       not self.validateComponentField(self.component["reagent"], self.component["reagentvalidation"]) or \
       not self.validateComponentField(self.component["deliveryposition"], self.component["deliverypositionvalidation"]) or \
       not self.validateComponentField(self.component["deliverytime"], self.component["deliverytimevalidation"]) or \
       not self.validateComponentField(self.component["deliverypressure"], self.component["deliverypressurevalidation"]):
      bValidationError = True

    # Set the validation error field
    self.component.update({"validationerror":bValidationError})
    return not bValidationError

  def saveValidation(self):
    """Saves validation-specific fields back to the database"""
    # Pull the original component from the database
    pDBComponent = self.database.GetComponent(self.username, self.component["id"])

    # Copy the validation fields
    pDBComponent["name"] = self.component["name"]
    pDBComponent["reactorvalidation"] = self.component["reactorvalidation"]
    pDBComponent["reagentreactorvalidation"] = self.component["reagentreactorvalidation"]
    pDBComponent["reagentvalidation"] = self.component["reagentvalidation"]
    pDBComponent["deliverypositionvalidation"] = self.component["deliverypositionvalidation"]
    pDBComponent["deliverytimevalidation"] = self.component["deliverytimevalidation"]
    pDBComponent["deliverypressurevalidation"] = self.component["deliverypressurevalidation"]
    pDBComponent["deliverytime"] = self.component["deliverytime"]
    pDBComponent["deliverypressure"] = self.component["deliverypressure"]
    pDBComponent["validationerror"] = self.component["validationerror"]

    # Save the component
    self.database.UpdateComponent(self.username, self.component["id"], pDBComponent["componenttype"], pDBComponent["name"], json.dumps(pDBComponent))

  def addComponentDetails(self):
    """Adds details to the component after retrieving it from the database and prior to sending it to the client"""
    # Skip if we've already updated the reagent
    try:
      int(self.component["reagent"])
    except TypeError:
      return

    # Look up the reagent we are adding
    pAddReagent = {}
    if self.component["reagent"] != 0:
      pAddReagent = self.database.GetReagent(self.username, self.component["reagent"])

    # Replace the reagent
    del self.component["reagent"]
    self.component["reagent"] = pAddReagent

    # Set the default delivery time and pressure
    if self.component["deliverytime"] == 0:
      self.component["deliverytime"] = DEFAULT_ADD_DELIVERYTIME
    if self.component["deliverypressure"] == 0:
      self.component["deliverypressure"]= DEFAULT_ADD_DELIVERYPRESSURE

  def updateComponentDetails(self, pTargetComponent):
    """Strips a component down to only the details we want to save in the database"""
    # Call the base handler
    UnitOperation.updateComponentDetails(pTargetComponent)

    # Update the fields we want to save
    pTargetComponent["reactor"] = self.component["reactor"]
    pTargetComponent["reagentreactor"] = self.component["reagentreactor"]
    pTargetComponent["deliveryposition"] = self.component["deliveryposition"]
    pTargetComponent["deliverytime"] = self.component["deliverytime"]
    pTargetComponent["deliverypressure"] = self.component["deliverypressure"]
    pTargetComponent["reagent"] = self.component["reagent"]
    if pTargetComponent["reagent"] != 0:
      pReagent = self.database.GetReagent(self.username, pTargetComponent["reagent"])
      pTargetComponent.update({"name":"Add " + pReagent["name"]})
    else:
      pTargetComponent.update({"name":"Add"})

  def copyComponentImpl(self, nSequenceID, pComponentCopy):
    """Performs unit-operation specific copying"""
    print "### Implement Add.copyComponent"

class Evaporate(UnitOperation):
  def __init__(self,systemModel,params,username = "", database = None):
    UnitOperation.__init__(self,systemModel,username,database)
    expectedParams = {REACTORID:STR,EVAPTEMP:FLOAT,PRESSURE:FLOAT,EVAPTIME:INT,COOLTEMP:INT,STIRSPEED:INT}
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
      self.setPressureRegulator(2,self.pressure/3)
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
      self.setPressureRegulator(2,self.pressure,self.evapTime/2) #Ramp pressure over the first half of the evaporation
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
      
  def initializeComponent(self, pComponent):
    """Initializes the component validation fields"""
    self.component = pComponent
    if not self.component.has_key("reactorvalidation"):
      self.component.update({"reactorvalidation":""})
    if not self.component.has_key("durationvalidation"):
      self.component.update({"durationvalidation":""})
    if not self.component.has_key("evaporationtemperaturevalidation"):
      self.component.update({"evaporationtemperaturevalidation":""})
    if not self.component.has_key("finaltemperaturevalidation"):
      self.component.update({"finaltemperaturevalidation":""})
    if not self.component.has_key("stirspeedvalidation"):
      self.component.update({"stirspeedvalidation":""})
    if not self.component.has_key("evaporationpressurevalidation"):
      self.component.update({"evaporationpressurevalidation":""})
    self.addComponentDetails()

  def validateFull(self, pAvailableReagents):
    """Performs a full validation on the component"""
    self.component["name"] = "Evaporate"
    self.component["reactorvalidation"] = "type=enum-number; values=1,2,3; required=true"
    self.component["durationvalidation"] = "type=number; min=0; max=7200; required=true"
    self.component["evaporationtemperaturevalidation"] = "type=number; min=20; max=200; required=true"
    self.component["finaltemperaturevalidation"] = "type=number; min=20; max=200; required=true"
    self.component["stirspeedvalidation"] = "type=number; min=0; max=5000; required=true"
    self.component["evaporationpressurevalidation"] = "type=number; min=0; max=25"
    return self.validateQuick()

  def validateQuick(self):
    """Performs a quick validation on the component"""
    #Validate all fields
    bValidationError = False
    if not self.validateComponentField(self.component["reactor"], self.component["reactorvalidation"]) or \
       not self.validateComponentField(self.component["duration"], self.component["durationvalidation"]) or \
       not self.validateComponentField(self.component["evaporationtemperature"], self.component["evaporationtemperaturevalidation"]) or \
       not self.validateComponentField(self.component["finaltemperature"], self.component["finaltemperaturevalidation"]) or \
       not self.validateComponentField(self.component["stirspeed"], self.component["stirspeedvalidation"]) or \
       not self.validateComponentField(self.component["evaporationpressure"], self.component["evaporationpressurevalidation"]):
        bValidationError = True

    # Set the validation error field
    self.component.update({"validationerror":bValidationError})
    return not bValidationError

  def saveValidation(self):
    """Saves validation-specific fields back to the database"""
    # Pull the original component from the database
    pDBComponent = self.database.GetComponent(self.username, self.component["id"])

    # Copy the validation fields
    pDBComponent["name"] = self.component["name"]
    pDBComponent["reactorvalidation"] = self.component["reactorvalidation"]
    pDBComponent["durationvalidation"] = self.component["durationvalidation"]
    pDBComponent["evaporationtemperaturevalidation"] = self.component["evaporationtemperaturevalidation"]
    pDBComponent["finaltemperaturevalidation"] = self.component["finaltemperaturevalidation"]
    pDBComponent["stirspeedvalidation"] = self.component["stirspeedvalidation"]
    pDBComponent["evaporationpressurevalidation"] = self.component["evaporationpressurevalidation"]
    pDBComponent["evaporationpressure"] = self.component["evaporationpressure"]
    pDBComponent["validationerror"] = self.component["validationerror"]

    # Save the component
    self.database.UpdateComponent(self.username, self.component["id"], pDBComponent["componenttype"], pDBComponent["name"], json.dumps(pDBComponent))

  def addComponentDetails(self):
    """Adds details to the component after retrieving it from the database and prior to sending it to the client"""
    # Set the default evaporation pressure if the value is zero
    if self.component["evaporationpressure"] == 0:
      self.component["evaporationpressure"] = DEFAULT_EVAPORATE_PRESSURE

  def updateComponentDetails(self, pTargetComponent):
    """Strips a component down to only the details we want to save in the database"""
    # Call the base handler
    UnitOperation.updateComponentDetails(pTargetComponent)

    # Update the fields we want to save
    pTargetComponent["reactor"] = self.component["reactor"]
    pTargetComponent["duration"] = self.component["duration"]
    pTargetComponent["evaporationtemperature"] = self.component["evaporationtemperature"]
    pTargetComponent["finaltemperature"] = self.component["finaltemperature"]
    pTargetComponent["stirspeed"] = self.component["stirspeed"]
    pTargetComponent["evaporationpressure"] = self.component["evaporationpressure"]

class Install(UnitOperation):
  def __init__(self,systemModel,params,username = "", database = None):
    UnitOperation.__init__(self,systemModel,username,database)
    self.setParams(params)
		#Should have parameters listed below:
    #self.ReactorID
    #self.userMessage
    
  def run(self):
    try:
      self.setStatus("Moving reactor")
      self.setReactorPosition(INSTALL)
      self.setStatus("Complete")
    except Exception as e:
      self.abortOperation(e)
      
  def initializeComponent(self, pComponent):
    """Initializes the component validation fields"""
    self.component = pComponent
    if not self.component.has_key("reactorvalidation"):
      self.component.update({"reactorvalidation":""})
    if not self.component.has_key("messagevalidation"):
      self.component.update({"messagevalidation":""})
    self.addComponentDetails()

  def validateFull(self, pAvailableReagents):
    """Performs a full validation on the component"""
    self.component["name"] = "Install"
    self.component["reactorvalidation"] = "type=enum-number; values=1,2,3; required=true"
    self.component["messagevalidation"] = "type=string; required=true"
    return self.validateQuick()

  def validateQuick(self):
    """Performs a quick validation on the component"""
    #Validate all fields
    bValidationError = False
    if not self.validateComponentField(self.component["reactor"], self.component["reactorvalidation"]) or \
       not self.validateComponentField(self.component["message"], self.component["messagevalidation"]):
      bValidationError = True

    # Set the validation error field
    self.component.update({"validationerror":bValidationError})
    return not bValidationError

  def saveValidation(self):
    """Saves validation-specific fields back to the database"""
    # Pull the original component from the database
    pDBComponent = self.database.GetComponent(self.username, self.component["id"])

    # Copy the validation fields
    pDBComponent["name"] = self.component["name"]
    pDBComponent["reactorvalidation"] = self.component["reactorvalidation"]
    pDBComponent["messagevalidation"] = self.component["messagevalidation"]
    pDBComponent["validationerror"] = self.component["validationerror"]

    # Save the component
    self.database.UpdateComponent(self.username, self.component["id"], pDBComponent["componenttype"], pDBComponent["name"], json.dumps(pDBComponent))

  def updateComponentDetails(self, pTargetComponent):
    """Strips a component down to only the details we want to save in the database"""
    # Call the base handler
    UnitOperation.updateComponentDetails(pTargetComponent)

    # Update the fields we want to save
    pTargetComponent["reactor"] = self.component["reactor"]
    pTargetComponent["message"] = self.omponent["message"]

class DeliverF18(UnitOperation):
  def __init__(self,systemModel,params,username = "", database = None):
    UnitOperation.__init__(self,systemModel,username,database)
    self.setParams(params)
    self.ReactorID='Reactor1'
    #Should have parameters listed below:
    #self.trapTime
    #self.trapPressure
    #self.eluteTime
    #self.elutePressure
    self.cyclotronFlag = False##Edit when user input possible
    
  def run(self):
    try:
      self.setStatus("Adjusting pressure")
      self.setPressureRegulator(2,0) #Vent pressure to avoid delivery issues
      self.setStatus("Moving reactor")
      self.setReactorPosition(ADDREAGENT)
      self.setStatus("Trapping")
      self.setStopcockPosition(F18TRAP)
      time.sleep(0.5)
      self.F18Trap(self.trapTime,self.trapPressure)
      self.setStatus("Adjusting pressure")
      self.setPressureRegulator(2,0) #Vent pressure to avoid delivery issues
      self.setStatus("Eluting")
      self.setStopcockPosition(F18ELUTE)
      time.sleep(0.5)
      self.F18Elute(self.eluteTime,self.elutePressure)
      self.setStopcockPosition(F18DEFAULT)
      self.setStatus("Complete")
    except Exception as e:
      self.abortOperation(e)
      
  def F18Trap(self,time,pressure):
    self.systemModel['ExternalSystems'].setF18LoadValveOpen(ON)  
    self.waitForCondition(self.systemModel['ExternalSystems'].getF18LoadValveOpen,ON,EQUAL,5)
    self.timerShowInStatus = False
    self.setPressureRegulator(2,pressure,5) #Set pressure after valve is opened
    if (self.cyclotronFlag):
      ##Wait for user to click OK
      pass
    else:
      self.startTimer(time)
      self.waitForTimer()
    self.systemModel['ExternalSystems'].setF18LoadValveOpen(OFF)
    self.waitForCondition(self.systemModel['ExternalSystems'].getF18LoadValveOpen,OFF,EQUAL,5)
    
  def F18Elute(self,time,pressure):
    self.systemModel['ExternalSystems'].setF18EluteValveOpen(ON)
    self.waitForCondition(self.systemModel['ExternalSystems'].getF18EluteValveOpen,ON,EQUAL,5)
    self.timerShowInStatus = False
    self.setPressureRegulator(2,pressure,5)
    self.startTimer(time)
    self.waitForTimer()
    self.systemModel['ExternalSystems'].setF18EluteValveOpen(OFF)
    self.waitForCondition(self.systemModel['ExternalSystems'].getF18EluteValveOpen,OFF,EQUAL,5)

  def initializeComponent(self, pComponent):
    """Initializes the component validation fields"""
    self.component = pComponent
    if not self.component.has_key("reactorvalidation"):
      self.component.update({"reactorvalidation":""})
    if not self.component.has_key("traptimevalidation"):
      self.component.update({"traptimevalidation":""})
    if not self.component.has_key("trappressurevalidation"):
      self.component.update({"trappressurevalidation":""})
    if not self.component.has_key("elutepressurevalidation"):
      self.component.update({"elutepressurevalidation":""})
    if not self.component.has_key("elutetimevalidation"):
      self.component.update({"elutetimevalidation":""})
    self.addComponentDetails()

  def validateFull(self, pAvailableReagents):
    """Performs a full validation on the component"""
    self.component["name"] = "Deliver F18"
    self.component["reactorvalidation"] = "type=enum-number; values=1,2,3; required=true"
    self.component["traptimevalidation"] = "type=number; min=0; max=7200; required=true"
    self.component["trappressurevalidation"] = "type=number; min=0; max=25"
    self.component["elutetimevalidation"] = "type=number; min=0; max=7200; required=true"
    self.component["elutepressurevalidation"] = "type=number; min=0; max=25"
    return self.validateQuick()

  def validateQuick(self):
    """Performs a quick validation on the component"""
    #Validate all fields
    bValidationError = False
    if not self.validateComponentField(self.component["reactor"], self.component["reactorvalidation"]) or \
       not self.validateComponentField(self.component["traptime"], self.component["traptimevalidation"]) or \
       not self.validateComponentField(self.component["trappressure"], self.component["trappressurevalidation"]) or \
       not self.validateComponentField(self.component["elutetime"], self.component["elutetimevalidation"]) or \
       not self.validateComponentField(self.component["elutepressure"], self.component["elutepressurevalidation"]):
      bValidationError = True

    # Set the validation error field
    self.component.update({"validationerror":bValidationError})
    return not bValidationError

  def saveValidation(self):
    """Saves validation-specific fields back to the database"""
    # Pull the original component from the database
    pDBComponent = self.database.GetComponent(self.username, self.component["id"])

    # Copy the validation fields
    pDBComponent["name"] = self.component["name"]
    pDBComponent["reactorvalidation"] = self.component["reactorvalidation"]
    pDBComponent["traptimevalidation"] = self.component["traptimevalidation"]
    pDBComponent["trappressurevalidation"] = self.component["trappressurevalidation"]
    pDBComponent["elutetimevalidation"] = self.component["elutetimevalidation"]
    pDBComponent["elutepressurevalidation"] = self.component["elutepressurevalidation"]
    pDBComponent["validationerror"] = self.component["validationerror"]

    # Save the component
    self.database.UpdateComponent(self.username, self.component["id"], pDBComponent["componenttype"], pDBComponent["name"], json.dumps(pDBComponent))

  def updateComponentDetails(self, pTargetComponent):
    """Strips a component down to only the details we want to save in the database"""
    # Call the base handler
    UnitOperation.updateComponentDetails(pTargetComponent)

    # Update the fields we want to save
    pTargetComponent["reactor"] = self.component["reactor"]
    pTargetComponent["traptime"] = self.component["traptime"]
    pTargetComponent["trappressure"] = self.component["trappressure"]
    pTargetComponent["elutetime"] = self.component["elutetime"]
    pTargetComponent["elutepressure"] = self.component["elutepressure"]

class Transfer(UnitOperation):
  def __init__(self,systemModel,params,username = "", database = None):
    UnitOperation.__init__(self,systemModel,username,database)
    self.setParams(params) 
    #Should have parameters listed below:
    #self.ReactorID
    #self.transferReactorID
    #self.transferType
    #self.transferTimer
    #self.transferPressure
  def run(self):
    try:
      self.setStatus("Moving reactors")
      self.setReactorPosition(TRANSFER)
      self.setReactorPosition(ADDREAGENT,self.transferReactorID)
      self.setStatus("Transferring")
      if (self.transferType == "Trap"):
        self.setStopcockPosition(TRANSFERTRAP)
      elif (self.transferType == "Elute"):
        self.setStopcockPosition(TRANSFERELUTE)
      else:
        raise Exception("Unknown transfer type")
      time.sleep(0.5)
      self.startTransfer(ON)
      self.startTimer(self.transferTimer)
      self.waitForTimer()
      self.startTransfer(OFF)
      self.setStopcockPosition(TRANSFERDEFAULT)
      self.setStatus("Complete")
    except Exception as e:
      self.abortOperation(e)
      
  def initializeComponent(self, pComponent):
    """Initializes the component validation fields"""
    self.component = pComponent
    if not self.component.has_key("sourcereactorvalidation"):
      self.component.update({"sourcereactorvalidation":""})
    if not self.component.has_key("targetreactorvalidation"):
      self.component.update({"targetreactorvalidation":""})
    if not self.component.has_key("modevalidation"):
      self.component.update({"modevalidation":""})
    if not self.component.has_key("pressurevalidation"):
      self.component.update({"pressurevalidation":""})
    if not self.component.has_key("durationvalidation"):
      self.component.update({"durationvalidation":""})
    self.addComponentDetails()

  def validateFull(self, pAvailableReagents):
    """Performs a full validation on the component"""
    self.component["name"] = "Transfer"
    self.component["sourcereactorvalidation"] = "type=enum-number; values=1,2,3; required=true"
    self.component["targetreactorvalidation"] = "type=enum-number; values=1,2,3; required=true"
    self.component["modevalidation"] = "type=enum-string; values=Trap,Elute; required=true"
    self.component["pressurevalidation"] = "type=number; min=0; max=25"
    self.component["durationvalidation"] = "type=number; min=0; max=7200; required=true"
    return self.validateQuick()

  def validateQuick(self):
    """Performs a quick validation on the component"""
    #Validate all fields
    bValidationError = False
    if not self.validateComponentField(self.component["sourcereactor"], self.component["sourcereactorvalidation"]) or \
       not self.validateComponentField(self.component["targetreactor"], self.component["targetreactorvalidation"]) or \
       not self.validateComponentField(self.component["mode"], self.component["modevalidation"]) or \
       not self.validateComponentField(self.component["pressure"], self.component["pressurevalidation"]) or \
       not self.validateComponentField(self.component["duration"], self.component["durationvalidation"]):
        bValidationError = True

    # Set the validation error field
    self.component.update({"validationerror":bValidationError})
    return not bValidationError

  def saveValidation(self):
    """Saves validation-specific fields back to the database"""
    # Pull the original component from the database
    pDBComponent = self.database.GetComponent(self.username, self.component["id"])

    # Copy the validation fields
    pDBComponent["name"] = self.component["name"]
    pDBComponent["sourcereactorvalidation"] = self.component["sourcereactorvalidation"]
    pDBComponent["targetreactorvalidation"] = self.component["targetreactorvalidation"]
    pDBComponent["pressurevalidation"] = self.component["pressurevalidation"]
    pDBComponent["modevalidation"] = self.component["modevalidation"]
    pDBComponent["durationvalidation"] = self.component["durationvalidation"]
    pDBComponent["validationerror"] = self.component["validationerror"]

    # Save the component
    self.database.UpdateComponent(self.username, self.component["id"], pDBComponent["componenttype"], pDBComponent["name"], json.dumps(pDBComponent))

  def updateComponentDetails(self, pTargetComponent):
    """Strips a component down to only the details we want to save in the database"""
    # Call the base handler
    UnitOperation.updateComponentDetails(pTargetComponent)

    # Update the fields we want to save
    pTargetComponent["sourcereactor"] = self.component["sourcereactor"]
    pTargetComponent["targetreactor"] = self.component["targetreactor"]
    pTargetComponent["pressure"] = self.component["pressure"]
    pTargetComponent["mode"] = self.component["mode"]
    pTargetComponent["duration"] = self.component["duration"]

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
      
class Mix(UnitOperation):
  def __init__(self,systemModel,params,username = "", database = None):
    UnitOperation.__init__(self,systemModel,username,database)
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
  
  def initializeComponent(self, pComponent):
    """Initializes the component validation fields"""
    self.component = pComponent
    if not self.component.has_key("reactorvalidation"):
      self.component.update({"reactorvalidation":""})
    if not self.component.has_key("mixtimevalidation"):
      self.component.update({"mixtimevalidation":""})
    if not self.component.has_key("stirspeedvalidation"):
      self.component.update({"stirspeedvalidation":""})
    self.addComponentDetails()

  def validateFull(self, pAvailableReagents):
    """Performs a full validation on the component"""
    self.component["name"] = "Mix"
    self.component["reactorvalidation"] = "type=enum-number; values=1,2,3; required=true"
    self.component["mixtimevalidation"] = "type=number; min=0; max=7200; required=true"
    self.component["stirspeedvalidation"] = "type=number; min=0; max=5000; required=true"
    return self.validateQuick()

  def validateQuick(self):
    """Performs a quick validation on the component"""
    #Validate all fields
    bValidationError = False
    if not self.validateComponentField(self.component["reactor"], self.component["reactorvalidation"]) or \
       not self.validateComponentField(self.component["mixtime"], self.component["mixtimevalidation"]) or \
       not self.validateComponentField(self.component["stirspeed"], self.component["stirspeedvalidation"]):
      bValidationError = True

    # Set the validation error field
    self.component.update({"validationerror":bValidationError})
    return not bValidationError

  def saveValidation(self):
    """Saves validation-specific fields back to the database"""
    # Pull the original component from the database
    pDBComponent = self.database.GetComponent(self.username, self.component["id"])

    # Copy the validation fields
    pDBComponent["name"] = self.component["name"]
    pDBComponent["reactorvalidation"] = self.component["reactorvalidation"]
    pDBComponent["mixtimevalidation"] = self.component["mixtimevalidation"]
    pDBComponent["stirspeedvalidation"] = self.component["stirspeedvalidation"]
    pDBComponent["validationerror"] = self.component["validationerror"]

    # Save the component
    self.database.UpdateComponent(self.username, self.component["id"], pDBComponent["componenttype"], pDBComponent["name"], json.dumps(pDBComponent))

  def updateComponentDetails(self, pTargetComponent):
    """Strips a component down to only the details we want to save in the database"""
    # Call the base handler
    UnitOperation.updateComponentDetails(pTargetComponent)

    # Update the fields we want to save
    pTargetComponent["reactor"] = self.component["reactor"]
    pTargetComponent["mixtime"] = self.component["mixtime"]
    pTargetComponent["stirspeed"] = self.component["stirspeed"]

class UserInput(UnitOperation):
  def __init__(self,systemModel,params):
    raise Exception("Implement UserInput")
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
  
  def setMessageBox(self):
    self.setDescription("Waiting for user input")
    self.waitForUser = True
    self.waitForCondition(self.getUserInput,True,EQUAL,65535) #timeout = Infinite
    self.setDescription()
    
  def getUserInput(self):
    return not(self.waitForUser)
    
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

class Cassette(UnitOperation):
  def __init__(self,systemModel,params,username = "", database = None):
    UnitOperation.__init__(self,systemModel,username,database)

  def run(self):
    #This unit operation doesn't do anything when run
    pass
  
  def initializeComponent(self, pComponent):
    """Initializes the component validation fields"""
    self.component = pComponent
    self.addComponentDetails()

  def validateFull(self, pAvailableReagents):
    """Performs a full validation on the component"""
    return self.validateQuick()

  def validateQuick(self):
    """Performs a quick validation on the component"""
    #Validate all reagents
    bValidationError = False
    for pReagent in self.component["reagents"]:
      if pReagent["available"]:
        if not self.validateComponentField(pReagent["name"], pReagent["namevalidation"]) or \
           not self.validateComponentField(pReagent["description"], pReagent["descriptionvalidation"]):
          bValidationError = True

    # Set the validation error field
    self.component.update({"validationerror":bValidationError})
    return not bValidationError

  def saveValidation(self):
    """Saves validation-specific fields back to the database"""
    # Pull the original component from the database
    pDBComponent = self.database.GetComponent(self.username, self.component["id"])

    # Copy the validation fields
    pDBComponent["name"] = self.component["name"]
    pDBComponent["validationerror"] = self.component["validationerror"]

    # Save the component
    self.database.UpdateComponent(self.username, self.component["id"], pDBComponent["componenttype"], pDBComponent["name"], json.dumps(pDBComponent))

  def addComponentDetails(self):
    """Adds details to the component after retrieving it from the database and prior to sending it to the client"""
    # Skip if we've already updated the reagents
    if self.component.has_key("reagents"):
      return

    # Look up each reagent in this cassette
    pReagentIDs = self.component["reagentids"]
    pReagents = []
    for nReagentID in pReagentIDs:
      pReagents.append(self.database.GetReagent(self.username, nReagentID))

    del self.component["reagentids"]
    self.component["reagents"] = pReagents

  def updateComponentDetails(self, pTargetComponent):
    """Strips a component down to only the details we want to save in the database"""
    # Call the base handler
    UnitOperation.updateComponentDetails(pTargetComponent)

    # Update the field we want to save
    pTargetComponent["available"] = self.component["available"]

  def copyComponent(self, nSequenceID):
    """Creates a copy of the component in the database"""
    # Cassettes can only be copied by the database
    print "### Skipping cassette"
    pass

class Prompt(UnitOperation):
  def __init__(self,systemModel,params,username = "", database = None):
    UnitOperation.__init__(self,systemModel,username,database)

  def run(self):
    #Need to implement this (combine with UserInput unit op)
    #self.userMessage
    pass
  
  def initializeComponent(self, pComponent):
    """Initializes the component validation fields"""
    self.component = pComponent
    if not self.component.has_key("messagevalidation"):
      self.component.update({"messagevalidation":""})
    self.addComponentDetails()

  def validateFull(self, pAvailableReagents):
    """Performs a full validation on the component"""
    self.component["name"] = "Prompt"
    self.component["messagevalidation"] = "type=string; required=true"
    return self.validateQuick()

  def validateQuick(self):
    """Performs a quick validation on the component"""
    #Validate all fields
    bValidationError = not self.validateComponentField(self.component["message"], self.component["messagevalidation"])

    # Set the validation error field
    self.component.update({"validationerror":bValidationError})
    return not bValidationError

  def saveValidation(self):
    """Saves validation-specific fields back to the database"""
    # Pull the original component from the database
    pDBComponent = self.database.GetComponent(self.username, self.component["id"])

    # Copy the validation fields
    pDBComponent["name"] = self.component["name"]
    pDBComponent["messagevalidation"] = self.component["messagevalidation"]
    pDBComponent["validationerror"] = self.component["validationerror"]

    # Save the component
    self.database.UpdateComponent(self.username, self.component["id"], pDBComponent["componenttype"], pDBComponent["name"], json.dumps(pDBComponent))

  def updateComponentDetails(self, pTargetComponent):
    """Strips a component down to only the details we want to save in the database"""
    # Call the base handler
    UnitOperation.updateComponentDetails(pTargetComponent)

    # Update the field we want to save
    pTargetComponent["message"] = self.component["message"]

class Comment(UnitOperation):
  def __init__(self,systemModel,params,username = "", database = None):
    UnitOperation.__init__(self,systemModel,username,database)

  def run(self):
    #This unit operation doesn't do anything when run
    pass
  
  def initializeComponent(self, pComponent):
    """Initializes the component validation fields"""
    self.component = pComponent
    if not self.component.has_key("commentvalidation"):
      self.component.update({"commentvalidation":""})
    self.addComponentDetails()

  def validateFull(self, pAvailableReagents):
    """Performs a full validation on the component"""
    self.component["name"] = "Comment"
    self.component["commentvalidation"] = "type=string"
    return self.validateQuick()

  def validateQuick(self):
    """Performs a quick validation on the component"""
    #Validate all fields
    bValidationError = not self.validateComponentField(self.component["comment"], self.component["commentvalidation"])

    # Set the validation error field
    self.component.update({"validationerror":bValidationError})
    return not bValidationError

  def saveValidation(self):
    """Saves validation-specific fields back to the database"""
    # Pull the original component from the database
    pDBComponent = self.database.GetComponent(self.username, self.component["id"])

    # Copy the validation fields
    pDBComponent["name"] = self.component["name"]
    pDBComponent["commentvalidation"] = self.component["commentvalidation"]
    pDBComponent["validationerror"] = self.component["validationerror"]

    # Save the component
    self.database.UpdateComponent(self.username, self.component["id"], pDBComponent["componenttype"], pDBComponent["name"], json.dumps(pDBComponent))

  def updateComponentDetails(self, pTargetComponent):
    """Strips a component down to only the details we want to save in the database"""
    # Call the base handler
    UnitOperation.updateComponentDetails(pTargetComponent)

    # Update the field we want to save
    pTargetComponent["comment"] = self.component["comment"]

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
