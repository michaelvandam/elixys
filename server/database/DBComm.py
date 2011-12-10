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

# Suppress MySQLdb's annoying warnings
import warnings
warnings.filterwarnings("ignore", "Unknown table.*")

# Database wrapper class
class DBComm:
  ### Construction / Destruction ###

  def __init__(self):
    """Initializes the DBComm class"""
    self.__pDatabase = None

  def Connect(self):
    """Connects to the database"""
    try:
      self.__pDatabase = MySQLdb.connect(host="localhost", user="Elixys", passwd="devel", db="Elixys")
      self.__pDatabase.autocommit(True)
    except:
      raise Exception("Unable to connect to SQL database")

  def Disconnect(self):
    """Disconnects from the database"""
    self.__pDatabase.close()
    self.__pDatabase = None

  ### Logging functions ###

  def Log(self, sCurrentUsername, sMessage):
    """Logs a message to the database"""
    # Log to stderr for now
    print >> sys.stderr, sCurrentUsername + ": " + sMessage + " [0x" + hex(threading.current_thread().ident) + "]"

  ### Configuration functions ###

  def GetConfiguration(self, sCurrentUsername):
    """Returns the system configuration"""
    self.Log(sCurrentUsername, "DBComm.GetConfiguration()")
    # Return hardcoded values for now but this should really come from the database
    return {"name":"Mini cell 3",
      "version":"2.0",
      "debug":"false",
      "reactors":3,
      "reagentsperreactor":11,
      "columnsperreactor":2}

  def GetSupportedOperations(self, sCurrentUsername):
    """Returns the supported operations"""
    self.Log(sCurrentUsername, "DBComm.GetSupportedOperations()")
    # Return hardcoded values for now but this should really come from the database
    return ["Add",
      "Evaporate",
      "Transfer",
      "React",
      "Prompt",
      "Install",
      "Comment",
      "TrapF18",
      "EluteF18",
      "Initialize",
      "Mix",
      "Move"]

  def GetReactorPositions(self, sCurrentUsername):
    """Returns the reactor positions"""
    self.Log(sCurrentUsername, "DBComm.GetReactorPositions()")
    # Return hardcoded values for now but this should really come from the database
    return ["Install",
      "Transfer",
      "React1",
      "Add",
      "React2",
      "Evaporate"]

  ### Role functions ###

  def GetAllRoles(self, sCurrentUsername):
    """Returns all user roles"""
    self.Log(sCurrentUsername, "DBComm.GetAllRoles()")
    return self.__CallStoredProcedure("GetRoles", ())

  def GetRole(self, sCurrentUsername, sRoleName):
    """Returns the desired role"""
    self.Log(sCurrentUsername, "DBComm.GetRole(%s)" % (sRoleName, ))
    return self.__CallStoredProcedure("GetRole", (sRoleName, ))

  def CreateRole(self, sCurrentUsername, sRoleName, nFlags):
    """Creates the specified role"""
    self.Log(sCurrentUsername, "DBComm.CreateRole(%s, %i)" % (sRoleName, nFlags))
    return self.__CallStoredProcedure("CreateRole", (sRoleName, nFlags))

  def UpdateRole(self, sCurrentUsername, sRoleName, sUpdateRoleName, nUpdatedFlags):
    """Updates the specified role"""
    self.Log(sCurrentUsername, "DBComm.UpdateRole(%s, %s, %i)" % (sRoleName, sUpdateRoleName, nUpdatedFlags))
    return self.__CallStoredProcedure("UpdateRole", (sRoleName, sUpdateRoleName, nUpdatedFlags))

  def DeleteRole(self, sCurrentUsername, sRoleName):
    """Deletes the specified role"""
    self.Log(sCurrentUsername, "DBComm.DeleteRole(%s)" % (sRoleName, ))
    return self.__CallStoredProcedure("DeleteRole", (sRoleName, ))

  ### User functions ###

  def GetAllUsers(self, sCurrentUsername):
    """Returns details of all system users"""
    self.Log(sCurrentUsername, "DBComm.GetAllUsers()")
    return self.__CallStoredProcedure("GetAllUsers", ())

  def GetUser(self, sCurrentUsername, sUsername):
    """Returns details of the specified user"""
    # Load the database access and get the user data
    self.Log(sCurrentUsername, "DBComm.GetUser(%s)" % (sUsername, ))
    pUserRaw = self.__CallStoredProcedure("GetUser", (sUsername, ))
    if len(pUserRaw) == 0:
        raise Exception("User " + sUsername + " not found")

    # Create the user object
    pUser = {"type":"user"}
    pUser["username"] = pUserRaw[0][0]
    pUser["firstname"] = pUserRaw[0][1]
    pUser["lastname"] = pUserRaw[0][2]
    pUser["accesslevel"] = pUserRaw[0][3]
    return pUser

  def CreateUser(self, sCurrentUsername, sUsername, sPasswordHash, sFirstName, sLastName, sRoleName):
    """Creates a new user"""
    self.Log(sCurrentUsername, "DBComm.CreateUser(%s, %s, %s, %s, %s)" % (sUsername, sPasswordHash, sFirstName, sLastName, sRoleName))
    pDefaultClientState = {"type":"clientstate",
      "screen":"HOME",
      "sequenceid":0,
      "componentid":0,
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
        "buttons":[]}}
    return self.__CallStoredProcedure("CreateUser", (sUsername, sPasswordHash, sFirstName, sLastName, sRoleName, json.dumps(pDefaultClientState)))

  def UpdateUser(self, sCurrentUsername, sUsername, sFirstName, sLastName, sRoleName):
    """Updates an existing user"""
    self.Log(sCurrentUsername, "DBComm.UpdateUser(%s, %s, %s, %s)" % (sUsername, sFirstName, sLastName, sRoleName))
    return self.__CallStoredProcedure("UpdateUser", (sUsername, sFirstName, sLastName, sRoleName))

  def UpdateUserPassword(self, sCurrentUsername, sUsername, sPasswordHash):
    """Updates an existing user's password"""
    self.Log(sCurrentUsername, "DBComm.UpdateUserPassword(%s, %s)" % (sUsername, sPasswordHash))
    return self.__CallStoredProcedure("UpdateUserPassword", (sUsername, sPasswordHash))

  def DeleteUser(self, sCurrentUsername, sUsername):
    """Deletes an existing user"""
    self.Log(sCurrentUsername, "DBComm.DeleteUser(%s, %s, %s, %s)" % (sUsername, DeleteUser))
    return self.__CallStoredProcedure("DeleteUser", (sUsername, ))

  def GetUserClientState(self, sCurrentUsername, sUsername):
    """Returns the client state of a user"""
    self.Log(sCurrentUsername, "DBComm.GetUserClientState(%s)" % (sUsername, ))
    pUserClientState = self.__CallStoredProcedure("GetUserClientState", (sUsername, ))
    if (len(pUserClientState) == 0) or (len(pUserClientState[0]) == 0):
       raise Exception("Failed to get client state for user " + sUsername)
    return json.loads(pUserClientState[0][0])

  def UpdateUserClientState(self, sCurrentUsername, sUsername, pClientState):
    """Updates the client state of a user"""
    sClientState = json.dumps(pClientState)
    self.Log(sCurrentUsername, "DBComm.UpdateUserClientState(%s, %s)" % (sUsername, sClientState))
    return self.__CallStoredProcedure("UpdateUserClientState", (sUsername, sClientState))

  ### Sequence functions ###

  def GetAllSequences(self, sCurrentUsername, sType):
    """Return all sequences"""
    # Load the access and get the sequence data
    self.Log(sCurrentUsername, "DBComm.GetAllSequences(%s)" % (sType, ))
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

  def GetSequence(self, sCurrentUsername, nSequenceID):
    """Gets a sequence"""
    # Log the function call and get the sequence data
    self.Log(sCurrentUsername, "DBComm.GetSequence(%i)" % (nSequenceID, ))
    pSequenceRaw = self.__CallStoredProcedure("GetSequence", (nSequenceID, ))
    if len(pSequenceRaw) == 0:
        raise Exceptions.SequenceNotFoundException(nSequenceID)

    # Fill in the sequence metadata
    pSequence = {"type":"sequence"}
    pSequence["metadata"] = {}
    pSequence["metadata"]["type"] = "sequencemetadata"
    pSequence["metadata"]["id"] = int(pSequenceRaw[0][0])
    pSequence["metadata"]["name"] = pSequenceRaw[0][1]
    pSequence["metadata"]["comment"] = pSequenceRaw[0][2]
    pSequence["metadata"]["timestamp"] = pSequenceRaw[0][4].strftime("%Y-%m-%d %H:%M:%S")
    pSequence["metadata"]["creator"] = pSequenceRaw[0][5]
    pSequence["metadata"]["components"] = int(pSequenceRaw[0][7])
    pSequence["metadata"]["valid"] = bool(pSequenceRaw[0][8])
    pSequence["metadata"]["dirty"] = bool(pSequenceRaw[0][9])

    # Load the components
    pSequence["components"] = self.GetComponentsBySequence(sCurrentUsername, nSequenceID)

    # Return
    return pSequence

  def CreateSequence(self, sCurrentUsername, sName, sComment, sType, nCassettes, nReagents, nColumns):
    """Creates a new sequence"""
    self.Log(sCurrentUsername, "DBComm.CreateSequence(%s, %s, %s, %i, %i, %i)" % (sName, sComment, sType, nCassettes, nReagents, nColumns))
    nSequenceID = 0
    self.__CallStoredProcedure("CreateSequence", (sName, sComment, sType, sCurrentUsername, nCassettes, nReagents, nColumns, nSequenceID))
    return self.__ExecuteQuery("SELECT @_CreateSequence_7")[0][0]

  def UpdateSequence(self, sCurrentUsername, nSequenceID, sName, sComment, bValid):
    """Update a sequence"""
    self.Log(sCurrentUsername, "DBComm.UpdateSequence(%i, %s, %s, %i)" % (nSequenceID, sName, sComment, bValid))
    return self.__CallStoredProcedure("UpdateSequence", (nSequenceID, sName, sComment, bValid))

  def UpdateSequenceDirtyFlag(self, sCurrentUsername, nSequenceID, bDirty):
    """Updates the sequence dirty flag"""
    self.Log(sCurrentUsername, "DBComm.UpdateSequenceDirtyFlag(%i, %i)" % (nSequenceID, bDirty))
    self.__CallStoredProcedure("UpdateSequenceDirtyFlag", (nSequenceID, bDirty))

  def DeleteSequence(self, sCurrentUsername, nSequenceID):
    """Delete a sequence"""
    self.Log(sCurrentUsername, "DBComm.DeleteSequence(%i)" % (nSequenceID, ))
    return self.__CallStoredProcedure("DeleteSequence", (nSequenceID, ))

  ### Reagent functions ###

  def GetReagent(self, sCurrentUsername, nReagentID):
    """Gets the specified reagent"""
    # Log the access and get the reagent
    self.Log(sCurrentUsername, "DBComm.GetReagent(%i)" % (nReagentID, ))
    pReagentRaw = self.__CallStoredProcedure("GetReagent", (nReagentID, ))
    if len(pReagentRaw) == 0:
        raise Exceptions.ReagentNotFoundException(nReagentID)
    return self.__CreateReagent(pReagentRaw[0])

  def GetReagentsBySequence(self, sCurrentUsername, nSequenceID):
    """Gets all reagents in the sequence"""
    # Log the access and get the reagents
    self.Log(sCurrentUsername, "DBComm.GetReagentsBySequence(%i)" % (nSequenceID, ))
    pReagentsRaw = self.__CallStoredProcedure("GetReagentsBySequence", (nSequenceID, ))

    # Create and return the reagent array
    pReagents = []
    for pReagentRaw in pReagentsRaw:
        pReagents.append(self.__CreateReagent(pReagentRaw))
    return pReagents

  def GetReagentsByName(self, sCurrentUsername, nSequenceID, sName):
    """Gets all reagents in the sequence that match the given name"""
    # Log the access and get the reagents
    self.Log(sCurrentUsername, "DBComm.GetReagentsByName(%i, %s)" % (nSequenceID, sName))
    pReagentsRaw = self.__CallStoredProcedure("GetReagentsByName", (nSequenceID, sName))

    # Create and return the reagent array
    pReagents = []
    for pReagentRaw in pReagentsRaw:
        pReagents.append(self.__CreateReagent(pReagentRaw))
    return pReagents

  def GetReagentByPosition(self, sCurrentUsername, nSequenceID, nCassette, sPosition):
    """Gets the reagent at the given position"""
    self.Log(sCurrentUsername, "DBComm.GetReagentByPosition(%i, %i, %s)" % (nSequenceID, nCassette, sPosition))
    pReagentRaw = self.__CallStoredProcedure("GetReagentByPosition", (nSequenceID, nCassette, sPosition))
    if len(pReagentRaw) == 0:
        raise Exceptions.ReagentNotFoundException(0, nSequenceID, nCassette, sPosition)
    return self.__CreateReagent(pReagentRaw[0])

  def GetReagentCassette(self, sCurrentUsername, nSequenceID, nReagentID):
    """Gets the cassette number that contains the given reagent"""
    self.Log(sCurrentUsername, "DBComm.GetReagentCassette(%i, %i)" % (nSequenceID, nReagentID))
    nCassette = 0
    pCassetteRaw = self.__CallStoredProcedure("GetReagentCassette", (nSequenceID, nReagentID, nCassette))
    return self.__ExecuteQuery("SELECT @_GetReagentCassette_2")[0][0]

  def UpdateReagent(self, sCurrentUsername, nReagentID, bAvailable, sName, sDescription):
    """Updates a existing reagent"""
    self.Log(sCurrentUsername, "DBComm.UpdateReagent(%i, %i, %s, %s)" % (nReagentID, bAvailable, sName, sDescription))
    return self.__CallStoredProcedure("UpdateReagent", (nReagentID, bAvailable, sName, sDescription))

  def UpdateReagentByPosition(self, sCurrentUsername, nSequenceID, nCassetteNumber, sPosition, bAvailable, sName, sDescription):
    """Update an existing reagent by position"""
    self.Log(sCurrentUsername, "DBComm.UpdateReagentByPosition(%i, %i, %s, %i, %s, %s)" % (nSequenceID, nCassetteNumber, sPosition, bAvailable, sName, sDescription))
    return self.__CallStoredProcedure("UpdateReagentByPosition", (nSequenceID, nCassetteNumber, sPosition, bAvailable, sName, sDescription))

  ### Component functions ###

  def GetComponent(self, sCurrentUsername, nComponentID):
    """Gets the specified component"""
    self.Log(sCurrentUsername, "DBComm.GetComponent(%i)" % (nComponentID, ))
    pComponent, nPreviousComponentID, nNextComponentID = self.__GetComponent(nComponentID)
    return pComponent

  def GetPreviousComponent(self, sCurrentUsername, nComponentID):
    """Gets the component previous to the one specified"""
    self.Log(sCurrentUsername, "DBComm.GetPreviousComponent(%i)" % (nComponentID, ))
    pComponent, nPreviousComponentID, nNextComponentID = self.__GetComponent(nComponentID)
    if nPreviousComponentID == 0:
        return None
    pComponent, nPreviousComponentID, nNextComponentID = self.__GetComponent(nPreviousComponentID)
    return pComponent

  def GetNextComponent(self, sCurrentUsername, nComponentID):
    """Gets the component after to the one specified"""
    self.Log(sCurrentUsername, "DBComm.GetPreviousComponent(%i)" % (nComponentID, ))
    pComponent, nPreviousComponentID, nNextComponentID = self.__GetComponent(nComponentID)
    if nNextComponentID == 0:
        return None
    pComponent, nPreviousComponentID, nNextComponentID = self.__GetComponent(nNextComponentID)
    return pComponent

  def GetCassette(self, sCurrentUsername, nSequenceID, nCassetteOffset):
    """Gets the cassette specified by the offset"""
    self.Log(sCurrentUsername, "DBComm.GetCassette(%i, %i)" % (nSequenceID, nCassetteOffset))
    pComponentRaw = self.__CallStoredProcedure("GetCassette", (nSequenceID, nCassetteOffset))
    if len(pComponentRaw) == 0:
        raise Exception("Failed to get cassette " + str(nCassetteOffset) + " of sequence " + str(nSequenceID))
    pComponent, nPreviousComponentID, nNextComponentID = self.__CreateComponent(pComponentRaw[0])
    return pComponent

  def GetComponentsBySequence(self, sCurrentUsername, nSequenceID):
    """Gets all of the components associated with the given sequence ID"""
    self.Log(sCurrentUsername, "DBComm.GetComponentsBySequence(%i)" % (nSequenceID, ))
    pComponentsRaw = self.__CallStoredProcedure("GetComponentsBySequence", (nSequenceID, ))
    pComponents = []
    for pComponentRaw in pComponentsRaw:
        pComponent, nPreviousComponentID, nNextComponentID = self.__CreateComponent(pComponentRaw)
        pComponents.append(pComponent)
    return pComponents

  def CreateComponent(self, sCurrentUsername, nSequenceID, sType, sName, sContent):
    """Creates a new component and inserts it at the end of a sequence"""
    self.Log(sCurrentUsername, "DBComm.CreateComponent(%i, %s, %s, %s)" % (nSequenceID, sType, sName, sContent))
    nComponentID = 0
    self.__CallStoredProcedure("CreateComponent", (nSequenceID, sType, sName, sContent, nComponentID))
    return self.__ExecuteQuery("SELECT @_CreateComponent_4")[0][0]

  def InsertComponent(self, sCurrentUsername, nSequenceID, sType, sName, sContent, nInsertID):
    """Inserts a component into a sequence"""
    self.Log(sCurrentUsername, "DBComm.InsertComponent(%i, %s, %s, %s, %i)" % (nSequenceID, sType, sName, sContent, nInsertID))
    nComponentID = 0
    self.__CallStoredProcedure("InsertComponent", (nSequenceID, sType, sName, sContent, nInsertID, nComponentID))
    return self.__ExecuteQuery("SELECT @_InsertComponent_5")[0][0]

  def UpdateComponent(self, sCurrentUsername, nComponentID, sType, sName, sDetails):
    """Updates the specified component"""
    self.Log(sCurrentUsername, "DBComm.UpdateComponent(%i, %s, %s, %s)" % (nComponentID, sType, sName, sDetails))
    self.__CallStoredProcedure("UpdateComponent", (nComponentID, sType, sName, sDetails))

  def MoveComponent(self, sCurrentUsername, nComponentID, nInsertAfterID):
    """Moves the specified component"""
    self.Log(sCurrentUsername, "DBComm.MoveComponent(%i, %i)" % (nComponentID, nInsertAfterID))
    self.__CallStoredProcedure("MoveComponent", (nComponentID, nInsertAfterID))

  def DeleteComponent(self, sCurrentUsername, nComponentID):
    """Deletes the component and removes it from the sequence"""
    self.Log(sCurrentUsername, "DBComm.DeleteComponent(%i)" % (nComponentID, ))
    return self.__CallStoredProcedure("DeleteComponent", (nComponentID, ))

  def EnableCassette(self, sCurrentUsername, nSequenceID, nCassette):
    """Enables the target cassette"""
    # Log the function call and get the raw cassette component
    self.Log(sCurrentUsername, "DBComm.EnableCassette(%i, %i)" % (nSequenceID, nCassette))
    pCassetteComponent = self.__CallStoredProcedure("GetCassette", (nSequenceID, nCassette))
    if (len(pCassetteComponent) == 0) or (len(pCassetteComponent[0]) == 0):
        raise Exception("Failed to get cassette " + str(nCassette) + " of sequence " + str(nSequenceID))

    # Update the "available" field in the JSON to true
    sDetailsJSON = pCassetteComponent[0][6]
    pDetails = json.loads(sDetailsJSON)
    pDetails["available"] = True;

    # Save the updated JSON back to the database
    sDetailsJSON = json.dumps(pDetails)
    self.UpdateComponent(sCurrentUsername, pCassetteComponent[0][0], pCassetteComponent[0][4], pCassetteComponent[0][5], sDetailsJSON)

  ### Internal functions ###

  def __CallStoredProcedure(self, sProcedureName, pArguments):
    """Calls the given SQL stored procedure"""
    try:
      # Call the stored procedure
      pCursor = self.__pDatabase.cursor()
      pCursor.callproc(sProcedureName, pArguments)
      pRows = pCursor.fetchall()
      pCursor.close()
      return pRows
    except MySQLdb.Error, e:
      raise Exception("SQL Error %d: %s" % (e.args[0],e.args[1]))

  def __ExecuteQuery(self, sQuery):
    """Executes the given SQL query"""
    try:
      # Execute the query
      pCursor = self.__pDatabase.cursor()
      pCursor.execute(sQuery)

      # Fetch and return all rows
      pRows = pCursor.fetchall()
      pCursor.close()
      return pRows
    except MySQLdb.Error, e:
      raise Exception("SQL Error %d: %s" % (e.args[0],e.args[1]))

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
    pComponent["name"] = pComponentRaw[5]
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
    pReagent["available"] = bool(pReagentRaw[4])
    pReagent["name"] = pReagentRaw[5]
    pReagent["namevalidation"] = "type=string; required=true"
    pReagent["description"] = pReagentRaw[6] 
    pReagent["descriptionvalidation"] = "type=string"
    return pReagent

