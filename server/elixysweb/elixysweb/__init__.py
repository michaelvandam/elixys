#!/usr/bin/python
# Elixys Web server

from flask import Flask
import logging
log = logging.getLogger('elixys.web')
app = Flask("elixysweb")
import elixysweb.stateview
import elixysweb.configview
import elixysweb.sequenceview
import elixysweb.reagentview

