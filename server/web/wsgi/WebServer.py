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
from DBComm import *

# Create a RPC connection to the core server
gCoreServer = CoreServerProxy.CoreServerProxy()

def application(pEnvironment, fStartResponse):
    # Handle the request
    global gCoreServer
    pDatabase = None
    try:
        # Take a starting timestamp
        nStart = time.time()

        # Extract input variables
        sRemoteUser = pEnvironment["REMOTE_USER"]
        sRequestMethod = pEnvironment["REQUEST_METHOD"]
        sPath = pEnvironment["PATH_INFO"]

        # Create a new database connection each time we receive a request or two things happen:
        #  1. We start receiving stale data from MySQLdb depending on which thread handles which request
        #  2. MySQL will run out of available database connections under heavy loads
        pDatabase = DBComm()
        pDatabase.Connect()

        # Load the client state and log the request
        pClientState = pDatabase.GetUserClientState(sRemoteUser, sRemoteUser)
        pDatabase.SystemLog(LOG_INFO, sRemoteUser, "Web server received " + sRequestMethod + " request for " + sPath)
        pDatabase.SystemLog(LOG_DEBUG, sRemoteUser, "Client state = " + str(pClientState))

        # Create the appropriate handler
        pBody = None
        nBodyLength = 0
        if sRequestMethod == "GET":
            pHandler = GetHandler.GetHandler(gCoreServer, pDatabase)
        elif sRequestMethod == "POST":
            nBodyLength = int(pEnvironment["CONTENT_LENGTH"])
            pBody = pEnvironment["wsgi.input"].read(nBodyLength)
            pHandler = PostHandler.PostHandler(gCoreServer, pDatabase)
        elif sRequestMethod == "DELETE":
            pHandler = DeleteHandler.DeleteHandler(gCoreServer, pDatabase)
        else:
            raise Exception("Unknown request method: " + sRequestMethod)

        # Handle the request
        pResponse = pHandler.HandleRequest(pClientState, sRemoteUser, sPath, pBody, nBodyLength)
    except Exceptions.SequenceNotFoundException as ex:
        pResponse = ExceptionHandler.HandleSequenceNotFound(gCoreServer, pDatabase, pClientState, sRemoteUser, sPath, ex.nSequenceID)
    except Exceptions.ComponentNotFoundException as ex:
        pResponse = ExceptionHandler.HandleComponentNotFound(gCoreServer, pDatabase, pClientState, sRemoteUser, sPath, ex.nComponentID)
    except Exceptions.ReagentNotFoundException as ex:
        pResponse = ExceptionHandler.HandleReagentNotFound(gCoreServer, pDatabase, pClientState, sRemoteUser, sPath, ex.nReagentID)
    except Exceptions.InvalidSequenceException as ex:
        pResponse = ExceptionHandler.HandleInvalidSequence(pDatabase, sRemoteUser, ex.nSequenceID)
    except Exceptions.StateMisalignmentException as ex:
        pResponse = ExceptionHandler.HandleStateMisalignment(pDatabase, sRemoteUser)
    except Exception as ex:
        pResponse = ExceptionHandler.HandleGeneralException(pDatabase, sRemoteUser, str(ex))

    # Initialize the return status and headers
    sStatus = "200 OK"
    sResponseJSON = json.dumps(pResponse)
    pHeaders = [("Content-type", "text/plain"), ("Content-length", str(len(sResponseJSON)))]

    # Log the timestamp
    if pDatabase != None:
        nElapsed = time.time() - nStart
        pDatabase.SystemLog(LOG_INFO, sRemoteUser, sRequestMethod + " " + sPath + " took " + str(nElapsed) + " seconds, returned " + str(len(sResponseJSON)) + " bytes")
        pDatabase.Disconnect()

    # Send the response
    fStartResponse(sStatus, pHeaders)
    return [sResponseJSON]

