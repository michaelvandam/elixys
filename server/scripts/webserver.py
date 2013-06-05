#!/usr/bin/python
# Elixys Web server

import os
import time
import sys
from functools import wraps
import flask
from flask import Flask
from flask import request, Response
import logging

log = logging.getLogger('Elixys Web server')
log.setLevel(logging.DEBUG)
fh = logging.FileHandler('elixysweb.log')
fh.setLevel(logging.DEBUG)
sh = logging.StreamHandler()
sh.setLevel(logging.DEBUG)
fmt = logging.Formatter('%(asctime)s-%(name)s-%(levelname)s-%(message)s')
fh.setFormatter(fmt)
sh.setFormatter(fmt)
log.addHandler(fh)
log.addHandler(sh)

sys.path.append("core")
sys.path.append("database")
sys.path.append("web/wsgi")

import CoreServerProxy
from CoreServer import InitialRunState
import DBComm



app = Flask("ElixysWebServer")

def check_auth(username, password):
    """
    Function checks is username and password is valid
    """
    return username == 'devel' and password == 'devel'

def authenticate():
    """
    Sends a 401 response that enables basic auth
    """
    log.info("Authenticate")
    return Response(
            'Could not verify your access level for elixys\n'
            'You must have proper credentials', 401,
            {'WWW-Authenticate':'Basic realm="Login Required"'})

def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            log.debug("Requires auth")
            return authenticate()
        log.debug("username:%s" % auth.username)
        return f(*args, **kwargs)
    return decorated


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

@app.route('/')
def index():
    pass

@app.route('/config', methods=['GET'])
@app.route('/configuration', methods=['GET'])
@app.route('/Elixys/configuration', methods=['GET'])
@requires_auth
def config():
    auth = request.authorization
    log.debug("Configuration requested by username:%s" % auth.username)
    config = {"type":"configuration"}
    db = databaseFactory()
    config.update(db.GetConfiguration(auth.username))
    config.update({"supportedoperations":db.GetSupportedOperations(auth.username)})
    return flask.jsonify(config)
    
@app.route('/state', methods=['GET'])
@app.route('/Elixys/state', methods=['GET'])
@requires_auth
def state():
    auth = request.authorization
    log.debug("State requested by username:%s" % auth.username)
    db = databaseFactory()
    user = db.GetUser(auth.username,auth.username)
    system = getCurrentSystemState(auth.username) 
    client = getCurrentClientState(auth.username)
    systemRunning = (system['runstate']['username']!="") 
    state = {"type":"state",
            "user":auth.username,
            "serverstate":system,
            "clientstate":client,
            "timestamp":time.time()}

    def home():
        log.debug("State: Home screen")
        homeState = {"buttons":[
                    {"type":"button","id":"SEQUENCER","enable":True},
                    {"type":"button","id":"MYACCOUNT","enable":False},
                    {"type":"button","id":"MANAGEUSERS","enable":False},
                    {"type":"button","id":"VIEWLOGS","enable":False},
                    {"type":"button","id":"VIEWRUN","enable":systemRunning},
                    {"type":"button","id":"LOGOUT","enable":True}]}
        state.update(homeState)                        


    def savedSeq():
        log.debug("State: Saved sequence screen")

    def runHist():
        log.debug("State: Run history screen")

    def view():
        log.debug("State: View screen")

    def edit():
        log.debug("State: Edit screen")

    def run():
        log.debug("State: Run screen")

    def default():
        log.debug("State: Default screen")

    options = {"HOME":home,
                "SELECT_SAVEDSEQUENCES":savedSeq,
                "SELECT_RUNHIST":runHist,
                "VIEW":view,
                "EDIT":edit,
                "RUN":run}

    choice = client["screen"]
    options.get(choice, default)()
    return flask.jsonify(state)

@app.route('/runstate', methods=['GET'])
@app.route('/Elixys/runstate', methods=['GET'])
@requires_auth
def runstate():

    return "run state"

@app.route('/sequence/<int:seqid>')
@app.route('/Elixys/sequence/<int:seqid>')
def sequences(seqid):
    return "sequence"

@app.route('/reagent/<int:reagentid>')
@app.route('/Elixys/reagent/<int:reagentid>')
def reagents(reagentid):
    return "reagents"


if __name__ == '__main__':
    log.info("Starting Elixys Web Server")
    app.run(debug=True,host='0.0.0.0')
