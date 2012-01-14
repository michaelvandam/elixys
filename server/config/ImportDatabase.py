"""ImportDatabase

Imports the contents of the specified database directory
"""

import os
import json
import sys
sys.path.append("/opt/elixys/database/")
sys.path.append("/opt/elixys/core/")
from DBComm import DBComm
from SequenceManager import SequenceManager

if __name__ == '__main__':
    # Make sure we have a command line argument
    if len(sys.argv) != 2:
        print "Target direcory argument not found.  Usage:"
        print "  python ImportDatabase.py [targetdirectory]"
        print ""
        exit()

    # Make sure the directory exists
    sTargetDirectory = sys.argv[1]
    if not os.path.isdir(sTargetDirectory):
        print "Target direcory \"" + sTargetDirectory + "\" not found."
        print ""
        exit()

    # Make sure the database file exists
    sDatabaseFile = os.path.join(sTargetDirectory, "Database.dat")
    if not os.path.isfile(sDatabaseFile):
        print "Database file \"" + sDatabaseFile + "\" not found."
        print ""
        exit()

    # Open and parse the database file
    pDatabaseFile = open(sDatabaseFile)
    sDatabaseJSON = pDatabaseFile.read()
    pDatabase = json.loads(sDatabaseJSON)

    # Create the database layer and sequence manager
    pDBComm = DBComm()
    pDBComm.Connect()
    pSequenceManager = SequenceManager(pDBComm)

    # Create the user roles
    print "Creating roles..."
    for pRole in pDatabase["roles"]:
        print "  " + pRole["name"]
        pDBComm.CreateRole("System", pRole["name"], pRole["flags"])

    # Create the users
    print "Creating users..."
    for pUser in pDatabase["users"]:
        print "  " + pUser["username"]
        pDBComm.CreateUser("System", pUser["username"], pUser["passwordhash"], pUser["firstname"], pUser["lastname"], pUser["role"])

    # Import the saved sequences
    print "Importing saved sequences..."
    for pSequence in pDatabase["savedsequences"]:
        # Make sure the sequence file exists
        sSequenceFile = os.path.join(sTargetDirectory, pSequence["filename"])
        if not os.path.isfile(sSequenceFile):
            print "Warning: sequence file \"" + sSequenceFile + "\" not found, skipping."
            continue
        print "  " + sSequenceFile
        pSequenceManager.ImportSequence("System", sSequenceFile, "Saved")

    # Import the run history
    print "Importing run history..."
    for pSequence in pDatabase["runhistory"]:
        # Make sure the sequence file exists
        sSequenceFile = os.path.join(sTargetDirectory, pSequence["filename"])
        if not os.path.isfile(sSequenceFile):
            print "Warning: sequence file \"" + sSequenceFile + "\" not found, skipping."
            continue
        print "  " + sSequenceFile
        pSequenceManager.ImportSequence("System", sSequenceFile, "History")

    # Complete
    pDBComm.Disconnect()
    print "Done"

