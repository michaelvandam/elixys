#!/usr/bin/python

# Imports
import json

# Default component values
DEFAULT_ADD_DELIVERYTIME = 10
DEFAULT_ADD_DELIVERYPRESSURE = 5
DEFAULT_EVAPORATE_PRESSURE = 10

class Utilities:
    # Constructor
    def __init__(self, pCoreServer, pDatabase, pLog):
        # Remember the input references
        self.__pCoreServer = pCoreServer
        self.__pDatabase = pDatabase
        self.__pLog = pLog

    # Fetch a sequence and components from the database
    def GetSequence(self, sRemoteUser, nSequenceID):
        # Fetch the sequence and reagents from the databse
        pSequence = self.__pDatabase.GetSequence(sRemoteUser, nSequenceID)
        pAllReagents = self.__pDatabase.GetReagentsBySequence(sRemoteUser, nSequenceID)

        # Filter reagents to keep only those that are available
        pReagents = []
        for pReagent in pAllReagents:
            if pReagent["available"]:
                pReagents.append(pReagent)

        # Add details to each component
        for pComponent in pSequence["components"]:
            self.__AddComponentDetails(sRemoteUser, pComponent, nSequenceID, pReagents)

        # Return
        return pSequence

    # Copy an existing sequence in the database
    def CopySequence(sRemoteUser, nSequenceID, sName, sComment, sType, nCassettes, nReagents, nColumns):
        # Create the new sequence
        nNewSequenceID = self.__pDatabase.CreateSequence(sRemoteUser, sName, sComment, sType, nCassettes, nReagents, nColumns)

        # Cassette loop
        for nCassette in range(1, nCassettes + 1):
            # Copy reagents
            for nReagent in range(1, nReagents + 1):
                pReagent = self.__pDatabase.GetReagentByPosition(sRemoteUser, nSequenceID, nCassette, str(nReagent))
                self.__pDatabase.UpdateReagentByPosition(sRemoteUser, nNewSequenceID, nCassette, str(nReagent), pReagent["available"],
                    pReagent["name"], pReagent["description"])

            # Copy columns
            for nColumn in range(0, nColumns):
                sPosition = chr(ord("A") + nColumn)
                pColumn = self.__pDatabase.GetReagentByPosition(sRemoteUser, nSequenceID, nCassette, sPosition)
                self.__pDatabase.UpdateReagentByPosition(sRemoteUser, nNewSequenceID, nCassette, sPosition, pReagent["available"], 
                    pReagent["name"], pReagent["description"])

            # Update the cassette settings
            #pCassette = gDatabase.GetCassette()
            #def UpdateComponentDetails(pTargetComponent, pSourceComponent):

        # Process each component of the sequence
        pSequence = GetSequence(sRemoteUser, nSequenceID)
        for pComponent in pSequence["components"]:
             if pComponent["componenttype"] == "CASSETTE":
                 self.__pLog("Update cassette: " + str(pComponent))
             else:
                 self.__pLog("Add component: " + str(pComponent))

        # Return the ID of the new sequence
        return nNewSequenceID    

    # Fetches a component from the database
    def GetComponent(self, sRemoteUser, nComponentID, nSequenceID):
        # Fetch the entire sequence and reagents from the databse
        pSequence = self.__pDatabase.GetSequence(sRemoteUser, nSequenceID)
        pAllReagents = self.__pDatabase.GetReagentsBySequence(sRemoteUser, nSequenceID)

        # Filter reagents to keep only those that are available
        pReagents = []
        for pReagent in pAllReagents:
            if pReagent["available"]:
                pReagents.append(pReagent)

        # Add details to each component until we find out component of interest
        for pComponent in pSequence["components"]:
            self.__AddComponentDetails(sRemoteUser, pComponent, nSequenceID, pReagents)
            if pComponent["id"] == nComponentID:
                return pComponent

        # Error
        raise Exception("Failed to find component")

    # Adds a new component to the database
    def AddComponent(self, sRemoteUser, nSequenceID, nInsertionID, pComponent):
        # Update the component fields we want to save
        pDBComponent = {}
        self.__UpdateComponentDetails(sRemoteUser, pDBComponent, pComponent)

        # Insert the new component
        return self.__pDatabase.InsertComponent(sRemoteUser, nSequenceID, pComponent["componenttype"], pComponent["name"], 
            json.dumps(pDBComponent), nInsertionID)

    # Updates an existing component
    def UpdateComponent(self, sRemoteUser, nSequenceID, nComponentID, nInsertionID, pComponent):
        # Update the component if one was provided
        if pComponent != None:
            self.__pLog("UpdateComponent: " + str(sRemoteUser) + ", " + str(nSequenceID) + ", " +  str(nComponentID) + ", " + str(nInsertionID) + ", " + str(pComponent))
            # Pull the component from the database and update it with the fields we want to save
            pDBComponent = self.__pDatabase.GetComponent(sRemoteUser, nComponentID)
            self.__UpdateComponentDetails(sRemoteUser, pDBComponent, pComponent)

            # Update the component
            self.__pDatabase.UpdateComponent(sRemoteUser, nComponentID, pDBComponent["componenttype"], pDBComponent["name"], json.dumps(pDBComponent))

        # Move the component as needed
        if nInsertionID != None:
            self.__pDatabase.MoveComponent(sRemoteUser, nComponentID, nInsertionID)

    # Deletes a component
    def DeleteComponent(self, sRemoteUser, nComponentID):
        # Check if the user is currently viewing this component
        sClientState = self.__pDatabase.GetUserClientState(sRemoteUser, sRemoteUser)
        pClientStateComponents = sClientState.split(".")
        nClientComponentID = int(pClientStateComponents[2])
        if nClientComponentID == nComponentID:
            # Yes, so move the user to the next component in the sequence
            pComponent = self.__pDatabase.GetNextComponent(sRemoteUser, nComponentID)
            if pComponent == None:
                # This is the last component in the sequence so move to the previous component
                pComponent = self.__pDatabase.GetPreviousComponent(sRemoteUser, nComponentID)
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
            self.__pDatabase.UpdateUserClientState(sRemoteUser, sRemoteUser, sClientState)

        # Delete the component from the database
        self.__pDatabase.DeleteComponent(sRemoteUser, nComponentID)

    # Gets a reagent from the database
    def GetReagent(self, sRemoteUser, nReagentID):
        # Fetch the reagent from the databse
        pReagent = self.__pDatabase.GetReagent(sRemoteUser, nReagentID)

        # Add details to the reagent and return
        pReagent["namedescription"] = "Short name of this reagent"
        pReagent["namevalidation"] = "type=string; required=true"
        pReagent["descriptiondescription"] = "Long name of this reagent"
        pReagent["descriptionvalidation"] = "type=string"
        return pReagent

    # Adds details to the component after retrieving it from the database and prior to sending it to the client
    def __AddComponentDetails(self, sRemoteUser, pComponent, nSequenceID, pReagents):
        # Details we add depends on the component type
        if pComponent["componenttype"] == "CASSETTE":
            # Set the description and validation strings
            pComponent.update({"reactordescription":"Reactor associated with this cassette"})
            pComponent.update({"reactorvalidation":"type=enum-number; values=1,2,3; required=true"})

            # Look up each reagent in this cassette
            pReagentIDs = pComponent["reagentids"]
            pReagents = []
            for nReagentID in pReagentIDs:
                pReagents.append(self.GetReagent(sRemoteUser, int(nReagentID)))
            del pComponent["reagentids"]
            pComponent["reagents"] = pReagents

            # Validate the component fields
            if not self.__ValidateComponentField(pComponent["reactor"], pComponent["reactorvalidation"]):
                pComponent.update({"validationerror":True})
            else:
                pComponent.update({"validationerror":False})
        elif pComponent["componenttype"] == "ADD":
            # Set the description and validation strings
            pComponent.update({"reactordescription":"Reactor where the reagent will be added"})
            pComponent.update({"reactorvalidation":"type=enum-number; values=1,2,3; required=true"})
            pComponent.update({"reagentdescription":"Reagent to add to the reactor"})
            pComponent.update({"reagentvalidation":"type=enum-reagent; values=" + self.__ListReagents(pReagents) + "; required=true"})
            pComponent.update({"deliverypositiondescription":"Delivery position where the reagent will be added"})
            pComponent.update({"deliverypositionvalidation":"type=enum-number; values=1,2; required=true"})
            pComponent.update({"deliverytimedescription":"Number of seconds to deliver the reagent"})
            pComponent.update({"deliverytimevalidation":"type=number; min=0; max=10"})
            pComponent.update({"deliverypressuredescription":"Pressure in PSI to use when delivering the reagent"})
            pComponent.update({"deliverypressurevalidation":"type=number; min=0; max=15"})

            # Look up the reagent we are adding
            bValidationError = False
            pAddReagent = {}
            sName = "Add"
            if pComponent["reagent"] != "":
                pReagent = self.__GetReagentByName(pComponent["reagent"], pReagents, True)
                if pReagent != None:
                    pAddReagent = pReagent
                    sName += " " + pReagent["name"]
                else:
                    bValidationError = True

            # Replace the reagent and set the component name
            del pComponent["reagent"]
            pComponent["reagent"] = pAddReagent
            pComponent.update({"name":sName})

            # Set the default delivery time and pressure if the values are zero
            if pComponent["deliverytime"] == 0:
                pComponent["deliverytime"] = DEFAULT_ADD_DELIVERYTIME
            if pComponent["deliverypressure"] == 0:
                pComponent["deliverypressure"]= DEFAULT_ADD_DELIVERYPRESSURE

            # Validate the component fields
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
            pComponent.update({"validationerror":bValidationError})
        elif pComponent["componenttype"] == "EVAPORATE":
            # Set the name, description and validation strings
            pComponent.update({"name":"Evaporate"})
            pComponent.update({"reactordescription":"Reactor where the evaporation will be performed"})
            pComponent.update({"reactorvalidation":"type=enum-number; values=1,2,3; required=true"})
            pComponent.update({"durationdescription":"Duration of evaporation after the target temperature is reached"})
            pComponent.update({"durationvalidation":"type=number; min=0; max=7200; required=true"})
            pComponent.update({"evaporationtemperaturedescription":"Reaction temperature in degrees Celsius"})
            pComponent.update({"evaporationtemperaturevalidation":"type=number; min=20; max=200; required=true"})
            pComponent.update({"finaltemperaturedescription":"Final temperature after evaporation in degrees Celsius"})
            pComponent.update({"finaltemperaturevalidation":"type=number; min=20; max=200; required=true"})
            pComponent.update({"stirspeeddescription":"Speed of the stir bar in arbitrary units"})
            pComponent.update({"stirspeedvalidation":"type=number; min=0; max=5000; required=true"})
            pComponent.update({"evaporationpressuredescription":"Pressure in PSI to use when evaporating"})
            pComponent.update({"evaporationpressurevalidation":"type=number; min=0; max=25"})

            # Set the default evaporation pressure if the value is zero
            if pComponent["evaporationpressure"] == 0:
                pComponent["evaporationpressure"] = DEFAULT_EVAPORATE_PRESSURE

            # Validate the component fields
            bValidationError = False
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
            pComponent.update({"validationerror":bValidationError})
        elif pComponent["componenttype"] == "TRANSFER":
            # Set the name, description and validation strings
            pComponent.update({"name":"Transfer"})
            pComponent.update({"reactordescription":"Reactor where the source reagent resides"})
            pComponent.update({"reactorvalidation":"type=enum-number; values=1,2,3; required=true"})
            pComponent.update({"targetdescription":"Target where the reactor contents will be transferred"})
            nTransferTargetID = self.__GetTarget(sRemoteUser, pComponent, nSequenceID, pReagents)
            pComponent.update({"targetvalidation":"type=enum-target; values=" + str(nTransferTargetID) + "; required=true"})

            # Look up the target to which we are transferring
            bValidationError = False
            pEluteTarget = {}
            sName = "Transfer"
            if pComponent["target"] != "":
                pTarget = self.__GetReagentByID(nTransferTargetID, pReagents, False)
                if (pTarget != None) and (pTarget["name"] == pComponent["target"]):
                    sName += " to " + pTarget["name"]
                    pEluteTarget = pTarget
                else:
                    bValidationError = True

            # Replace the target and set the component name
            del pComponent["target"]
            pComponent["target"] = pEluteTarget
            pComponent.update({"name":sName})

            # Validate the component fields
            if not self.__ValidateComponentField(pComponent["reactor"], pComponent["reactorvalidation"]):
                bValidationError = True
            elif not self.__ValidateComponentField(pComponent["target"], pComponent["targetvalidation"]):
                bValidationError = True
            pComponent.update({"validationerror":bValidationError})
        elif pComponent["componenttype"] == "ELUTE":
            # Set the description and validation strings
            pComponent.update({"reactordescription":"Reactor where the reagent will be eluted"})
            pComponent.update({"reactorvalidation":"type=enum-number; values=1,2,3; required=true"})
            pComponent.update({"reagentdescription":"Reagent used to elute the target"})
            pComponent.update({"reagentvalidation":"type=enum-reagent; values=" + self.__ListReagents(pReagents) + "; required=true"})
            pComponent.update({"targetdescription":"Target to be eluted with the reagent"})
            nEluteTargetID = self.__GetTarget(sRemoteUser, pComponent, nSequenceID, pReagents)
            pComponent.update({"targetvalidation":"type=enum-target; values=" + str(nEluteTargetID) + "; required=true"})

            # Look up the reagent and target we are eluting
            bValidationError = False
            pEluteReagent = {}
            pEluteTarget = {}
            sName = "Elute"
            if pComponent["reagent"] != "":
                pReagent = self.__GetReagentByName(pComponent["reagent"], pReagents, True)
                if pReagent != None:
                    pEluteReagent = pReagent
                    sName += " with " + pReagent["name"]
                else:
                    bValidationError = True
            if pComponent["target"] != "":
                pTarget = self.__GetReagentByID(nEluteTargetID, pReagents, False)
                if (pTarget != None) and (pTarget["name"] == pComponent["target"]):
                    pEluteTarget = pTarget
                else:
                    bValidationError = True

            # Replace the reagent and target and set the component name
            del pComponent["reagent"]
            del pComponent["target"]
            pComponent["reagent"] = pEluteReagent
            pComponent["target"] = pEluteTarget
            pComponent.update({"name":sName})

            # Validate the component fields
            if not self.__ValidateComponentField(pComponent["reactor"], pComponent["reactorvalidation"]):
                bValidationError = True
            elif not self.__ValidateComponentField(pComponent["reagent"], pComponent["reagentvalidation"]):
                bValidationError = True
            elif not self.__ValidateComponentField(pComponent["target"], pComponent["targetvalidation"]):
                bValidationError = True
            pComponent.update({"validationerror":bValidationError})
        elif pComponent["componenttype"] == "REACT":
            # Set the name, description and validation strings
            pComponent.update({"name":"React"})
            pComponent.update({"reactordescription":"Reactor where the reaction will be performed"})
            pComponent.update({"reactorvalidation":"type=enum-number; values=1,2,3; required=true"})
            pComponent.update({"positiondescription":"Position where the reaction will take place"})
            pComponent.update({"positionvalidation":"type=enum-number; values=1,2; required=true"})
            pComponent.update({"durationdescription":"Duration of reaction after the target temperature is reached"})
            pComponent.update({"durationvalidation":"type=number; min=0; max=7200; required=true"})
            pComponent.update({"reactiontemperaturedescription":"Reaction temperature in degrees Celsius"})
            pComponent.update({"reactiontemperaturevalidation":"type=number; min=20; max=200; required=true"})
            pComponent.update({"finaltemperaturedescription":"Final temperature after evaporation in degrees Celsius"})
            pComponent.update({"finaltemperaturevalidation":"type=number; min=20; max=200; required=true"})
            pComponent.update({"stirspeeddescription":"Speed of the stir bar in arbitrary units"})
            pComponent.update({"stirspeedvalidation":"type=number; min=0; max=5000; required=true"})

            # Validate the component fields
            bValidationError = False
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
            pComponent.update({"validationerror":bValidationError})
        elif pComponent["componenttype"] == "PROMPT":
            # Set the name, description and validation strings
            pComponent.update({"name":"Prompt"})
            pComponent.update({"messagedescription":"Prompt that will be displayed to the user"})
            pComponent.update({"messagevalidation":"type=string; required=true"})

            # Validate the component fields
            bValidationError = False
            if not self.__ValidateComponentField(pComponent["message"], pComponent["messagevalidation"]):
                pComponent.update({"validationerror":True})
            else:
                pComponent.update({"validationerror":False})
        elif pComponent["componenttype"] == "INSTALL":
            # Set the name, description and validation strings
            pComponent.update({"name":"Install"})
            pComponent.update({"reactordescription":"Reactor that will be moved to the install position"})
            pComponent.update({"reactorvalidation":"type=enum-number; values=1,2,3; required=true"})
            pComponent.update({"messagedescription":"Prompt that will be displayed to the user"})
            pComponent.update({"messagevalidation":"type=string; required=true"})

            # Validate the component fields
            bValidationError = False
            if not self.__ValidateComponentField(pComponent["reactor"], pComponent["reactorvalidation"]):
                bValidationError = True
            elif not self.__ValidateComponentField(pComponent["message"], pComponent["messagevalidation"]):
                bValidationError = True
            pComponent.update({"validationerror":bValidationError})
        elif pComponent["componenttype"] == "COMMENT":
            # Set the name, description and validation strings
            pComponent.update({"name":"Comment"})
            pComponent.update({"commentdescription":"Enter a comment"})
            pComponent.update({"commentvalidation":"type=string"})
            pComponent.update({"validationerror":False})

    # Strips a component down to only the details we want to save in the database
    def __UpdateComponentDetails(self, sRemoteUser, pTargetComponent, pSourceComponent):
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

            # Save the reagent by name
            if pSourceComponent["reagent"] != 0:
                pReagent = self.__pDatabase.GetReagent(sRemoteUser, pSourceComponent["reagent"])
                pTargetComponent["reagent"] = pReagent["name"]
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

            # Save the target by name
            if pSourceComponent["target"] != 0:
                pTarget = self.__pDatabase.GetReagent(sRemoteUser, pSourceComponent["target"])
                pTargetComponent["target"] = pTarget["name"]
        elif pTargetComponent["componenttype"] == "ELUTE":
            # Update the component fields
            pTargetComponent["reactor"] = pSourceComponent["reactor"]

            # Save the reagent and target by name
            if pSourceComponent["reagent"] != 0:
                pReagent = self.__pDatabase.GetReagent(sRemoteUser, pSourceComponent["reagent"])
                pTargetComponent["reagent"] = pReagent["name"]
            if pSourceComponent["target"] != 0:
                pTarget = self.__pDatabase.GetReagent(sRemoteUser, pSourceComponent["target"])
                pTargetComponent["target"] = pTarget["name"]
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

    # Validates the field using the validation string
    def __ValidateComponentField(self, pValue, sValidation):
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

    # Validates an enumeration of numbers
    def __ValidateEnumNumber(self, nValue, pValidation):
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

    # Validates an enumeration of reagents
    def __ValidateEnumReagent(self, pReagent, pValidation):
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

    # Validates a number
    def __ValidateNumber(self, nValue, pValidation):
        return True
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

    # Validates a string
    def __ValidateString(self, sValue, pValidation):
        # Is the value set?
        if sValue == "":
            # No, so check if it is required
            if pValidation.has_key("required"):
                if pValidation["required"]:
                    return False

        # Valid
        return True

    # Locates the next reagent that matches the name and returns it, optionally popping it off the list
    def __GetReagentByName(self, sReagentName, pReagents, bPopReagent):
        nIndex = 0
        for pReagent in pReagents:
            if pReagent["name"] == sReagentName:
                if bPopReagent:
                    return pReagents.pop(nIndex)
                else:
                    return pReagents[nIndex]
            nIndex += 1
        return None

    # Locates the next reagent that matches the ID and returns it, optionally popping it off the list
    def __GetReagentByID(self, nReagentID, pReagents, bPopReagent):
        nIndex = 0
        for pReagent in pReagents:
            if pReagent["reagentid"] == nReagentID:
                if bPopReagent:
                    return pReagents.pop(nIndex)
                else:
                    return pReagents[nIndex]
            nIndex += 1
        return None

    # Formats a list of reagent IDs
    def __ListReagents(self, pReagents):
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

    # Gets the target ID
    def __GetTarget(self, sRemoteUser, pComponent, nSequenceID, pReagents):
        # Do we have a valid reactor?
        if not self.__ValidateComponentField(pComponent["reactor"], pComponent["reactorvalidation"]):
            # No, so we cannot find our target
            return 0

        # Look up the second column on the cassette associated with the reactor
        pColumn = self.__pDatabase.GetReagentByPosition(sRemoteUser, nSequenceID, int(pComponent["reactor"]), "B")

        # Check if the column is available
        if pColumn["available"]:
            return pColumn["reagentid"]
        else:
            return 0

    # Check if the string contains a number
    def __IsNumber(self, sValue):
        try:
            int(sValue)
            return True
        except ValueError:
            return False

