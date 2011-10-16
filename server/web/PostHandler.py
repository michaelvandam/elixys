#!/usr/bin/python

# Imports
import json
import GetHandler
import sys
sys.path.append("/opt/elixys/core")
import SequenceManager

class PostHandler:
    # Constructor
    def __init__(self, pCoreServer, pDatabase):
        # Remember the input references
        self.__pCoreServer = pCoreServer
        self.__pDatabase = pDatabase

        # Create the sequence manager
        self.__pSequenceManager = SequenceManager.SequenceManager(pDatabase)

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
                return self.__UpdateStates("SELECT_SAVEDSEQUENCES")
            elif sActionTargetID == "OBSERVE":
                # Swtich to Run Sequence
                return self.__UpdateStates(self.__pCoreServer.GetRunState(self.__sRemoteUser))

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
                return self.__UpdateStates("VIEW." + str(nSequenceID))
            elif sActionTargetID == "EDIT":
                # Switch states to Edit Sequence
                return self.__UpdateStates("EDIT." + str(nSequenceID))
            elif sActionTargetID == "RUN":
                # Switch states to Prompt (Run Sequence)
                return self.__UpdateStates("PROMPT_RUNSEQUENCE;" + str(nSequenceID) + ";" + self.__sClientState)
            elif sActionTargetID == "BACK":
                # Switch states to Home
                return self.__UpdateStates("HOME")
            elif sActionTargetID == "CREATE":
                # Switch states to Prompt (Create Sequence)
                return self.__UpdateStates("PROMPT_CREATESEQUENCE;" + self.__sClientState)
            elif sActionTargetID == "COPY":
                # Switch states to Prompt (Copy Sequence)
                return self.__UpdateStates("PROMPT_COPYSEQUENCE_" + str(nSequenceID) + ";" + self.__sClientState)
            elif sActionTargetID == "DELETE":
                # Switch states to Prompt (Delete Sequence)
                return self.__UpdateStates("PROMPT_DELETESEQUENCE_" + str(nSequenceID) + ";" + self.__sClientState)
        elif sActionType == "TABCLICK":
            if sActionTargetID == "SAVEDSEQUENCES":
                # Switch states to the Saved Sequences tab
                return self.__UpdateStates("SELECT_SAVEDSEQUENCES")
            elif sActionTargetID == "RUNHISTORY":
                # Switch states to the Run History tab
                return self.__UpdateStates("SELECT_RUNHISTORY")

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
            return self.__UpdateStates(sNewClientState)

        # Handle View Sequence specific requests
        if sActionType == "BUTTONCLICK":
            if sActionTargetID == "EDIT":
                # Switch states to Edit Sequence
                return self.__UpdateStates("EDIT." + str(nSequenceID) + "." + str(nComponentID))
            elif sActionTargetID == "RUN":
                # Switch states to Prompt (Run Sequence)
                return self.__UpdateStates("PROMPT_RUNSEQUENCE;" + str(nSequenceID) + ";" + self.__sClientState)

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
            return self.__UpdateStates(sNewClientState)

        # Handle Edit Sequence specific requests
        if sActionType == "BUTTONCLICK":
            if sActionTargetID == "RUN":
                # Switch states to Prompt (Run Sequence)
                return self.UpdateStates("PROMPT_RUNSEQUENCE;" + str(nSequenceID) + ";" + self.__sClientState)

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
                return self.__UpdateStates("PROMPT_ABORTSEQUENCERUN;" + self.__sClientState)
            elif sActionTargetID == "BACK":
                # Switch states to Home
                return self.__UpdateStates("HOME")

        # Unhandled use case
        raise Exception("State misalignment")

    # Handle sequence POST requests
    def __HandlePostBaseSequence(self, sType, nSequenceID, nComponentID, sActionType, sActionTargetID):
        # Check which option the user selected
        if sActionType == "BUTTONCLICK":
            if sActionTargetID == "BACK":
                # Switch states to Select Sequence
                return "SELECT_SAVEDSEQUENCES"
            elif sActionTargetID == "PREVIOUS":
                # Move to the previous component ID
                nPreviousComponentID = -1
                pSequence = self.__pSequenceManager.GetSequence(self.__sRemoteUser, nSequenceID, False)
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
                pSequence = self.__pSequenceManager.GetSequence(self.__sRemoteUser, nSequenceID, False)
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
                pSequence = self.__pSequenceManager.GetSequence(self.__sRemoteUser, nSequenceID, False)
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
                return self.__UpdateStates("EDIT." + str(nSequenceID))
            if sActionTargetID == "CANCEL":
                # Switch to the previous state
                return self.__UpdateStates(self.__sClientState.split(";")[1])
        elif self.__sClientState.startswith("PROMPT_COPYSEQUENCE"):
            if sActionTargetID == "COPY":
                # Sequence name is required
                if sEdit1 == "":
                    raise Exception("Sequence name is required")

                # Duplicate the sequence in the database
                nSequenceID = int(self.__sClientState.split(";")[0].split("_")[2])
                nSequenceID = self.__pSequenceManager.CopySequence(self.__sRemoteUser, nSequenceID, sEdit1, sEdit2, "Saved", 3, 10, 2)

                # Move the client to the editing the new sequence
                self.__UpdateStates("EDIT." + str(nSequenceID))
            if sActionTargetID == "CANCEL":
                # Switch to the previous state
                return self.__UpdateStates(self.__sClientState.split(";")[1])
        elif self.__sClientState.startswith("PROMPT_DELETESEQUENCE"):
            if sActionTargetID == "DELETE":
                # Delete the sequence from the database
                nSequenceID = int(self.__sClientState.split(";")[0].split("_")[2])
                self.__pDatabase.DeleteSequence(self.__sRemoteUser, nSequenceID)

                # Switch to the previous state
                return self.__UpdateStates(self.__sClientState.split(";")[1])
            if sActionTargetID == "CANCEL":
                # Switch to the previous state
                return self.__UpdateStates(self.__sClientState.split(";")[1])
        elif self.__sClientState.startswith("PROMPT_ABORTSEQUENCERUN"):
            if sActionTargetID == "ABORT":
                # Abort the run and return to the home page
                self.__pCoreServer.AbortRun(self.__sRemoteUser)
                return self.__UpdateStates("HOME")
            if sActionTargetID == "CANCEL":
                # Switch to the previous state
                return self.__UpdateStates(self.__sClientState.split(";")[1])
        elif self.__sClientState.startswith("PROMPT_RUNSEQUENCE"):
            if sActionTargetID == "OK":
                # Run the sequence
                self.__pCoreServer.RunSequence(self.__sRemoteUser, int(self.__sClientState.split(";")[1]))
                return self.__UpdateStates(self.__pCoreServer.GetRunState(self.__sRemoteUser))
            if sActionTargetID == "CANCEL":
                # Switch to the previous state
                return self.__UpdateStates(self.__sClientState.split(";")[2])
        elif self.__sClientState.startswith("PROMPT_UNITOPERATION"):
            if sActionTargetID == "OK":
                # Are we in the middle of a sequence or manual run?
                sRunState = self.__pCoreServer.GetRunState(self.__sRemoteUser)
                if sRunState.split(".")[0] == "RUNSEQUENCE":
                    # Continue the sequence run
                    self.__pCoreServer.ContinueRun(self.__sRemoteUser)
                return self.__UpdateStates(self.__pCoreServer.GetRunState(self.sRemoteUser))
            if sActionTargetID == "BACK":
                # Return to the home page
                return self.__UpdateStates("HOME")

        # Unhandled use case
        raise Exception("State misalignment")

    # Handle POST /sequence/[sequenceid]
    def __HandlePostSequence(self):
        # Ignore this function for now
        return self.__UpdateStates(self.__sClientState)

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
            self.__pSequenceManager.UpdateComponent(self.__sRemoteUser, nSequenceID, nComponentID, nInsertionID, pComponent)
        else:
            # No, so add a new component
            nComponentID = self.__pSequenceManager.AddComponent(self.__sRemoteUser, nSequenceID, nInsertionID, pComponent)

            # Update the client to show the new component
            pClientStateComponents = self.__sClientState.split(".")
            self.__sClientState = pClientStateComponents[0] + "." + str(nSequenceID) + "." + str(nComponentID)

        # Return the new state
        return self.__UpdateStates(self.__sClientState)

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
        return self.__UpdateStates(self.__sClientState)

    # Update the client state and returns the full state
    def __UpdateStates(self, sClientState):
        self.__sClientState = sClientState
        self.__pDatabase.UpdateUserClientState(self.__sRemoteUser, self.__sRemoteUser, self.__sClientState)
        pGetHandler = GetHandler.GetHandler(self.__pCoreServer, self.__pDatabase)
        return pGetHandler.HandleRequest(self.__sClientState, self.__sRemoteUser, "/state", None, 0)

