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

import logging
log = logging.getLogger("elixys.unitop")


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
TRANSFERPOSITION = 12
EVAPORATEPOSITION = 5

#Stopcock positions
NA = ''
CW = 'CW'
CCW = 'CCW'
F18DEFAULT = (NA,CCW,CW)
F18TRAP = (NA,CCW,CCW)
F18ELUTE = (NA,CW,CW)
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
STOPATTEMPERATURE = "stopAtTemperature"
BROADCASTFLAG = 'broadcastFlag'

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

# Pressures
GAS_TRANSFER_PRESSURE = 5
PNEUMATIC_PRESSURE = 60

# Default component values
DEFAULT_ADD_DURATION = 15
DEFAULT_ADD_PRESSURE = 3
DEFAULT_EVAPORATE_PRESSURE = 10
DEFAULT_STIRSPEED = 500
DEFAULT_TRANSFER_DURATION = 45
DEFAULT_TRANSFER_PRESSURE = 10

# Soft error values
SOFTERROR_NONE = 0
SOFTERROR_RETRY = 1
SOFTERROR_IGNORE = 2
SOFTERROR_ABORT = 4
SOFTERROR_RETRY_DESCRIPTION = "Retry"
SOFTERROR_IGNORE_DESCRIPTION = "Ignore"
SOFTERROR_ABORT_DESCRIPTION = "Abort"

# This exception is thrown on a serious error
class UnitOpError(Exception):
  def __init__(self, value):
    self.value = value
  def __str__(self):
    return str(self.value)

# This exception is thrown when an operation times out
class UnitOpTimeout(Exception):
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
    self.timerOverridden = False
    self.timerStopped = False
    self.waitingForUserInput = False
    self.error = ""
    self.softError = ""
    self.softErrorOptions = 0
    self.softErrorDecision = SOFTERROR_NONE
    self.description = ""
    self.stopAtTemperature = False
    self.cyclotronFlag = False
    self.updateStatusWhileWaiting = None

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
      elif paramname=="stopAtTemperature":
        self.stopAtTemperature = params['stopAtTemperature']
      elif paramname=="broadcastFlag":
        self.broadcastFlag = params['broadcastFlag']
      else:
        raise Exception("Unknown parameter: " + paramname)

  def logError(self, sError):
    """Logs an error string."""
    if self.database != None:
      log.error(sError)
    else:
      print sError

  def logInfo(self, sInfo):
    """Logs an information string."""
    if self.database != None:
      log.debug(sInfo)
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
    log.debug("Class:<%s> | setStatus:%s " % (self.__class__.__name__, self.status))
    if not bUpdate:
      self.logInfo(urllib.unquote(status))

  def updateStatus(self,status):
    statusComponents = self.status.split(" (")
    self.setStatus(statusComponents[0] + " (" + status + ")", True)

  def setAbort(self):
    self.abort = True
    
  def checkAbort(self):
    if self.abort:
      log.error("Oberation aborted: <%s>" % self.__class__.__name__)
      self.abortOperation("Operation aborted")

  def getError(self):
    return self.error

  def setSoftError(self, error, options):
    """Sets the flags when a soft error is encountered"""
    self.softError = error
    self.softErrorOptions = options
    self.softErrorDecision = SOFTERROR_NONE
    self.logError("Soft error encountered: " + error)

  def getSoftError(self):
    """Called by the core server to check if a soft error has occurred"""
    optionsArray = []
    if self.softErrorOptions & SOFTERROR_RETRY:
      optionsArray.append(SOFTERROR_RETRY_DESCRIPTION)
    if self.softErrorOptions & SOFTERROR_IGNORE:
      optionsArray.append(SOFTERROR_IGNORE_DESCRIPTION)
    if self.softErrorOptions & SOFTERROR_ABORT:
      optionsArray.append(SOFTERROR_ABORT_DESCRIPTION)
    return (self.softError, optionsArray)

  def setSoftErrorDecision(self, decision):
    """Called by the core server set the user's decision"""
    self.softError = ""
    self.softErrorOptions = 0
    if decision == SOFTERROR_RETRY_DESCRIPTION:
      self.softErrorDecision = SOFTERROR_RETRY
    elif decision == SOFTERROR_IGNORE_DESCRIPTION:
      self.softErrorDecision = SOFTERROR_IGNORE
    elif decision == SOFTERROR_ABORT_DESCRIPTION:
      self.softErrorDecision = SOFTERROR_ABORT

  def waitForSoftErrorDecision(self):
    """Pauses and waits for the user to decide what to do"""
    previousStatus = self.status
    self.setStatus("Error, waiting for user input")
    while self.softErrorDecision == SOFTERROR_NONE:
      time.sleep(0.25)
    self.setStatus(previousStatus)
    return self.softErrorDecision

  def doStep(self, function, error):
    """Performs the step with error handling"""
    log.debug("Do step: %s" % self.__class__.__name__)
    success = False
    while not success:
      try:
        function()
        success = True
      except UnitOpTimeout:
        self.setSoftError(error, SOFTERROR_RETRY | SOFTERROR_IGNORE | SOFTERROR_ABORT)
        option = self.waitForSoftErrorDecision()
        if option == SOFTERROR_IGNORE:
          success = True
        elif option == SOFTERROR_ABORT:
          self.abortOperation(error)

  def setReactorPosition(self,reactorPosition,ReactorID=255):
    #Determine the target reactor
    if ReactorID == 255:
      self.setReactorPosition_ReactorID = self.ReactorID
    else:
      self.setReactorPosition_ReactorID = ReactorID

    #Check if we are in the correct position
    if self.checkForCondition(self.systemModel[self.setReactorPosition_ReactorID]['Motion'].getCurrentPosition,reactorPosition,EQUAL):
      if not reactorPosition == INSTALL:
        if self.checkForCondition(self.systemModel[self.setReactorPosition_ReactorID]['Motion'].getCurrentReactorUp,True,EQUAL):
          return
      else:
        if not self.checkForCondition(self.systemModel[self.setReactorPosition_ReactorID]['Motion'].getCurrentReactorDown,True,EQUAL):
          return
          
    #Lower the pneumatic pressure if we are in one of the react positions and up
    bRestorePressure = False
    if self.checkForCondition(self.systemModel[self.setReactorPosition_ReactorID]['Motion'].getCurrentPosition,REACT_A,EQUAL) or \
        self.checkForCondition(self.systemModel[self.setReactorPosition_ReactorID]['Motion'].getCurrentPosition,REACT_B,EQUAL):
      if self.checkForCondition(self.systemModel[self.setReactorPosition_ReactorID]['Motion'].getCurrentReactorUp,True,EQUAL):
        self.setPressureRegulator(2,30)
        bRestorePressure = True

    #Lower the reactor and enable the robot
    self.doStep(self.setReactorPosition_Step1, "Failed to lower the reactor")
    if not(self.checkForCondition(self.systemModel[self.setReactorPosition_ReactorID]['Motion'].getCurrentRobotStatus,ENABLED,EQUAL)):
      self.doStep(self.setReactorPosition_Step2, "Failed to enable the reactor robot")

    #Restore the pneumatic pressure
    if bRestorePressure:
      self.setPressureRegulator(2,PNEUMATIC_PRESSURE)

    # Move to the correct position
    self.setReactorPosition_reactorPosition = reactorPosition
    self.doStep(self.setReactorPosition_Step3, "Failed to move the reactor")

    # Raise the reactor and disable the robot
    self.doStep(self.setReactorPosition_Step4, "Failed to raise the reactor")
    self.doStep(self.setReactorPosition_Step5, "Failed to disable the reactor robot")

  def setReactorPosition_Step1(self):
    self.systemModel[self.setReactorPosition_ReactorID]['Motion'].moveReactorDown()
    self.waitForCondition(self.systemModel[self.setReactorPosition_ReactorID]['Motion'].getCurrentReactorDown,True,EQUAL,10)

  def setReactorPosition_Step2(self):
    self.systemModel[self.setReactorPosition_ReactorID]['Motion'].setEnableReactorRobot()      
    self.waitForCondition(self.systemModel[self.setReactorPosition_ReactorID]['Motion'].getCurrentRobotStatus,ENABLED,EQUAL,3)

  def setReactorPosition_Step3(self):
    # Move to the correct position, retrying up to three times
    bSuccess = False
    nRetryCount = 0
    while not bSuccess and (nRetryCount < 3):
      self.systemModel[self.setReactorPosition_ReactorID]['Motion'].moveToPosition(self.setReactorPosition_reactorPosition)
      try:
        self.waitForCondition(self.systemModel[self.setReactorPosition_ReactorID]['Motion'].getCurrentPosition,self.setReactorPosition_reactorPosition,EQUAL,10)
        bSuccess = True
      except UnitOpTimeout, ex:
        # Cycle the reactor robot to give it a kick
        self.error = ""
        self.systemModel[self.setReactorPosition_ReactorID]['Motion'].setDisableReactorRobot()
        time.sleep(0.5)
        self.systemModel[self.setReactorPosition_ReactorID]['Motion'].setEnableReactorRobot()
        time.sleep(0.5)
        nRetryCount += 1
    if not bSuccess:
      raise UnitOpTimeout("Failed to move reactor to the desired position")

  def setReactorPosition_Step4(self):
    self.systemModel[self.setReactorPosition_ReactorID]['Motion'].moveReactorUp()
    if self.setReactorPosition_reactorPosition == INSTALL:
      # Sleep briefly since we don't have up sensors for the install position
      time.sleep(0.5)
    elif self.setReactorPosition_reactorPosition == ADDREAGENT:
      # Nor do the up sensor for the add position work properly
      time.sleep(2)
    else:
      self.waitForCondition(self.systemModel[self.setReactorPosition_ReactorID]['Motion'].getCurrentReactorUp,True,EQUAL,10)

  def setReactorPosition_Step5(self):
    self.systemModel[self.setReactorPosition_ReactorID]['Motion'].setDisableReactorRobot()
    self.waitForCondition(self.systemModel[self.setReactorPosition_ReactorID]['Motion'].getCurrentRobotStatus,DISABLED,EQUAL,3)

  def setGripperPlace(self, nElute):
    #Make sure we are open and up
    if not self.checkForCondition(self.systemModel['ReagentDelivery'].getCurrentGripperOpen,True,EQUAL):
      self.doStep(self.setGripperPlace_Step1, "Failed to open gripper")
    if not self.checkForCondition(self.systemModel['ReagentDelivery'].getCurrentGripperUp,True,EQUAL):
      self.doStep(self.setGripperPlace_Step2, "Failed to raise gripper")
    if not self.checkForCondition(self.systemModel['ReagentDelivery'].getCurrentGasTransferUp,True,EQUAL):
      self.doStep(self.setGripperPlace_Step3, "Failed to raise gas transfer")

    #Make sure the reagent robots are enabled
    if not(self.checkForCondition(self.systemModel['ReagentDelivery'].getRobotStatus,(ENABLED,ENABLED),EQUAL)):
      self.doStep(self.setGripperPlace_Step4, "Failed to enable reagent robots")

    #Move to the reagent position
    self.doStep(self.setGripperPlace_Step5, "Failed to move robot to reagent position")

    #Pick up the vial
    bHaveVial = False
    while not bHaveVial:
      #Lowering, close and raise the gripper
      self.doStep(self.setGripperPlace_Step6, "Failed to lower gripper")
      self.doStep(self.setGripperPlace_Step7, "Failed to close gripper")
      self.doStep(self.setGripperPlace_Step8, "Failed to raise gripper")

      #Make sure we have a vial
      if self.checkForCondition(self.systemModel['ReagentDelivery'].getCurrentGripperClose,True,EQUAL):
        bHaveVial = True
      else:
        self.setSoftError("Failed to pick up vial", SOFTERROR_RETRY | SOFTERROR_IGNORE | SOFTERROR_ABORT)
        option = self.waitForSoftErrorDecision()
        if option == SOFTERROR_RETRY:
          self.doStep(self.setGripperPlace_Step9, "Failed to open gripper")
        elif option == SOFTERROR_IGNORE:
          bHaveVial = True
        elif option == SOFTERROR_ABORT:
          self.abortOperation(error)

    #Move to the delivery or elute position
    self.setGripperPlace_elute = nElute
    self.doStep(self.setGripperPlace_Step10, "Failed to move robot to the target position")
    
    #Lower and turn on the gas transfer and lower the vial
    self.doStep(self.setGripperPlace_Step11, "Failed to lower gas transfer")
    self.setGasTransferValve(ON)
    self.doStep(self.setGripperPlace_Step12, "Failed to lower vial")

  def setGripperPlace_Step1(self):
    self.systemModel['ReagentDelivery'].setMoveGripperOpen()
    self.waitForCondition(self.systemModel['ReagentDelivery'].getCurrentGripperOpen,True,EQUAL,3)

  def setGripperPlace_Step2(self):
    self.systemModel['ReagentDelivery'].setMoveGripperUp()
    self.waitForCondition(self.systemModel['ReagentDelivery'].getCurrentGripperUp,True,EQUAL,4)

  def setGripperPlace_Step3(self):
    self.systemModel['ReagentDelivery'].setMoveGasTransferUp()
    self.waitForCondition(self.systemModel['ReagentDelivery'].getCurrentGasTransferUp,True,EQUAL,3)

  def setGripperPlace_Step4(self):
    self.systemModel['ReagentDelivery'].setEnableRobots()
    self.waitForCondition(self.systemModel['ReagentDelivery'].getRobotStatus,(ENABLED,ENABLED),EQUAL,3)

  def setGripperPlace_Step5(self):
    #Retry up to three times
    bSuccess = False
    nRetryCount = 0
    while not bSuccess and (nRetryCount < 3):
      self.systemModel['ReagentDelivery'].moveToReagentPosition(int(self.ReagentReactorID[-1]),self.reagentPosition)
      try:
        self.waitForCondition(self.systemModel['ReagentDelivery'].getCurrentPosition,(int(self.ReagentReactorID[-1]),
          self.reagentPosition, 0, 0),EQUAL,5)
        bSuccess = True
      except UnitOpTimeout, ex:
        self.checkAbort()
        self.error = ""
        nRetryCount += 1
    if not bSuccess:
      raise UnitOpTimeout("Failed to move robot to the desired position")

  def setGripperPlace_Step6(self):
    self.systemModel['ReagentDelivery'].setMoveGripperDown()
    self.waitForCondition(self.systemModel['ReagentDelivery'].getCurrentGripperDown,True,EQUAL,4)

  def setGripperPlace_Step7(self):
    self.systemModel['ReagentDelivery'].setMoveGripperClose()
    self.waitForCondition(self.systemModel['ReagentDelivery'].getCurrentGripperClose,True,EQUAL,3)

  def setGripperPlace_Step8(self):
    self.systemModel['ReagentDelivery'].setMoveGripperUp()
    self.waitForCondition(self.systemModel['ReagentDelivery'].getCurrentGripperUp,True,EQUAL,4)

  def setGripperPlace_Step9(self):
    self.systemModel['ReagentDelivery'].setMoveGripperOpen()
    self.waitForCondition(self.systemModel['ReagentDelivery'].getCurrentGripperOpen,True,EQUAL,3)

  def setGripperPlace_Step10(self):
    #Retry up to three times
    bSuccess = False
    nRetryCount = 0
    while not bSuccess and (nRetryCount < 3):
      if self.setGripperPlace_elute == 0:
        self.systemModel['ReagentDelivery'].moveToDeliveryPosition(int(self.ReactorID[-1]),self.reagentLoadPosition)
      else:
        self.systemModel['ReagentDelivery'].moveToElutePosition(int(self.ReactorID[-1]))
      try:
        if self.setGripperPlace_elute == 0:
          self.waitForCondition(self.systemModel['ReagentDelivery'].getCurrentPosition,(int(self.ReactorID[-1]),
            0, self.reagentLoadPosition, 0),EQUAL,5)
        else:
          self.waitForCondition(self.systemModel['ReagentDelivery'].getCurrentPosition,(int(self.ReactorID[-1]), 0, 0, 1),EQUAL,5)
        bSuccess = True
      except UnitOpTimeout, ex:
        self.checkAbort()
        self.error = ""
        nRetryCount += 1
    if not bSuccess:
      raise UnitOpTimeout("Failed to move robot to the target position")

  def setGripperPlace_Step11(self):
    self.systemModel['ReagentDelivery'].setMoveGasTransferDown()
    self.waitForCondition(self.systemModel['ReagentDelivery'].getCurrentGasTransferDown,True,EQUAL,5)

  def setGripperPlace_Step12(self):
    self.systemModel['ReagentDelivery'].setMoveGripperDown()
    self.waitForCondition(self.systemModel['ReagentDelivery'].getCurrentGripperDown,True,EQUAL,20)

  def removeGripperPlace(self):
    #This function only makes sense if we just finished delivering a reagent and are in the closed and down position
    if not self.checkForCondition(self.systemModel['ReagentDelivery'].getCurrentGripperClose,True,EQUAL):
      self.abortOperation("SetGripperRemove called while gripper was not closed")
    if not self.checkForCondition(self.systemModel['ReagentDelivery'].getCurrentGripperDown,True,EQUAL):
      self.abortOperation("SetGripperRemove called while gripper was not up")

    # Remove the vial
    bVialUp = False
    nFailureCount = 0
    time.sleep(1)
    while not bVialUp:
      self.doStep(self.removeGripperPlace_Step1, "Failed to raise gripper")
      if self.checkForCondition(self.systemModel['ReagentDelivery'].getCurrentGripperClose,True,EQUAL):
        bVialUp = True
      elif nFailureCount < 10:
        self.doStep(self.removeGripperPlace_Step2, "Failed to open gripper")
        self.doStep(self.removeGripperPlace_Step3, "Failed to lower gripper")
        self.doStep(self.removeGripperPlace_Step4, "Failed to close gripper")
        nFailureCount += 1
      else:
        raise Exception("Failed to remove vial")

    #Turn off and raise the transfer gas
    self.setGasTransferValve(OFF)
    self.doStep(self.removeGripperPlace_Step5, "Failed to raise gas transfer")

    #Move to the reagent position, down and open
    self.doStep(self.removeGripperPlace_Step6, "Failed to move the robot to reagent position")
    self.systemModel['ReagentDelivery'].setMoveGripperDown()
    time.sleep(2)  #The vial often slips in the gripper when raising so our down sensor won't register
    self.doStep(self.removeGripperPlace_Step7, "Failed to open gripper")
    
    #Move up and to home
    self.doStep(self.removeGripperPlace_Step8, "Failed to raise gripper")
    self.doStep(self.removeGripperPlace_Step9, "Failed to move robot to home")

  def removeGripperPlace_Step1(self):
    self.systemModel['ReagentDelivery'].setMoveGripperUp()
    self.waitForCondition(self.systemModel['ReagentDelivery'].getCurrentGripperUp,True,EQUAL,6)

  def removeGripperPlace_Step2(self):
    self.systemModel['ReagentDelivery'].setMoveGripperOpen()
    self.waitForCondition(self.systemModel['ReagentDelivery'].getCurrentGripperOpen,True,EQUAL,3)

  def removeGripperPlace_Step3(self):
    self.systemModel['ReagentDelivery'].setMoveGripperDown()
    self.waitForCondition(self.systemModel['ReagentDelivery'].getCurrentGripperDown,True,EQUAL,3)

  def removeGripperPlace_Step4(self):
    self.systemModel['ReagentDelivery'].setMoveGripperClose()
    self.waitForCondition(self.systemModel['ReagentDelivery'].getCurrentGripperClose,True,EQUAL,3)

  def removeGripperPlace_Step5(self):
    self.systemModel['ReagentDelivery'].setMoveGasTransferUp()
    self.waitForCondition(self.systemModel['ReagentDelivery'].getCurrentGasTransferUp,True,EQUAL,5)

  def removeGripperPlace_Step6(self):
    #Retry up to three times
    bSuccess = False
    nRetryCount = 0
    while not bSuccess and (nRetryCount < 3):
      self.systemModel['ReagentDelivery'].moveToReagentPosition(int(self.ReagentReactorID[-1]),self.reagentPosition)
      try:
        self.waitForCondition(self.systemModel['ReagentDelivery'].getCurrentPosition,(int(self.ReagentReactorID[-1]), self.reagentPosition, 0, 0),EQUAL,5)
        bSuccess = True
      except UnitOpTimeout, ex:
        self.checkAbort()
        self.error = ""
        nRetryCount += 1
    if not bSuccess:
      raise UnitOpTimeout("Failed to move the robot to reagent position")

  def removeGripperPlace_Step7(self):
    self.systemModel['ReagentDelivery'].setMoveGripperOpen()
    self.waitForCondition(self.systemModel['ReagentDelivery'].getCurrentGripperOpen,True,EQUAL,3)

  def removeGripperPlace_Step8(self):
    self.systemModel['ReagentDelivery'].setMoveGripperUp()
    self.waitForCondition(self.systemModel['ReagentDelivery'].getCurrentGripperUp,True,EQUAL,3)

  def removeGripperPlace_Step9(self):
    self.systemModel['ReagentDelivery'].moveToHomeFast()
    self.waitForCondition(self.systemModel['ReagentDelivery'].getCurrentPosition,(0,0,0,0),EQUAL,5)

  def waitForCondition(self,function,condition,comparator,timeout): #Timeout in seconds, default to 3.
    log.info("waitForCondition")
    startTime = time.time()
    self.delay = 500
    self.checkAbort()
    bConditionMet = False

    if comparator == EQUAL:
      while not bConditionMet:
        value = function()
        bConditionMet = (value == condition)
        if not bConditionMet:
          self.logInfo("Function %s is %s, waiting to be EQUAL TO %s" % (str(function.__name__),str(value),str(condition)))
          self.stateCheckInterval(self.delay)
          if not(timeout == 65535):
            if self.isTimerExpired(startTime,timeout):
              self.logError("waitForCondition call timed out on function:%s class:%s" % (function.__name__,function.im_class))
              raise UnitOpTimeout("waitForCondition")
        self.checkAbort()
        if self.updateStatusWhileWaiting != None:
          self.updateStatus(self.updateStatusWhileWaiting(value))
      self.logInfo("Function %s is EQUAL TO %s, continuing" % (str(function.__name__),str(value)))
    elif comparator == NOTEQUAL:
      while not bConditionMet:
        value = function()
        bConditionMet = (value != condition)
        if not bConditionMet:
          self.logInfo("Function %s is %s, waiting to be NOT EQUAL TO %s" % (str(function.__name__),str(value),str(condition)))
          self.stateCheckInterval(self.delay)
          if not(timeout == 65535):
            if self.isTimerExpired(startTime,timeout):
              self.logError("waitForCondition call timed out on function:%s class:%s" % (function.__name__,function.im_class))
              raise UnitOpTimeout("waitForCondition")
        self.checkAbort()
        if self.updateStatusWhileWaiting != None:
          self.updateStatus(self.updateStatusWhileWaiting(value))
      self.logInfo("Function %s is NOT EQUAL TO %s, continuing" % (str(function.__name__),str(value)))
    elif comparator == GREATER:
      while not bConditionMet:
        value = function()
        bConditionMet = (value >= condition)
        if not bConditionMet:
          self.logInfo("Function %s is %s, waiting to be GREATER THAN %s" % (str(function.__name__),str(value),str(condition)))
          self.stateCheckInterval(self.delay)
          if not(timeout == 65535):
            if self.isTimerExpired(startTime,timeout):
              self.logError("waitForCondition call timed out on function:%s class:%s" % (function.__name__,function.im_class))
              raise UnitOpTimeout("waitForCondition")
        self.checkAbort()
        if self.updateStatusWhileWaiting != None:
          self.updateStatus(self.updateStatusWhileWaiting(value))
      self.logInfo("Function %s is GREATER THAN %s, continuing" % (str(function.__name__),str(value)))
    elif comparator == LESS:
      while not bConditionMet:
        value = function()
        bConditionMet = (value <= condition)
        if not bConditionMet:
          self.logInfo("Function %s is %s, waiting to be LESS THAN %s" % (str(function.__name__),str(value),str(condition)))
          self.stateCheckInterval(self.delay)
          if not(timeout == 65535):
            if self.isTimerExpired(startTime,timeout):
              self.logError("waitForCondition call timed out on function:%s class:%s" % (function.__name__,function.im_class))
              raise UnitOpTimeout("waitForCondition")
        self.checkAbort()
        if self.updateStatusWhileWaiting != None:
          self.updateStatus(self.updateStatusWhileWaiting(value))
      self.logInfo("Function %s is LESS EQUAL to %s, continuing" % (str(function.__name__),str(value)))
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
    
  def startTimer(self,timerLength):  #In seconds
    #Remember the start time and length
    self.timerStartTime = time.time()
    self.timerLength = timerLength
    self.timerStopped = False
    
  def waitForTimer(self):
    while self.timerOverridden or not self.isTimerExpired(self.timerStartTime, self.timerLength):
      self.checkAbort()
      self.stateCheckInterval(50) #Sleep 50ms between checks
    return (time.time() - self.timerStartTime)

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

  def overrideTimer(self):
    """Overrides the running unit operation timer"""
    if not self.timerOverridden:
      self.timerOverridden = True

  def stopTimer(self):
    """Stops the unit operation timer"""
    if self.timerOverridden:
      self.timerLength = time.time() - self.timerStartTime
      self.timerOverridden = False
    self.timerStopped = True

  def getTimerStatus(self):
    """Returns the timer status"""
    if self.timerStartTime == 0:
      return "None"
    elif self.timerOverridden:
      return "Overridden"
    elif not self.isTimerExpired(self.timerStartTime, self.timerLength):
      return "Running"
    else:
      return "Complete"

  def getTime(self):
    """Returns either the elapsed time or time remaining"""
    sStatus = self.getTimerStatus()
    nCurrentTime = time.time()
    if sStatus == "Overridden":
      return (nCurrentTime - self.timerStartTime)
    elif sStatus == "Running":
      nEndTime = self.timerStartTime + self.timerLength
      if nCurrentTime < nEndTime:
        return (nEndTime - nCurrentTime)
    return 0

  def abortOperation(self,error,raiseException=True):
    #Safely abort -> Do not move, turn off heaters, turn set points to zero.
    for nReactor in range(1, 4):
      sReactor = "Reactor" + str(nReactor)
      self.systemModel[sReactor]['Thermocouple'].setSetPoint(OFF)
      self.systemModel[sReactor]['Thermocouple'].setHeaterOff()
    self.systemModel['CoolingSystem'].setCoolingSystemOn(OFF)
    self.error = error
    log.error("Traceback: %s" % traceback.format_exc())
    log.error("Class:<%s> | Error:%s | Status:%s " % (self.__class__.__name__, self.error, self.status))
    if raiseException:
      raise UnitOpError(error)
    print error
    
  def setStopcockPosition(self,stopcockPositions,ReactorID=255):
    # Set the reactor ID
    if ReactorID == 255:
      self.setStopcockPosition_ReactorID = self.ReactorID
    else:
      self.setStopcockPosition_ReactorID = ReactorID

    # Set the stopcocks
    for stopcock in range(1,(len(stopcockPositions)+1)):
      if not stopcockPositions[stopcock-1] == NA:
        self.setStopcockPosition_stopcock = "Stopcock" + str(stopcock)
        if stopcockPositions[stopcock-1] == CW:
          self.doStep(self.setStopcockPosition_Step1, "Failed to set stopcock position")
        elif stopcockPositions[stopcock-1] == CCW:
          self.doStep(self.setStopcockPosition_Step2, "Failed to set stopcock position")
        else:
          self.abortOperation("Unknown stopcock position: " + stopcockPosition[stopcock-1])
 
  def setStopcockPosition_Step1(self):
    self.systemModel[self.setStopcockPosition_ReactorID][self.setStopcockPosition_stopcock].setCW()
    self.waitForCondition(self.systemModel[self.setStopcockPosition_ReactorID][self.setStopcockPosition_stopcock].getCW,True,EQUAL,3) 

  def setStopcockPosition_Step2(self):
    self.systemModel[self.setStopcockPosition_ReactorID][self.setStopcockPosition_stopcock].setCCW()
    self.waitForCondition(self.systemModel[self.setStopcockPosition_ReactorID][self.setStopcockPosition_stopcock].getCCW,True,EQUAL,3) 

  def startTransfer(self,state):
    self.doStep(self.startTransfer_Step1, "Failed to open transfer valve")

  def startTransfer_Step1(self):
    self.systemModel[self.ReactorID]['Valves'].setTransferValveOpen(state)
    self.waitForCondition(self.systemModel[self.ReactorID]['Valves'].getTransferValveOpen,state,EQUAL,3)

  def setHeater(self,heaterState):
    if heaterState == ON:
      self.updateStatusWhileWaiting = self.updateHeaterStatus
      self.doStep(self.setHeater_Step1, "Failed to turn on heaters")
      self.waitForCondition(self.systemModel[self.ReactorID]['Thermocouple'].getCurrentTemperature,self.reactTemp,GREATER,65535)
      self.updateStatusWhileWaiting = None
    elif heaterState == OFF:
      self.doStep(self.setHeater_Step2, "Failed to turn off heaters")

  def setHeater_Step1(self):
    self.systemModel[self.ReactorID]['Thermocouple'].setHeaterOn()
    self.waitForCondition(self.systemModel[self.ReactorID]['Thermocouple'].getHeaterOn,True,EQUAL,3)

  def setHeater_Step2(self):
    self.systemModel[self.ReactorID]['Thermocouple'].setHeaterOff()
    self.waitForCondition(self.systemModel[self.ReactorID]['Thermocouple'].getHeaterOn,False,EQUAL,3)

  def updateHeaterStatus(self,currentTemp):
      return ("%i C" % currentTemp)
      
  def setTemp(self):
    self.doStep(self.setTemp_Step1, "Failed to set temperature")

  def setTemp_Step1(self):
    self.systemModel[self.ReactorID]['Thermocouple'].setSetPoint(self.reactTemp)
    self.waitForCondition(self.systemModel[self.ReactorID]['Thermocouple'].getSetTemperature,self.reactTemp,EQUAL,3)

  def setCool(self,coolingDelay = 0):
    self.doStep(self.setCool_Step1, "Failed to turn off heaters")
    self.setCoolingSystem(ON)
    self.updateStatusWhileWaiting = self.updateHeaterStatus
    self.waitForCondition(self.systemModel[self.ReactorID]['Thermocouple'].getCurrentTemperature,self.coolTemp,LESS,65535) 
    if coolingDelay > 0:
      self.startTimer(coolingDelay)
      coolingDelay = self.waitForTimer()
    self.updateStatusWhileWaiting = None
    self.setCoolingSystem(OFF)
    return coolingDelay

  def setCool_Step1(self):
    self.systemModel[self.ReactorID]['Thermocouple'].setHeaterOff()
    self.waitForCondition(self.systemModel[self.ReactorID]['Thermocouple'].getHeaterOn,False,EQUAL,3)
    
  def setStirSpeed(self,stirSpeed):
    if (stirSpeed == OFF): #Fix issue with False being misinterpreted.
      stirSpeed = 0
    self.setStirSpeed_stirSpeed = stirSpeed
    self.doStep(self.setStirSpeed_Step1, "Failed to set stir speed")

  def setStirSpeed_Step1(self):
    self.systemModel[self.ReactorID]['Stir'].setSpeed(self.setStirSpeed_stirSpeed)
    self.waitForCondition(self.systemModel[self.ReactorID]['Stir'].getCurrentSpeed,self.setStirSpeed_stirSpeed,EQUAL,3)

  def setGasTransferValve(self,valveSetting):
    if (valveSetting):
      self.doStep(self.setGasTransferValve_Step1, "Failed to open gas transfer valve")
    else:
      self.doStep(self.setGasTransferValve_Step2, "Failed to close gas transfer valve")

  def setGasTransferValve_Step1(self):
    self.systemModel['Valves'].setGasTransferValveOpen(ON)
    self.waitForCondition(self.systemModel['Valves'].getGasTransferValveOpen,True,EQUAL,3)     

  def setGasTransferValve_Step2(self):
    self.systemModel['Valves'].setGasTransferValveOpen(OFF)
    self.waitForCondition(self.systemModel['Valves'].getGasTransferValveOpen,False,EQUAL,3)      
  
  def setVacuumSystem(self,systemOn):
    if (systemOn):
      self.doStep(self.setVacuumSystem_Step1, "Failed to turn on the vacuum system")
    else:
      self.doStep(self.setVacuumSystem_Step2, "Failed to turn off the vacuum system")

  def setVacuumSystem_Step1(self):
      self.systemModel['VacuumSystem'].setVacuumSystemOn()
      self.waitForCondition(self.systemModel['VacuumSystem'].getVacuumSystemOn,True,EQUAL,3)     

  def setVacuumSystem_Step2(self):
      self.systemModel['VacuumSystem'].setVacuumSystemOff()
      self.waitForCondition(self.systemModel['VacuumSystem'].getVacuumSystemOn,False,EQUAL,3)     

  def setCoolingSystem(self,systemOn):
    if (systemOn):
      self.doStep(self.setCoolingSystem_Step1, "Failed to turn on the cooling system")
    else:
      self.doStep(self.setCoolingSystem_Step2, "Failed to turn off the cooling system")

  def setCoolingSystem_Step1(self):
    self.systemModel['CoolingSystem'].setCoolingSystemOn(ON)
    self.waitForCondition(self.systemModel['CoolingSystem'].getCoolingSystemOn,ON,EQUAL,3)

  def setCoolingSystem_Step2(self):
    self.systemModel['CoolingSystem'].setCoolingSystemOn(OFF)
    self.waitForCondition(self.systemModel['CoolingSystem'].getCoolingSystemOn,OFF,EQUAL,3)

  def setPressureRegulator(self,regulator,pressureSetPoint,rampTime=0): #Time in seconds
    if (str(regulator) == '1') or (str(regulator) == 'PressureRegulator1'):
      self.pressureRegulator = 'PressureRegulator1'
    elif (str(regulator) == '2') or (str(regulator) == 'PressureRegulator2'):
      self.pressureRegulator = 'PressureRegulator2'
    if rampTime:
      nRefreshFrequency = 5  # Update pressure this number of times per second
      #log.error("Break1") # Looks like it took to long to ramp up?
      currentPressure = float(self.systemModel[self.pressureRegulator].getSetPressure())
      #log.error("Break2")
      rampRate = (float(pressureSetPoint) - float(currentPressure)) / float(rampTime) / float(nRefreshFrequency)
      nElapsedTime = 0
      while (not self.timerStopped) and (nElapsedTime < rampTime):
        time.sleep(1 / float(nRefreshFrequency))
        nElapsedTime += 1 / float(nRefreshFrequency)
        currentPressure += rampRate
        self.systemModel[self.pressureRegulator].setRegulatorPressure(currentPressure) #Set analog value on PLC
        
        self.checkAbort()
        #log.error("Break3")
      if self.timerStopped:
        return
    self.pressureSetPoint = pressureSetPoint
    self.doStep(self.setPressureRegulator_Step1, "Failed to reach the target pressure")

  def setPressureRegulator_Step1(self):
    self.systemModel[self.pressureRegulator].setRegulatorPressure(self.pressureSetPoint)
    self.waitForCondition(self.pressureSet,True,EQUAL,20)

  def pressureSet(self):
    log.debug("getCurrentPressure: %d, pressureSetPoint: %d" 
            %(self.systemModel[self.pressureRegulator].getCurrentPressure(),self.pressureSetPoint))

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
    pTargetComponent["note"] = self.component["note"]

  def copyComponent(self, nSourceSequenceID, nTargetSequenceID):
    """Creates a copy of the component in the database"""
    # Pull the original component from the database and create a deep copy
    pDBComponent = self.database.GetComponent(self.username, self.component["id"])
    pComponentCopy = copy.deepcopy(pDBComponent)

    # Allow the derived class a chance to alter the component copy
    self.copyComponentImpl(nSourceSequenceID, nTargetSequenceID, pComponentCopy)

    # Add the component to the database and return the ID
    nComponentCopyID = self.database.CreateComponent(self.username, nTargetSequenceID, pComponentCopy["componenttype"], pComponentCopy["note"], 
      json.dumps(pComponentCopy))
    return nComponentCopyID

  def copyComponentImpl(self, nSourceSequenceID, nTargetSequenceID, pComponentCopy):
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
    self.setStatus("Waiting for user input")

    # Wait until we get the signal to continue
    while self.waitingForUserInput:
      time.sleep(0.25)
      self.checkAbort()

