#!/usr/bin/python

# Imports
import GetHandler
import PostHandler
import sys
sys.path.append("/opt/elixys/core")
sys.path.append("/opt/elixys/database")
import Exceptions
from DBComm import *

def HandleSequenceNotFound(pCoreServer, pDatabase, pClientState, sRemoteUser, sPath, nSequenceID):
    """Handles the error when the server fails to find a sequence"""
    pDatabase.SystemLog(LOG_ERROR, sRemoteUser, "Failed to find sequence " + str(nSequenceID))

    # Was it the sequence that the user is currently on?
    if pClientState["sequenceid"] == nSequenceID:
        # Yes, so return the user to the last Select Sequence screen
        PostHandler.DirectToLastSelectScreen(pClientState)
        pDatabase.UpdateUserClientState(sRemoteUser, sRemoteUser, pClientState)
        pDatabase.SystemLog(LOG_WARNING, sRemoteUser, "Redirecting user to select sequences page")

    # Return the state
    pGetHandler = GetHandler.GetHandler(pCoreServer, pDatabase)
    return pGetHandler.HandleRequest(pClientState, sRemoteUser, "/state", None, 0)

def HandleComponentNotFound(pCoreServer, pDatabase, pClientState, sRemoteUser, sPath, nComponentID):
    """Handles the error when the server fails to find a component"""
    pDatabase.SystemLog(LOG_ERROR, sRemoteUser, "Failed to find component " + str(nComponentID))

    # Was it the component that the user is currently on?
    if pClientState["componentid"] == nComponentID:
        # Yes
        nSequenceID = 0
        try:
            # Get the sequence
            nSequenceID = pClientState["sequenceid"]
            pSequence = pDatabase.GetSequence(sRemoteUser, nSequenceID)

            # Move the client to the first unit operation
            pClientState["componentid"] = pSequence["components"][0]["id"]
            pDatabase.UpdateUserClientState(sRemoteUser, sRemoteUser, pClientState)
            pDatabase.SystemLog(LOG_WARNING, sRemoteUser, "Redirecting user to the first component of sequence " + str(nSequenceID))
        except Exceptions.SequenceNotFoundException as ex:
            # Sequence not found
            return HandleSequenceNotFound(pCoreServer, pDatabase, pClientState, sRemoteUser, sPath, nSequenceID)

    # Return the state
    pGetHandler = GetHandler.GetHandler(pCoreServer, pDatabase)
    return pGetHandler.HandleRequest(pClientState, sRemoteUser, "/state", None, 0)

def HandleReagentNotFound(pCoreServer, pDatabase, pClientState, sRemoteUser, sPath, nReagentID):
    """Handles the error when the server fails to find a reagent"""
    pDatabase.SystemLog(LOG_ERROR, sRemoteUser, "Failed to find reagent " + str(nReagentID))

    # This error should only occur if the user has the sequence they are currently viewing delete out from
    # under them.  Redirect them to the last Select Sequence screen
    PostHandler.DirectToLastSelectScreen(pClientState)
    pDatabase.UpdateUserClientState(sRemoteUser, sRemoteUser, pClientState)
    pDatabase.SystemLog(LOG_WARNING, sRemoteUser, "Redirecting user to select sequences page")

    # Return the state
    pGetHandler = GetHandler.GetHandler(pCoreServer, pDatabase)
    return pGetHandler.HandleRequest(pClientState, sRemoteUser, "/state", None, 0)

def HandleInvalidSequence(pDatabase, sRemoteUser, nSequenceID):
    """Handles the error when the use attempts to run an invalid sequence"""
    pDatabase.SystemLog(LOG_ERROR, sRemoteUser, "Cannot run invalid sequence (" + str(nSequenceID) + ")")
    return {"type":"error", "description":"Invalid sequence"}

def HandleGeneralException(pDatabase, sRemoteUser, sError):
    """Handles all other exceptions"""
    # Log the actual error and send the client a generic error
    if pDatabase != None:
        pDatabase.SystemLog(LOG_ERROR, sRemoteUser, sError)
    else:
        print sError
    return {"type":"error", "description":"An internal server error occurred"}

