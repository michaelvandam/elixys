#!/usr/bin/env python
'''Python Script shall connect to the CLI and CoreServer so
commands can be sent outside of the CLI and client side.
'''
import sys
import logging
sys.path.append("/var/www/wsgi/")
import CoreServerProxy
import time

log = logging.getLogger("elixys.admin")
log.setLevel(logging.DEBUG)

ch = logging.StreamHandler(sys.stdout)
ch.setLevel(logging.DEBUG)

formatter = logging.Formatter('%(asctime)s-%(name)s-%(levelname)s-%(message)    s')
ch.setFormatter(formatter)

log.addHandler(ch)
log.info("Initializing Proxy Instance")

proxy = CoreServerProxy.CoreServerProxy()
log.info("Connecting to Elixys Core Sever")
proxy.Connect()

log.info("Connected! Initializing, Please wait...")
proxy.CLIExecuteCommand("system", "Init()")
time.sleep(50)

log.info("Successfully finished Initializing!")


