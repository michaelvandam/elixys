"""SequenceValidation

Validates synthesis sequences
"""

import json

class SequenceValidation:

  def __init__(self, pDatabase, pSequenceManager):
    """Constructor"""
    self.database = pDatabase
    self.sequenceManager = pSequenceManager

  ### Validation functions ###

  def ValidateSequenceFull(self, sRemoteUser, nSequenceID):
    """Performs a full validation of the sequence"""
    # Load the sequence and all of the reagents
    pSequence = self.sequenceManager.GetSequence(sRemoteUser, nSequenceID)
    pAllReagents = self.database.GetReagentsBySequence(sRemoteUser, nSequenceID)

    # Filter reagents to keep only those that are available
    pAvailableReagents = []
    for pReagent in pAllReagents:
      if pReagent["available"]:
        pAvailableReagents.append(pReagent)

    # Do a full validation of each component
    bValid = True
    for pComponent in pSequence["components"]:
      if not self.__ValidateComponentFull(sRemoteUser, pComponent, nSequenceID, pAvailableReagents):
        bValid = False

    # Save the validated components back to the database
    for pComponent in pSequence["components"]:
      self.__SaveComponentValidation(sRemoteUser, pComponent, pComponent["id"])

    # Update the valid flag in the database and return
    self.database.UpdateSequence(sRemoteUser, nSequenceID, pSequence["metadata"]["name"], pSequence["metadata"]["comment"], bValid)
    self.database.UpdateSequenceDirtyFlag(sRemoteUser, nSequenceID, False)
    return bValid

  def InitializeComponent(self, sRemoteUser, nSequenceID, nComponentID):
    """Initializes the validation fields of a newly added component"""
    # Initialize the validation fields of the raw component
    pComponent = self.database.GetComponent(sRemoteUser, nComponentID)
    self.__ValidateComponentInit(sRemoteUser, pComponent, nSequenceID)
    self.database.UpdateComponent(sRemoteUser, nComponentID, pComponent["componenttype"], pComponent["name"], json.dumps(pComponent))

    # Flag the sequence validation as dirty
    self.database.UpdateSequenceDirtyFlag(sRemoteUser, nSequenceID, True)

  def ValidateComponent(self, sRemoteUser, nSequenceID, nComponentID):
    """Performs a quick validation of the given component"""
    # Load the component and do a quick validation
    pComponent = self.sequenceManager.GetComponent(sRemoteUser, nComponentID, nSequenceID)
    self.__ValidateComponentQuick(sRemoteUser, pComponent, nSequenceID)

    # Initialize the component and do a quick validation
    self.__ValidateComponentInit(sRemoteUser, pComponent, nSequenceID)
    self.__ValidateComponentQuick(sRemoteUser, pComponent, nSequenceID)

    # Load the raw component and update just the validation field
    pDBComponent = self.database.GetComponent(sRemoteUser, nComponentID)
    pDBComponent["validationerror"] = pComponent["validationerror"]
    self.database.UpdateComponent(sRemoteUser, nComponentID, pDBComponent["componenttype"], pDBComponent["name"], json.dumps(pDBComponent))

    # Flag the sequence validation as dirty
    self.database.UpdateSequenceDirtyFlag(sRemoteUser, nSequenceID, True)

  ### Internal functions ###

  def __ValidateComponentFull(self, sRemoteUser, pComponent, nSequenceID, pAvailableReagents):
    """Fully validate the given component"""
    # Initialize the validation fields
    self.__ValidateComponentInit(sRemoteUser, pComponent, nSequenceID)

    # Fill in the validation fields based on component type
    if pComponent["componenttype"] == "ADD":
      # Set the name and validation strings
      pComponent["name"] = "Add"
      pComponent["reactorvalidation"] = "type=enum-number; values=1,2,3; required=true"
      pComponent["reagentvalidation"] = "type=enum-reagent; values=" + self.__ListReagents(pAvailableReagents) + "; required=true"
      pComponent["deliverypositionvalidation"] = "type=enum-number; values=1,2; required=true"
      pComponent["deliverytimevalidation"] = "type=number; min=0; max=10"
      pComponent["deliverypressurevalidation"] = "type=number; min=0; max=15"

      # Look up the reagent we are adding and remove it from the list of available reagents
      if pComponent["reagent"].has_key("reagentid"):
        pReagent = self.__GetReagentByID(pComponent["reagent"]["reagentid"], pAvailableReagents, True)
        if pReagent != None:
          # Set the component name
          pComponent["name"] = "Add " + pReagent["name"]
    elif pComponent["componenttype"] == "EVAPORATE":
      # Set the name and validation strings
      pComponent["name"] = "Evaporate"
      pComponent["reactorvalidation"] = "type=enum-number; values=1,2,3; required=true"
      pComponent["durationvalidation"] = "type=number; min=0; max=7200; required=true"
      pComponent["evaporationtemperaturevalidation"] = "type=number; min=20; max=200; required=true"
      pComponent["finaltemperaturevalidation"] = "type=number; min=20; max=200; required=true"
      pComponent["stirspeedvalidation"] = "type=number; min=0; max=5000; required=true"
      pComponent["evaporationpressurevalidation"] = "type=number; min=0; max=25"
    elif pComponent["componenttype"] == "TRANSFER":
      # Set the name and validation strings
      pComponent["name"] = "Transfer"
      pComponent["reactorvalidation"] = "type=enum-number; values=1,2,3; required=true"
      nTransferTargetID = self.__GetTarget(sRemoteUser, pComponent, nSequenceID, pAvailableReagents)
      pComponent["targetvalidation"] = "type=enum-target; values=" + str(nTransferTargetID) + "; required=true"

      # Look up the target we are transferring to
      if pComponent["target"].has_key("reagentid"):
        pTarget = self.__GetReagentByID(pComponent["target"]["reagentid"], pAvailableReagents, False)
        if (pTarget != None) and (pTarget["name"] == pComponent["target"]):
          # Set the component name
          pComponent["name"] = "Transfer to " + pTarget["name"]
    elif pComponent["componenttype"] == "ELUTE":
      # Set the name and validation strings
      pComponent["name"] = "Elute"
      pComponent["reactorvalidation"] = "type=enum-number; values=1,2,3; required=true"
      pComponent["reagentvalidation"] = "type=enum-reagent; values=" + self.__ListReagents(pAvailableReagents) + "; required=true"
      nEluteTargetID = self.__GetTarget(sRemoteUser, pComponent, nSequenceID, pAvailableReagents)
      pComponent["targetvalidation"] = "type=enum-target; values=" + str(nEluteTargetID) + "; required=true"

      # Look up the reagent we are eluting with
      if pComponent["reagent"].has_key("reagentid"):
        pReagent = self.__GetReagentByID(pComponent["reagent"]["reagentid"], pAvailableReagents, True)
        if pReagent != None:
          # Set the component name
          pComponent["name"] = "Elute with " + pReagent["name"]
    elif pComponent["componenttype"] == "REACT":
      # Set the name and validation strings
      pComponent["name"] = "React"
      pComponent["reactorvalidation"] = "type=enum-number; values=1,2,3; required=true"
      pComponent["positionvalidation"] = "type=enum-number; values=1,2; required=true"
      pComponent["durationvalidation"] = "type=number; min=0; max=7200; required=true"
      pComponent["reactiontemperaturevalidation"] = "type=number; min=20; max=200; required=true"
      pComponent["finaltemperaturevalidation"] = "type=number; min=20; max=200; required=true"
      pComponent["stirspeedvalidation"] = "type=number; min=0; max=5000; required=true"
    elif pComponent["componenttype"] == "PROMPT":
      # Set the name and validation strings
      pComponent["name"] = "Prompt"
      pComponent["messagevalidation"] = "type=string; required=true"
    elif pComponent["componenttype"] == "INSTALL":
      # Set the name and validation strings
      pComponent["name"] = "Install"
      pComponent["reactorvalidation"] = "type=enum-number; values=1,2,3; required=true"
      pComponent["messagevalidation"] = "type=string; required=true"
    elif pComponent["componenttype"] == "COMMENT":
      # Set the name and validation strings
      pComponent["name"] = "Comment"
      pComponent["commentvalidation"] = "type=string"

    # Do a quick validation of the component fields
    self.__ValidateComponentQuick(sRemoteUser, pComponent, nSequenceID)

  def __ValidateComponentInit(self, sRemoteUser, pComponent, nSequenceID):
    """Initializes the component validation fields"""
    # Validate based on component type
    if pComponent["componenttype"] == "ADD":
      if not pComponent.has_key("reactorvalidation"):
        pComponent.update({"reactorvalidation":""})
      if not pComponent.has_key("reagentvalidation"):
        pComponent.update({"reagentvalidation":""})
      if not pComponent.has_key("deliverypositionvalidation"):
        pComponent.update({"deliverypositionvalidation":""})
      if not pComponent.has_key("deliverytimevalidation"):
        pComponent.update({"deliverytimevalidation":""})
      if not pComponent.has_key("deliverypressurevalidation"):
        pComponent.update({"deliverypressurevalidation":""})
    elif pComponent["componenttype"] == "EVAPORATE":
      if not pComponent.has_key("reactorvalidation"):
        pComponent.update({"reactorvalidation":""})
      if not pComponent.has_key("durationvalidation"):
        pComponent.update({"durationvalidation":""})
      if not pComponent.has_key("evaporationtemperaturevalidation"):
        pComponent.update({"evaporationtemperaturevalidation":""})
      if not pComponent.has_key("finaltemperaturevalidation"):
        pComponent.update({"finaltemperaturevalidation":""})
      if not pComponent.has_key("stirspeedvalidation"):
        pComponent.update({"stirspeedvalidation":""})
      if not pComponent.has_key("evaporationpressurevalidation"):
        pComponent.update({"evaporationpressurevalidation":""})
    elif pComponent["componenttype"] == "TRANSFER":
      if not pComponent.has_key("reactorvalidation"):
        pComponent.update({"reactorvalidation":""})
      if not pComponent.has_key("targetvalidation"):
        pComponent.update({"targetvalidation":""})
    elif pComponent["componenttype"] == "ELUTE":
      if not pComponent.has_key("reactorvalidation"):
        pComponent.update({"reactorvalidation":""})
      if not pComponent.has_key("reagentvalidation"):
        pComponent.update({"reagentvalidation":""})
      if not pComponent.has_key("targetvalidation"):
        pComponent.update({"targetvalidation":""})
    elif pComponent["componenttype"] == "REACT":
      if not pComponent.has_key("reactorvalidation"):
        pComponent.update({"reactorvalidation":""})
      if not pComponent.has_key("positionvalidation"):
        pComponent.update({"positionvalidation":""})
      if not pComponent.has_key("durationvalidation"):
        pComponent.update({"durationvalidation":""})
      if not pComponent.has_key("reactiontemperaturevalidation"):
        pComponent.update({"reactiontemperaturevalidation":""})
      if not pComponent.has_key("finaltemperaturevalidation"):
        pComponent.update({"finaltemperaturevalidation":""})
      if not pComponent.has_key("stirspeedvalidation"):
        pComponent.update({"stirspeedvalidation":""})
    elif pComponent["componenttype"] == "PROMPT":
      if not pComponent.has_key("messagevalidation"):
        pComponent.update({"messagevalidation":""})
    elif pComponent["componenttype"] == "INSTALL":
      if not pComponent.has_key("reactorvalidation"):
        pComponent.update({"reactorvalidation":""})
      if not pComponent.has_key("messagevalidation"):
        pComponent.update({"messagevalidation":""})
    elif pComponent["componenttype"] == "COMMENT":
      if not pComponent.has_key("commentvalidation"):
        pComponent.update({"commentvalidation":""})

    if not pComponent.has_key("validationerror"):
      pComponent.update({"validationerror":False})

  def __ValidateComponentQuick(self, sRemoteUser, pComponent, nSequenceID):
    """Performs a quick validation of the component"""
    # Validate based on component type
    bValidationError = False
    if pComponent["componenttype"] == "CASSETTE":
      for pReagent in pComponent["reagents"]:
        if pReagent["available"]:
          if not self.__ValidateComponentField(pReagent["name"], pReagent["namevalidation"]):
            bValidationError = True
          elif not self.__ValidateComponentField(pReagent["description"], pReagent["descriptionvalidation"]):
            bValidationError = True
    elif pComponent["componenttype"] == "ADD":
      if not self.__ValidateComponentField(pComponent["reactor"], pComponent["reactorvalidation"]):
        bValidationError = True
      elif not self.__ValidateComponentField(pComponent["reagent"], pComponent["reagentvalidation"]):
        bValidationError = True
      elif not self.__ValidateComponentField(pComponent["deliveryposition"], pComponent["deliverypositionvalidation"]):
        bValidationError = True
      elif not self.__ValidateComponentField(pComponent["deliverytime"], pComponent["deliverytimevalidation"]):
        bValidationError = True
      elif not self.__ValidateComponentField(pComponent["deliverypressure"], pComponent["deliverypressurevalidation"]):
        bValidationError = True
    elif pComponent["componenttype"] == "EVAPORATE":
      if not self.__ValidateComponentField(pComponent["reactor"], pComponent["reactorvalidation"]):
        bValidationError = True
      elif not self.__ValidateComponentField(pComponent["duration"], pComponent["durationvalidation"]):
        bValidationError = True
      elif not self.__ValidateComponentField(pComponent["evaporationtemperature"], pComponent["evaporationtemperaturevalidation"]):
        bValidationError = True
      elif not self.__ValidateComponentField(pComponent["finaltemperature"], pComponent["finaltemperaturevalidation"]):
        bValidationError = True
      elif not self.__ValidateComponentField(pComponent["stirspeed"], pComponent["stirspeedvalidation"]):
        bValidationError = True
      elif not self.__ValidateComponentField(pComponent["evaporationpressure"], pComponent["evaporationpressurevalidation"]):
        bValidationError = True
    elif pComponent["componenttype"] == "TRANSFER":
      if not self.__ValidateComponentField(pComponent["reactor"], pComponent["reactorvalidation"]):
        bValidationError = True
      elif not self.__ValidateComponentField(pComponent["target"], pComponent["targetvalidation"]):
        bValidationError = True
    elif pComponent["componenttype"] == "ELUTE":
      if not self.__ValidateComponentField(pComponent["reactor"], pComponent["reactorvalidation"]):
        bValidationError = True
      elif not self.__ValidateComponentField(pComponent["reagent"], pComponent["reagentvalidation"]):
        bValidationError = True
      elif not self.__ValidateComponentField(pComponent["target"], pComponent["targetvalidation"]):
        bValidationError = True
    elif pComponent["componenttype"] == "REACT":
      if not self.__ValidateComponentField(pComponent["reactor"], pComponent["reactorvalidation"]):
        bValidationError = True
      elif not self.__ValidateComponentField(pComponent["position"], pComponent["positionvalidation"]):
        bValidationError = True
      elif not self.__ValidateComponentField(pComponent["duration"], pComponent["durationvalidation"]):
        bValidationError = True
      elif not self.__ValidateComponentField(pComponent["reactiontemperature"], pComponent["reactiontemperaturevalidation"]):
        bValidationError = True
      elif not self.__ValidateComponentField(pComponent["finaltemperature"], pComponent["finaltemperaturevalidation"]):
        bValidationError = True
      elif not self.__ValidateComponentField(pComponent["stirspeed"], pComponent["stirspeedvalidation"]):
        bValidationError = True
    elif pComponent["componenttype"] == "PROMPT":
      if not self.__ValidateComponentField(pComponent["message"], pComponent["messagevalidation"]):
        bValidationError = True
    elif pComponent["componenttype"] == "INSTALL":
      if not self.__ValidateComponentField(pComponent["reactor"], pComponent["reactorvalidation"]):
        bValidationError = True
      elif not self.__ValidateComponentField(pComponent["message"], pComponent["messagevalidation"]):
        bValidationError = True

    # Set the validation error field
    pComponent.update({"validationerror":bValidationError})

  def __ValidateComponentField(self, pValue, sValidation):
    """ Validates the field using the validation string """
    # Skip empty validation fields
    if sValidation == "":
      return True

    # Create a dictionary from the validation string
    pValidation = {}
    pKeyValues = sValidation.split(";")
    for sKeyValue in pKeyValues:
      pComponents = sKeyValue.split("=")
      pValidation[pComponents[0].strip()] = pComponents[1].strip()

    # Call the appropriate validation function
    if pValidation["type"] == "enum-number":
      return self.__ValidateEnumNumber(pValue, pValidation)
    elif (pValidation["type"] == "enum-reagent") or (pValidation["type"] == "enum-target"):
      return self.__ValidateEnumReagent(pValue, pValidation)
    elif pValidation["type"] == "number":
      return self.__ValidateNumber(pValue, pValidation)
    elif pValidation["type"] == "string":
      return self.__ValidateString(pValue, pValidation)
    else:
      raise Exception("Unknown validation type")

  def __ValidateEnumNumber(self, nValue, pValidation):
    """ Validates an enumeration of numbers"""
    # Is the value set?
    if nValue == 0:
      # No, so check if it is required
      if pValidation.has_key("required"):
        if pValidation["required"]:
          return False

      # Valid
      return True
    else:
      # Yes, so make sure it is set to one of the allowed values
      pValues = pValidation["values"].split(",")
      for nValidValue in pValues:
        if float(nValue) == float(nValidValue):
          # Found it
          return True

      # Invalid
      return False

  def __ValidateEnumReagent(self, pReagent, pValidation):
    """ Validates an enumeration of reagents """
    # Is the value set?
    if not pReagent.has_key("reagentid"):
      # No, so check if it is required
      if pValidation.has_key("required"):
        if pValidation["required"]:
          return False

      # Valid
      return True
    else:
      # Yes, so validate the reagent ID
      return self.__ValidateEnumNumber(pReagent["reagentid"], pValidation)

  def __ValidateNumber(self, nValue, pValidation):
    """ Validates a number """
    # Is the value set?
    if nValue == 0:
      # No, so check if it is required
      if pValidation.has_key("required"):
        if pValidation["required"]:
          return False

      # Valid
      return True
    else:
      # Yes, so make sure it within the acceptable range
      if (float(nValue) >= float(pValidation["min"])) and (float(nValue) <= float(pValidation["max"])):
        return True
      else:
        return False

  def __ValidateString(self, sValue, pValidation):
    """ Validates a string """
    # Is the value set?
    if sValue == "":
      # No, so check if it is required
      if pValidation.has_key("required"):
        if pValidation["required"]:
          return False

    # Valid
    return True

  def __GetReagentByID(self, nReagentID, pReagents, bPopReagent):
    """ Locates the next reagent that matches the ID and returns it, optionally popping it off the list """
    nIndex = 0
    for pReagent in pReagents:
      if pReagent["reagentid"] == nReagentID:
        if bPopReagent:
          return pReagents.pop(nIndex)
        else:
          return pReagents[nIndex]
      nIndex += 1
    return None

  def __ListReagents(self, pReagents):
    """ Formats a list of reagent IDs """
    sReagentIDs = ""
    pUsedNames = {}
    for pReagent in pReagents:
      # Skip columns
      if not self.__IsNumber(pReagent["position"]):
        continue

      # Skip duplicate reagent names
      if pUsedNames.has_key(pReagent["name"]):
        continue
      else:
        pUsedNames[pReagent["name"]] = ""

      # Append the reagent ID
      if sReagentIDs != "":
        sReagentIDs += ","
      sReagentIDs += str(pReagent["reagentid"])
    return sReagentIDs

  def __GetTarget(self, sRemoteUser, pComponent, nSequenceID, pReagents):
    """ Gets the target ID """
    # Skip if reactor is zero
    if pComponent["reactor"] == 0:
      return 0

    # Look up the second column on the cassette associated with the reactor
    pColumn = self.database.GetReagentByPosition(sRemoteUser, nSequenceID, pComponent["reactor"], "B")

    # Check if the column is available
    if pColumn["available"]:
      return pColumn["reagentid"]
    else:
      return 0

  def __IsNumber(self, sValue):
    """ Check if the string contains a number """
    try:
      int(sValue)
      return True
    except ValueError:
      return False

  def __SaveComponentValidation(self, sRemoteUser, pComponent, nComponentID):
    """ Saves validation-specific fields back to the database """
    # Pull the original component from the database
    pDBComponent = self.database.GetComponent(sRemoteUser, nComponentID)

    # Copy the validation fields based on component type
    if pComponent["componenttype"] == "ADD":
      pDBComponent["name"] = pComponent["name"]
      pDBComponent["reactorvalidation"] = pComponent["reactorvalidation"]
      pDBComponent["reagentvalidation"] = pComponent["reagentvalidation"]
      pDBComponent["deliverypositionvalidation"] = pComponent["deliverypositionvalidation"]
      pDBComponent["deliverytimevalidation"] = pComponent["deliverytimevalidation"]
      pDBComponent["deliverypressurevalidation"] = pComponent["deliverypressurevalidation"]
      pDBComponent["deliverytime"] = pComponent["deliverytime"]
      pDBComponent["deliverypressure"] = pComponent["deliverypressure"]
    elif pComponent["componenttype"] == "EVAPORATE":
      pDBComponent["name"] = pComponent["name"]
      pDBComponent["reactorvalidation"] = pComponent["reactorvalidation"]
      pDBComponent["durationvalidation"] = pComponent["durationvalidation"]
      pDBComponent["evaporationtemperaturevalidation"] = pComponent["evaporationtemperaturevalidation"]
      pDBComponent["finaltemperaturevalidation"] = pComponent["finaltemperaturevalidation"]
      pDBComponent["stirspeedvalidation"] = pComponent["stirspeedvalidation"]
      pDBComponent["evaporationpressurevalidation"] = pComponent["evaporationpressurevalidation"]
      pDBComponent["evaporationpressure"] = pComponent["evaporationpressure"]
    elif pComponent["componenttype"] == "TRANSFER":
      pDBComponent["name"] = pComponent["name"]
      pDBComponent["reactorvalidation"] = pComponent["reactorvalidation"]
      pDBComponent["targetvalidation"] = pComponent["targetvalidation"]
    elif pComponent["componenttype"] == "ELUTE":
      pDBComponent["name"] = pComponent["name"]
      pDBComponent["reactorvalidation"] = pComponent["reactorvalidation"]
      pDBComponent["reagentvalidation"] = pComponent["reagentvalidation"]
      pDBComponent["targetvalidation"] = pComponent["targetvalidation"]
    elif pComponent["componenttype"] == "REACT":
      pDBComponent["name"] = pComponent["name"]
      pDBComponent["reactorvalidation"] = pComponent["reactorvalidation"]
      pDBComponent["positionvalidation"] = pComponent["positionvalidation"]
      pDBComponent["durationvalidation"] = pComponent["durationvalidation"]
      pDBComponent["reactiontemperaturevalidation"] = pComponent["reactiontemperaturevalidation"]
      pDBComponent["finaltemperaturevalidation"] = pComponent["finaltemperaturevalidation"]
      pDBComponent["stirspeedvalidation"] = pComponent["stirspeedvalidation"]
    elif pComponent["componenttype"] == "PROMPT":
      pDBComponent["name"] = pComponent["name"]
      pDBComponent["messagevalidation"] = pComponent["messagevalidation"]
    elif pComponent["componenttype"] == "INSTALL":
      pDBComponent["name"] = pComponent["name"]
      pDBComponent["reactorvalidation"] = pComponent["reactorvalidation"]
      pDBComponent["messagevalidation"] = pComponent["messagevalidation"]
    elif pComponent["componenttype"] == "COMMENT":
      pDBComponent["name"] = pComponent["name"]
      pDBComponent["commentvalidation"] = pComponent["commentvalidation"]

    # Copy the validation error field
    pDBComponent["validationerror"] = pComponent["validationerror"]

    # Save the component
    self.database.UpdateComponent(sRemoteUser, nComponentID, pDBComponent["componenttype"], pDBComponent["name"], json.dumps(pDBComponent))

