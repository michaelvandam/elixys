#!/usr/bin/python26

# Imports
from wsgiref.simple_server import make_server
import json
from wsgiref.headers import Headers
import sys
sys.path.append(/var/www/wsgi')
import DummyInterface

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
            return HandleGetComponent(sPath)
        elif sPath.find("/reagent/") != -1:
            return HandleGetReagent(sPath)
        else:
            return HandleGetSequence(sPath)
    else:
        raise Exception("Unknown path: " + sPath)

# Handle GET /configuration
def HandleGetConfiguration():
    pConfig = {"type":"configuration"}
    pConfig.update(DummyInterface.GetConfiguration())
    return pConfig

# Handdle GET /state request
def HandleGetState(sClientState, sRemoteUser):
    # Start the state with the common fields
    pUser = {"type":"user"}
    pUser.update(DummyInterface.GetUser(sRemoteUser))
    pServerState = {"type":"serverstate"}
    pServerState.update(DummyInterface.GetServerState())
    pState = {"type":"state",
        "user":pUser,
        "serverstate":pServerState,
        "clientstate":DummyInterface.GetClientState()}

    # Complete the state with the values specific to this page
    if sClientState.startswith("HOME"):
        pState.update(HandleGetStateHome())
    elif sClientState.startswith("SELECT_SAVEDSEQUENCES"):
        pState.update(HandleGetStateSelectSavedSequences())
    elif sClientState.startswith("SELECT_MANUALRUNS"):
        pState.update(HandleGetStateSelectManualRuns())
    elif sClientState.startswith("PROMPT_CREATESEQUENCE"):
        pState.update(HandleGetStateSelectPromptCreateSequence())
    elif sClientState.startswith("PROMPT_COPYSEQUENCE"):
        pState.update(HandleGetStateSelectPromptCopySequence())
    elif sClientState.startswith("PROMPT_DELETESEQUENCE"):
        pState.update(HandleGetStateSelectPromptDeleteSequence())
    elif sClientState.startswith("VIEW"):
        pState.update(HandleGetStateView(sClientState))
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

# Handles GET /state for Select Sequence
def HandleGetStateSelectSavedSequences():
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
            "id":"COPY"},
            {"type":"button",
            "text":"Delete",
            "id":"DELETE"}],
        "navigationbuttons":[{"type":"button",
            "text":"Create",
            "id":"CREATE"},
            {"type":"button",
            "text":"Back",
            "id":"BACK"}]}

# Handle GET /state for Select Sequence (Saved Sequences tab)
def HandleGetStateSelectSavedSequences():
    pState = HandleGetStateSelect()
    pState.update({"tabid":"SAVEDSEQUENCES"})
    pState.update({"sequences":DummyInterface.GetSequenceList("Saved")})
    return pState

# Handle GET /state for Select Sequence (Manual Runs tab)
def HandleGetStateSelectManualRuns():
    pState = HandleGetStateSelect()
    pState.update({"tabid":"MANUALRUNS"})
    pState.update({"sequences":DummyInterface.GetSequenceList("Manual")})
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
def HandleGetStateView(sClientState):
    pClientStateComponents = sClientState.split(".")
    return {"navigationbuttons":[{"type":"button",
            "text":"Edit",
            "id":"EDIT"},
            {"type":"button",
            "text":"Run",
            "id":"RUN"},
            {"type":"button",
            "text":"Back",
            "id":"BACK"}],
        "sequenceid":25,
        "componentid":int(pClientStateComponents[1])}

# Handle GET /sequence/[sequenceid]
def HandleGetSequence(sPath):
    # Extract sequence ID
    pPathComponents = sPath.split("/")
    nSequenceID = int(pPathComponents[1])

    # Load the entire sequence
    pSequence = DummerInterface.GetSequence(nSequenceID, 0)

    # Remove excess sequence data

    # Return cleanedd sequence
    return pSequence

# Handle GET /sequence/[sequenceid]/component/[componentid]
def HandleGetComponent(sPath):
    # Extract sequence and component IDs
    pPathComponents = sPath.split("/")
    nSequenceID = int(pPathComponents[1])
    nComponentID = int(pPathComponents[3])

    # Load the sequence and only the desired component
    pSequence = DummyInterface.GetSequence(nSequenceID, nComponentID)

    # Add component-specific information...
    pComponent = {"type":"component"}
    pComponent.update(pSequence["component"][0])

    # Return the complete component
    return pComponent

# Handle GET /sequence/[sequenceid]/reagent/[reagentid]
def HandleGetReagent(sPath):
    # Extract sequence and reagent IDs
    pPathComponents = sPath.split("/")
    nSequenceID = int(pPathComponents[1])
    nReagentID = int(pPathComponents[3])

    # Return the sequence reagent
    pReagent = {"type":"reagent"}
    pReagent.update(DummyInterface.GetReagent(nSequenceID, nReagentID))

### POST handler functions ###

# Handle all POST requests
def HandlePost(sClientState, sRemoteUser, sPath, pBody):
    if sPath == "/HOME":
        return HandlePostHome(sClientState, sRemoteUser, pBody)
    elif sPath == "/SELECT":
        return HandlePostSelect(sClientState, sRemoteUser, pBody)
    elif sPath == "/VIEW":
        return HandlePostView(sClientState, sRemoteUser, pBody)
    elif sPath == "/PROMPT":
        return HandlePostPrompt(sClientState, sRemoteUser, pBody)
    else:
        raise Exception("Unknown path: " + sPath)

# Handle POST /HOME
def HandlePostHome(sClientState, sRemoteUser, pBody):
    # Make sure we are on the home page
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
            DummyInterface.SaveClientState(sClientState)
            return HandleGet(sClientState, sRemoteUser, "/state")
        elif sActionTargetID == "MANUAL":
            # Ignore this button for now
            return HandleGet(sClientState, sRemoteUser, "/state")
        elif sActionTargetID == "OBSERVE":
            # Ignore this button for now
            return HandleGet(sClientState, sRemoteUser, "/state")

    # Unhandled use case
    raise Exception("State misalignment")

#def HandlePostSelect(nState, sRemoteUser, pBody):
#    # Make sure we are on the select page
#    if (nState != STATE_SELECT_SAVEDSEQUENCES) and (nState != STATE_SELECT_MANUALRUNS):
#        raise Exception("State misalignment");
#
#    # Parse the JSON string in the body
#    pJSON = json.loads(pBody)
#
#    # Check which option the user selected
#    sActionType = str(pJSON["action"]["type"])
#    sActionTargetID = str(pJSON["action"]["targetid"])
#    sSequenceID = str(pJSON["sequenceid"])
#    if sActionType == "BUTTONCLICK":
#        if sActionTargetID == "VIEW":
#            # Update our state and return it to the client
#            nState = STATE_VIEW
#            SaveState(nState)
#            return HandleGet(nState, sRemoteUser, "/state")
#        elif sActionTargetID == "BACK":
#            # Update our state and return it to the client
#            nState = STATE_HOME
#            SaveState(nState)
#            return HandleGet(nState, sRemoteUser, "/state")
#        elif sActionTargetID == "CREATE":
#            # Update our state and return it to the client
#            nState = STATE_PROMPT_CREATESEQUENCE
#            SaveState(nState)
#            return HandleGet(nState, sRemoteUser, "/state")
#        elif sActionTargetID == "COPY":
#            # Update our state and return it to the client
#            nState = STATE_PROMPT_COPYSEQUENCE
#            SaveState(nState)
#            return HandleGet(nState, sRemoteUser, "/state")
#        elif sActionTargetID == "DELETE":
#            # Update our state and return it to the client
#            nState = STATE_PROMPT_DELETESEQUENCE
#            SaveState(nState)
#            return HandleGet(nState, sRemoteUser, "/state")
#        else:
#            # Do nothing but return the state to the client
#            return HandleGet(nState, sRemoteUser, "/state")
#    elif sActionType == "TABCLICK":
#        if sActionTargetID == "SAVEDSEQUENCES":
#            # Update our state and return it to the client
#            nState = STATE_SELECT_SAVEDSEQUENCES
#            SaveState(nState)
#            return HandleGet(nState, sRemoteUser, "/state")
#        elif sActionTargetID == "MANUALRUNS":
#            # Update our state and return it to the client
#            nState = STATE_SELECT_MANUALRUNS
#            SaveState(nState)
#            return HandleGet(nState, sRemoteUser, "/state")
#
#    # Unhandled use case
#    raise Exception("State misalignment")
#
#def HandlePostView(nState, sRemoteUser, pBody):
#    # Make sure we are on the view page
#    global gSequence
#    if nState != STATE_VIEW:
#        raise Exception("State misalignment")
#
#    # Parse the JSON string in the body
#    pJSON = json.loads(pBody)
#
#    # Check which option the user selected
#    sActionType = str(pJSON["action"]["type"])
#    sActionTargetID = str(pJSON["action"]["targetid"])
#    if sActionType == "BUTTONCLICK":
#        if sActionTargetID == "BACK":
#            # Update our state and return it to the client
#            nState = STATE_SELECT_SAVEDSEQUENCES
#            SaveState(nState)
#            return HandleGet(nState, sRemoteUser, "/state")
#        elif sActionTargetID == "PREVIOUS":
#            # Move to the previous component ID
#            sCurrentComponentID = LoadComponentID()
#            sPreviousComponentID = -1
#            for pComponent in gSequence:
#                if pComponent["id"] == str(sCurrentComponentID):
#                    if sPreviousComponentID != -1:
#                        SaveComponentID(sPreviousComponentID)
#                    return HandleGet(nState, sRemoteUser, "/state")
#                else:
#                    sPreviousComponentID = pComponent["id"]
#            raise Exception("Component ID not found in sequence")
#        elif sActionTargetID == "NEXT":
#            # Move to the next component ID
#            sCurrentComponentID = LoadComponentID()
#            bComponentIDFound = False
#            for pComponent in gSequence:
#                if bComponentIDFound:
#                    SaveComponentID(pComponent["id"])
#                    return HandleGet(nState, sRemoteUser, "/state")
#                elif pComponent["id"] == str(sCurrentComponentID):
#                    bComponentIDFound = True
#            if bComponentIDFound:
#                return HandleGet(nState, sRemoteUser, "/state")
#            raise Exception("Component ID not found in sequence")
#        else:
#            # Check if the target ID corresponds to one of our sequence components
#            for pComponent in gSequence:
#                if pComponent["id"] == sActionTargetID:
#                    # Update the current component and return the latest state to the client
#                    SaveComponentID(pComponent["id"])
#                    return HandleGet(nState, sRemoteUser, "/state")
#
#    # Unhandled use case
#    raise Exception("State misalignment")
#
#def HandlePostPrompt(nState, sRemoteUser, pBody):
#    # Parse the JSON string in the body
#    pJSON = json.loads(pBody)
#
#    # Extract the post parameters
#    sActionType = str(pJSON["action"]["type"])
#    sActionTargetID = str(pJSON["action"]["targetid"])
#    sEdit1 = str(pJSON["edit1"])
#    sEdit2 = str(pJSON["edit2"])
#
#    # The only recognized action from a prompt is a button click
#    if sActionType != "BUTTONCLICK":
#        raise Exception("State misalignment")
#
#    # Interpret the response in context of the client state
#    nState = LoadState()
#    if nState == STATE_PROMPT_CREATESEQUENCE:
#        if sActionTargetID == "CREATE":
#            # Update our state and return it to the client
#            nState = STATE_SELECT_SAVEDSEQUENCES
#            SaveState(nState)
#            return HandleGet(nState, sRemoteUser, "/state")
#        if sActionTargetID == "CANCEL":
#            # Update our state and return it to the client
#            nState = STATE_SELECT_SAVEDSEQUENCES
#            SaveState(nState)
#            return HandleGet(nState, sRemoteUser, "/state")
#    elif nState == STATE_PROMPT_COPYSEQUENCE:
#        if sActionTargetID == "COPY":
#            # Update our state and return it to the client
#            nState = STATE_SELECT_SAVEDSEQUENCES
#            SaveState(nState)
#            return HandleGet(nState, sRemoteUser, "/state")
#        if sActionTargetID == "CANCEL":
#            # Update our state and return it to the client
#            nState = STATE_SELECT_SAVEDSEQUENCES
#            SaveState(nState)
#            return HandleGet(nState, sRemoteUser, "/state")
#    elif nState == STATE_PROMPT_DELETESEQUENCE:
#        if sActionTargetID == "DELETE":
#            # Update our state and return it to the client
#            nState = STATE_SELECT_SAVEDSEQUENCES
#            SaveState(nState)
#            return HandleGet(nState, sRemoteUser, "/state")
#        if sActionTargetID == "CANCEL":
#            # Update our state and return it to the client
#            nState = STATE_SELECT_SAVEDSEQUENCES
#            SaveState(nState)
#            return HandleGet(nState, sRemoteUser, "/state")
#
#    # Unhandled use case
#    raise Exception("State misalignment")

# Handle DELETE requests
def HandleDelete(sClientState, sRemoteUser, sPath):
    raise Exception("Implement DELETE")

# Main WSGI application entry point
def application(pEnvironment, fStartResponse):
    # Load the client state
    sClientState = DummyInterface.LoadClientState()

    # Extract important input variables
    if pEnvironment.has_key("REMOTE_USER"):
        sRemoteUser = pEnvironment["REMOTE_USER"]
    else:
        sRemoteUser = "devel"    # Debugging hack: use "devel" as default user
    sRequestMethod = pEnvironment["REQUEST_METHOD"]
    sPath = pEnvironment["PATH_INFO"]
    if sPath.startswith("/Elixys"):
        # Debugging hack: trim off any leading "/Elixys" string
        sPath = sPath[7:]

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

