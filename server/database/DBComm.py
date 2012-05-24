"""DBComm

Elixys MySQL database communication layer
"""

# Imports
import json
import datetime
import sys
import MySQLdb
import threading
import Exceptions
import Utilities
from configobj import ConfigObj
import os
import TimedLock
import datetime

# Suppress MySQLdb's annoying warnings
import warnings
warnings.filterwarnings("ignore", "Unknown table.*")

# Error log levels
LOG_ERROR = 0
LOG_WARNING = 1
LOG_INFO = 2
LOG_DEBUG = 3

# Parse a log level string into an integer
def ParseLogLevel(sLogLevel):
    if sLogLevel == "error":
        return LOG_ERROR
    elif sLogLevel == "warning":
        return LOG_WARNING
    elif sLogLevel == "info":
        return LOG_INFO
    elif sLogLevel == "debug":
        return LOG_DEBUG
    else:
        return -1

# Database wrapper class
class DBComm:
  ### Construction / Destruction ###

  def __init__(self):
    """Initializes the DBComm class"""
    # Initialize variables
    self.__pDatabase = None
    self.__pDatabaseLock = TimedLock.TimedLock()

    # Open the system configuration
    sSystemConfiguration = "/opt/elixys/config/SystemConfiguration.ini"
    if not os.path.exists(sSystemConfiguration):
        raise Exception("System configuration INI file not found")
    self.__pSystemConfiguration = ConfigObj(sSystemConfiguration)

    # Create the configuration object
    self.__pConfiguration = {}
    self.__pConfiguration["name"] = self.__pSystemConfiguration["Name"]
    self.__pConfiguration["version"] = self.__pSystemConfiguration["Version"]
    self.__pConfiguration["debug"] = self.__pSystemConfiguration["Debug"] == "True"
    self.__pConfiguration["reactors"] = int(self.__pSystemConfiguration["Reactors"])
    self.__pConfiguration["reagentsperreactor"] = int(self.__pSystemConfiguration["ReagentsPerReactor"])
    self.__pConfiguration["columnsperreactor"] = int(self.__pSystemConfiguration["ColumnsPerReactor"])
    self.__pConfiguration["disallowedreagentpositions"] = []
    for sDisallowedPosition in self.__pSystemConfiguration["DisallowedPositions"]:
      pPositionComponents = sDisallowedPosition.split("-")
      pDisallowedPosition = {}
      pDisallowedPosition["type"] = "disallowedreagentposition"
      pDisallowedPosition["cassette"] = int(pPositionComponents[0])
      pDisallowedPosition["reagent"] = int(pPositionComponents[1])
      self.__pConfiguration["disallowedreagentpositions"].append(pDisallowedPosition)

    # Interpret the log level
    self.__nLogLevel = ParseLogLevel(self.__pSystemConfiguration["LogLevel"])
    if self.__nLogLevel == -1:
        raise Exception("Invalid log level in system configuration file")

  def Connect(self):
    """Connects to the database"""
    try:
      # Connect to the database
      self.__pDatabase = MySQLdb.connect(host="localhost", user="Elixys", passwd="devel", db="Elixys")
      self.__pDatabase.autocommit(True)
    except:
      raise Exception("Unable to connect to SQL database")

  def Disconnect(self):
    """Disconnects from the database"""
    # Disconnect from the database
    if self.__pDatabase != None:
      self.__pDatabase.close()
      self.__pDatabase = None

  ### Logging functions ###

  def GetLogLevel(self):
    """Returns the current log level"""
    return self.__nLogLevel

  def SystemLog(self, nLevel, sCurrentUsername, sMessage):
    """Logs a message to the SystemLog table in the database"""
    # Drop the log message if it's above our logging level
    if nLevel > self.__nLogLevel:
      return

    # Temp
    print sMessage

    # Log the message to the database
    if self.__pDatabase != None:
      self.__CallStoredProcedure("SystemLog", (datetime.datetime.now(), nLevel, sCurrentUsername, sMessage))
    else:
      print sMessage

  def RunLog(self, nLevel, sCurrentUsername, nSequenceID, nComponentID, sMessage):
    """Logs a message to the RunLog table in the database"""
    # Drop the log message if it's above our logging level
    if nLevel > self.__nLogLevel:
      return

    # Temp
    print sMessage

    # Log the message to the database
    if self.__pDatabase != None:
      self.__CallStoredProcedure("RunLog", (datetime.datetime.now(), nLevel, sCurrentUsername, nSequenceID, nComponentID, sMessage))
    else:
      print sMessage

  def StatusLog(self, bVacuumSystemOn, fVacuumSystemPressure, bCoolingSystemOn, fPressureRegulator1SetPressure, fPressureRegulator1ActualPressure,
      fPressureRegulator2SetPressure, fPressureRegulator2ActualPressure, bGasTransferValveOpen, bF18LoadValveOpen, bHPLCLoadValveOpen, sReagentRobotPositionSet,
      sReagentRobotPositionActual, nReagentRobotPositionSetX, nReagentRobotPositionSetY, nReagentRobotPositionActualX, nReagentRobotPositionActualY,
      sReagentRobotStatusX, sReagentRobotStatusY, sReagentRobotErrorX, sReagentRobotErrorY, nReagentRobotControlX, nReagentRobotControlY, nReagentRobotCheckX,
      nReagentRobotCheckY, bGripperSetUp, bGripperSetDown, bGripperSetOpen, bGripperSetClose, bGasTransferSetUp, bGasTransferSetDown, bGripperUp, bGripperDown,
      bGripperOpen, bGripperClose, bGasTransferUp, bGasTransferDown, sReactor1SetPosition, sReactor1ActualPosition, nReactor1SetY, nReactor1ActualY, sReactor1RobotStatus,
      nReactor1RobotError, nReactor1RobotControl, nReactor1RobotCheck, bReactor1SetUp, bReactor1SetDown, bReactor1Up, bReactor1Down, sReactor1Stopcock1Position,
      sReactor1Stopcock2Position, sReactor1Stopcock3Position, bReactor1Collet1On, fReactor1Collet1SetTemperature, fReactor1Collet1ActualTemperature,
      bReactor1Collet2On, fReactor1Collet2SetTemperature, fReactor1Collet2ActualTemperature, bReactor1Collet3On, fReactor1Collet3SetTemperature,
      fReactor1Collet3ActualTemperature, nReactor1StirMotor, fReactor1RaditationDetector, sReactor2SetPosition, sReactor2ActualPosition, nReactor2SetY,
      nReactor2ActualY, sReactor2RobotStatus, nReactor2RobotError, nReactor2RobotControl, nReactor2RobotCheck, bReactor2SetUp, bReactor2SetDown, bReactor2Up,
      bReactor2Down, sReactor2Stopcock1Position, bReactor2Collet1On, fReactor2Collet1SetTemperature, fReactor2Collet1ActualTemperature, bReactor2Collet2On,
      fReactor2Collet2SetTemperature, fReactor2Collet2ActualTemperature, bReactor2Collet3On, fReactor2Collet3SetTemperature, fReactor2Collet3ActualTemperature,
      nReactor2StirMotor, fReactor2RaditationDetector, sReactor3SetPosition, sReactor3ActualPosition, nReactor3SetY, nReactor3ActualY, sReactor3RobotStatus,
      nReactor3RobotError, nReactor3RobotControl, nReactor3RobotCheck, bReactor3SetUp, bReactor3SetDown, bReactor3Up, bReactor3Down, sReactor3Stopcock1Position, 
      bReactor3Collet1On, fReactor3Collet1SetTemperature, fReactor3Collet1ActualTemperature, bReactor3Collet2On, fReactor3Collet2SetTemperature, 
      fReactor3Collet2ActualTemperature, bReactor3Collet3On, fReactor3Collet3SetTemperature, fReactor3Collet3ActualTemperature, nReactor3StirMotor, 
      fReactor3RaditationDetector):
    """Logs the system state to the StatusLog table in the database"""
    # Log the message to the database
    if self.__pDatabase != None:
      self.__CallStoredProcedure("StatusLog", (datetime.datetime.now(), bVacuumSystemOn, fVacuumSystemPressure, bCoolingSystemOn, fPressureRegulator1SetPressure,
        fPressureRegulator1ActualPressure, fPressureRegulator2SetPressure, fPressureRegulator2ActualPressure, bGasTransferValveOpen, bF18LoadValveOpen,
        bHPLCLoadValveOpen, sReagentRobotPositionSet, sReagentRobotPositionActual, nReagentRobotPositionSetX, nReagentRobotPositionSetY, nReagentRobotPositionActualX,
        nReagentRobotPositionActualY, sReagentRobotStatusX, sReagentRobotStatusY, sReagentRobotErrorX, sReagentRobotErrorY, nReagentRobotControlX, nReagentRobotControlY, 
        nReagentRobotCheckX, nReagentRobotCheckY, bGripperSetUp, bGripperSetDown, bGripperSetOpen, bGripperSetClose, bGasTransferSetUp, bGasTransferSetDown, bGripperUp,
        bGripperDown, bGripperOpen, bGripperClose, bGasTransferUp, bGasTransferDown, sReactor1SetPosition, sReactor1ActualPosition, nReactor1SetY, nReactor1ActualY, 
        sReactor1RobotStatus, nReactor1RobotError, nReactor1RobotControl, nReactor1RobotCheck, bReactor1SetUp, bReactor1SetDown, bReactor1Up, bReactor1Down, 
        sReactor1Stopcock1Position, sReactor1Stopcock2Position, sReactor1Stopcock3Position, bReactor1Collet1On, fReactor1Collet1SetTemperature, fReactor1Collet1ActualTemperature,
        bReactor1Collet2On, fReactor1Collet2SetTemperature, fReactor1Collet2ActualTemperature, bReactor1Collet3On, fReactor1Collet3SetTemperature, 
        fReactor1Collet3ActualTemperature, nReactor1StirMotor, fReactor1RaditationDetector, sReactor2SetPosition, sReactor2ActualPosition, nReactor2SetY, nReactor2ActualY, 
        sReactor2RobotStatus, nReactor2RobotError, nReactor2RobotControl, nReactor2RobotCheck, bReactor2SetUp, bReactor2SetDown, bReactor2Up, bReactor2Down, 
        sReactor2Stopcock1Position, bReactor2Collet1On, fReactor2Collet1SetTemperature, fReactor2Collet1ActualTemperature, bReactor2Collet2On, fReactor2Collet2SetTemperature,
        fReactor2Collet2ActualTemperature, bReactor2Collet3On, fReactor2Collet3SetTemperature, fReactor2Collet3ActualTemperature, nReactor2StirMotor, 
        fReactor2RaditationDetector, sReactor3SetPosition, sReactor3ActualPosition, nReactor3SetY, nReactor3ActualY, sReactor3RobotStatus, nReactor3RobotError,
        nReactor3RobotControl, nReactor3RobotCheck, bReactor3SetUp, bReactor3SetDown, bReactor3Up, bReactor3Down, sReactor3Stopcock1Position, bReactor3Collet1On,
        fReactor3Collet1SetTemperature, fReactor3Collet1ActualTemperature, bReactor3Collet2On, fReactor3Collet2SetTemperature, fReactor3Collet2ActualTemperature, 
        bReactor3Collet3On, fReactor3Collet3SetTemperature, fReactor3Collet3ActualTemperature, nReactor3StirMotor, fReactor3RaditationDetector))

  def GetRecentLogsByTimestamp(self, sCurrentUsername, nLevel, pTimestamp):
    """Gets any logs in the SystemLog and RunLog tables that are more recent than the timestamp"""
    # Load the database access and get the raw logs
    self.SystemLog(LOG_DEBUG, sCurrentUsername, "DBComm.GetRecentLogsByTimestamp(%s, %i, %s)" % (sCurrentUsername, nLevel, str(pTimestamp)))
    pLogsRaw = self.__CallStoredProcedure("GetRecentLogsByTimestamp", (nLevel, pTimestamp))

    # Create the log array
    pLogs = []
    for pLogRaw in pLogsRaw:
      pLogs.append(self.__CreateLog(pLogRaw))
    return pLogs

  def GetRecentLogsByCount(self, sCurrentUsername, nLevel, nCount):
    """Gets the N most recent logs in the SystemLog and RunLog tables"""
    # Load the database access and get the raw logs
    self.SystemLog(LOG_DEBUG, sCurrentUsername, "DBComm.GetRecentLogsByCount(%s, %i, %i)" % (sCurrentUsername, nLevel, nCount))
    pLogsRaw = self.__CallStoredProcedure("GetRecentLogsByCount", (nLevel, nCount))

    # Create the log array
    pLogs = []
    for pLogRaw in pLogsRaw:
      pLogs.append(self.__CreateLog(pLogRaw))
    return pLogs

  ### Configuration functions ###

  def GetConfiguration(self, sCurrentUsername):
    """Returns the system configuration"""
    self.SystemLog(LOG_DEBUG, sCurrentUsername, "DBComm.GetConfiguration()")
    return self.__pConfiguration

  def GetSupportedOperations(self, sCurrentUsername):
    """Returns the supported operations"""
    self.SystemLog(LOG_DEBUG, sCurrentUsername, "DBComm.GetSupportedOperations()")
    return self.__pSystemConfiguration["UnitOperations"]

  def GetReactorPositions(self, sCurrentUsername):
    """Returns the reactor positions"""
    self.SystemLog(LOG_DEBUG, sCurrentUsername, "DBComm.GetReactorPositions()")
    return self.__pSystemConfiguration["ReactorPositions"]

  ### Role functions ###

  def GetAllRoles(self, sCurrentUsername):
    """Returns all user roles"""
    self.SystemLog(LOG_DEBUG, sCurrentUsername, "DBComm.GetAllRoles()")
    pRolesRaw = self.__CallStoredProcedure("GetAllRoles", ())

    # Create and return the role objects
    pRoles = []
    for pRoleRaw in pRolesRaw:
      pRoles.append(self.__CreateRole(pRoleRaw))
    return pRoles

  def GetRole(self, sCurrentUsername, sRoleName):
    """Returns the desired role"""
    # Load the database access and get the role
    self.SystemLog(LOG_DEBUG, sCurrentUsername, "DBComm.GetRole(%s)" % (sRoleName, ))
    pRoleRaw = self.__CallStoredProcedure("GetRole", (sRoleName, ))
    if len(pRoleRaw) == 0:
        raise Exception("Role " + sUsername + " not found")

    # Create and return the role object
    return self.__CreateRole(pRoleRaw[0])

  def CreateRole(self, sCurrentUsername, sRoleName, nFlags):
    """Creates the specified role"""
    self.SystemLog(LOG_DEBUG, sCurrentUsername, "DBComm.CreateRole(%s, %i)" % (sRoleName, nFlags))
    return self.__CallStoredProcedure("CreateRole", (sRoleName, nFlags))

  def UpdateRole(self, sCurrentUsername, sRoleName, sUpdateRoleName, nUpdatedFlags):
    """Updates the specified role"""
    self.SystemLog(LOG_DEBUG, sCurrentUsername, "DBComm.UpdateRole(%s, %s, %i)" % (sRoleName, sUpdateRoleName, nUpdatedFlags))
    return self.__CallStoredProcedure("UpdateRole", (sRoleName, sUpdateRoleName, nUpdatedFlags))

  def DeleteRole(self, sCurrentUsername, sRoleName):
    """Deletes the specified role"""
    self.SystemLog(LOG_DEBUG, sCurrentUsername, "DBComm.DeleteRole(%s)" % (sRoleName, ))
    return self.__CallStoredProcedure("DeleteRole", (sRoleName, ))

  ### User functions ###

  def GetAllUsers(self, sCurrentUsername):
    """Returns details of all system users"""
    self.SystemLog(LOG_DEBUG, sCurrentUsername, "DBComm.GetAllUsers()")
    pUsersRaw = self.__CallStoredProcedure("GetAllUsers", ())

    # Create and return the user objects
    pUsers = []
    for pUserRaw in pUsersRaw:
      pUsers.append(self.__CreateUser(pUserRaw))
    return pUsers

  def GetUser(self, sCurrentUsername, sUsername):
    """Returns details of the specified user"""
    # Load the database access and get the user data
    self.SystemLog(LOG_DEBUG, sCurrentUsername, "DBComm.GetUser(%s)" % (sUsername, ))
    pUserRaw = self.__CallStoredProcedure("GetUser", (sUsername, ))
    if len(pUserRaw) == 0:
        raise Exception("User " + sUsername + " not found")

    # Create and return the user object
    return self.__CreateUser(pUserRaw[0])

  def GetUserPasswordHash(self, sCurrentUsername, sUsername):
    """Returns the password hash of the specified user"""
    # Load the database access and get the user password hash
    self.SystemLog(LOG_DEBUG, sCurrentUsername, "DBComm.GetUserPasswordHash(%s)" % (sUsername, ))
    pPasswordHash = self.__CallStoredProcedure("GetUserPasswordHash", (sUsername, ))
    if len(pPasswordHash) == 0:
        raise Exception("User " + sUsername + " not found")
    return pPasswordHash[0][0]

  def CreateUser(self, sCurrentUsername, sUsername, sPasswordHash, sFirstName, sLastName, sRoleName):
    """Creates a new user"""
    self.SystemLog(LOG_DEBUG, sCurrentUsername, "DBComm.CreateUser(%s, %s, %s, %s, %s)" % (sUsername, sPasswordHash, sFirstName, sLastName, sRoleName))
    pDefaultClientState = {"type":"clientstate",
      "screen":"HOME",
      "sequenceid":0,
      "componentid":0,
      "lastselectscreen":"SAVED",
      "prompt":{"type":"promptstate",
        "screen":"",
        "title":"",
        "show":False,
        "text1":"",
        "edit1":False,
        "edit1default":"",
        "edit1validation":"",
        "text2":"",
        "edit2":False,
        "edit2default":"",
        "edit2validation":"",
        "buttons":[]},
      "selectsequencesort":{"type":"sort",
        "column":"name",
        "mode":"down"},
      "runhistorysort":{"type":"sort",
        "column":"date&time",
        "mode":"down"}}
    return self.__CallStoredProcedure("CreateUser", (sUsername, sPasswordHash, sFirstName, sLastName, sRoleName, json.dumps(pDefaultClientState)))

  def UpdateUser(self, sCurrentUsername, sUsername, sFirstName, sLastName, sRoleName):
    """Updates an existing user"""
    self.SystemLog(LOG_DEBUG, sCurrentUsername, "DBComm.UpdateUser(%s, %s, %s, %s)" % (sUsername, sFirstName, sLastName, sRoleName))
    return self.__CallStoredProcedure("UpdateUser", (sUsername, sFirstName, sLastName, sRoleName))

  def UpdateUserPassword(self, sCurrentUsername, sUsername, sPasswordHash):
    """Updates an existing user's password"""
    self.SystemLog(LOG_DEBUG, sCurrentUsername, "DBComm.UpdateUserPassword(%s, %s)" % (sUsername, sPasswordHash))
    return self.__CallStoredProcedure("UpdateUserPassword", (sUsername, sPasswordHash))

  def DeleteUser(self, sCurrentUsername, sUsername):
    """Deletes an existing user"""
    self.SystemLog(LOG_DEBUG, sCurrentUsername, "DBComm.DeleteUser(%s, %s, %s, %s)" % (sUsername, DeleteUser))
    return self.__CallStoredProcedure("DeleteUser", (sUsername, ))

  def GetUserClientState(self, sCurrentUsername, sUsername):
    """Returns the client state of a user"""
    self.SystemLog(LOG_DEBUG, sCurrentUsername, "DBComm.GetUserClientState(%s)" % (sUsername, ))
    pUserClientState = self.__CallStoredProcedure("GetUserClientState", (sUsername, ))
    if (len(pUserClientState) == 0) or (len(pUserClientState[0]) == 0):
       raise Exception("Failed to get client state for user " + sUsername)
    return json.loads(pUserClientState[0][0])

  def UpdateUserClientState(self, sCurrentUsername, sUsername, pClientState):
    """Updates the client state of a user"""
    sClientState = json.dumps(pClientState)
    self.SystemLog(LOG_DEBUG, sCurrentUsername, "DBComm.UpdateUserClientState(%s, %s)" % (sUsername, sClientState))
    return self.__CallStoredProcedure("UpdateUserClientState", (sUsername, sClientState))

  ### Sequence functions ###

  def GetAllSequences(self, sCurrentUsername, sType):
    """Return all sequences"""
    # Load the access and get the sequence data
    self.SystemLog(LOG_DEBUG, sCurrentUsername, "DBComm.GetAllSequences(%s)" % (sType, ))
    pSequencesRaw = self.__CallStoredProcedure("GetAllSequences", (sType, ))

    # Fill in each sequence
    pSequences = []
    for pSequenceRaw in pSequencesRaw:
      pSequence = {}
      pSequence["id"] = int(pSequenceRaw[0])
      pSequence["name"] = pSequenceRaw[1]
      pSequence["comment"] = pSequenceRaw[2]
      pSequence["date"] = pSequenceRaw[4].strftime("%m/%d/%Y")
      pSequence["time"] = pSequenceRaw[4].strftime("%H:%M.%S")
      pSequence["creator"] = pSequenceRaw[5]
      pSequence["components"] = int(pSequenceRaw[7])
      pSequence["valid"] = bool(pSequenceRaw[8])
      pSequence["dirty"] = bool(pSequenceRaw[9])
      pSequences.append(pSequence)

    # Return
    return pSequences

  def GetSequenceMetadata(self, sCurrentUsername, nSequenceID):
    """Gets a sequence"""
    # Log the function call and get the sequence data
    self.SystemLog(LOG_DEBUG, sCurrentUsername, "DBComm.GetSequenceMetadata(%i)" % (nSequenceID, ))
    pSequenceRaw = self.__CallStoredProcedure("GetSequence", (nSequenceID, ))
    if len(pSequenceRaw) == 0:
        raise Exceptions.SequenceNotFoundException(nSequenceID)

    # Fill in the sequence metadata
    pSequenceMetadata = {}
    pSequenceMetadata["type"] = "sequencemetadata"
    pSequenceMetadata["id"] = int(pSequenceRaw[0][0])
    pSequenceMetadata["name"] = pSequenceRaw[0][1]
    pSequenceMetadata["comment"] = pSequenceRaw[0][2]
    pSequenceMetadata["sequencetype"] = pSequenceRaw[0][3]
    pSequenceMetadata["timestamp"] = pSequenceRaw[0][4].strftime("%Y-%m-%d %H:%M:%S")
    pSequenceMetadata["creator"] = pSequenceRaw[0][5]
    pSequenceMetadata["components"] = int(pSequenceRaw[0][7])
    pSequenceMetadata["valid"] = bool(pSequenceRaw[0][8])
    pSequenceMetadata["dirty"] = bool(pSequenceRaw[0][9])

    # Return
    return pSequenceMetadata

  def GetSequence(self, sCurrentUsername, nSequenceID):
    """Gets a sequence"""
    # Log the function call and get the sequence data
    self.SystemLog(LOG_DEBUG, sCurrentUsername, "DBComm.GetSequence(%i)" % (nSequenceID, ))
    pSequenceRaw = self.__CallStoredProcedure("GetSequence", (nSequenceID, ))
    if len(pSequenceRaw) == 0:
        raise Exceptions.SequenceNotFoundException(nSequenceID)

    # Load the sequence
    pSequence = {"type":"sequence"}
    pSequence["metadata"] = self.GetSequenceMetadata(sCurrentUsername, nSequenceID)
    pSequence["components"] = self.GetComponentsBySequence(sCurrentUsername, nSequenceID)

    # Return
    return pSequence

  def CreateSequence(self, sCurrentUsername, sName, sComment, sType, nCassettes, nReagents, nColumns):
    """Creates a new sequence"""
    self.SystemLog(LOG_DEBUG, sCurrentUsername, "DBComm.CreateSequence(%s, %s, %s, %i, %i, %i)" % (sName, sComment, sType, nCassettes, nReagents, nColumns))
    pRows, pReturn = self.__CallStoredProcedureWithReturn("CreateSequence", (sName, sComment, sType, sCurrentUsername, nCassettes, nReagents, nColumns))
    return pReturn[0][0]

  def UpdateSequence(self, sCurrentUsername, nSequenceID, sName, sComment, bValid):
    """Update a sequence"""
    self.SystemLog(LOG_DEBUG, sCurrentUsername, "DBComm.UpdateSequence(%i, %s, %s, %i)" % (nSequenceID, sName, sComment, bValid))
    return self.__CallStoredProcedure("UpdateSequence", (nSequenceID, sName, sComment, bValid))

  def UpdateSequenceDirtyFlag(self, sCurrentUsername, nSequenceID, bDirty):
    """Updates the sequence dirty flag"""
    self.SystemLog(LOG_DEBUG, sCurrentUsername, "DBComm.UpdateSequenceDirtyFlag(%i, %i)" % (nSequenceID, bDirty))
    self.__CallStoredProcedure("UpdateSequenceDirtyFlag", (nSequenceID, bDirty))

  def DeleteSequence(self, sCurrentUsername, nSequenceID):
    """Delete a sequence"""
    self.SystemLog(LOG_DEBUG, sCurrentUsername, "DBComm.DeleteSequence(%i)" % (nSequenceID, ))
    return self.__CallStoredProcedure("DeleteSequence", (nSequenceID, ))

  ### Reagent functions ###

  def GetReagent(self, sCurrentUsername, nReagentID):
    """Gets the specified reagent"""
    # Log the access and get the reagent
    self.SystemLog(LOG_DEBUG, sCurrentUsername, "DBComm.GetReagent(%i)" % (nReagentID, ))
    pReagentRaw = self.__CallStoredProcedure("GetReagent", (nReagentID, ))
    if len(pReagentRaw) == 0:
        raise Exceptions.ReagentNotFoundException(nReagentID)
    return self.__CreateReagent(pReagentRaw[0])

  def GetReagentsBySequence(self, sCurrentUsername, nSequenceID):
    """Gets all reagents in the sequence"""
    # Log the access and get the reagents
    self.SystemLog(LOG_DEBUG, sCurrentUsername, "DBComm.GetReagentsBySequence(%i)" % (nSequenceID, ))
    pReagentsRaw = self.__CallStoredProcedure("GetReagentsBySequence", (nSequenceID, ))

    # Create and return the reagent array
    pReagents = []
    for pReagentRaw in pReagentsRaw:
        pReagents.append(self.__CreateReagent(pReagentRaw))
    return pReagents

  def GetReagentsByName(self, sCurrentUsername, nSequenceID, sName):
    """Gets all reagents in the sequence that match the given name"""
    # Log the access and get the reagents
    self.SystemLog(LOG_DEBUG, sCurrentUsername, "DBComm.GetReagentsByName(%i, %s)" % (nSequenceID, sName))
    pReagentsRaw = self.__CallStoredProcedure("GetReagentsByName", (nSequenceID, sName))

    # Create and return the reagent array
    pReagents = []
    for pReagentRaw in pReagentsRaw:
        pReagents.append(self.__CreateReagent(pReagentRaw))
    return pReagents

  def GetReagentByPosition(self, sCurrentUsername, nSequenceID, nCassette, sPosition):
    """Gets the reagent at the given position"""
    self.SystemLog(LOG_DEBUG, sCurrentUsername, "DBComm.GetReagentByPosition(%i, %i, %s)" % (nSequenceID, nCassette, sPosition))
    pReagentRaw = self.__CallStoredProcedure("GetReagentByPosition", (nSequenceID, nCassette, sPosition))
    if len(pReagentRaw) == 0:
        raise Exceptions.ReagentNotFoundException(0, nSequenceID, nCassette, sPosition)
    return self.__CreateReagent(pReagentRaw[0])

  def GetReagentCassette(self, sCurrentUsername, nSequenceID, nReagentID):
    """Gets the cassette number that contains the given reagent"""
    self.SystemLog(LOG_DEBUG, sCurrentUsername, "DBComm.GetReagentCassette(%i, %i)" % (nSequenceID, nReagentID))
    pCassetteRaw, pReturn = self.__CallStoredProcedureWithReturn("GetReagentCassette", (nSequenceID, nReagentID))
    return pReturn[0][0]

  def UpdateReagent(self, sCurrentUsername, nReagentID, sName, sDescription):
    """Updates a existing reagent"""
    self.SystemLog(LOG_DEBUG, sCurrentUsername, "DBComm.UpdateReagent(%i, %s, %s)" % (nReagentID, sName, sDescription))
    return self.__CallStoredProcedure("UpdateReagent", (nReagentID, sName, sDescription))

  def UpdateReagentByPosition(self, sCurrentUsername, nSequenceID, nCassetteNumber, sPosition, sName, sDescription):
    """Update an existing reagent by position"""
    self.SystemLog(LOG_DEBUG, sCurrentUsername, "DBComm.UpdateReagentByPosition(%i, %i, %s, %s, %s)" % (nSequenceID, nCassetteNumber, sPosition, sName, sDescription))
    return self.__CallStoredProcedure("UpdateReagentByPosition", (nSequenceID, nCassetteNumber, sPosition, sName, sDescription))

  ### Component functions ###

  def GetComponent(self, sCurrentUsername, nComponentID):
    """Gets the specified component"""
    self.SystemLog(LOG_DEBUG, sCurrentUsername, "DBComm.GetComponent(%i)" % (nComponentID, ))
    pComponent, nPreviousComponentID, nNextComponentID = self.__GetComponent(nComponentID)
    return pComponent

  def GetPreviousComponent(self, sCurrentUsername, nComponentID):
    """Gets the component previous to the one specified"""
    self.SystemLog(LOG_DEBUG, sCurrentUsername, "DBComm.GetPreviousComponent(%i)" % (nComponentID, ))
    pComponent, nPreviousComponentID, nNextComponentID = self.__GetComponent(nComponentID)
    if nPreviousComponentID == 0:
        return None
    pComponent, nPreviousComponentID, nNextComponentID = self.__GetComponent(nPreviousComponentID)
    return pComponent

  def GetNextComponent(self, sCurrentUsername, nComponentID):
    """Gets the component after to the one specified"""
    self.SystemLog(LOG_DEBUG, sCurrentUsername, "DBComm.GetPreviousComponent(%i)" % (nComponentID, ))
    pComponent, nPreviousComponentID, nNextComponentID = self.__GetComponent(nComponentID)
    if nNextComponentID == 0:
        return None
    pComponent, nPreviousComponentID, nNextComponentID = self.__GetComponent(nNextComponentID)
    return pComponent

  def GetCassette(self, sCurrentUsername, nSequenceID, nCassetteOffset):
    """Gets the cassette specified by the offset"""
    self.SystemLog(LOG_DEBUG, sCurrentUsername, "DBComm.GetCassette(%i, %i)" % (nSequenceID, nCassetteOffset))
    pComponentRaw = self.__CallStoredProcedure("GetCassette", (nSequenceID, nCassetteOffset))
    if len(pComponentRaw) == 0:
        raise Exception("Failed to get cassette " + str(nCassetteOffset) + " of sequence " + str(nSequenceID))
    pComponent, nPreviousComponentID, nNextComponentID = self.__CreateComponent(pComponentRaw[0])
    return pComponent

  def GetComponentsBySequence(self, sCurrentUsername, nSequenceID):
    """Gets all of the components associated with the given sequence ID"""
    self.SystemLog(LOG_DEBUG, sCurrentUsername, "DBComm.GetComponentsBySequence(%i)" % (nSequenceID, ))
    pComponentsRaw = self.__CallStoredProcedure("GetComponentsBySequence", (nSequenceID, )) 
    pComponents = []
    for pComponentRaw in pComponentsRaw:
        pComponent, nPreviousComponentID, nNextComponentID = self.__CreateComponent(pComponentRaw)
        pComponents.append(pComponent)
    return pComponents

  def CreateComponent(self, sCurrentUsername, nSequenceID, sType, sNote, sContent):
    """Creates a new component and inserts it at the end of a sequence"""
    self.SystemLog(LOG_DEBUG, sCurrentUsername, "DBComm.CreateComponent(%i, %s, %s, %s)" % (nSequenceID, sType, sNote, sContent))
    pRows, pReturn = self.__CallStoredProcedureWithReturn("CreateComponent", (nSequenceID, sType, sNote, sContent))
    return pReturn[0][0]

  def InsertComponent(self, sCurrentUsername, nSequenceID, sType, sNote, sContent, nInsertID):
    """Inserts a component into a sequence"""
    self.SystemLog(LOG_DEBUG, sCurrentUsername, "DBComm.InsertComponent(%i, %s, %s, %s, %i)" % (nSequenceID, sType, sNote, sContent, nInsertID))
    pRows, pReturn = self.__CallStoredProcedureWithReturn("InsertComponent", (nSequenceID, sType, sNote, sContent, nInsertID))
    return pReturn[0][0]

  def UpdateComponent(self, sCurrentUsername, nComponentID, sType, sNote, sDetails):
    """Updates the specified component"""
    self.SystemLog(LOG_DEBUG, sCurrentUsername, "DBComm.UpdateComponent(%i, %s, %s, %s)" % (nComponentID, sType, sNote, sDetails))
    self.__CallStoredProcedure("UpdateComponent", (nComponentID, sType, sNote, sDetails))

  def MoveComponent(self, sCurrentUsername, nComponentID, nInsertAfterID):
    """Moves the specified component"""
    self.SystemLog(LOG_DEBUG, sCurrentUsername, "DBComm.MoveComponent(%i, %i)" % (nComponentID, nInsertAfterID))
    self.__CallStoredProcedure("MoveComponent", (nComponentID, nInsertAfterID))

  def DeleteComponent(self, sCurrentUsername, nComponentID):
    """Deletes the component and removes it from the sequence"""
    self.SystemLog(LOG_DEBUG, sCurrentUsername, "DBComm.DeleteComponent(%i)" % (nComponentID, ))
    return self.__CallStoredProcedure("DeleteComponent", (nComponentID, ))

  ### Internal functions ###

  def __CallStoredProcedure(self, sProcedureName, pArguments):
    """Calls the given SQL stored procedure"""
    pRows = None
    sError = ""
    bLocked = False
    try:
      # Acquire the database lock
      self.__pDatabaseLock.Acquire(10)
      bLocked = True

      # Acquire the cursor and internal database reference
      pCursor = self.__pDatabase.cursor()
      pInternalDB = pCursor._get_db()

      # Format the argument list
      sArguments = ""
      for pArgument in pArguments:
        if len(sArguments) != 0:
          sArguments += ", "
        sArguments += pInternalDB.literal(pArgument)

      # Invoke the stored procedure
      sQuery = "CALL " + sProcedureName + "(" + sArguments + ")"
      pCursor._query(sQuery)
      pCursor._executed = sQuery
      pRows = pCursor.fetchall()
      pCursor.close()
    except Exception, ex:
      # Remember error
      sError = str(ex)
    finally:
      # Release the database lock
      if bLocked:
        self.__pDatabaseLock.Release()

    # Raise an exception if an error occurred
    if sError != "":
      self.__pDatabase = None
      raise Exception(sError)

    # Return the result
    return pRows

  def __CallStoredProcedureWithReturn(self, sProcedureName, pArguments):
    """Calls the given SQL stored procedure where the last parameter is a return value"""
    pRows = None
    pReturn = None
    sError = ""
    bLocked = False
    try:
      # Acquire the database lock
      self.__pDatabaseLock.Acquire(10)
      bLocked = True

      # Acquire the cursor and internal database reference
      pCursor = self.__pDatabase.cursor()
      pInternalDB = pCursor._get_db()

      # Set the return parameter as a server variable
      sReturnValueName = "@_" + sProcedureName + "_ret"
      sQuery = "SET " + sReturnValueName + "=0"
      pCursor._query(sQuery)
      pCursor.nextset()

      # Format the argument list
      sArguments = ""
      for pArgument in pArguments:
        if len(sArguments) != 0:
          sArguments += ", "
        sArguments += pInternalDB.literal(pArgument)
      sArguments += ", " + sReturnValueName

      # Invoke the stored procedure
      sQuery = "CALL " + sProcedureName + "(" + sArguments + ")"
      pCursor._query(sQuery)
      pCursor._executed = sQuery
      pRows = pCursor.fetchall()
      pCursor.close()
    except Exception, ex:
      # Remember error
      sError = str(ex)
    finally:
      # Release the database lock
      if bLocked:
        self.__pDatabaseLock.Release()

    # Raise an exception if an error occurred
    if sError != "":
      self.__pDatabase = None
      raise Exception(sError)

    # Fetch the return value
    pReturn = self.__ExecuteQuery("SELECT " + sReturnValueName)
    return pRows, pReturn

  def __ExecuteQuery(self, sQuery):
    """Executes the given SQL query"""
    pRows = None
    sError = ""
    bLocked = False
    try:
      # Acquire the database lock
      self.__pDatabaseLock.Acquire(10)
      bLocked = True

      # Execute the query
      pCursor = self.__pDatabase.cursor()
      pCursor.execute(sQuery)
      pRows = pCursor.fetchall()
      pCursor.close()
    except Exception, ex:
      # Remember error
      sError = str(ex)
    finally:
      # Release the database lock
      if bLocked:
        self.__pDatabaseLock.Release()

    # Raise an exception if an error occurred
    if sError != "":
      self.__pDatabase = None
      raise Exception(sError)

    # Return the result
    return pRows

  def __CreateLog(self, pLogRaw):
    """Packages a log"""
    pLog = {"type":"log"}
    pLog["id"] = pLogRaw[0]
    pLog["date"] = pLogRaw[1]
    pLog["level"] = pLogRaw[2]
    pLog["username"] = pLogRaw[3]
    pLog["sequenceid"] = pLogRaw[4]
    pLog["componentid"] = pLogRaw[5]
    pLog["message"] = pLogRaw[6]
    return pLog

  def __CreateRole(self, pRoleRaw):
    """Packages a role"""
    pRole = {"type":"role"}
    pRole["id"] = pRoleRaw[0]
    pRole["name"] = pRoleRaw[1]
    pRole["flags"] = pRoleRaw[2]
    return pRole

  def __CreateUser(self, pUserRaw):
    """Packages a user"""
    pUser = {"type":"user"}
    pUser["username"] = pUserRaw[0]
    pUser["firstname"] = pUserRaw[1]
    pUser["lastname"] = pUserRaw[2]
    pUser["accesslevel"] = pUserRaw[3]
    return pUser

  def __GetComponent(self, nComponentID):
    """Fetches and packages a component"""
    pComponentRaw = self.__CallStoredProcedure("GetComponent", (nComponentID, ))
    if len(pComponentRaw) == 0:
        raise Exceptions.ComponentNotFoundException(nComponentID)
    return self.__CreateComponent(pComponentRaw[0])

  def __CreateComponent(self, pComponentRaw):
    """Packages a component"""
    pComponent = json.loads(pComponentRaw[6])
    pComponent["id"] = int(pComponentRaw[0])
    pComponent["note"] = pComponentRaw[5]
    pComponent["sequenceid"] = int(pComponentRaw[1])
    nPreviousComponentID = int(pComponentRaw[2])
    nNextComponentID = int(pComponentRaw[3])
    return pComponent, nPreviousComponentID, nNextComponentID

  def __CreateReagent(self, pReagentRaw):
    """Packages a reagent"""
    pReagent = {}
    pReagent["type"] = "reagent"
    pReagent["reagentid"] = pReagentRaw[0]
    pReagent["componentid"] = pReagentRaw[2]
    pReagent["position"] = pReagentRaw[3]
    pReagent["name"] = pReagentRaw[4]
    pReagent["namevalidation"] = "type=string; required=true"
    pReagent["description"] = pReagentRaw[5] 
    pReagent["descriptionvalidation"] = "type=string"
    return pReagent

