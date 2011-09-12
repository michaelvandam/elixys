#!/usr/bin/python

# Imports
import json
import Utilities
import GetHandler

class PostHandler:
    # Constructor
    def __init__(self, pCoreServer, pDatabase, pLog):
        # Remember the input references
        self.__pCoreServer = pCoreServer
        self.__pDatabase = pDatabase
        self.__pLog = pLog

        # Create the utilities object
        self.__pUtilities = Utilities.Utilities(pCoreServer, pDatabase, pLog)

    # Main entry point for handling all POST requests
    def HandleRequest(self, sClientState, sRemoteUser, sPath, pBody, nBodyLength):
        # Remember the request variables
        self.__sClientState = sClientState
        self.__sRemoteUser = sRemoteUser
        self.__sPath = sPath
        self.__pBody = pBody
        self.__nBodyLength = nBodyLength

        # Call the appropriate handler function
        if self.__sPath == "/HOME":
            return self.__HandlePostHome()
        elif self.__sPath == "/SELECT":
            return self.__HandlePostSelect()
        elif self.__sPath == "/VIEW":
            return self.__HandlePostView()
        elif self.__sPath == "/EDIT":
            return self.__HandlePostEdit()
        elif self.__sPath == "/RUNSEQUENCE":
            return self.__HandlePostRunSequence()
        elif self.__sPath == "/MANUALRUN":
            return self.__HandlePostManualRun()
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
        if self.__sClientState.startswith("HOME") == False:
            raise Exception("State misalignment");

        # Parse the JSON string in the body
        pJSON = json.loads(self.__pBody)

        # Check which option the user selected
        sActionType = str(pJSON["action"]["type"])
        sActionTargetID = str(pJSON["action"]["targetid"])
        if sActionType == "BUTTONCLICK":
            if sActionTargetID == "CREATE":
                # Switch states to Select Sequence
                return self.__UpdateClientState("SELECT_SAVEDSEQUENCES")
            elif sActionTargetID == "MANUAL":
                # Switch states to Prompt (Manual Run)
                return self.__UpdateClientState("PROMPT_MANUALRUN;" + self.__sClientState)
            elif sActionTargetID == "OBSERVE":
                # Swtich to Run Sequence
                return self.__UpdateClientState(self.__pCoreServer.GetRunState(self.__sRemoteUser))

        # Unhandled use case
        raise Exception("State misalignment")

    # Handle POST /SELECT
    def __HandlePostSelect(self):
        # Make sure we are on Select Sequence
        if self.__sClientState.startswith("SELECT") == False:
            raise Exception("State misalignment");

        # Parse the JSON string in the body
        pJSON = json.loads(self.__pBody)

        # Check which option the user selected
        sActionType = str(pJSON["action"]["type"])
        sActionTargetID = str(pJSON["action"]["targetid"])
        nSequenceID = pJSON["sequenceid"]
        if sActionType == "BUTTONCLICK":
            if sActionTargetID == "VIEW":
                # Switch states to View Sequence
                return self.__UpdateClientState("VIEW." + str(nSequenceID))
            elif sActionTargetID == "EDIT":
                # Switch states to Edit Sequence
                return self.__UpdateClientState("EDIT." + str(nSequenceID))
            elif sActionTargetID == "RUN":
                # Switch states to Prompt (Run Sequence)
                return self.__UpdateClientState("PROMPT_RUNSEQUENCE;" + str(nSequenceID) + ";" + self.__sClientState)
            elif sActionTargetID == "BACK":
                # Switch states to Home
                return self.__UpdateClientState("HOME")
            elif sActionTargetID == "CREATE":
                # Switch states to Prompt (Create Sequence)
                return self.__UpdateClientState("PROMPT_CREATESEQUENCE;" + self.__sClientState)
            elif sActionTargetID == "COPY":
                # Switch states to Prompt (Copy Sequence)
                return self.__UpdateClientState("PROMPT_COPYSEQUENCE_" + str(nSequenceID) + ";" + self.__sClientState)
            elif sActionTargetID == "DELETE":
                # Switch states to Prompt (Delete Sequence)
                return self.__UpdateClientState("PROMPT_DELETESEQUENCE_" + str(nSequenceID) + ";" + self.__sClientState)
        elif sActionType == "TABCLICK":
            if sActionTargetID == "SAVEDSEQUENCES":
                # Switch states to the Saved Sequences tab
                return self.__UpdateClientState("SELECT_SAVEDSEQUENCES")
            elif sActionTargetID == "MANUALRUNS":
                # Switch states to the Manual Runs tab
                return self.__UpdateClientState("SELECT_MANUALRUNS")

        # Unhandled use case
        raise Exception("State misalignment")

    # Handle POST /VIEW
    def __HandlePostView(self):
        # Make sure we are on View Sequence
        if self.__sClientState.startswith("VIEW") == False:
            raise Exception("State misalignment")

        # Determine our sequence and component IDs
        pClientStateComponents = self.__sClientState.split(".")
        nSequenceID = int(pClientStateComponents[1])
        nComponentID = int(pClientStateComponents[2])

        # Parse the JSON string in the body and extract the action type and target
        pJSON = json.loads(self.__pBody)
        sActionType = str(pJSON["action"]["type"])
        sActionTargetID = str(pJSON["action"]["targetid"])

        # Call the base sequence POST handler first
        sNewClientState = self.__HandlePostBaseSequence("VIEW", nSequenceID, nComponentID, sActionType, sActionTargetID)
        if sNewClientState != "":
            # POST handled
            return self.__UpdateClientState(sNewClientState)

        # Handle View Sequence specific requests
        if sActionType == "BUTTONCLICK":
            if sActionTargetID == "EDIT":
                # Switch states to Edit Sequence
                return self.__UpdateClientState("EDIT." + str(nSequenceID) + "." + str(nComponentID))
            elif sActionTargetID == "RUN":
                # Switch states to Prompt (Run Sequence)
                return self.__UpdateClientState("PROMPT_RUNSEQUENCE;" + str(nSequenceID) + ";" + self.__sClientState)

        # Unhandled use case
        raise Exception("State misalignment")

    # Handle POST /EDIT
    def __HandlePostEdit(self):
        # Make sure we are on Edit Sequence
        if self.__sClientState.startswith("EDIT") == False:
            raise Exception("State misalignment")

        # Determine our sequence and component IDs
        pClientStateComponents = self.__sClientState.split(".")
        nSequenceID = int(pClientStateComponents[1])
        nComponentID = int(pClientStateComponents[2])

        # Parse the JSON string in the body and extract the action type and target
        pJSON = json.loads(self.__pBody)
        sActionType = str(pJSON["action"]["type"])
        sActionTargetID = str(pJSON["action"]["targetid"])

        # Call the base sequence POST handler first
        sNewClientState = self.__HandlePostBaseSequence("EDIT", nSequenceID, nComponentID, sActionType, sActionTargetID)
        if sNewClientState != "":
            # POST handled
            return self.__UpdateClientState(sNewClientState)

        # Handle Edit Sequence specific requests
        if sActionType == "BUTTONCLICK":
            if sActionTargetID == "RUN":
                # Switch states to Prompt (Run Sequence)
                return self.UpdateClientState("PROMPT_RUNSEQUENCE;" + str(nSequenceID) + ";" + self.__sClientState)

        # Unhandled use case
        raise Exception("State misalignment")

    # Handle POST /RUNSEQUENCE
    def __HandlePostRunSequence(self):
        # Make sure we are on Run Sequence
        if self.__sClientState.startswith("RUNSEQUENCE") == False:
            raise Exception("State misalignment")

        # Determine our sequence and component IDs
        pClientStateComponents = self.__sClientState.split(".")
        nSequenceID = int(pClientStateComponents[1])
        nComponentID = int(pClientStateComponents[2])

        # Parse the JSON string in the body and extract the action type and target
        pJSON = json.loads(self.__pBody)
        sActionType = str(pJSON["action"]["type"])
        sActionTargetID = str(pJSON["action"]["targetid"])

        # Check which button the user clicked
        if sActionType == "BUTTONCLICK":
            if sActionTargetID == "ABORT":
                # Switch states to Prompt (Abort sequence run)
                return self.__UpdateClientState("PROMPT_ABORTSEQUENCERUN;" + self.__sClientState)
            elif sActionTargetID == "BACK":
                # Switch states to Home
                return self.__UpdateClientState("HOME")

        # Unhandled use case
        raise Exception("State misalignment")

    # Handle POST /MANUALRUN
    def __HandlePostManualRun(self):
        # Make sure we are on Manual Run
        if self.__sClientState.startswith("MANUALRUN") == False:
            raise Exception("State misalignment")

        # Determine our sequence and component IDs and manual run step
        pClientStateComponents = self.__sClientState.split(".")
        nSequenceID = int(pClientStateComponents[1])
        nComponentID = int(pClientStateComponents[2])
        sManualRunStep = pClientStateComponents[3]

        # Parse the JSON string in the body and extract the action type and target
        pJSON = json.loads(self.__pBody)
        sActionType = str(pJSON["action"]["type"])
        sActionTargetID = str(pJSON["action"]["targetid"])

        # Are we observing another user's manual run?
        if sRemoteUser != self.__pCoreServer.GetRunUser(self.__sRemoteUser):
            # Yes, so the only thing we can do is go back to home
            if sActionType == "BUTTONCLICK":
                if sActionTargetID == "BACK":
                    # Switch states to home
                    return self.__UpdateClientState("HOME")

            # State misalignment in the observing client
            raise Exception("State misalignment")

        # Interpret the post event
        if sManualRunStep == "CASSETTE":
            if sActionType == "BUTTONCLICK":
                if sActionTargetID == "ABORT":
                    # Switch states to Prompt (Abort manual run)
                    return self.__UpdateClientState("PROMPT_ABORTMANUALRUN;" + sClientState)
                elif sActionTargetID == "START":
                    # Advance to the SELECT step
                    self.__sClientState = "MANUALRUN." + str(nSequenceID) + "." + str(nComponentID) + ".SELECT"
                    self.__pCoreServer.SaveRunState(self.__sRemoteUser, self.__sClientState)
                    return self.__UpdateClientState(self.__sClientState)
                else:
                    # Change the selected cassette
                    self.__sClientState = "MANUALRUN." + str(nSequenceID) + "." + sActionTargetID + ".CASSETTE"
                    self.__pCoreServer.SaveRunState(self.__sRemoteUser, self.__sClientState)
                    return self.__UpdateClientState(self.__sClientState)
        elif sManualRunStep == "SELECT":
            if sActionType == "BUTTONCLICK":
                if sActionTargetID == "COMPLETE":
                    # Switch states to Prompt (Complete manual run)
                    return self.__UpdateClientState("PROMPT_COMPLETEMANUALRUN;" + self.__sClientState)
        elif sManualRunStep == "CONFIGURE":
            if sActionType == "BUTTONCLICK":
                if sActionTargetID == "BACK":
                    # Delete the unit operation
                    self.__pUtilities.DeleteComponent(self.__sRemoteUser, nComponentID)

                    # Return to the SELECT step
                    nComponentID = self.__pUtilities.GetSequence(self.__sRemoteUser, nSequenceID)["components"][0]["id"]
                    self.__sClientState = "MANUALRUN." + str(nSequenceID) + "." + str(nComponentID) + ".SELECT"
                    self.__pCoreServer.SaveRunState(self.__sRemoteUser, self.__sClientState)
                    return self.__UpdateClientState(self.__sClientState)
                elif sActionTargetID == "RUN":
                    # Perform the unit operation
                    self.__pCoreServer.PerformOperation(self.__sRemoteUser, nComponentID, nSequenceID)

                    # Update the client state
                    self.__sClientState = self.__pCoreServer.GetRunState(self.__sRemoteUser)
                    return self.__UpdateClientState(self.__sClientState)
        elif sManualRunStep == "RUN":
            if sActionType == "BUTTONCLICK":
                if sActionTargetID == "ABORT":
                    # Switch states to Prompt (Abort manual operation)
                    return self.__UpdateClientState("PROMPT_ABORTMANUALOPERATION;" + sClientState)

        # Unhandled use case
        raise Exception("State misalignment")

    # Handle sequence POST requests
    def __HandlePostBaseSequence(self, sType, nSequenceID, nComponentID, sActionType, sActionTargetID):
        # Check which option the user selected
        if sActionType == "BUTTONCLICK":
            if sActionTargetID == "BACK":
                # Switch states to Select Sequence
                return self.__UpdateClientState("SELECT_SAVEDSEQUENCES")
            elif sActionTargetID == "PREVIOUS":
                # Move to the previous component ID
                nPreviousComponentID = -1
                pSequence = self.__pUtilities.GetSequence(self.__sRemoteUser, nSequenceID)
                for pComponent in pSequence["components"]:
                    if pComponent["id"] == nComponentID:
                        if nPreviousComponentID != -1:
                            self.__sClientState = sType + "." + str(nSequenceID) + "." + str(nPreviousComponentID)
                            self.__pDatabase.UpdateUserClientState(self.__sRemoteUser, self.__sRemoteUser, self.__sClientState)
                        return self.__sClientState
                    else:
                        nPreviousComponentID = pComponent["id"]
                raise Exception("Component ID not found in sequence")
            elif sActionTargetID == "NEXT":
                # Move to the next component ID
                bComponentIDFound = False
                pSequence = self.__pUtilities.GetSequence(self.__sRemoteUser, nSequenceID)
                for pComponent in pSequence["components"]:
                    if bComponentIDFound:
                        self.__sClientState = sType + "." + str(nSequenceID) + "." + str(pComponent["id"])
                        self.__pDatabase.UpdateUserClientState(self.__sRemoteUser, self.__sRemoteUser, self.__sClientState)
                        return self.__sClientState
                    elif pComponent["id"] == nComponentID:
                        bComponentIDFound = True
                if bComponentIDFound:
                    return self.__sClientState
                raise Exception("Component ID not found in sequence" + str(nComponentID))
            else:
                # Check if the target ID corresponds to one of our sequence components
                pSequence = self.__pUtilities.GetSequence(self.__sRemoteUser, nSequenceID)
                for pComponent in pSequence["components"]:
                    if str(pComponent["id"]) == sActionTargetID:
                        # Update the current component and return the latest state to the client
                        self.__sClientState = sType + "." + str(nSequenceID) + "." + str(pComponent["id"])
                        self.__pDatabase.UpdateUserClientState(self.__sRemoteUser, self.__sRemoteUser, self.__sClientState)
                        return self.__sClientState

        # Tell the caller we didn't handle the use case
        return ""

    # Handle POST /PROMPT
    def __HandlePostPrompt(self):
        # Make sure we are on Prompt
        if self.__sClientState.startswith("PROMPT") == False:
            raise Exception("State misalignment");

        # Parse the JSON string in the body
        pJSON = json.loads(self.__pBody)

        # Extract the post parameters
        sActionType = str(pJSON["action"]["type"])
        sActionTargetID = str(pJSON["action"]["targetid"])
        sEdit1 = str(pJSON["edit1"])
        sEdit2 = str(pJSON["edit2"])

        # The only recognized action from a prompt is a button click
        if sActionType != "BUTTONCLICK":
            raise Exception("State misalignment")

        # Interpret the response in context of the client state
        if self.__sClientState.startswith("PROMPT_CREATESEQUENCE"):
            if sActionTargetID == "CREATE":
                # Sequence name is required
                if sEdit1 == "":
                    raise Exception("Sequence name is required")

                # Create the new sequence
                nSequenceID = self.__pDatabase.CreateSequence(self.__sRemoteUser, sEdit1, sEdit2, "Saved", 3, 10, 2)

                # Move the client to the editing the new sequence
                return self.__UpdateClientState("EDIT." + str(nSequenceID))
            if sActionTargetID == "CANCEL":
                # Switch to the previous state
                return self.__UpdateClientState(self.__sClientState.split(";")[1])
        elif sClientState.startswith("PROMPT_COPYSEQUENCE"):
            if sActionTargetID == "COPY":
                # Sequence name is required
                if sEdit1 == "":
                    raise Exception("Sequence name is required")

                # Duplicate the sequence in the database
                nSequenceID = int(self.__sClientState.split(";")[0].split("_")[2])
                nSequenceID = self.__pUtilities.CopySequence(self.__sRemoteUser, nSequenceID, sEdit1, sEdit2, "Saved", 3, 10, 2)

                # Move the client to the editing the new sequence
                self.__UpdateClientState("EDIT." + str(nSequenceID))
            if sActionTargetID == "CANCEL":
                # Switch to the previous state
                return self.__UpdateClientState(self.__sClientState.split(";")[1])
        elif sClientState.startswith("PROMPT_DELETESEQUENCE"):
            if sActionTargetID == "DELETE":
                # Delete the sequence from the database
                nSequenceID = int(self.__sClientState.split(";")[0].split("_")[2])
                self.__pDatabase.DeleteSequence(self.__sRemoteUser, nSequenceID)

                # Switch to the previous state
                return self.__UpdateClientState(self.__sClientState.split(";")[1])
            if sActionTargetID == "CANCEL":
                # Switch to the previous state
                return self.__UpdateClientState(self.__sClientState.split(";")[1])
        elif sClientState.startswith("PROMPT_ABORTSEQUENCERUN"):
            if sActionTargetID == "ABORT":
                # Abort the run and return to the home page
                self.__pCoreServer.AbortRun(self.__sRemoteUser)
                return self.__UpdateClientState("HOME")
            if sActionTargetID == "CANCEL":
                # Switch to the previous state
                return self.__UpdateClientState(self.__sClientState.split(";")[1])
        elif sClientState.startswith("PROMPT_RUNSEQUENCE"):
            if sActionTargetID == "OK":
                # Run the sequence
                self.__pCoreServer.RunSequence(self.__sRemoteUser, int(self.__sClientState.split(";")[1]))
                return self.__UpdateClientState(self.__pCoreServer.GetRunState(self.__sRemoteUser))
            if sActionTargetID == "CANCEL":
                # Switch to the previous state
                return self.__UpdateClientState(self.__sClientState.split(";")[2])
        elif sClientState.startswith("PROMPT_UNITOPERATION"):
            if sActionTargetID == "OK":
                # Are we in the middle of a sequence or manual run?
                sRunState = self.__pCoreServer.GetRunState(self.__sRemoteUser)
                if sRunState.split(".")[0] == "RUNSEQUENCE":
                    # Continue the sequence run
                    self.__pCoreServer.ContinueRun(self.__sRemoteUser)
                else:
                    # Continue the manual run
                    self.__pCoreServer.ContinueOperation(self.__sRemoteUser)
                return self.__UpdateClientState(self.__pCoreServer.GetRunState(self.sRemoteUser))
            if sActionTargetID == "BACK":
                # Return to the home page
                return self.__UpdateClientState("HOME")
        elif sClientState.startswith("PROMPT_MANUALRUN"):
            if sActionTargetID == "OK":
                # Start the manual run
                self.__pCoreServer.StartManualRun(self.__sRemoteUser)
                return self.__UpdateClientState(self.__pCoreServer.GetRunState(self.__sRemoteUser))
            if sActionTargetID == "CANCEL":
                # Switch to the previous state
                return self.__UpdateClientState(self.__sClientState.split(";")[1])
        elif sClientState.startswith("PROMPT_ABORTMANUALRUN"):
            if sActionTargetID == "ABORT":
                # Set the client and system states
                return self.__UpdateClientState("HOME")
            if sActionTargetID == "CANCEL":
                # Switch to the previous state
                return self.__UpdateClientState(self.__sClientState.split(";")[1])
        elif sClientState.startswith("PROMPT_ABORTMANUALOPERATION"):
            if sActionTargetID == "ABORT":
                # Return to the selection step
                sRunState = self.__pCoreServer.GetRunState(self.__sRemoteUser)
                pRunStateComponents = sRunState.split(".")
                self.__sClientState = "MANUALRUN." + pRunStateComponents[1] + "." + pRunStateComponents[2] + ".SELECT"
                self.__pCoreServer.SaveRunState(self.__sRemoteUser, self.__sClientState)
                return self.__UpdateClientState(self.__sClientState)
            if sActionTargetID == "CANCEL":
                # Switch to the previous state
                return self.__UpdateClientState(self.__sClientState.split(";")[1])
        elif sClientState.startswith("PROMPT_COMPLETEMANUALRUN"):
            if sActionTargetID == "SAVE":
                # Finish the manual run
                self.__pCoreServer.FinishManualRun(self.__sRemoteUser)
                return self.__UpdateClientState("HOME")
            if sActionTargetID == "CANCEL":
                # Switch to the previous state
                return self.__UpdateClientState(self.__sClientState.split(";")[1])

        # Unhandled use case
        raise Exception("State misalignment")

    # Handle POST /sequence/[sequenceid]
    def __HandlePostSequence(self):
        # Ignore this function for now
        return self.__UpdateClientState(self.__sClientState)

    # Handle POST /sequence/[sequenceid]/component/[componentid]
    def __HandlePostComponent(self):
        # Extract sequence and component IDs
        pPathComponents = self.__sPath.split("/")
        nSequenceID = int(pPathComponents[2])
        nComponentID = int(pPathComponents[4])
        nInsertionID = None
        if len(pPathComponents) == 6:
            nInsertionID = int(pPathComponents[5])

        # Parse the component JSON if present
        pComponent = None
        if self.__nBodyLength != 0:
            pComponent = json.loads(self.__pBody)

        # Are we working with an existing component?
        if nComponentID != 0:
            # Yes, so update the existing component
            self.__pUtilities.UpdateComponent(self.__sRemoteUser, nSequenceID, nComponentID, nInsertionID, pComponent)
        else:
            # No, so add a new component
            nComponentID = self.__pUtilities.AddComponent(self.__sRemoteUser, nSequenceID, nInsertionID, pComponent)

            # Update the client to show the new component
            pClientStateComponents = self.__sClientState.split(".")
            self.__sClientState = pClientStateComponents[0] + "." + str(nSequenceID) + "." + str(nComponentID)

            # Is the remote user the one that is currently running the system?
            if self.__sRemoteUser == self.__pCoreServer.GetRunUser(self.__sRemoteUser):
                # Yes, so advance to the configuration step after adding a new component
                if nComponentID == 0:
                    self.__sClientState = "MANUALRUN." + str(nSequenceID) + "." + str(pComponent["id"]) + ".CONFIGURE"
                    self.__pCoreServer.SaveRunState(self.__sRemoteUser, self.__sClientState)

        # Return the new state
        return self.__UpdateClientState(self.__sClientState)

    # Handle POST /sequence/[sequenceid]/reagent/[reagentid]
    def __HandlePostReagent(self):
        # Extract sequence and reagent IDs
        pPathComponents = self.__sPath.split("/")
        nSequenceID = int(pPathComponents[2])
        nReagentID = int(pPathComponents[4])

        # Save the reagent
        pReagent = json.loads(self.__pBody)
        self.__pDatabase.UpdateReagent(self.__sRemoteUser, nReagentID, pReagent["available"], pReagent["name"], pReagent["description"])

        # Return the new state
        return self.__UpdateClientState(self.__sClientState)

    # Update the client state and returns the full state
    def __UpdateClientState(self, sClientState):
        self.__sClientState = sClientState
        self.__pDatabase.UpdateUserClientState(self.__sRemoteUser, self.__sRemoteUser, self.__sClientState)
        pGetHandler = GetHandler.GetHandler(self.__pCoreServer, self.__pDatabase, self.__pLog)
        return pGetHandler.HandleRequest(self.__sClientState, self.__sRemoteUser, "/state", None, 0)

