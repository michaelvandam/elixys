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
import traceback
import logging.config
import logging

logging.config.fileConfig("/opt/elixys/config/elixyslog.conf")
log = logging.getLogger("elixys.web")
seqlog = logging.getLogger("elixys.seq")


log.info("Starting Elixys Web Server")

def application(pEnvironment, fStartResponse):
    # Handle the request
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

        # Likewise, create a new RPC connection to the core server or we will start having thread-specific
        # issues if the hardware is turned on and off
        pCoreServer = CoreServerProxy.CoreServerProxy()
        pCoreServer.Connect()

        # Load the client state and log the request
        pClientState = pDatabase.GetUserClientState(sRemoteUser, sRemoteUser)

        log.debug("Web server received " + sRequestMethod + 
                " request for " + sPath)
        log.debug("Client state = " + str(pClientState))

        # Create the appropriate handler
        pBody = None
        nBodyLength = 0
        if sRequestMethod == "GET":
            pHandler = GetHandler.GetHandler(pCoreServer, pDatabase)
        elif sRequestMethod == "POST":
            nBodyLength = int(pEnvironment["CONTENT_LENGTH"])
            pBody = pEnvironment["wsgi.input"].read(nBodyLength)
            pHandler = PostHandler.PostHandler(pCoreServer, pDatabase)
        elif sRequestMethod == "DELETE":
            pHandler = DeleteHandler.DeleteHandler(pCoreServer, pDatabase)
        else:
            raise Exception("Unknown request method: " + sRequestMethod)

        try:
            # Handle the request
            pResponse = pHandler.HandleRequest(pClientState, sRemoteUser, sPath, pBody, nBodyLength)
        except Exceptions.StateMisalignmentException as ex:
            # The client state is misaligned, send the correct state as our response
            pGetHandler = GetHandler.GetHandler(pCoreServer, pDatabase)
            pResponse = pGetHandler.HandleRequest(pClientState, sRemoteUser, "/state", None, 0)
    except Exceptions.SequenceNotFoundException as ex:
        seqlog.error("Sequence Error Traceback:\n\r%s\n\r" % traceback.format_exc()) 
        pResponse = ExceptionHandler.HandleSequenceNotFound(pCoreServer, pDatabase, pClientState, sRemoteUser, sPath, ex.nSequenceID)
    except Exceptions.ComponentNotFoundException as ex:
        seqlog.error("Component Error Traceback:\n\r%s\n\r" % traceback.format_exc()) 
        pResponse = ExceptionHandler.HandleComponentNotFound(pCoreServer, pDatabase, pClientState, sRemoteUser, sPath, ex.nComponentID)
    except Exceptions.ReagentNotFoundException as ex:
        seqlog.error("Reagent Error Traceback:\n\r%s\n\r" % traceback.format_exc()) 
        pResponse = ExceptionHandler.HandleReagentNotFound(pCoreServer, pDatabase, pClientState, sRemoteUser, sPath, ex.nReagentID)
    except Exceptions.InvalidSequenceException as ex:
        seqlog.error("Invalid Sequence Error Traceback:\n\r%s\n\r" % traceback.format_exc()) 
        pResponse = ExceptionHandler.HandleInvalidSequence(pDatabase, sRemoteUser, ex.nSequenceID)
    except Exception as ex:
        seqlog.error("Unknown Error Traceback:%s" % traceback.format_exc()) 
        pResponse = ExceptionHandler.HandleGeneralException(pDatabase, sRemoteUser, str(ex))

    # Initialize the return status and headers
    sStatus = "200 OK"
    sResponseJSON = json.dumps(pResponse)
    pHeaders = [("Content-type", "text/plain"), ("Content-length", str(len(sResponseJSON)))]

    # Log the timestamp
    if pDatabase != None:
        nElapsed = time.time() - nStart
        log.info(sRequestMethod + " " + sPath + " took " + str(nElapsed) + 
                " seconds, returned " + str(len(sResponseJSON)) + " bytes")
        if nElapsed > 0.15:
            log.info("##  Long request processing time ##")
        pDatabase.Disconnect()

    # Send the response
    fStartResponse(sStatus, pHeaders)
    return [sResponseJSON]

