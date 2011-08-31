#!/usr/bin/python

# Imports
from wsgiref.simple_server import make_server
import json
from wsgiref.headers import Headers
import sys
sys.path.append("/opt/elixys/core")
sys.path.append("/opt/elixys/database")

# Change the python egg cache directory to a place where Apache has write permission
import os
os.environ["PYTHON_EGG_CACHE"] = "/var/www/wsgi"

# Import and create the database connection
import DBComm
gDatabase = DBComm.DBComm()

# Import and create the core Elixys server
from DummyElixys import Elixys 
gElixys = Elixys()
gElixys.SetDatabase(gDatabase)

### Logging function

def Log(sMessage):
    print >> sys.stderr, sMessage

### GET handler functions ###

# Handle all GET requests
def HandleGet(sClientState, sRemoteUser, sPath):
    if sPath == "/configuration":
        return HandleGetConfiguration(sRemoteUser)
    if sPath == "/state":
        return HandleGetState(sClientState, sRemoteUser)
    if sPath.startswith("/sequence/"):
        if sPath.find("/component/") != -1:
            return HandleGetComponent(sRemoteUser, sPath)
        elif sPath.find("/reagent/") != -1:
            return HandleGetReagent(sRemoteUser, sPath)
        else:
            return HandleGetSequence(sRemoteUser, sPath)
    else:
        raise Exception("Unknown path: " + sPath)

# Handle GET /configuration
def HandleGetConfiguration(sRemoteUser):
    global gElixys
    pConfig = {"type":"configuration"}
    pConfig.update(gElixys.GetConfiguration(sRemoteUser))
    pConfig.update({"supportedoperations":gElixys.GetSupportedOperations(sRemoteUser)})
    return pConfig

# Handle GET /state request
def HandleGetState(sClientState, sRemoteUser):
    # Is the remote user the one that is currently running the system?
    global gElixys
    global gDatabase
    if sRemoteUser == gElixys.GetRunUser(sRemoteUser):
        # Yes, so make sure the user is in the appropriate run state
        sRunState = gElixys.GetRunState(sRemoteUser)
        if sRunState.startswith("RUNSEQUENCE") and not sClientState.startswith("RUNSEQUENCE") and not sClientState.startswith("PROMPT"):
            pRunStateComponents = sRunState.split(".")
            sClientState = "RUNSEQUENCE." + pRunStateComponents[1] + "." + pRunStateComponents[2]
            gDatabase.UpdateUserClientState(sRemoteUser, sRemoteUser, sClientState)
        elif sRunState.startswith("RUNMANUAL") and not sClientState.startswith("RUNMANUAL") and not sClientState.startswith("PROMPT"):
            pRunStateComponents = sRunState.split(".")
            sClientState = "RUNMANUAL." + pRunStateComponents[1] + "." + pRunStateComponents[2]
            gDatabase.UpdateUserClientState(sRemoteUser, sRemoteUser, sClientState)

    # Get the user information and server state
    pUser = {"type":"user"}
    pUser.update(gElixys.GetUser(sRemoteUser))
    pServerState = {"type":"serverstate"}
    pServerState.update(gElixys.GetServerState(sRemoteUser))

    # Update the full client state because GetServerState() may have changed it
    sClientState = gDatabase.GetUserClientState(sRemoteUser, sRemoteUser)

    # Get the full client state and break it into prompt and client components
    pPromptStateComponent = GetPromptStateComponent(sClientState, sRemoteUser)
    sClientStateComponent = GetClientStateComponent(sClientState)

    # Start the state with the common fields
    pServerState.update(pServerState)
    pState = {"type":"state",
        "user":pUser,
        "serverstate":pServerState,
        "promptstate":pPromptStateComponent,
        "clientstate":sClientStateComponent}

    # Complete the state with the values specific to this page
    if sClientStateComponent.startswith("HOME"):
        pState.update(HandleGetStateHome(sRemoteUser))
    elif sClientStateComponent.startswith("SELECT_SAVEDSEQUENCES"):
        pState.update(HandleGetStateSelectSavedSequences(sRemoteUser))
    elif sClientStateComponent.startswith("SELECT_MANUALRUNS"):
        pState.update(HandleGetStateSelectManualRuns(sRemoteUser))
    elif sClientStateComponent.startswith("VIEW"):
        pState.update(HandleGetStateView(sClientStateComponent, sRemoteUser))
    elif sClientStateComponent.startswith("EDIT"):
        pState.update(HandleGetStateEdit(sClientStateComponent, sRemoteUser))
    elif sClientStateComponent.startswith("RUNSEQUENCE"):
        pState.update(HandleGetStateRunSequence(sClientStateComponent, sRemoteUser))
    elif sClientStateComponent.startswith("MANUALRUN"):
        pState.update(HandleGetStateManualRun(sClientStateComponent, sRemoteUser))
    else:
        raise Exception("Unknown state: " + sClientStateComponent)

    # Return the state
    return pState

# Returns the prompt state component from the full client state
def GetPromptStateComponent(sClientState, sRemoteUser):
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
    if not sClientState.startswith("PROMPT_"):
        return pPromptState

    # Fill in the prompt state with prompt-specific details
    if sClientState.startswith("PROMPT_CREATESEQUENCE"):
        return HandleGetStateSelectPromptCreateSequence(pPromptState)
    elif sClientState.startswith("PROMPT_COPYSEQUENCE"):
        return HandleGetStateSelectPromptCopySequence(pPromptState)
    elif sClientState.startswith("PROMPT_DELETESEQUENCE"):
        return HandleGetStateSelectPromptDeleteSequence(pPromptState)
    elif sClientState.startswith("PROMPT_RUNSEQUENCE"):
        return HandleGetStatePromptRunSequence(pPromptState)
    elif sClientState.startswith("PROMPT_MANUALRUN"):
        return HandleGetStatePromptManualRun(pPromptState)
    elif sClientState.startswith("PROMPT_ABORTSEQUENCERUN"):
        return HandleGetStateRunSequencePromptAbort(pPromptState)
    elif sClientState.startswith("PROMPT_UNITOPERATION"):
        return HandleGetStateRunSequencePromptUnitOperation(pPromptState, sClientState, sRemoteUser)
    elif sClientState.startswith("PROMPT_ABORTMANUALRUN"):
        return HandleGetStateManualRunPromptAbortRun(pPromptState)
    elif sClientState.startswith("PROMPT_ABORTMANUALOPERATION"):
        return HandleGetStateManualRunPromptAbortOperation(pPromptState)
    elif sClientState.startswith("PROMPT_COMPLETEMANUALRUN"):
        return HandleGetStateManualRunPromptComplete(pPromptState)
    else:
        raise Exception("Unknown prompt state")

# Returns the client state component of the full client state
def GetClientStateComponent(sClientState):
    # Are we in prompt mode?
    if sClientState.startswith("PROMPT_"):
        # Yes, so the client state is the last component delimited by a semicolon
        pClientStateComponents = sClientState.split(";")
        return pClientStateComponents[len(pClientStateComponents) - 1]
    else:
        # No, so return the client state as it is
        return sClientState

# Handles GET /state request for Home
def HandleGetStateHome(sRemoteUser):
    # Start with the common buttons
    global gElixys
    pState = {"buttons":[{"type":"button",
        "text":"Create, view or run a sequence",
        "id":"CREATE"}]}

    # Is someone running the system?
    if gElixys.GetRunState(sRemoteUser) == "NONE":
        # No, so add the manual run button
        pState["buttons"].append({"type":"button",
            "text":"Operate the system manually",
            "id":"MANUAL"})
    else:
        # Yes, so add the observe button
        pState["buttons"].append({"type":"button",
            "text":"Observe the current run by " + gElixys.GetRunUser(sRemoteUser),
            "id":"OBSERVE"})

    # Return the state
    return pState

# Handles GET /state for Select Sequence (both tabs)
def HandleGetStateSelect(sRemoteUser):
    # Start with the common state
    global gElixys
    pState = {"tabs":[{"type":"tab",
            "text":"Saved Sequences",
            "id":"SAVEDSEQUENCES",
            "columns":["name:Name", "comment:Comment"]},
            {"type":"tab",
            "text":"Manual Runs",
            "id":"MANUALRUNS",
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
    if gElixys.GetRunState(sRemoteUser) == "NONE":
        pState["optionbuttons"].insert(1, {"type":"button",
            "text":"Run",
            "id":"RUN"})
    return pState

# Handle GET /state for Select Sequence (Saved Sequences tab)
def HandleGetStateSelectSavedSequences(sRemoteUser):
    global gDatabase
    pState = HandleGetStateSelect(sRemoteUser)
    pState.update({"tabid":"SAVEDSEQUENCES"})
    pState["optionbuttons"].append({"type":"button",
        "text":"Edit",
        "id":"EDIT"})
    pState["optionbuttons"].append({"type":"button",
        "text":"Delete",
        "id":"DELETE"})
    pState.update({"sequences":gDatabase.GetAllSequences(sRemoteUser, "Saved")})
    return pState

# Handle GET /state for Select Sequence (Manual Runs tab)
def HandleGetStateSelectManualRuns(sRemoteUser):
    global gDatabase
    pState = HandleGetStateSelect(sRemoteUser)
    pState.update({"tabid":"MANUALRUNS"})
    pState.update({"sequences":gDatabase.GetAllSequences(sRemoteUser, "Manual")})
    return pState

# Handle GET /state for View Sequence
def HandleGetStateView(sClientState, sRemoteUser):
    # Split the state and extract the sequence ID
    global gElixys
    global gDatabase
    pClientStateComponents = sClientState.split(".")
    nSequenceID = int(pClientStateComponents[1])

    # Do we have a component ID?
    if (len(pClientStateComponents) > 2):
        # Yes, so extract it
        nComponentID = int(pClientStateComponents[2])
    else:
        # No, the component ID is missing.  Get the sequence and the ID of the first component
        pSequence = GetSequence(sRemoteUser, nSequenceID)
        nComponentID = pSequence["components"][0]["id"]

        # Update our state
        sClientState = "VIEW." + str(nSequenceID) + "." + str(nComponentID)
        gDatabase.UpdateUserClientState(sRemoteUser, sRemoteUser, sClientState)

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
    if gElixys.GetRunState(sRemoteUser) == "NONE":
        pState["navigationbuttons"].insert(1, {"type":"button",
            "text":"Run",
            "id":"RUN"})
    return pState

# Handle GET /state for Edit Sequence
def HandleGetStateEdit(sClientState, sRemoteUser):
    # Split the state and extract the sequence ID
    global gElixys
    global gDatabase
    pClientStateComponents = sClientState.split(".")
    nSequenceID = int(pClientStateComponents[1])

    # Do we have a component ID?
    if (len(pClientStateComponents) > 2):
        # Yes, so extract it
        nComponentID = int(pClientStateComponents[2])
    else:
        # No, the component ID is missing.  Get the sequence and the ID of the first component
        pSequence = GetSequence(sRemoteUser, nSequenceID)
        nComponentID = pSequence["components"][0]["id"]

        # Update our state
        sClientState = "EDIT." + str(nSequenceID) + "." + str(nComponentID)
        gDatabase.UpdateUserClientState(sRemoteUser, sRemoteUser, sClientState)

    # Start with the common return object
    pState = {"navigationbuttons":[{"type":"button",
            "text":"Back",
            "id":"BACK"}],
        "sequenceid":nSequenceID,
        "componentid":nComponentID}

    # Add the run button if no one is running the system
    if gElixys.GetRunState(sRemoteUser) == "NONE":
        pState["navigationbuttons"].insert(0, {"type":"button",
            "text":"Run",
            "id":"RUN"})
    return pState

# Handle GET /state for Run Sequence
def HandleGetStateRunSequence(sClientState, sRemoteUser):
    # Get the run state and extract the sequence and component IDs
    global gElixys
    sRunState = gElixys.GetRunState(sRemoteUser)
    pRunStateComponents = sRunState.split(".")
    nSequenceID = int(pRunStateComponents[1])
    nComponentID = int(pRunStateComponents[2])

    # Create the return object
    pState = {"navigationbuttons":[],
        "sequenceid":nSequenceID,
        "componentid":nComponentID}

    # Add the button depending on the user running the system
    if sRemoteUser == gElixys.GetRunUser(sRemoteUser):
        pState["navigationbuttons"].append({"type":"button",
            "text":"Abort",
            "id":"ABORT"})
    else:
        pState["navigationbuttons"].append({"type":"button",
            "text":"Back",
            "id":"BACK"})

    # Return the state
    return pState

# Handle GET /state for Manual Run
def HandleGetStateManualRun(sClientState, sRemoteUser):
    # Get the run state and extract the sequence and component IDs and manual run step
    global gElixys
    sRunState = gElixys.GetRunState(sRemoteUser)
    pRunStateComponents = sRunState.split(".")
    nSequenceID = int(pRunStateComponents[1])
    nComponentID = int(pRunStateComponents[2])
    sManualRunStep = pRunStateComponents[3]

    # Create the return object
    pState = {"manualrunstep":sManualRunStep,
        "navigationbuttons":[],
        "sequenceid":nSequenceID,
        "componentid":nComponentID,
        "operationresult":True}

    # Add the button depending on the user running the system and the manual run step
    if sRemoteUser == gElixys.GetRunUser(sRemoteUser):
        if sManualRunStep == "CASSETTE":
            pState["navigationbuttons"].append({"type":"button",
                "text":"Abort",
                "id":"ABORT"})
            pState["navigationbuttons"].append({"type":"button",
                "text":"Start Run",
                "id":"START"})
        elif sManualRunStep == "SELECT":
            pState["navigationbuttons"].append({"type":"button",
                "text":"Complete",
                "id":"COMPLETE"})
        elif sManualRunStep == "CONFIGURE":
            pState["navigationbuttons"].append({"type":"button",
                "text":"Back",
                "id":"BACK"})
            pState["navigationbuttons"].append({"type":"button",
                "text":"Run",
                "id":"RUN"})
        elif sManualRunStep == "RUN":
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
def HandleGetStateSelectPromptCreateSequence(pPromptState):
    pPromptState["show"] = True
    pPromptState["title"] = "Create new sequence"
    pPromptState["text1"] = "Enter the name of the new sequence:"
    pPromptState["edit1"] = True
    pPromptState["edit1validation"] = "type=string; required=true"
    pPromptState["buttons"].append({"type":"button",
        "text":"Cancel",
        "id":"CANCEL"})
    pPromptState["buttons"].append({"type":"button",
        "text":"Create",
        "id":"CREATE"})
    return pPromptState

# Handle GET /state for Select Sequence (Copy Sequence prompt)
def HandleGetStateSelectPromptCopySequence(pPromptState):
    pPromptState["show"] = True
    pPromptState["title"] = "Copy sequence"
    pPromptState["text1"] = "Enter the name of the new sequence:"
    pPromptState["edit1"] = True
    pPromptState["edit1validation"] = "type=string; required=true"
    pPromptState["buttons"].append({"type":"button",
        "text":"Cancel",
        "id":"CANCEL"})
    pPromptState["buttons"].append({"type":"button",
        "text":"Copy",
        "id":"COPY"})
    return pPromptState

# Handle GET /state for Select Sequence (Delete Sequence prompt)
def HandleGetStateSelectPromptDeleteSequence(pPromptState):
    pPromptState["show"] = True
    pPromptState["title"] = "Delete sequence"
    pPromptState["text1"] = "Are you sure that you want to permanently delete sequence \"Fake Sequence Name Here\"?"
    pPromptState["buttons"].append({"type":"button",
        "text":"Cancel",
        "id":"CANCEL"})
    pPromptState["buttons"].append({"type":"button",
        "text":"Delete",
        "id":"DELETE"})
    return pPromptState

# Handle GET /state for Run Sequence prompt
def HandleGetStatePromptRunSequence(pPromptState):
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

# Handle GET /state for Home (Manual Run prompt)
def HandleGetStatePromptManualRun(pPromptState):
    pPromptState["show"] = True
    pPromptState["title"] = "Manual run"
    pPromptState["text1"] = "Prepare the Elixys system for the manual run and click OK to continue."
    pPromptState["buttons"].append({"type":"button",
        "text":"Cancel",
        "id":"CANCEL"})
    pPromptState["buttons"].append({"type":"button",
        "text":"OK",
        "id":"OK"})
    return pPromptState

# Handle GET /state for Run Sequence (Abort prompt)
def HandleGetStateRunSequencePromptAbort(pPromptState):
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
def HandleGetStateRunSequencePromptUnitOperation(pPromptState, sClientState, sRemoteUser):
    # Look up the current sequence component
    global gElixys
    global gDatabase
    sRunState = gElixys.GetRunState(sRemoteUser)
    pRunStateComponents = sRunState.split(".")
    nSequenceID = int(pRunStateComponents[1])
    nComponentID = int(pRunStateComponents[2])
    pComponent = GetComponent(sRemoteUser, nComponentID)

    # Make sure this component requires a prompt
    if (pComponent["componenttype"] != "PROMPT") and (pComponent["componenttype"] != "INSTALL"):
        # No, so update the client state and return
        sClientState = gElixys.GetRunState(sRemoteUser)
        gDatabase.UpdateUserClientState(sRemoteUser, sRemoteUser, sClientState)
        return pPromptState

    # Set the prompt message
    pPromptState["show"] = True
    pPromptState["title"] = "Prompt"
    pPromptState["text1"] = pComponent["message"]

    # Set the button text depending on whether we are the user running the system
    if sRemoteUser == gElixys.GetRunUser(sRemoteUser):
        pPromptState["buttons"].append({"type":"button",
            "text":"OK",
            "id":"OK"})
    else:
        pPromptState["buttons"].append({"type":"button",
            "text":"Back",
            "id":"BACK"})

    # Return the state
    return pPromptState

# Handle GET /state for Manual Run (Abort run prompt)
def HandleGetStateManualRunPromptAbortRun(pPromptState):
    pPromptState["show"] = True
    pPromptState["title"] = "Abort manual run"
    pPromptState["text1"] = "Are you sure you want to abort the manual run?  This operation cannot be undone."
    pPromptState["buttons"].append({"type":"button",
        "text":"Cancel",
        "id":"CANCEL"})
    pPromptState["buttons"].append({"type":"button",
        "text":"Abort",
        "id":"ABORT"})
    return pPromptState

# Handle GET /state for Manual Run (Abort operation prompt)
def HandleGetStateManualRunPromptAbortOperation(pPromptState):
    pPromptState["show"] = True
    pPromptState["title"] = "Abort operation"
    pPromptState["text1"] = "Are you sure you want to abort the current operation?  This cannot be undone."
    pPromptState["buttons"].append({"type":"button",
        "text":"Cancel",
        "id":"CANCEL"})
    pPromptState["buttons"].append({"type":"button",
        "text":"Abort",
        "id":"ABORT"})
    return pPromptState

# Handle GET /state for Manual Run (Complete prompt)
def HandleGetStateManualRunPromptComplete(pPromptState):
    pPromptState["show"] = True
    pPromptState["title"] = "Complete manual run"
    pPromptState["text1"] = "Enter a brief comment to describes this manual run:"
    pPromptState["edit1"] = True
    pPromptState["edit1validation"] = "type=string; required=true"
    pPromptState["text2"] = "Specify a sequence name if you would like to add this run to your saved sequences:"
    pPromptState["edit2"] = True
    pPromptState["edit2validation"] = "type=string; required=false"
    pPromptState["buttons"].append({"type":"button",
        "text":"Cancel",
        "id":"CANCEL"})
    pPromptState["buttons"].append({"type":"button",
        "text":"Save",
        "id":"SAVE"})
    return pPromptState

# Handle GET /sequence/[sequenceid]
def HandleGetSequence(sRemoteUser, sPath):
    # Extract sequence ID
    global gElixys
    pPathComponents = sPath.split("/")
    nSequenceID = int(pPathComponents[2])

    # Load the entire sequence
    pSequence = {"type":"sequence"}
    pSequence.update(GetSequence(sRemoteUser, nSequenceID))

    # Remove excess sequence data
    pNewComponents = []
    for pOldComponent in pSequence["components"]:
        pNewComponent = {"type":"sequencecomponent",
            "name":pOldComponent["name"],
            "id":pOldComponent["id"],
            "componenttype":pOldComponent["componenttype"],
            "validationerror":pOldComponent["validationerror"]}
        pNewComponents.append(pNewComponent)
    pSequence["components"] = pNewComponents

    # Return cleanedd sequence
    return pSequence

# Handle GET /sequence/[sequenceid]/component/[componentid]
def HandleGetComponent(sRemoteUser, sPath):
    # Extract sequence and component IDs
    pPathComponents = sPath.split("/")
    nComponentID = int(pPathComponents[4])

    # Return the desired component
    return GetComponent(sRemoteUser, nComponentID)

# Handle GET /sequence/[sequenceid]/reagent/[reagentid]
def HandleGetReagent(sRemoteUser, sPath):
    # Extract sequence and reagent IDs
    global gDatabase
    pPathComponents = sPath.split("/")
    nSequenceID = int(pPathComponents[2])
    nReagentID = int(pPathComponents[4])

    # Return the sequence reagent
    return gDatabase.GetReagent(sRemoteUser, nReagentID)

### POST handler functions ###

# Handle all POST requests
def HandlePost(sClientState, sRemoteUser, sPath, pBody, nBodyLength):
    # Handle based on the path
    if sPath == "/HOME":
        return HandlePostHome(sClientState, sRemoteUser, pBody, nBodyLength)
    elif sPath == "/SELECT":
        return HandlePostSelect(sClientState, sRemoteUser, pBody, nBodyLength)
    elif sPath == "/VIEW":
        return HandlePostView(sClientState, sRemoteUser, pBody, nBodyLength)
    elif sPath == "/EDIT":
        return HandlePostEdit(sClientState, sRemoteUser, pBody, nBodyLength)
    elif sPath == "/RUNSEQUENCE":
        return HandlePostRunSequence(sClientState, sRemoteUser, pBody, nBodyLength)
    elif sPath == "/MANUALRUN":
        return HandlePostManualRun(sClientState, sRemoteUser, pBody, nBodyLength)
    elif sPath == "/PROMPT":
        return HandlePostPrompt(sClientState, sRemoteUser, pBody, nBodyLength)
    elif sPath.startswith("/sequence/"):
        if sPath.find("/component/") != -1:
            return HandlePostComponent(sClientState, sRemoteUser, pBody, nBodyLength, sPath)
        elif sPath.find("/reagent/") != -1:
            return HandlePostReagent(sClientState, sRemoteUser, pBody, nBodyLength, sPath)
        else:
            return HandlePostSequence(sClientState, sRemoteUser, pBody, nBodyLength, sPath)

    # Unhandled use case
    raise Exception("Unknown path: " + sPath)

# Handle POST /HOME
def HandlePostHome(sClientState, sRemoteUser, pBody, nBodyLength):
    # Make sure we are on the home page
    global gElixys
    global gDatabase
    if sClientState.startswith("HOME") == False:
        raise Exception("State misalignment");

    # Parse the JSON string in the body
    pJSON = json.loads(pBody)

    # Check which option the user selected
    sActionType = str(pJSON["action"]["type"])
    sActionTargetID = str(pJSON["action"]["targetid"])
    if sActionType == "BUTTONCLICK":
        if sActionTargetID == "CREATE":
            # Switch states to Select Sequence
            sClientState = "SELECT_SAVEDSEQUENCES"
            gDatabase.UpdateUserClientState(sRemoteUser, sRemoteUser, sClientState)
            return HandleGet(sClientState, sRemoteUser, "/state")
        elif sActionTargetID == "MANUAL":
            # Switch states to Prompt (Manual Run)
            sClientState = "PROMPT_MANUALRUN;" + sClientState
            gDatabase.UpdateUserClientState(sRemoteUser, sRemoteUser, sClientState)
            return HandleGet(sClientState, sRemoteUser, "/state")
        elif sActionTargetID == "OBSERVE":
            # Swtich to Run Sequence
            sClientState = gElixys.GetRunState(sRemoteUser)
            gDatabase.UpdateUserClientState(sRemoteUser, sRemoteUser, sClientState)
            return HandleGet(sClientState, sRemoteUser, "/state")

    # Unhandled use case
    raise Exception("State misalignment")

# Handle POST /SELECT
def HandlePostSelect(sClientState, sRemoteUser, pBody, nBodyLength):
    # Make sure we are on Select Sequence
    global gElixys
    global gDatabase
    if sClientState.startswith("SELECT") == False:
        raise Exception("State misalignment");

    # Parse the JSON string in the body
    pJSON = json.loads(pBody)

    # Check which option the user selected
    sActionType = str(pJSON["action"]["type"])
    sActionTargetID = str(pJSON["action"]["targetid"])
    nSequenceID = pJSON["sequenceid"]
    if sActionType == "BUTTONCLICK":
        if sActionTargetID == "VIEW":
            # Switch states to View Sequence
            sClientState = "VIEW." + str(nSequenceID)
            gDatabase.UpdateUserClientState(sRemoteUser, sRemoteUser, sClientState)
            return HandleGet(sClientState, sRemoteUser, "/state")
        elif sActionTargetID == "EDIT":
            # Switch states to Edit Sequence
            sClientState = "EDIT." + str(nSequenceID)
            gDatabase.UpdateUserClientState(sRemoteUser, sRemoteUser, sClientState)
            return HandleGet(sClientState, sRemoteUser, "/state")
        elif sActionTargetID == "RUN":
            # Switch states to Prompt (Run Sequence)
            sClientState = "PROMPT_RUNSEQUENCE;" + str(nSequenceID) + ";" + sClientState
            gDatabase.UpdateUserClientState(sRemoteUser, sRemoteUser, sClientState)
            return HandleGet(sClientState, sRemoteUser, "/state")
        elif sActionTargetID == "BACK":
            # Switch states to Home
            sClientState = "HOME"
            gDatabase.UpdateUserClientState(sRemoteUser, sRemoteUser, sClientState)
            return HandleGet(sClientState, sRemoteUser, "/state")
        elif sActionTargetID == "CREATE":
            # Switch states to Prompt (Create Sequence)
            sClientState = "PROMPT_CREATESEQUENCE;" + sClientState
            gDatabase.UpdateUserClientState(sRemoteUser, sRemoteUser, sClientState)
            return HandleGet(sClientState, sRemoteUser, "/state")
        elif sActionTargetID == "COPY":
            # Switch states to Prompt (Copy Sequence)
            sClientState = "PROMPT_COPYSEQUENCE;" + sClientState
            gDatabase.UpdateUserClientState(sRemoteUser, sRemoteUser, sClientState)
            return HandleGet(sClientState, sRemoteUser, "/state")
        elif sActionTargetID == "DELETE":
            # Switch states to Prompt (Delete Sequence)
            sClientState = "PROMPT_DELETESEQUENCE;" + sClientState
            gDatabase.UpdateUserClientState(sRemoteUser, sRemoteUser, sClientState)
            return HandleGet(sClientState, sRemoteUser, "/state")
    elif sActionType == "TABCLICK":
        if sActionTargetID == "SAVEDSEQUENCES":
            # Switch states to the Saved Sequences tab
            sClientState = "SELECT_SAVEDSEQUENCES"
            gDatabase.UpdateUserClientState(sRemoteUser, sRemoteUser, sClientState)
            return HandleGet(sClientState, sRemoteUser, "/state")
        elif sActionTargetID == "MANUALRUNS":
            # Switch states to the Manual Runs tab
            sClientState = "SELECT_MANUALRUNS"
            gDatabase.UpdateUserClientState(sRemoteUser, sRemoteUser, sClientState)
            return HandleGet(sClientState, sRemoteUser, "/state")

    # Unhandled use case
    raise Exception("State misalignment")

# Handle POST /VIEW
def HandlePostView(sClientState, sRemoteUser, pBody, nBodyLength):
    # Make sure we are on View Sequence
    global gElixys
    global gDatabase
    if sClientState.startswith("VIEW") == False:
        raise Exception("State misalignment")

    # Determine our sequence and component IDs
    pClientStateComponents = sClientState.split(".")
    nSequenceID = int(pClientStateComponents[1])
    nComponentID = int(pClientStateComponents[2])

    # Parse the JSON string in the body and extract the action type and target
    pJSON = json.loads(pBody)
    sActionType = str(pJSON["action"]["type"])
    sActionTargetID = str(pJSON["action"]["targetid"])

    # Call the base sequence POST handler first
    sNewClientState = HandlePostBaseSequence(sClientState, sRemoteUser, "VIEW", nSequenceID, nComponentID, sActionType, sActionTargetID)
    if sNewClientState != "":
        # POST handled
        return HandleGet(sNewClientState, sRemoteUser, "/state")

    # Handle View Sequence specific requests
    if sActionType == "BUTTONCLICK":
        if sActionTargetID == "EDIT":
            # Switch states to Edit Sequence
            sClientState = "EDIT." + str(nSequenceID) + "." + str(nComponentID)
            gDatabase.UpdateUserClientState(sRemoteUser, sRemoteUser, sClientState)
            return HandleGet(sClientState, sRemoteUser, "/state")
        elif sActionTargetID == "RUN":
            # Switch states to Prompt (Run Sequence)
            sClientState = "PROMPT_RUNSEQUENCE;" + str(nSequenceID) + ";" + sClientState
            gDatabase.UpdateUserClientState(sRemoteUser, sRemoteUser, sClientState)
            return HandleGet(sClientState, sRemoteUser, "/state")

    # Unhandled use case
    raise Exception("State misalignment")

# Handle POST /EDIT
def HandlePostEdit(sClientState, sRemoteUser, pBody, nBodyLength):
    # Make sure we are on Edit Sequence
    global gElixys
    global gDatabase
    if sClientState.startswith("EDIT") == False:
        raise Exception("State misalignment")

    # Determine our sequence and component IDs
    pClientStateComponents = sClientState.split(".")
    nSequenceID = int(pClientStateComponents[1])
    nComponentID = int(pClientStateComponents[2])

    # Parse the JSON string in the body and extract the action type and target
    pJSON = json.loads(pBody)
    sActionType = str(pJSON["action"]["type"])
    sActionTargetID = str(pJSON["action"]["targetid"])

    # Call the base sequence POST handler first
    sNewClientState = HandlePostBaseSequence(sClientState, sRemoteUser, "EDIT", nSequenceID, nComponentID, sActionType, sActionTargetID)
    if sNewClientState != "":
        # POST handled
        return HandleGet(sNewClientState, sRemoteUser, "/state")

    # Handle Edit Sequence specific requests
    if sActionType == "BUTTONCLICK":
        if sActionTargetID == "RUN":
            # Switch states to Prompt (Run Sequence)
            sClientState = "PROMPT_RUNSEQUENCE;" + str(nSequenceID) + ";" + sClientState
            gDatabase.UpdateUserClientState(sRemoteUser, sRemoteUser, sClientState)
            return HandleGet(sClientState, sRemoteUser, "/state")

    # Unhandled use case
    raise Exception("State misalignment")

# Handle POST /RUNSEQUENCE
def HandlePostRunSequence(sClientState, sRemoteUser, pBody, nBodyLength):
    # Make sure we are on Run Sequence
    global gElixys
    global gDatabase
    if sClientState.startswith("RUNSEQUENCE") == False:
        raise Exception("State misalignment")

    # Determine our sequence and component IDs
    pClientStateComponents = sClientState.split(".")
    nSequenceID = int(pClientStateComponents[1])
    nComponentID = int(pClientStateComponents[2])

    # Parse the JSON string in the body and extract the action type and target
    pJSON = json.loads(pBody)
    sActionType = str(pJSON["action"]["type"])
    sActionTargetID = str(pJSON["action"]["targetid"])

    # Check which button the user clicked
    if sActionType == "BUTTONCLICK":
        if sActionTargetID == "ABORT":
            # Switch states to Prompt (Abort sequence run)
            sClientState = "PROMPT_ABORTSEQUENCERUN;" + sClientState
            gDatabase.UpdateUserClientState(sRemoteUser, sRemoteUser, sClientState)
            return HandleGet(sClientState, sRemoteUser, "/state")
        elif sActionTargetID == "BACK":
            # Switch states to Home
            sClientState = "HOME"
            gDatabase.UpdateUserClientState(sRemoteUser, sRemoteUser, sClientState)
            return HandleGet(sClientState, sRemoteUser, "/state")

    # Unhandled use case
    raise Exception("State misalignment")

# Handle POST /MANUALRUN
def HandlePostManualRun(sClientState, sRemoteUser, pBody, nBodyLength):
    # Make sure we are on Manual Run
    global gElixys
    global gDatabase
    if sClientState.startswith("MANUALRUN") == False:
        raise Exception("State misalignment")

    # Determine our sequence and component IDs and manual run step
    pClientStateComponents = sClientState.split(".")
    nSequenceID = int(pClientStateComponents[1])
    nComponentID = int(pClientStateComponents[2])
    sManualRunStep = pClientStateComponents[3]

    # Parse the JSON string in the body and extract the action type and target
    pJSON = json.loads(pBody)
    sActionType = str(pJSON["action"]["type"])
    sActionTargetID = str(pJSON["action"]["targetid"])

    # Are we observing another user's manual run?
    if sRemoteUser != gElixys.GetRunUser(sRemoteUser):
        # Yes, so the only thing we can do is go back to home
        if sActionType == "BUTTONCLICK":
            if sActionTargetID == "BACK":
                # Switch states to home
                sClientState = "HOME"
                gDatabase.UpdateUserClientState(sRemoteUser, sRemoteUser, sClientState)
                return HandleGet(sClientState, sRemoteUser, "/state")

        # State misalignment in the observing client
        raise Exception("State misalignment")

    # Interpret the post event
    if sManualRunStep == "CASSETTE":
        if sActionType == "BUTTONCLICK":
            if sActionTargetID == "ABORT":
                # Switch states to Prompt (Abort manual run)
                sClientState = "PROMPT_ABORTMANUALRUN;" + sClientState
                gDatabase.UpdateUserClientState(sRemoteUser, sRemoteUser, sClientState)
                return HandleGet(sClientState, sRemoteUser, "/state")
            elif sActionTargetID == "START":
                # Advance to the SELECT step
                sClientState = "MANUALRUN." + str(nSequenceID) + "." + str(nComponentID) + ".SELECT"
                gElixys.SaveRunState(sRemoteUser, sClientState)
                gDatabase.UpdateUserClientState(sRemoteUser, sRemoteUser, sClientState)
                return HandleGet(sClientState, sRemoteUser, "/state")
            else:
                # Change the selected cassette
                sClientState = "MANUALRUN." + str(nSequenceID) + "." + sActionTargetID + ".CASSETTE"
                gElixys.SaveRunState(sRemoteUser, sClientState)
                gDatabase.UpdateUserClientState(sRemoteUser, sRemoteUser, sClientState)
                return HandleGet(sClientState, sRemoteUser, "/state")
    elif sManualRunStep == "SELECT":
        if sActionType == "BUTTONCLICK":
            if sActionTargetID == "COMPLETE":
                # Switch states to Prompt (Complete manual run)
                sClientState = "PROMPT_COMPLETEMANUALRUN;" + sClientState
                gDatabase.UpdateUserClientState(sRemoteUser, sRemoteUser, sClientState)
                return HandleGet(sClientState, sRemoteUser, "/state")
    elif sManualRunStep == "CONFIGURE":
        if sActionType == "BUTTONCLICK":
            if sActionTargetID == "BACK":
                # Delete the unit operation
                gElixys.DeleteSequenceComponent(sRemoteUser, nSequenceID, nComponentID)

                # Return to the SELECT step
                nComponentID = GetSequence(sRemoteUser, nSequenceID)["components"][0]["id"]
                sClientState = "MANUALRUN." + str(nSequenceID) + "." + str(nComponentID) + ".SELECT"
                gElixys.SaveRunState(sRemoteUser, sClientState)
                gDatabase.UpdateUserClientState(sRemoteUser, sRemoteUser, sClientState)
                return HandleGet(sClientState, sRemoteUser, "/state")
            elif sActionTargetID == "RUN":
                # Perform the unit operation
                gElixys.PerformOperation(sRemoteUser, nComponentID, nSequenceID)

                # Update the client state
                sClientState = gElixys.GetRunState(sRemoteUser)
                gDatabase.UpdateUserClientState(sRemoteUser, sRemoteUser, sClientState)
                return HandleGet(sClientState, sRemoteUser, "/state")
    elif sManualRunStep == "RUN":
        if sActionType == "BUTTONCLICK":
            if sActionTargetID == "ABORT":
                # Switch states to Prompt (Abort manual operation)
                sClientState = "PROMPT_ABORTMANUALOPERATION;" + sClientState
                gDatabase.UpdateUserClientState(sRemoteUser, sRemoteUser, sClientState)
                return HandleGet(sClientState, sRemoteUser, "/state")

    # Unhandled use case
    raise Exception("State misalignment")

# Handle sequence POST requests
def HandlePostBaseSequence(sClientState, sRemoteUser, sType, nSequenceID, nComponentID, sActionType, sActionTargetID):
    # Check which option the user selected
    global gDatabase
    if sActionType == "BUTTONCLICK":
        if sActionTargetID == "BACK":
            # Switch states to Select Sequence
            sClientState = "SELECT_SAVEDSEQUENCES"
            gDatabase.UpdateUserClientState(sRemoteUser, sRemoteUser, sClientState)
            return sClientState
        elif sActionTargetID == "PREVIOUS":
            # Move to the previous component ID
            nPreviousComponentID = -1
            pSequence = GetSequence(sRemoteUser, nSequenceID)
            for pComponent in pSequence["components"]:
                if pComponent["id"] == nComponentID:
                    if nPreviousComponentID != -1:
                        sClientState = sType + "." + str(nSequenceID) + "." + str(nPreviousComponentID)
                        gDatabase.UpdateUserClientState(sRemoteUser, sRemoteUser, sClientState)
                    return sClientState
                else:
                    nPreviousComponentID = pComponent["id"]
            raise Exception("Component ID not found in sequence")
        elif sActionTargetID == "NEXT":
            # Move to the next component ID
            bComponentIDFound = False
            pSequence = GetSequence(sRemoteUser, nSequenceID)
            for pComponent in pSequence["components"]:
                if bComponentIDFound:
                    sClientState = sType + "." + str(nSequenceID) + "." + str(pComponent["id"])
                    gDatabase.UpdateUserClientState(sRemoteUser, sRemoteUser, sClientState)
                    return sClientState
                elif pComponent["id"] == nComponentID:
                    bComponentIDFound = True
            if bComponentIDFound:
                return sClientState
            raise Exception("Component ID not found in sequence" + str(nComponentID))
        else:
            # Check if the target ID corresponds to one of our sequence components
            pSequence = GetSequence(sRemoteUser, nSequenceID)
            for pComponent in pSequence["components"]:
                if str(pComponent["id"]) == sActionTargetID:
                    # Update the current component and return the latest state to the client
                    sClientState = sType + "." + str(nSequenceID) + "." + str(pComponent["id"])
                    gDatabase.UpdateUserClientState(sRemoteUser, sRemoteUser, sClientState)
                    return sClientState

    # Tell the caller we didn't handle the use case
    return ""

# Handle POST /PROMPT
def HandlePostPrompt(sClientState, sRemoteUser, pBody, nBodyLength):
    # Make sure we are on Prompt
    global gElixys
    global gDatabase
    if sClientState.startswith("PROMPT") == False:
        raise Exception("State misalignment");

    # Parse the JSON string in the body
    pJSON = json.loads(pBody)

    # Extract the post parameters
    sActionType = str(pJSON["action"]["type"])
    sActionTargetID = str(pJSON["action"]["targetid"])
    sEdit1 = str(pJSON["edit1"])
    sEdit2 = str(pJSON["edit2"])

    # The only recognized action from a prompt is a button click
    if sActionType != "BUTTONCLICK":
        raise Exception("State misalignment")

    # Interpret the response in context of the client state
    if sClientState.startswith("PROMPT_CREATESEQUENCE"):
        if sActionTargetID == "CREATE":
            # Ignore this button for now
            return HandleGet(sClientState, sRemoteUser, "/state")
        if sActionTargetID == "CANCEL":
            # Switch to the previous state
            sClientState = sClientState.split(";")[1]
            gDatabase.UpdateUserClientState(sRemoteUser, sRemoteUser, sClientState)
            return HandleGet(sClientState, sRemoteUser, "/state")
    elif sClientState.startswith("PROMPT_COPYSEQUENCE"):
        if sActionTargetID == "COPY":
            # Ignore this button for now
            return HandleGet(sClientState, sRemoteUser, "/state")
        if sActionTargetID == "CANCEL":
            # Switch to the previous state
            sClientState = sClientState.split(";")[1]
            gDatabase.UpdateUserClientState(sRemoteUser, sRemoteUser, sClientState)
            return HandleGet(sClientState, sRemoteUser, "/state")
    elif sClientState.startswith("PROMPT_DELETESEQUENCE"):
        if sActionTargetID == "DELETE":
            # Ignore this button for now
            return HandleGet(sClientState, sRemoteUser, "/state")
        if sActionTargetID == "CANCEL":
            # Switch to the previous state
            sClientState = sClientState.split(";")[1]
            gDatabase.UpdateUserClientState(sRemoteUser, sRemoteUser, sClientState)
            return HandleGet(sClientState, sRemoteUser, "/state")
    elif sClientState.startswith("PROMPT_ABORTSEQUENCERUN"):
        if sActionTargetID == "ABORT":
            # Abort the run and return to the home page
            gElixys.AbortRun(sRemoteUser)
            sClientState = "HOME"
            gDatabase.UpdateUserClientState(sRemoteUser, sRemoteUser, sClientState)
            return HandleGet(sClientState, sRemoteUser, "/state")
        if sActionTargetID == "CANCEL":
            # Switch to the previous state
            sClientState = sClientState.split(";")[1]
            gDatabase.UpdateUserClientState(sRemoteUser, sRemoteUser, sClientState)
            return HandleGet(sClientState, sRemoteUser, "/state")
    elif sClientState.startswith("PROMPT_RUNSEQUENCE"):
        if sActionTargetID == "OK":
            # Run the sequence
            gElixys.RunSequence(sRemoteUser, int(sClientState.split(";")[1]))
            sClientState = gElixys.GetRunState(sRemoteUser)
            gDatabase.UpdateUserClientState(sRemoteUser, sRemoteUser, sClientState)
            return HandleGet(sClientState, sRemoteUser, "/state")
        if sActionTargetID == "CANCEL":
            # Switch to the previous state
            sClientState = sClientState.split(";")[2]
            gDatabase.UpdateUserClientState(sRemoteUser, sRemoteUser, sClientState)
            return HandleGet(sClientState, sRemoteUser, "/state")
    elif sClientState.startswith("PROMPT_UNITOPERATION"):
        if sActionTargetID == "OK":
            # Are we in the middle of a sequence or manual run?
            sRunState = gElixys.GetRunState(sRemoteUser)
            if sRunState.split(".")[0] == "RUNSEQUENCE":
                # Continue the sequence run
                gElixys.ContinueRun(sRemoteUser)
            else:
                # Continue the manual run
                gElixys.ContinueOperation(sRemoteUser)
            sClientState = gElixys.GetRunState(sRemoteUser)
            #gDatabase.UpdateUserClientState(sRemoteUser, sRemoteUser, sClientState)
            return HandleGet(sClientState, sRemoteUser, "/state")
        if sActionTargetID == "BACK":
            # Return to the home page
            sClientState = "HOME"
            gDatabase.UpdateUserClientState(sRemoteUser, sRemoteUser, sClientState)
            return HandleGet(sClientState, sRemoteUser, "/state")
    elif sClientState.startswith("PROMPT_MANUALRUN"):
        if sActionTargetID == "OK":
            # Start the manual run
            gElixys.StartManualRun(sRemoteUser)
            sClientState = gElixys.GetRunState(sRemoteUser)
            gDatabase.UpdateUserClientState(sRemoteUser, sRemoteUser, sClientState)
            return HandleGet(sClientState, sRemoteUser, "/state")
        if sActionTargetID == "CANCEL":
            # Switch to the previous state
            sClientState = sClientState.split(";")[1]
            gDatabase.UpdateUserClientState(sRemoteUser, sRemoteUser, sClientState)
            return HandleGet(sClientState, sRemoteUser, "/state")
    elif sClientState.startswith("PROMPT_ABORTMANUALRUN"):
        if sActionTargetID == "ABORT":
            # Set the client and system states
            sClientState = "HOME"
            gDatabase.UpdateUserClientState(sRemoteUser, sRemoteUser, sClientState)
            gElixys.SaveSystemState(sRemoteUser, "NONE")
            return HandleGet(sClientState, sRemoteUser, "/state")
        if sActionTargetID == "CANCEL":
            # Switch to the previous state
            sClientState = sClientState.split(";")[1]
            gDatabase.UpdateUserClientState(sRemoteUser, sRemoteUser, sClientState)
            return HandleGet(sClientState, sRemoteUser, "/state")
    elif sClientState.startswith("PROMPT_ABORTMANUALOPERATION"):
        if sActionTargetID == "ABORT":
            # Return to the selection step
            sRunState = gElixys.GetRunState(sRemoteUser)
            pRunStateComponents = sRunState.split(".")
            sClientState = "MANUALRUN." + pRunStateComponents[1] + "." + pRunStateComponents[2] + ".SELECT"
            gElixys.SaveRunState(sRemoteUser, sClientState)
            gDatabase.UpdateUserClientState(sRemoteUser, sRemoteUser, sClientState)
            return HandleGet(sClientState, sRemoteUser, "/state")
        if sActionTargetID == "CANCEL":
            # Switch to the previous state
            sClientState = sClientState.split(";")[1]
            gDatabase.UpdateUserClientState(sRemoteUser, sRemoteUser, sClientState)
            return HandleGet(sClientState, sRemoteUser, "/state")
    elif sClientState.startswith("PROMPT_COMPLETEMANUALRUN"):
        if sActionTargetID == "SAVE":
            # Finish the manual run
            gElixys.FinishManualRun(sRemoteUser)
            sClientState = "HOME"
            gDatabase.UpdateUserClientState(sRemoteUser, sRemoteUser, sClientState)
            return HandleGet(sClientState, sRemoteUser, "/state")
        if sActionTargetID == "CANCEL":
            # Switch to the previous state
            sClientState = sClientState.split(";")[1]
            gDatabase.UpdateUserClientState(sRemoteUser, sRemoteUser, sClientState)
            return HandleGet(sClientState, sRemoteUser, "/state")

    # Unhandled use case
    raise Exception("State misalignment")

# Handle POST /sequence/[sequenceid]
def HandlePostSequence(sClientState, sRemoteUser, pBody, sPath):
    # Ignore this function for now
    return HandleGet(sClientState, sRemoteUser, "/state")

# Handle POST /sequence/[sequenceid]/component/[componentid]
def HandlePostComponent(sClientState, sRemoteUser, pBody, nBodyLength, sPath):
    # Extract sequence and component IDs
    global gDatabase
    pPathComponents = sPath.split("/")
    nSequenceID = int(pPathComponents[2])
    nComponentID = int(pPathComponents[4])
    nInsertionID = None
    if len(pPathComponents) == 6:
        nInsertionID = int(pPathComponents[5])

    # Parse the component JSON if present
    pComponent = None
    if nBodyLength != 0:
        pComponent = json.loads(pBody)

    # Are we working with an existing component?
    if nComponentID != 0:
        # Yes, so update the existing component
        UpdateComponent(sRemoteUser, nSequenceID, nComponentID, nInsertionID, pComponent)
    else:
        # No, so add a new component
        nComponentID = AddComponent(sRemoteUser, nSequenceID, nInsertionID, pComponent)

        # Update the client to show the new component
        sClientState = gDatabase.GetUserClientState(sRemoteUser, sRemoteUser)
        pClientStateComponents = sClientState.split(".")
        sClientState = pClientStateComponents[0] + "." + str(nSequenceID) + "." + str(pComponent["id"])
        gDatabase.UpdateUserClientState(sRemoteUser, sRemoteUser, sClientState)

        # Is the remote user the one that is currently running the system?
        if sRemoteUser == gElixys.GetRunUser(sRemoteUser):
            # Yes, so advance to the configuration step after adding a new component
            if nComponentID == 0:
                sClientState = "MANUALRUN." + str(nSequenceID) + "." + str(pComponent["id"]) + ".CONFIGURE"
                gElixys.SaveRunState(sRemoteUser, sClientState)
                gDatabase.UpdateUserClientState(sRemoteUser, sRemoteUser, sClientState)

    # Return the new state
    return HandleGet(sClientState, sRemoteUser, "/state")

# Handle POST /sequence/[sequenceid]/reagent/[reagentid]
def HandlePostReagent(sClientState, sRemoteUser, pBody, nBodyLength, sPath):
    # Extract sequence and reagent IDs
    global gDatabase
    pPathComponents = sPath.split("/")
    nSequenceID = int(pPathComponents[2])
    nReagentID = int(pPathComponents[4])

    # Save the reagent
    pReagent = json.loads(pBody)
    gDatabase.UpdateReagent(sRemoteUser, nReagentID, pReagent["available"], pReagent["name"], pReagent["description"])

    # Return the new state
    return HandleGet(sClientState, sRemoteUser, "/state")

# Handle DELETE requests
def HandleDelete(sClientState, sRemoteUser, sPath):
    if sPath.startswith("/sequence/"):
        if sPath.find("/component/") != -1:
            return HandleDeleteComponent(sClientState, sRemoteUser, sPath)

    # Unhandled use case
    raise Exception("Unknown path: " + sPath)

# Handle DELETE /sequence/[sequenceid]/component/[componentid]
def HandleDeleteComponent(sClientState, sRemoteUser, sPath):
    # Extract sequence and component IDs
    global gElixys
    pPathComponents = sPath.split("/")
    nSequenceID = int(pPathComponents[2])
    nComponentID = int(pPathComponents[4])

    # Delete the sequence component
    gElixys.DeleteSequenceComponent(sRemoteUser, nSequenceID, nComponentID)

    # Return the new state
    return HandleGet(sClientState, sRemoteUser, "/state")

### Utility functions ###

# Fetches a sequence and components from the database
def GetSequence(sRemoteUser, nSequenceID):
    # Fetch the sequence from the databse
    global gDatabase
    pSequence = gDatabase.GetSequence(sRemoteUser, nSequenceID)

    # Add details to each component
    for pComponent in pSequence["components"]:
        AddComponentDetails(pComponent)

    # Return
    return pSequence

# Fetches a component from the database
def GetComponent(sRemoteUser, nComponentID):
    # Fetch the component from the databse
    global gDatabase
    pComponent = gDatabase.GetComponent(sRemoteUser, nComponentID)

    # Add details to the component and return
    AddComponentDetails(pComponent)
    return pComponent

# Adds a new component to the database
def AddComponent(sRemoteUser, nSequenceID, nInsertionID, pComponent):
    # Strip the component down to the fields we want to save
    global gDatabase
    pDBComponent = RemoveComponentDetails(pComponent)

    # Insert the new component
    return gDatabase.InsertComponent(sRemoteUser, nSequenceID, pComponent["componenttype"], pComponent["name"], json.dumps(pDBComponent), nInsertionID)

# Updates an existing component
def UpdateComponent(sRemoteUser, nSequenceID, nComponentID, nInsertionID, pComponent):
    # Update the component if one was provided
    global gDatabase
    if pComponent != None:
        # Pull the component from the database and update it with the fields we want to save
        pDBComponent = GetComponent(sRemoteUser, nComponentID)
        UpdateComponentDetails(pDBComponent, pComponent)

        # Update the component
        gDatabase.UpdateComponent(sRemoteUser, nComponentID, pDBComponent["componenttype"], pDBComponent["name"], json.dumps(pDBComponent))

    # Move the component as needed
    if nInsertionID != None:
        gDatabase.MoveComponent(sRemoteUser, nComponentID, nInsertionID)

# Adds details to the component after retrieving it from the database and prior to sending it to the client
def AddComponentDetails(pComponent):
    # Determine the starting reagent ID
    #if nSequenceID != 10000:
    nBaseReagentID = 1
    #else:
    #    nBaseReagentID = 31;

    # Add component-specific details
    if pComponent["componenttype"] == "CASSETTE":
        pComponent.update({"name":"Cassette " + str(pComponent["id"])})
        pComponent.update({"reactordescription":"Reactor associated with this cassette"})
        pComponent.update({"reactorvalidation":"type=enum-literal; values=1,2,3; required=true"})
        pComponent.update({"validationerror":False})
    elif pComponent["componenttype"] == "ADD":
        #pReagent = self.GetSequenceReagent(sUsername, nSequenceID, pComponent["reagent"])
        #if pReagent["name"] != "[invalid]":
        #    pComponent.update({"name":"Add " + pReagent["name"]})
        #else:
        pComponent.update({"name":"Add"})
        pComponent.update({"reactordescription":"Reactor where the reagent will be added"})
        pComponent.update({"reactorvalidation":"type=enum-literal; values=1,2,3; required=true"})
        pComponent.update({"reagentdescription":"Reagent to add to the reactor"})
        pComponent.update({"reagentvalidation":"type=enum-reagent; values=" + str(nBaseReagentID) + "," + str(nBaseReagentID + 1) + "," +
            str(nBaseReagentID + 2) + "," + str(nBaseReagentID + 3) + "," + str(nBaseReagentID + 4) + "," + str(nBaseReagentID + 5) + "," +
            str(nBaseReagentID + 6) + "," + str(nBaseReagentID + 7) + "; required=true"})
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
        pComponent.update({"targetvalidation":"type=enum-target; values=" + str(nBaseReagentID + 8) + "; required=true"})
        pComponent.update({"validationerror":False})
    elif pComponent["componenttype"] == "ELUTE":
        pComponent.update({"name":"Elute"})
        pComponent.update({"reactordescription":"Reactor where the reagent will be eluted"})
        pComponent.update({"reactorvalidation":"type=enum-literal; values=1,2,3; required=true"})
        pComponent.update({"reagentdescription":"Reagent used to elute the target"})
        pComponent.update({"reagentvalidation":"type=enum-reagent; values=1,2,3,4,5,6,7,8; required=true"})
        pComponent.update({"targetdescription":"Target to be eluted with the reagent"})
        pComponent.update({"targetvalidation":"type=enum-target; values=" + str(nBaseReagentID + 9) + "; required=true"})
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

# Update the database component with the relavent details that we have received from the client
def UpdateComponentDetails(pTargetComponent, pSourceComponent):
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

# Strips a component down to only the details we want to save in the database
def RemoveComponentDetails(pComponent):
    # Get a list of component-specific keys we want to save
    pDesiredKeys = None
    if pComponent["componenttype"] == "ADD":
        pDesiredKeys = ["type", "componenttype", "id", "reactor", "reagent"]
    elif pComponent["componenttype"] == "EVAPORATE":
        pDesiredKeys = ["type", "componenttype", "id", "reactor", "duration", "evaporationtemperature", "finaltemperature", "stirspeed"]
    elif pComponent["componenttype"] == "TRANSFER":
        pDesiredKeys = ["type", "componenttype", "id", "reactor", "target"]
    elif pComponent["componenttype"] == "ELUTE":
        pDesiredKeys = ["type", "componenttype", "id", "reactor", "reagent", "target"]
    elif pComponent["componenttype"] == "REACT":
        pDesiredKeys = ["type", "componenttype", "id", "reactor", "position", "duration", "reactiontemperature", "finaltemperature", "stirspeed"]
    elif pComponent["componenttype"] == "PROMPT":
        pDesiredKeys = ["type", "componenttype", "id", "reactor", "message"]
    elif pComponent["componenttype"] == "INSTALL":
        pDesiredKeys = ["type", "componenttype", "id", "reactor", "message"]
    elif pComponent["componenttype"] == "COMMENT":
        pDesiredKeys = ["type", "componenttype", "id", "reactor", "comment"]
    elif pComponent["componenttype"] == "ACTIVITY":
        pDesiredKeys = ["type", "componenttype", "id", "reactor"]

    # Remove the keys that we do not want to save
    pReturn = pComponent.copy()
    if pDesiredKeys != None:
        pUnwantedKeys = set(pReturn) - set(pDesiredKeys)
        for pUnwantedKey in pUnwantedKeys:
            del pReturn[pUnwantedKey]
    return pReturn

### Main WSGI application entry point ###

def application(pEnvironment, fStartResponse):
    # Connnect to the database.  It is important that we do this at the start of every request or two things happen:
    #  1. We start receiving stale data from MySQLdb depending on which thread handles this request
    #  2. MySQL will run out of available database connections under heavy loads
    global gElixys
    global gDatabase
    gDatabase.Connect()

    # Extract input variables
    if pEnvironment.has_key("REMOTE_USER"):
        sRemoteUser = pEnvironment["REMOTE_USER"]
    else:
        sRemoteUser = "devel"    # Debugging hack: use "devel" as default user
    sRequestMethod = pEnvironment["REQUEST_METHOD"]
    sPath = pEnvironment["PATH_INFO"]
    if sPath.startswith("/Elixys"):
        # Debugging hack: trim off any leading "/Elixys" string
        sPath = sPath[7:]

    # Load the client and system state
    sClientState = gDatabase.GetUserClientState(sRemoteUser, sRemoteUser)
    if sClientState == "":
        # Default to the home screen
        sClientState = "HOME"
        gDatabase.UpdateUserClientState(sRemoteUser, sRemoteUser, sClientState)
    sSystemState = gElixys.GetSystemState(sRemoteUser)

    # Log the request
    Log("Received " + sRequestMethod + " request for " + sPath + " (client = " + sRemoteUser + ", client state = " + sClientState +
        ", system state = " + sSystemState + ")");

    # Handle the request
    try:
        # Call the appropriate handler
        if sRequestMethod == "GET":
            sResponse = HandleGet(sClientState, sRemoteUser, sPath)
        elif sRequestMethod == "POST":
            nBodyLength = int(pEnvironment["CONTENT_LENGTH"])
            pBody = pEnvironment["wsgi.input"].read(nBodyLength)
            sResponse = HandlePost(sClientState, sRemoteUser, sPath, pBody, nBodyLength)
        elif sRequestMethod == "DELETE":
            sResponse = HandleDelete(sClientState, sRemoteUser, sPath)
        else:
            raise Exception("Unknown request method")
    except Exception as ex:
        # Send an error message back to the client
        sResponse = {"type":"error","description":str(ex)}

    # Initialize the return status and headers
    sStatus = "200 OK"
    sResponseJSON = json.dumps(sResponse)
    pHeaders = [("Content-type", "text/plain"), ("Content-length", str(len(sResponseJSON)))]

    # Close the database connection
    gDatabase.Disconnect()

    # Send the response
    fStartResponse(sStatus, pHeaders)
    return [sResponseJSON]

# Main function used for local execution
if __name__ == '__main__':
    httpd = make_server('', 80, application)
    print "Serving on port 80..."
    httpd.serve_forever()
