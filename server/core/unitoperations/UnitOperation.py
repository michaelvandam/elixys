"""Base unit operation"""

#Imports
import time
import threading
import json
import copy
import sys
sys.path.append("/opt/elixys/database")
from DBComm import *
import urllib

#Reactor Y Positions
REACT_A    = 'React1'
REACT_B    = 'React2'
INSTALL    = 'Install'
TRANSFER   = 'Transfer'
EVAPORATE  = 'Evaporate'
ADDREAGENT = 'Add'

#Robot states
ENABLED    = 'Enabled'
DISABLED   = 'Disabled'

#Reagent robot position for transfer
TRANSFERPOSITION = 11
EVAPORATEPOSITION = 3

#Stopcock positions
NA = ''
CW = 'CW'
CCW = 'CCW'
F18DEFAULT = (NA,CCW,CCW)
F18TRAP = (NA,CCW,CW)
F18ELUTE = (NA,CW,CCW)
TRANSFERDEFAULT = (CCW,NA,NA)
TRANSFERTRAP = (CW,NA,NA)
TRANSFERELUTE = (CCW,NA,NA)

ON = True
OFF = False

EVAPTEMP  = 'evapTemp'
EVAPTIME  = 'evapTime'
REACTORID = 'ReactorID'
REACTTEMP = 'reactTemp'
REACTTIME = 'reactTime'
COOLTEMP  = 'coolTemp'
COOLINGDELAY  = 'coolingDelay'
STIRSPEED = 'stirSpeed'
REACTPOSITION = 'reactPosition'
REAGENTPOSITION = 'ReagentPosition'
REAGENTREACTORID = 'ReagentReactorID'
REAGENTLOADPOSITION = 'reagentLoadPosition'
PRESSUREREGULATOR = 'pressureRegulator'
PRESSURE = 'pressure'
DURATION = 'duration'
LIQUIDTCREACTOR = 'liquidTCReactor'
LIQUIDTCCOLLET = 'liquidTCCollet'
USERMESSAGE = 'userMessage'
CYCLOTRONFLAG = 'cyclotronFlag'
TRAPTIME = "trapTime"
TRAPPRESSURE = "trapPressure"
ELUTETIME = "eluteTime"
ELUTEPRESSURE = "elutePressure"
SUMMARYFLAG = "summaryFlag"
SUMMARYMESSAGE = "summaryMessage"
EXTERNALREAGENTNAME = "externalReagentName"

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
DEFAULT_ADD_DURATION = 15
DEFAULT_ADD_PRESSURE = 3
DEFAULT_EVAPORATE_PRESSURE = 10
DEFAULT_STIRSPEED = 500
DEFAULT_TRANSFER_DURATION = 45
DEFAULT_TRANSFER_PRESSURE = 10

class UnitOpError(Exception):
  def __init__(self, value):
    self.value = value
  def __str__(self):
    return str(self.value)

class UnitOperation(threading.Thread):
  def __init__(self,systemModel,username = "",sequenceID = 0, componentID = 0, database = None):
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
    self.sequenceID = sequenceID
    self.componentID = componentID
    self.status = ""
    self.delay = 50#50ms delay
    self.abort = False
    self.timerStartTime = 0
    self.timerLength = 0
    self.timerShowInStatus = False
    self.timerPaused = False
    self.timerPauseTime = 0
    self.timerPausedTime = 0
    self.waitingForUserInput = False
    self.error = ""

  def setParams(self,params): #Params come in as Dict, we can loop through and assign each 'key' to a variable. Eg. self.'key' = 'value'
    for paramname in params.keys():
      #print "\n%s:\n%s" % (paramname,params[paramname])
      if (paramname=="reactTemp"):
        self.reactTemp = params['reactTemp']
      elif (paramname=="reactTime"):
        self.reactTime = params['reactTime']
      elif (paramname=="evapTemp"):
        self.reactTemp = params['evapTemp']
      elif (paramname=="evapTime"):
        self.reactTime = params['evapTime']
      elif paramname=="coolTemp":
        self.coolTemp = params['coolTemp']
      elif paramname=="coolingDelay":
        self.coolingDelay = params['coolingDelay']
      elif paramname=="ReactorID":
        self.ReactorID = params['ReactorID']
      elif paramname=="ReagentReactorID":
        self.ReagentReactorID = params['ReagentReactorID']
      elif paramname=="stirSpeed":
        self.stirSpeed = params['stirSpeed']
      elif paramname=="isCheckbox":
        self.isCheckbox = params['isCheckbox']
      elif paramname=="userMessage":
        self.userMessage = params['userMessage']
      elif paramname=="description":
        self.description = params['description']
      elif paramname=="stopcockPosition":
        self.stopcockPosition = params['stopcockPosition']
      elif paramname=="transferReactorID":
        self.transferReactorID = params['transferReactorID']
      elif paramname=="reagentLoadPosition":
        self.reagentLoadPosition = params['reagentLoadPosition']
      elif paramname=="reactPosition":
        self.reactPosition = params['reactPosition']
      elif paramname=="ReagentPosition":
        self.reagentPosition = params['ReagentPosition']
      elif paramname=="trapTime":
        self.trapTime = params['trapTime']
      elif paramname=="trapPressure":
        self.trapPressure = params['trapPressure']
      elif paramname=="eluteTime":
        self.eluteTime = params['eluteTime']
      elif paramname=="elutePressure":
        self.elutePressure = params['elutePressure']
      elif paramname=="pressureRegulator":
        self.pressureRegulator = params['pressureRegulator']
      elif paramname=="pressure":
        self.pressure = params['pressure']
      elif paramname=="duration":
        self.duration = params['duration']
      elif paramname=="cyclotronFlag":
        self.cyclotronFlag = params['cyclotronFlag']
      elif paramname=="transferType":
        self.transferType = params['transferType']
      elif paramname=="transferTimer":
        self.transferTimer = params['transferTimer']
      elif paramname=="transferPressure":
        self.transferPressure = params['transferPressure']      
      elif paramname=="liquidTCReactor":
        self.liquidTCReactor = params['liquidTCReactor']      
      elif paramname=="liquidTCCollet":
        self.liquidTCCollet = params['liquidTCCollet']
      elif paramname=="summaryFlag":
        self.summaryFlag = params['summaryFlag']
      elif paramname=="summaryMessage":
        self.summaryMessage = params['summaryMessage']
      elif paramname=="externalReagentName":
        self.externalReagentName = params['externalReagentName']
      else:
        raise Exception("Unknown parameter: " + paramname)

  def logError(self, sError):
    """Logs an error string."""
    if self.database != None:
      self.database.RunLog(LOG_ERROR, self.username, self.sequenceID, self.componentID, sError)
    else:
      print sError

  def logInfo(self, sInfo):
    """Logs an information string."""
    if self.database != None:
      self.database.RunLog(LOG_INFO, self.username, self.sequenceID, self.componentID, sInfo)
    else:
      print sInfo
    
  def validateParams(self,userSetParams,expectedParamDict):
    """Validates parameters before starting unit operation"""
    errorMessage = ""
    self.paramsValid = True
    paramTypeInt = ""
    for parameter in expectedParamDict.keys():
      try:
        paramType = userSetParams[parameter].__class__.__name__
        if paramType == "unicode":
          paramType = "str"
      except:
        pass
      if not(parameter in userSetParams): #Parameter not entered in CLI
        self.paramsValid = False
        errorMessage += "Parameter: \'%s\' was not set." % parameter
      elif (not((paramType) in (STR,INT,FLOAT)) and (userSetParams[parameter])): #Check for invalid value -- Including none and empty strings.
        self.paramsValid = False
        errorMessage += "Parameter: \'%s\' was set to invalid value: \'%s\' (1)." % (parameter,userSetParams[parameter])
      else:
        if not(paramType == expectedParamDict[parameter]):
          valid = False
          try:
            if not(paramType == STR): #As long as it's not a string, check if float/int were mixed up.
              if (int(userSetParams[parameter]) == userSetParams[parameter]) and (expectedParamDict[parameter] == INT):
                valid = True
              if (float(userSetParams[parameter]) == userSetParams[parameter]) and (expectedParamDict[parameter] == FLOAT):
                valid = True
          except ValueError:
            pass
          if not(valid):
            self.paramsValid=False
            errorMessage += "Parameter: \'%s\' was set to invalid value: \'%s\' (2)." % (parameter,userSetParams[parameter])
        if (paramType == STR):
          try:
            if (int(userSetParams[parameter])) and (expectedParamDict[parameter] == STR):
              self.paramsValid=False
              errorMessage += "Parameter: \'%s\' was set to invalid value: \'%s\' (3)." % (parameter,userSetParams[parameter])
          except ValueError:
            pass
    return errorMessage
      
  def setStatus(self,status,bUpdate=False):
    self.status = status
    if not bUpdate:
      self.logInfo(urllib.unquote(status))

  def updateStatus(self,status):
    statusComponents = self.status.split(", ")
    if len(statusComponents) > 0:
       self.setStatus(statusComponents[0] + ", " + status, True)
    else:
       self.setStatus(status, True)

  def setAbort(self):
    self.abort = True
    
  def checkAbort(self):
    if self.abort:
      self.abortOperation("Operation aborted")

  def getError(self):
    return self.error

  def setReactorPosition(self,reactorPosition,ReactorID=255):
    motionTimeout = 10 #How long to wait before erroring out.
    if (ReactorID==255):
      ReactorID = self.ReactorID

    #Check if we are in the correct position
    if self.checkForCondition(self.systemModel[ReactorID]['Motion'].getCurrentPosition,reactorPosition,EQUAL):
      if not reactorPosition == INSTALL:
        if self.checkForCondition(self.systemModel[ReactorID]['Motion'].getCurrentReactorUp,True,EQUAL):
          return
      else:
        if not self.checkForCondition(self.systemModel[ReactorID]['Motion'].getCurrentReactorDown,True,EQUAL):
          return

    #Lower the reactor and enable the robot
    self.systemModel[ReactorID]['Motion'].moveReactorDown()
    self.waitForCondition(self.systemModel[ReactorID]['Motion'].getCurrentReactorDown,True,EQUAL,motionTimeout)
    if not(self.checkForCondition(self.systemModel[ReactorID]['Motion'].getCurrentRobotStatus,ENABLED,EQUAL)):
      self.systemModel[ReactorID]['Motion'].setEnableReactorRobot()      
      self.waitForCondition(self.systemModel[ReactorID]['Motion'].getCurrentRobotStatus,ENABLED,EQUAL,3)

    #Move to the correct position and raise the reactor
    self.systemModel[ReactorID]['Motion'].moveToPosition(reactorPosition)
    self.waitForCondition(self.systemModel[ReactorID]['Motion'].getCurrentPosition,reactorPosition,EQUAL,motionTimeout)
    self.systemModel[ReactorID]['Motion'].moveReactorUp()
    if reactorPosition == INSTALL:
      # Sleep briefly since we don't have up sensors for the install position
      time.sleep(0.5)
    elif reactorPosition == ADDREAGENT:
      # Nor do we have up sensors for the add position
      time.sleep(2)
    else:
      self.waitForCondition(self.systemModel[ReactorID]['Motion'].getCurrentReactorUp,True,EQUAL,motionTimeout)

    #Disable the robot
    self.systemModel[ReactorID]['Motion'].setDisableReactorRobot()
    self.waitForCondition(self.systemModel[ReactorID]['Motion'].getCurrentRobotStatus,DISABLED,EQUAL,3)
    
  def setGripperPlace(self, nElute):
    #Make sure we are open and up
    if not self.checkForCondition(self.systemModel['ReagentDelivery'].getCurrentGripperOpen,True,EQUAL):
      self.abortOperation("ERROR: setGripperPlace called while gripper was not open. Operation aborted.")
    if not self.checkForCondition(self.systemModel['ReagentDelivery'].getCurrentGripperUp,True,EQUAL):
      self.abortOperation("ERROR: setGripperPlace called while gripper was not up. Operation aborted.") 
    if not self.checkForCondition(self.systemModel['ReagentDelivery'].getCurrentGasTransferUp,True,EQUAL):
      self.abortOperation("ERROR: setGripperPlace called while gas transfer was not up. Operation aborted.") 

    #Make sure the reagent robots are enabled
    if not(self.checkForCondition(self.systemModel['ReagentDelivery'].getRobotStatus,(ENABLED,ENABLED),EQUAL)):
      self.systemModel['ReagentDelivery'].setEnableRobots()
      self.waitForCondition(self.systemModel['ReagentDelivery'].getRobotStatus,(ENABLED,ENABLED),EQUAL,3)

    #Move to the reagent position
    self.systemModel['ReagentDelivery'].moveToReagentPosition(int(self.ReagentReactorID[-1]),self.reagentPosition)
    self.waitForCondition(self.systemModel['ReagentDelivery'].getCurrentPosition,(int(self.ReagentReactorID[-1]),
      self.reagentPosition, 0, 0),EQUAL,5)

    #Move down, close and up
    self.systemModel['ReagentDelivery'].setMoveGripperDown()
    self.waitForCondition(self.systemModel['ReagentDelivery'].getCurrentGripperDown,True,EQUAL,4)
    self.systemModel['ReagentDelivery'].setMoveGripperClose()
    self.waitForCondition(self.systemModel['ReagentDelivery'].getCurrentGripperClose,True,EQUAL,3)
    self.systemModel['ReagentDelivery'].setMoveGripperUp()
    self.waitForCondition(self.systemModel['ReagentDelivery'].getCurrentGripperUp,True,EQUAL,4)

    #Move to the delivery or elute position
    if nElute == 0:
      self.systemModel['ReagentDelivery'].moveToDeliveryPosition(int(self.ReactorID[-1]),self.reagentLoadPosition)
      self.waitForCondition(self.systemModel['ReagentDelivery'].getCurrentPosition,(int(self.ReactorID[-1]),
        0, self.reagentLoadPosition, 0),EQUAL,5)
    else:
      self.systemModel['ReagentDelivery'].moveToElutePosition(int(self.ReactorID[-1]))
      self.waitForCondition(self.systemModel['ReagentDelivery'].getCurrentPosition,(int(self.ReactorID[-1]), 0, 0, 1),EQUAL,5)
    
    #Lower and turn on the gas transfer
    self.systemModel['ReagentDelivery'].setMoveGasTransferDown()
    self.waitForCondition(self.systemModel['ReagentDelivery'].getCurrentGasTransferDown,True,EQUAL,3)
    self.setGasTransferValve(ON)

    #Increase the pressure and lower the vial
    self.setPressureRegulator(2,60)
    self.systemModel['ReagentDelivery'].setMoveGripperDown()
    self.waitForCondition(self.systemModel['ReagentDelivery'].getCurrentGripperDown,True,EQUAL,6)
    self.setPressureRegulator(2,47)
    
  def removeGripperPlace(self):
    #Make sure we are closed and down
    if not self.checkForCondition(self.systemModel['ReagentDelivery'].getCurrentGripperClose,True,EQUAL):
      self.abortOperation("ERROR: setGripperRemove called while gripper was not closed. Operation aborted.")
    if not self.checkForCondition(self.systemModel['ReagentDelivery'].getCurrentGripperDown,True,EQUAL):
      self.abortOperation("ERROR: setGripperRemove called while gripper was not up. Operation aborted.")

    # Remove the vial
    bVialUp = False
    nFailureCount = 0
    self.setPressureRegulator(2,60)
    time.sleep(1)
    while not bVialUp:
      #Move the vial up
      self.systemModel['ReagentDelivery'].setMoveGripperUp()
      self.waitForCondition(self.systemModel['ReagentDelivery'].getCurrentGripperUp,True,EQUAL,6)

      #Do we still have the vial?
      if self.checkForCondition(self.systemModel['ReagentDelivery'].getCurrentGripperClose,True,EQUAL):
        #Yes
        bVialUp = True
      elif nFailureCount < 3:
        #No, so pick it up again
        self.systemModel['ReagentDelivery'].setMoveGripperOpen()
        self.waitForCondition(self.systemModel['ReagentDelivery'].getCurrentGripperOpen,True,EQUAL,3)
        self.systemModel['ReagentDelivery'].setMoveGripperDown()
        self.waitForCondition(self.systemModel['ReagentDelivery'].getCurrentGripperDown,True,EQUAL,3)
        self.systemModel['ReagentDelivery'].setMoveGripperClose()
        self.waitForCondition(self.systemModel['ReagentDelivery'].getCurrentGripperClose,True,EQUAL,3)
        nFailureCount += 1
      else:
        self.setPressureRegulator(2,47)
        raise Exception("Failed to remove vial")
    self.setPressureRegulator(2,47)

    #Turn off and raise the transfer gas
    self.setGasTransferValve(OFF)
    self.systemModel['ReagentDelivery'].setMoveGasTransferUp()
    self.waitForCondition(self.systemModel['ReagentDelivery'].getCurrentGasTransferUp,True,EQUAL,3)

    #Move to ReagentPosition, then down and open
    self.systemModel['ReagentDelivery'].moveToReagentPosition(int(self.ReagentReactorID[-1]),self.reagentPosition)
    self.waitForCondition(self.systemModel['ReagentDelivery'].getCurrentPosition,(int(self.ReagentReactorID[-1]), self.reagentPosition, 0, 0),EQUAL,5)
    self.systemModel['ReagentDelivery'].setMoveGripperDown()
    #self.waitForCondition(self.systemModel['ReagentDelivery'].getCurrentGripperDown,True,EQUAL,3)
    time.sleep(2)  # This is a workaround in case the gripper slipped a little bit and the reagent vial is lower than usual
    self.systemModel['ReagentDelivery'].setMoveGripperOpen()
    self.waitForCondition(self.systemModel['ReagentDelivery'].getCurrentGripperOpen,True,EQUAL,3)
    
    #Move up and to home
    self.systemModel['ReagentDelivery'].setMoveGripperUp()
    self.waitForCondition(self.systemModel['ReagentDelivery'].getCurrentGripperUp,True,EQUAL,3)
    self.systemModel['ReagentDelivery'].moveToHomeFast()
    self.waitForCondition(self.systemModel['ReagentDelivery'].getCurrentPosition,(0,0,0,0),EQUAL,5)

  def waitForCondition(self,function,condition,comparator,timeout): #Timeout in seconds, default to 3.
    startTime = time.time()
    self.delay = 500
    self.checkAbort()
    if comparator == EQUAL:
      while not(function() == condition):
        self.stateCheckInterval(self.delay)
        if not(timeout == 65535):
          if self.isTimerExpired(startTime,timeout):
            self.logError("waitForCondition call timed out on function:%s class:%s" % (function.__name__,function.im_class))
            self.abortOperation("Function %s == %s, expected %s" % (str(function.__name__),str(function()),str(condition)))
            break
        self.checkAbort()
    elif comparator == NOTEQUAL:
      while (function() == condition):
        self.stateCheckInterval(self.delay)
        if not(timeout == 65535):
          if self.isTimerExpired(startTime,timeout):
            self.logError("waitForCondition call timed out on function:%s class:%s" % (function.__name__,function.im_class))
            self.abortOperation("Function %s == %s, expected %s" % (str(function.__name__),str(function()),str(condition)))
            break
        self.checkAbort()
    elif comparator == GREATER:
      while not(function() >= condition):
        self.stateCheckInterval(self.delay)
        if not(timeout == 65535):
          if self.isTimerExpired(startTime,timeout):
            self.logError("waitForCondition call timed out on function:%s class:%s" % (function.__name__,function.im_class))
            self.abortOperation("Function %s == %s, expected %s" % (str(function.__name__),str(function()),str(condition)))
            break            
        self.checkAbort()
    elif comparator == LESS:
      while not(function() <=condition):
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
    while self.timerPaused or not self.isTimerExpired(self.timerStartTime, self.timerLength + self.timerPausedTime):
      self.updateTimer()
      self.checkAbort()
      self.stateCheckInterval(50) #Sleep 50ms between checks
    return (time.time() - self.timerStartTime)

  def updateTimer(self):
    if self.timerShowInStatus:
      if not self.timerPaused:
        nSecondsRemaining = self.timerLength - (time.time() - self.timerStartTime) + self.timerPausedTime
        self.updateStatus("%s remaining" % self.formatTime(nSecondsRemaining))
      else:
        self.updateStatus("paused")
      
  def isTimerExpired(self,startTime,length):
    if (length == 65535):
      return False
    if (time.time()-startTime >= length):
      return True
    return False
    
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

  def pauseTimer(self):
    """Pauses the running unit operation timer"""
    if not self.timerPaused:
      self.timerPaused = True
      self.timerPauseTime = time.time()

  def continueTimer(self):
    """Continues the paused unit operation timer"""
    if self.timerPaused:
      self.timerPaused = False
      self.timerPausedTime += time.time() - self.timerPauseTime

  def stopTimer(self):
    """Stops the unit operation timer"""
    if self.timerPaused:
      self.continueTimer()
    if not self.isTimerExpired(self.timerStartTime, self.timerLength + self.timerPausedTime):
      self.timerLength = time.time() - self.timerStartTime - self.timerPausedTime

  def getTimerStatus(self):
    if self.timerStartTime == 0:
      return "None"
    if self.timerPaused:
      return "Paused"
    if not self.isTimerExpired(self.timerStartTime, self.timerLength + self.timerPausedTime):
      return "Running"
    else:
      return "Complete"

  def abortOperation(self,error,raiseException=True):
    #Safely abort -> Do not move, turn off heaters, turn set points to zero.
    for nReactor in range(1, 4):
      sReactor = "Reactor" + str(nReactor)
      self.systemModel[sReactor]['Thermocouple'].setSetPoint(OFF)
      self.systemModel[sReactor]['Thermocouple'].setHeaterOff()
    self.systemModel['CoolingSystem'].setCoolingSystemOn(OFF)
    self.error = error
    if raiseException:
      raise UnitOpError(error)
    
  def setStopcockPosition(self,stopcockPositions,ReactorID=255,adjustPressure=True):
    if (ReactorID==255):
      ReactorID = self.ReactorID
    if (adjustPressure==True):
      self.setPressureRegulator(2,60)
    for stopcock in range(1,(len(stopcockPositions)+1)):
      if not stopcockPositions[stopcock-1] == NA:
        if stopcockPositions[stopcock-1] == CW:
          self.systemModel[ReactorID]['Stopcock'+str(stopcock)].setCW()
          self.waitForCondition(self.systemModel[ReactorID]['Stopcock'+str(stopcock)].getCW,True,EQUAL,3) 
        elif stopcockPositions[stopcock-1] == CCW:
          self.systemModel[ReactorID]['Stopcock'+str(stopcock)].setCCW()
          self.waitForCondition(self.systemModel[ReactorID]['Stopcock'+str(stopcock)].getCCW,True,EQUAL,3) 
        else:
          self.abortOperation("Unknown stopcock position: " + stopcockPosition[stopcock-1])
    if (adjustPressure==True):
      time.sleep(1)
      self.setPressureRegulator(2,47)
 
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

  def setCool(self,coolingDelay = 0):
    self.systemModel[self.ReactorID]['Thermocouple'].setHeaterOff()
    self.waitForCondition(self.systemModel[self.ReactorID]['Thermocouple'].getHeaterOn,False,EQUAL,3)
    self.setCoolingSystem(ON)
    self.waitForCondition(self.systemModel[self.ReactorID]['Thermocouple'].getCurrentTemperature,self.coolTemp,LESS,65535) 
    if coolingDelay > 0:
      self.startTimer(coolingDelay)
      self.waitForTimer()
    self.setCoolingSystem(OFF)
    
  def setStirSpeed(self,stirSpeed):
    if (stirSpeed == OFF): #Fix issue with False being misinterpreted.
      stirSpeed = 0
    self.systemModel[self.ReactorID]['Stir'].setSpeed(stirSpeed) #Set analog value on PLC
    self.waitForCondition(self.systemModel[self.ReactorID]['Stir'].getCurrentSpeed,stirSpeed,EQUAL,10) #Read value from PLC memory... should be equal
  
  def setGasTransferValve(self,valveSetting):
    if (valveSetting):
      self.systemModel['Valves'].setGasTransferValveOpen(ON)
      self.waitForCondition(self.systemModel['Valves'].getGasTransferValveOpen,True,EQUAL,3)     
    else:
      self.systemModel['Valves'].setGasTransferValveOpen(OFF)
      self.waitForCondition(self.systemModel['Valves'].getGasTransferValveOpen,False,EQUAL,3)      
  
  def setVacuumSystem(self,systemOn):
    if (systemOn):
      self.systemModel['VacuumSystem'].setVacuumSystemOn()
      self.waitForCondition(self.systemModel['VacuumSystem'].getVacuumSystemOn,True,EQUAL,3)     
    else:
      self.systemModel['VacuumSystem'].setVacuumSystemOff()
      self.waitForCondition(self.systemModel['VacuumSystem'].getVacuumSystemOn,False,EQUAL,3)     

  def setCoolingSystem(self,systemOn):
    if (systemOn):
      self.systemModel['CoolingSystem'].setCoolingSystemOn(ON)
      self.waitForCondition(self.systemModel['CoolingSystem'].getCoolingSystemOn,ON,EQUAL,3)
    else:
      self.systemModel['CoolingSystem'].setCoolingSystemOn(OFF)
      self.waitForCondition(self.systemModel['CoolingSystem'].getCoolingSystemOn,OFF,EQUAL,3)

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
    self.waitForCondition(self.pressureSet,True,EQUAL,4)

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
    #Make sure it is set to one of the allowed values
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
    #Make sure it within the acceptable range
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
    except TypeError:
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
    return nComponentCopyID

  def copyComponentImpl(self, nSequenceID, pComponentCopy):
    """Performs unit-operation specific copying"""
    # Base handler does nothing
    pass

  def deliverUserInput(self):
    """Signal the unit operation to continue"""
    # Clear the waiting flag
    self.waitingForUserInput = False

  def waitForUserInput(self):
    """Pauses the unit operation until we get a signal to continue"""
    # Signal that we are waiting for user input
    self.waitingForUserInput = True

    # Wait until we get the signal to continue
    while self.waitingForUserInput:
      time.sleep(0.25)
      self.checkAbort()

