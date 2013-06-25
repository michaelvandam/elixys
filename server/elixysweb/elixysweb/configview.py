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
from util.basicauth import *
from util.core import coreServerFactory, \
                    databaseFactory, \
                    getCurrentClientState, \
                    getCurrentSystemState

from elixysweb import app

log = logging.getLogger('elixys.web')

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
    

