#!/usr/bin/env python

import sys
import logging
sys.path.append("/var/www/wsgi/")
import CoreServerProxy

log = logging.getLogger("elixys.admin")
log.setLevel(logging.DEBUG)

ch = logging.StreamHandler(sys.stdout)
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s-%(name)s-%(levelname)s-%(message)s')
ch.setFormatter(formatter)
log.addHandler(ch)
log.info("Initializing Proxy Instance")
proxy = CoreServerProxy.CoreServerProxy()
log.info("Connecting to Elixys Core Sever")
proxy.Connect()
log.info("Running the Initialize Command")
proxy.CLIExecuteCommand("System","Init()")
raw_input("Sent Initialize Command\r\nPress Enter")

