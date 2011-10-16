#!/usr/bin/python

# Imports
import sys
sys.path.append("/opt/elixys/core")
import SequenceManager

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
    def HandleRequest(self, sClientState, sRemoteUser, sPath, pBody, nBodyLength):
        # Remember the request variables
        self.__sClientState = sClientState
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
        # Is the remote user the one that is currently running the system?
        pServerState = self.__GetServerState()
        if self.__sRemoteUser == pServerState["runstate"]["username"]:
            # Yes, so make sure the user is in the appropriate run state
            raise Exception("User is running system, make sure they are in the right place")
            sRunState = self.__pCoreServer.GetRunState(self.__sRemoteUser)
            if sRunState.startswith("RUNSEQUENCE") and not self.__sClientState.startswith("RUNSEQUENCE") and not self.__sClientState.startswith("PROMPT"):
                pRunStateComponents = sRunState.split(".")
                self.__sClientState = "RUNSEQUENCE." + pRunStateComponents[1] + "." + pRunStateComponents[2]
                self.__pDatabase.UpdateUserClientState(self.__sRemoteUser, self.__sRemoteUser, self.__sClientState)

        # Get the user information
        pUser = self.__pDatabase.GetUser(self.__sRemoteUser, self.__sRemoteUser)

        # Get the full client state and break it into prompt and client components
        pPromptStateComponent = self.__GetPromptStateComponent()
        sClientStateComponent = self.__GetClientStateComponent()

        # Start the state with the common fields
        pState = {"type":"state",
            "user":pUser,
            "serverstate":pServerState,
            "promptstate":pPromptStateComponent,
            "clientstate":sClientStateComponent}

        # Complete the state with the values specific to this page
        if sClientStateComponent.startswith("HOME"):
            pState.update(self.__HandleGetStateHome())
        elif sClientStateComponent.startswith("SELECT_SAVEDSEQUENCES"):
            pState.update(self.__HandleGetStateSelectSavedSequences())
        elif sClientStateComponent.startswith("SELECT_RUNHISTORY"):
            pState.update(self.__HandleGetStateSelectRunHistory())
        elif sClientStateComponent.startswith("VIEW"):
            pState.update(self.__HandleGetStateView())
        elif sClientStateComponent.startswith("EDIT"):
            pState.update(self.__HandleGetStateEdit())
        elif sClientStateComponent.startswith("RUNSEQUENCE"):
            pState.update(self.__HandleGetStateRunSequence())
        else:
            raise Exception("Unknown state: " + sClientStateComponent)

        # Return the state
        return pState

    # Returns the prompt state component from the full client state
    def __GetPromptStateComponent(self):
        # Initialize the response
        pPromptState = {"type":"promptstate",
            "title":"",
            "show":False,
            "text1":"",
            "edit1":False,
            "edit1validation":"",
            "text2":"",
            "edit2":False,
            "edit2validation":"",
            "buttons":[]}

        # Return if we are not in prompt mode
        if not self.__sClientState.startswith("PROMPT_"):
            return pPromptState

        # Fill in the prompt state with prompt-specific details
        if self.__sClientState.startswith("PROMPT_CREATESEQUENCE"):
            return self.__HandleGetStateSelectPromptCreateSequence(pPromptState)
        elif self.__sClientState.startswith("PROMPT_COPYSEQUENCE"):
            return self.__HandleGetStateSelectPromptCopySequence(pPromptState)
        elif self.__sClientState.startswith("PROMPT_DELETESEQUENCE"):
            return self.__HandleGetStateSelectPromptDeleteSequence(pPromptState)
        elif self.__sClientState.startswith("PROMPT_RUNSEQUENCE"):
            return self.__HandleGetStatePromptRunSequence(pPromptState)
        elif self.__sClientState.startswith("PROMPT_ABORTSEQUENCERUN"):
            return self.__HandleGetStateRunSequencePromptAbort(pPromptState)
        elif self.__sClientState.startswith("PROMPT_UNITOPERATION"):
            return self.__HandleGetStateRunSequencePromptUnitOperation(pPromptState)
        else:
            raise Exception("Unknown prompt state")

    # Returns the client state component of the full client state
    def __GetClientStateComponent(self):
        # Are we in prompt mode?
        if self.__sClientState.startswith("PROMPT_"):
            # Yes, so the client state is the last component delimited by a semicolon
            pClientStateComponents = self.__sClientState.split(";")
            return pClientStateComponents[len(pClientStateComponents) - 1]
        else:
            # No, so return the client state as it is
            return self.__sClientState

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

    # Handle GET /state for View Sequence
    def __HandleGetStateView(self):
        # Split the state and extract the sequence ID
        pClientStateComponents = self.__sClientState.split(".")
        nSequenceID = int(pClientStateComponents[1])

        # Do we have a component ID?
        if (len(pClientStateComponents) > 2):
            # Yes, so extract it
            nComponentID = int(pClientStateComponents[2])
        else:
            # No, the component ID is missing.  Get the sequence and the ID of the first component
            pSequence = self.__pSequenceManager.GetSequence(self.__sRemoteUser, nSequenceID, False)
            nComponentID = pSequence["components"][0]["id"]

            # Update our state
            self.__sClientState = "VIEW." + str(nSequenceID) + "." + str(nComponentID)
            self.__pDatabase.UpdateUserClientState(self.__sRemoteUser, self.__sRemoteUser, self.__sClientState)

        # Start with the common return object
        pState = {"navigationbuttons":[{"type":"button",
                "text":"Edit",
                "id":"EDIT"},
                {"type":"button",
                "text":"Back",
                "id":"BACK"}],
            "sequenceid":nSequenceID,
            "componentid":nComponentID}

        # Add the run button if no one is running the system
        pServerState = self.__GetServerState()
        if pServerState["runstate"]["username"] == "":
            pState["navigationbuttons"].insert(1, {"type":"button",
                "text":"Run",
                "id":"RUN"})
        return pState

    # Handle GET /state for Edit Sequence
    def __HandleGetStateEdit(self):
        # Split the state and extract the sequence ID
        pClientStateComponents = self.__sClientState.split(".")
        nSequenceID = int(pClientStateComponents[1])

        # Do we have a component ID?
        if (len(pClientStateComponents) > 2):
            # Yes, so extract it
            nComponentID = int(pClientStateComponents[2])
        else:
            # No, the component ID is missing.  Get the sequence and the ID of the first component
            pSequence = self.__pSequenceManager.GetSequence(self.__sRemoteUser, nSequenceID, False)
            nComponentID = pSequence["components"][0]["id"]

            # Update our state
            self.__sClientState = "EDIT." + str(nSequenceID) + "." + str(nComponentID)
            self.__pDatabase.UpdateUserClientState(self.__sRemoteUser, self.__sRemoteUser, self.__sClientState)

        # Start with the common return object
        pState = {"navigationbuttons":[{"type":"button",
                "text":"Back",
                "id":"BACK"}],
            "sequenceid":nSequenceID,
            "componentid":nComponentID}

        # Add the run button if no one is running the system
        pServerState = self.__GetServerState()
        if pServerState["runstate"]["username"] == "":
            pState["navigationbuttons"].insert(0, {"type":"button",
                "text":"Run",
                "id":"RUN"})
        return pState

    # Handle GET /state for Run Sequence
    def __HandleGetStateRunSequence(self):
        # Get the server state
        pServerState = self.__GetServerState()

        # Create the return object
        pState = {"navigationbuttons":[],
            "sequenceid":pServerState["runstate"]["sequenceid"],
            "componentid":pServerState["runstate"]["componentid"]}

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

    # Handle GET /state for Select Sequence (Create Sequence prompt)
    def __HandleGetStateSelectPromptCreateSequence(self, pPromptState):
        pPromptState["show"] = True
        pPromptState["title"] = "Create new sequence"
        pPromptState["text1"] = "Enter the name of the new sequence:"
        pPromptState["edit1"] = True
        pPromptState["edit1validation"] = "type=string; required=true"
        pPromptState["text2"] = "Enter optional sequence description:"
        pPromptState["edit2"] = True
        pPromptState["edit2validation"] = "type=string; required=false"
        pPromptState["buttons"].append({"type":"button",
            "text":"Cancel",
            "id":"CANCEL"})
        pPromptState["buttons"].append({"type":"button",
            "text":"Create",
            "id":"CREATE"})
        return pPromptState

    # Handle GET /state for Select Sequence (Copy Sequence prompt)
    def __HandleGetStateSelectPromptCopySequence(self, pPromptState):
        # Look up the sequence
        nSequenceID = int(self.__sClientState.split(";")[0].split("_")[2])
        pSequence = self.__pSequenceManager.GetSequence(self.__sRemoteUser, nSequenceID, False)

        # Create the prompt state
        pPromptState["show"] = True
        pPromptState["title"] = "Copy sequence"
        pPromptState["text1"] = "Enter the name of the new sequence:"
        pPromptState["edit1"] = True
        pPromptState["edit1default"] = pSequence["metadata"]["name"] + " Copy"
        pPromptState["edit1validation"] = "type=string; required=true"
        pPromptState["text2"] = "Enter an optional description of the new sequence:"
        pPromptState["edit2"] = True
        pPromptState["edit2default"] = pSequence["metadata"]["comment"]
        pPromptState["edit2validation"] = "type=string; required=false"
        pPromptState["buttons"].append({"type":"button",
            "text":"Cancel",
            "id":"CANCEL"})
        pPromptState["buttons"].append({"type":"button",
            "text":"Copy",
            "id":"COPY"})
        return pPromptState

    # Handle GET /state for Select Sequence (Delete Sequence prompt)
    def __HandleGetStateSelectPromptDeleteSequence(self, pPromptState):
        # Look up the sequence
        nSequenceID = int(self.__sClientState.split(";")[0].split("_")[2])
        pSequence = self.__pSequenceManager.GetSequence(self.__sRemoteUser, nSequenceID, False)

        # Create the prompt state
        pPromptState["show"] = True
        pPromptState["title"] = "Delete sequence"
        pPromptState["text1"] = "Are you sure that you want to permanently delete sequence \"" + pSequence["metadata"]["name"] + "\"?"
        pPromptState["buttons"].append({"type":"button",
            "text":"Cancel",
            "id":"CANCEL"})
        pPromptState["buttons"].append({"type":"button",
            "text":"Delete",
            "id":"DELETE"})
        return pPromptState

    # Handle GET /state for Run Sequence prompt
    def __HandleGetStatePromptRunSequence(self, pPromptState):
        pPromptState["show"] = True
        pPromptState["title"] = "Run sequence"
        pPromptState["text1"] = "Prepare the Elixys system to run \"Fake Sequence Name Here\" and click OK to continue."
        pPromptState["buttons"].append({"type":"button",
            "text":"Cancel",
            "id":"CANCEL"})
        pPromptState["buttons"].append({"type":"button",
            "text":"OK",
            "id":"OK"})
        return pPromptState

    # Handle GET /state for Run Sequence (Abort prompt)
    def __HandleGetStateRunSequencePromptAbort(self, pPromptState):
        pPromptState["show"] = True
        pPromptState["title"] = "Abort run"
        pPromptState["text1"] = "Are you sure you want to abort the sequence run?  This operation cannot be undone."
        pPromptState["buttons"].append({"type":"button",
            "text":"Cancel",
            "id":"CANCEL"})
        pPromptState["buttons"].append({"type":"button",
            "text":"Abort",
            "id":"ABORT"})
        return pPromptState

    # Handle GET /state for Run Sequence (Prompt/install unit operations)
    def __HandleGetStateRunSequencePromptUnitOperation(self, pPromptState):
        # Look up the current sequence component
        pServerState = self.__GetServerState()
        pComponent = self.__pSequenceManager.GetComponent(self.__sRemoteUser, pServerState["runstate"]["componentid"], pServerState["runstate"]["sequenceid"])

        # Make sure this component requires a prompt
        if (pComponent["componenttype"] != "PROMPT") and (pComponent["componenttype"] != "INSTALL"):
            # No, so update the client state and return
            raise Exception("Shouldn't be at prompt")
            self.__sClientState = self.__pCoreServer.GetRunState(self.__sRemoteUser)
            self.__pDatabase.UpdateUserClientState(self.__sRemoteUser, self.__sRemoteUser, self.__sClientState)
            return pPromptState

        # Set the prompt message
        pPromptState["show"] = True
        pPromptState["title"] = "Prompt"
        pPromptState["text1"] = pComponent["message"]

        # Set the button text depending on whether we are the user running the system
        if self.__sRemoteUser == pServerState["runstate"]["username"]:
            pPromptState["buttons"].append({"type":"button",
                "text":"OK",
                "id":"OK"})
        else:
            pPromptState["buttons"].append({"type":"button",
                "text":"Back",
                "id":"BACK"})

        # Return the state
        return pPromptState

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
                "validationerror":pOldComponent["validationerror"]}
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

