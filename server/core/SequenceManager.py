"""SequenceManager

Elixys Sequence Manager
"""

import json
import SequenceValidation
import sys
sys.path.append("/opt/elixys/core/unitoperations")
import UnitOperations

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
          pUnitOperation = UnitOperations.createFromComponent(nSequenceID, pComponent, sRemoteUser, self.database)
          pUnitOperation.addComponentDetails()

    # Return
    return pSequence

  def CopySequence(self, sRemoteUser, nSequenceID, sName, sComment):
    """ Creates a copy of an existing sequence in the database """
    # Create the new saved sequence
    pConfiguration = self.database.GetConfiguration(sRemoteUser)
    nNewSequenceID = self.database.CreateSequence(sRemoteUser, sName, sComment, "Saved", pConfiguration["reactors"], pConfiguration["reagentsperreactor"],
      pConfiguration["columnsperreactor"])

    # Copy each component of the sequence
    pSequence = self.GetSequence(sRemoteUser, nSequenceID)
    for pComponent in pSequence["components"]:
      pUnitOperation = UnitOperations.createFromComponent(nSequenceID, pComponent, sRemoteUser, self.database)
      pUnitOperation.copyComponent(nNewSequenceID)

    # Validate the sequence
    self.validation.ValidateSequenceFull(sRemoteUser, nNewSequenceID)

    # Return the ID of the new sequence
    return nNewSequenceID  
  
  def ImportSequence(self, sRemoteUser, sFilename, sType):
    """Imports the specified sequence into the database"""
    # Open the file and read the contents
    pSequenceFile = open(sFilename)
    sSequence = pSequenceFile.read()
    pSequence = json.loads(sSequence)

    # Make sure the sequence hardware requirements meet our current system
    pConfiguration = self.database.GetConfiguration(sRemoteUser)
    if (pSequence["reactors"] != pConfiguration["reactors"]) or (pSequence["reagentsperreactor"] != pConfiguration["reagentsperreactor"]) or \
       (pSequence["columnsperreactor"] != pConfiguration["columnsperreactor"]):
      raise Exception("This sequence you are trying to import does not match the system hardware")

    # Create the sequence
    if (pSequence["type"] == "sequence") and (pSequence["name"] != "") and (pSequence["reactors"] != 0) and (pSequence["reagentsperreactor"] != 0) and \
       (pSequence["columnsperreactor"] != 0):
      nSequenceID = self.database.CreateSequence(sRemoteUser, pSequence["name"], pSequence["description"], sType, pSequence["reactors"], 
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
        # Convert reagent names into IDs
        if pComponent.has_key("reagent"):
          pReagent = self.__PopReagent(pComponent["reagent"], pAvailableReagents)
          pComponent["reagent"] = pReagent["reagentid"]

        # Add the component
        self.database.CreateComponent(sRemoteUser, nSequenceID, pComponent["componenttype"], "", json.dumps(pComponent))
      else:
        raise Exception("Invalid reagent parameters in \"" + str(pReagent) + "\"")

    # Validate the sequence
    self.validation.ValidateSequenceFull(sRemoteUser, nSequenceID)

  def ExportSequence(self, sRemoteUser, nSequenceID, sFilename):
    """Exports the specified sequence from the database"""
    # Load the sequence
    pDBSequence = self.GetSequence(sRemoteUser, nSequenceID, False)
    print "DB sequence = " + str(pDBSequence)

    # Get the system configuration
    pConfiguration = self.database.GetConfiguration(sRemoteUser)

    # Create the sequence
    pSequence = {}
    pSequence["type"] ="sequence"
    pSequence["name"] = pDBSequence["metadata"]["name"]
    pSequence["description"] = pDBSequence["metadata"]["comment"]
    pSequence["reactors"] = pConfiguration["reactors"]
    pSequence["reagentsperreactor"] = pConfiguration["reagentsperreactor"]
    pSequence["columnsperreactor"] = pConfiguration["columnsperreactor"]
    pSequence["reagents"] = []
    pSequence["components"] = []

    # Add the reagents from each cassette
    nCassette = 1
    for pComponent in pDBSequence["components"]:
        if pComponent["componenttype"] == "CASSETTE":
            pCassette = UnitOperations.createFromComponent(nSequenceID, pComponent, sRemoteUser, self.database)
            pCassette.addComponentDetails()
            for pReagent in pCassette.component["reagents"]:
                if pReagent["available"]:
                    pSequence["reagents"].append({"type":"reagent",
                        "cassette":nCassette,
                        "position":pReagent["position"],
                        "name":pReagent["name"],
                        "description":pReagent["description"]})
            nCassette += 1

    # Add each component
    for pComponent in pDBSequence["components"]:
        # Skip the cassettes
        if pComponent["componenttype"] == "CASSETTE":
            continue

        # Minimalize the component
        pUnitOperation = UnitOperations.createFromComponent(nSequenceID, pComponent, sRemoteUser, self.database)
        pMinimalComponent = {}
        pUnitOperation.updateComponentDetails(pMinimalComponent)

        # Replace any reagent ID with a name
        if pComponent.has_key("reagent"):
            pMinimalComponent["reagent"] = pComponent["reagent"]["name"]
        print "Minimal component = " + str(pMinimalComponent)

        # Append the component
        pSequence["components"].append(pMinimalComponent)

    # Save the sequence to the file
    pSequenceFile = open(sFilename, "w")
    sSequenceJSON = json.dumps(pSequence)
    pSequenceFile.write(sSequenceJSON)

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
    pUnitOperation = UnitOperations.createFromComponent(nSequenceID, pComponent, sRemoteUser, self.database)
    pUnitOperation.addComponentDetails()
    return pUnitOperation.component

  def AddComponent(self, sRemoteUser, nSequenceID, nInsertionID, pComponent):
    """ Adds a new component to the database """
    # Update the component fields we want to save
    pUnitOperation = UnitOperations.createFromComponent(nSequenceID, pComponent, sRemoteUser, self.database)
    pDBComponent = {}
    pUnitOperation.updateComponentDetails(pDBComponent)

    # Insert the new component
    nComponentID = self.database.InsertComponent(sRemoteUser, nSequenceID, pDBComponent["componenttype"], pDBComponent["name"], 
      json.dumps(pDBComponent), nInsertionID)

    # Initialize the new component's validation fields
    self.validation.InitializeComponent(sRemoteUser, nSequenceID, nComponentID)
    self.validation.ValidateComponent(sRemoteUser, nSequenceID, nComponentID)
    return nComponentID

  def UpdateComponent(self, sRemoteUser, nSequenceID, nComponentID, nInsertionID, pComponent):
    """ Updates an existing component """
    # Do we have an input component?
    if pComponent != None:
      # Yes, so pull the original from the database and update it with the fields we want to save
      pUnitOperation = UnitOperations.createFromComponent(nSequenceID, pComponent, sRemoteUser, self.database)
      pDBComponent = self.database.GetComponent(sRemoteUser, nComponentID)
      pUnitOperation.updateComponentDetails(pDBComponent)

      # Update the component
      self.database.UpdateComponent(sRemoteUser, nComponentID, pDBComponent["componenttype"], pDBComponent["name"], json.dumps(pDBComponent))

    # Do a quick validation of the component
    self.validation.ValidateComponent(sRemoteUser, nSequenceID, nComponentID)

    # Move the component as needed
    if nInsertionID != None:
      self.database.MoveComponent(sRemoteUser, nComponentID, nInsertionID)

  def DeleteComponent(self, sRemoteUser, nSequenceID, nComponentID):
    """ Deletes a component """
    # Delete the component from the database
    self.database.DeleteComponent(sRemoteUser, nComponentID)

    # Flag the sequence validation as dirty
    self.database.UpdateSequenceDirtyFlag(sRemoteUser, nSequenceID, True)

  ### Internal functions ###

  def __PopReagent(self, sReagentName, pReagents):
    """ Locates the next reagent that matches the name and pops it off the list """
    nIndex = 0
    for pReagent in pReagents:
      if pReagent["name"] == sReagentName:
        return pReagents.pop(nIndex)
      nIndex += 1
    raise Exception("Too few '" + sReagentName + "' reagents in sequence")

