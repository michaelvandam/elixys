#!/usr/bin/python

# Imports
import json
import GetHandler
import sys
sys.path.append("/opt/elixys/core")
import SequenceManager
import Exceptions
from CoreServer import InitialRunState
import time
from PDFHandler import PDFHandler

import logging
log = logging.getLogger("elixys.web")


# Directs the user to the appropriate select screen (also used by ExceptionHandler.py)
def DirectToLastSelectScreen(pClientState):
    if pClientState["lastselectscreen"] == "SAVED":
        pClientState["screen"] = "SELECT_SAVEDSEQUENCES"
    elif pClientState["lastselectscreen"] == "HISTORY":
        pClientState["screen"] = "SELECT_RUNHISTORY"
    else:
        raise Exception("Invalid last select screen value")

class PostHandler:
    # Constructor
    def __init__(self, pCoreServer, pDatabase):
        # Remember the input references
        self.__pCoreServer = pCoreServer
        self.__pDatabase = pDatabase

        # Create the sequence manager
        self.__pSequenceManager = SequenceManager.SequenceManager(pDatabase)

    # Main entry point for handling all POST requests
    def HandleRequest(self, pClientState, sRemoteUser, sPath, pBody, nBodyLength):
        # Remember the request variables
        self.__pClientState = pClientState
        self.__sRemoteUser = sRemoteUser
        self.__sPath = sPath
        self.__pBody = pBody
        self.__nBodyLength = nBodyLength
        # Initialize server state
        self.__pServerState = None

        # Call the appropriate handler function
        if self.__sPath == "/HOME":
            return self.__HandlePostHome()
        elif self.__sPath == "/SELECT":
            return self.__HandlePostSelect()
        elif self.__sPath == "/VIEW":
            return self.__HandlePostView()
        elif self.__sPath == "/EDIT":
            return self.__HandlePostEdit()
        elif self.__sPath == "/RUN":
            return self.__HandlePostRun()
        elif self.__sPath == "/PROMPT":
            return self.__HandlePostPrompt()
        elif self.__sPath.startswith("/sequence/"):
            if self.__sPath.find("/component/") != -1:
                return self.__HandlePostComponent()
            elif self.__sPath.find("/reagent/") != -1:
                return self.__HandlePostReagent()
            else:
                return self.__HandlePostSequence()
        else:
            raise Exception("Unknown path: " + sPath)

    # Handle POST /HOME
    def __HandlePostHome(self):
        # Make sure we are on the home page
        if self.__pClientState["screen"] != "HOME":
            raise Exceptions.StateMisalignmentException()

        # Parse the JSON string in the body
        pJSON = json.loads(self.__pBody)

        # Check which option the user selected
        sActionType = str(pJSON["action"]["type"])
        sActionTargetID = str(pJSON["action"]["targetid"])
        if sActionType == "BUTTONCLICK":
            if sActionTargetID == "SEQUENCER":
                # Switch states to the last Select Sequence screen
                DirectToLastSelectScreen(self.__pClientState)
                return self.__SaveClientStateAndReturn()
            elif sActionTargetID == "VIEWRUN":
                # Switch to Run Sequence
                pServerState = self.__GetServerState()
                self.__pClientState["screen"] = "RUN"
                self.__pClientState["sequenceid"] = pServerState["runstate"]["sequenceid"]
                self.__pClientState["componentid"] = pServerState["runstate"]["componentid"]
                return self.__SaveClientStateAndReturn()

        # Unhandled use case
        raise Exceptions.StateMisalignmentException()

    # Handle POST /SELECT
    def __HandlePostSelect(self):
        # Make sure we are on Select Sequence
        if not self.__pClientState["screen"].startswith("SELECT"):
            raise Exceptions.StateMisalignmentException()

        # Parse the JSON string in the body
        pJSON = json.loads(self.__pBody)

        # Check which option the user selected
        sActionType = str(pJSON["action"]["type"])
        sActionTargetID = str(pJSON["action"]["targetid"])
        nSequenceID = pJSON["sequenceid"]
        if sActionType == "BUTTONCLICK":
            if sActionTargetID == "SEQUENCER":
                # Switch states to Home
                self.__pClientState["screen"] = "HOME"
                return self.__SaveClientStateAndReturn()
            elif sActionTargetID == "VIEWSEQUENCE":
                # Switch states to View Sequence
                self.__pClientState["screen"] = "VIEW"
                self.__pClientState["sequenceid"] = nSequenceID
                self.__pClientState["componentid"] = 0
                return self.__SaveClientStateAndReturn()
            elif sActionTargetID == "EDITSEQUENCE":
                # Switch states to Edit Sequence
                self.__pClientState["screen"] = "EDIT"
                self.__pClientState["sequenceid"] = nSequenceID
                self.__pClientState["componentid"] = 0
                return self.__SaveClientStateAndReturn()
            elif sActionTargetID == "RUNSEQUENCE":
                # Show the Run Sequence prompt
                return self.__ShowRunSequencePrompt(nSequenceID)
            elif sActionTargetID == "NEWSEQUENCE":
                # Show the Create Sequence prompt
                self.__pClientState["prompt"]["screen"] = "PROMPT_CREATESEQUENCE"
                self.__pClientState["prompt"]["show"] = True
                self.__pClientState["prompt"]["title"] = "NEW SEQUENCE"
                self.__pClientState["prompt"]["text1"] = "SEQUENCE NAME"
                self.__pClientState["prompt"]["edit1"] = True
                self.__pClientState["prompt"]["edit1default"] = ""
                self.__pClientState["prompt"]["edit1validation"] = "type=string; required=true"
                self.__pClientState["prompt"]["text2"] = "SEQUENCE DESCRIPTION"
                self.__pClientState["prompt"]["edit2"] = True
                self.__pClientState["prompt"]["edit2validation"] = "type=string; required=false"
                self.__pClientState["prompt"]["edit2default"] = ""
                self.__pClientState["prompt"]["buttons"] = [{"type":"button",
                    "text":"OK",
                    "id":"OK"},
                    {"type":"button",
                    "text":"CANCEL",
                    "id":"CANCEL"}]
                return self.__SaveClientStateAndReturn()
            elif sActionTargetID == "COPYSEQUENCE":
                # Show the Copy Sequence prompt
                pSequence = self.__pSequenceManager.GetSequence(self.__sRemoteUser, nSequenceID, False)
                self.__pClientState["prompt"]["screen"] = "PROMPT_COPYSEQUENCE"
                self.__pClientState["prompt"]["show"] = True
                self.__pClientState["prompt"]["title"] = "COPY SEQUENCE"
                self.__pClientState["prompt"]["text1"] = "SEQUENCE NAME"
                self.__pClientState["prompt"]["edit1"] = True
                self.__pClientState["prompt"]["edit1default"] = pSequence["metadata"]["name"] + " Copy"
                self.__pClientState["prompt"]["edit1validation"] = "type=string; required=true"
                self.__pClientState["prompt"]["text2"] = "SEQUENCE DESCRIPTION"
                self.__pClientState["prompt"]["edit2"] = True
                self.__pClientState["prompt"]["edit2default"] = pSequence["metadata"]["comment"]
                self.__pClientState["prompt"]["edit2validation"] = "type=string; required=false"
                self.__pClientState["prompt"]["buttons"] = [{"type":"button",
                    "text":"OK",
                    "id":"OK"},
                    {"type":"button",
                    "text":"CANCEL",
                    "id":"CANCEL"}]
                self.__pClientState["sequenceid"] = nSequenceID
                return self.__SaveClientStateAndReturn()
            elif sActionTargetID == "DELETESEQUENCE":
                # Show the Delete Sequence prompt
                pSequence = self.__pSequenceManager.GetSequence(self.__sRemoteUser, nSequenceID, False)
                self.__pClientState["prompt"]["screen"] = "PROMPT_DELETESEQUENCE"
                self.__pClientState["prompt"]["show"] = True
                self.__pClientState["prompt"]["title"] = "DELETE SEQUENCE"
                self.__pClientState["prompt"]["text1"] = "Are you sure that you want to delete the sequence \"" + pSequence["metadata"]["name"] + "\"?"
                self.__pClientState["prompt"]["edit1"] = False
                self.__pClientState["prompt"]["text2"] = ""
                self.__pClientState["prompt"]["edit2"] = False
                self.__pClientState["prompt"]["buttons"] = [{"type":"button",
                    "text":"YES",
                    "id":"YES"},
                    {"type":"button",
                    "text":"NO",
                    "id":"NO"}]
                self.__pClientState["sequenceid"] = nSequenceID
                return self.__SaveClientStateAndReturn()
        elif sActionType == "TABCLICK":
            if sActionTargetID == "SAVEDSEQUENCES":
                # Switch states to the Saved Sequences tab
                self.__pClientState["screen"] = "SELECT_SAVEDSEQUENCES"
                self.__pClientState["lastselectscreen"] = "SAVED"
                self.__pClientState["sequenceid"] = nSequenceID
                return self.__SaveClientStateAndReturn()
            elif sActionTargetID == "RUNHISTORY":
                # Switch states to the Run History tab
                self.__pClientState["screen"] = "SELECT_RUNHISTORY"
                self.__pClientState["lastselectscreen"] = "HISTORY"
                self.__pClientState["sequenceid"] = nSequenceID
                return self.__SaveClientStateAndReturn()
        elif sActionType == "HEADERCLICK":
                if self.__pClientState["screen"] == "SELECT_SAVEDSEQUENCES":
                    # Change the select sequences sort order
                    if sActionTargetID == "name":
                        if self.__pClientState["selectsequencesort"]["column"] == "name":
                            if self.__pClientState["selectsequencesort"]["mode"] == "down":
                                self.__pClientState["selectsequencesort"]["mode"] = "up"
                            else:
                                self.__pClientState["selectsequencesort"]["mode"] = "down"
                        else:
                            self.__pClientState["selectsequencesort"]["column"] = "name"
                            self.__pClientState["selectsequencesort"]["mode"] = "down"
                        return self.__SaveClientStateAndReturn()
                    elif sActionTargetID == "comment":
                        if self.__pClientState["selectsequencesort"]["column"] == "comment":
                            if self.__pClientState["selectsequencesort"]["mode"] == "down":
                                self.__pClientState["selectsequencesort"]["mode"] = "up"
                            else:
                                self.__pClientState["selectsequencesort"]["mode"] = "down"
                        else:
                            self.__pClientState["selectsequencesort"]["column"] = "comment"
                            self.__pClientState["selectsequencesort"]["mode"] = "down"
                        return self.__SaveClientStateAndReturn()
                elif self.__pClientState["screen"] == "SELECT_RUNHISTORY":
                    # Change the run history sort order
                    if sActionTargetID == "name":
                        if self.__pClientState["runhistorysort"]["column"] == "name":
                            if self.__pClientState["runhistorysort"]["mode"] == "down":
                                self.__pClientState["runhistorysort"]["mode"] = "up"
                            else:
                                self.__pClientState["runhistorysort"]["mode"] = "down"
                        else:
                            self.__pClientState["runhistorysort"]["column"] = "name"
                            self.__pClientState["runhistorysort"]["mode"] = "down"
                        return self.__SaveClientStateAndReturn()
                    elif sActionTargetID == "comment":
                        if self.__pClientState["runhistorysort"]["column"] == "comment":
                            if self.__pClientState["runhistorysort"]["mode"] == "down":
                                self.__pClientState["runhistorysort"]["mode"] = "up"
                            else:
                                self.__pClientState["runhistorysort"]["mode"] = "down"
                        else:
                            self.__pClientState["runhistorysort"]["column"] = "comment"
                            self.__pClientState["runhistorysort"]["mode"] = "down"
                        return self.__SaveClientStateAndReturn()
                    elif sActionTargetID == "creator":
                        if self.__pClientState["runhistorysort"]["column"] == "creator":
                            if self.__pClientState["runhistorysort"]["mode"] == "down":
                                self.__pClientState["runhistorysort"]["mode"] = "up"
                            else:
                                self.__pClientState["runhistorysort"]["mode"] = "down"
                        else:
                            self.__pClientState["runhistorysort"]["column"] = "creator"
                            self.__pClientState["runhistorysort"]["mode"] = "down"
                        return self.__SaveClientStateAndReturn()
                    elif sActionTargetID == "date&time":
                        if self.__pClientState["runhistorysort"]["column"] == "date&time":
                            if self.__pClientState["runhistorysort"]["mode"] == "down":
                                self.__pClientState["runhistorysort"]["mode"] = "up"
                            else:
                                self.__pClientState["runhistorysort"]["mode"] = "down"
                        else:
                            self.__pClientState["runhistorysort"]["column"] = "date&time"
                            self.__pClientState["runhistorysort"]["mode"] = "down"
                        return self.__SaveClientStateAndReturn()

        # Unhandled use case
        raise Exceptions.StateMisalignmentException()

    # Show the Run Sequence prompt
    def __ShowRunSequencePrompt(self, nSequenceID):
        # Load the sequence
        pSequence = self.__pSequenceManager.GetSequence(self.__sRemoteUser, nSequenceID, False)

        # Fill in the state
        self.__pClientState["prompt"]["screen"] = "PROMPT_RUNSEQUENCE"
        self.__pClientState["prompt"]["show"] = True
        self.__pClientState["prompt"]["title"] = "RUN SEQUENCE"
        self.__pClientState["prompt"]["text1"] = "Would you like to run the sequence \"" + pSequence["metadata"]["name"] + "\"?"
        self.__pClientState["prompt"]["edit1"] = False
        self.__pClientState["prompt"]["text2"] = ""
        self.__pClientState["prompt"]["edit2"] = False
        self.__pClientState["prompt"]["buttons"] = [{"type":"button",
            "text":"YES",
            "id":"YES"},
            {"type":"button",
            "text":"NO",
            "id":"NO"}]
        self.__pClientState["sequenceid"] = nSequenceID
        return self.__SaveClientStateAndReturn()

    # Show the Run Sequence From Component prompt
    def __ShowRunSequenceFromComponentPrompt(self, nSequenceID, nComponentID):
        # Load the sequence and find the component
        pSequence = self.__pSequenceManager.GetSequence(self.__sRemoteUser, nSequenceID, False)
        pComponent = None
        nIndex = 1
        for pSeqComponent in pSequence["components"]:
             if pSeqComponent["id"] == nComponentID:
                 pComponent = pSeqComponent
                 break
             nIndex += 1
        if pComponent == None:
            raise Exception("Component " + str(nComponentID) + " not found in sequence " + str(nSequenceID))

        # Adjust the component index for the cassettes
        nIndex -= self.__pDatabase.GetConfiguration(self.__sRemoteUser)["reactors"]

        # Fill in the state
        self.__pClientState["prompt"]["screen"] = "PROMPT_RUNSEQUENCEFROMCOMPONENT"
        self.__pClientState["prompt"]["show"] = True
        self.__pClientState["prompt"]["title"] = "RUN SEQUENCE"
        self.__pClientState["prompt"]["text1"] = "Would you like to run the sequence \"" + pSequence["metadata"]["name"] + \
            "\" starting with unit operation number " + str(nIndex) + " (" + pComponent["componenttype"] + ")?"
        self.__pClientState["prompt"]["edit1"] = False
        self.__pClientState["prompt"]["text2"] = ""
        self.__pClientState["prompt"]["edit2"] = False
        self.__pClientState["prompt"]["buttons"] = [{"type":"button",
            "text":"YES",
            "id":"YES"},
            {"type":"button",
            "text":"NO",
            "id":"NO"}]
        self.__pClientState["sequenceid"] = nSequenceID
        return self.__SaveClientStateAndReturn()

    # Handle POST /VIEW
    def __HandlePostView(self):
        # Make sure we are on View Sequence
        if self.__pClientState["screen"] != "VIEW":
            raise Exceptions.StateMisalignmentException()

        # Parse the JSON string in the body and extract the action type and target
        pJSON = json.loads(self.__pBody)
        sActionType = str(pJSON["action"]["type"])
        sActionTargetID = str(pJSON["action"]["targetid"])

        # Call the base sequence POST handler first
        if self.__HandlePostBaseSequence(sActionType, sActionTargetID):
            return self.__SaveClientStateAndReturn()

        # Handle View Sequence specific requests
        if sActionType == "BUTTONCLICK":
            if sActionTargetID == "EDITSEQUENCE":
                # Switch states to Edit Sequence
                self.__pClientState["screen"] = "EDIT"
                return self.__SaveClientStateAndReturn()
            elif sActionTargetID == "RUNSEQUENCE":
                # Show the Run Sequence prompt
                return self.__ShowRunSequencePrompt(self.__pClientState["sequenceid"])
            elif sActionTargetID == "RUNSEQUENCEHERE":
                # Show the Run Sequence From Component prompt
                return self.__ShowRunSequenceFromComponentPrompt(self.__pClientState["sequenceid"], self.__pClientState["componentid"])

        # Unhandled use case
        raise Exceptions.StateMisalignmentException()

    # Handle POST /EDIT
    def __HandlePostEdit(self):
        # Make sure we are on Edit Sequence
        if self.__pClientState["screen"] != "EDIT":
            raise Exceptions.StateMisalignmentException()

        # Parse the JSON string in the body and extract the action type and target
        pJSON = json.loads(self.__pBody)
        sActionType = str(pJSON["action"]["type"])
        sActionTargetID = str(pJSON["action"]["targetid"])

        # Call the base sequence POST handler first
        if self.__HandlePostBaseSequence(sActionType, sActionTargetID):
            return self.__SaveClientStateAndReturn()

        # Handle Edit Sequence specific requests
        if sActionType == "BUTTONCLICK":
            if sActionTargetID == "VIEWSEQUENCE":
                # Switch states to View Sequence
                self.__pClientState["screen"] = "VIEW"
                return self.__SaveClientStateAndReturn()
            elif sActionTargetID == "RUNSEQUENCE":
                # Show the Run Sequence prompt
                return self.__ShowRunSequencePrompt(self.__pClientState["sequenceid"])
            elif sActionTargetID == "RUNSEQUENCEHERE":
                # Show the Run Sequence From Component prompt
                return self.__ShowRunSequenceFromComponentPrompt(self.__pClientState["sequenceid"], self.__pClientState["componentid"])

        # Unhandled use case
        raise Exceptions.StateMisalignmentException()

    # Handle POST /RUN
    def __HandlePostRun(self):
        # Make sure we are on Run Sequence
        if self.__pClientState["screen"] != "RUN":
            raise Exceptions.StateMisalignmentException()

        # Parse the JSON string in the body and extract the action type and target
        pJSON = json.loads(self.__pBody)
        sActionType = str(pJSON["action"]["type"])
        sActionTargetID = str(pJSON["action"]["targetid"])

        # Check which button the user clicked
        if sActionType == "BUTTONCLICK":
            if sActionTargetID == "ABORTRUN":
                # Show the abort confirmation prompt
                self.__pCoreServer.ShowAbortSequencePrompt(self.__sRemoteUser, True)
                return self.__SaveClientStateAndReturn()
            elif sActionTargetID == "SEQUENCER":
                # Switch states to Home
                self.__pClientState["screen"] = "HOME"
                return self.__SaveClientStateAndReturn()
            elif sActionTargetID == "TIMEROVERRIDE":
                # Override the timer
                self.__pCoreServer.OverrideTimer(self.__sRemoteUser)
                return self.__SaveClientStateAndReturn()
            elif sActionTargetID == "TIMERCONTINUE":
                # Stop the timer
                self.__pCoreServer.StopTimer(self.__sRemoteUser)
                return self.__SaveClientStateAndReturn()
            elif sActionTargetID == "USERINPUT":
                # Deliver user input
                self.__pCoreServer.DeliverUserInput(self.__sRemoteUser)
                return self.__SaveClientStateAndReturn()
            elif sActionTargetID == "PAUSERUN":
                # Pause the run
                self.__pCoreServer.PauseSequence(self.__sRemoteUser)
                return self.__SaveClientStateAndReturn()
            elif sActionTargetID == "CONTINUERUN":
                # Continue the run
                self.__pCoreServer.ContinueSequence(self.__sRemoteUser)
                return self.__SaveClientStateAndReturn()
            elif sActionTargetID == "REPORT":
                # Handle PDF Report Generator
                self.__pClientState['pdffilename'] = self.__HandleReport()
                self.__pCoreServer.DeliverUserInput(self.__sRemoteUser)
                return self.__SaveClientStateAndReturn()

        # Unhandled use case
        raise Exceptions.StateMisalignmentException()

    # Handle sequence POST requests
    def __HandlePostBaseSequence(self, sActionType, sActionTargetID):
        # Check which option the user selected
        if sActionType == "BUTTONCLICK":
            if sActionTargetID == "SEQUENCER":
                # Switch states to the last Select Sequence screen
                DirectToLastSelectScreen(self.__pClientState)
                return True
            elif sActionTargetID == "PREVIOUS":
                # Move to the previous component
                pPreviousComponent = self.__pDatabase.GetPreviousComponent(self.__sRemoteUser, self.__pClientState["componentid"])
                if pPreviousComponent != None:
                    self.__pClientState["componentid"] = pPreviousComponent["id"]
                return True
            elif sActionTargetID == "NEXT":
                # Move to the next component
                pNextComponent = self.__pDatabase.GetNextComponent(self.__sRemoteUser, self.__pClientState["componentid"])
                if pNextComponent != None:
                    self.__pClientState["componentid"] = pNextComponent["id"]
                return True
            else:
                # Check if the target ID corresponds to one of our sequence components
                try:
                    # Cast the action target ID to an integer and fetch the corresponding component
                    nActionTargetID = int(sActionTargetID)
                    pComponent = self.__pDatabase.GetComponent(self.__sRemoteUser, nActionTargetID)

                    # Make sure the sequence IDs match
                    if pComponent["sequenceid"] != self.__pClientState["sequenceid"]:
                        return False

                    # Move to the component
                    self.__pClientState["componentid"] = pComponent["id"]
                    return True
                except ValueError:
                    # Action target ID is not an integer
                    pass
                except Exceptions.ComponentNotFoundException:
                    # Interger does not correspond to a component ID
                    pass

        # Tell the caller we didn't handle it
        return False

    # Handle POST /PROMPT
    def __HandlePostPrompt(self):
        # Make sure we are on Prompt
        if not self.__pClientState["prompt"]["show"] or not self.__pClientState["prompt"]["screen"].startswith("PROMPT"):
            raise Exceptions.StateMisalignmentException()

        # Parse the JSON string in the body
        pJSON = json.loads(self.__pBody)

        # Extract the post parameters
        sActionType = str(pJSON["action"]["type"])
        sActionTargetID = str(pJSON["action"]["targetid"])
        sEdit1 = str(pJSON["edit1"])
        sEdit2 = str(pJSON["edit2"])

        # The only recognized action from a prompt is a button click
        if sActionType != "BUTTONCLICK":
            raise Exceptions.StateMisalignmentException()

        # Interpret the response in context of the client state
        if self.__pClientState["prompt"]["screen"] == "PROMPT_CREATESEQUENCE":
            if sActionTargetID == "OK":
                # Sequence name is required
                if sEdit1 == "":
                    raise Exception("Sequence name is required")

                # Create the new sequence
                pConfiguration = self.__pDatabase.GetConfiguration(self.__sRemoteUser)
                nSequenceID = self.__pDatabase.CreateSequence(self.__sRemoteUser, sEdit1, sEdit2, "Saved", pConfiguration["reactors"], pConfiguration["reagentsperreactor"])

                # Hide the prompt and move the client to the editing the new sequence
                self.__pClientState["prompt"]["show"] = False
                self.__pClientState["screen"] = "EDIT"
                self.__pClientState["sequenceid"] = nSequenceID
                return self.__SaveClientStateAndReturn()
            if sActionTargetID == "CANCEL":
                # Hide the prompt
                self.__pClientState["prompt"]["show"] = False
                return self.__SaveClientStateAndReturn()
        elif self.__pClientState["prompt"]["screen"] == "PROMPT_COPYSEQUENCE":
            if sActionTargetID == "OK":
                # Sequence name is required
                if sEdit1 == "":
                    raise Exception("Sequence name is required")

                # Create a copy of the sequence in the database
                nNewSequenceID = self.__pSequenceManager.CopySequence(self.__sRemoteUser, self.__pClientState["sequenceid"], sEdit1, sEdit2)

                # Hide the prompt and move the client to the saved sequences screen
                self.__pClientState["prompt"]["show"] = False
                self.__pClientState["screen"] = "SELECT_SAVEDSEQUENCES"
                self.__pClientState["lastselectscreen"] = "SAVED"
                return self.__SaveClientStateAndReturn()
            if sActionTargetID == "CANCEL":
                # Hide the prompt
                self.__pClientState["prompt"]["show"] = False
                return self.__SaveClientStateAndReturn()
        elif self.__pClientState["prompt"]["screen"] == "PROMPT_DELETESEQUENCE":
            if sActionTargetID == "YES":
                # Delete the sequence from the database
                self.__pDatabase.DeleteSequence(self.__sRemoteUser, self.__pClientState["sequenceid"])

                # Hide the prompt
                self.__pClientState["prompt"]["show"] = False
                return self.__SaveClientStateAndReturn()
            if sActionTargetID == "NO":
                # Hide the prompt
                self.__pClientState["prompt"]["show"] = False
                return self.__SaveClientStateAndReturn()
        elif self.__pClientState["prompt"]["screen"] == "PROMPT_RUNSEQUENCE":
            if sActionTargetID == "YES":
                # Fetch the sequence from the database and make sure it is valid
                pSequence = self.__pSequenceManager.GetSequence(self.__sRemoteUser, self.__pClientState["sequenceid"])
                if not pSequence["metadata"]["valid"]:
                    raise Exceptions.InvalidSequenceException(self.__pClientState["sequenceid"])

                # Run the sequence
                self.__pCoreServer.RunSequence(self.__sRemoteUser, self.__pClientState["sequenceid"])

                # Hide the prompt and switch states to Run Sequence
                self.__pClientState["prompt"]["show"] = False
                self.__pClientState["screen"] = "RUN"
                return self.__SaveClientStateAndReturn()
            if sActionTargetID == "NO":
                # Hide the prompt
                self.__pClientState["prompt"]["show"] = False
                return self.__SaveClientStateAndReturn()
        elif self.__pClientState["prompt"]["screen"] == "PROMPT_RUNSEQUENCEFROMCOMPONENT":
            if sActionTargetID == "YES":
                # Fetch the sequence from the database and make sure it is valid
                pSequence = self.__pSequenceManager.GetSequence(self.__sRemoteUser, self.__pClientState["sequenceid"])
                if not pSequence["metadata"]["valid"]:
                    raise Exceptions.InvalidSequenceException(self.__pClientState["sequenceid"])

                # Run the sequence from the component
                self.__pCoreServer.RunSequenceFromComponent(self.__sRemoteUser, self.__pClientState["sequenceid"], self.__pClientState["componentid"])

                # Hide the prompt and switch states to Run Sequence
                self.__pClientState["prompt"]["show"] = False
                self.__pClientState["screen"] = "RUN"
                return self.__SaveClientStateAndReturn()
            if sActionTargetID == "NO":
                # Hide the prompt
                self.__pClientState["prompt"]["show"] = False
                return self.__SaveClientStateAndReturn()
        elif self.__pClientState["prompt"]["screen"] == "PROMPT_UNITOPERATION":
            # Currently unused
            return self.__SaveClientStateAndReturn()
        elif self.__pClientState["prompt"]["screen"] == "PROMPT_SOFTERROR":
            # Pass the user's decision to the core server
            self.__pCoreServer.SetSoftErrorDecision(self.__sRemoteUser, sActionTargetID)
        elif self.__pClientState["prompt"]["screen"] == "PROMPT_ABORTRUN":
            if sActionTargetID == "YES":
                # Abort the run and return to the home page
                self.__pCoreServer.AbortSequence(self.__sRemoteUser)
                self.__pClientState["prompt"]["show"] = False
                self.__pClientState["screen"] = "HOME"
                return self.__SaveClientStateAndReturn()
            if sActionTargetID == "NO":
                # Hide the prompt
                self.__pCoreServer.ShowAbortSequencePrompt(self.__sRemoteUser, False)
                return self.__SaveClientStateAndReturn()
        # Unhandled use case
        raise Exceptions.StateMisalignmentException()

    # Handle POST /sequence/[sequenceid]
    def __HandlePostSequence(self):
        raise Exception("Implement post sequence")
        # There currently isn't any way in the UI to edit the sequence metadata

    # Handle POST /sequence/[sequenceid]/component/[componentid]
    def __HandlePostComponent(self):
        # Extract sequence and component IDs
        pPathComponents = self.__sPath.split("/")
        nSequenceID = int(pPathComponents[2])
        nComponentID = int(pPathComponents[4])
        nInsertionID = None
        if len(pPathComponents) == 6:
            nInsertionID = int(pPathComponents[5])

        # Make sure we can edit this sequence
        pSequenceMetadata = self.__pDatabase.GetSequenceMetadata(self.__sRemoteUser, nSequenceID)
        if pSequenceMetadata["sequencetype"] != "Saved":
            raise Exception("Cannot edit sequence")

        # Parse the component JSON if present
        pComponent = None
        if self.__nBodyLength != 0:
            pComponent = json.loads(self.__pBody)

        # Are we working with an existing component?
        if nComponentID != 0:
            # Yes, so update the existing component
            self.__pSequenceManager.UpdateComponent(self.__sRemoteUser, nSequenceID, nComponentID, nInsertionID, pComponent)
        else:
            # No, so add a new component
            nComponentID = self.__pSequenceManager.AddComponent(self.__sRemoteUser, nSequenceID, nInsertionID, pComponent)

            # Update the client to show the new component
            self.__pClientState["componentid"] = nComponentID

        # Return the new state
        return self.__SaveClientStateAndReturn()

    # Handle POST /sequence/[sequenceid]/reagent/[reagentid]
    def __HandlePostReagent(self):
        # Extract sequence and reagent IDs
        pPathComponents = self.__sPath.split("/")
        nSequenceID = int(pPathComponents[2])
        nReagentID = int(pPathComponents[4])

        # Make sure we can edit this sequence
        pSequenceMetadata = self.__pDatabase.GetSequenceMetadata(self.__sRemoteUser, nSequenceID)
        if pSequenceMetadata["sequencetype"] != "Saved":
            raise Exception("Cannot edit sequence")

        # Save the reagent
        pReagent = json.loads(self.__pBody)
        self.__pDatabase.UpdateReagent(self.__sRemoteUser, nReagentID, pReagent["name"], pReagent["description"])

        # Flag the sequence validation as dirty
        self.__pDatabase.UpdateSequenceDirtyFlag(self.__sRemoteUser, nSequenceID, True)

        # Return the new state
        return self.__SaveClientStateAndReturn()
    
    # Handles the PFD Report Generator.
    # Added by: Luis    
    def __HandleReport(self):
        ''' Get the sequences and their components. They will be added to the PDF.
        Function (getSequences) will return a filename that will be appended onto the server state
        '''
        pdffile = PDFHandler()
        filename = pdffile.write_pdf(self.__pClientState, self.__sRemoteUser, self.__pDatabase)
        return filename
        
    # Save the client state and return
    def __SaveClientStateAndReturn(self):
        self.__pDatabase.UpdateUserClientState(self.__sRemoteUser, self.__sRemoteUser, self.__pClientState)
        pGetHandler = GetHandler.GetHandler(self.__pCoreServer, self.__pDatabase)
        return pGetHandler.HandleRequest(self.__pClientState, self.__sRemoteUser, "/state", None, 0)

    # Initializes and/or returns the cached server state
    def __GetServerState(self):
        if self.__pServerState == None:
            self.__pServerState = self.__pCoreServer.GetServerState(self.__sRemoteUser)
            if self.__pServerState == None:
                log.error("PostHandler.__GetServerState() failed, assuming hardware off")
                self.__pServerState = {"type":"serverstate"}
                self.__pServerState["timestamp"] = time.time()
                self.__pServerState["runstate"] = InitialRunState()
                self.__pServerState["runstate"]["status"] = "Offline"
                self.__pServerState["runstate"]["username"] = ""
        return self.__pServerState

