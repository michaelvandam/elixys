"""Base unit operation"""

#Imports
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
