#!/usr/bin/python26

# Imports
import sys
import os
import os.path
import time
import errno
import json
import random
sys.path.append('/var/www/wsgi')
import DummyData

### Implementation of Elixys interface with dummy data ###

class Elixys:

    ### Interface functions ###

    def SetDatabase(self, pDatabase):
        self.pDatabase = pDatabase

    def GetConfiguration(self, sUsername):
        return {"name":"Mini cell 3",
            "version":"2.0",
            "debug":"false"}

    def GetSupportedOperations(self, sUsername):
        return ["Add",
            "Evaporate",
            "Transfer",
            "Elute",
            "React",
            "Prompt",
            "Install",
            "Comment",
            "Activity"]

    def GetServerState(self, sUsername):
        # Are we running the user running the system?
        sRunUsername = self.GetRunUser(sUsername)
        sClientState = self.pDatabase.GetUserClientState(sUsername, sUsername)
        if sUsername == sRunUsername:
           # Yes.  Advance the system state to simulate a run
           self.AdvanceSystemState(sUsername)
        else:
           # No. Is the client currently showing the unit operation prompt?
           if sClientState.startswith("PROMPT_UNITOPERATION"):
               # Yes.  Are we in sync with the run state?
               sRunState = self.GetRunState(sUsername)
               if sClientState != sRunState:
                   # No.  Update the client state
                   sClientState = sRunState
                   self.pDatabase.UpdateUserClientState(sUsername, sUsername, sClientState)

        # Is the user on one of the run screens?
        if sClientState.startswith("RUNSEQUENCE") or sClientState.startswith("MANUALRUN"):
            # Yes.  Is the system running?
            sSystemState = self.GetSystemState(sUsername)
            if sSystemState != "NONE":
                # The system is running.  Make sure the client is displaying the prompt window if the sequence run calls for it
                pSystemStateComponents = sSystemState.split(".")
                nSequenceID = int(pSystemStateComponents[2])
                nComponentID = int(pSystemStateComponents[3])
                if len(pSystemStateComponents) == 5:
                    sManualRunStep = pSystemStateComponents[4]
                else:
                    sManualRunStep = ""
                pSequence = None #self.GetSequenceComponent(sUsername, nSequenceID, nComponentID)

                # Are we on a prompt or install unit operation?
                if (pSequence["components"][0]["componenttype"] == "PROMPT") or (pSequence["components"][0]["componenttype"] == "INSTALL"):
                    # Yes.  Is the client currently showing the unit operation prompt?
                    if not sClientState.startswith("PROMPT_UNITOPERATION"):
                        # No.  Are we running a sequence automatically or on the run step of a manual run?
                        if sClientState.startswith("RUNSEQUENCE") or (sManualRunStep == "RUN"):
                            # Yes.  Move the client state to the unit operation prompt
                            sClientState = "PROMPT_UNITOPERATION;" + sClientState;
                            self.pDatabase.UpdateUserClientState(sUsername, sUsername, sClientState)
            else:
                # The system is no longer running.  Move the client away from the run page
                sClientState = "HOME"
                self.pDatabase.UpdateUserClientState(sUsername, sUsername, sClientState)

        # Update and return the default system state
        return self.UpdateServerState(DummyData.GetDefaultSystemState(sRunUsername))

    def GetRunState(self, sUsername):
        # Are we running?
        sSystemState = self.GetSystemState(sUsername)
        if sSystemState != "NONE":
            # Yes, so strip the user name
            sSystemState = sSystemState[len(sSystemState.split(".")[0]) + 1:]

        # Return the state
        return sSystemState

    def SaveRunState(self, sUsername, sSystemState):
        # Get the run user
        sRunUsername = self.GetRunUser(sUsername)
        if sRunUsername == "":
            raise Exception("System is not running")

        # Save the state
        self.SaveSystemState(sUsername, sRunUsername + "." + sSystemState)
        return True

    def GetRunUser(self, sUsername):
        # Are we running?
        sSystemState = self.GetSystemState(sUsername)
        sRunUser = ""
        if sSystemState != "NONE":
            # Yes, so extract the user name
            sRunUser = sSystemState.split(".")[0]

        # Return the user
        return sRunUser

    def RunSequence(self, sUsername, nSequenceID):
        # Load the user's sequence and save it as the system sequence
        pSequence = self.GetSequenceInternal(sUsername, nSequenceID)
        pSequence["metadata"]["id"] = 10000
        self.SaveSequence(sUsername, pSequence, True, True)

        # Load the user's sequence reagents and save them as the system sequence reagents
        pReagents = self.GetSequenceReagentsInternal(sUsername, nSequenceID)
        self.SaveSequenceReagentsInternal(sUsername, pReagents, True, True)

        # Format the initial system state
        sSystemState = sUsername + ".RUNSEQUENCE.10000."
        pSequence = self.GetSequenceInternal(sUsername, nSequenceID)
        sSystemState += str(pSequence["components"][3]["id"])

        # Save the state
        self.SaveSystemState(sUsername, sSystemState)
        return True

    def AbortRun(self, sUsername):
        # Save the state and return
        self.SaveSystemState(sUsername, "NONE")
        return True

    def ContinueRun(self, sUsername):
        # Look up the current run component
        sSystemState = self.GetSystemState(sUsername)
        pSystemStateComponents = sSystemState.split(".")
        sMode = pSystemStateComponents[1]
        nSequenceID = int(pSystemStateComponents[2])
        nComponentID = int(pSystemStateComponents[3])
        if sMode == "MANUALRUN":
            sManualRunStep = pSystemStateComponents[4]
        else:
            sManualRunStep = ""

        # Attempt to advance to the next component
        nNextComponentID = self.RunSequenceAdvance(sUsername, nSequenceID, nComponentID, sManualRunStep)
        if nNextComponentID == None:
            # Run is complete
            return

        # Set the component ID and state
        nComponentID = nNextComponentID
        nComponentState = 0

        # Save the states and return
        sRunState = sMode + "." + str(nSequenceID) + "." + str(nComponentID) + "." + str(nComponentState)
        self.SaveRunState(sUsername, sRunState)
        self.pDatabase.UpdateUserClientState(sUsername, sUsername, sRunState)
        return True

    def StartManualRun(self, sUsername):
        # Create a new blank sequence save it as the system sequence
        pSequence = DummyData.GetBlankSequence(sUsername)
        pSequence["metadata"]["id"] = 10000
        self.SaveSequence(sUsername, pSequence, True, True)

        # Create and save the blank reagent array
        pReagents = []
        for nCassetteID in range(0, 3):
            for nPositionID in range(0, 10):
                pReagent = {"available":False,
                    "reagentid":((nCassetteID * 10) + nPositionID + 31),
                    "componentid":(nCassetteID + 1),
                    "position":str(nPositionID + 1),
                    "name":"",
                    "description":""},
                pReagents.extend(pReagent)
        self.SaveSequenceReagentsInternal(sUsername, pReagents, True, True)

        # Format the initial system state
        sSystemState = sUsername + ".MANUALRUN.10000."
        pSequence = self.GetSequenceInternal(sUsername, 10000)
        sSystemState += str(pSequence["components"][0]["id"])
        sSystemState += ".CASSETTE"

        # Save the state
        self.SaveSystemState(sUsername, sSystemState)
        return True

    def PerformOperation(self, sUsername, nComponentID, nSequenceID):
        # Update the run state
        sRunState = "MANUALRUN." + str(nSequenceID) + "." + str(nComponentID) + ".RUN"
        self.SaveRunState(sUsername, sRunState)
        return True

    def AbortOperation(self, sUsername):
        return False

    def ContinueOperation(self, sUsername):
        # Get the run state
        sRunState = self.GetRunState(sUsername)
        pRunStateComponents = sRunState.split(".")

        # Advance to the select step
        sRunState = "MANUALRUN." + pRunStateComponents[1] + "." + pRunStateComponents[2] + ".SELECT"
        self.SaveRunState(sUsername, sRunState)
        self.pDatabase.UpdateUserClientState(sUsername, sUsername, sRunState)
        return True

    def FinishManualRun(self, sUsername):
        # Complete the run
        self.SaveSystemState(sUsername, "NONE")
        return True





    ### Functions below to be moved to DBComm.py ###

    def GetUserAccessLevels(self, sUsername):
        return {}

    def GetUser(self, sUsername):
        return {"username":sUsername,
            "useraccesslevel":"Administrator"}

    def SaveUser(self, sUsername, sPassword, sAccesslevel):
        return False

    def DeleteUser(self, sUsername):
        return False

    def SaveSequence(self, sUsername, pSequence, bLockSystem = True, bSystemSequence = False):
        # Obtain a lock on the system
        if bLockSystem:
            self.LockSystem(sUsername, bSystemSequence)

        # Set the subdirectory
        if bSystemSequence:
            sSubdirectory = "system"
        else:
            sSubdirectory = sUsername

        # Remove details to each component
        for pComponent in pSequence["components"]:
            self.RemoveComponentDetails(pComponent)

        # Open and write to the sequence file
        pSequenceFile = os.open("/var/www/wsgi/" + sSubdirectory + "/sequence.txt", os.O_CREAT | os.O_TRUNC | os.O_RDWR)
        os.write(pSequenceFile, json.dumps(pSequence))
        os.close(pSequenceFile)

        # Release the system lock
        if bLockSystem:
            self.UnlockSystem(sUsername, bSystemSequence)
        return True

    def SaveSequenceComponent(self, sUsername, nSequenceID, nComponentID, nInsertionID, pComponent):
        # Load the sequence
        pSequence = self.GetSequenceInternal(sUsername, nSequenceID)

        # Locate the component
        nComponentIndex = 0
        for pSequenceComponent in pSequence["components"]:
            if pSequenceComponent["id"] == nComponentID:
                # The index points to this component
                break
            else:
                nComponentIndex += 1

        # Locate the insertion index
        if nInsertionID != None:
            nInsertionIndex = 0
            for pSequenceComponent in pSequence["components"]:
                if pSequenceComponent["id"] == nInsertionID:
                    # Insert at the index after the specified component
                    nInsertionIndex += 1
                    break
                else:
                    nInsertionIndex += 1

        # Are we working with an existing component or adding a new one?
        if nComponentIndex < len(pSequence["components"]):
            # We are working with an existing component.  Update the component first
            if pComponent != None:
                self.UpdateComponentDetails(pSequence["components"][nComponentIndex], pComponent)

            # Are we also moving the component?
            if nInsertionID != None:
                # Load the component if we don't have one
                if pComponent == None:
                    pComponent = None  #self.GetSequenceComponent(sUsername, nSequenceID, nComponentID)["components"][0]

                # Insert the component and remove the old
                pSequence["components"].insert(nInsertionIndex, self.RemoveComponentDetails(pComponent))
                if nInsertionIndex < nComponentIndex:
                    del pSequence["components"][nComponentIndex + 1]
                else:
                    del pSequence["components"][nComponentIndex]
        else:
            # We are adding a new component.  Generate a random number for the component ID
            pComponent["id"] = int(random.random() * 100000)

            # Are we inserting somewhere in the middle?
            if (nInsertionID != None) and (nInsertionIndex < len(pSequence["components"])):
                # Yes, so insert at the desired position
                print >> sys.stderr, "Inserting at index " + str(nInsertionIndex)
                pSequence["components"].insert(nInsertionIndex, self.RemoveComponentDetails(pComponent))
            else:
                # No, so append at the end of the sequence
                pSequence["components"].append(self.RemoveComponentDetails(pComponent))

            # Select the component
            sClientState = self.pDatabase.GetUserClientState(sUsername, sUsername)
            pClientStateComponents = sClientState.split(".")
            sClientState = pClientStateComponents[0] + "." + str(nSequenceID) + "." + str(pComponent["id"])
            self.pDatabase.UpdateUserClientState(sUsername, sUsername, sClientState)

        # Save the sequence
        self.SaveSequence(sUsername, pSequence, False, nSequenceID == 10000)
        return True

    def DeleteSequence(self, sUsername, nSequenceID):
        return False

    def DeleteSequenceComponent(self, sUsername, nSequenceID, nComponentID):
        # Load the sequence
        pSequence = self.GetSequenceInternal(sUsername, nSequenceID)

        # Locate the component
        nComponentIndex = 0
        for pSequenceComponent in pSequence["components"]:
            if pSequenceComponent["id"] == nComponentID:
                # The index points to this component
                break
            else:
                nComponentIndex += 1

        # Make sure we found the component
        if nComponentIndex == len(pSequence["components"]):
            raise Exception("Failed to locate sequence component")

        # Delete the component
        del pSequence["components"][nComponentIndex]

        # Save the sequence
        self.SaveSequence(sUsername, pSequence, False, nSequenceID == 10000)
        return True

    def CopySequence(self, sUsername, nSequenceID, sName, sComment, sCreator):
        return False

    ### Internal functions ###

    def LockSystem(self, sUsername, bGlobalState = False):
        # Set the subdirectory
        if bGlobalState:
            sSubdirectory = "system"
        else:
            sSubdirectory = sUsername

        # Create the user's state directory as needed
        if not os.path.exists("/var/www/wsgi/" + sSubdirectory):
            os.makedirs("/var/www/wsgi/" + sSubdirectory)

        # Loop until we acquire the lock
        nFailCount = 0
        while True:
            try:
                self.m_pLockFile = os.open("/var/www/wsgi/" + sSubdirectory + "/lock.file", os.O_CREAT | os.O_EXCL | os.O_RDWR)
                break
            except OSError as e:
                if e.errno != errno.EEXIST:
                    raise
                if nFailCount < 10:
                    time.sleep(0.05)
                    nFailCount += 1
                else:
                    # The most likely cause of us getting here is the system crashed and left the lock file behind.  Go ahead
                    # and capture the lock file anyway since this solution is only temporary until we move to MySQL
                    m_pLockFile = os.open("/var/www/wsgi/" + sSubdirectory + "/lock.file", os.O_RDWR)
                    break

    def UnlockSystem(self, sUsername, bGlobalState = False):
        # Set the subdirectory
        if bGlobalState:
            sSubdirectory = "system"
        else:
            sSubdirectory = sUsername

         # Release the lock
        os.close(self.m_pLockFile)
        os.unlink("/var/www/wsgi/" + sSubdirectory + "/lock.file")

    def GetSequenceInternal(self, sUsername, nSequenceID):
        # Obtain a lock on the system
        self.LockSystem(sUsername)

        # Determine the subdirectory
        if nSequenceID == 10000:
            sSubdirectory = "system"
        else:
            sSubdirectory = sUsername

        # Attempt to get the sequence from the file system
        try:
            pSequenceFile = os.open("/var/www/wsgi/" + sSubdirectory + "/sequence.txt", os.O_RDWR)
            sSequence = os.read(pSequenceFile, 100000)
            os.close(pSequenceFile)
            pSequence = json.loads(sSequence)
        except OSError as e:
            # Check the error type
            if e.errno != errno.ENOENT:
                # An error other than file does not exist was encountered.  Release the system local and raise again
                self.UnlockSystem(sUsername)
                raise
            else:
                # Sequence files does not exist.  Default to the dummy sequence and create the file
                pSequence = DummyData.GetDefaultSequence()
                self.SaveSequence(sUsername, pSequence, False)

        # Release the system lock
        self.UnlockSystem(sUsername)

        # Return the sequence
        return pSequence

    def GetSystemState(self, sUsername):
        # Obtain a lock on the system
        self.LockSystem(sUsername, True)

        # Attempt to get the system state from the file system
        try:
            pStateFile = os.open("/var/www/wsgi/system/state.txt", os.O_RDWR)
            sSystemState = os.read(pStateFile, 99)
            os.close(pStateFile)
        except OSError as e:
            # Check the error type
            if e.errno != errno.ENOENT:
                # An error other than file does not exist was encountered.  Release the system lock and raise again
                self.UnlockSystem(sUsername, True)
                raise
            else:
                # System state file does not exist.  Default to the no run state and create the file
                sSystemState = "NONE"
                self.SaveSystemState(sUsername, sSystemState, False)

        # Release the system lock and return
        self.UnlockSystem(sUsername, True)
        return sSystemState

    def SaveSystemState(self, sUsername, sSystemState, bLockSystem = True):
        # Obtain a lock on the system
        if bLockSystem:
            self.LockSystem(sUsername, True)

        # Open and write to the system state file
        pStateFile = os.open("/var/www/wsgi/system/state.txt", os.O_CREAT | os.O_TRUNC | os.O_RDWR)
        os.write(pStateFile, str(sSystemState))
        os.close(pStateFile)

        # Release the system lock
        if bLockSystem:
            self.UnlockSystem(sUsername, True)
        return True

    def UpdateComponentDetails(self, pTargetComponent, pSourceComponent):
        # Update the parts of the component that we save
        if pTargetComponent["componenttype"] == "CASSETTE":
            pTargetComponent["available"] = pSourceComponent["available"]
        elif pTargetComponent["componenttype"] == "ADD":
            pTargetComponent["reactor"] = pSourceComponent["reactor"]
            pTargetComponent["reagent"] = pSourceComponent["reagent"]
        elif pTargetComponent["componenttype"] == "EVAPORATE":
            pTargetComponent["reactor"] = pSourceComponent["reactor"]
            pTargetComponent["duration"] = pSourceComponent["duration"]
            pTargetComponent["evaporationtemperature"] = pSourceComponent["evaporationtemperature"]
            pTargetComponent["finaltemperature"] = pSourceComponent["finaltemperature"]
            pTargetComponent["stirspeed"] = pSourceComponent["stirspeed"]
        elif pTargetComponent["componenttype"] == "TRANSFER":
            pTargetComponent["reactor"] = pSourceComponent["reactor"]
            pTargetComponent["target"] = pSourceComponent["target"]
        elif pTargetComponent["componenttype"] == "ELUTE":
            pTargetComponent["reactor"] = pSourceComponent["reactor"]
            pTargetComponent["reagent"] = pSourceComponent["reagent"]
            pTargetComponent["target"] = pSourceComponent["target"]
        elif pTargetComponent["componenttype"] == "REACT":
            pTargetComponent["reactor"] = pSourceComponent["reactor"]
            pTargetComponent["position"] = pSourceComponent["position"]
            pTargetComponent["duration"] = pSourceComponent["duration"]
            pTargetComponent["reactiontemperature"] = pSourceComponent["reactiontemperature"]
            pTargetComponent["finaltemperature"] = pSourceComponent["finaltemperature"]
            pTargetComponent["stirspeed"] = pSourceComponent["stirspeed"]
        elif pTargetComponent["componenttype"] == "PROMPT":
            pTargetComponent["message"] = pSourceComponent["message"]
        elif pTargetComponent["componenttype"] == "INSTALL":
            pTargetComponent["reactor"] = pSourceComponent["reactor"]
            pTargetComponent["message"] = pSourceComponent["message"]
        elif pTargetComponent["componenttype"] == "COMMENT":
            pTargetComponent["comment"] = pSourceComponent["comment"]
        elif pTargetComponent["componenttype"] == "ACTIVITY":
            pTargetComponent["reactor"] = pSourceComponent["reactor"]

    def RemoveComponentDetails(self, pComponent):
        # Get a list of component-specific keys we want to save
        pDesiredKeys = None
        if pComponent["componenttype"] == "ADD":
            pDesiredKeys = ["componenttype", "id", "reactor", "reagent"]
        elif pComponent["componenttype"] == "EVAPORATE":
            pDesiredKeys = ["componenttype", "id", "reactor", "duration", "evaporationtemperature", "finaltemperature", "stirspeed"]
        elif pComponent["componenttype"] == "TRANSFER":
            pDesiredKeys = ["componenttype", "id", "reactor", "target"]
        elif pComponent["componenttype"] == "ELUTE":
            pDesiredKeys = ["componenttype", "id", "reactor", "reagent", "target"]
        elif pComponent["componenttype"] == "REACT":
            pDesiredKeys = ["componenttype", "id", "reactor", "position", "duration", "reactiontemperature", "finaltemperature", "stirspeed"]
        elif pComponent["componenttype"] == "PROMPT":
            pDesiredKeys = ["componenttype", "id", "reactor", "message"]
        elif pComponent["componenttype"] == "INSTALL":
            pDesiredKeys = ["componenttype", "id", "reactor", "message"]
        elif pComponent["componenttype"] == "COMMENT":
            pDesiredKeys = ["componenttype", "id", "reactor", "comment"]
        elif pComponent["componenttype"] == "ACTIVITY":
            pDesiredKeys = ["componenttype", "id", "reactor"]

        # Remove the keys that we do not want to save
        if pDesiredKeys != None:
            pUnwantedKeys = set(pComponent) - set(pDesiredKeys)
            for pUnwantedKey in pUnwantedKeys:
                del pComponent[pUnwantedKey]
        return pComponent

    def AdvanceSystemState(self, sUsername):
        # Load the system state
        sSystemState = self.GetSystemState(sUsername)

        # Extract the component-specific part of the system state
        pSystemStateComponents = sSystemState.split(".")
        sUsername = pSystemStateComponents[0]
        sMode = pSystemStateComponents[1]
        nSequenceID = int(pSystemStateComponents[2])
        nComponentID = int(pSystemStateComponents[3])
        sManualRunStep = ""
        if sMode == "MANUALRUN":
            # Get the manual run step and return if we are not on the run step
            sManualRunStep = pSystemStateComponents[4]
            if sManualRunStep != "RUN":
                return

            # Initialize or extract the component state
            if len(pSystemStateComponents) < 6:
                nComponentState = 0
            else:
                nComponentState = int(pSystemStateComponents[5])
        else:
            # Initialize or extract the component state
            if len(pSystemStateComponents) < 5:
                nComponentState = 0
            else:
                nComponentState = int(pSystemStateComponents[4])

        # Load the component
        pSequence = None #self.GetSequenceComponent(sUsername, nSequenceID, nComponentID)

        # Advance the system state depending on the component type
        if pSequence["components"][0]["componenttype"] == "COMMENT":
            # Skip comment operations.  Attempt to advance to the next component
            nNextComponentID = self.RunSequenceAdvance(sUsername, nSequenceID, nComponentID, sManualRunStep)
            if nNextComponentID == None:
                # Run is complete
                return

            # Set the component ID and state
            nComponentID = nNextComponentID
            nComponentState = 0
        elif (pSequence["components"][0]["componenttype"] == "PROMPT") or (pSequence["components"][0]["componenttype"] == "INSTALL"):
            # Do nothing until the user responds
            return
        else:
            # Default behavior is to show each unit operation for a few seconds
            if nComponentState < 7:
                # Increment our value
                nComponentState += 1
            else:
                # Attempt to advance to the next component
                nNextComponentID = self.RunSequenceAdvance(sUsername, nSequenceID, nComponentID, sManualRunStep)
                if nNextComponentID == None:
                    # Run is complete
                    return

                # Set the component ID and state
                nComponentID = nNextComponentID
                nComponentState = 0

        # Save the system state and return
        sSystemState = sUsername + "." + sMode + "." + str(nSequenceID) + "." + str(nComponentID) + "."
        if sMode == "MANUALRUN":
            sSystemState = sSystemState + sManualRunStep + "."
        sSystemState = sSystemState + str(nComponentState)
        self.SaveSystemState(sUsername, sSystemState)
        return

    def RunSequenceAdvance(self, sUsername, nSequenceID, nComponentID, sManualRunStep):
        # Try and find the next component
        pSequence = None #self.GetSequence(sUsername, nSequenceID)
        nIndex = 0
        bComponentFound = False
        nNextComponentID = None
        while nIndex < len(pSequence["components"]):
            pComponent = pSequence["components"][nIndex]
            if bComponentFound:
                # This is the next component
                nNextComponentID = pComponent["id"]
                break
            elif pComponent["id"] == nComponentID:
                # Found it
                bComponentFound = True
            nIndex += 1

        # Return the next component if we found it
        if nNextComponentID != None:
            return nNextComponentID
        else:
            # Failed to find the next component so this run is complete.  Update the states and return
            if sManualRunStep == "RUN":
                # The manual run step is complete.  Return to the selection step
                sRunState = "MANUALRUN." + str(nSequenceID) + "." + str(nComponentID) + ".SELECT"
                self.SaveRunState(sUsername, sRunState)
                self.pDatabase.UpdateUserClientState(sUsername, sUsername, sRunState)
            else:
                # The noninteractive sequence run is complete.  Return to the home page
                self.SaveSystemState(sUsername, "NONE")
                self.pDatabase.UpdateUserClientState(sUsername, sUsername, "HOME")
            return None

    def UpdateServerState(self, pServerState):
        return pServerState

    # Lock file
    m_pLockFile = 0
