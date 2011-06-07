#!/usr/bin/python26

# Imports
import sys
import os
import os.path
import time
import errno
import json
sys.path.append('/var/www/wsgi')
import DummyData

### Implementation of Elixys interface with dummy data ###

class Elixys:

    ### Interface functions ###

    def GetConfiguration(self):
        return {"name":"Mini cell 3",
            "version":"2.0",
            "debug":"false"}

    def GetSupportedOperations(self):
        return ["Add",
            "Evaporate",
            "Transfer",
            "Elute",
            "React",
            "Prompt",
            "Install",
            "Comment",
            "Activity"]

    def GetUserAccessLevels(self):
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
                # An error other than file does not exist was encountered.  Release the system local and raise again
                self.UnlockState()
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

    def GetServerState(self):
        return {}

    def GetSequenceList(self, sUsername, sType):
        # Load the sequence
        pSequence = self.GetSequenceInternal(sUsername, 1)

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
        # Get the sequence without the additional component information
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

    def SaveSequence(self, sUsername, pSequence, bLockSystem = True):
        # Obtain a lock on the system
        if bLockSystem:
            self.LockSystem(sUsername)

        # Open and write to the sequence file
        pSequenceFile = os.open("/var/www/wsgi/" + sUsername + "/sequence.txt", os.O_CREAT | os.O_TRUNC | os.O_RDWR)
        os.write(pSequenceFile, json.dumps(pSequence))
        os.close(pSequenceFile)

        # Release the system lock
        if bLockSystem:
            self.UnlockSystem(sUsername)
        return True

    def SaveSequenceComponent(self, sUsername, nSequenceID, pComponent, nInsertionID):
        # Load the sequence
        pSequence = self.GetSequenceInternal(sUsername, nSequenceID)

        # Locate the component
        nComponentIndex = 0
        for pSequenceComponent in pSequence["components"]:
            if pSequenceComponent["id"] == pComponent["id"]:
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
            self.UpdateComponent(pSequence["components"][nComponentIndex], pComponent)

            # Are we also moving the component?
            if nInsertionID != None:
                # Use nInsertionIndex
                raise Exception("Handle moving an existing component")
        else:
            # We are adding a new component.  Use the next number in the sequence for the component ID for now
            pComponent["id"] = len(pSequence["components"]) + 1

            # Are we inserting somewhere in the middle?
            if nInsertionIndex < len(pSequence["components"]):
                # Yes, so insert at the desired position
                print >> sys.stderr, "Inserting at index " + str(nInsertionIndex)
                pSequence["components"].insert(nInsertionIndex, self.RemoveComponentDetails(pComponent))
            else:
                # No, so append at the end of the sequence
                pSequence["components"].append(self.RemoveComponentDetails(pComponent))

        # Save the sequence
        self.SaveSequence(sUsername, pSequence)
        return True

    def DeleteSequence(self, nSequenceID):
        return False

    def DeleteSequenceComponent(self, nSequenceID, nComponentID):
        return False

    def CopySequence(self, nSequenceID, sName, sComment, sCreator):
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

    def RunSequence(self, nSequenceID):
        return False

    def AbortRun(self):
        return False

    def ContinueRun(self):
        return False

    def StartManualRun(self):
        return False

    def PerformOperation(self, nComponentID, nSequenceID):
        return False

    def AbortOperation(self):
        return False

    def ContinueOperation(self):
        return False

    def FinishManualRun(self):
        return False

    ### Internal functions ###

    def LockSystem(self, sUsername):
        # Create the user's state directory as needed
        if not os.path.exists("/var/www/wsgi/" + sUsername):
            os.makedirs("/var/www/wsgi/" + sUsername)

        # Loop until we acquire the lock
        nFailCount = 0
        while True:
            try:
                self.m_pLockFile = os.open("/var/www/wsgi/" + sUsername + "/lock.file", os.O_CREAT | os.O_EXCL | os.O_RDWR)
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
                    m_pLockFile = os.open("/var/www/wsgi/" + sUsername + "/lock.file", os.O_RDWR)
                    break

    def UnlockSystem(self, sUsername):
         # Release the lock
        os.close(self.m_pLockFile)
        os.unlink("/var/www/wsgi/" + sUsername + "/lock.file")

    def GetSequenceInternal(self, sUsername, nSequenceID):
        # Obtain a lock on the system
        self.LockSystem(sUsername)

        # Attempt to get the sequence from the file system
        try:
            pSequenceFile = os.open("/var/www/wsgi/" + sUsername + "/sequence.txt", os.O_RDWR)
            sSequence = os.read(pSequenceFile, 100000)
            os.close(pSequenceFile)
            pSequence = json.loads(sSequence)
        except OSError as e:
            # Check the error type
            if e.errno != errno.ENOENT:
                # An error other than file does not exist was encountered.  Release the system local and raise again
                self.UnlockState()
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
                # An error other than file does not exist was encountered.  Release the system local and raise again
                self.UnlockState()
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

    def AddComponentDetails(self, sUsername, nSequenceID, pComponent):
        # Add component-specific details
        if pComponent["componenttype"] == "CASSETTE":
            nComponentID = pComponent["id"]
            pComponent.update({"name":"Cassette " + str(nComponentID)})
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

    def UpdateComponent(self, pTargetComponent, pSourceComponent):
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
        elif pTargetComponent["componenttype"] == "EVAPORATE":
            pDesiredKeys = ["componenttype", "id", "reactor", "duration", "evaporationtemperature", "finaltemperature", "stirspeed"]
        elif pTargetComponent["componenttype"] == "TRANSFER":
            pDesiredKeys = ["componenttype", "id", "reactor", "target"]
        elif pTargetComponent["componenttype"] == "ELUTE":
            pDesiredKeys = ["componenttype", "id", "reactor", "reagent", "target"]
        elif pTargetComponent["componenttype"] == "REACT":
            pDesiredKeys = ["componenttype", "id", "reactor", "position", "duration", "reactiontemperature", "finaltemperature", "stirspeed"]
        elif pTargetComponent["componenttype"] == "PROMPT":
            pDesiredKeys = ["componenttype", "id", "reactor", "message"]
        elif pTargetComponent["componenttype"] == "INSTALL":
            pDesiredKeys = ["componenttype", "id", "reactor", "message"]
        elif pTargetComponent["componenttype"] == "COMMENT":
            pDesiredKeys = ["componenttype", "id", "reactor", "comment"]
        elif pTargetComponent["componenttype"] == "ACTIVITY":
            pDesiredKeys = ["componenttype", "id", "reactor"]

        # Remove the keys that we do not want to save
        if pDesiredKeys != None:
            pUnwantedKeys = set(pComponent) - set(pDesiredKeys)
            for pUnwantedKey in pUnwantedKeys:
                del pComponent[pUnwantedKey]
        return pComponent

    # Lock file
    m_pLockFile = 0
