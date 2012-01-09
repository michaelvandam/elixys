#!/usr/bin/python

# Imports
import GetHandler
import sys
sys.path.append("/opt/elixys/core")
sys.path.append("/opt/elixys/database")
import Exceptions
from DBComm import *

def HandleSequenceNotFound(pCoreServer, pDatabase, pClientState, sRemoteUser, sPath, nSequenceID):
    """ Handles the error when the server fails to find a sequence """
    pDatabase.SystemLog(LOG_ERROR, sRemoteUser, "Failed to find sequence " + str(nSequenceID))

    # Was it the sequence that the user is currently on?
    if pClientState["sequenceid"] == nSequenceID:
        # Yes, so return the user to the select sequence screen
        pClientState["screen"] = "SELECT_SAVEDSEQUENCES"
        pDatabase.UpdateUserClientState(sRemoteUser, sRemoteUser, pClientState)
        pDatabase.SystemLog(LOG_WARNING, sRemoteUser, "Redirecting user to select sequences page")

    # Return the state
    pGetHandler = GetHandler.GetHandler(pCoreServer, pDatabase)
    return pGetHandler.HandleRequest(pClientState, sRemoteUser, "/state", None, 0)

def HandleComponentNotFound(pCoreServer, pDatabase, pClientState, sRemoteUser, sPath, nComponentID):
    """ Handles the error when the server fails to find a component """
    pDatabase.SystemLog(LOG_ERROR, sRemoteUser, "Failed to find component " + str(nComponentID))

    # Was it the component that the user is currently on?
    if pClientState["componentid"] == nComponentID:
        # Yes
        try:
            # Get the sequence
            pSequence = pDatabase.GetSequence(sRemoteUser, pClientState["sequenceid"])

            # Move the client to the first unit operation
            pClientState["componentid"] = pSequence["components"][0]["id"]
            pDatabase.UpdateUserClientState(sRemoteUser, sRemoteUser, pClientState)
            pDatabase.SystemLog(LOG_WARNING, sRemoteUser, "Redirecting user to the first component of sequence " + str(pClientState["sequenceid"]))
        except Exceptions.SequenceNotFoundException as ex:
            # Sequence not found
            return HandleSequenceNotFound(pCoreServer, pDatabase, pClientState, sRemoteUser, sPath, nClientStateSequenceID)

    # Return the state
    pGetHandler = GetHandler.GetHandler(pCoreServer, pDatabase)
    return pGetHandler.HandleRequest(pClientState, sRemoteUser, "/state", None, 0)

def HandleReagentNotFound(pCoreServer, pDatabase, pClientState, sRemoteUser, sPath, nReagentID):
    """ Handles the error when the server fails to find a reagent """
    pDatabase.SystemLog(LOG_ERROR, sRemoteUser, "Failed to find reagent " + str(nReagentID))

    # This error should only occur if the user has the sequence they are currently viewing delete out from
    # under them.  Redirect them to the select sequence screen
    pClientState["screen"] = "SELECT_SAVEDSEQUENCES"
    pDatabase.UpdateUserClientState(sRemoteUser, sRemoteUser, pClientState)
    pDatabase.SystemLog(LOG_WARNING, sRemoteUser, "Redirecting user to select sequences page")

    # Return the state
    pGetHandler = GetHandler.GetHandler(pCoreServer, pDatabase)
    return pGetHandler.HandleRequest(pClientState, sRemoteUser, "/state", None, 0)

