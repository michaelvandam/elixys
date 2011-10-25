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

    # Set the name and validation strings based on component type
    if pComponent["componenttype"] == "ADD":
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
      pComponent["name"] = "Evaporate"
      pComponent["reactorvalidation"] = "type=enum-number; values=1,2,3; required=true"
      pComponent["durationvalidation"] = "type=number; min=0; max=7200; required=true"
      pComponent["evaporationtemperaturevalidation"] = "type=number; min=20; max=200; required=true"
      pComponent["finaltemperaturevalidation"] = "type=number; min=20; max=200; required=true"
      pComponent["stirspeedvalidation"] = "type=number; min=0; max=5000; required=true"
      pComponent["evaporationpressurevalidation"] = "type=number; min=0; max=25"
    elif pComponent["componenttype"] == "TRANSFER":
      pComponent["name"] = "Transfer"
      pComponent["sourcereactorvalidation"] = "type=enum-number; values=1,2,3; required=true"
      pComponent["targetreactorvalidation"] = "type=enum-number; values=1,2,3; required=true"
      pComponent["pressurevalidation"] = "type=number; min=0; max=25"
      pComponent["modevalidation"] = "type=enum-string; values=Trap,Elute; required=true"
      pComponent["durationvalidation"] = "type=number; min=0; max=7200; required=true"
    elif pComponent["componenttype"] == "REACT":
      pComponent["name"] = "React"
      pComponent["reactorvalidation"] = "type=enum-number; values=1,2,3; required=true"
      pComponent["positionvalidation"] = "type=enum-number; values=1,2; required=true"
      pComponent["durationvalidation"] = "type=number; min=0; max=7200; required=true"
      pComponent["reactiontemperaturevalidation"] = "type=number; min=20; max=200; required=true"
      pComponent["finaltemperaturevalidation"] = "type=number; min=20; max=200; required=true"
      pComponent["stirspeedvalidation"] = "type=number; min=0; max=5000; required=true"
    elif pComponent["componenttype"] == "PROMPT":
      pComponent["name"] = "Prompt"
      pComponent["messagevalidation"] = "type=string; required=true"
    elif pComponent["componenttype"] == "INSTALL":
      pComponent["name"] = "Install"
      pComponent["reactorvalidation"] = "type=enum-number; values=1,2,3; required=true"
      pComponent["messagevalidation"] = "type=string; required=true"
    elif pComponent["componenttype"] == "COMMENT":
      pComponent["name"] = "Comment"
      pComponent["commentvalidation"] = "type=string"
    elif pComponent["componenttype"] == "DELIVERF18":
      pComponent["name"] = "Deliver F18"
      pComponent["reactorvalidation"] = "type=enum-number; values=1,2,3; required=true"
      pComponent["traptimevalidation"] = "type=number; min=0; max=7200; required=true"
      pComponent["trappressurevalidation"] = "type=number; min=0; max=25"
      pComponent["elutetimevalidation"] = "type=number; min=0; max=7200; required=true"
      pComponent["elutepressurevalidation"] = "type=number; min=0; max=25"
    elif pComponent["componenttype"] == "INITIALIZE":
      pComponent["name"] = "Initialize"
    elif pComponent["componenttype"] == "MIX":
      pComponent["name"] = "Mix"
      pComponent["reactorvalidation"] = "type=enum-number; values=1,2,3; required=true"
      pComponent["mixtimevalidation"] = "type=number; min=0; max=7200; required=true"
      pComponent["stirspeedvalidation"] = "type=number; min=0; max=5000; required=true"
    elif pComponent["componenttype"] == "MOVE":
      pComponent["name"] = "Move"
      pComponent["reactorvalidation"] = "type=enum-number; values=1,2,3; required=true"
      pComponent["positionvalidation"] = "type=enum-string; values=" + (",").join(self.database.GetReactorPositions(sRemoteUser)) + "; required=true"

    # Do a quick validation of the component fields and return if the component is valid
    return self.__ValidateComponentQuick(sRemoteUser, pComponent, nSequenceID)

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
      if not pComponent.has_key("sourcereactorvalidation"):
        pComponent.update({"sourcereactorvalidation":""})
      if not pComponent.has_key("targetreactorvalidation"):
        pComponent.update({"targetreactorvalidation":""})
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
    elif pComponent["componenttype"] == "DELIVERF18":
      if not pComponent.has_key("reactorvalidation"):
        pComponent.update({"reactorvalidation":""})
      if not pComponent.has_key("traptimevalidation"):
        pComponent.update({"traptimevalidation":""})
      if not pComponent.has_key("trappressurevalidation"):
        pComponent.update({"trappressurevalidation":""})
      if not pComponent.has_key("elutepressurevalidation"):
        pComponent.update({"elutepressurevalidation":""})
      if not pComponent.has_key("elutetimevalidation"):
        pComponent.update({"elutetimevalidation":""})
    elif pComponent["componenttype"] == "MIX":
      if not pComponent.has_key("reactorvalidation"):
        pComponent.update({"reactorvalidation":""})
      if not pComponent.has_key("mixtimevalidation"):
        pComponent.update({"mixtimevalidation":""})
      if not pComponent.has_key("stirspeedvalidation"):
        pComponent.update({"stirspeedvalidation":""})
    elif pComponent["componenttype"] == "MOVE":
      if not pComponent.has_key("reactorvalidation"):
        pComponent.update({"reactorvalidationvalidation":""})
      if not pComponent.has_key("positionvalidation"):
        pComponent.update({"positionvalidation":""})
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
      if not self.__ValidateComponentField(pComponent["sourcereactor"], pComponent["sourcereactorvalidation"]):
        bValidationError = True
      elif not self.__ValidateComponentField(pComponent["targetreactor"], pComponent["targetreactorvalidation"]):
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
    elif pComponent["componenttype"] == "DELIVERF18":
      if not self.__ValidateComponentField(pComponent["reactor"], pComponent["reactorvalidation"]):
        bValidationError = True
      elif not self.__ValidateComponentField(pComponent["traptime"], pComponent["traptimevalidation"]):
        bValidationError = True
      elif not self.__ValidateComponentField(pComponent["trappressure"], pComponent["trappressurevalidation"]):
        bValidationError = True
      elif not self.__ValidateComponentField(pComponent["elutetime"], pComponent["elutetimevalidation"]):
        bValidationError = True
      elif not self.__ValidateComponentField(pComponent["elutepressure"], pComponent["elutepressurevalidation"]):
        bValidationError = True
    elif pComponent["componenttype"] == "MIX":
      if not self.__ValidateComponentField(pComponent["reactor"], pComponent["reactorvalidation"]):
        bValidationError = True
      elif not self.__ValidateComponentField(pComponent["mixtime"], pComponent["mixtimevalidation"]):
        bValidationError = True
      elif not self.__ValidateComponentField(pComponent["stirspeed"], pComponent["stirspeedvalidation"]):
        bValidationError = True
    elif pComponent["componenttype"] == "MOVE":
      if not self.__ValidateComponentField(pComponent["reactor"], pComponent["reactorvalidation"]):
        bValidationError = True
      elif not self.__ValidateComponentField(pComponent["position"], pComponent["positionvalidation"]):
        bValidationError = True

    # Set the validation error field and return if the component is valid
    pComponent.update({"validationerror":bValidationError})
    return not bValidationError

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
    elif pValidation["type"] == "enum-reagent":
      return self.__ValidateEnumReagent(pValue, pValidation)
    elif pValidation["type"] == "enum-string":
      return self.__ValidateEnumString(pValue, pValidation)
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

  def __ValidateEnumString(self, sValue, pValidation):
    """ Validates an enumeration of strings"""
    # Is the value set?
    if sValue == "":
      # No, so check if it is required
      if pValidation.has_key("required"):
        if pValidation["required"]:
          return False

      # Valid
      return True
    else:
      # Yes, so make sure it is set to one of the allowed values
      pValues = pValidation["values"].split(",")
      for sValidValue in pValues:
        if sValue == sValidValue:
          # Found it
          return True

      # Invalid
      return False

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
    pDBComponent["name"] = pComponent["name"]
    if pComponent["componenttype"] == "ADD":
      pDBComponent["reactorvalidation"] = pComponent["reactorvalidation"]
      pDBComponent["reagentvalidation"] = pComponent["reagentvalidation"]
      pDBComponent["deliverypositionvalidation"] = pComponent["deliverypositionvalidation"]
      pDBComponent["deliverytimevalidation"] = pComponent["deliverytimevalidation"]
      pDBComponent["deliverypressurevalidation"] = pComponent["deliverypressurevalidation"]
      pDBComponent["deliverytime"] = pComponent["deliverytime"]
      pDBComponent["deliverypressure"] = pComponent["deliverypressure"]
    elif pComponent["componenttype"] == "EVAPORATE":
      pDBComponent["reactorvalidation"] = pComponent["reactorvalidation"]
      pDBComponent["durationvalidation"] = pComponent["durationvalidation"]
      pDBComponent["evaporationtemperaturevalidation"] = pComponent["evaporationtemperaturevalidation"]
      pDBComponent["finaltemperaturevalidation"] = pComponent["finaltemperaturevalidation"]
      pDBComponent["stirspeedvalidation"] = pComponent["stirspeedvalidation"]
      pDBComponent["evaporationpressurevalidation"] = pComponent["evaporationpressurevalidation"]
      pDBComponent["evaporationpressure"] = pComponent["evaporationpressure"]
    elif pComponent["componenttype"] == "TRANSFER":
      pDBComponent["sourcereactorvalidation"] = pComponent["sourcereactorvalidation"]
      pDBComponent["targetreactorvalidation"] = pComponent["targetreactorvalidation"]
      pDBComponent["pressurevalidation"] = pComponent["pressurevalidation"]
      pDBComponent["modevalidation"] = pComponent["modevalidation"]
      pDBComponent["durationvalidation"] = pComponent["durationvalidation"]
    elif pComponent["componenttype"] == "REACT":
      pDBComponent["reactorvalidation"] = pComponent["reactorvalidation"]
      pDBComponent["positionvalidation"] = pComponent["positionvalidation"]
      pDBComponent["durationvalidation"] = pComponent["durationvalidation"]
      pDBComponent["reactiontemperaturevalidation"] = pComponent["reactiontemperaturevalidation"]
      pDBComponent["finaltemperaturevalidation"] = pComponent["finaltemperaturevalidation"]
      pDBComponent["stirspeedvalidation"] = pComponent["stirspeedvalidation"]
    elif pComponent["componenttype"] == "PROMPT":
      pDBComponent["messagevalidation"] = pComponent["messagevalidation"]
    elif pComponent["componenttype"] == "INSTALL":
      pDBComponent["reactorvalidation"] = pComponent["reactorvalidation"]
      pDBComponent["messagevalidation"] = pComponent["messagevalidation"]
    elif pComponent["componenttype"] == "COMMENT":
      pDBComponent["commentvalidation"] = pComponent["commentvalidation"]
    elif pComponent["componenttype"] == "DELIVERF18":
      pDBComponent["reactorvalidation"] = pComponent["reactorvalidation"]
      pDBComponent["traptimevalidation"] = pComponent["traptimevalidation"]
      pDBComponent["trappressurevalidation"] = pComponent["trappressurevalidation"]
      pDBComponent["elutetimevalidation"] = pComponent["elutetimevalidation"]
      pDBComponent["elutepressurevalidation"] = pComponent["elutepressurevalidation"]
    elif pComponent["componenttype"] == "MIX":
      pDBComponent["reactorvalidation"] = pComponent["reactorvalidation"]
      pDBComponent["mixtimevalidation"] = pComponent["mixtimevalidation"]
      pDBComponent["stirspeedvalidation"] = pComponent["stirspeedvalidation"]
    elif pComponent["componenttype"] == "MOVE":
      pDBComponent["reactorvalidation"] = pComponent["reactorvalidation"]
      pDBComponent["positionvalidation"] = pComponent["positionvalidation"]

    # Copy the validation error field
    pDBComponent["validationerror"] = pComponent["validationerror"]

    # Save the component
    self.database.UpdateComponent(sRemoteUser, nComponentID, pDBComponent["componenttype"], pDBComponent["name"], json.dumps(pDBComponent))

