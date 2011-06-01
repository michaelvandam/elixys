"""Communication

Elixys JSON communication for GUI
"""
import MySQLdb as SQL

class DBComm:
  def __init__(self):
    try:
      self.database = SQL.connect('localhost', 'root', 'kevin', 'elixys');
    except:
      print "Unable to connect to SQL database."
    
  def getFromDB(self, type, query):
    if (type=='sequences'):
      self.getSequences()
    elif (type=='unitop'):
      self.getUnitOperations(query)
    
  def getUnitOperations(self, query):
    rows = self.runQuery('SELECT id,unitop_name FROM unitoperations WHERE unitop_sequence=\'%s\'' % query)
    print "Sequences:"
    for row in rows:
        print row[0],row[1]
  def getSequences(self):
    rows = self.runQuery('SELECT id,seq_name FROM sequences')
    print "Sequences:"
    for row in rows:
        print row[0],row[1]
        
        
  def getSequence(self, query):
    #sequence = self.runQuery('SHOW COLUMNS FROM sequences')
    sequence = self.runQuery('SELECT column_name FROM information_schema.columns WHERE table_name=\'sequences\'')
    print "\n\n"
    """
    for each in sequence:
      print each
    rows = self.runQuery('SELECT * FROM sequences WHERE id=\'%s\'' % query)
    for seq,row in map(None,sequence,rows):
      pass
      #print (seq,row)
     """ 
  def runQuery(self,query):
    try:

      cursor = self.database.cursor()
      cursor.execute(query)
      rows = cursor.fetchall()
      return rows
      for row in rows:
          print row
          for query in row:
            print query
      cursor.close()
    except SQL.Error, e:
        print "Error %d: %s" % (e.args[0],e.args[1])
        sys.exit(1)
        
  def closeDB(self):
    self.database = SQL.connect('localhost', 'root', 'kevin', 'elixys');

def test():
  sqldata = DBComm()
  #sqldata.runQuery('SELECT * FROM unitoperations ORDER BY unitop_step ASC')
  sqldata.getFromDB('sequences','placeholder')
  sqldata.getFromDB('unitop','1')
  sqldata.closeDB()
  
if __name__ == '__main__':
    test()
    
    
    
"""
    
    
    #!/usr/bin/python26

# Imports
from wsgiref.simple_server import make_server
import json
from wsgiref.headers import Headers
import sys
import os
import os.path
import time
import errno

# States
STATE_HOME = 0
STATE_SELECT_SAVEDSEQUENCES = 1
STATE_SELECT_MANUALRUNS = 2
STATE_VIEW = 3
STATE_PROMPT_CREATESEQUENCE = 4
STATE_PROMPT_COPYSEQUENCE = 5
STATE_PROMPT_DELETESEQUENCE = 6

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
        "8",
        "9",
        "10"]},
    {"type":"component",
    "componenttype":"CASSETTE",
    "name":"Cassette 2",
    "id":"2",
    "reactor":"2",
    "reactordescription":"Reactor associated with this cassette",
    "reactorvalidation":"",
    "used":"true",
    "reagents":["11",
        "12",
        "13",
        "14",
        "15",
        "16",
        "17",
        "18",
        "19",
        "20"]},
    {"type":"component",
    "componenttype":"CASSETTE",
    "name":"Cassette 3",
    "id":"3",
    "reactor":"3",
    "reactordescription":"Reactor associated with this cassette",
    "reactorvalidation":"",
    "used":"false",
    "reagents":["21",
        "22",
        "23",
        "24",
        "25",
        "26",
        "27",
        "28",
        "29",
        "30"]},
    {"type":"component",
    "componenttype":"ADD",
    "name":"Add F-18",
    "id":"4",
    "reactor":"1",
    "reactordescription":"Reactor where the reagent will be added",
    "reactorvalidation":"type=enum-literal; values=1,2,3; required=true",
    "reagent":"1",
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
    "target":"3",
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
    "target":"2",
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
    "messagedescription":"This will be displayed to the user",
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
    "componentid":"1",
    "position":"A",
    "name":"QMA",
    "nameerror":"",
    "description":"QMA column",
    "descriptionerror":"",
    "id":"9"},
    {"type":"reagent",
    "used":"true",
    "componentid":"1",
    "position":"B",
    "name":"Seppak1",
    "nameerror":"",
    "description":"Sep-Pak",
    "descriptionerror":"",
    "id":"10"},
    {"type":"reagent",
    "used":"true",
    "componentid":"2",
    "position":"1",
    "name":"C6H12O6",
    "nameerror":"",
    "description":"Sugar (yum!)",
    "descriptionerror":"",
    "id":"11"},
    {"type":"reagent",
    "used":"true",
    "componentid":"2",
    "position":"2",
    "name":"HCl",
    "nameerror":"",
    "description":"Hydrochloric acid",
    "descriptionerror":"",
    "id":"12"},
    {"type":"reagent",
    "used":"false",
    "componentid":"2",
    "position":"3",
    "name":"",
    "nameerror":"",
    "description":"",
    "descriptionerror":"",
    "id":"13"},
    {"type":"reagent",
    "used":"true",
    "componentid":"2",
    "position":"4",
    "name":"H2",
    "nameerror":"",
    "description":"Hydrogen gas",
    "descriptionerror":"",
    "id":"14"},
    {"type":"reagent",
    "used":"false",
    "componentid":"2",
    "position":"5",
    "name":"",
    "nameerror":"",
    "description":"",
    "descriptionerror":"",
    "id":"15"},
    {"type":"reagent",
    "used":"true",
    "componentid":"2",
    "position":"6",
    "name":"KCl",
    "nameerror":"",
    "description":"Potassium chloride",
    "descriptionerror":"",
    "id":"16"},
    {"type":"reagent",
    "used":"false",
    "componentid":"2",
    "position":"7",
    "name":"",
    "nameerror":"",
    "description":"",
    "descriptionerror":"",
    "id":"17"},
    {"type":"reagent",
    "used":"true",
    "componentid":"2",
    "position":"8",
    "name":"N2",
    "nameerror":"",
    "description":"Liquid nitrogen",
    "descriptionerror":"",
    "id":"18"},
    {"type":"reagent",
    "used":"true",
    "componentid":"2",
    "position":"A",
    "name":"Seppak2",
    "nameerror":"",
    "description":"Sep-Pak",
    "descriptionerror":"",
    "id":"19"},
    {"type":"reagent",
    "used":"false",
    "componentid":"2",
    "position":"B",
    "name":"",
    "nameerror":"",
    "description":"",
    "descriptionerror":"",
    "id":"20"}]

def Log(sMessage):
    print >> sys.stderr, sMessage

def StateString(nState):
    if nState == STATE_HOME:
        return "HOME"
    elif nState == STATE_SELECT_SAVEDSEQUENCES:
        return "SELECT/SAVEDSEQUENCES"
    elif nState == STATE_SELECT_MANUALRUNS:
        return "SELECT/MANUALRUNS"
    elif nState == STATE_VIEW:
        return "VIEW"
    elif nState == STATE_PROMPT_CREATESEQUENCE:
        return "PROMPT/CREATESEQUENCE"
    elif nState == STATE_PROMPT_COPYSEQUENCE:
        return "PROMPT/COPYSEQUENCE"
    elif nState == STATE_PROMPT_DELETESEQUENCE:
        return "PROMPT/DELETESEQUENCE"
    else:
        return "UNKNOWN"

def LockState():
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

def LoadState():
    # Attempt to open the state file
    try:
        # Open the state file
        pStateFile = os.open("/var/www/wsgi/state.txt", os.O_RDWR)

        # Read in the state
        nState = int(os.read(pStateFile, 99))
        os.close(pStateFile)

        # Return the state
        return nState
    except OSError as e:
        # Check for errors other than a nonexistant state file
        if e.errno != errno.ENOENT:
            raise

        # Default to the home state
        return STATE_HOME

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

def SaveState(nState):
    # Open the state file
    pStateFile = os.open("/var/www/wsgi/state.txt", os.O_CREAT | os.O_TRUNC | os.O_RDWR)

    # Write the state
    os.write(pStateFile, str(nState))
    os.close(pStateFile)

def SaveComponentID(nComponentID):
    # Open the component file
    pComponentFile = os.open("/var/www/wsgi/component.txt", os.O_CREAT | os.O_TRUNC | os.O_RDWR)

    # Write the component
    os.write(pComponentFile, str(nComponentID))
    os.close(pComponentFile)

def HandleGet(nState, sRemoteUser, sPath):
    if sPath == "/configuration":
        return HandleGetConfiguration(sRemoteUser)
    if sPath == "/state":
        return HandleGetState(nState, sRemoteUser)
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

def HandleGetState(nState, sRemoteUser):
    if nState == STATE_HOME:
        return HandleGetStateHome(sRemoteUser)
    elif nState == STATE_SELECT_SAVEDSEQUENCES:
        return HandleGetStateSelectSavedSequences(sRemoteUser)
    elif nState == STATE_SELECT_MANUALRUNS:
        return HandleGetStateSelectManualRuns(sRemoteUser)
    elif nState == STATE_VIEW:
        return HandleGetStateView(sRemoteUser)
    elif nState == STATE_PROMPT_CREATESEQUENCE:
        return HandleGetStatePromptCreateSequence(sRemoteUser)
    elif nState == STATE_PROMPT_COPYSEQUENCE:
        return HandleGetStatePromptCopySequence(sRemoteUser)
    elif nState == STATE_PROMPT_DELETESEQUENCE:
        return HandleGetStatePromptDeleteSequence(sRemoteUser)
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
        "componentid":str(LoadComponentID())}

def HandleGetStatePromptCreateSequence(sRemoteUser):
    return {"type":"state",
        "user":{"type":"user",
            "username":"devel",
            "useraccesslevel":"Administrator"},
        "serverstate":{"type":"serverstate"},
        "clientstate":"PROMPT",
        "text1":"Enter the name of the new sequence:",
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

def HandleGetStatePromptCopySequence(sRemoteUser):
    return {"type":"state",
        "user":{"type":"user",
            "username":"devel",
            "useraccesslevel":"Administrator"},
        "serverstate":{"type":"serverstate"},
        "clientstate":"PROMPT",
        "text1":"Enter the name of the new sequence:",
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

def HandleGetStatePromptDeleteSequence(sRemoteUser):
    return {"type":"state",
        "user":{"type":"user",
            "username":"devel",
            "useraccesslevel":"Administrator"},
        "serverstate":{"type":"serverstate"},
        "clientstate":"PROMPT",
        "text1":"Are you sure that you want to permanently delete sequence \"Fake Sequence Name Here\"?",
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

def HandlePost(nState, sRemoteUser, sPath, pBody):
    if sPath == "/HOME":
        return HandlePostHome(nState, sRemoteUser, pBody)
    elif sPath == "/SELECT":
        return HandlePostSelect(nState, sRemoteUser, pBody)
    elif sPath == "/VIEW":
        return HandlePostView(nState, sRemoteUser, pBody)
    elif sPath == "/PROMPT":
        return HandlePostPrompt(nState, sRemoteUser, pBody)
    else:
        raise Exception("Unknown path: " + sPath)

def HandlePostHome(nState, sRemoteUser, pBody):
    # Make sure we are on the home page
    if nState != STATE_HOME:
        raise Exception("State misalignment");

    # Parse the JSON string in the body
    pJSON = json.loads(pBody)

    # Check which option the user selected
    sActionType = str(pJSON["action"]["type"])
    sActionTargetID = str(pJSON["action"]["targetid"])
    if sActionType == "BUTTONCLICK":
        if sActionTargetID == "CREATE":
            # Update our state and return it to the client
            nState = STATE_SELECT_SAVEDSEQUENCES
            SaveState(nState)
            return HandleGet(nState, sRemoteUser, "/state")
        elif sActionTargetID == "MANUAL":
            # Do nothing but return the state to the client
            return HandleGet(nState, sRemoteUser, "/state")
        elif sActionTargetID == "OBSERVE":
            # Do nothing but return the state to the client
            return HandleGet(nState, sRemoteUser, "/state")

    # Unhandled use case
    raise Exception("State misalignment")

def HandlePostSelect(nState, sRemoteUser, pBody):
    # Make sure we are on the select page
    if (nState != STATE_SELECT_SAVEDSEQUENCES) and (nState != STATE_SELECT_MANUALRUNS):
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
            nState = STATE_VIEW
            SaveState(nState)
            return HandleGet(nState, sRemoteUser, "/state")
        elif sActionTargetID == "BACK":
            # Update our state and return it to the client
            nState = STATE_HOME
            SaveState(nState)
            return HandleGet(nState, sRemoteUser, "/state")
        elif sActionTargetID == "CREATE":
            # Update our state and return it to the client
            nState = STATE_PROMPT_CREATESEQUENCE
            SaveState(nState)
            return HandleGet(nState, sRemoteUser, "/state")
        elif sActionTargetID == "COPY":
            # Update our state and return it to the client
            nState = STATE_PROMPT_COPYSEQUENCE
            SaveState(nState)
            return HandleGet(nState, sRemoteUser, "/state")
        elif sActionTargetID == "DELETE":
            # Update our state and return it to the client
            nState = STATE_PROMPT_DELETESEQUENCE
            SaveState(nState)
            return HandleGet(nState, sRemoteUser, "/state")
        else:
            # Do nothing but return the state to the client
            return HandleGet(nState, sRemoteUser, "/state")
    elif sActionType == "TABCLICK":
        if sActionTargetID == "SAVEDSEQUENCES":
            # Update our state and return it to the client
            nState = STATE_SELECT_SAVEDSEQUENCES
            SaveState(nState)
            return HandleGet(nState, sRemoteUser, "/state")
        elif sActionTargetID == "MANUALRUNS":
            # Update our state and return it to the client
            nState = STATE_SELECT_MANUALRUNS
            SaveState(nState)
            return HandleGet(nState, sRemoteUser, "/state")

    # Unhandled use case
    raise Exception("State misalignment")

def HandlePostView(nState, sRemoteUser, pBody):
    # Make sure we are on the view page
    global gSequence
    if nState != STATE_VIEW:
        raise Exception("State misalignment")

    # Parse the JSON string in the body
    pJSON = json.loads(pBody)

    # Check which option the user selected
    sActionType = str(pJSON["action"]["type"])
    sActionTargetID = str(pJSON["action"]["targetid"])
    if sActionType == "BUTTONCLICK":
        if sActionTargetID == "BACK":
            # Update our state and return it to the client
            nState = STATE_SELECT_SAVEDSEQUENCES
            SaveState(nState)
            return HandleGet(nState, sRemoteUser, "/state")
        elif sActionTargetID == "PREVIOUS":
            # Move to the previous component ID
            sCurrentComponentID = LoadComponentID()
            sPreviousComponentID = -1
            for pComponent in gSequence:
                if pComponent["id"] == str(sCurrentComponentID):
                    if sPreviousComponentID != -1:
                        SaveComponentID(sPreviousComponentID)
                    return HandleGet(nState, sRemoteUser, "/state")
                else:
                    sPreviousComponentID = pComponent["id"]
            raise Exception("Component ID not found in sequence")
        elif sActionTargetID == "NEXT":
            # Move to the next component ID
            sCurrentComponentID = LoadComponentID()
            bComponentIDFound = False
            for pComponent in gSequence:
                if bComponentIDFound:
                    SaveComponentID(pComponent["id"])
                    return HandleGet(nState, sRemoteUser, "/state")
                elif pComponent["id"] == str(sCurrentComponentID):
                    bComponentIDFound = True
            if bComponentIDFound:
                return HandleGet(nState, sRemoteUser, "/state")
            raise Exception("Component ID not found in sequence")
        else:
            # Check if the target ID corresponds to one of our sequence components
            for pComponent in gSequence:
                if pComponent["id"] == sActionTargetID:
                    # Update the current component and return the latest state to the client
                    SaveComponentID(pComponent["id"])
                    return HandleGet(nState, sRemoteUser, "/state")

    # Unhandled use case
    raise Exception("State misalignment")

def HandlePostPrompt(nState, sRemoteUser, pBody):
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
    nState = LoadState()
    if nState == STATE_PROMPT_CREATESEQUENCE:
        if sActionTargetID == "CREATE":
            # Update our state and return it to the client
            nState = STATE_SELECT_SAVEDSEQUENCES
            SaveState(nState)
            return HandleGet(nState, sRemoteUser, "/state")
        if sActionTargetID == "CANCEL":
            # Update our state and return it to the client
            nState = STATE_SELECT_SAVEDSEQUENCES
            SaveState(nState)
            return HandleGet(nState, sRemoteUser, "/state")
    elif nState == STATE_PROMPT_COPYSEQUENCE:
        if sActionTargetID == "COPY":
            # Update our state and return it to the client
            nState = STATE_SELECT_SAVEDSEQUENCES
            SaveState(nState)
            return HandleGet(nState, sRemoteUser, "/state")
        if sActionTargetID == "CANCEL":
            # Update our state and return it to the client
            nState = STATE_SELECT_SAVEDSEQUENCES
            SaveState(nState)
            return HandleGet(nState, sRemoteUser, "/state")
    elif nState == STATE_PROMPT_DELETESEQUENCE:
        if sActionTargetID == "DELETE":
            # Update our state and return it to the client
            nState = STATE_SELECT_SAVEDSEQUENCES
            SaveState(nState)
            return HandleGet(nState, sRemoteUser, "/state")
        if sActionTargetID == "CANCEL":
            # Update our state and return it to the client
            nState = STATE_SELECT_SAVEDSEQUENCES
            SaveState(nState)
            return HandleGet(nState, sRemoteUser, "/state")

    # Unhandled use case
    raise Exception("State misalignment")

# Handle DELETE requests
def HandleDelete(nState, sRemoteUser, sPath):
    return "DELETE"

# Main WSGI application entry point
def application(pEnvironment, fStartResponse):
    # Lock and load the state
    LockState()
    nState = LoadState()

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
    Log("Received " + sRequestMethod + " request for " + sPath + " (state = " + StateString(nState) + ")");

    # Handle the request
    try:
        # Call the appropriate handler
        if sRequestMethod == "GET":
            sResponse = HandleGet(nState, sRemoteUser, sPath)
        elif sRequestMethod == "POST":
            pBodyLength = int(pEnvironment["CONTENT_LENGTH"])
            pBody = pEnvironment["wsgi.input"].read(pBodyLength)
            sResponse = HandlePost(nState, sRemoteUser, sPath, pBody)
        elif sRequestMethod == "DELETE":
            sResponse = HandleDelete(nState, sRemoteUser, sPath)
        else:
            raise Exception("Unknown request method")
    except Exception as ex:
        # Send an error message back to the client
        sResponse = {"type":"error","description":str(ex)}

    # Initialize the return status and headers
    sStatus = "200 OK"
    sResponseJSON = json.dumps(sResponse)
    pHeaders = [("Content-type", "text/plain"), ("Content-length", str(len(sResponseJSON)))]

    # Unlock the state
    UnlockState()

    # Send the response
    fStartResponse(sStatus, pHeaders)
    return [sResponseJSON]

# Main function used for local execution
if __name__ == '__main__':
    httpd = make_server('', 80, application)
    print "Serving on port 80..."
    httpd.serve_forever()
 """