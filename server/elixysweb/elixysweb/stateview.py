#!/usr/bin/python
# Elixys Web server

import os
import time
import sys
import copy
from functools import wraps
import flask
from flask import Flask
from flask import request, Response
import logging
from util.basicauth import *
from util.core import coreServerFactory, \
                    databaseFactory, \
                    getCurrentClientState, \
                    getCurrentSystemState, \
                    getSequenceManager

from elixysweb import app



log = logging.getLogger('elixys.web')

def home(db, username, system, client):
    state = {"type":"state",
            "user":username,
            "serverstate":system,
            "clientstate":client,
            "timestamp":time.time()}
    log.debug("State: Home screen")
    homeState = {"buttons":[
                {"type":"button","id":"SEQUENCER","enable":True},
                {"type":"button","id":"MYACCOUNT","enable":False},
                {"type":"button","id":"MANAGEUSERS","enable":False},
                {"type":"button","id":"VIEWLOGS","enable":False},
                {"type":"button","id":"VIEWRUN","enable":systemRunning},
                {"type":"button","id":"LOGOUT","enable":True}]}
    state.update(homeState)                        
    return state


def savedSeq(db, username, system, client):
    log.debug("State: Saved sequence screen")

def runHist(db, username, system, client):
    log.debug("State: Run history screen")

def view(db, username, system, client):
    log.debug("State: View screen")
    state = {"type":"state",
            "user":username,
            "serverstate":system,
            "clientstate":client,
            "timestamp":time.time()}   
    seqMan = getSequenceManager(db)
    
    if client["componentid"] == 0:
        # Component ID is missing. Get Sequence ID of first component
        seq = seqMan.GetSequence(username, client["sequenceid"], False)
        client['componentid'] = seq['components'][0]["id"]
        db.UpdateUserClientState(username, username, client)
    
    seqmeta = db.GetSequenceMetadata(username, client["sequenceid"])
    editAllowed = (seqmeta['sequencetype'] == "Saved")
    runAllowed = (system['runstate']['status'] == "Idle")
    
    runAllowedHere = False
    if runAllowed:
        comp = seqMan.GetComponent(username, client["componentid"],
                                    client['sequenceid'])
        runAllowedHere = (comp["componenttype"] != "CASSETTE")

    viewState = {"buttons":[
                {"type":"button","id":"SEQUENCER","enabled":True},
                {"type":"button","id":"EDITSEQUENCE","enabled":editAllowed},
                {"type":"button","id":"RUNSEQUENCE","enabled":runAllowed},
                {"type":"button","id":"RUNSEQUENCEHERE","enabled":runAllowedHere}],
                    "sequenceid":client["sequenceid"],
                    "componentid":client["componentid"]}

    state.update(viewState)
    return state


def edit(db, username, system, client):
    log.debug("State: Edit screen")

def run(db, username, system, client):
    log.debug("State: Run screen")

def default(db, username, system, client):
    log.debug("State: Default screen")


@app.route('/')
def index():
    pass
   
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


    options = {"HOME":home,
                "SELECT_SAVEDSEQUENCES":savedSeq,
                "SELECT_RUNHIST":runHist,
                "VIEW":view,
                "EDIT":edit,
                "RUN":run}

    choice = client["screen"]
    state = options.get(choice, default)(db,auth.username, system, client)
    return flask.jsonify(state)

@app.route('/runstate', methods=['GET'])
@app.route('/Elixys/runstate', methods=['GET'])
@requires_auth
def runstate():
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
            "clientstate":copy.deepcopy(client),
            "timestamp":time.time()}
    if system["runstate"]["running"]:
        state["clientstate"]["screen"] = "RUN"
    else:
        state["clientstate"]["screen"] = "HOME"
        state["clientstate"]["prompt"]["show"] = False

    return flask.jsonify(state)



