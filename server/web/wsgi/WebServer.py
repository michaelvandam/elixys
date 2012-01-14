#!/usr/bin/python

# Change the python egg cache directory to a place where Apache has write permission
import os
os.environ["PYTHON_EGG_CACHE"] = "/var/www/eggs"

# Imports
from wsgiref.simple_server import make_server
import json
from wsgiref.headers import Headers
import time
import sys
sys.path.append("/opt/elixys/core")
sys.path.append("/opt/elixys/database")
sys.path.append("/var/www/wsgi")
import GetHandler
import PostHandler
import DeleteHandler
import ExceptionHandler
import CoreServerProxy
import Exceptions

# Import and create the database connection
from DBComm import *
gDatabase = DBComm()

# Create a proxy connection to the core server
gCoreServer = CoreServerProxy.CoreServerProxy()

def application(pEnvironment, fStartResponse):
    # Connect to the database.  It is important that we do this at the start of every request or two things happen:
    #  1. We start receiving stale data from MySQLdb depending on which thread handles this request
    #  2. MySQL will run out of available database connections under heavy loads
    global gCoreServer
    global gDatabase
    nStart = time.time()
    gDatabase.Connect()

    # Extract input variables
    sRemoteUser = pEnvironment["REMOTE_USER"]
    sRequestMethod = pEnvironment["REQUEST_METHOD"]
    sPath = pEnvironment["PATH_INFO"]

    # Load the client state and log the request
    pClientState = gDatabase.GetUserClientState(sRemoteUser, sRemoteUser)
    gDatabase.SystemLog(LOG_INFO, sRemoteUser, "Web server received " + sRequestMethod + " request for " + sPath)
    gDatabase.SystemLog(LOG_DEBUG, sRemoteUser, "Client state = " + str(pClientState))

    # Handle the request
    try:
        # Create the appropriate handler
        pBody = None
        nBodyLength = 0
        if sRequestMethod == "GET":
            pHandler = GetHandler.GetHandler(gCoreServer, gDatabase)
        elif sRequestMethod == "POST":
            nBodyLength = int(pEnvironment["CONTENT_LENGTH"])
            pBody = pEnvironment["wsgi.input"].read(nBodyLength)
            pHandler = PostHandler.PostHandler(gCoreServer, gDatabase)
        elif sRequestMethod == "DELETE":
            pHandler = DeleteHandler.DeleteHandler(gCoreServer, gDatabase)
        else:
            raise Exception("Unknown request method: " + sRequestMethod)

        # Handle the request
        sResponse = pHandler.HandleRequest(pClientState, sRemoteUser, sPath, pBody, nBodyLength)
    except Exceptions.SequenceNotFoundException as ex:
        sResponse = ExceptionHandler.HandleSequenceNotFound(gCoreServer, gDatabase, pClientState, sRemoteUser, sPath, ex.nSequenceID)
    except Exceptions.ComponentNotFoundException as ex:
        sResponse = ExceptionHandler.HandleComponentNotFound(gCoreServer, gDatabase, pClientState, sRemoteUser, sPath, ex.nComponentID)
    except Exceptions.ReagentNotFoundException as ex:
        sResponse = ExceptionHandler.HandleReagentNotFound(gCoreServer, gDatabase, pClientState, sRemoteUser, sPath, ex.nReagentID, )
    except Exception as ex:
        # Log the actual error and send the client a generic error
        gDatabase.SystemLog(LOG_ERROR, sRemoteUser, str(ex))
        sResponse = {"type":"error","description":"An internal server error occurred"}

    # Initialize the return status and headers
    sStatus = "200 OK"
    sResponseJSON = json.dumps(sResponse)
    pHeaders = [("Content-type", "text/plain"), ("Content-length", str(len(sResponseJSON)))]

    # Log the timestamp
    nElapsed = time.time() - nStart
    gDatabase.SystemLog(LOG_DEBUG, sRemoteUser, sRequestMethod + " " + sPath + " took " + str(nElapsed) + " seconds, returned " + str(len(sResponseJSON)) + " bytes")
    gDatabase.Disconnect()

    # Send the response
    fStartResponse(sStatus, pHeaders)
    return [sResponseJSON]

