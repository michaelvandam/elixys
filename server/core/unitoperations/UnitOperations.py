"""Unit operations
Elixys Unit Operations
"""

#Import unit operations
from Cassette import Cassette
from Add import Add
from Evaporate import Evaporate
from Transfer import Transfer
from React import React
from Prompt import Prompt
from Install import Install
from Comment import Comment
from TrapF18 import TrapF18
from EluteF18 import EluteF18
from Initialize import Initialize
from Mix import Mix
from Move import Move

#Create a unit operation from a component object
def createFromComponent(nSequenceID, pComponent, username, database, systemModel = None):
  if pComponent["componenttype"] == "CASSETTE":
    pCassette = Cassette(systemModel, {}, username, database)
    pCassette.initializeComponent(pComponent)
    return pCassette
  elif pComponent["componenttype"] == "ADD":
    pParams = {}
    pParams["ReactorID"] = "Reactor" + str(pComponent["reactor"])
    pParams["ReagentReactorID"] = "Reactor0"   #We'll get the actual value once we initialize the component
    pParams["ReagentPosition"] = 0             #Ditto
    pParams["reagentLoadPosition"] = pComponent["deliveryposition"]
    pParams["duration"] = pComponent["deliverytime"]
    pParams["pressure"] = pComponent["deliverypressure"]
    pAdd = Add(systemModel, pParams, username, database)
    pAdd.initializeComponent(pComponent)
    if pComponent["reagent"].has_key("position"):
      pAdd.reagentPosition = int(pComponent["reagent"]["position"])
    if pComponent["reagent"].has_key("reagentid"):
      pAdd.ReagentReactorID = "Reactor" + str(database.GetReagentCassette(username, nSequenceID, pComponent["reagent"]["reagentid"]))
    return pAdd
  elif pComponent["componenttype"] == "EVAPORATE":
    pParams = {}
    pParams["ReactorID"] =  "Reactor" + str(pComponent["reactor"])
    pParams["evapTemp"] = pComponent["evaporationtemperature"]
    pParams["pressure"] = pComponent["evaporationpressure"]
    pParams["evapTime"] = pComponent["duration"]
    pParams["coolTemp"] = pComponent["finaltemperature"]
    pParams["stirSpeed"] = pComponent["stirspeed"]
    pEvaporate = Evaporate(systemModel, pParams, username, database)
    pEvaporate.initializeComponent(pComponent)
    return pEvaporate
  elif pComponent["componenttype"] == "TRANSFER":
    pParams = {}
    pParams["ReactorID"] = "Reactor" + str(pComponent["sourcereactor"])
    pParams["transferReactorID"] = "Reactor" + str(pComponent["targetreactor"])
    pParams["transferType"] = str(pComponent["mode"])
    pParams["transferTimer"] = pComponent["duration"]
    pParams["transferPressure"] = pComponent["pressure"]
    pTransfer = Transfer(systemModel, pParams, username, database)
    pTransfer.initializeComponent(pComponent)
    return pTransfer
  elif pComponent["componenttype"] == "REACT":
    pParams = {}
    pParams["ReactorID"] = "Reactor" + str(pComponent["reactor"])
    pParams["reactTemp"] = pComponent["reactiontemperature"]
    pParams["reactTime"] = pComponent["duration"]
    pParams["coolTemp"] = pComponent["finaltemperature"]
    pParams["coolingDelay"] = pComponent["coolingdelay"]
    pParams["reactPosition"] = "React" + str(pComponent["position"])
    pParams["stirSpeed"] = pComponent["stirspeed"]
    pReact = React(systemModel, pParams, username, database)
    pReact.initializeComponent(pComponent)
    return pReact
  elif pComponent["componenttype"] == "PROMPT":
    pParams = {}
    pParams["userMessage"] = str(pComponent["message"])
    pPrompt = Prompt(systemModel, pParams, username, database)
    pPrompt.initializeComponent(pComponent)
    return pPrompt
  elif pComponent["componenttype"] == "INSTALL":
    pParams = {}
    pParams["ReactorID"] = "Reactor" + str(pComponent["reactor"])
    pParams["userMessage"] = pComponent["message"]
    pInstall = Install(systemModel, pParams, username, database)
    pInstall.initializeComponent(pComponent)
    return pInstall
  elif pComponent["componenttype"] == "COMMENT":
    pParams = {}
    pParams["userMessage"] = pComponent["comment"]
    pComment = Comment(systemModel, pParams, username, database)
    pComment.initializeComponent(pComponent)
    return pComment
  elif pComponent["componenttype"] == "TRAPF18":
    pParams = {}
    pParams["cyclotronFlag"] = pComponent["cyclotronflag"]
    pParams["trapTime"] = pComponent["traptime"]
    pParams["trapPressure"] = pComponent["trappressure"]
    pTrapF18 = TrapF18(systemModel, pParams, username, database)
    pTrapF18.initializeComponent(pComponent)
    return pTrapF18
  elif pComponent["componenttype"] == "ELUTEF18":
    pParams = {}
    pParams["eluteTime"] = pComponent["elutetime"]
    pParams["elutePressure"] = pComponent["elutepressure"]
    pParams["ReagentReactorID"] = "Reactor0"   #We'll get the actual value once we initialize the component
    pParams["ReagentPosition"] = 0             #Ditto
    pEluteF18 = EluteF18(systemModel, pParams, username, database)
    pEluteF18.initializeComponent(pComponent)
    if pComponent["reagent"].has_key("position"):
      pEluteF18.reagentPosition = int(pComponent["reagent"]["position"])
    if pComponent["reagent"].has_key("reagentid"):
      pEluteF18.ReagentReactorID = "Reactor" + str(database.GetReagentCassette(username, nSequenceID, pComponent["reagent"]["reagentid"]))
    return pEluteF18
  elif pComponent["componenttype"] == "INITIALIZE":
    pInitialize = Initialize(systemModel, {}, username, database)
    pInitialize.initializeComponent(pComponent)
    return pInitialize
  elif pComponent["componenttype"] == "MIX":
    pParams = {}
    pParams["ReactorID"] = "Reactor" + str(pComponent["reactor"])
    pParams["stirSpeed"] = pComponent["stirspeed"]
    pParams["duration"] = pComponent["mixtime"]
    pMix = Mix(systemModel, pParams, username, database)
    pMix.initializeComponent(pComponent)
    return pMix
  elif pComponent["componenttype"] == "MOVE":
    pParams = {}
    pParams["ReactorID"] = "Reactor" + str(pComponent["reactor"])
    pParams["reactPosition"] = str(pComponent["position"])
    pMove = Move(systemModel, pParams, username, database)
    pMove.initializeComponent(pComponent)
    return pMove
  else:
    raise Exception("Unknown component type: " + pComponent["componenttype"])
