"""ImportDatabase

Imports the contents of the specified database directory
"""

import os
import json
import sys
sys.path.append("../database/")
sys.path.append("../core/")
from DBComm import DBComm
from SequenceManager import SequenceManager

# Create the database layer and sequence manager
pDBComm = DBComm()
pDBComm.Connect()

if __name__ == '__main__':
    pDBComm.CreateUser("System", "Harvard",
                "ZH0FoaR3LmTDk", 
                "Harvard University", 
                "",
                "Administrator",
                "developer@sofiebio.com", 
                "", 
                0)

    print "Done"

