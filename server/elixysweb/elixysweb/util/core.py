import os
import sys
abspath = os.path.sep.join(os.path.abspath(__file__).split(os.path.sep)[0:-4])
print "Path:%s" % abspath
sys.path.append(os.path.join(abspath,"core"))
sys.path.append(os.path.join(abspath,"database"))
sys.path.append(os.path.join(os.path.join(abspath,"web"),"wsgi"))

import logging
log = logging.getLogger("elixys.web")
log.debug("Path:%s" % os.path.abspath(__file__))
print "Path:%s" % os.path.abspath(__file__)

import CoreServerProxy
from CoreServer import InitialRunState
import DBComm
import SequenceManager

def coreServerFactory():
    coreServer = CoreServerProxy.CoreServerProxy()
    coreServer.Connect()
    return coreServer

def databaseFactory():
    db = DBComm.DBComm()
    db.Connect()
    return db

def getCurrentSystemState(username):
    core = coreServerFactory()
    state = core.GetServerState(username)
    if state is None:
        log.debug("Failed to get CoreServer state, hardware available?")
        state = {"type":"serverstate",
                "timestamp":time.time(),
                "runstate":InitialRunState(),
                }
        state['runstate']['status'] = "Offline"
        state['runstate']['username'] = ""
    return state
    
def getCurrentClientState(username):
    db = DBComm.DBComm()
    db.Connect()
    client = db.GetUserClientState(username,username)
    return client

def getSequenceManager(db):
    return SequenceManager.SequenceManager(db)
