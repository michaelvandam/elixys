"""LoadDemoData

Load the demo data into the Elixys database
"""

import sys
sys.path.append("/opt/elixys/database/")
from DBComm import DBComm
import json

def GetReagentsByName(pReagents, sReagentName):
    """Returns all reagents that match the given name"""
    pReturn = []
    for pReagent in pReagents:
        # Add reagents that match the target name
        if pReagent["name"] == sReagentName:
            pReturn.append(pReagent)
    return pReturn

def ImportSequence(sFilename, pDBComm):
    # Open the file and read the contents
    pSequenceFile = open(sFilename)
    sSequence = pSequenceFile.read()
    pSequence = json.loads(sSequence)

    # Create the sequence
    if (pSequence["type"] == "sequence") and (pSequence["name"] != "") and (pSequence["reactors"] != 0) and (pSequence["reagentsperreactor"] != 0) and (pSequence["columnsperreactor"] != 0):
        nSequenceID = pDBComm.CreateSequence("System", pSequence["name"], pSequence["reactors"], pSequence["reactors"], pSequence["reagentsperreactor"], pSequence["columnsperreactor"])
    else:
        raise Exception("Invalid sequence parameters")

    # Add the reagents
    for pReagent in pSequence["reagents"]:
        if (pReagent["type"] == "reagent") and (pReagent["cassette"] != 0) and (pReagent["position"] != "") and (pReagent["name"] != ""):
            pDBComm.UpdateReagentByPosition("System", nSequenceID, pReagent["cassette"], pReagent["position"], True, pReagent["name"], pReagent["description"])
        else:
            raise Exception("Invalid reagent parameters in \"" + str(pReagent) + "\"")

    # Process each component
    for pComponent in pSequence["components"]:
        if (pComponent["type"] != ""):
            # Convert any reagent entries to IDs
            if pComponent.has_key("reagent"):
                # Remove the reagent from our local list
                pLocalReagents = GetReagentsByName(pSequence["reagents"], pComponent["reagent"])
                if len(pLocalReagents) == 0:
                    raise Exception("Missing reagent " + pComponent["reagent"])
                pSequence["reagents"].remove(pLocalReagents[0])

                # Get a list of reagents from the database
                pDatabaseReagents = pDBComm.GetReagentsByName("System", nSequenceID, pComponent["reagent"])
                if len(pDatabaseReagents) == 0:
                    raise Exception("Database missing reagent " + pComponent["reagent"])

                # Look up the desired reagent and update the component
                pComponent["reagent"] = pDatabaseReagents[len(pDatabaseReagents) - len(pLocalReagents)][0]

            # Convert any targets to IDs
            if pComponent.has_key("target"):
                # Get a list of reagents from the database
                pDatabaseReagents = pDBComm.GetReagentsByName("System", nSequenceID, pComponent["target"])
                if len(pDatabaseReagents) == 0:
                    # Check again to see if this is a reserved reagent
                    pDatabaseReagents = pDBComm.GetReservedReagentsByName("System", pComponent["target"])
                    if len(pDatabaseReagents) == 0:
                        # OK, now it's a problem
                        raise Exception("Database missing target " + pComponent["target"])

                    # Update the component
                    pComponent["target"] = pDatabaseReagents[0][0]
                else:
                    # Targets always go with the current reactor
                    for pReagent in pDatabaseReagents:
                        if pReagent[2] == pComponent["reactor"]:
                            # Update the component
                            pComponent["target"] = pReagent[0]

            # Add the component
            pDBComm.AddComponent("System", nSequenceID, pComponent["type"], "", json.dumps(pComponent))
        else:
            raise Exception("Invalid reagent parameters in \"" + str(pReagent) + "\"")

if __name__ == '__main__':
    # Create the database layer
    pDBComm = DBComm()

    # Create the user roles
    print "Creating user roles"
    pDBComm.CreateRole("System", "Administrator", 255);
    pDBComm.CreateRole("System", "Researcher", 255);
    pDBComm.CreateRole("System", "Technician", 255);

    # Create the users
    print "Creating users"
    pDBComm.CreateUser("System", "System", "", "", "", "Administrator");
    pDBComm.CreateUser("System", "Administrator", "6E3kYsJnM9p2Y", "first", "last", "Administrator");
    pDBComm.CreateUser("System", "Researcher", "6E3kYsJnM9p2Y", "first", "last", "Researcher");
    pDBComm.CreateUser("System", "Technician", "6E3kYsJnM9p2Y", "first", "last", "Technician");
    pDBComm.CreateUser("System", "devel", "6E3kYsJnM9p2Y", "first", "last", "Administrator");
    pDBComm.CreateUser("System", "shane", "6E3kYsJnM9p2Y", "Shane", "Claggett", "Administrator");
    pDBComm.CreateUser("System", "kevin", "6E3kYsJnM9p2Y", "Kevin", "Quinn", "Administrator");
    pDBComm.CreateUser("System", "mike", "6E3kYsJnM9p2Y", "Mike", "van Dam", "Administrator");
    pDBComm.CreateUser("System", "melissa", "6E3kYsJnM9p2Y", "Melissa", "Esterby", "Administrator");
    pDBComm.CreateUser("System", "jeff", "6E3kYsJnM9p2Y", "Jeff", "Esterby", "Administrator");
    pDBComm.CreateUser("System", "mark", "6E3kYsJnM9p2Y", "Mark", "Lazari", "Researcher");
    pDBComm.CreateUser("System", "garauv", "6E3kYsJnM9p2Y", "Gaurav", "Shah", "Researcher");
    pDBComm.CreateUser("System", "graciela", "6E3kYsJnM9p2Y", "Graciela", "Flores", "Researcher");
    pDBComm.CreateUser("System", "patrick", "6E3kYsJnM9p2Y", "Patrick", "Phelps", "Researcher");

    # Create reserved reagents
    pDBComm.CreateReservedReagent("System", "HPLC", "External HPLC instrument");

    # Import the FAC synthesis sequence
    ImportSequence("FACSynthesis.seq", pDBComm);

    # Complete
    print "Done"

