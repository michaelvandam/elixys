#!/usr/bin/python26

# Imports
import sys
import os
import os.path
import time
import errno
sys.path.append('/var/www/wsgi')
import DummyData

### Implementation of Elixys interface with dummy data ###

class Elixys:

    ### Interface functions ###

    def GetConfiguration(self):
        return {"name":"Mini cell 3",
            "version":"2.0",
            "debug":"false",
            "supportedoperations":
                ["Add",
                "Evaporate",
                "Transfer",
                "Elute",
                "React",
                "Prompt",
                "Install",
                "Comment",
                "Activity"]}

    def GetUserAccessLevels(self):
        return {}

    def GetUser(self, sUsername):
        return {"username":sUsername,
            "useraccesslevel":"Administrator"}

    def SaveUser(self, sUsername, sPassword, sAccesslevel):
        return False

    def DeleteUser(self, sUsername):
        return False

    def GetClientState(self):
        # Obtain a lock on the system
        self.LockSystem()

        # Attempt to get the client state from the file system
        try:
            pStateFile = os.open("/var/www/wsgi/state.txt", os.O_RDWR)
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
                self.SaveClientState(sClientState, False)

        # Release the system lock and return
        self.UnlockSystem()
        return sClientState

    def SaveClientState(self, sClientState, bLockSystem = True):
        # Obtain a lock on the system
        if bLockSystem:
            self.LockSystem()

        # Open and write to the client state file
        pStateFile = os.open("/var/www/wsgi/state.txt", os.O_CREAT | os.O_TRUNC | os.O_RDWR)
        os.write(pStateFile, str(sClientState))
        os.close(pStateFile)

        # Release the system lock
        if bLockSystem:
            self.UnlockSystem()
        return True

    def GetServerState(self):
        return {}

    def GetSequenceList(self, sType):
        # Create 25 copies of our dummy sequence
        pSequenceMetadata = DummyData.GetDefaultSequenceMetadata()
        pSequences = []
        for x in range(0, 25):
            pSequence = pSequenceMetadata.copy()
            pSequence["name"] += " (" + str(x) + ")"
            pSequence["comment"] += " (" + str(x) + ")"
            pSequence["id"] += x
            pSequences.append(pSequence)
        return pSequences

    def GetSequence(self, nSequenceID, nComponentID = 0):
        # Create the sequence response
        pSequence = {"metadata":DummyData.GetDefaultSequenceMetadata(),
            "components":[]}
        for pComponent in DummyData.GetDefaultSequenceComponents():
            if nComponentID != 0:
                if pComponent["id"] == nComponentID:
                    pSequence["components"].append(pComponent)
                    return pSequence
            else:
                pSequence["components"].append(pComponent)
        if (nComponentID != 0):
            raise Exception("Failed to locate component")
        return pSequence

    def SaveSequence(self, nSequenceID, sType, sName, sComment, sCreator):
        return False

    def SaveSequenceComponent(self, nSequenceID, sType, nComponentID, sReactor, pAdditionalDetails):
        return False

    def DeleteSequence(self, nSequenceID):
        return False

    def DeleteSequenceComponent(self, nSequenceID, nComponentID):
        return False

    def CopySequence(self, nSequenceID, sName, sComment, sCreator):
        return False

    def GetReagent(self, nSequenceID, nReagentID):
        # Locate the reagent of interest
        pReagent = {"type":"reagent"}
        for pSequenceReagent in DummyData.GetDefaultSequenceReagents():
            if pSequenceReagent["reagentid"] == nReagentID:
                pReagent.update(pSequenceReagent)
                return pReagent
        raise Exception("Failed to find reagent")

    def SaveReagent(self, nReagentID, nComponentID, nSequenceID, bAvailable, nPosition, sName, sDescription):
        return False

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

    def LockSystem(self):
        # Loop until we acquire the lock
        nFailCount = 0
        while True:
            try:
                self.m_pLockFile = os.open("/var/www/wsgi/lock.file", os.O_CREAT | os.O_EXCL | os.O_RDWR)
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
                    m_pLockFile = os.open("/var/www/wsgi/lock.file", os.O_RDWR)
                    break

    def UnlockSystem(self):
         # Release the lock
        os.close(self.m_pLockFile)
        os.unlink("/var/www/wsgi/lock.file")

    # Lock file
    m_pLockFile = 0

    ### Functions to be ported ###

    def LoadComponentID(self):
        # Attempt to open the component file
        try:
            # Open the component file
            pComponentFile = os.open("/var/www/wsgi/component.txt", os.O_RDWR)

            # Read in the component ID
            nComponentID = int(os.read(pComponentFile, 99))
            os.close(pComponentFile)

            # Return the component ID
            return nComponentID
        except OSError as e:
            # Check for errors other than a nonexistant component file
            if e.errno != errno.ENOENT:
                raise

            # Default to the first component ID
            return 1

    def SaveComponentID(self, nComponentID):
        # Open the component file
        pComponentFile = os.open("/var/www/wsgi/component.txt", os.O_CREAT | os.O_TRUNC | os.O_RDWR)

        # Write the component
        os.write(pComponentFile, str(nComponentID))
        os.close(pComponentFile)

