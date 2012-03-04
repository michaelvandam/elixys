#!/usr/bin/python

# Imports
import sys
sys.path.append("/opt/elixys/core")
sys.path.append("/opt/elixys/database")
import SequenceManager
import copy
from DBComm import *

class GetHandler:
    # Constructor
    def __init__(self, pCoreServer, pDatabase):
        # Remember the input references
        self.__pCoreServer = pCoreServer
        self.__pDatabase = pDatabase

        # Create the sequence manager
        self.__pSequenceManager = SequenceManager.SequenceManager(pDatabase)

        # Initialize server state
        self.__pServerState = None

    # Main entry point for handling all GET requests
    def HandleRequest(self, pClientState, sRemoteUser, sPath, pBody, nBodyLength):
        # Remember the request variables
        self.__pClientState = pClientState
        self.__sRemoteUser = sRemoteUser
        self.__sPath = sPath

        # Call the appropriate handler function
        if self.__sPath == "/configuration":
            return self.__HandleGetConfiguration()
        if self.__sPath == "/state":
            return self.__HandleGetState()
        if self.__sPath.startswith("/sequence/"):
            if self.__sPath.find("/component/") != -1:
                return self.__HandleGetComponent()
            elif self.__sPath.find("/reagent/") != -1:
                return self.__HandleGetReagent()
            else:
                return self.__HandleGetSequence()
        else:
            raise Exception("Unknown path: " + self.__sPath)

    # Handle GET /configuration
    def __HandleGetConfiguration(self):
        pConfig = {"type":"configuration"}
        pConfig.update(self.__pDatabase.GetConfiguration(self.__sRemoteUser))
        pConfig.update({"supportedoperations":self.__pDatabase.GetSupportedOperations(self.__sRemoteUser)})
        return pConfig

    # Handle GET /state request
    def __HandleGetState(self):
        # Get the user information and server state
        pUser = self.__pDatabase.GetUser(self.__sRemoteUser, self.__sRemoteUser)
        pServerState = self.__GetServerState()

        # Is the remote user the one that is currently running the system?
        if self.__sRemoteUser == pServerState["runstate"]["username"]:
            # Yes, so make sure the user is on the run screen
            if self.__pClientState["screen"] != "RUN":
                # Update the client state
                self.__pClientState["screen"] = "RUN"
                self.__pDatabase.UpdateUserClientState(self.__sRemoteUser, self.__sRemoteUser, self.__pClientState)

        # Start the state object
        pState = {"type":"state",
            "user":pUser,
            "serverstate":pServerState,
            "clientstate":self.__pClientState}

        # Complete the state with the values specific to this page
        if self.__pClientState["screen"] == "HOME":
            pState.update(self.__HandleGetStateHome())
        elif self.__pClientState["screen"] == "SELECT_SAVEDSEQUENCES":
            pState.update(self.__HandleGetStateSelectSavedSequences())
        elif self.__pClientState["screen"] == "SELECT_RUNHISTORY":
            pState.update(self.__HandleGetStateSelectRunHistory())
        elif self.__pClientState["screen"] == "VIEW":
            pState.update(self.__HandleGetStateView())
        elif self.__pClientState["screen"] == "EDIT":
            pState.update(self.__HandleGetStateEdit())
        elif self.__pClientState["screen"] == "RUN":
            pState.update(self.__HandleGetStateRun())
        else:
            raise Exception("Unknown screen: " + self.__pClientState["screen"])

        # Return the state
        return pState

    # Handles GET /state request for Home
    def __HandleGetStateHome(self):
        # Check if someone running the system
        pServerState = self.__GetServerState()
        bSystemRunning = (pServerState["runstate"]["username"] != "")

        # Return the button array
        return {"buttons":[{"type":"button",
            "id":"SEQUENCER",
            "enabled":True},
            {"type":"button",
            "id":"MYACCOUNT",
            "enabled":False},
            {"type":"button",
            "id":"MANAGEUSERS",
            "enabled":False},
            {"type":"button",
            "id":"VIEWLOGS",
            "enabled":False},
            {"type":"button",
            "id":"VIEWRUN",
            "enabled":bSystemRunning},
            {"type":"button",
            "id":"LOGOUT",
            "enabled":True}]}

    # Handle GET /state for Select Saved Sequence
    def __HandleGetStateSelectSavedSequences(self):
        # Check if the system is running
        pServerState = self.__GetServerState()
        bSystemAvailable = (pServerState["runstate"]["username"] == "")

        # Format the buttons, tabs and columns
        pState = {"buttons":[{"type":"button",
            "id":"SEQUENCER",
            "enabled":True},
            {"type":"button",
            "id":"NEWSEQUENCE",
            "enabled":True},
            {"type":"button",
            "id":"COPYSEQUENCE",
            "enabled":True},
            {"type":"button",
            "id":"VIEWSEQUENCE",
            "enabled":True},
            {"type":"button",
            "id":"EDITSEQUENCE",
            "enabled":True},
            {"type":"button",
            "id":"RUNSEQUENCE",
            "enabled":bSystemAvailable},
            {"type":"button",
            "id":"DELETESEQUENCE",
            "enabled":True}],
            "tabs":[{"type":"tab",
            "text":"SEQUENCE LIST",
            "id":"SAVEDSEQUENCES"},
            {"type":"tab",
            "text":"RUN HISTORY",
            "id":"RUNHISTORY"}],
            "tabid":"SAVEDSEQUENCES",
            "columns":[{"type":"column",
            "data":"name",
            "display":"NAME",
            "percentwidth":35,
            "sortable":True,
            "sortmode":"down"},
            {"type":"column",
            "data":"comment",
            "display":"COMMENT",
            "percentwidth":65,
            "sortable":True,
            "sortmode":"none"}]}

        # Append the saved sequence list
        pSavedSequences = self.__pDatabase.GetAllSequences(self.__sRemoteUser, "Saved")
        pState.update({"sequences":pSavedSequences})
        return pState

    # Handle GET /state for Select Sequence (Run history tab)
    def __HandleGetStateSelectRunHistory(self):
        # Check if the system is running
        pServerState = self.__GetServerState()
        bSystemAvailable = (pServerState["runstate"]["username"] == "")

        # Format the buttons, tabs and columns
        pState = {"buttons":[{"type":"button",
            "id":"SEQUENCER",
            "enabled":True},
            {"type":"button",
            "id":"COPYSEQUENCE",
            "enabled":True},
            {"type":"button",
            "id":"VIEWSEQUENCE",
            "enabled":True},
            {"type":"button",
            "id":"RUNSEQUENCE",
            "enabled":bSystemAvailable},
            {"type":"button",
            "id":"VIEWRUNLOGS",
            "enabled":False},
            {"type":"button",
            "id":"VIEWBATCHRECORD",
            "enabled":False}],
            "tabs":[{"type":"tab",
            "text":"SEQUENCE LIST",
            "id":"SAVEDSEQUENCES"},
            {"type":"tab",
            "text":"RUN HISTORY",
            "id":"RUNHISTORY"}],
            "tabid":"RUNHISTORY",
            "columns":[{"type":"column",
            "data":"name",
            "display":"NAME",
            "percentwidth":20,
            "sortable":True,
            "sortmode":"none"},
            {"type":"column",
            "data":"comment",
            "display":"COMMENT",
            "percentwidth":40,
            "sortable":True,
            "sortmode":"none"},
            {"type":"column",
            "data":"creator",
            "display":"USER",
            "percentwidth":15,
            "sortable":True,
            "sortmode":"none"},
            {"type":"column",
            "data":"date&time",
            "display":"DATE",
            "percentwidth":25,
            "sortable":True,
            "sortmode":"down"}]}

        # Append the run history list
        pRunHistorySequences = self.__pDatabase.GetAllSequences(self.__sRemoteUser, "History")
        pState.update({"sequences":pRunHistorySequences})
        return pState

    # Handle GET /state for View Sequence
    def __HandleGetStateView(self):
        # Do we have a component ID?
        if self.__pClientState["componentid"] == 0:
            # No, the component ID is missing.  Get the sequence and the ID of the first component
            pSequence = self.__pSequenceManager.GetSequence(self.__sRemoteUser, self.__pClientState["sequenceid"], False)
            self.__pClientState["componentid"] = pSequence["components"][0]["id"]

            # Save the client state
            self.__pDatabase.UpdateUserClientState(self.__sRemoteUser, self.__sRemoteUser, self.__pClientState)

        # Start with the common return object
        pState = {"buttons":[{"type":"button",
                "text":"Back",
                "id":"BACK"}],
            "sequenceid":self.__pClientState["sequenceid"],
            "componentid":self.__pClientState["componentid"]}

        # Add the edit button if this is a saved sequence
        pSequenceMetadata = self.__pDatabase.GetSequenceMetadata(self.__sRemoteUser, self.__pClientState["sequenceid"])
        if pSequenceMetadata["sequencetype"] == "Saved":
            pState["buttons"].insert(0, {"type":"button",
                "text":"Edit",
                "id":"EDIT"})
            nInsertionOffset = 1
        else:
            nInsertionOffset = 0

        # Add the run buttons if no one is running the system
        pServerState = self.__GetServerState()
        if pServerState["runstate"]["username"] == "":
            pState["buttons"].insert(nInsertionOffset, {"type":"button",
                "text":"Run",
                "id":"RUN"})
            nInsertionOffset += 1
            pComponent = self.__pSequenceManager.GetComponent(self.__sRemoteUser, self.__pClientState["componentid"], self.__pClientState["sequenceid"])
            if pComponent["componenttype"] != "CASSETTE":
                pState["buttons"].insert(nInsertionOffset, {"type":"button",
                    "text":"Run here",
                    "id":"RUNHERE"})
        return pState

    # Handle GET /state for Edit Sequence
    def __HandleGetStateEdit(self):
        # Do we have a component ID?
        if self.__pClientState["componentid"] == 0:
            # No, the component ID is missing.  Get the sequence and the ID of the first component
            pSequence = self.__pSequenceManager.GetSequence(self.__sRemoteUser, self.__pClientState["sequenceid"], False)
            self.__pClientState["componentid"] = pSequence["components"][0]["id"]

            # Save the client state
            self.__pDatabase.UpdateUserClientState(self.__sRemoteUser, self.__sRemoteUser, self.__pClientState)

        # Start with the common return object
        pState = {"buttons":[{"type":"button",
                "text":"Back",
                "id":"BACK"}],
            "sequenceid":self.__pClientState["sequenceid"],
            "componentid":self.__pClientState["componentid"]}

        # Add the run buttons if no one is running the system
        pServerState = self.__GetServerState()
        if pServerState["runstate"]["username"] == "":
            pState["buttons"].insert(0, {"type":"button",
                "text":"Run",
                "id":"RUN"})
            pComponent = self.__pSequenceManager.GetComponent(self.__sRemoteUser, self.__pClientState["componentid"], self.__pClientState["sequenceid"])
            if pComponent["componenttype"] != "CASSETTE":
                pState["buttons"].insert(1, {"type":"button",
                    "text":"Run here",
                    "id":"RUNHERE"})
        return pState

    # Handle GET /state for Run Sequence
    def __HandleGetStateRun(self):
        # Sync the client state with the run state
        pServerState = self.__GetServerState()
        if (self.__pClientState["sequenceid"] != pServerState["runstate"]["sequenceid"]) or \
           (self.__pClientState["componentid"] != pServerState["runstate"]["componentid"]) or \
           (self.__pClientState["prompt"]["show"] != pServerState["runstate"]["prompt"]["show"]):
            # Update the sequence and component IDs
            self.__pClientState["sequenceid"] = pServerState["runstate"]["sequenceid"]
            self.__pClientState["componentid"] = pServerState["runstate"]["componentid"]

            # Update the prompt if it isn't abort
            if (self.__pClientState["prompt"]["show"] == False) or \
               (self.__pClientState["prompt"].has_key("screen") and self.__pClientState["prompt"]["screen"] != "PROMPT_ABORTSEQUENCERUN"):
                self.__pClientState["prompt"] = copy.copy(pServerState["runstate"]["prompt"])

            # Update the client state
            self.__pDatabase.UpdateUserClientState(self.__sRemoteUser, self.__sRemoteUser, self.__pClientState)

        # Start with the common return object
        pState = {"buttons":[],
            "sequenceid":self.__pClientState["sequenceid"],
            "componentid":self.__pClientState["componentid"]}

        # Add the button depending on the user running the system
        if self.__sRemoteUser == pServerState["runstate"]["username"]:
            if self.__pCoreServer.WillSequencePause(self.__sRemoteUser):
                pState["buttons"].append({"type":"button",
                    "text":"Don't Pause",
                    "id":"CONTINUERUN"})
            elif self.__pCoreServer.IsSequencePaused(self.__sRemoteUser):
                pState["buttons"].append({"type":"button",
                    "text":"Resume Run",
                    "id":"CONTINUERUN"})
            else:
                pState["buttons"].append({"type":"button",
                    "text":"Pause Run",
                    "id":"PAUSERUN"})
            pState["buttons"].append({"type":"button",
                "text":"Abort",
                "id":"ABORT"})
        else:
            pState["buttons"].append({"type":"button",
                "text":"Back",
                "id":"BACK"})

        # Return the state
        return pState

    # Handle GET /sequence/[sequenceid]
    def __HandleGetSequence(self):
        # Extract sequence ID
        pPathComponents = self.__sPath.split("/")
        nSequenceID = int(pPathComponents[2])

        # Load the entire sequence
        pSequence = self.__pSequenceManager.GetSequence(self.__sRemoteUser, nSequenceID, False)

        # Copy a subset of the sequence data
        pNewComponents = []
        for pOldComponent in pSequence["components"]:
            pNewComponent = {"type":"sequencecomponent",
                "name":pOldComponent["name"],
                "id":pOldComponent["id"],
                "componenttype":pOldComponent["componenttype"],
                "validationerror":False}
            if pOldComponent.has_key("validationerror"):
                pNewComponent["validationerror"] = pOldComponent["validationerror"]
            pNewComponents.append(pNewComponent)
        pSequence["components"] = pNewComponents

        # Return cleaned sequence
        return pSequence

    # Handle GET /sequence/[sequenceid]/component/[componentid]
    def __HandleGetComponent(self):
        # Extract sequence and component IDs
        pPathComponents = self.__sPath.split("/")
        nSequenceID = int(pPathComponents[2])
        nComponentID = int(pPathComponents[4])

        # Return the desired component
        return self.__pSequenceManager.GetComponent(self.__sRemoteUser, nComponentID, nSequenceID)

    # Handle GET /sequence/[sequenceid]/reagent/[reagentid1].[reagentID2]...[reagentIDN]
    def __HandleGetReagent(self):
        # Extract sequence and reagent IDs
        pPathComponents = self.__sPath.split("/")
        nSequenceID = int(pPathComponents[2])
        pReagentIDs = pPathComponents[4].split(".")

        # Create and return the reagent array
        pReagents = {}
        pReagents["type"] = "reagents"
        pReagents["reagents"] = []
        for nReagentID in pReagentIDs:
            pReagents["reagents"].append(self.__pSequenceManager.GetReagent(self.__sRemoteUser, int(nReagentID)))
        return pReagents

    # Initializes and/or returns the cached server state
    def __GetServerState(self):
        if self.__pServerState == None:
            self.__pServerState = self.__pCoreServer.GetServerState(self.__sRemoteUser)
        return self.__pServerState

