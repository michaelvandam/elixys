"""SequenceManager

Elixys Sequence Manager
"""

import json
import sys
sys.path.append("/opt/elixys/core/unitoperations")
import UnitOperations

class SequenceManager:

  def __init__(self, pDatabase):
    self.database = pDatabase

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
    nNewSequenceID = self.database.CreateSequence(sRemoteUser, sName, sComment, "Saved", pConfiguration["reactors"], pConfiguration["reagentsperreactor"])

    # Copy each component of the sequence
    pSequence = self.GetSequence(sRemoteUser, nSequenceID)
    for pComponent in pSequence["components"]:
      pUnitOperation = UnitOperations.createFromComponent(nSequenceID, pComponent, sRemoteUser, self.database)
      pUnitOperation.copyComponent(nSequenceID, nNewSequenceID)

    # Validate the sequence
    self.ValidateSequenceFull(sRemoteUser, nNewSequenceID)

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
    #print "REACTORS " + str(pConfiguration['reagentsperreactor'])
    #print "REACTORS " + str(pSequence["reagentsperreactor"]) 
    if (pSequence["reactors"] != pConfiguration["reactors"]) or \
	 (pSequence["reagentsperreactor"] >= pConfiguration["reagentsperreactor"]):
      raise Exception("This sequence you are trying to import does not match the system hardware")

    # Create the sequence
    if (pSequence["type"] == "sequence") and \
	 (pSequence["name"] != "") and \
	 (pSequence["reactors"] != 0) and \
	(pSequence["reagentsperreactor"] != 0):
      nSequenceID = self.database.CreateSequence(sRemoteUser, pSequence["name"], 
						pSequence["description"], sType, 
						pSequence["reactors"], 
        					pSequence["reagentsperreactor"])
						 
    else:
      raise Exception("Invalid sequence parameters")

    # Add the reagents
    for pReagent in pSequence["reagents"]:
      if (pReagent["type"] == "reagent") and \
	 (pReagent["cassette"] != 0) and \
	(pReagent["position"] != "") and \
	(pReagent["name"] != ""):
        self.database.UpdateReagentByPosition(sRemoteUser, nSequenceID, 
						pReagent["cassette"], pReagent["position"], 
						pReagent["name"], pReagent["description"])
      else:
        raise Exception("Invalid reagent parameters in \"" + str(pReagent) + "\"")

    # Create a list of available reagents
    pAllReagents = self.database.GetReagentsBySequence(sRemoteUser, nSequenceID)
    pAvailableReagents = []
    for pReagent in pAllReagents:
      if pReagent["name"] != "":
        pAvailableReagents.append(pReagent)

    # Process each component
    for pComponent in pSequence["components"]:
      if (pComponent["type"] != ""):
        # Convert reagent names into IDs
        if pComponent.has_key("reagent"):
          pReagent = self.__PopReagent(pComponent["reagent"], pAvailableReagents)
          pComponent["reagent"] = pReagent["reagentid"]

        # Add the component
        self.database.CreateComponent(sRemoteUser, 
					nSequenceID, 
					pComponent["componenttype"], 
					"", 
					json.dumps(pComponent))
      else:
        raise Exception("Invalid reagent parameters in \"" + str(pReagent) + "\"")

    # Validate the sequence
    self.ValidateSequenceFull(sRemoteUser, nSequenceID)

  def ExportSequence(self, sRemoteUser, nSequenceID, sFilename):
    """Exports the specified sequence from the database"""
    # Load the sequence
    pDBSequence = self.GetSequence(sRemoteUser, nSequenceID, False)

    # Get the system configuration
    pConfiguration = self.database.GetConfiguration(sRemoteUser)

    # Create the sequence
    pSequence = {}
    pSequence["type"] ="sequence"
    pSequence["name"] = pDBSequence["metadata"]["name"]
    pSequence["description"] = pDBSequence["metadata"]["comment"]
    pSequence["reactors"] = pConfiguration["reactors"]
    pSequence["reagentsperreactor"] = pConfiguration["reagentsperreactor"]
    pSequence["reagents"] = []
    pSequence["components"] = []

    # Add the reagents from each cassette
    nCassette = 1
    for pComponent in pDBSequence["components"]:
        if pComponent["componenttype"] == "CASSETTE":
            pCassette = UnitOperations.createFromComponent(nSequenceID, pComponent, sRemoteUser, self.database)
            pCassette.addComponentDetails()
            for pReagent in pCassette.component["reagents"]:
                if pReagent["name"] != "":
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
    nComponentID = self.database.InsertComponent(sRemoteUser, nSequenceID, pDBComponent["componenttype"], pDBComponent["note"], 
      json.dumps(pDBComponent), nInsertionID)

    # Initialize the new component's validation fields
    self.InitializeComponent(sRemoteUser, nSequenceID, nComponentID)
    self.ValidateComponent(sRemoteUser, nSequenceID, nComponentID)
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
      self.database.UpdateComponent(sRemoteUser, nComponentID, pDBComponent["componenttype"], pDBComponent["note"], json.dumps(pDBComponent))

    # Do a quick validation of the component
    self.ValidateComponent(sRemoteUser, nSequenceID, nComponentID)

    # Move the component as needed
    if nInsertionID != None:
      self.database.MoveComponent(sRemoteUser, nComponentID, nInsertionID)

  def DeleteComponent(self, sRemoteUser, nSequenceID, nComponentID):
    """ Deletes a component """
    # Delete the component from the database
    self.database.DeleteComponent(sRemoteUser, nComponentID)

    # Flag the sequence validation as dirty
    self.database.UpdateSequenceDirtyFlag(sRemoteUser, nSequenceID, True)

  ### Validation functions ###

  def ValidateSequenceFull(self, sRemoteUser, nSequenceID):
    """Performs a full validation of the sequence"""
    # Load the sequence and all of the reagents
    pSequence = self.GetSequence(sRemoteUser, nSequenceID)
    pAllReagents = self.database.GetReagentsBySequence(sRemoteUser, nSequenceID)

    # Filter reagents to keep only those that have a name
    pAvailableReagents = []
    for pReagent in pAllReagents:
      if pReagent["name"] != "":
        pAvailableReagents.append(pReagent)

    # Do a full validation of each component
    bValid = True
    for pComponent in pSequence["components"]:
      pUnitOperation = UnitOperations.createFromComponent(nSequenceID, pComponent, sRemoteUser, self.database)
      if not pUnitOperation.validateFull(pAvailableReagents):
        bValid = False
      pUnitOperation.saveValidation()

    # Update the valid flag in the database and return
    self.database.UpdateSequence(sRemoteUser, nSequenceID, pSequence["metadata"]["name"], pSequence["metadata"]["comment"], bValid)
    self.database.UpdateSequenceDirtyFlag(sRemoteUser, nSequenceID, False)
    return bValid

  def InitializeComponent(self, sRemoteUser, nSequenceID, nComponentID):
    """Initializes the validation fields of a newly added component"""
    # Initialize the validation fields of the raw component
    pComponent = self.database.GetComponent(sRemoteUser, nComponentID)
    pUnitOperation = UnitOperations.createFromComponent(nSequenceID, pComponent, sRemoteUser, self.database)
    self.database.UpdateComponent(sRemoteUser, nComponentID, pComponent["componenttype"], pUnitOperation.component["note"], json.dumps(pUnitOperation.component))

    # Flag the sequence validation as dirty
    self.database.UpdateSequenceDirtyFlag(sRemoteUser, nSequenceID, True)

  def ValidateComponent(self, sRemoteUser, nSequenceID, nComponentID):
    """Performs a quick validation of the given component"""
    # Load the component and do a quick validation
    pComponent = self.GetComponent(sRemoteUser, nComponentID, nSequenceID)
    pUnitOperation = UnitOperations.createFromComponent(nSequenceID, pComponent, sRemoteUser, self.database)
    pUnitOperation.validateQuick()

    # Load the raw component and update just the validation field
    pDBComponent = self.database.GetComponent(sRemoteUser, nComponentID)
    pDBComponent["validationerror"] = pUnitOperation.component["validationerror"]
    self.database.UpdateComponent(sRemoteUser, nComponentID, pDBComponent["componenttype"], pDBComponent["note"], json.dumps(pDBComponent))

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

