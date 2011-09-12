#!/usr/bin/python

# Imports
from wsgiref.simple_server import make_server
import json
from wsgiref.headers import Headers
import sys
sys.path.append("/opt/elixys/core")
sys.path.append("/opt/elixys/database")
sys.path.append("/var/www/wsgi")
import GetHandler
import PostHandler

# Change the python egg cache directory to a place where Apache has write permission
import os
os.environ["PYTHON_EGG_CACHE"] = "/var/www/wsgi"

# Import and create the database connection
import DBComm
gDatabase = DBComm.DBComm()

# Import and create the core Elixys server
from DummyElixys import Elixys 
gElixys = Elixys()
gElixys.SetDatabase(gDatabase)

# Log to Apache's error log file
def Log(sMessage):
    # Log to Apache's error log file
    print >> sys.stderr, sMessage

def application(pEnvironment, fStartResponse):
    # Connnect to the database.  It is important that we do this at the start of every request or two things happen:
    #  1. We start receiving stale data from MySQLdb depending on which thread handles this request
    #  2. MySQL will run out of available database connections under heavy loads
    global gElixys
    global gDatabase
    gDatabase.Connect()

    # Extract input variables
    sRemoteUser = pEnvironment["REMOTE_USER"]
    sRequestMethod = pEnvironment["REQUEST_METHOD"]
    sPath = pEnvironment["PATH_INFO"]

    # Load the client and system state
    sClientState = gDatabase.GetUserClientState(sRemoteUser, sRemoteUser)
    sSystemState = gElixys.GetSystemState(sRemoteUser)

    # Log the request
    Log("Received " + sRequestMethod + " request for " + sPath + " (client = " + sRemoteUser + ", client state = " + sClientState + ", system state = " + sSystemState + ")");

    # Handle the request
    try:
        # Create the appropriate handler
        pBody = None
        nBodyLength = 0
        if sRequestMethod == "GET":
            pHandler = GetHandler.GetHandler(gElixys, gDatabase, Log)
        elif sRequestMethod == "POST":
            nBodyLength = int(pEnvironment["CONTENT_LENGTH"])
            pBody = pEnvironment["wsgi.input"].read(nBodyLength)
            pHandler = PostHandler.PostHandler(gElixys, gDatabase, Log)
        elif sRequestMethod == "DELETE":
            pHandler = DeleteHandler.DeleteHandler(gElixys, gDatabase, Log)
        else:
            raise Exception("Unknown request method: " + sRequestMethod)

        # Handle the request
        sResponse = pHandler.HandleRequest(sClientState, sRemoteUser, sPath, pBody, nBodyLength)
    except Exception as ex:
        # Send an error message back to the client
        sResponse = {"type":"error","description":str(ex)}

    # Initialize the return status and headers
    sStatus = "200 OK"
    sResponseJSON = json.dumps(sResponse)
    pHeaders = [("Content-type", "text/plain"), ("Content-length", str(len(sResponseJSON)))]

    # Close the database connection
    gDatabase.Disconnect()

    # Send the response
    fStartResponse(sStatus, pHeaders)
    return [sResponseJSON]

