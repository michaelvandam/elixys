#!/usr/bin/python

# Imports
import GetHandler
import sys
sys.path.append("/opt/elixys/core")
import Exceptions

def HandleSequenceNotFound(pCoreServer, pDatabase, sClientState, sRemoteUser, sPath, nSequenceID):
    """ Handles the error when the server fails to find a sequence """
    pDatabase.Log(sRemoteUser, "Failed to find sequence " + str(nSequenceID))

    # Was it the sequence that the user is currently on?
    pClientStateComponents = sClientState.split(".")
    if len(pClientStateComponents) > 1:
        nClientStateSequenceID = int(pClientStateComponents[1])
        if (nClientStateSequenceID == nSequenceID):
            # Yes, so return the user to the select sequence screen
            sClientState = "SELECT_SAVEDSEQUENCES"
            pDatabase.UpdateUserClientState(sRemoteUser, sRemoteUser, sClientState)
            pDatabase.Log(sRemoteUser, "Redirecting user to select sequences page")

    # Return the state
    pGetHandler = GetHandler.GetHandler(pCoreServer, pDatabase)
    return pGetHandler.HandleRequest(sClientState, sRemoteUser, "/state", None, 0)

def HandleComponentNotFound(pCoreServer, pDatabase, sClientState, sRemoteUser, sPath, nComponentID):
    """ Handles the error when the server fails to find a component """
    pDatabase.Log(sRemoteUser, "Failed to find component " + str(nComponentID))

    # Was it the component that the user is currently on?
    pClientStateComponents = sClientState.split(".")
    if len(pClientStateComponents) > 2:
        nClientStateSequenceID = int(pClientStateComponents[1])
        nClientStateComponentID = int(pClientStateComponents[2])
        if (nClientStateComponentID == nComponentID):
            # Yes
            try:
                # Get the sequence
                pSequence = pDatabase.GetSequence(sRemoteUser, nClientStateSequenceID)

                # Move the client to the first unit operation
                sClientState = pClientStateComponents[0] + "." + str(nClientStateSequenceID) + "." + str(pSequence["components"][0]["id"])
                pDatabase.UpdateUserClientState(sRemoteUser, sRemoteUser, sClientState)
                pDatabase.Log(sRemoteUser, "Redirecting user to the first component of sequence " + str(nClientStateSequenceID))
            except Exceptions.SequenceNotFoundException as ex:
                # Sequence not found
                return HandleSequenceNotFound(pCoreServer, pDatabase, sClientState, sRemoteUser, sPath, nClientStateSequenceID)

    # Return the state
    pGetHandler = GetHandler.GetHandler(pCoreServer, pDatabase)
    return pGetHandler.HandleRequest(sClientState, sRemoteUser, "/state", None, 0)

def HandleReagentNotFound(pCoreServer, pDatabase, sClientState, sRemoteUser, sPath, nReagentID):
    """ Handles the error when the server fails to find a reagent """
    pDatabase.Log(sRemoteUser, "Failed to find reagent " + str(nReagentID))

    # This error should only occur if the user has the sequence they are currently viewing delete out from
    # under them.  Redirect them to the select sequence screen
    sClientState = "SELECT_SAVEDSEQUENCES"
    pDatabase.UpdateUserClientState(sRemoteUser, sRemoteUser, sClientState)
    pDatabase.Log(sRemoteUser, "Redirecting user to select sequences page")

    # Return the state
    pGetHandler = GetHandler.GetHandler(pCoreServer, pDatabase)
    return pGetHandler.HandleRequest(sClientState, sRemoteUser, "/state", None, 0)

