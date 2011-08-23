#!/usr/bin/python

# Imports
from wsgiref.simple_server import make_server
import json
from wsgiref.headers import Headers
import sys
sys.path.append("/opt/elixys/core")
#sys.path.append("/opt/elixys/database")
#from DBComm import DBComm

# Import and create the core Elixys server
from DummyElixys import Elixys 
gElixys = Elixys()

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
    if sRemoteUser == gElixys.GetRunUser(sRemoteUser):
        # Yes, so make sure the user is in the appropriate run state
        sRunState = gElixys.GetRunState(sRemoteUser)
        if sRunState.startswith("RUNSEQUENCE") and not sClientState.startswith("RUNSEQUENCE") and not sClientState.startswith("PROMPT"):
            pRunStateComponents = sRunState.split(".")
            sClientState = "RUNSEQUENCE." + pRunStateComponents[1] + "." + pRunStateComponents[2]
            gElixys.SaveClientState(sRemoteUser, sClientState)
        elif sRunState.startswith("RUNMANUAL") and not sClientState.startswith("RUNMANUAL") and not sClientState.startswith("PROMPT"):
            pRunStateComponents = sRunState.split(".")
            sClientState = "RUNMANUAL." + pRunStateComponents[1] + "." + pRunStateComponents[2]
            gElixys.SaveClientState(sRemoteUser, sClientState)

    # Get the user information and server state
    pUser = {"type":"user"}
    pUser.update(gElixys.GetUser(sRemoteUser))
    pServerState = {"type":"serverstate"}
    pServerState.update(gElixys.GetServerState(sRemoteUser))

    # Update the full client state because GetServerState() may have changed it
    sClientState = gElixys.GetClientState(sRemoteUser)

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
    global gElixys
    pState = HandleGetStateSelect(sRemoteUser)
    pState.update({"tabid":"SAVEDSEQUENCES"})
    pState["optionbuttons"].append({"type":"button",
        "text":"Edit",
        "id":"EDIT"})
    pState["optionbuttons"].append({"type":"button",
        "text":"Delete",
        "id":"DELETE"})
    pState.update({"sequences":gElixys.GetSequenceList(sRemoteUser, "Saved")})
    return pState

# Handle GET /state for Select Sequence (Manual Runs tab)
def HandleGetStateSelectManualRuns(sRemoteUser):
    global gElixys
    pState = HandleGetStateSelect(sRemoteUser)
    pState.update({"tabid":"MANUALRUNS"})
    pState.update({"sequences":gElixys.GetSequenceList(sRemoteUser, "Manual")})
    return pState

# Handle GET /state for View Sequence
def HandleGetStateView(sClientState, sRemoteUser):
    # Split the state and extract the sequence ID
    global gElixys
    pClientStateComponents = sClientState.split(".")
    nSequenceID = int(pClientStateComponents[1])

    # Do we have a component ID?
    if (len(pClientStateComponents) > 2):
        # Yes, so extract it
        nComponentID = int(pClientStateComponents[2])
    else:
        # No, the component ID is missing.  Get the sequence and the ID of the first component
        pSequence = gElixys.GetSequence(sRemoteUser, nSequenceID)
        nComponentID = pSequence["components"][0]["id"]

        # Update our state
        sClientState = "VIEW." + str(nSequenceID) + "." + str(nComponentID)
        gElixys.SaveClientState(sRemoteUser, sClientState)

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
    pClientStateComponents = sClientState.split(".")
    nSequenceID = int(pClientStateComponents[1])

    # Do we have a component ID?
    if (len(pClientStateComponents) > 2):
        # Yes, so extract it
        nComponentID = int(pClientStateComponents[2])
    else:
        # No, the component ID is missing.  Get the sequence and the ID of the first component
        pSequence = gElixys.GetSequence(sRemoteUser, nSequenceID)
        nComponentID = pSequence["components"][0]["id"]

        # Update our state
        sClientState = "EDIT." + str(nSequenceID) + "." + str(nComponentID)
        gElixys.SaveClientState(sRemoteUser, sClientState)

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
    sRunState = gElixys.GetRunState(sRemoteUser)
    pRunStateComponents = sRunState.split(".")
    nSequenceID = int(pRunStateComponents[1])
    nComponentID = int(pRunStateComponents[2])
    pSequence = gElixys.GetSequenceComponent(sRemoteUser, nSequenceID, nComponentID)

    # Make sure this component requires a prompt
    if (pSequence["components"][0]["componenttype"] != "PROMPT") and (pSequence["components"][0]["componenttype"] != "INSTALL"):
        # No, so update the client state and return
        sClientState = gElixys.GetRunState(sRemoteUser)
        gElixys.SaveClientState(sRemoteUser, sClientState)
        return pPromptState

    # Set the prompt message
    pPromptState["show"] = True
    pPromptState["title"] = "Prompt"
    pPromptState["text1"] = pSequence["components"][0]["message"]

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
    pSequence.update(gElixys.GetSequence(sRemoteUser, nSequenceID))

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
    global gElixys
    pPathComponents = sPath.split("/")
    nSequenceID = int(pPathComponents[2])
    nComponentID = int(pPathComponents[4])

    # Load the sequence and only the desired component
    pSequence = gElixys.GetSequenceComponent(sRemoteUser, nSequenceID, nComponentID)

    # Create and return the component
    pComponent = {"type":"component"}
    pComponent.update(pSequence["components"][0])
    return pComponent

# Handle GET /sequence/[sequenceid]/reagent/[reagentid]
def HandleGetReagent(sRemoteUser, sPath):
    # Extract sequence and reagent IDs
    global gElixys
    pPathComponents = sPath.split("/")
    nSequenceID = int(pPathComponents[2])
    nReagentID = int(pPathComponents[4])

    # Return the sequence reagent
    pReagent = {"type":"reagent"}
    pReagent.update(gElixys.GetSequenceReagent(sRemoteUser, nSequenceID, nReagentID))
    return pReagent

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
            gElixys.SaveClientState(sRemoteUser, sClientState)
            return HandleGet(sClientState, sRemoteUser, "/state")
        elif sActionTargetID == "MANUAL":
            # Switch states to Prompt (Manual Run)
            sClientState = "PROMPT_MANUALRUN;" + sClientState
            gElixys.SaveClientState(sRemoteUser, sClientState)
            return HandleGet(sClientState, sRemoteUser, "/state")
        elif sActionTargetID == "OBSERVE":
            # Swtich to Run Sequence
            sClientState = gElixys.GetRunState(sRemoteUser)
            gElixys.SaveClientState(sRemoteUser, sClientState)
            return HandleGet(sClientState, sRemoteUser, "/state")

    # Unhandled use case
    raise Exception("State misalignment")

# Handle POST /SELECT
def HandlePostSelect(sClientState, sRemoteUser, pBody, nBodyLength):
    # Make sure we are on Select Sequence
    global gElixys
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
            gElixys.SaveClientState(sRemoteUser, sClientState)
            return HandleGet(sClientState, sRemoteUser, "/state")
        elif sActionTargetID == "EDIT":
            # Switch states to Edit Sequence
            sClientState = "EDIT." + str(nSequenceID)
            gElixys.SaveClientState(sRemoteUser, sClientState)
            return HandleGet(sClientState, sRemoteUser, "/state")
        elif sActionTargetID == "RUN":
            # Switch states to Prompt (Run Sequence)
            sClientState = "PROMPT_RUNSEQUENCE;" + str(nSequenceID) + ";" + sClientState
            gElixys.SaveClientState(sRemoteUser, sClientState)
            return HandleGet(sClientState, sRemoteUser, "/state")
        elif sActionTargetID == "BACK":
            # Switch states to Home
            sClientState = "HOME"
            gElixys.SaveClientState(sRemoteUser, sClientState)
            return HandleGet(sClientState, sRemoteUser, "/state")
        elif sActionTargetID == "CREATE":
            # Switch states to Prompt (Create Sequence)
            sClientState = "PROMPT_CREATESEQUENCE;" + sClientState
            gElixys.SaveClientState(sRemoteUser, sClientState)
            return HandleGet(sClientState, sRemoteUser, "/state")
        elif sActionTargetID == "COPY":
            # Switch states to Prompt (Copy Sequence)
            sClientState = "PROMPT_COPYSEQUENCE;" + sClientState
            gElixys.SaveClientState(sRemoteUser, sClientState)
            return HandleGet(sClientState, sRemoteUser, "/state")
        elif sActionTargetID == "DELETE":
            # Switch states to Prompt (Delete Sequence)
            sClientState = "PROMPT_DELETESEQUENCE;" + sClientState
            gElixys.SaveClientState(sRemoteUser, sClientState)
            return HandleGet(sClientState, sRemoteUser, "/state")
    elif sActionType == "TABCLICK":
        if sActionTargetID == "SAVEDSEQUENCES":
            # Switch states to the Saved Sequences tab
            sClientState = "SELECT_SAVEDSEQUENCES"
            gElixys.SaveClientState(sRemoteUser, sClientState)
            return HandleGet(sClientState, sRemoteUser, "/state")
        elif sActionTargetID == "MANUALRUNS":
            # Switch states to the Manual Runs tab
            sClientState = "SELECT_MANUALRUNS"
            gElixys.SaveClientState(sRemoteUser, sClientState)
            return HandleGet(sClientState, sRemoteUser, "/state")

    # Unhandled use case
    raise Exception("State misalignment")

# Handle POST /VIEW
def HandlePostView(sClientState, sRemoteUser, pBody, nBodyLength):
    # Make sure we are on View Sequence
    global gElixys
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
            gElixys.SaveClientState(sRemoteUser, sClientState)
            return HandleGet(sClientState, sRemoteUser, "/state")
        elif sActionTargetID == "RUN":
            # Switch states to Prompt (Run Sequence)
            sClientState = "PROMPT_RUNSEQUENCE;" + str(nSequenceID) + ";" + sClientState
            gElixys.SaveClientState(sRemoteUser, sClientState)
            return HandleGet(sClientState, sRemoteUser, "/state")

    # Unhandled use case
    raise Exception("State misalignment")

# Handle POST /EDIT
def HandlePostEdit(sClientState, sRemoteUser, pBody, nBodyLength):
    # Make sure we are on Edit Sequence
    global gElixys
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
            gElixys.SaveClientState(sRemoteUser, sClientState)
            return HandleGet(sClientState, sRemoteUser, "/state")

    # Unhandled use case
    raise Exception("State misalignment")

# Handle POST /RUNSEQUENCE
def HandlePostRunSequence(sClientState, sRemoteUser, pBody, nBodyLength):
    # Make sure we are on Run Sequence
    global gElixys
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
            gElixys.SaveClientState(sRemoteUser, sClientState)
            return HandleGet(sClientState, sRemoteUser, "/state")
        elif sActionTargetID == "BACK":
            # Switch states to Home
            sClientState = "HOME"
            gElixys.SaveClientState(sRemoteUser, sClientState)
            return HandleGet(sClientState, sRemoteUser, "/state")

    # Unhandled use case
    raise Exception("State misalignment")

# Handle POST /MANUALRUN
def HandlePostManualRun(sClientState, sRemoteUser, pBody, nBodyLength):
    # Make sure we are on Manual Run
    global gElixys
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
                gElixys.SaveClientState(sRemoteUser, sClientState)
                return HandleGet(sClientState, sRemoteUser, "/state")

        # State misalignment in the observing client
        raise Exception("State misalignment")

    # Interpret the post event
    if sManualRunStep == "CASSETTE":
        if sActionType == "BUTTONCLICK":
            if sActionTargetID == "ABORT":
                # Switch states to Prompt (Abort manual run)
                sClientState = "PROMPT_ABORTMANUALRUN;" + sClientState
                gElixys.SaveClientState(sRemoteUser, sClientState)
                return HandleGet(sClientState, sRemoteUser, "/state")
            elif sActionTargetID == "START":
                # Advance to the SELECT step
                sClientState = "MANUALRUN." + str(nSequenceID) + "." + str(nComponentID) + ".SELECT"
                gElixys.SaveRunState(sRemoteUser, sClientState)
                gElixys.SaveClientState(sRemoteUser, sClientState)
                return HandleGet(sClientState, sRemoteUser, "/state")
            else:
                # Change the selected cassette
                sClientState = "MANUALRUN." + str(nSequenceID) + "." + sActionTargetID + ".CASSETTE"
                gElixys.SaveRunState(sRemoteUser, sClientState)
                gElixys.SaveClientState(sRemoteUser, sClientState)
                return HandleGet(sClientState, sRemoteUser, "/state")
    elif sManualRunStep == "SELECT":
        if sActionType == "BUTTONCLICK":
            if sActionTargetID == "COMPLETE":
                # Switch states to Prompt (Complete manual run)
                sClientState = "PROMPT_COMPLETEMANUALRUN;" + sClientState
                gElixys.SaveClientState(sRemoteUser, sClientState)
                return HandleGet(sClientState, sRemoteUser, "/state")
    elif sManualRunStep == "CONFIGURE":
        if sActionType == "BUTTONCLICK":
            if sActionTargetID == "BACK":
                # Delete the unit operation
                gElixys.DeleteSequenceComponent(sRemoteUser, nSequenceID, nComponentID)

                # Return to the SELECT step
                nComponentID = gElixys.GetSequence(sRemoteUser, nSequenceID)["components"][0]["id"]
                sClientState = "MANUALRUN." + str(nSequenceID) + "." + str(nComponentID) + ".SELECT"
                gElixys.SaveRunState(sRemoteUser, sClientState)
                gElixys.SaveClientState(sRemoteUser, sClientState)
                return HandleGet(sClientState, sRemoteUser, "/state")
            elif sActionTargetID == "RUN":
                # Perform the unit operation
                gElixys.PerformOperation(sRemoteUser, nComponentID, nSequenceID)

                # Update the client state
                sClientState = gElixys.GetRunState(sRemoteUser)
                gElixys.SaveClientState(sRemoteUser, sClientState)
                return HandleGet(sClientState, sRemoteUser, "/state")
    elif sManualRunStep == "RUN":
        if sActionType == "BUTTONCLICK":
            if sActionTargetID == "ABORT":
                # Switch states to Prompt (Abort manual operation)
                sClientState = "PROMPT_ABORTMANUALOPERATION;" + sClientState
                gElixys.SaveClientState(sRemoteUser, sClientState)
                return HandleGet(sClientState, sRemoteUser, "/state")

    # Unhandled use case
    raise Exception("State misalignment")

# Handle sequence POST requests
def HandlePostBaseSequence(sClientState, sRemoteUser, sType, nSequenceID, nComponentID, sActionType, sActionTargetID):
    # Check which option the user selected
    if sActionType == "BUTTONCLICK":
        if sActionTargetID == "BACK":
            # Switch states to Select Sequence
            sClientState = "SELECT_SAVEDSEQUENCES"
            gElixys.SaveClientState(sRemoteUser, sClientState)
            return sClientState
        elif sActionTargetID == "PREVIOUS":
            # Move to the previous component ID
            nPreviousComponentID = -1
            for pComponent in gElixys.GetSequence(sRemoteUser, nSequenceID)["components"]:
                if pComponent["id"] == nComponentID:
                    if nPreviousComponentID != -1:
                        sClientState = sType + "." + str(nSequenceID) + "." + str(nPreviousComponentID)
                        gElixys.SaveClientState(sRemoteUser, sClientState)
                    return sClientState
                else:
                    nPreviousComponentID = pComponent["id"]
            raise Exception("Component ID not found in sequence")
        elif sActionTargetID == "NEXT":
            # Move to the next component ID
            bComponentIDFound = False
            for pComponent in gElixys.GetSequence(sRemoteUser, nSequenceID)["components"]:
                if bComponentIDFound:
                    sClientState = sType + "." + str(nSequenceID) + "." + str(pComponent["id"])
                    gElixys.SaveClientState(sRemoteUser, sClientState)
                    return sClientState
                elif pComponent["id"] == nComponentID:
                    bComponentIDFound = True
            if bComponentIDFound:
                return sClientState
            raise Exception("Component ID not found in sequence" + str(nComponentID))
        else:
            # Check if the target ID corresponds to one of our sequence components
            for pComponent in gElixys.GetSequence(sRemoteUser, nSequenceID)["components"]:
                if str(pComponent["id"]) == sActionTargetID:
                    # Update the current component and return the latest state to the client
                    sClientState = sType + "." + str(nSequenceID) + "." + str(pComponent["id"])
                    gElixys.SaveClientState(sRemoteUser, sClientState)
                    return sClientState

    # Tell the caller we didn't handle the use case
    return ""

# Handle POST /PROMPT
def HandlePostPrompt(sClientState, sRemoteUser, pBody, nBodyLength):
    # Make sure we are on Prompt
    global gElixys
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
            gElixys.SaveClientState(sRemoteUser, sClientState)
            return HandleGet(sClientState, sRemoteUser, "/state")
    elif sClientState.startswith("PROMPT_COPYSEQUENCE"):
        if sActionTargetID == "COPY":
            # Ignore this button for now
            return HandleGet(sClientState, sRemoteUser, "/state")
        if sActionTargetID == "CANCEL":
            # Switch to the previous state
            sClientState = sClientState.split(";")[1]
            gElixys.SaveClientState(sRemoteUser, sClientState)
            return HandleGet(sClientState, sRemoteUser, "/state")
    elif sClientState.startswith("PROMPT_DELETESEQUENCE"):
        if sActionTargetID == "DELETE":
            # Ignore this button for now
            return HandleGet(sClientState, sRemoteUser, "/state")
        if sActionTargetID == "CANCEL":
            # Switch to the previous state
            sClientState = sClientState.split(";")[1]
            gElixys.SaveClientState(sRemoteUser, sClientState)
            return HandleGet(sClientState, sRemoteUser, "/state")
    elif sClientState.startswith("PROMPT_ABORTSEQUENCERUN"):
        if sActionTargetID == "ABORT":
            # Abort the run and return to the home page
            gElixys.AbortRun(sRemoteUser)
            sClientState = "HOME"
            gElixys.SaveClientState(sRemoteUser, sClientState)
            return HandleGet(sClientState, sRemoteUser, "/state")
        if sActionTargetID == "CANCEL":
            # Switch to the previous state
            sClientState = sClientState.split(";")[1]
            gElixys.SaveClientState(sRemoteUser, sClientState)
            return HandleGet(sClientState, sRemoteUser, "/state")
    elif sClientState.startswith("PROMPT_RUNSEQUENCE"):
        if sActionTargetID == "OK":
            # Run the sequence
            gElixys.RunSequence(sRemoteUser, int(sClientState.split(";")[1]))
            sClientState = gElixys.GetRunState(sRemoteUser)
            gElixys.SaveClientState(sRemoteUser, sClientState)
            return HandleGet(sClientState, sRemoteUser, "/state")
        if sActionTargetID == "CANCEL":
            # Switch to the previous state
            sClientState = sClientState.split(";")[2]
            gElixys.SaveClientState(sRemoteUser, sClientState)
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
            #gElixys.SaveClientState(sRemoteUser, sClientState)
            return HandleGet(sClientState, sRemoteUser, "/state")
        if sActionTargetID == "BACK":
            # Return to the home page
            sClientState = "HOME"
            gElixys.SaveClientState(sRemoteUser, sClientState)
            return HandleGet(sClientState, sRemoteUser, "/state")
    elif sClientState.startswith("PROMPT_MANUALRUN"):
        if sActionTargetID == "OK":
            # Start the manual run
            gElixys.StartManualRun(sRemoteUser)
            sClientState = gElixys.GetRunState(sRemoteUser)
            gElixys.SaveClientState(sRemoteUser, sClientState)
            return HandleGet(sClientState, sRemoteUser, "/state")
        if sActionTargetID == "CANCEL":
            # Switch to the previous state
            sClientState = sClientState.split(";")[1]
            gElixys.SaveClientState(sRemoteUser, sClientState)
            return HandleGet(sClientState, sRemoteUser, "/state")
    elif sClientState.startswith("PROMPT_ABORTMANUALRUN"):
        if sActionTargetID == "ABORT":
            # Set the client and system states
            sClientState = "HOME"
            gElixys.SaveClientState(sRemoteUser, sClientState)
            gElixys.SaveSystemState(sRemoteUser, "NONE")
            return HandleGet(sClientState, sRemoteUser, "/state")
        if sActionTargetID == "CANCEL":
            # Switch to the previous state
            sClientState = sClientState.split(";")[1]
            gElixys.SaveClientState(sRemoteUser, sClientState)
            return HandleGet(sClientState, sRemoteUser, "/state")
    elif sClientState.startswith("PROMPT_ABORTMANUALOPERATION"):
        if sActionTargetID == "ABORT":
            # Return to the selection step
            sRunState = gElixys.GetRunState(sRemoteUser)
            pRunStateComponents = sRunState.split(".")
            sClientState = "MANUALRUN." + pRunStateComponents[1] + "." + pRunStateComponents[2] + ".SELECT"
            gElixys.SaveRunState(sRemoteUser, sClientState)
            gElixys.SaveClientState(sRemoteUser, sClientState)
            return HandleGet(sClientState, sRemoteUser, "/state")
        if sActionTargetID == "CANCEL":
            # Switch to the previous state
            sClientState = sClientState.split(";")[1]
            gElixys.SaveClientState(sRemoteUser, sClientState)
            return HandleGet(sClientState, sRemoteUser, "/state")
    elif sClientState.startswith("PROMPT_COMPLETEMANUALRUN"):
        if sActionTargetID == "SAVE":
            # Finish the manual run
            gElixys.FinishManualRun(sRemoteUser)
            sClientState = "HOME"
            gElixys.SaveClientState(sRemoteUser, sClientState)
            return HandleGet(sClientState, sRemoteUser, "/state")
        if sActionTargetID == "CANCEL":
            # Switch to the previous state
            sClientState = sClientState.split(";")[1]
            gElixys.SaveClientState(sRemoteUser, sClientState)
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
    global gElixys
    pPathComponents = sPath.split("/")
    nSequenceID = int(pPathComponents[2])
    nComponentID = int(pPathComponents[4])
    nInsertionID = None
    if len(pPathComponents) == 6:
        nInsertionID = int(pPathComponents[5])

    # Save the sequence component
    if nBodyLength != 0:
        pComponent = json.loads(pBody)
    else:
        pComponent = None
    gElixys.SaveSequenceComponent(sRemoteUser, nSequenceID, nComponentID, nInsertionID, pComponent)

    # Is the remote user the one that is currently running the system?
    if sRemoteUser == gElixys.GetRunUser(sRemoteUser):
        # Yes, so advance to the configuration step after adding a new component
        if nComponentID == 0:
            sClientState = "MANUALRUN." + str(nSequenceID) + "." + str(pComponent["id"]) + ".CONFIGURE"
            gElixys.SaveRunState(sRemoteUser, sClientState)
            gElixys.SaveClientState(sRemoteUser, sClientState)

    # Return the new state
    return HandleGet(sClientState, sRemoteUser, "/state")

# Handle POST /sequence/[sequenceid]/reagent/[reagentid]
def HandlePostReagent(sClientState, sRemoteUser, pBody, nBodyLength, sPath):
    # Extract sequence and component IDs
    global gElixys
    pPathComponents = sPath.split("/")
    nSequenceID = int(pPathComponents[2])
    nReagentID = int(pPathComponents[4])

    # Save the sequence component
    pReagent = json.loads(pBody)
    gElixys.SaveSequenceReagent(sRemoteUser, nSequenceID, pReagent)

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

# Main WSGI application entry point
def application(pEnvironment, fStartResponse):
    # Extract important input variables
    global gElixys
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
    sClientState = gElixys.GetClientState(sRemoteUser)
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

    # Send the response
    fStartResponse(sStatus, pHeaders)
    return [sResponseJSON]

# Main function used for local execution
if __name__ == '__main__':
    httpd = make_server('', 80, application)
    print "Serving on port 80..."
    httpd.serve_forever()
