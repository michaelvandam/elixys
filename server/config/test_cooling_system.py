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

log.info("\n\tRunning the Cooling Test...\n\tTurning on Cooling System")
a = proxy.CLIExecuteCommand("System","CoolingSystemOn()")
print str(a)

log.info("\n\tTurned on Cooling System!\n\tWaiting three minutes...")
time.sleep(180)

log.info("\n\tFinished waiting three minutes.\nTurning off cooling system and initalizing.")
a = proxy.CLIExecuteCommand("System","CoolingSystemOff()")
a = proxy.CLIExecuteCommand("System","Init()")

log.info("\n\tSuccessfully tested the cooling system.")
