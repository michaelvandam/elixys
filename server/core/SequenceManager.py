"""SequenceManager

Elixys Sequence Manager
"""

import json
import SequenceValidation

# Default component values
DEFAULT_ADD_DELIVERYTIME = 10
DEFAULT_ADD_DELIVERYPRESSURE = 5
DEFAULT_EVAPORATE_PRESSURE = 10

class SequenceManager:

  def __init__(self, pDatabase):
    self.database = pDatabase
    self.validation = SequenceValidation.SequenceValidation(pDatabase, self)

  ### Sequence functions ###

  def GetSequence(self, sRemoteUser, nSequenceID, bFullLoad = True):
    """ Load the sequence and component metadata from the database """
    # Load the sequence
    pSequence = self.database.GetSequence(sRemoteUser, nSequenceID)

    # Add details to each component if we're doing a full load
    if bFullLoad:
        for pComponent in pSequence["components"]:
          self.__AddComponentDetails(sRemoteUser, pComponent, nSequenceID)

    # Return
    return pSequence

  def CopySequence(sRemoteUser, nSequenceID, sName, sComment, sType, nCassettes, nReagents, nColumns):
    """ Creates a copy of an existing sequence in the database """
    # Create the new sequence
    nNewSequenceID = self.database.CreateSequence(sRemoteUser, sName, sComment, sType, nCassettes, nReagents, nColumns)

    # Cassette loop
    for nCassette in range(1, nCassettes + 1):
      # Copy reagents
      for nReagent in range(1, nReagents + 1):
        pReagent = self.database.GetReagentByPosition(sRemoteUser, nSequenceID, nCassette, str(nReagent))
        self.database.UpdateReagentByPosition(sRemoteUser, nNewSequenceID, nCassette, str(nReagent), pReagent["available"], 
          pReagent["name"], pReagent["description"])

      # Copy columns
      for nColumn in range(0, nColumns):
        sPosition = chr(ord("A") + nColumn)
        pColumn = self.database.GetReagentByPosition(sRemoteUser, nSequenceID, nCassette, sPosition)
        self.database.UpdateReagentByPosition(sRemoteUser, nNewSequenceID, nCassette, sPosition, pReagent["available"], 
          pReagent["name"], pReagent["description"])

      # Update the cassette settings
      #pCassette = gDatabase.GetCassette()
      #def UpdateComponentDetails(pTargetComponent, pSourceComponent):

      # Yeah, this function isn't fully implemented yet

    # Process each component of the sequence
    pSequence = GetSequence(sRemoteUser, nSequenceID)
    for pComponent in pSequence["components"]:
      if pComponent["componenttype"] == "CASSETTE":
        self.database.Log(sRemoteUser, "Update cassette: " + str(pComponent))
      else:
        self.database.Log(sRemoteUser, "Add component: " + str(pComponent))

    # Return the ID of the new sequence
    return nNewSequenceID  
  
  def ImportSequence(self, sRemoteUser, sFilename):
    """Imports the specified sequence into the database"""
    # Open the file and read the contents
    pSequenceFile = open(sFilename)
    sSequence = pSequenceFile.read()
    pSequence = json.loads(sSequence)

    # Create the sequence
    if (pSequence["type"] == "sequence") and (pSequence["name"] != "") and (pSequence["reactors"] != 0) and (pSequence["reagentsperreactor"] != 0) and \
        (pSequence["columnsperreactor"] != 0):
      nSequenceID = self.database.CreateSequence(sRemoteUser, pSequence["name"], pSequence["description"], "Saved", pSequence["reactors"], 
        pSequence["reagentsperreactor"], pSequence["columnsperreactor"])
    else:
      raise Exception("Invalid sequence parameters")

    # Add the reagents
    nCurrentCassette = 0
    for pReagent in pSequence["reagents"]:
      if (pReagent["type"] == "reagent") and (pReagent["cassette"] != 0) and (pReagent["position"] != "") and (pReagent["name"] != ""):
        self.database.UpdateReagentByPosition(sRemoteUser, nSequenceID, pReagent["cassette"], pReagent["position"], True, pReagent["name"], pReagent["description"])
        if nCurrentCassette != pReagent["cassette"]:
          self.database.EnableCassette(sRemoteUser, nSequenceID, pReagent["cassette"] - 1)
          nCurrentCassette = pReagent["cassette"]
      else:
        raise Exception("Invalid reagent parameters in \"" + str(pReagent) + "\"")

    # Create a list of available reagents
    pAllReagents = self.database.GetReagentsBySequence(sRemoteUser, nSequenceID)
    pAvailableReagents = []
    for pReagent in pAllReagents:
      if pReagent["available"]:
        pAvailableReagents.append(pReagent)

    # Process each component
    for pComponent in pSequence["components"]:
      if (pComponent["type"] != ""):
        # Convert reagent and target names into IDs
        if pComponent["componenttype"] == "ADD":
          pReagent = self.__PopReagent(pComponent["reagent"], pAvailableReagents)
          pComponent["reagent"] = pReagent["reagentid"]
        elif pComponent["componenttype"] == "TRANSFER":
          pTarget = self.database.GetReagentByPosition(sRemoteUser, nSequenceID, pComponent["reactor"], "B")
          pComponent["target"] = pTarget["reagentid"]
        elif pComponent["componenttype"] == "ELUTE":
          pReagent = self.__PopReagent(pComponent["reagent"], pAvailableReagents)
          pComponent["reagent"] = pReagent["reagentid"]
          pTarget = self.database.GetReagentByPosition(sRemoteUser, nSequenceID, pComponent["reactor"], "B")
          pComponent["target"] = pTarget["reagentid"]

        # Add the component
        self.database.CreateComponent(sRemoteUser, nSequenceID, pComponent["componenttype"], "", json.dumps(pComponent))
      else:
        raise Exception("Invalid reagent parameters in \"" + str(pReagent) + "\"")

    # Validate the sequence
    self.validation.ValidateSequenceFull(sRemoteUser, nSequenceID)

  ### Reagent functions ###

  def GetReagent(self, sRemoteUser, nReagentID):
    """ Gets a reagent from the database """
    # Fetch the reagent from the databse
    return self.database.GetReagent(sRemoteUser, nReagentID)

  ### Component functions ###

  def GetComponent(self, sRemoteUser, nComponentID, nSequenceID):
    """ Fetches a component from the database """
    # Fetch the component from the database
    pComponent = self.database.GetComponent(sRemoteUser, nComponentID)

    # Add details to the component and return
    self.__AddComponentDetails(sRemoteUser, pComponent, nSequenceID)
    return pComponent

  def AddComponent(self, sRemoteUser, nSequenceID, nInsertionID, pComponent):
    """ Adds a new component to the database """
    # Update the component fields we want to save
    pDBComponent = {}
    self.__UpdateComponentDetails(sRemoteUser, pDBComponent, pComponent)

    # Insert the new component
    nComponentID = self.database.InsertComponent(sRemoteUser, nSequenceID, pComponent["componenttype"], pComponent["name"], 
      json.dumps(pDBComponent), nInsertionID)

    # Do a quick validation of the component and return
    self.validation.ValidateComponent(sRemoteUser, nSequenceID, nComponentID)
    return nComponentID

  def UpdateComponent(self, sRemoteUser, nSequenceID, nComponentID, nInsertionID, pComponent):
    """ Updates an existing component """
    # Do we have an input component?
    if pComponent != None:
      # Yes, so pull the original from the database and update it with the fields we want to save
      pDBComponent = self.database.GetComponent(sRemoteUser, nComponentID)
      self.__UpdateComponentDetails(sRemoteUser, pDBComponent, pComponent)

      # Update the component
      self.database.UpdateComponent(sRemoteUser, nComponentID, pDBComponent["componenttype"], pDBComponent["name"], json.dumps(pDBComponent))

    # Do a quick validation of the component
    self.validation.ValidateComponent(sRemoteUser, nSequenceID, nComponentID)

    # Move the component as needed
    if nInsertionID != None:
      self.database.MoveComponent(sRemoteUser, nComponentID, nInsertionID)

  def DeleteComponent(self, sRemoteUser, nComponentID):
    """ Deletes a component

    This logic should go in the web server

    # Check if the user is currently viewing this component
    sClientState = self.database.GetUserClientState(sRemoteUser, sRemoteUser)
    pClientStateComponents = sClientState.split(".")
    nClientComponentID = int(pClientStateComponents[2])
    if nClientComponentID == nComponentID:
      # Yes, so move the user to the next component in the sequence
      pComponent = self.database.GetNextComponent(sRemoteUser, nComponentID)
      if pComponent == None:
        # This is the last component in the sequence.  Move to the previous component
        pComponent = self.database.GetPreviousComponent(sRemoteUser, nComponentID)
        if pComponent == None:
          raise Exception("Failed to find previous or next components")

      # Update the client state
      sClientState = ""
      nIndex = 0
      for sItem in pClientStateComponents:
        if sClientState != "":
          sClientState += "."
        if nIndex == 2:
          sClientState += str(pComponent["id"])
        else:
          sClientState += sItem
        nIndex += 1
      self.database.UpdateUserClientState(sRemoteUser, sRemoteUser, sClientState)"""

    # Delete the component from the database
    self.database.DeleteComponent(sRemoteUser, nComponentID)

    # Flag the sequence validation as dirty
    self.database.UpdateSequenceDirtyFlag(sRemoteUser, nSequenceID, True)

  ### Internal functions ###

  # Adds details to the component after retrieving it from the database and prior to sending it to the client
  def __AddComponentDetails(self, sRemoteUser, pComponent, nSequenceID):
    # Details we add depends on the component type
    if pComponent["componenttype"] == "CASSETTE":
      # Look up each reagent in this cassette
      pReagentIDs = pComponent["reagentids"]
      pReagents = []
      for nReagentID in pReagentIDs:
        pReagents.append(self.GetReagent(sRemoteUser, nReagentID))
      del pComponent["reagentids"]
      pComponent["reagents"] = pReagents
    elif pComponent["componenttype"] == "ADD":
      # Look up the reagent we are adding
      pAddReagent = {}
      if pComponent["reagent"] != 0:
        pAddReagent = self.GetReagent(sRemoteUser, pComponent["reagent"])

      # Replace the reagent
      del pComponent["reagent"]
      pComponent["reagent"] = pAddReagent

      # Set the default delivery time and pressure
      if pComponent["deliverytime"] == 0:
        pComponent["deliverytime"] = DEFAULT_ADD_DELIVERYTIME
      if pComponent["deliverypressure"] == 0:
        pComponent["deliverypressure"]= DEFAULT_ADD_DELIVERYPRESSURE
    elif pComponent["componenttype"] == "EVAPORATE":
      # Set the default evaporation pressure if the value is zero
      if pComponent["evaporationpressure"] == 0:
        pComponent["evaporationpressure"] = DEFAULT_EVAPORATE_PRESSURE
    elif pComponent["componenttype"] == "TRANSFER":
      # Look up the target to which we are transferring
      pEluteTarget = {}
      if pComponent["target"] != 0:
        pEluteTarget = self.GetReagent(sRemoteUser, pComponent["target"])

      # Replace the target
      del pComponent["target"]
      pComponent["target"] = pEluteTarget
    elif pComponent["componenttype"] == "ELUTE":
      # Look up the reagent we are using to elute
      pEluteReagent = {}
      if pComponent["reagent"] != 0:
        pEluteReagent = self.GetReagent(sRemoteUser, pComponent["reagent"])

      # Look up the target from which we are eluting
      pEluteTarget = {}
      if pComponent["target"] != 0:
        pEluteTarget = self.GetReagent(sRemoteUser, pComponent["target"])

      # Replace the reagent and target
      del pComponent["reagent"]
      del pComponent["target"]
      pComponent["reagent"] = pEluteReagent
      pComponent["target"] = pEluteTarget

  def __UpdateComponentDetails(self, sRemoteUser, pTargetComponent, pSourceComponent):
    """ Strips a component down to only the details we want to save in the database """
    # Update the type and componenttype if they don't exist in the target component
    if not pTargetComponent.has_key("type"):
      pTargetComponent["type"] = pSourceComponent["type"]
      pTargetComponent["componenttype"] = pSourceComponent["componenttype"]

    # Handle the details depending on the component type
    if pTargetComponent["componenttype"] == "CASSETTE":
      # Update the component fields
      pTargetComponent["available"] = pSourceComponent["available"]
    elif pTargetComponent["componenttype"] == "ADD":
      # Update the component fields
      pTargetComponent["reactor"] = pSourceComponent["reactor"]
      pTargetComponent["deliveryposition"] = pSourceComponent["deliveryposition"]
      pTargetComponent["deliverytime"] = pSourceComponent["deliverytime"]
      pTargetComponent["deliverypressure"] = pSourceComponent["deliverypressure"]
      pTargetComponent["reagent"] = pSourceComponent["reagent"]
      if pTargetComponent["reagent"] != 0:
        pReagent = self.GetReagent(sRemoteUser, pTargetComponent["reagent"])
        pTargetComponent.update({"name":"Add " + pReagent["name"]})
      else:
        pTargetComponent.update({"name":"Add"})
    elif pTargetComponent["componenttype"] == "EVAPORATE":
      # Update the component fields
      pTargetComponent["reactor"] = pSourceComponent["reactor"]
      pTargetComponent["duration"] = pSourceComponent["duration"]
      pTargetComponent["evaporationtemperature"] = pSourceComponent["evaporationtemperature"]
      pTargetComponent["finaltemperature"] = pSourceComponent["finaltemperature"]
      pTargetComponent["stirspeed"] = pSourceComponent["stirspeed"]
      pTargetComponent["evaporationpressure"] = pSourceComponent["evaporationpressure"]
    elif pTargetComponent["componenttype"] == "TRANSFER":
      # Update the component fields
      pTargetComponent["reactor"] = pSourceComponent["reactor"]
      pTargetComponent["target"] = pSourceComponent["target"]
      if pTargetComponent["target"] != 0:
        pTarget = self.GetReagent(sRemoteUser, pTargetComponent["target"])
        pTargetComponent.update({"name":"Transfer to " + ppTargetagent["name"]})
      else:
        pTargetComponent.update({"name":"Transfer"})
    elif pTargetComponent["componenttype"] == "ELUTE":
      # Update the component fields
      pTargetComponent["reactor"] = pSourceComponent["reactor"]
      pTargetComponent["reagent"] = pSourceComponent["reagent"]
      pTargetComponent["target"] = pSourceComponent["target"]
      if pTargetComponent["reagent"] != 0:
        pReagent = self.GetReagent(sRemoteUser, pTargetComponent["reagent"])
        pTargetComponent.update({"name":"Elute with " + pReagent["name"]})
      else:
        pTargetComponent.update({"name":"Elute"})
    elif pTargetComponent["componenttype"] == "REACT":
      # Update the component fields
      pTargetComponent["reactor"] = pSourceComponent["reactor"]
      pTargetComponent["position"] = pSourceComponent["position"]
      pTargetComponent["duration"] = pSourceComponent["duration"]
      pTargetComponent["reactiontemperature"] = pSourceComponent["reactiontemperature"]
      pTargetComponent["finaltemperature"] = pSourceComponent["finaltemperature"]
      pTargetComponent["stirspeed"] = pSourceComponent["stirspeed"]
    elif pTargetComponent["componenttype"] == "PROMPT":
      # Update the component fields
      pTargetComponent["message"] = pSourceComponent["message"]
    elif pTargetComponent["componenttype"] == "INSTALL":
      # Update the component fields
      pTargetComponent["reactor"] = pSourceComponent["reactor"]
      pTargetComponent["message"] = pSourceComponent["message"]
    elif pTargetComponent["componenttype"] == "COMMENT":
      # Update the component fields
      pTargetComponent["comment"] = pSourceComponent["comment"]

  def __PopReagent(self, sReagentName, pReagents):
    """ Locates the next reagent that matches the name and pops it off the list """
    nIndex = 0
    for pReagent in pReagents:
      if pReagent["name"] == sReagentName:
        return pReagents.pop(nIndex)
      nIndex += 1
    raise Exception("Too few '" + sReagentName + "' reagents in sequence")

# Main function
import sys
sys.path.append("../database/")
from DBComm import DBComm
if __name__ == "__main__":
  pDatabase = DBComm()
  pDatabase.Connect()
  pSequenceManager = SequenceManager(pDatabase)
  print "Loading sequence"
  pSequence = pSequenceManager.GetSequence("main", 1)
  print str(pSequence)
  print "Done"

