#!/usr/bin/python

# Imports
import json

class Utilities:
    # Constructor
    def __init__(self, pCoreServer, pDatabase, pLog):
        # Remember the input references
        self.__pCoreServer = pCoreServer
        self.__pDatabase = pDatabase
        self.__pLog = pLog

    # Fetch a sequence and components from the database
    def GetSequence(self, sRemoteUser, nSequenceID):
        # Fetch the sequence from the databse
        pSequence = {"type":"sequence"}
        pSequence.update(self.__pDatabase.GetSequence(sRemoteUser, nSequenceID))

        # Add details to each component
        for pComponent in pSequence["components"]:
            self.__AddComponentDetails(sRemoteUser, pComponent, nSequenceID)

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
        # Fetch the component from the databse
        pComponent = self.__pDatabase.GetComponent(sRemoteUser, nComponentID)

        # Add details to the component and return
        self.__AddComponentDetails(sRemoteUser, pComponent, nSequenceID)
        return pComponent

    # Adds a new component to the database
    def AddComponent(self, sRemoteUser, nSequenceID, nInsertionID, pComponent):
        # Strip the component down to the fields we want to save
        pDBComponent = self.__RemoveComponentDetails(pComponent)

        # Insert the new component
        return self.__pDatabase.InsertComponent(sRemoteUser, nSequenceID, pComponent["componenttype"], pComponent["name"], 
            json.dumps(pDBComponent), nInsertionID)

    # Updates an existing component
    def UpdateComponent(self, sRemoteUser, nSequenceID, nComponentID, nInsertionID, pComponent):
        # Update the component if one was provided
        if pComponent != None:
            self.__pLog("Updating existing component")
            # Pull the component from the database and update it with the fields we want to save
            pDBComponent = self.__pDatabase.GetComponent(sRemoteUser, nComponentID)
            self.__UpdateComponentDetails(pDBComponent, pComponent)

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
    def __AddComponentDetails(self, sRemoteUser, pComponent, nSequenceID):
        # Details we add depends on the component type
        if pComponent["componenttype"] == "CASSETTE":
            # Set static values
            pComponent.update({"reactordescription":"Reactor associated with this cassette"})
            pComponent.update({"reactorvalidation":"type=enum-literal; values=1,2,3; required=true"})

            # Look up each reagent
            pReagentIDs = pComponent["reagentids"]
            pReagents = []
            for nReagentID in pReagentIDs:
                pReagents.append(self.GetReagent(sRemoteUser, int(nReagentID)))
            del pComponent["reagentids"]
            pComponent["reagents"] = pReagents

            # Set the validation error
            pComponent.update({"validationerror":False})
        elif pComponent["componenttype"] == "ADD":
            # Set static values
            pComponent.update({"reactordescription":"Reactor where the reagent will be added"})
            pComponent.update({"reactorvalidation":"type=enum-literal; values=1,2,3; required=true"})
            pComponent.update({"reagentdescription":"Reagent to add to the reactor"})

            # Look up the reagent
            pReagent = {}
            sName = "Add"
            if pComponent["reagent"] != "":
                pReagents = self.__pDatabase.GetReagentsByName(sRemoteUser, nSequenceID, pComponent["reagent"])
                if len(pReagents) > 0:
                    pReagent = pReagents[0]
                    sName += " " + pReagent["name"]
            del pComponent["reagent"]
            pComponent["reagent"] = pReagent
            pComponent.update({"name":sName})

            # Set the available reagent IDs
            pComponent.update({"reagentvalidation":"type=enum-reagent; values=1,2,3,4,5,6,7,8; required=true"})

            # Set the validation error
            pComponent.update({"validationerror":False})
        elif pComponent["componenttype"] == "EVAPORATE":
            # Set static values
            pComponent.update({"name":"Evaporate"})
            pComponent.update({"reactordescription":"Reactor where the evaporation will be performed"})
            pComponent.update({"reactorvalidation":"type=enum-literal; values=1,2,3; required=true"})
            pComponent.update({"durationdescription":"Evaporation duration after the target temperature is reached"})
            pComponent.update({"durationvalidation":"type=time; min=00:00.00; max=02:00.00; required=true"})
            pComponent.update({"evaporationtemperaturedescription":"Reaction temperature in degrees Celsius"})
            pComponent.update({"evaporationtemperaturevalidation":"type=temperature; min=20; max=200; required=true"})
            pComponent.update({"finaltemperaturedescription":"Final temperature after evaporation in degrees Celsius"})
            pComponent.update({"finaltemperaturevalidation":"type=temperature; min=20; max=200; required=true"})
            pComponent.update({"stirspeeddescription":"Speed of the stir bar in rotations per minute"})
            pComponent.update({"stirespeedvalidation":"type=speed; min=0; max=5000; required=true"})

            # Set the validation error
            pComponent.update({"validationerror":False})
        elif pComponent["componenttype"] == "TRANSFER":
            pComponent.update({"name":"Transfer"})
            pComponent.update({"reactordescription":"Reactor where the source reagent resides"})
            pComponent.update({"reactorvalidation":"type=enum-literal; values=1,2,3; required=true"})
            pComponent.update({"targetdescription":"Target where the reactor contents will be transferred"})
            pComponent.update({"targetvalidation":"type=enum-target; values=A; required=true"})
            pComponent.update({"validationerror":False})
        elif pComponent["componenttype"] == "ELUTE":
            pComponent.update({"name":"Elute"})
            pComponent.update({"reactordescription":"Reactor where the reagent will be eluted"})
            pComponent.update({"reactorvalidation":"type=enum-literal; values=1,2,3; required=true"})
            pComponent.update({"reagentdescription":"Reagent used to elute the target"})
            pComponent.update({"reagentvalidation":"type=enum-reagent; values=1,2,3,4,5,6,7,8; required=true"})
            pComponent.update({"targetdescription":"Target to be eluted with the reagent"})
            pComponent.update({"targetvalidation":"type=enum-target; values=A; required=true"})
            pComponent.update({"validationerror":False})
        elif pComponent["componenttype"] == "REACT":
            # Set static values
            pComponent.update({"name":"React"})
            pComponent.update({"reactordescription":"Reactor where the reaction will be performed"})
            pComponent.update({"reactorvalidation":"type=enum-literal; values=1,2,3; required=true"})
            pComponent.update({"positiondescription":"Position where the reaction will take place"})
            pComponent.update({"positionvalidation":"type=enum-literal; values=1,2; required=true"})
            pComponent.update({"durationdescription":"Evaporation duration after the target temperature is reached"})
            pComponent.update({"durationvalidation":"type=time; min=00:00.00; max=02:00.00; required=true"})
            pComponent.update({"reactiontemperaturedescription":"Reaction temperature in degrees Celsius"})
            pComponent.update({"reactiontemperaturevalidation":"type=temperature; min=20; max=200; required=true"})
            pComponent.update({"finaltemperaturedescription":"Final temperature after evaporation in degrees Celsius"})
            pComponent.update({"finaltemperaturevalidation":"type=temperature; min=20; max=200; required=true"})
            pComponent.update({"stirspeeddescription":"Speed of the stir bar in rotations per minute"})
            pComponent.update({"stirespeedvalidation":"type=speed; min=0; max=5000; required=true"})

            # Set the validation error
            pComponent.update({"validationerror":False})
        elif pComponent["componenttype"] == "PROMPT":
            # Set static values
            pComponent.update({"name":"Prompt"})
            pComponent.update({"reactordescription":""})
            pComponent.update({"reactorvalidation":""})
            pComponent.update({"messagedescription":"This will be displayed to the user"})
            pComponent.update({"messagevalidation":"type=string; required=true"})

            # Set the validation error
            pComponent.update({"validationerror":False})
        elif pComponent["componenttype"] == "INSTALL":
            # Set static values
            pComponent.update({"name":"Install"})
            pComponent.update({"reactordescription":"Reactor that will be moved to the install position"})
            pComponent.update({"reactorvalidation":"type=enum-literal; values=1,2,3; required=true"})
            pComponent.update({"messagedescription":"This will be displayed to the user"})
            pComponent.update({"messagevalidation":"type=string; required=true"})

            # Set the validation error
            pComponent.update({"validationerror":False})
        elif pComponent["componenttype"] == "COMMENT":
            # Set static values
            pComponent.update({"name":"Comment"})
            pComponent.update({"reactordescription":""})
            pComponent.update({"reactorvalidation":""})
            pComponent.update({"commentdescription":"Enter a comment"})
            pComponent.update({"commentvalidation":"type=string"})

            # Set the validation error
            pComponent.update({"validationerror":False})
        elif pComponent["componenttype"] == "ACTIVITY":
            # Set static values
            pComponent.update({"name":"Activity"})
            pComponent.update({"reactordescription":"Reactor where the radioactivity will be measures"})
            pComponent.update({"reactorvalidation":"type=enum-literal; values=1,2,3; required=true"})

            # Set the validation error
            pComponent.update({"validationerror":False})

    # Update the database component with the relavent details that we have received from the client
    def __UpdateComponentDetails(self, pTargetComponent, pSourceComponent):
        # Update the parts of the component that we save
        if pTargetComponent["componenttype"] == "CASSETTE":
            pTargetComponent["available"] = pSourceComponent["available"]
        elif pTargetComponent["componenttype"] == "ADD":
            pTargetComponent["reactor"] = pSourceComponent["reactor"]
            pTargetComponent["reagent"] = pSourceComponent["reagent"]
        elif pTargetComponent["componenttype"] == "EVAPORATE":
            pTargetComponent["reactor"] = pSourceComponent["reactor"]
            pTargetComponent["duration"] = pSourceComponent["duration"]
            pTargetComponent["evaporationtemperature"] = pSourceComponent["evaporationtemperature"]
            pTargetComponent["finaltemperature"] = pSourceComponent["finaltemperature"]
            pTargetComponent["stirspeed"] = pSourceComponent["stirspeed"]
        elif pTargetComponent["componenttype"] == "TRANSFER":
            pTargetComponent["reactor"] = pSourceComponent["reactor"]
            pTargetComponent["target"] = pSourceComponent["target"]
        elif pTargetComponent["componenttype"] == "ELUTE":
            pTargetComponent["reactor"] = pSourceComponent["reactor"]
            pTargetComponent["reagent"] = pSourceComponent["reagent"]
            pTargetComponent["target"] = pSourceComponent["target"]
        elif pTargetComponent["componenttype"] == "REACT":
            pTargetComponent["reactor"] = pSourceComponent["reactor"]
            pTargetComponent["position"] = pSourceComponent["position"]
            pTargetComponent["duration"] = pSourceComponent["duration"]
            pTargetComponent["reactiontemperature"] = pSourceComponent["reactiontemperature"]
            pTargetComponent["finaltemperature"] = pSourceComponent["finaltemperature"]
            pTargetComponent["stirspeed"] = pSourceComponent["stirspeed"]
        elif pTargetComponent["componenttype"] == "PROMPT":
            pTargetComponent["message"] = pSourceComponent["message"]
        elif pTargetComponent["componenttype"] == "INSTALL":
            pTargetComponent["reactor"] = pSourceComponent["reactor"]
            pTargetComponent["message"] = pSourceComponent["message"]
        elif pTargetComponent["componenttype"] == "COMMENT":
            pTargetComponent["comment"] = pSourceComponent["comment"]
        elif pTargetComponent["componenttype"] == "ACTIVITY":
            pTargetComponent["reactor"] = pSourceComponent["reactor"]

    # Strips a component down to only the details we want to save in the database
    def __RemoveComponentDetails(self, pComponent):
        # Get a list of component-specific keys we want to save
        pDesiredKeys = None
        if pComponent["componenttype"] == "ADD":
            pDesiredKeys = ["type", "componenttype", "reactor", "reagent"]
        elif pComponent["componenttype"] == "EVAPORATE":
            pDesiredKeys = ["type", "componenttype", "reactor", "duration", "evaporationtemperature", "finaltemperature", "stirspeed"]
        elif pComponent["componenttype"] == "TRANSFER":
            pDesiredKeys = ["type", "componenttype", "reactor", "target"]
        elif pComponent["componenttype"] == "ELUTE":
            pDesiredKeys = ["type", "componenttype", "reactor", "reagent", "target"]
        elif pComponent["componenttype"] == "REACT":
            pDesiredKeys = ["type", "componenttype", "reactor", "position", "duration", "reactiontemperature", "finaltemperature", "stirspeed"]
        elif pComponent["componenttype"] == "PROMPT":
            pDesiredKeys = ["type", "componenttype", "reactor", "message"]
        elif pComponent["componenttype"] == "INSTALL":
            pDesiredKeys = ["type", "componenttype", "reactor", "message"]
        elif pComponent["componenttype"] == "COMMENT":
            pDesiredKeys = ["type", "componenttype", "reactor", "comment"]
        elif pComponent["componenttype"] == "ACTIVITY":
            pDesiredKeys = ["type", "componenttype", "reactor"]

        # Remove the keys that we do not want to save
        pReturn = pComponent.copy()
        if pDesiredKeys != None:
            pUnwantedKeys = set(pReturn) - set(pDesiredKeys)
            for pUnwantedKey in pUnwantedKeys:
                del pReturn[pUnwantedKey]
        return pReturn

