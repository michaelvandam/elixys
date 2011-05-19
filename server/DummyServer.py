#!/usr/bin/python26

# Imports
from wsgiref.simple_server import make_server
import json
from wsgiref.headers import Headers

# States
STATE_HOME = 0
STATE_SELECT_SAVEDSEQUENCES = 1
STATE_SELECT_MANUALRUNS = 2

# User state
gState = STATE_HOME

# Handle GET requests
def HandleGet(sRemoteUser, sPath):
    if sPath == "/configuration":
        return HandleGetConfiguration(sRemoteUser);
    if sPath == "/state":
        return HandleGetState(sRemoteUser);
    else:
        raise Exception("Unknown path: " + sPath);

# Handle GET configuration request
def HandleGetConfiguration(sRemoteUser):
    pConfig = {"type":"configuration",
        "name":"Mini cell 3",
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
            "Activity"]};

    return pConfig;

def HandleGetState(sRemoteUser):
    global gState
    if gState == STATE_HOME:
        return HandleGetStateHome(sRemoteUser)
    elif gState == STATE_SELECT_SAVEDSEQUENCES:
        return HandleGetStateSelectSavedSequences(sRemoteUser)
    elif gState == STATE_SELECT_MANUALRUNS:
        return HandleGetStateSelectManualRuns(sRemoteUser)
    else:
        raise Exception("Unknown state")

def HandleGetStateHome(sRemoteUser):
    return {"type":"state",
        "user":{"type":"user",
            "username":"devel",
            "useraccesslevel":"Administrator"},
        "serverstate":{"type":"serverstate"},
        "clientstate":"HOME",
        "clientdetails":{"type":"HOME",
            "buttons":[{"type":"button",
                "text":"Create, view or run a sequence",
                "id":"CREATE"},
                {"type":"button",
                "text":"Operation the system manually",
                "id":"MANUAL"},
                {"type":"button",
                "text":"Observe the current run",
                "id":"OBSERVE"}]}}

def HandleGetStateSelectSavedSequences(sRemoteUser):
    return {"type":"state",
        "user":{"type":"user",
            "username":"devel",
            "useraccesslevel":"Administrator"},
        "serverstate":{"type":"serverstate"},
        "clientstate":"SELECT",
        "clientdetails":{"type":"SELECT",
            "tabs":[{"type":"tab",
                "text":"Saved Sequences",
                "id":"SAVEDSEQUENCES"},
                {"type":"tab",
                "text":"Manual Runs",
                "id":"MANUALRUNS"}],
            "tabid":"SAVEDSEQUENCES",
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
                "id":"BACK"}],
            "sequences":CreateSequenceArray()}}

def HandleGetStateSelectManualRuns(sRemoteUser):
    return {"type":"state",
        "user":{"type":"user",
            "username":"devel",
            "useraccesslevel":"Administrator"},
        "serverstate":{"type":"serverstate"},
        "clientstate":"SELECT",
        "clientdetails":{"type":"SELECT",
            "tabs":[{"type":"tab",
                "text":"Saved Sequences",
                "id":"SAVEDSEQUENCES"},
                {"type":"tab",
                "text":"Manual Runs",
                "id":"MANUALRUNS"}],
            "tabid":"MANUALRUNS",
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
                "id":"BACK"}],
            "sequences":CreateSequenceArray()}}

def CreateSequenceArray():
    pSequences = []
    for x in range(0, 25):
        pSequence = {"type":"sequencemetadata",
            "name":"FAC (" + str(x) + ")",
            "time":"8:00",
            "date":"05/01/2012",
            "comment":"Experimental FAC synthesis using high temperatures (" + str(x) + ")",
            "id":"108" + str(x),
            "creator":"devel",
            "operations":"17"}
        pSequences.append(pSequence)
 
    return pSequences

# Handle POST requests
def HandlePost(sRemoteUser, sPath, pBody):
    if sPath == "/HOME":
        return HandlePostHome(sRemoteUser, pBody);
    elif sPath == "/SELECT":
        return HandlePostSelect(sRemoteUser, pBody);
    else:
        raise Exception("Unknown path: " + sPath);

def HandlePostHome(sRemoteUser, pBody):
    # Make sure we are on the home page
    global gState
    if gState != STATE_HOME:
        raise Exception("State misalignment");

    # Parse the JSON string in the body
    pJSON = json.loads(pBody)

    # Check which option the user selected
    sActionType = str(pJSON["action"]["type"])
    sActionTargetID = str(pJSON["action"]["targetid"])
    if sActionType == "BUTTONCLICK":
        if sActionTargetID == "CREATE":
            # Update our state and return it to the client
            gState = STATE_SELECT_SAVEDSEQUENCES
            return HandleGet(sRemoteUser, "/state")
        elif sActionTargetID == "MANUAL":
            # Do nothing but return the state to the client
            return HandleGet(sRemoteUser, "/state")
        elif sActionTargetID == "OBSERVE":
            # Do nothing but return the state to the client
            return HandleGet(sRemoteUser, "/state")

    # Unhandled use case
    raise Exception("State misalignment")

def HandlePostSelect(sRemoteUser, pBody):
    # Make sure we are on the select page
    global gState
    if (gState != STATE_SELECT_SAVEDSEQUENCES) and (gState != STATE_SELECT_MANUALRUNS):
        raise Exception("State misalignment");

    # Parse the JSON string in the body
    pJSON = json.loads(pBody)

    # Check which option the user selected
    sActionType = str(pJSON["action"]["type"])
    sActionTargetID = str(pJSON["action"]["targetid"])
    if sActionType == "BUTTONCLICK":
        if sActionTargetID == "BACK":
            # Update our state and return it to the client
            gState = STATE_HOME
            return HandleGet(sRemoteUser, "/state")
        else:
            # Do nothing but return the state to the client
            return HandleGet(sRemoteUser, "/state")
    elif sActionType == "TABCLICK":
        if sActionTargetID == "SAVEDSEQUENCES":
            # Update our state and return it to the client
            gState = STATE_SELECT_SAVEDSEQUENCES
            return HandleGet(sRemoteUser, "/state")
        elif sActionTargetID == "MANUALRUNS":
            # Update our state and return it to the client
            gState = STATE_SELECT_MANUALRUNS
            return HandleGet(sRemoteUser, "/state")

    # Unhandled use case
    raise Exception("State misalignment")

# Handle DELETE requests
def HandleDelete(sRemoteUser, sPath):
    return "DELETE"

# Main WSGI application entry point
def application(pEnvironment, fStartResponse):
    # Extract important input variables
    sRemoteUser = pEnvironment["REMOTE_USER"]
    sRequestMethod = pEnvironment["REQUEST_METHOD"]
    sPath = pEnvironment["PATH_INFO"]

    # Handle the request
    try:
        # Call the appropriate handler
        if sRequestMethod == "GET":
            sResponse = HandleGet(sRemoteUser, sPath)
        elif sRequestMethod == "POST":
            pBodyLength = int(pEnvironment["CONTENT_LENGTH"])
            pBody = pEnvironment["wsgi.input"].read(pBodyLength)
            sResponse = HandlePost(sRemoteUser, sPath, pBody)
        elif sRequestMethod == "DELETE":
            sResponse = HandleDelete(sRemoteUser, sPath)
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
    return sResponseJSON

# Main function used for local execution
if __name__ == '__main__':
    httpd = make_server('', 80, application)
    print "Serving on port 80..."
    httpd.serve_forever()

