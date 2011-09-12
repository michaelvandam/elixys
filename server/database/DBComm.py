"""DBComm

Elixys MySQL Database Comminication
"""

# Imports
import MySQLdb as SQL
import json
import datetime

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
      # Create the database connection
      self.__pDatabase = SQL.connect(host="localhost", user="Elixys", passwd="devel", db="Elixys");
    except:
      print "Unable to connect to SQL database"

  def Disconnect(self):
    """Disconnects from the database"""
    self.__pDatabase.close()
    self.__pDatabase = None

  ### Role functions ###

  def GetAllRoles(self, sCurrentUsername):
    """Returns all user roles"""
    self.__LogDBAccess(sCurrentUsername, "GetAllRoles()")
    return self.__CallStoredProcedure("GetRoles", ())

  def GetRole(self, sCurrentUsername, sRoleName):
    """Returns the desired role"""
    self.__LogDBAccess(sCurrentUsername, "GetRole(%s)" % (sRoleName, ))
    return self.__CallStoredProcedure("GetRole", (sRoleName, ))

  def CreateRole(self, sCurrentUsername, sRoleName, nFlags):
    """Creates the specified role"""
    self.__LogDBAccess(sCurrentUsername, "CreateRole(%s, %i)" % (sRoleName, nFlags))
    return self.__CallStoredProcedure("CreateRole", (sRoleName, nFlags), True)

  def UpdateRole(self, sCurrentUsername, sRoleName, sUpdateRoleName, nUpdatedFlags):
    """Updates the specified role"""
    self.__LogDBAccess(sCurrentUsername, "UpdateRole(%s, %s, %i)" % (sRoleName, sUpdateRoleName, nUpdatedFlags))
    return self.__CallStoredProcedure("UpdateRole", (sRoleName, sUpdateRoleName, nUpdatedFlags), True)

  def DeleteRole(self, sCurrentUsername, sRoleName):
    """Deletes the specified role"""
    self.__LogDBAccess(sCurrentUsername, "DeleteRole(%s)" % (sRoleName, ))
    return self.__CallStoredProcedure("DeleteRole", (sRoleName, ), True)

  ### User functions ###

  def GetAllUsers(self, sCurrentUsername):
    """Returns details of all system users"""
    self.__LogDBAccess(sCurrentUsername, "GetAllUsers()")
    return self.__CallStoredProcedure("GetAllUsers", ())

  def GetUser(self, sCurrentUsername, sUsername):
    """Returns details of the specified user"""
    # Load the database access and get the user data
    self.__LogDBAccess(sCurrentUsername, "GetUser(%s)" % (sUsername, ))
    pUserRaw = self.__CallStoredProcedure("GetUser", (sUsername, ))

    # Create the user object
    pUser = {}
    pUser["username"] = pUserRaw[0][0]
    pUser["firstname"] = pUserRaw[0][1]
    pUser["lastname"] = pUserRaw[0][2]
    pUser["useraccesslevel"] = pUserRaw[0][3]
    return pUser

  def CreateUser(self, sCurrentUsername, sUsername, sPasswordHash, sFirstName, sLastName, sRoleName):
    """Creates a new user"""
    self.__LogDBAccess(sCurrentUsername, "CreateUser(%s, %s, %s, %s, %s)" % (sUsername, sPasswordHash, sFirstName, sLastName, sRoleName))
    return self.__CallStoredProcedure("CreateUser", (sUsername, sPasswordHash, sFirstName, sLastName, sRoleName), True)

  def UpdateUser(self, sCurrentUsername, sUsername, sFirstName, sLastName, sRoleName):
    """Updates an existing user"""
    self.__LogDBAccess(sCurrentUsername, "UpdateUser(%s, %s, %s, %s)" % (sUsername, sFirstName, sLastName, sRoleName))
    return self.__CallStoredProcedure("UpdateUser", (sUsername, sFirstName, sLastName, sRoleName), True)

  def UpdateUserPassword(self, sCurrentUsername, sUsername, sPasswordHash):
    """Updates an existing user's password"""
    self.__LogDBAccess(sCurrentUsername, "UpdateUserPassword(%s, %s)" % (sUsername, sPasswordHash))
    return self.__CallStoredProcedure("UpdateUserPassword", (sUsername, sPasswordHash), True)

  def DeleteUser(self, sCurrentUsername, sUsername):
    """Deletes an existing user"""
    self.__LogDBAccess(sCurrentUsername, "DeleteUser(%s, %s, %s, %s)" % (sUsername, DeleteUser))
    return self.__CallStoredProcedure("DeleteUser", (sUsername, ), True)

  def GetUserClientState(self, sCurrentUsername, sUsername):
    """Returns the client state of a user"""
    self.__LogDBAccess(sCurrentUsername, "GetUserClientState(%s)" % (sUsername, ))
    pUserClientState = self.__CallStoredProcedure("GetUserClientState", (sUsername, ))
    return pUserClientState[0][0]

  def UpdateUserClientState(self, sCurrentUsername, sUsername, sClientState):
    """Updates the client state of a user"""
    self.__LogDBAccess(sCurrentUsername, "UpdateUserClientState(%s, %s)" % (sUsername, sClientState))
    return self.__CallStoredProcedure("UpdateUserClientState", (sUsername, sClientState), True)

  ### Sequence functions ###

  def GetAllSequences(self, sCurrentUsername, sType):
    """Return all sequences"""
    # Load the access and get the sequence data
    self.__LogDBAccess(sCurrentUsername, "GetAllSequences(%s)" % (sType, ))
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
      pSequences.append(pSequence)

    # Return
    return pSequences

  def GetSequence(self, sCurrentUsername, nSequenceID):
    """Gets a sequence"""
    # Log the function call and get the sequence data
    self.__LogDBAccess(sCurrentUsername, "GetSequence(%i)" % (nSequenceID, ))
    pSequenceRaw = self.__CallStoredProcedure("GetSequence", (nSequenceID, ))

    # Fill in the sequence metadata
    pSequence = {}
    pSequence["metadata"] = {}
    pSequence["metadata"]["id"] = int(pSequenceRaw[0][0])
    pSequence["metadata"]["name"] = pSequenceRaw[0][1]
    pSequence["metadata"]["comment"] = pSequenceRaw[0][2]
    pSequence["metadata"]["date"] = pSequenceRaw[0][4].strftime("%m/%d/%Y")
    pSequence["metadata"]["time"] = pSequenceRaw[0][4].strftime("%H:%M.%S")
    pSequence["metadata"]["creator"] = pSequenceRaw[0][5]
    pSequence["metadata"]["components"] = int(pSequenceRaw[0][7])

    # Load the components in order
    nComponentID = int(pSequenceRaw[0][6])
    pSequence["components"] = []
    while nComponentID != 0:
        # Get the component
        pComponent, nPreviousComponentID, nNextComponentID = self.__GetComponent(nComponentID)
        pSequence["components"].append(pComponent)
        nComponentID = nNextComponentID

    # Return
    return pSequence

  def CreateSequence(self, sCurrentUsername, sName, sComment, sType, nCassettes, nReagents, nColumns):
    """Creates a new sequence"""
    self.__LogDBAccess(sCurrentUsername, "CreateSequence(%s, %s, %s, %i, %i, %i)" % (sName, sComment, sType, nCassettes, nReagents, nColumns))
    nSequenceID = 0
    self.__CallStoredProcedure("CreateSequence", (sName, sComment, sType, sCurrentUsername, nCassettes, nReagents, nColumns, nSequenceID), True)
    return self.__ExecuteQuery("SELECT @_CreateSequence_7")[0][0]

  def UpdateSequence(self, sCurrentUsername, nSequenceID, sName, sComment):
    """Update a sequence"""
    self.__LogDBAccess(sCurrentUsername, "UpdateSequence(%i, %s, %s)" % (nSequenceID, sName, sComment))
    return self.__CallStoredProcedure("UpdateSequence", (nSequenceID, sName, sComment), True)

  def DeleteSequence(self, sCurrentUsername, nSequenceID):
    """Delete a sequence"""
    self.__LogDBAccess(sCurrentUsername, "DeleteSequence(%i)" % (nSequenceID, ))
    return self.__CallStoredProcedure("DeleteSequence", (nSequenceID, ), True)

  ### Reagent functions ###

  def GetReagent(self, sCurrentUsername, nReagentID):
    """Gets the specified reagent"""
    # Log the access and get the reagent
    self.__LogDBAccess(sCurrentUsername, "GetReagent(%i)" % (nReagentID, ))
    return self.__CreateReagent(self.__CallStoredProcedure("GetReagent", (nReagentID, ))[0])

  def GetReagentsByName(self, sCurrentUsername, nSequenceID, sName):
    """Gets all reagents in the sequence that match the given name"""
    # Log the access and get the reagents
    self.__LogDBAccess(sCurrentUsername, "GetReagentsByName(%i, %s)" % (nSequenceID, sName))
    pReagentsRaw = self.__CallStoredProcedure("GetReagentsByName", (nSequenceID, sName))

    # Create and return the reagent array
    pReagents = []
    for pReagentRaw in pReagentsRaw:
        pReagents.append(self.__CreateReagent(pReagentRaw))
    return pReagents

  def GetReagentByPosition(self, sCurrentUsername, nSequenceID, nCassette, sPosition):
    """Gets the reagent at the given position"""
    self.__LogDBAccess(sCurrentUsername, "GetReagentByPosition(%i, %i, %s)" % (nSequenceID, nCassette, sPosition))
    return self.__CreateReagent(self.__CallStoredProcedure("GetReagentByPosition", (nSequenceID, nCassette, sPosition))[0])

  def GetReservedReagentsByName(self, sCurrentUsername, sName):
    """Gets all reserved reagents in the database that match the given name"""
    self.__LogDBAccess(sCurrentUsername, "GetReservedReagentsByName(%s)" % (sName, ))
    return self.__CallStoredProcedure("GetReservedReagentsByName", (sName, ))

  def UpdateReagent(self, sCurrentUsername, nReagentID, bAvailable, sName, sDescription):
    """Updates a existing reagent"""
    self.__LogDBAccess(sCurrentUsername, "UpdateReagent(%i, %i, %s, %s)" % (nReagentID, bAvailable, sName, sDescription))
    return self.__CallStoredProcedure("UpdateReagent", (nReagentID, bAvailable, sName, sDescription), True)

  def UpdateReagentByPosition(self, sCurrentUsername, nSequenceID, nCassetteNumber, sPosition, bAvailable, sName, sDescription):
    """Update an existing reagent by position"""
    self.__LogDBAccess(sCurrentUsername, "UpdateReagentByPosition(%i, %i, %s, %i, %s, %s)" % (nSequenceID, nCassetteNumber, sPosition, bAvailable, sName, sDescription))
    return self.__CallStoredProcedure("UpdateReagentByPosition", (nSequenceID, nCassetteNumber, sPosition, bAvailable, sName, sDescription), True)

  def CreateReservedReagent(self, sCurrentUsername, sName, sDescription):
    """Creates a reserved reagent"""
    self.__LogDBAccess(sCurrentUsername, "CreateReservedReagent(%s, %s)" % (sName, sDescription))
    return self.__CallStoredProcedure("CreateReservedReagent", (sName, sDescription), True)

  ### Component functions ###

  def GetComponent(self, sCurrentUsername, nComponentID):
    """Gets the specified component"""
    self.__LogDBAccess(sCurrentUsername, "GetComponent(%i)" % (nComponentID, ))
    pComponent, nPreviousComponentID, nNextComponentID = self.__GetComponent(nComponentID)
    return pComponent

  def GetPreviousComponent(self, sCurrentUsername, nComponentID):
    """Gets the component previous to the one specified"""
    self.__LogDBAccess(sCurrentUsername, "GetPreviousComponent(%i)" % (nComponentID, ))
    pComponent, nPreviousComponentID, nNextComponentID = self.__GetComponent(nComponentID)
    if nPreviousComponentID == 0:
        return None
    pComponent, nPreviousComponentID, nNextComponentID = self.__GetComponent(nPreviousComponentID)
    return pComponent

  def GetNextComponent(self, sCurrentUsername, nComponentID):
    """Gets the component after to the one specified"""
    self.__LogDBAccess(sCurrentUsername, "GetPreviousComponent(%i)" % (nComponentID, ))
    pComponent, nPreviousComponentID, nNextComponentID = self.__GetComponent(nComponentID)
    if nNextComponentID == 0:
        return None
    pComponent, nPreviousComponentID, nNextComponentID = self.__GetComponent(nNextComponentID)
    return pComponent

  def GetCassette(self, sCurrentUsername, nSequenceID, nCassetteOffset):
    """Gets the cassette specified by the offset"""
    self.__LogDBAccess(sCurrentUsername, "GetCassette(%i, %i)" % (nSequenceID, nCassetteOffset))
    pComponentRaw = self.__CallStoredProcedure("GetCassette", (nSequenceID, nCassetteOffset))
    pComponent, nPreviousComponentID, nNextComponentID = self.__CreateComponent(pComponentRaw)
    return pComponent

  def CreateComponent(self, sCurrentUsername, nSequenceID, sType, sName, sContent):
    """Creates a new component and inserts it at the end of a sequence"""
    self.__LogDBAccess(sCurrentUsername, "CreateComponent(%i, %s, %s, %s)" % (nSequenceID, sType, sName, sContent))
    nComponentID = 0
    self.__CallStoredProcedure("CreateComponent", (nSequenceID, sType, sName, sContent, nComponentID), True)
    return self.__ExecuteQuery("SELECT @_CreateComponent_4")[0][0]

  def InsertComponent(self, sCurrentUsername, nSequenceID, sType, sName, sContent, nInsertID):
    """Inserts a component into a sequence"""
    self.__LogDBAccess(sCurrentUsername, "InsertComponent(%i, %s, %s, %s, %i)" % (nSequenceID, sType, sName, sContent, nInsertID))
    nComponentID = 0
    self.__CallStoredProcedure("InsertComponent", (nSequenceID, sType, sName, sContent, nInsertID, nComponentID), True)
    return self.__ExecuteQuery("SELECT @_InsertComponent_5")[0][0]

  def UpdateComponent(self, sCurrentUsername, nComponentID, sType, sName, sDetails):
    """Updates the specified component"""
    self.__LogDBAccess(sCurrentUsername, "UpdateComponent(%i, %s, %s, %s)" % (nComponentID, sType, sName, sDetails))
    self.__CallStoredProcedure("UpdateComponent", (nComponentID, sType, sName, sDetails), True)

  def MoveComponent(self, sCurrentUsername, nComponentID, nInsertAfterID):
    """Moves the specified component"""
    self.__LogDBAccess(sCurrentUsername, "MoveComponent(%i, %i)" % (nComponentID, nInsertAfterID))
    self.__CallStoredProcedure("MoveComponent", (nComponentID, nInsertAfterID), True)

  def DeleteComponent(self, sCurrentUsername, nComponentID):
    """Deletes the component and removes it from the sequence"""
    self.__LogDBAccess(sCurrentUsername, "DeleteComponent(%i)" % (nComponentID, ))
    return self.__CallStoredProcedure("DeleteComponent", (nComponentID, ), True)

  def EnableCassette(self, sCurrentUsername, nSequenceID, nCassette):
    """Enables the target cassette"""
    # Log the function call and get the cassette component
    self.__LogDBAccess(sCurrentUsername, "EnableCassette(%i, %i)" % (nSequenceID, nCassette))
    pCassetteComponent = self.__CallStoredProcedure("GetCassette", (nSequenceID, nCassette))

    # Update the "available" field in the JSON to true
    sDetailsJSON = pCassetteComponent[0][6]
    pDetails = json.loads(sDetailsJSON)
    pDetails["available"] = True;

    # Save the updated JSON back to the database
    sDetailsJSON = json.dumps(pDetails)
    self.UpdateComponent(sCurrentUsername, pCassetteComponent[0][0], pCassetteComponent[0][4], pCassetteComponent[0][5], sDetailsJSON)

  ### Internal functions ###

  def __LogDBAccess(self, sUsername, sMessage):
    """Logs that the given user has accessed the database"""
    with open("/var/www/wsgi/dblog.txt", "a") as myfile:
        now = datetime.datetime.now()
        myfile.write(now.strftime("%H:%M:%S") + "  " + sUsername + " called " + sMessage + "\n")

  def __CallStoredProcedure(self, sProcedureName, pArguments, bCommit = False):
    """Calls the given SQL stored procedure"""
    try:
      # Call the stored procedure
      pCursor = self.__pDatabase.cursor()
      pCursor.callproc(sProcedureName, pArguments)
      pRows = pCursor.fetchall()
      pCursor.close()

      # Commit the transaction and return the result
      if bCommit:
          self.__pDatabase.commit()
      return pRows
    except SQL.Error, e:
      # Report error
      print "SQL Error %d: %s" % (e.args[0],e.args[1])

  def __ExecuteQuery(self, sQuery):
    """Executes the given SQL query"""
    try:
      # Execute the query
      pCursor = self.__pDatabase.cursor()
      pCursor.execute(sQuery)
      self.__pDatabase.commit()

      # Fetch and return all rows
      pRows = pCursor.fetchall()
      pCursor.close()
      return pRows
    except SQL.Error, e:
      # Report error
      print "SQL Error %d: %s" % (e.args[0],e.args[1])

  def __GetComponent(self, nComponentID):
    """Fetches and packages a component"""
    pComponentRaw = self.__CallStoredProcedure("GetComponent", (nComponentID, ))
    return self.__CreateComponent(pComponentRaw)

  def __CreateComponent(self, pComponentRaw):
    """Packages a component"""
    pComponent = json.loads(pComponentRaw[0][6])
    pComponent["id"] = int(pComponentRaw[0][0])
    pComponent["name"] = pComponentRaw[0][5]
    nPreviousComponentID = int(pComponentRaw[0][2])
    nNextComponentID = int(pComponentRaw[0][3])
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
    pReagent["description"] = pReagentRaw[6] 
    return pReagent

if __name__ == '__main__':
  pDBComm = DBComm()
  pReturn = pDBComm.EnableCassette("System", 1, 2)
  print "Enable cassette: " + str(pReturn)

