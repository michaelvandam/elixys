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

    def GetUserAccessLevels(self, sUsername):
        return {}

    def GetUser(self, sUsername):
        return {"username":sUsername,
            "useraccesslevel":"Administrator"}

    def SaveUser(self, sUsername, sPassword, sAccesslevel):
        return False

    def DeleteUser(self, sUsername):
        return False

    def GetClientState(self, sUsername):
        # Obtain a lock on the system
        self.LockSystem(sUsername)

        # Attempt to get the client state from the file system
        try:
            pStateFile = os.open("/var/www/wsgi/" + sUsername + "/state.txt", os.O_RDWR)
            sClientState = os.read(pStateFile, 99)
            os.close(pStateFile)
        except OSError as e:
            # Check the error type
            if e.errno != errno.ENOENT:
                # An error other than file does not exist was encountered.  Release the system lock and raise again
                self.UnlockSystem(sUsername, True)
                raise
            else:
                # Client state file does not exist.  Default to the home state and create the file
                sClientState = "HOME"
                self.SaveClientState(sUsername, sClientState, False)

        # Release the system lock and return
        self.UnlockSystem(sUsername)
        return sClientState

    def SaveClientState(self, sUsername, sClientState, bLockSystem = True):
        # Obtain a lock on the system
        if bLockSystem:
            self.LockSystem(sUsername)

        # Open and write to the client state file
        pStateFile = os.open("/var/www/wsgi/" + sUsername + "/state.txt", os.O_CREAT | os.O_TRUNC | os.O_RDWR)
        os.write(pStateFile, str(sClientState))
        os.close(pStateFile)

        # Release the system lock
        if bLockSystem:
            self.UnlockSystem(sUsername)
        return True

    def GetServerState(self, sUsername):
        # Are we running the system?
        if sUsername == self.GetRunUser(sUsername):
           # Yes, so run the system one step
           self.AdvanceSystemState(sUsername)

        # Update and return the default system state
        return self.UpdateServerState(DummyData.GetDefaultSystemState())

    def GetSequenceList(self, sUsername, sType):
        # Load the sequence
        pSequence = self.GetSequenceInternal(sUsername, 108)

        # Create 25 copies of our sequence
        pSequenceList = []
        for x in range(0, 25):
            pSequenceListItem = pSequence["metadata"].copy()
            pSequenceListItem["name"] += " (" + str(x) + ")"
            pSequenceListItem["comment"] += " (" + str(x) + ")"
            pSequenceListItem["id"] += x
            pSequenceList.append(pSequenceListItem)

        # Return the sequence list
        return pSequenceList

    def GetSequence(self, sUsername, nSequenceID):
        # Get the basic sequence
        pSequence = self.GetSequenceInternal(sUsername, nSequenceID)

        # Add details to each component
        for pComponent in pSequence["components"]:
            self.AddComponentDetails(sUsername, nSequenceID, pComponent)

        # Return the sequence
        return pSequence

    def GetSequenceComponent(self, sUsername, nSequenceID, nComponentID):
        # Load the sequence
        pSequence = self.GetSequenceInternal(sUsername, nSequenceID)

        # Remove all the components except the one we are interested in
        pSequence["components"] = filter(lambda pComponent: pComponent["id"] == nComponentID, pSequence["components"])

        # Make sure we found the component
        if len(pSequence["components"]) == 0:
            raise Exception("Failed to locate sequence component")

        # Add details to the component
        self.AddComponentDetails(sUsername, nSequenceID, pSequence["components"][0])

        # Return the sequence
        return pSequence

    def SaveSequence(self, sUsername, pSequence, bLockSystem = True, bGlobalSequence = False):
        # Obtain a lock on the system
        if bLockSystem:
            self.LockSystem(sUsername, bGlobalSequence)

        # Set the subdirectory
        if bGlobalSequence:
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
            self.UnlockSystem(sUsername, bGlobalSequence)
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
                    pComponent = self.GetSequenceComponent(sUsername, nSequenceID, nComponentID)["components"][0]

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
            if nInsertionIndex < len(pSequence["components"]):
                # Yes, so insert at the desired position
                print >> sys.stderr, "Inserting at index " + str(nInsertionIndex)
                pSequence["components"].insert(nInsertionIndex, self.RemoveComponentDetails(pComponent))
            else:
                # No, so append at the end of the sequence
                pSequence["components"].append(self.RemoveComponentDetails(pComponent))

            # Select the component
            sClientState = self.GetClientState(sUsername)
            pClientStateComponents = sClientState.split(".")
            sClientState = pClientStateComponents[0] + "." + str(nSequenceID) + "." + str(pComponent["id"])
            self.SaveClientState(sUsername, sClientState)

        # Save the sequence
        self.SaveSequence(sUsername, pSequence)
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
        self.SaveSequence(sUsername, pSequence)
        return True

    def CopySequence(self, sUsername, nSequenceID, sName, sComment, sCreator):
        return False

    def GetSequenceReagent(self, sUsername, nSequenceID, nReagentID):
        # Load all of our reagents
        pReagents = self.GetSequenceReagentsInternal(sUsername, nSequenceID)

        # Locate and return the reagent of interest
        pReagent = {"type":"reagent"}
        for pSequenceReagent in pReagents:
            if pSequenceReagent["reagentid"] == nReagentID:
                pReagent.update(pSequenceReagent)
                return pReagent

        # Request reagent not found
        pReagent.update({"available":False,
            "reagentid":0,
            "componentid":0,
            "position":"",
            "name":"[invalid]",
            "description":"[invalid]"})
        return pReagent

    def SaveSequenceReagent(self, sUsername, nSequenceID, pReagent):
        # Load all of our reagents
        pReagents = self.GetSequenceReagentsInternal(sUsername, nSequenceID)

        # Locate the reagent of interest
        nReagentIndex = 0
        for pTargetReagent in pReagents:
            if pTargetReagent["reagentid"] == pReagent["reagentid"]:
                # The index points to this reagent
                break
            else:
                nReagentIndex += 1

        # Update the existing reagent
        if nReagentIndex < len(pReagents):
            pReagents[nReagentIndex]["available"] = pReagent["available"]
            pReagents[nReagentIndex]["name"] = pReagent["name"]
            pReagents[nReagentIndex]["description"] = pReagent["description"]
        else:
            raise Exception("Failed to find reagent")

        # Save the reagents
        self.SaveSequenceReagentsInternal(sUsername, pReagents)
        return True

    def GetRunState(self, sUsername):
        # Are we running?
        sSystemState = self.GetSystemState(sUsername)
        if sSystemState != "NONE":
            # Yes, so strip the user name
            sSystemState = sSystemState[len(sSystemState.split(".")[0]) + 1:]

        # Return the state
        return sSystemState

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
        return False

    def StartManualRun(self, sUsername):
        return False

    def PerformOperation(self, sUsername, nComponentID, nSequenceID):
        return False

    def AbortOperation(self, sUsername):
        return False

    def ContinueOperation(self, sUsername):
        return False

    def FinishManualRun(self, sUsername):
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

    def GetSequenceReagentsInternal(self, sUsername, nSequenceID):
        # Obtain a lock on the system
        self.LockSystem(sUsername)

        # Attempt to get the reagents from the file system
        try:
            pReagentsFile = os.open("/var/www/wsgi/" + sUsername + "/reagents.txt", os.O_RDWR)
            sReagents = os.read(pReagentsFile, 10000)
            os.close(pReagentsFile)
            pReagents = json.loads(sReagents)
        except OSError as e:
            # Check the error type
            if e.errno != errno.ENOENT:
                # An error other than file does not exist was encountered.  Release the system lock and raise again
                self.UnlockSystem(sUsername)
                raise
            else:
                # Reagents do not exist.  Default to the dummy reagents and create the file
                pReagents = DummyData.GetDefaultSequenceReagents()
                self.SaveSequenceReagentsInternal(sUsername, pReagents, False)

        # Release the system lock and return the list of reagents
        self.UnlockSystem(sUsername)
        return pReagents

    def SaveSequenceReagentsInternal(self, sUsername, pReagents, bLockSystem = True):
        # Obtain a lock on the system
        if bLockSystem:
            self.LockSystem(sUsername)

        # Open and write to the reagent file
        pReagentsFile = os.open("/var/www/wsgi/" + sUsername + "/reagents.txt", os.O_CREAT | os.O_TRUNC | os.O_RDWR)
        os.write(pReagentsFile, json.dumps(pReagents))
        os.close(pReagentsFile)

        # Release the system lock
        if bLockSystem:
            self.UnlockSystem(sUsername)
        return True

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

    def AddComponentDetails(self, sUsername, nSequenceID, pComponent):
        # Add component-specific details
        if pComponent["componenttype"] == "CASSETTE":
            pComponent.update({"name":"Cassette " + str(pComponent["id"])})
            pComponent.update({"reactordescription":"Reactor associated with this cassette"})
            pComponent.update({"reactorvalidation":"type=enum-literal; values=1,2,3; required=true"})
            pComponent.update({"validationerror":False})
        elif pComponent["componenttype"] == "ADD":
            pReagent = self.GetSequenceReagent(sUsername, nSequenceID, pComponent["reagent"])
            if pReagent["name"] != "[invalid]":
                pComponent.update({"name":"Add " + pReagent["name"]})
            else:
                pComponent.update({"name":"Add"})
            pComponent.update({"reactordescription":"Reactor where the reagent will be added"})
            pComponent.update({"reactorvalidation":"type=enum-literal; values=1,2,3; required=true"})
            pComponent.update({"reagentdescription":"Reagent to add to the reactor"})
            pComponent.update({"reagentvalidation":"type=enum-reagent; values=1,2,3,4,5,6,7,8; required=true"})
            pComponent.update({"validationerror":False})
        elif pComponent["componenttype"] == "EVAPORATE":
            pComponent.update({"name":"Evaporate"})
            pComponent.update({"reactordescription":"Reactor where the evaporation will be performed"})
            pComponent.update({"reactorvalidation":"type=enum-literal; values=1,2,3; required=true"})
            pComponent.update({"durationdescription":"Evaporation duration after the target temperature is reached"})
            pComponent.update({"durationvalidation":"type=time; min=00:00.00; max=02:00.00; required=true"})
            pComponent.update({"evaporationtemperaturedescription":"Reaction temperature in degrees Celsius"})
            pComponent.update({"evaporationtemperaturevalidation":"type=temperature; min=20; max=200; required=true"})
            pComponent.update({"finaltemperaturedescription":"Final temperature after evaporation in degrees Celsius"})
            pComponent.update({"finaltemperaturevalidation":"type=temperature; min=20; max=200; required=true"})
            pComponent.update({"stirspeeddescription":"Speed of the stir bar in rotations per minute"})
            pComponent.update({"stirespeedvalidation":"type=speed; min=0; max=5000; required=true"})
            pComponent.update({"validationerror":False})
        elif pComponent["componenttype"] == "TRANSFER":
            pComponent.update({"name":"Transfer"})
            pComponent.update({"reactordescription":"Reactor where the source reagent resides"})
            pComponent.update({"reactorvalidation":"type=enum-literal; values=1,2,3; required=true"})
            pComponent.update({"targetdescription":"Target where the reactor contents will be transferred"})
	    pComponent.update({"targetvalidation":"type=enum-target; values=9; required=true"})
            pComponent.update({"validationerror":False})
        elif pComponent["componenttype"] == "ELUTE":
            pComponent.update({"name":"Elute"})
            pComponent.update({"reactordescription":"Reactor where the reagent will be eluted"})
            pComponent.update({"reactorvalidation":"type=enum-literal; values=1,2,3; required=true"})
            pComponent.update({"reagentdescription":"Reagent used to elute the target"})
            pComponent.update({"reagentvalidation":"type=enum-reagent; values=1,2,3,4,5,6,7,8; required=true"})
            pComponent.update({"targetdescription":"Target to be eluted with the reagent"})
            pComponent.update({"targetvalidation":"type=enum-target; values=10; required=true"})
            pComponent.update({"validationerror":False})
        elif pComponent["componenttype"] == "REACT":
            pComponent.update({"name":"React"})
            pComponent.update({"reactordescription":"Reactor where the reaction will be performed"})
            pComponent.update({"reactorvalidation":"type=enum-literal; values=1,2,3; required=true"})
            pComponent.update({"positiondescription":"Position where the reaction will take place"})
            pComponent.update({"positionvalidation":"type=enum-literal; values=1,2; required=true"})
            pComponent.update({"durationdescription":"Evaporation duration after the target temperature is reached"})
            pComponent.update({"durationvalidation":"type=time; min=00:00.00; max=02:00.00; required=true"})
            pComponent.update({"reactiontemperaturedescription":"Reaction temperature in degrees Celsius"})
            pComponent.update({"reactiontemperaturevalidation":"type=temperature; min=20; max=200; required=true"})
            pComponent.update({"finaltemperaturedescription":"Final temperature after evaporation in degrees Celsius"})
            pComponent.update({"finaltemperaturevalidation":"type=temperature; min=20; max=200; required=true"})
            pComponent.update({"stirspeeddescription":"Speed of the stir bar in rotations per minute"})
            pComponent.update({"stirespeedvalidation":"type=speed; min=0; max=5000; required=true"})
            pComponent.update({"validationerror":False})
        elif pComponent["componenttype"] == "PROMPT":
            pComponent.update({"name":"Prompt"})
            pComponent.update({"reactordescription":""})
            pComponent.update({"reactorvalidation":""})
            pComponent.update({"messagedescription":"This will be displayed to the user"})
            pComponent.update({"messagevalidation":"type=string; required=true"})
            pComponent.update({"validationerror":False})
        elif pComponent["componenttype"] == "INSTALL":
            pComponent.update({"name":"Install"})
            pComponent.update({"reactordescription":"Reactor that will be moved to the install position"})
            pComponent.update({"reactorvalidation":"type=enum-literal; values=1,2,3; required=true"})
            pComponent.update({"messagedescription":"This will be displayed to the user"})
            pComponent.update({"messagevalidation":"type=string; required=true"})
            pComponent.update({"validationerror":False})
        elif pComponent["componenttype"] == "COMMENT":
            pComponent.update({"name":"Comment"})
            pComponent.update({"reactordescription":""})
            pComponent.update({"reactorvalidation":""})
            pComponent.update({"commentdescription":"Enter a comment"})
            pComponent.update({"commentvalidation":"type=string"})
            pComponent.update({"validationerror":False})
        elif pComponent["componenttype"] == "ACTIVITY":
            pComponent.update({"name":"Activity"})
            pComponent.update({"reactordescription":"Reactor where the radioactivity will be measures"})
            pComponent.update({"reactorvalidation":"type=enum-literal; values=1,2,3; required=true"})
            pComponent.update({"validationerror":False})

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

        # Extract the component specific part of the system state
        pSystemStateComponents = sSystemState.split(".")
        sUsername = pSystemStateComponents[0]
        sMode = pSystemStateComponents[1]
        nSequenceID = int(pSystemStateComponents[2])
        nComponentID = int(pSystemStateComponents[3])

        # Advance the system state
        if len(pSystemStateComponents) < 5:
            # State with an initial value of one
            nComponentState = 1
        else:
            nComponentState = int(pSystemStateComponents[4])
            if nComponentState < 7:
                # Increment our value
                nComponentState += 1
            else:
                # Attempt to advance to the next component
                pSequence = self.GetSequence(sUsername, nSequenceID)
                nIndex = 0
                bComponentFound = False
                nNextComponentID = None
                while nIndex < len(pSequence["components"]):
                    pComponent = pSequence["components"][nIndex]
                    if bComponentFound:
                        # This is the next component
                        nNextComponentID = pComponent["id"]
                        break
                    if pComponent["id"] == nComponentID:
                        # Found it
                        bComponentFound = True
                    nIndex += 1

                # Do we find the next component?
                if nNextComponentID == None:
                    # No, the run is complete so update the system and client states and return
                    self.SaveSystemState(sUsername, "NONE")
                    self.SaveClientState(sUsername, "HOME")
                    return

                # Set the component ID and state
                nComponentID = nNextComponentID
                nComponentState = 0

        # Save the system state and return
        sSystemState = sUsername + "." + sMode + "." + str(nSequenceID) + "." + str(nComponentID) + "." + str(nComponentState)
        self.SaveSystemState(sUsername, sSystemState)
        return

    def UpdateServerState(self, pServerState):
        return pServerState

    # Lock file
    m_pLockFile = 0
