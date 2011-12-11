#!/usr/bin/python

# Imports
import sys
sys.path.append("/opt/elixys/core")
import SequenceManager
import copy

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
        # Start with the common buttons
        pState = {"buttons":[{"type":"button",
            "text":"Create, view or run a sequence",
            "id":"CREATE"}]}

        # Is someone running the system?
        pServerState = self.__GetServerState()
        if pServerState["runstate"]["username"] != "":
            # Yes, so add the observe button
            pState["buttons"].append({"type":"button",
               "text":"Observe the current run by " + pServerState["runstate"]["username"],
                "id":"OBSERVE"})

        # Return the state
        return pState

    # Handle GET /state for Select Sequence (Saved Sequences tab)
    def __HandleGetStateSelectSavedSequences(self):
        pState = self.__HandleGetStateSelect()
        pState.update({"tabid":"SAVEDSEQUENCES"})
        pState["optionbuttons"].append({"type":"button",
            "text":"Edit",
            "id":"EDIT"})
        pState["optionbuttons"].append({"type":"button",
            "text":"Delete",
            "id":"DELETE"})
        pState.update({"sequences":self.__pDatabase.GetAllSequences(self.__sRemoteUser, "Saved")})
        return pState

    # Handle GET /state for Select Sequence (Run history tab)
    def __HandleGetStateSelectRunHistory(self):
        pState = self.__HandleGetStateSelect()
        pState.update({"tabid":"RUNHISTORY"})
        pState.update({"sequences":self.__pDatabase.GetAllSequences(self.__sRemoteUser, "History")})
        return pState

    # Handles GET /state for Select Sequence (both tabs)
    def __HandleGetStateSelect(self):
        # Start with the common state
        pState = {"tabs":[{"type":"tab",
                "text":"Saved Sequences",
                "id":"SAVEDSEQUENCES",
                "columns":["name:Name", "comment:Comment"]},
                {"type":"tab",
                "text":"Run History",
                "id":"RUNHISTORY",
                "columns":["date:Date", "creator:User", "name:Name", "comment:Comment"]}],
            "optionbuttons":[{"type":"button",
                "text":"View",
                "id":"VIEW"},
                {"type":"button",
                "text":"Copy",
                "id":"COPY"}],
            "navigationbuttons":[{"type":"button",
                "text":"Create",
                "id":"CREATE"},
                {"type":"button",
                "text":"Back",
                "id":"BACK"}]}

        # Add the run button if no one is running the system
        pServerState = self.__GetServerState()
        if pServerState["runstate"]["username"] == "":
            pState["optionbuttons"].insert(1, {"type":"button",
                "text":"Run",
                "id":"RUN"})
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
        pState = {"navigationbuttons":[{"type":"button",
                "text":"Edit",
                "id":"EDIT"},
                {"type":"button",
                "text":"Back",
                "id":"BACK"}],
            "sequenceid":self.__pClientState["sequenceid"],
            "componentid":self.__pClientState["componentid"]}

        # Add the run button if no one is running the system
        pServerState = self.__GetServerState()
        if pServerState["runstate"]["username"] == "":
            pState["navigationbuttons"].insert(1, {"type":"button",
                "text":"Run",
                "id":"RUN"})
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
        pState = {"navigationbuttons":[{"type":"button",
                "text":"Back",
                "id":"BACK"}],
            "sequenceid":self.__pClientState["sequenceid"],
            "componentid":self.__pClientState["componentid"]}

        # Add the run button if no one is running the system
        pServerState = self.__GetServerState()
        if pServerState["runstate"]["username"] == "":
            pState["navigationbuttons"].insert(0, {"type":"button",
                "text":"Run",
                "id":"RUN"})
        return pState

    # Handle GET /state for Run Sequence
    def __HandleGetStateRun(self):
        # Sync the client state with the run state
        pServerState = self.__GetServerState()
        if (self.__pClientState["sequenceid"] != pServerState["runstate"]["sequenceid"]) or \
           (self.__pClientState["componentid"] != pServerState["runstate"]["componentid"]) or \
           (self.__pClientState["prompt"]["show"] != pServerState["runstate"]["prompt"]["show"]):
            # Update the client state
            self.__pClientState["sequenceid"] = pServerState["runstate"]["sequenceid"]
            self.__pClientState["componentid"] = pServerState["runstate"]["componentid"]
            self.__pClientState["prompt"] = copy.copy(pServerState["runstate"]["prompt"])
            self.__pDatabase.UpdateUserClientState(self.__sRemoteUser, self.__sRemoteUser, self.__pClientState)

        # Start with the common return object
        pState = {"navigationbuttons":[],
            "sequenceid":self.__pClientState["sequenceid"],
            "componentid":self.__pClientState["componentid"]}

        # Add the button depending on the user running the system
        if self.__sRemoteUser == pServerState["runstate"]["username"]:
            pState["navigationbuttons"].append({"type":"button",
                "text":"Abort",
                "id":"ABORT"})
        else:
            pState["navigationbuttons"].append({"type":"button",
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

