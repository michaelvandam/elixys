#!/usr/bin/env python
'''Python Script shall connect to a proxy to the server
and send the cooldown command.
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

# Get the core server object.
proxy_core_server = proxy._CoreServerProxy__pCoreServer
# Set the Hardware object. Then turn on cooling system.
proxy_hardware = proxy_core_server.root.exposed_GetSystemModel().hardwareComm

proxy_hardware.CoolingSystemOn()
log.info("Sent the 'CoolingSystemOn()' command.\nNow waiting three minutes to cool")
time.sleep(180)

proxy_hardware.CoolingSystemOff()
log.info("Sent the 'CoolingSystemOff()' command.")
time.sleep(2)

log.info("Successfully executed the cool_elixys_system pyhton script")


