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
log.info("\n\tConnecting to Elixys Core Sever")
proxy.Connect()

# Obtain the Core Server from the proxy
proxy_core_server = proxy._CoreServerProxy__pCoreServer
#print proxy_core_server

# Obtain the System model for the Core Server
proxy_hardware = proxy_core_server.root.exposed_GetSystemModel()
#print proxy_hardware

# Obtain the Reagent Delivery value
reagent_delivery = proxy_hardware.model['ReagentDelivery']
#print reagent_delivery

# Obtain the robot's current position
print str(reagent_delivery.getCurrentPositionRaw())

