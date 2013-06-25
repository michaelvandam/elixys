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

@app.route('/sequence/<int:seqid>')
@app.route('/Elixys/sequence/<int:seqid>')
def sequences(seqid):
    return "sequence"
