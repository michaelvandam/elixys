#!/usr/bin/python26

# Imports
from wsgiref.simple_server import make_server
import json
from wsgiref.headers import Headers
import sys

# Import and create the core Elixys server
sys.path.append('/var/www/wsgi')
from DummyElixys import Elixys 
gElixys = Elixys()

### Logging function

def Log(sMessage):
    print >> sys.stderr, sMessage

### GET handler functions ###

# Handle all GET requests
def HandleGet(sClientState, sRemoteUser, sPath):
    if sPath == "/configuration":
        return HandleGetConfiguration()
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
def HandleGetConfiguration():
    global gElixys
    pConfig = {"type":"configuration"}
    pConfig.update(gElixys.GetConfiguration())
    pConfig.update({"supportedoperations":gElixys.GetSupportedOperations()})
    return pConfig

# Handdle GET /state request
def HandleGetState(sClientState, sRemoteUser):
    # Start the state with the common fields
    global gElixys
    pUser = {"type":"user"}
    pUser.update(gElixys.GetUser(sRemoteUser))
    pServerState = {"type":"serverstate"}
    pServerState.update(gElixys.GetServerState())
    pState = {"type":"state",
        "user":pUser,
        "serverstate":pServerState,
        "clientstate":gElixys.GetClientState(sRemoteUser)}

    # Complete the state with the values specific to this page
    if sClientState.startswith("HOME"):
        pState.update(HandleGetStateHome())
    elif sClientState.startswith("SELECT_SAVEDSEQUENCES"):
        pState.update(HandleGetStateSelectSavedSequences(sRemoteUser))
    elif sClientState.startswith("SELECT_MANUALRUNS"):
        pState.update(HandleGetStateSelectManualRuns(sRemoteUser))
    elif sClientState.startswith("PROMPT_CREATESEQUENCE"):
        pState.update(HandleGetStateSelectPromptCreateSequence())
    elif sClientState.startswith("PROMPT_COPYSEQUENCE"):
        pState.update(HandleGetStateSelectPromptCopySequence())
    elif sClientState.startswith("PROMPT_DELETESEQUENCE"):
        pState.update(HandleGetStateSelectPromptDeleteSequence())
    elif sClientState.startswith("VIEW"):
        pState.update(HandleGetStateView(sClientState, sRemoteUser))
    elif sClientState.startswith("EDIT"):
        pState.update(HandleGetStateEdit(sClientState, sRemoteUser))
    else:
        raise Exception("Unknown state")

    # Return the state
    return pState

# Handles GET /state request for Home
def HandleGetStateHome():
    return {"buttons":[{"type":"button",
        "text":"Create, view or run a sequence",
        "id":"CREATE"},
        {"type":"button",
        "text":"Operation the system manually",
        "id":"MANUAL"},
        {"type":"button",
        "text":"Observe the current run",
        "id":"OBSERVE"}]}

# Handles GET /state for Select Sequence (both tabs)
def HandleGetStateSelect():
    return {"tabs":[{"type":"tab",
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
            "text":"Run",
            "id":"RUN"},
            {"type":"button",
            "text":"Copy",
            "id":"COPY"}],
        "navigationbuttons":[{"type":"button",
            "text":"Create",
            "id":"CREATE"},
            {"type":"button",
            "text":"Back",
            "id":"BACK"}]}

# Handle GET /state for Select Sequence (Saved Sequences tab)
def HandleGetStateSelectSavedSequences(sRemoteUser):
    global gElixys
    pState = HandleGetStateSelect()
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
    pState = HandleGetStateSelect()
    pState.update({"tabid":"MANUALRUNS"})
    pState.update({"sequences":gElixys.GetSequenceList(sRemoteUser, "Manual")})
    return pState

# Handle GET /state for Select Sequence (Create Sequence prompt)
def HandleGetStateSelectPromptCreateSequence():
    return {"text1":"Enter the name of the new sequence:",
        "edit1":"true",
        "edit1validation":"type=string; required=true",
        "text2":"",
        "edit2":"false",
        "edit2validation":"",
        "buttons":[{"type":"button",
            "text":"Cancel",
            "id":"CANCEL"},
            {"type":"button",
            "text":"Create",
            "id":"CREATE"}]}

# Handle GET /state for Select Sequence (Copy Sequence prompt)
def HandleGetStateSelectPromptCopySequence():
    return {"text1":"Enter the name of the new sequence:",
        "edit1":"true",
        "edit1validation":"type=string; required=true",
        "text2":"",
        "edit2":"false",
        "edit2validation":"",
        "buttons":[{"type":"button",
            "text":"Cancel",
            "id":"CANCEL"},
            {"type":"button",
            "text":"Copy",
            "id":"COPY"}]}

# Handle GET /state for Select Sequence (Delete Sequence prompt)
def HandleGetStateSelectPromptDeleteSequence():
    return {"text1":"Are you sure that you want to permanently delete sequence \"Fake Sequence Name Here\"?",
        "edit1":"false",
        "edit1validation":"",
        "text2":"",
        "edit2":"false",
        "edit2validation":"",
        "buttons":[{"type":"button",
            "text":"Cancel",
            "id":"CANCEL"},
            {"type":"button",
            "text":"Delete",
            "id":"DELETE"}]}

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

    # Create the return object
    return {"navigationbuttons":[{"type":"button",
            "text":"Edit",
            "id":"EDIT"},
            {"type":"button",
            "text":"Run",
            "id":"RUN"},
            {"type":"button",
            "text":"Back",
            "id":"BACK"}],
        "sequenceid":nSequenceID,
        "componentid":nComponentID}

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

    # Create the return object
    return {"navigationbuttons":[{"type":"button",
            "text":"Run",
            "id":"RUN"},
            {"type":"button",
            "text":"Back",
            "id":"BACK"}],
        "sequenceid":nSequenceID,
        "componentid":nComponentID}

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
def HandlePost(sClientState, sRemoteUser, sPath, pBody):
    if sPath == "/HOME":
        return HandlePostHome(sClientState, sRemoteUser, pBody)
    elif sPath == "/SELECT":
        return HandlePostSelect(sClientState, sRemoteUser, pBody)
    elif sPath == "/VIEW":
        return HandlePostView(sClientState, sRemoteUser, pBody)
    elif sPath == "/EDIT":
        return HandlePostEdit(sClientState, sRemoteUser, pBody)
    elif sPath == "/PROMPT":
        return HandlePostPrompt(sClientState, sRemoteUser, pBody)
    if sPath.startswith("/sequence/"):
        if sPath.find("/component/") != -1:
            return HandlePostComponent(sClientState, sRemoteUser, pBody, sPath)
        elif sPath.find("/reagent/") != -1:
            return HandlePostReagent(sClientState, sRemoteUser, pBody, sPath)
        else:
            return HandlePostSequence(sClientState, sRemoteUser, pBody, sPath)
    else:
        raise Exception("Unknown path: " + sPath)

# Handle POST /HOME
def HandlePostHome(sClientState, sRemoteUser, pBody):
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
            # Ignore this button for now
            return HandleGet(sClientState, sRemoteUser, "/state")
        elif sActionTargetID == "OBSERVE":
            # Ignore this button for now
            return HandleGet(sClientState, sRemoteUser, "/state")

    # Unhandled use case
    raise Exception("State misalignment")

# Handle POST /SELECT
def HandlePostSelect(sClientState, sRemoteUser, pBody):
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
            # Ignore this button for now
            return HandleGet(sClientState, sRemoteUser, "/state")
        elif sActionTargetID == "BACK":
            # Switch states to Home
            sClientState = "HOME"
            gElixys.SaveClientState(sRemoteUser, sClientState)
            return HandleGet(sClientState, sRemoteUser, "/state")
        elif sActionTargetID == "CREATE":
            # Switch states to Prompt (Create Sequence)
            sClientState = "PROMPT_CREATESEQUENCE." + sClientState
            gElixys.SaveClientState(sRemoteUser, sClientState)
            return HandleGet(sClientState, sRemoteUser, "/state")
        elif sActionTargetID == "COPY":
            # Switch states to Prompt (Copy Sequence)
            sClientState = "PROMPT_COPYSEQUENCE." + sClientState
            gElixys.SaveClientState(sRemoteUser, sClientState)
            return HandleGet(sClientState, sRemoteUser, "/state")
        elif sActionTargetID == "DELETE":
            # Switch states to Prompt (Delete Sequence)
            sClientState = "PROMPT_DELETESEQUENCE." + sClientState
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
def HandlePostView(sClientState, sRemoteUser, pBody):
    # Make sure we are on View Sequence
    if sClientState.startswith("VIEW") == False:
        raise Exception("State misalignment")

    # Determine our sequence and component IDs
    pClientStateComponents = sClientState.split(".")
    nSequenceID = int(pClientStateComponents[1])
    nComponentID = int(pClientStateComponents[2])

    # Parse the JSON string in the body and check extract the action type and target
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
            # Ignore this button for now
            return HandleGet(sClientState, sRemoteUser, "/state")

    # Unhandled use case
    raise Exception("State misalignment")

# Handle POST /EDIT
def HandlePostEdit(sClientState, sRemoteUser, pBody):
    # Make sure we are on Edit Sequence
    if sClientState.startswith("EDIT") == False:
        raise Exception("State misalignment")

    # Determine our sequence and component IDs
    pClientStateComponents = sClientState.split(".")
    nSequenceID = int(pClientStateComponents[1])
    nComponentID = int(pClientStateComponents[2])

    # Parse the JSON string in the body and check extract the action type and target
    pJSON = json.loads(pBody)
    sActionType = str(pJSON["action"]["type"])
    sActionTargetID = str(pJSON["action"]["targetid"])

    # Call the base sequence POST handler first
    sNewClientState = HandlePostBaseSequence(sClientState, sRemoteUser, "EDIT", nSequenceID, nComponentID, sActionType, sActionTargetID)
    if sNewClientState != "":
        # POST handled
        return HandleGet(sNewClientState, sRemoteUser, "/state")

    # Handle View Sequence specific requests
    if sActionType == "BUTTONCLICK":
        if sActionTargetID == "RUN":
            # Ignore this button for now
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
def HandlePostPrompt(sClientState, sRemoteUser, pBody):
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
            sClientState = sClientState.split(".")[1]
            gElixys.SaveClientState(sRemoteUser, sClientState)
            return HandleGet(sClientState, sRemoteUser, "/state")
    elif sClientState.startswith("PROMPT_COPYSEQUENCE"):
        if sActionTargetID == "COPY":
            # Ignore this button for now
            return HandleGet(sClientState, sRemoteUser, "/state")
        if sActionTargetID == "CANCEL":
            # Switch to the previous state
            sClientState = sClientState.split(".")[1]
            gElixys.SaveClientState(sRemoteUser, sClientState)
            return HandleGet(sClientState, sRemoteUser, "/state")
    elif sClientState.startswith("PROMPT_DELETESEQUENCE"):
        if sActionTargetID == "DELETE":
            # Ignore this button for now
            return HandleGet(sClientState, sRemoteUser, "/state")
        if sActionTargetID == "CANCEL":
            # Switch to the previous state
            sClientState = sClientState.split(".")[1]
            gElixys.SaveClientState(sRemoteUser, sClientState)
            return HandleGet(sClientState, sRemoteUser, "/state")

    # Unhandled use case
    raise Exception("State misalignment")

# Handle POST /sequence/[sequenceid]
def HandlePostSequence(sClientState, sRemoteUser, pBody, sPath):
    # Ignore this function for now
    return HandleGet(sClientState, sRemoteUser, "/state")

# Handle POST /sequence/[sequenceid]/component/[componentid]
def HandlePostComponent(sClientState, sRemoteUser, pBody, sPath):
    # Extract sequence and component IDs
    global gElixys
    pPathComponents = sPath.split("/")
    nSequenceID = int(pPathComponents[2])
    nComponentID = int(pPathComponents[4])

    # Save the sequence component
    pComponent = json.loads(pBody)
    gElixys.SaveSequenceComponent(sRemoteUser, nSequenceID, pComponent)

    # Return the new state
    return HandleGet(sClientState, sRemoteUser, "/state")

# Handle POST /sequence/[sequenceid]/reagent/[reagentid]
def HandlePostReagent(sClientState, sRemoteUser, pBody, sPath):
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
    raise Exception("Implement DELETE")

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

    # Load the client state
    sClientState = gElixys.GetClientState(sRemoteUser)

    # Log the request
    Log("Received " + sRequestMethod + " request for " + sPath + " (client state = " + sClientState + ")");

    # Handle the request
    try:
        # Call the appropriate handler
        if sRequestMethod == "GET":
            sResponse = HandleGet(sClientState, sRemoteUser, sPath)
        elif sRequestMethod == "POST":
            pBodyLength = int(pEnvironment["CONTENT_LENGTH"])
            pBody = pEnvironment["wsgi.input"].read(pBodyLength)
            sResponse = HandlePost(sClientState, sRemoteUser, sPath, pBody)
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
