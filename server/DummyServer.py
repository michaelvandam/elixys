#!/usr/bin/python26

# Imports
from wsgiref.simple_server import make_server
import json
from wsgiref.headers import Headers
from threading import Lock

# States
STATE_HOME = 0
STATE_SELECT_SAVEDSEQUENCES = 1
STATE_SELECT_MANUALRUNS = 2
STATE_VIEW = 3

# User state
gState = STATE_HOME
gStateMutex = Lock()
gComponentID = "1"

# Sequence that exists only in memory
gSequenceMetadata = {"type":"sequencemetadata",
    "name":"FAC synthesis",
    "time":"8:00",
    "date":"05/01/2012",
    "comment":"Routine FAC synthesis",
    "id":"1",
    "creator":"devel",
    "operations":"17"}
gSequence = [{"type":"component",
    "componenttype":"CASSETTE",
    "name":"Cassette 1",
    "id":"1",
    "reactor":"1",
    "reactordescription":"Reactor associated with this cassette",
    "reactorvalidation":"",
    "used":"true",
    "reagents":["1",
        "2",
        "3",
        "4",
        "5",
        "6",
        "7",
        "8"]},
    {"type":"component",
    "componenttype":"CASSETTE",
    "name":"Cassette 2",
    "id":"2",
    "reactor":"2",
    "reactordescription":"Reactor associated with this cassette",
    "reactorvalidation":"",
    "used":"true",
    "reagents":["9",
        "10",
        "11",
        "12",
        "13",
        "14",
        "15",
        "16"]},
    {"type":"component",
    "componenttype":"CASSETTE",
    "name":"Cassette 3",
    "id":"3",
    "reactor":"3",
    "reactordescription":"Reactor associated with this cassette",
    "reactorvalidation":"",
    "used":"false",
    "reagents":["17",
        "18",
        "19",
        "20",
        "21",
        "22",
        "23",
        "24"]},
    {"type":"component",
    "componenttype":"ADD",
    "name":"Add F-18",
    "id":"4",
    "reactor":"1",
    "reactordescription":"Reactor where the reagent will be added",
    "reactorvalidation":"type=enum-literal; values=1,2,3; required=true",
    "reagent":"344",
    "reagentdescription":"Reagent to add to the reactor",
    "reagentvalidation":"type=enum-reagent; values=211,212,213; required=true"},
    {"type":"component",
    "componenttype":"EVAPORATE",
    "name":"Evaporate",
    "id":"5",
    "reactor":"1",
    "reactordescription":"Reactor where the reagent will be added",
    "reactorvalidation":"type=enum-literal; values=1,2,3; required=true",
    "duration":"00:05.00",
    "durationdescription":"Evaporation duration after the target temperature is reached",
    "durationvalidation":"type=time; min=00:00.00; max=02:00.00; required=true",
    "evaporationtemperature":"165.0",
    "evaporationtemperaturedescription":"Evaporation temperature in degrees Celsius",
    "evaporationtemperaturevalidation":"type=temperature, min=20; max=200; required=true",
    "finaltemperature":"35.0",
    "finaltemperaturedescription":"Final temperature after evaporation in degrees Celsius",
    "finaltemperaturevalidation":"type=temperature; min=20; max=200; required=true",
    "stirspeed":"500",
    "stirspeeddescription":"Speed of the stir bar in rotations per minute",
    "stirespeedvalidation":"type=speed; min=0; max=5000; required=true"},
    {"type":"component",
    "componenttype":"TRANSFER",
    "name":"Transfer",
    "id":"6",
    "reactor":"1",
    "reactordescription":"Reactor whose contents will be transferred",
    "reactorvalidation":"type=enum-literal; values=1,2,3; required=true",
    "target":"321",
    "targetdescription":"Target where the reactor contents will be transferred",
    "targetvalidation":"type=enum-target; values=321; required=true"},
    {"type":"component",
    "componenttype":"ELUTE",
    "name":"Elute",
    "id":"7",
    "reactor":"1",
    "reactordescription":"Reactor where the reagent will be eluted",
    "reactorvalidation":"type=enum-literal; values=1,2,3; required=true",
    "reagent":"12",
    "reagentdescription":"Reagent used for elution",
    "reagentvalidation":"type=enum-reagent; values=12,23,34; required=true",
    "target":"321",
    "targetdescription":"Target through which the eluent will be passed",
    "targetvalidation":"type=enum-target; values=321; required=true"},
    {"type":"component",
    "componenttype":"REACT",
    "name":"React",
    "id":"8",
    "reactor":"1",
    "reactordescription":"Reactor where the reagent will be added",
    "reactorvalidation":"type=enum-literal; values=1,2,3; required=true",
    "position":"1",
    "positiondescription":"Position where the reaction will take place",
    "positionvalidation":"type=enum-literal; values=1,2; required=true",
    "duration":"00:04.30",
    "durationdescription":"Evaporation duration after the target temperature is reached",
    "durationvalidation":"type=time; min=00:00.00; max=02:00.00; required=true",
    "reactiontemperature":"165.0",
    "reactiontemperaturedescription":"Reaction temperature in degrees Celsius",
    "reactiontemperaturevalidation":"type=temperature; min=20; max=200; required=true",
    "finaltemperature":"35.0",
    "finaltemperaturedescription":"Final temperature after evaporation in degrees Celsius",
    "finaltemperaturevalidation":"type=temperature; min=20; max=200; required=true",
    "stirspeed":"500",
    "stirspeeddescription":"Speed of the stir bar in rotations per minute",
    "stirespeedvalidation":"type=speed; min=0; max=5000; required=true"},
    {"type":"component",
    "componenttype":"PROMPT",
    "name":"Prompt",
    "id":"9",
    "reactor":"",
    "reactordescription":"",
    "reactorvalidation":"",
    "message":"Please take a sample for analysis",
    "messagevalidation":"type=string; required=true"},
    {"type":"component",
    "componenttype":"INSTALL",
    "name":"Install",
    "id":"10",
    "reactor":"1",
    "reactordescription":"Reactor that will be moved to the install position",
    "reactorvalidation":"type=enum-literal; values=1,2,3; required=true",
    "message":"Take a radiation measurement",
    "messageerror":""},
    {"type":"component",
    "componenttype":"COMMENT",
    "name":"Comment",
    "id":"11",
    "reactor":"",
    "reactordescription":"",
    "reactorvalidation":"",
    "comment":"Bromination and cytosine coupling",
    "commentdescription":"Enter a comment",
    "commentvalidation":"type=string"},
    {"type":"component",
    "componenttype":"ACTIVITY",
    "name":"Activity",
    "id":"12",
    "reactor":"1",
    "reactordescription":"Reactor where the radioactivity will be measured",
    "reactorvalidation":"type=enum-literal; values=1,2,3; required=true"}]
gReagents = [{"type":"reagent",
    "used":"true",
    "componentid":"1",
    "position":"1",
    "name":"F-18",
    "nameerror":"",
    "description":"[18F]F-, 10 mg Kryptofix (K222) and 1.0 mg potassium carbonate (K2CO3) in acetonitrile (MeCN)",
    "descriptionerror":"",
    "id":"1"},
    {"type":"reagent",
    "used":"true",
    "componentid":"1",
    "position":"2",
    "name":"MeCN1",
    "nameerror":"",
    "description":"Acetonitrile",
    "descriptionerror":"",
    "id":"2"},
    {"type":"reagent",
    "used":"true",
    "componentid":"1",
    "position":"3",
    "name":"MeCN2",
    "nameerror":"",
    "description":"Acetonitrile",
    "descriptionerror":"",
    "id":"3"},
    {"type":"reagent",
    "used":"true",
    "componentid":"1",
    "position":"4",
    "name":"MeCN3",
    "nameerror":"",
    "description":"Acetonitrile",
    "descriptionerror":"",
    "id":"4"},
    {"type":"reagent",
    "used":"true",
    "componentid":"1",
    "position":"5",
    "name":"H2O1",
    "nameerror":"",
    "description":"Water",
    "descriptionerror":"",
    "id":"5"},
    {"type":"reagent",
    "used":"true",
    "componentid":"1",
    "position":"6",
    "name":"H2O2",
    "nameerror":"",
    "description":"Water",
    "descriptionerror":"",
    "id":"6"},
    {"type":"reagent",
    "used":"true",
    "componentid":"1",
    "position":"7",
    "name":"HBr",
    "nameerror":"",
    "description":"Hydrobromic acid",
    "descriptionerror":"",
    "id":"7"},
    {"type":"reagent",
    "used":"false",
    "componentid":"1",
    "position":"8",
    "name":"",
    "nameerror":"",
    "description":"",
    "descriptionerror":"",
    "id":"8"},
    {"type":"reagent",
    "used":"true",
    "componentid":"2",
    "position":"1",
    "name":"C6H12O6",
    "nameerror":"",
    "description":"Sugar (yum!)",
    "descriptionerror":"",
    "id":"9"},
    {"type":"reagent",
    "used":"true",
    "componentid":"2",
    "position":"2",
    "name":"HCl",
    "nameerror":"",
    "description":"Hydrochloric acid",
    "descriptionerror":"",
    "id":"10"},
    {"type":"reagent",
    "used":"false",
    "componentid":"2",
    "position":"3",
    "name":"",
    "nameerror":"",
    "description":"",
    "descriptionerror":"",
    "id":"11"},
    {"type":"reagent",
    "used":"true",
    "componentid":"2",
    "position":"4",
    "name":"H2",
    "nameerror":"",
    "description":"Hydrogen gas",
    "descriptionerror":"",
    "id":"12"},
    {"type":"reagent",
    "used":"false",
    "componentid":"2",
    "position":"5",
    "name":"",
    "nameerror":"",
    "description":"",
    "descriptionerror":"",
    "id":"13"},
    {"type":"reagent",
    "used":"true",
    "componentid":"2",
    "position":"6",
    "name":"KCl",
    "nameerror":"",
    "description":"Potassium chloride",
    "descriptionerror":"",
    "id":"14"},
    {"type":"reagent",
    "used":"false",
    "componentid":"2",
    "position":"7",
    "name":"",
    "nameerror":"",
    "description":"",
    "descriptionerror":"",
    "id":"15"},
    {"type":"reagent",
    "used":"true",
    "componentid":"1",
    "position":"8",
    "name":"N2",
    "nameerror":"",
    "description":"Liquid nitrogen",
    "descriptionerror":"",
    "id":"16"}]

def HandleGet(sRemoteUser, sPath):
    if sPath == "/configuration":
        return HandleGetConfiguration(sRemoteUser)
    if sPath == "/state":
        return HandleGetState(sRemoteUser)
    if sPath.startswith("/sequence/"):
        if sPath.find("/component/") != -1:
            return HandleGetComponent(sRemoteUser, sPath)
        elif sPath.find("/reagent/") != -1:
            return HandleGetReagent(sRemoteUser, sPath)
        else:
            return HandleGetSequence(sRemoteUser, sPath)
    else:
        raise Exception("Unknown path: " + sPath)

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
    elif gState == STATE_VIEW:
        return HandleGetStateView(sRemoteUser)
    else:
        raise Exception("Unknown state")

def HandleGetStateHome(sRemoteUser):
    return {"type":"state",
        "user":{"type":"user",
            "username":"devel",
            "useraccesslevel":"Administrator"},
        "serverstate":{"type":"serverstate"},
        "clientstate":"HOME",
        "buttons":[{"type":"button",
            "text":"Create, view or run a sequence",
            "id":"CREATE"},
            {"type":"button",
            "text":"Operation the system manually",
            "id":"MANUAL"},
            {"type":"button",
            "text":"Observe the current run",
            "id":"OBSERVE"}]}

def HandleGetStateSelectSavedSequences(sRemoteUser):
    return {"type":"state",
        "user":{"type":"user",
            "username":"devel",
            "useraccesslevel":"Administrator"},
        "serverstate":{"type":"serverstate"},
        "clientstate":"SELECT",
        "tabs":[{"type":"tab",
            "text":"Saved Sequences",
            "id":"SAVEDSEQUENCES",
            "columns":["name:Name", "comment:Comment"]},
            {"type":"tab",
            "text":"Manual Runs",
            "id":"MANUALRUNS",
            "columns":["date:Date", "creator:User", "name:Name", "comment:Comment"]}],
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
        "sequences":CreateSequenceArray()}

def HandleGetStateSelectManualRuns(sRemoteUser):
    return {"type":"state",
        "user":{"type":"user",
            "username":"devel",
            "useraccesslevel":"Administrator"},
        "serverstate":{"type":"serverstate"},
        "clientstate":"SELECT",
        "tabs":[{"type":"tab",
            "text":"Saved Sequences",
            "id":"SAVEDSEQUENCES",
            "columns":["name:Name", "comment:Comment"]},
            {"type":"tab",
            "text":"Manual Runs",
            "id":"MANUALRUNS",
            "columns":["date:Date", "creator:User", "name:Name", "comment:Comment"]}],
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
        "sequences":CreateSequenceArray()}

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

def HandleGetStateView(sRemoteUser):
    global gComponentID
    return {"type":"state",
        "user":{"type":"user",
            "username":"devel",
            "useraccesslevel":"Administrator"},
        "serverstate":{"type":"serverstate"},
        "clientstate":"VIEWSEQUENCE",
        "navigationbuttons":[{"type":"button",
            "text":"Edit",
            "id":"EDIT"},
            {"type":"button",
            "text":"Run",
            "id":"RUN"},
            {"type":"button",
            "text":"Back",
            "id":"BACK"}],
        "sequenceid":"25",
        "componentid":gComponentID}

def HandleGetSequence(sRemoteUser, sPath):
    global gSequenceMetadata
    global gSequence
    pReturn = {"type":"sequence",
        "metadata":gSequenceMetadata,
        "components":[]}
    for pComponent in gSequence:
        pReturn["components"].append({"type":"sequencecomponent",
            "name":pComponent["name"],
            "id":pComponent["id"],
            "componenttype":pComponent["componenttype"],
            "validationerror":"false"})
    return pReturn

def HandleGetComponent(sRemoteUser, sPath):
    global gSequence
    nIndex = sPath.find("/component/") + 11
    nComponent = int(sPath[nIndex:])
    return gSequence[nComponent - 1]

def HandleGetReagent(sRemoteUser, sPath):
    global gReagents
    nIndex = sPath.find("/reagent/") + 9
    nReagent = int(sPath[nIndex:])
    return gReagents[nReagent - 1]

def HandlePost(sRemoteUser, sPath, pBody):
    if sPath == "/HOME":
        return HandlePostHome(sRemoteUser, pBody)
    elif sPath == "/SELECT":
        return HandlePostSelect(sRemoteUser, pBody)
    elif sPath == "/VIEW":
        return HandlePostView(sRemoteUser, pBody)
    else:
        raise Exception("Unknown path: " + sPath)

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
    sSequenceID = str(pJSON["sequenceid"])
    if sActionType == "BUTTONCLICK":
        if sActionTargetID == "VIEW":
            # Update our state and return it to the client
            gState = STATE_VIEW
            return HandleGet(sRemoteUser, "/state")
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

def HandlePostView(sRemoteUser, pBody):
    # Make sure we are on the view page
    global gState
    global gSequence
    global gComponentID
    if gState != STATE_VIEW:
        raise Exception("State misalignment")

    # Parse the JSON string in the body
    pJSON = json.loads(pBody)

    # Check which option the user selected
    sActionType = str(pJSON["action"]["type"])
    sActionTargetID = str(pJSON["action"]["targetid"])
    if sActionType == "BUTTONCLICK":
        if sActionTargetID == "BACK":
            # Update our state and return it to the client
            gState = STATE_SELECT_SAVEDSEQUENCES
            return HandleGet(sRemoteUser, "/state")
        else:
            # Check if the target ID corresponds to one of our sequence components
            for pComponent in gSequence:
                if pComponent["id"] == sActionTargetID:
                    # Update the current component and return the latest state to the client
                    gComponentID = pComponent["id"]
                    return HandleGet(sRemoteUser, "/state")

    # Unhandled use case
    raise Exception("State misalignment")

# Handle DELETE requests
def HandleDelete(sRemoteUser, sPath):
    return "DELETE"

# Main WSGI application entry point
def application(pEnvironment, fStartResponse):
    gStateMutex.acquire()

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

    gStateMutex.release()

    # Send the response
    fStartResponse(sStatus, pHeaders)
    return sResponseJSON

# Main function used for local execution
if __name__ == '__main__':
    httpd = make_server('', 80, application)
    print "Serving on port 80..."
    httpd.serve_forever()

