"""LoadDemoData

Load the demo data into the Elixys database
"""

import sys
sys.path.append("../database/")
sys.path.append("../core/")
from DBComm import DBComm
from SequenceManager import SequenceManager
from SystemModel import SystemModel

if __name__ == '__main__':
    # Create the database layer and sequence manager
    pDBComm = DBComm()
    pDBComm.Connect()
    pSequenceManager = SequenceManager(pDBComm)

    # Create the user roles
    print "Creating user roles"
    pDBComm.CreateRole("System", "Administrator", 255)
    pDBComm.CreateRole("System", "Researcher", 255)
    pDBComm.CreateRole("System", "Technician", 255)

    # Create the users
    print "Creating users"
    pDBComm.CreateUser("System", "System", "", "", "", "Administrator")
    pDBComm.CreateUser("System", "Administrator", "6E3kYsJnM9p2Y", "first", "last", "Administrator")
    pDBComm.CreateUser("System", "Researcher", "6E3kYsJnM9p2Y", "first", "last", "Researcher")
    pDBComm.CreateUser("System", "Technician", "6E3kYsJnM9p2Y", "first", "last", "Technician")
    pDBComm.CreateUser("System", "devel", "6E3kYsJnM9p2Y", "first", "last", "Administrator")
    pDBComm.CreateUser("System", "shane", "6E3kYsJnM9p2Y", "Shane", "Claggett", "Administrator")
    pDBComm.CreateUser("System", "kevin", "6E3kYsJnM9p2Y", "Kevin", "Quinn", "Administrator")
    pDBComm.CreateUser("System", "mike", "6E3kYsJnM9p2Y", "Mike", "van Dam", "Administrator")
    pDBComm.CreateUser("System", "melissa", "6E3kYsJnM9p2Y", "Melissa", "Esterby", "Administrator")
    pDBComm.CreateUser("System", "jeff", "6E3kYsJnM9p2Y", "Jeff", "Esterby", "Administrator")
    pDBComm.CreateUser("System", "mark", "6E3kYsJnM9p2Y", "Mark", "Lazari", "Researcher")
    pDBComm.CreateUser("System", "garauv", "6E3kYsJnM9p2Y", "Gaurav", "Shah", "Researcher")
    pDBComm.CreateUser("System", "graciela", "6E3kYsJnM9p2Y", "Graciela", "Flores", "Researcher")
    pDBComm.CreateUser("System", "patrick", "6E3kYsJnM9p2Y", "Patrick", "Phelps", "Researcher")

    # Import the FAC synthesis sequence
    pSequenceManager.ImportSequence("System", "FACSynthesis.seq")

    # Complete
    pDBComm.Disconnect()
    print "Done"

