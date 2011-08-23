"""DBComm

Elixys MySQL Database Comminication
"""

# Imports
import MySQLdb as SQL

# Suppress MySQLdb's annoying warnings
import warnings
warnings.filterwarnings("ignore", "Unknown table.*")

# Database wrapper class
class DBComm:
  ### Construction / Destruction ###

  def __init__(self):
    """Initializes the DBComm class"""
    # Create the database connection
    try:
      self.__pDatabase = SQL.connect(host="localhost", user="Elixys", passwd="devel", db="Elixys");
    except:
      print "Unable to connect to SQL database."

  ### Role functions ###

  def GetAllRoles(self, sCurrentUsername):
    """Returns all user roles"""
    self.__LogDBAccess(sCurrentUsername, "GetAllRoles()")
    return self.__callStoredProcedure("GetRoles", ())

  def GetRole(self, sCurrentUsername, sRoleName):
    """Returns the desired role"""
    self.__LogDBAccess(sCurrentUsername, "GetRole(%s)" % (sRoleName, ))
    return self.__callStoredProcedure("GetRole", (sRoleName, ))

  def CreateRole(self, sCurrentUsername, sRoleName, nFlags):
    """Creates the specified role"""
    self.__LogDBAccess(sCurrentUsername, "CreateRole(%s, %i)" % (sRoleName, nFlags))
    return self.__callStoredProcedure("CreateRole", (sRoleName, nFlags), True)

  def UpdateRole(self, sCurrentUsername, sRoleName, sUpdateRoleName, nUpdatedFlags):
    """Updates the specified role"""
    self.__LogDBAccess(sCurrentUsername, "UpdateRole(%s, %s, %i)" % (sRoleName, sUpdateRoleName, nUpdatedFlags))
    return self.__callStoredProcedure("UpdateRole", (sRoleName, sUpdateRoleName, nUpdatedFlags), True)

  def DeleteRole(self, sCurrentUsername, sRoleName):
    """Deletes the specified role"""
    self.__LogDBAccess(sCurrentUsername, "DeleteRole(%s)" % (sRoleName, ))
    return self.__callStoredProcedure("DeleteRole", (sRoleName, ), True)

  ### User functions ###

  def GetAllUsers(self, sCurrentUsername):
    """Returns details of all system users"""
    self.__LogDBAccess(sCurrentUsername, "GetAllUsers()")
    return self.__callStoredProcedure("GetAllUsers", ())

  def GetUser(self, sCurrentUsername, sUsername):
    """Returns details of the specified user"""
    self.__LogDBAccess(sCurrentUsername, "GetUser(%s)" % (Username, ))
    return self.__callStoredProcedure("GetUser", (sUsername, ))

  def CreateUser(self, sCurrentUsername, sUsername, sPasswordHash, sFirstName, sLastName, sRoleName):
    """Creates a new user"""
    self.__LogDBAccess(sCurrentUsername, "CreateUser(%s, %s, %s, %s, %s)" % (sUsername, sPasswordHash, sFirstName, sLastName, sRoleName))
    return self.__callStoredProcedure("CreateUser", (sUsername, sPasswordHash, sFirstName, sLastName, sRoleName), True)

  def UpdateUser(self, sCurrentUsername, sUsername, sFirstName, sLastName, sRoleName):
    """Updates an existing user"""
    self.__LogDBAccess(sCurrentUsername, "UpdateUser(%s, %s, %s, %s)" % (sUsername, sFirstName, sLastName, sRoleName))
    return self.__callStoredProcedure("UpdateUser", (sUsername, sFirstName, sLastName, sRoleName), True)

  def UpdateUserPassword(self, sCurrentUsername, sUsername, sPasswordHash):
    """Updates an existing user's password"""
    self.__LogDBAccess(sCurrentUsername, "UpdateUserPassword(%s, %s)" % (sUsername, sPasswordHash))
    return self.__callStoredProcedure("UpdateUserPassword", (sUsername, sPasswordHash), True)

  def DeleteUser(self, sCurrentUsername, sUsername):
    """Deletes an existing user"""
    self.__LogDBAccess(sCurrentUsername, "DeleteUser(%s, %s, %s, %s)" % (sUsername, DeleteUser))
    return self.__callStoredProcedure("DeleteUser", (sUsername, ), True)

  def GetUserClientState(self, sCurrentUsername, sUsername):
    """Returns the client state of a user"""
    self.__LogDBAccess(sCurrentUsername, "GetUserClientState(%s)" % (Username, ))
    return self.__callStoredProcedure("GetUserClientState", (sUsername, ))

  def UpdateUserClientState(self, sCurrentUsername, sUsername, sClientState):
    """Updates the client state of a user"""
    self.__LogDBAccess(sCurrentUsername, "UpdateUserClientState(%s, %s)" % (sUsername, sClientState))
    return self.__callStoredProcedure("UpdateUserClientState", (sUsername, sClientState), True)

  ### Sequence functions ###

  def GetAllSequences(self, sCurrentUsername, sType):
    """Return all sequences"""
    self.__LogDBAccess(sCurrentUsername, "GetAllSequences(%s)" % (sType, ))
    return self.__callStoredProcedure("GetAllSequences", (sType, ))

  def GetSequence(self, sCurrentUsername, nSequenceID):
    """Gets a sequence"""
    self.__LogDBAccess(sCurrentUsername, "GetSequence(%i)" % (nSequenceID, ))
    return self.__callStoredProcedure("GetSequence", (nSequenceID, ))

  def CreateSequence(self, sCurrentUsername, sName, sComment, sType, nCassettes, nReagents, nColumns):
    """Creates a new sequence"""
    self.__LogDBAccess(sCurrentUsername, "CreateSequence(%s, %s, %s, %i, %i, %i)" % (sName, sComment, sType, nCassettes, nReagents, nColumns))
    nSequenceID = 0
    self.__callStoredProcedure("CreateSequence", (sName, sComment, sType, sCurrentUsername, nCassettes, nReagents, nColumns, nSequenceID), True)
    return self.__executeQuery("SELECT @_CreateSequence_7")[0][0]

  def UpdateSequence(self, sCurrentUsername, nSequenceID, sName, sComment):
    """Update a sequence"""
    self.__LogDBAccess(sCurrentUsername, "UpdateSequence(%i, %s, %s)" % (nSequenceID, sName, sComment))
    return self.__callStoredProcedure("UpdateSequence", (nSequenceID, sName, sComment), True)

  def DeleteSequence(self, sCurrentUsername, nSequenceID):
    """Delete a sequence"""
    self.__LogDBAccess(sCurrentUsername, "DeleteSequence(%i)" % (nSequenceID, ))
    return self.__callStoredProcedure("DeleteSequence", (nSequenceID, ), True)

  ### Reagent functions ###

  def GetReagent(self, sCurrentUsername, nReagentID):
    """Gets the specified reagent"""
    self.__LogDBAccess(sCurrentUsername, "GetReagent(%i)" % (nReagentID, ))
    return self.__callStoredProcedure("GetReagent", (nReagentID, ))

  def GetReagentsByName(self, sCurrentUsername, nSequenceID, sName):
    """Gets all reagents in the sequence that match the given name"""
    self.__LogDBAccess(sCurrentUsername, "GetReagentsByName(%i, %s)" % (nSequenceID, sName))
    return self.__callStoredProcedure("GetReagentsByName", (nSequenceID, sName))

  def GetReservedReagentsByName(self, sCurrentUsername, sName):
    """Gets all reserved reagents in the database that match the given name"""
    self.__LogDBAccess(sCurrentUsername, "GetReservedReagentsByName(%s)" % (sName, ))
    return self.__callStoredProcedure("GetReservedReagentsByName", (sName, ))

  def UpdateReagent(self, sCurrentUsername, nReagentID, bAvailable, sName, sDescription):
    """Updates a existing reagent"""
    self.__LogDBAccess(sCurrentUsername, "UpdateReagent(%i, %i, %s, %s)" % (nReagentID, bAvailable, sName, sDescription))
    return self.__callStoredProcedure("UpdateReagent", (nReagentID, bAvailable, sName, sDescription), True)

  def UpdateReagentByPosition(self, sCurrentUsername, nSequenceID, nCassetteNumber, sPosition, bAvailable, sName, sDescription):
    """Update an existing reagent by position"""
    self.__LogDBAccess(sCurrentUsername, "UpdateReagentByPosition(%i, %i, %s, %i, %s, %s)" % (nSequenceID, nCassetteNumber, sPosition, bAvailable, sName, sDescription))
    return self.__callStoredProcedure("UpdateReagentByPosition", (nSequenceID, nCassetteNumber, sPosition, bAvailable, sName, sDescription), True)

  def CreateReservedReagent(self, sCurrentUsername, sName, sDescription):
    """Creates a reserved reagent"""
    self.__LogDBAccess(sCurrentUsername, "CreateReservedReagent(%s, %s)" % (sName, sDescription))
    return self.__callStoredProcedure("CreateReservedReagent", (sName, sDescription), True)

  ### Component functions ###

  def GetComponent(self, sCurrentUsername, nComponentID):
    """Gets the specified component"""
    self.__LogDBAccess(sCurrentUsername, "GetComponent(%i)" % (nComponentID, ))
    return self.__callStoredProcedure("GetComponent", (nComponentID, ))

  def GetSequenceComponents(self, sCurrentUsername, nSequenceID):
    """Gets all components associated with a sequence"""
    self.__LogDBAccess(sCurrentUsername, "GetSequenceComponents(%i)" % (nSequenceID, ))
    return self.__callStoredProcedure("GetSequenceComponents", (nSequenceID, ))

  def CreateComponent(self, sCurrentUsername, nSequenceID, sType, sName, sContent):
    """Creates a new component and inserts it at the end of a sequence"""
    self.__LogDBAccess(sCurrentUsername, "CreateComponent(%i, %s, %s, %s)" % (nSequenceID, sType, sName, sContent))
    nComponentID = 0
    self.__callStoredProcedure("CreateComponent", (nSequenceID, sType, sName, sContent, nComponentID), True)
    return self.__executeQuery("SELECT @_CreateComponent_4")[0][0]

  def InsertComponent(self, sCurrentUsername, nSequenceID, sType, sName, sContent, nInsertID):
    """Inserts a component into a sequence"""
    self.__LogDBAccess(sCurrentUsername, "InsertComponent(%i, %s, %s, %s, %i)" % (nSequenceID, sType, sName, sContent, nInsertID))
    nComponentID = 0
    self.__callStoredProcedure("InsertComponent", (nSequenceID, sType, sName, sContent, nInsertID), True)
    return self.__executeQuery("SELECT @_InsertComponent_5")[0][0]

  def DeleteComponent(self, sCurrentUsername, nComponentID):
    """Deletes the component and removes it from the sequence"""
    self.__LogDBAccess(sCurrentUsername, "DeleteComponent(%i)" % (nComponentID, ))
    return self.__callStoredProcedure("DeleteComponent", (nComponentID, ), True)

  ### Internal functions ###

  def __LogDBAccess(self, sUsername, sMessage):
    """Logs that the given user has accessed the database"""
    pass

  def __callStoredProcedure(self, sProcedureName, pArguments, bCommit = False):
    """Calls the given SQL stored procedure"""
    try:
      # Call the stored procedure
      pCursor = self.__pDatabase.cursor()
      pCursor.callproc(sProcedureName, pArguments)
      if bCommit:
          self.__pDatabase.commit()

      # Fetch and return all rows
      pRows = pCursor.fetchall()
      pCursor.close()
      return pRows
    except SQL.Error, e:
      # Report error
      print "SQL Error %d: %s" % (e.args[0],e.args[1])

  # This is temporary and will no longer work once the database is properly configured!
  def __executeQuery(self, sQuery):
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

if __name__ == '__main__':
  pDBComm = DBComm()
  pReturn = pDBComm.CreateUser("shane", "test1", "pwd", "f", "l", "Researcher")
  print "Create user: " + str(pReturn)

