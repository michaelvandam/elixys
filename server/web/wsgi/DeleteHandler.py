#!/usr/bin/python

import sys
sys.path.append("/opt/elixys/core")
import SequenceManager
import GetHandler

class DeleteHandler:
    # Constructor
    def __init__(self, pCoreServer, pDatabase):
        # Remember the input references
        self.__pCoreServer = pCoreServer
        self.__pDatabase = pDatabase

        # Create the sequence manager
        self.__pSequenceManager = SequenceManager.SequenceManager(pDatabase)

    # Main entry point for handling all GET requests
    def HandleRequest(self, pClientState, sRemoteUser, sPath, pBody, nBodyLength):
        # Remember the request variables
        self.__pClientState = pClientState
        self.__sRemoteUser = sRemoteUser
        self.__sPath = sPath

        # Call the appropriate handler function
        if sPath.startswith("/sequence/"):
            if sPath.find("/component/") != -1:
                return self.__HandleDeleteComponent()

        # Unhandled use case
        raise Exception("Unknown path: " + sPath)

    # Handle DELETE /sequence/[sequenceid]/component/[componentid]
    def __HandleDeleteComponent(self):
        # Extract sequence and component IDs
        pPathComponents = self.__sPath.split("/")
        nSequenceID = int(pPathComponents[2])
        nComponentID = int(pPathComponents[4])

        # Is the user currently viewing this component?
        if (self.__pClientState["sequenceid"] == nSequenceID) and (self.__pClientState["componentid"] == nComponentID):
            # Yes, so move the user to the previous component in the sequence
            pPreviousComponent = self.__pDatabase.GetPreviousComponent(self.__sRemoteUser, nComponentID)
            if pPreviousComponent == None:
                raise Exception("Failed to find previous component")

            # Update the client state
            self.__pClientState["componentid"] = pPreviousComponent["id"]
            self.__pDatabase.UpdateUserClientState(self.__sRemoteUser, self.__sRemoteUser, self.__pClientState)

        # Delete the sequence component
        self.__pSequenceManager.DeleteComponent(self.__sRemoteUser, nSequenceID, nComponentID)

        # Return the state
        pGetHandler = GetHandler.GetHandler(self.__pCoreServer, self.__pDatabase)
        return pGetHandler.HandleRequest(self.__pClientState, self.__sRemoteUser, "/state", None, 0)

