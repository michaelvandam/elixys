"""ExportDatabase

Exports the contents of the database to the specified directory
"""

import os
import json
import sys
sys.path.append("../database/")
sys.path.append("../core/")
from DBComm import DBComm
from SequenceManager import SequenceManager

if __name__ == '__main__':
    # Make sure we have a command line argument
    if len(sys.argv) != 2:
        print "Target direcory argument not found.  Usage:"
        print "  python ExportDatabase.py [targetdirectory]"
        print ""
        exit()

    # Create the database layer and sequence manager
    pDBComm = DBComm()
    pDBComm.Connect()
    pSequenceManager = SequenceManager(pDBComm)

    # Create the directory if it doesn't exist
    sTargetDirectory = sys.argv[1]
    if not os.path.isdir(sTargetDirectory):
        print "Target direcory \"" + sTargetDirectory + "\" not found, creating..."
        os.mkdir(sTargetDirectory)

    # Create the database object
    pDatabase = {}
    pDatabase["type"] = "database"
    pDatabase["roles"] = []
    pDatabase["users"] = []
    pDatabase["savedsequences"] = []
    pDatabase["runhistory"] = []

    # Add the user roles
    print "Exporting roles..."
    pRoles = pDBComm.GetAllRoles("System")
    for pRole in pRoles:
        pDatabase["roles"].append({"type":"role",
            "name":pRole["name"],
            "flags":pRole["flags"]})

    # Add the users
    print "Exporting users..."
    pUsers = pDBComm.GetAllUsers("System")
    for pUser in pUsers:
        pDatabase["users"].append({"type":"user",
            "username":pUser["username"],
            "firstname":pUser["firstname"],
            "lastname":pUser["lastname"],
            "passwordhash":"secret",
            "role":pUser["accesslevel"]})

    # Add the saved sequences
    print "Exporting saved sequences..."
    pSequences = pDBComm.GetAllSequences("System", "Saved")
    nCount = 1
    for pSequence in pSequences:
        # Format the filename
        sFilenameShort = "SavedSequence" + str(nCount) + ".seq"
        sFilenameLong = os.path.join(sTargetDirectory, sFilenameShort)
        pDatabase["savedsequences"].append({"type":"sequence",
            "filename":sFilenameShort})
        nCount += 1

        # Export the sequence
        pSequenceManager.ExportSequence("System", pSequence["id"], sFilenameLong)

    # Add the run history
    print "Exporting run history..."
    pSequences = pDBComm.GetAllSequences("System", "History")
    nCount = 1
    for pSequence in pSequences:
        # Format the filename
        sFilenameShort = "RunHistory" + str(nCount) + ".seq"
        sFilenameLong = os.path.join(sTargetDirectory, sFilenameShort)
        pDatabase["runhistory"].append({"type":"sequence",
            "filename":sFilenameShort})
        nCount += 1

        # Export the sequence
        pSequenceManager.ExportSequence("System", pSequence["id"], sFilenameLong)

    # Save the database file
    sDatabaseFile = os.path.join(sTargetDirectory, "Database.dat")
    pDatabaseFile = open(sDatabaseFile, "w")
    sDatabaseJSON = json.dumps(pDatabase)
    pDatabaseFile.write(sDatabaseJSON)

    # Complete
    pDBComm.Disconnect()
    print "Done"

