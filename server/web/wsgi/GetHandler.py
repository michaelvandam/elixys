#!/usr/bin/python

# Imports
import sys
sys.path.append("/opt/elixys/core")
sys.path.append("/opt/elixys/database")
import SequenceManager
import copy
from DBComm import *
from operator import itemgetter
import Exceptions
from CoreServer import InitialRunState
import time

import logging
log = logging.getLogger("elixys.web")


# Function used to sort strings in a case-insensitive manner
def LowerIfPossible(x):
    try:
        return x.lower()
    except AttributeError:
        return x

class GetHandler:
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

        # Initialize server state
        self.__pServerState = None

        # Call the appropriate handler function
        if self.__sPath == "/configuration":
            return self.__HandleGetConfiguration()
        if self.__sPath == "/state":
            return self.__HandleGetState()
        if self.__sPath == "/runstate":
            return self.__HandleGetRunState()
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
            "clientstate":self.__pClientState,
            "timestamp":time.time()}

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

    # Handle GET /runstate request
    def __HandleGetRunState(self):
        # Get the user information and server state
        pUser = self.__pDatabase.GetUser(self.__sRemoteUser, self.__sRemoteUser)
        pServerState = self.__GetServerState()

        # Start the state object
        pState = {"type":"state",
            "user":pUser,
            "serverstate":pServerState,
            "clientstate":copy.deepcopy(self.__pClientState),
            "timestamp":time.time()}

        # Complete with either the run or home states
        if pServerState["runstate"]["running"]:
            pState.update(self.__HandleGetStateRun())
            pState["clientstate"]["screen"] = "RUN"
        else:
            pState.update(self.__HandleGetStateHome())
            pState["clientstate"]["screen"] = "HOME"
            pState["clientstate"]["prompt"]["show"] = False

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
        bSystemAvailable = (pServerState["runstate"]["status"] == "Idle")

        # Determine the sorting modes
        bSortDescending = True
        sSortKey = ""
        sNameSortMode = "none"
        if self.__pClientState["selectsequencesort"]["column"] == "name":
            sSortKey = "name"
            sNameSortMode = self.__pClientState["selectsequencesort"]["mode"]
            if sNameSortMode == "down":
                bSortDescending = False
        sCommentSortMode = "none"
        if self.__pClientState["selectsequencesort"]["column"] == "comment":
            sSortKey = "comment"
            sCommentSortMode = self.__pClientState["selectsequencesort"]["mode"]
            if sCommentSortMode == "down":
                bSortDescending = False

        # Format the buttons, tabs and columns
        pState = {"buttons":[{"type":"button",
            "id":"SEQUENCER",
            "enabled":True,
            "selectionrequired":False},
            {"type":"button",
            "id":"NEWSEQUENCE",
            "enabled":True,
            "selectionrequired":False},
            {"type":"button",
            "id":"COPYSEQUENCE",
            "enabled":True,
            "selectionrequired":True},
            {"type":"button",
            "id":"VIEWSEQUENCE",
            "enabled":True,
            "selectionrequired":True},
            {"type":"button",
            "id":"EDITSEQUENCE",
            "enabled":True,
            "selectionrequired":True},
            {"type":"button",
            "id":"RUNSEQUENCE",
            "enabled":bSystemAvailable,
            "selectionrequired":True},
            {"type":"button",
            "id":"DELETESEQUENCE",
            "enabled":True,
            "selectionrequired":True}],
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
            "sortmode":sNameSortMode},
            {"type":"column",
            "data":"comment",
            "display":"COMMENT",
            "percentwidth":65,
            "sortable":True,
            "sortmode":sCommentSortMode}]}

        # Append the saved sequence list
        pSavedSequences = self.__pDatabase.GetAllSequences(self.__sRemoteUser, "Saved")
        pSavedSequences.sort(key=lambda pSequence: map(LowerIfPossible, pSequence[sSortKey]), reverse=bSortDescending)
        pState.update({"sequences":pSavedSequences})
        return pState

    # Handle GET /state for Select Sequence (Run history tab)
    def __HandleGetStateSelectRunHistory(self):
        # Check if the system is running
        pServerState = self.__GetServerState()
        bSystemAvailable = (pServerState["runstate"]["status"] == "Idle")

        # Determine the sorting modes
        bSortDescending = True
        sSortKey1 = ""
        sSortKey2 = ""
        sNameSortMode = "none"
        if self.__pClientState["runhistorysort"]["column"] == "name":
            sSortKey1 = "name"
            sNameSortMode = self.__pClientState["runhistorysort"]["mode"]
            if sNameSortMode == "down":
                bSortDescending = False
        sCommentSortMode = "none"
        if self.__pClientState["runhistorysort"]["column"] == "comment":
            sSortKey1 = "comment"
            sCommentSortMode = self.__pClientState["runhistorysort"]["mode"]
            if sCommentSortMode == "down":
                bSortDescending = False
        sCreatorSortMode = "none"
        if self.__pClientState["runhistorysort"]["column"] == "creator":
            sSortKey1 = "creator"
            sCreatorSortMode = self.__pClientState["runhistorysort"]["mode"]
            if sCreatorSortMode == "down":
                bSortDescending = False
        sDateTimeSortMode = "none"
        if self.__pClientState["runhistorysort"]["column"] == "date&time":
            sSortKey1 = "date"
            sSortKey2 = "time"
            sDateTimeSortMode = self.__pClientState["runhistorysort"]["mode"]
            if sDateTimeSortMode == "down":
                bSortDescending = False

        # Format the buttons, tabs and columns
        pState = {"buttons":[{"type":"button",
            "id":"SEQUENCER",
            "enabled":True},
            {"type":"button",
            "id":"COPYSEQUENCE",
            "enabled":True,
            "selectionrequired":True},
            {"type":"button",
            "id":"VIEWSEQUENCE",
            "enabled":True,
            "selectionrequired":True},
            {"type":"button",
            "id":"RUNSEQUENCE",
            "enabled":bSystemAvailable,
            "selectionrequired":True},
            {"type":"button",
            "id":"VIEWRUNLOGS",
            "enabled":False,
            "selectionrequired":True},
            {"type":"button",
            "id":"VIEWBATCHRECORD",
            "enabled":False,
            "selectionrequired":True}],
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
            "sortmode":sNameSortMode},
            {"type":"column",
            "data":"comment",
            "display":"COMMENT",
            "percentwidth":40,
            "sortable":True,
            "sortmode":sCommentSortMode},
            {"type":"column",
            "data":"creator",
            "display":"USER",
            "percentwidth":15,
            "sortable":True,
            "sortmode":sCreatorSortMode},
            {"type":"column",
            "data":"date&time",
            "display":"DATE",
            "percentwidth":25,
            "sortable":True,
            "sortmode":sDateTimeSortMode}]}

        # Append the run history list
        pRunHistorySequences = self.__pDatabase.GetAllSequences(self.__sRemoteUser, "History")
        if sSortKey2 == "":
            pRunHistorySequences.sort(key=lambda pSequence: map(LowerIfPossible, pSequence[sSortKey1]), reverse=bSortDescending)
        else:
            pRunHistorySequences.sort(key=lambda pSequence: (map(LowerIfPossible, pSequence[sSortKey1]), map(LowerIfPossible, pSequence[sSortKey2])), reverse=bSortDescending)
        pState.update({"sequences":pRunHistorySequences})
        return pState

    # Handle GET /state for View Sequence
    def __HandleGetStateView(self):
        # Do we have a component ID?
        if self.__pClientState["componentid"] == 0:
            # No, the component ID is missing.  Get the sequence and the ID of the first component
            pSequence = self.__pSequenceManager.GetSequence(self.__sRemoteUser, 
                    self.__pClientState["sequenceid"], False)
            self.__pClientState["componentid"] = pSequence["components"][0]["id"]

            # Save the client state
            self.__pDatabase.UpdateUserClientState(self.__sRemoteUser, 
                    self.__sRemoteUser, self.__pClientState)

        # Allow editing if this is a saved sequence
        pSequenceMetadata = self.__pDatabase.GetSequenceMetadata(self.__sRemoteUser, 
                self.__pClientState["sequenceid"])
        bEditAllowed = (pSequenceMetadata["sequencetype"] == "Saved")

        # Allow running if the system is not in use
        pServerState = self.__GetServerState()
        bRunAllowed = (pServerState["runstate"]["status"] == "Idle")

        # Allow running from here if this is not a cassette
        bRunHereAllowed = False
        if bRunAllowed:
            pComponent = self.__pSequenceManager.GetComponent(self.__sRemoteUser, 
                    self.__pClientState["componentid"], self.__pClientState["sequenceid"])
            bRunHereAllowed = (pComponent["componenttype"] != "CASSETTE")

        # Return the state
        return {"buttons":[{"type":"button",
            "id":"SEQUENCER",
            "enabled":True},
            {"type":"button",
            "id":"EDITSEQUENCE",
            "enabled":bEditAllowed},
            {"type":"button",
            "id":"RUNSEQUENCE",
            "enabled":bRunAllowed},
            {"type":"button",
            "id":"RUNSEQUENCEHERE",
            "enabled":bRunHereAllowed}],
            "sequenceid":self.__pClientState["sequenceid"],
            "componentid":self.__pClientState["componentid"]}

    # Handle GET /state for Edit Sequence
    def __HandleGetStateEdit(self):
        # Do we have a component ID?
        if self.__pClientState["componentid"] == 0:
            # No, the component ID is missing.  Get the sequence and the ID of the first component
            pSequence = self.__pSequenceManager.GetSequence(self.__sRemoteUser, self.__pClientState["sequenceid"], False)
            self.__pClientState["componentid"] = pSequence["components"][0]["id"]

            # Save the client state
            self.__pDatabase.UpdateUserClientState(self.__sRemoteUser, self.__sRemoteUser, self.__pClientState)

        # Allow running if the system is not in use
        pServerState = self.__GetServerState()
        bRunAllowed = (pServerState["runstate"]["status"] == "Idle")

        # Allow running from here if this is not a cassette
        bRunHereAllowed = False
        if bRunAllowed:
            pComponent = self.__pSequenceManager.GetComponent(self.__sRemoteUser, self.__pClientState["componentid"], self.__pClientState["sequenceid"])
            bRunHereAllowed = (pComponent["componenttype"] != "CASSETTE")

        # Return the state
        return {"buttons":[{"type":"button",
            "id":"SEQUENCER",
            "enabled":True},
            {"type":"button",
            "id":"VIEWSEQUENCE",
            "enabled":True},
            {"type":"button",
            "id":"RUNSEQUENCE",
            "enabled":bRunAllowed},
            {"type":"button",
            "id":"RUNSEQUENCEHERE",
            "enabled":bRunHereAllowed}],
            "sequenceid":self.__pClientState["sequenceid"],
            "componentid":self.__pClientState["componentid"]}

    # Handle GET /state for Run Sequence
    def __HandleGetStateRun(self):
        # Sync the client state with the run state
        pServerState = self.__GetServerState()
        if (self.__pClientState["sequenceid"] != pServerState["runstate"]["sequenceid"]) or \
           (self.__pClientState["componentid"] != pServerState["runstate"]["componentid"]) or \
           (self.__pClientState["prompt"]["show"] != pServerState["runstate"]["prompt"]["show"]) or \
           ((self.__pClientState["prompt"].has_key("screen")) and 
            (pServerState["runstate"]["prompt"].has_key("screen")) and \
            (self.__pClientState["prompt"]["screen"] != pServerState["runstate"]["prompt"]["screen"])):
            # Update the sequence and component IDs
            self.__pClientState["sequenceid"] = pServerState["runstate"]["sequenceid"]
            self.__pClientState["componentid"] = pServerState["runstate"]["componentid"]
           
                       # Update the prompt
            self.__pClientState["prompt"] = copy.copy(pServerState["runstate"]["prompt"])

            # Update the client state
            self.__pDatabase.UpdateUserClientState(self.__sRemoteUser, self.__sRemoteUser, self.__pClientState)
        
        #self.__pClientState["reactor1_temp"] = pServerState["hardwarestate"]['reactors']
        
        # Append to the client the reactor temp levels
        for reactor in range(0,3):
            self.__pClientState["reactor" + str(reactor) + "_temp"] = \
                    pServerState["hardwarestate"]["reactors"][reactor]["temperature"]
            #log.error("NONERROR: " + str(pServerState["hardwarestate"]["reactors"][reactor]["temperature"]))


        

        # Determine if we are the user running the system
        if self.__sRemoteUser == pServerState["runstate"]["username"]:
            # Enable or disable buttons
            bSequencerEnabled = False
            bPauseEnabled = False   #not pServerState["runstate"]["runcomplete"]
            bAbortEnabled = not pServerState["runstate"]["runcomplete"]
        else:
            # Enable or disable buttons
            bSequencerEnabled = True
            bPauseEnabled = False
            bAbortEnabled = False

        # Return the state
        return {"buttons":[{"type":"button",
            "id":"SEQUENCER",
            "enabled":bSequencerEnabled},
            {"type":"button",
            "id":"PAUSERUN",
            "enabled":bPauseEnabled},
            {"type":"button",
            "id":"ABORTRUN",
            "enabled":bAbortEnabled},
            {"type":"button",
            "id":"LOGOUT",
            "enabled":True}],
            "sequenceid":self.__pClientState["sequenceid"],
            "componentid":self.__pClientState["componentid"]}

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
                "note":pOldComponent["note"],
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

        # Get the component and verify the sequence ID
        pComponent = self.__pSequenceManager.GetComponent(self.__sRemoteUser, nComponentID, nSequenceID)
        if pComponent["sequenceid"] == nSequenceID:
            return pComponent
        else:
            raise Exceptions.ComponentNotFoundException(nComponentID)

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
            if self.__pServerState == None:
                log.error("GetHandler.__GetServerState() failed, assuming hardware off")
                self.__pServerState = {"type":"serverstate"}
                self.__pServerState["timestamp"] = time.time()
                self.__pServerState["runstate"] = InitialRunState()
                self.__pServerState["runstate"]["status"] = "Offline"
                self.__pServerState["runstate"]["username"] = ""
        return self.__pServerState

