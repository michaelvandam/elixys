#!/usr/bin/python26

# Imports
import sys
import os
import os.path
import time
import errno
sys.path.append('/var/www/wsgi')
import DummySequence

### Interface functions ###

def GetConfiguration():
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

def GetUserAccessLevels():
    return {}

def GetUser(sUsername):
    return {"username":sUsername,
        "useraccesslevel":"Administrator"}

def SaveUser(sUsername, sPassword, sAccesslevel):
    return False

def DeleteUser(sUsername):
    return False

def GetClientState():
    # Obtain a lock on the system
    LockSystem()

    # Attempt to get the client state from the file system
    try:
        pStateFile = os.open("/var/www/wsgi/state.txt", os.O_RDWR)
        sClientState = int(os.read(pStateFile, 99))
        os.close(pStateFile)
    except OSError as e:
        # Check the error type
        if e.errno != errno.ENOENT:
            # An error other than file does not exist was encountered.  Release the system local and raise again
            UnlockState()
            raise
        else:
            # Client state file does not exist.  Default to the home state and create the file
            sClientState = "HOME"
            SaveClientState(sClientState, False)

    # Release the system lock and return
    UnlockSystem()
    return sClientState

def SaveClientState(sClientState, bLockSystem = True):
    # Obtain a lock on the system
    if bLockSystem:
        LockSystem()

    # Open and write to the client state file
    pStateFile = os.open("/var/www/wsgi/state.txt", os.O_CREAT | os.O_TRUNC | os.O_RDWR)
    os.write(pStateFile, str(nState))
    os.close(pStateFile)

    # Release the system lock
    if bLockSystem:
        UnlockSystem()
    return True

def GetServerState():
    return {}

def GetSequenceList(sType):
    # Create 25 copies of our dummy sequence
    pSequenceMetadata = DummySequence.GetDefaultSequenceMetadata()
    pSequences = []
    for x in range(0, 25):
        pSequence = pSequenceMetadata.copy()
        pSequence["name"] += " (" + str(x) + ")"
        pSequence["comment"] += " (" + str(x) + ")"
        pSequence["id"] += x
        pSequences.append(pSequence)
    return pSequences

def GetSequence(nSequenceID, nComponentID):
    # Create the sequence response
    pSequence = {"metadata":DummySequence.GetDefaultSequenceMetadata(),
        "components":[]}
    for pComponent in DummySequence.GetDefaultSequenceComponents():
        if ((nComponentID != 0) and (pComponent["id"] == nComponentID):
            pSequence["components"].append(pComponent)
            return pSequence
        else:
            pSequence["components"].append(pComponent)
    if (nComponentID != 0):
        raise Exception("Failed to locate component")
    return pSequence

def SaveSequence(nSequenceID, sType, sName, sComment, sCreator):
    return False

def SaveSequenceComponent(nSequenceID, sType, nComponentID, sReactor, pAdditionalDetails):
    return False

def DeleteSequence(nSequenceID):
    return False

def DeleteSequenceComponent(nSequenceID, nComponentID):
    return False

def CopySequence(nSequenceID, sName, sComment, sCreator):
    return False

def GetReagent(nSequenceID, nReagentID):
    # Locate the reagent of interest
    pReagent = {"type":"reagent"}
    for pSequenceReagent in DummySequence.GetDefaultSequenceReagents():
        if pSequenceReagent["reagentid"] == nReagentID:
            pReagent.update(pSequenceReagent)
            return pReagent
    raise Exception("Failed to find reagent")

def SaveReagent(nReagentID, nComponentID, nSequenceID, bAvailable, nPosition, sName, sDescription):
    return False

def RunSequence(nSequenceID):
    return False

def AbortRun():
    return False

def ContinueRun():
    return False

def StartManualRun():
    return False

def PerformOperation(nComponentID, nSequenceID):
    return False

def AbortOperation():
    return False

def ContinueOperation():
    return False

def FinishManualRun():
    return False

### Internal functions ###

def LockSystem():
    # Loop until we acquire the lock
    global pLockFile
    nFailCount = 0
    while True:
        try:
            pLockFile = os.open("/var/www/wsgi/lock.file", os.O_CREAT | os.O_EXCL | os.O_RDWR)
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
                pLockFile = os.open("/var/www/wsgi/lock.file", os.O_RDWR)
                break

def UnlockState():
     # Release the lock
    global pLockFile
    os.close(pLockFile)
    os.unlink("/var/www/wsgi/lock.file")


### Functions to be ported ###

def LoadComponentID():
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

def SaveComponentID(nComponentID):
    # Open the component file
    pComponentFile = os.open("/var/www/wsgi/component.txt", os.O_CREAT | os.O_TRUNC | os.O_RDWR)

    # Write the component
    os.write(pComponentFile, str(nComponentID))
    os.close(pComponentFile)

