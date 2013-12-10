#!/usr/bin/env python
'''Python Script shall connect to a proxy to the server
and shall test the reactor components of the Elixys
hardware system. Script shall move each reactor to
the Add, Elute, Transfer, React, and Evap positions.
Then the reactor will be moved up and verified that
it has hit the up position. If successful, move down
and verify reactor is down. Move to next reactor and
repeat process.
'''
import sys
import logging
sys.path.append("/var/www/wsgi/")
import CoreServerProxy
import csv
import time
import json

def is_user_ready():
    '''Function shall prompt if the user wishes to 
    execute the test reactor robot movement script
    '''
    user_input = raw_input("Do you wish to execute the Reactor Robot " + \
            "Movement Test? (y/n)")
    if (str(user_input) == 'y' or
        str(user_input) == 'Y'):
        return True
    
    return False

def enable_reactor_robots(hardware):
    '''Function shall enable the reactor robots
    '''
    for reactor in range(1,4):
        hardware.EnableReactorRobot(reactor)
        log.info("Enabled Reactor Robot " + str(reactor))
    time.sleep(3)
    log.info("Enabled all Reactor Robots")

def disable_reactor_robots(hardware):
    '''Function shall disable the reactor robots
    '''
    for reactor in range(1,4):
        hardware.DisableReactorRobot(reactor)
        log.info("Disabled Reactor Robot " + str(reactor))
    time.sleep(3)
    log.info("Disabled all Reactor Robots")

def set_reactor_robot_up(hardware):
    '''Function shall set the reactor
    robots to the up position.
    '''
    time.sleep(1)
    for reactor in range(1,4):
        hardware.ReactorUp(reactor)
        log.info("Set Reactor Robot " + str(reactor)+ \
                " up")
    time.sleep(3)

def set_reactor_robot_down(hardware):
    '''Function shall set the reactor
    robots to the down position.
    '''
    time.sleep(1)
    for reactor in range(1,4):
        hardware.ReactorDown(reactor)
        log.info("Set Reactor Robot " + str(reactor)+ \
                " down")
    time.sleep(3)
    
def move_reactor_robots_to_add(hardware):
    '''Function shall move reactor robots
    to the add position.
    '''
    time.sleep(2)
    for reactor in range(1,4):
        hardware.MoveReactor(reactor, 'Add')
        log.info("Sent Reactor Robot " + str(reactor) + \
                " to the 'ADD' position")

def move_reactor_robots_to_install(hardware):
    '''Function shall move reactor robots
    to the init position.
    '''
    time.sleep(2)
    for reactor in range(1,4):
        hardware.MoveReactor(reactor, 'Install')
        log.info("Sent Reactor Robot " + str(reactor) + \
                " to the 'install' position")

def move_reactor_robots_to_evaporate(hardware):
    '''Function shall move reactor robots
    to the evaporate position.
    '''
    time.sleep(2)
    for reactor in range(1,4):
        hardware.MoveReactor(reactor, 'Evaporate')
        log.info("Sent Reactor Robot " + str(reactor) + \
                " to the 'Evaporate' position")

def move_reactor_robots_to_react1(hardware):
    '''Function shall move reactor robots
    to the react 1 position.
    '''
    time.sleep(2)
    for reactor in range(1,4):
        hardware.MoveReactor(reactor, 'React1')
        log.info("Sent Reactor Robot " + str(reactor) + \
                " to the 'React1' position")

def move_reactor_robots_to_react2(hardware):
    '''Function shall move reactor robots
    to the react 2 position.
    '''
    time.sleep(2)
    for reactor in range(1,4):
        hardware.MoveReactor(reactor, 'React2')
        log.info("Sent Reactor Robot " + str(reactor) + \
                " to the 'React2' position")

def move_reactor_robots_to_transfer(hardware):
    '''Function shall move reactor robots
    to the transfer position.
    '''
    time.sleep(2)
    for reactor in range(1,4):
        hardware.MoveReactor(reactor, 'Transfer')
        log.info("Sent Reactor Robot " + str(reactor) + \
                " to the 'Transfer' position")

log = logging.getLogger("elixys.admin")
log.setLevel(logging.DEBUG)
ch = logging.StreamHandler(sys.stdout)
ch.setLevel(logging.DEBUG)

formatter = logging.Formatter(
    '%(asctime)s-%(name)s-%(levelname)s-%(message)    s')
ch.setFormatter(formatter)

log.addHandler(ch)

#Prompt if user wishes to execute script.
if not is_user_ready():
    log.info("User declined to run 'Reactor Robot Movement test'")
    sys.exit(0)

log.info("Initializing Proxy Instance")

# Connect and Init() robot
proxy = CoreServerProxy.CoreServerProxy()
log.info("Connecting to Elixys Core Sever")
proxy.Connect()

# Try to get the Hardware Object to find the positions of the robot.
# Obtain the Core Server from the proxy
proxy_core_server = proxy._CoreServerProxy__pCoreServer
# Obtain the System model for the Core Server
proxy_hardware = proxy_core_server.root.exposed_GetSystemModel()
# Set hardware object to talk to PLC
hardware = proxy_hardware.hardwareComm

# Enable each reactor robot & set robots down
enable_reactor_robots(hardware)
set_reactor_robot_down(hardware)

# Move Reactor robots to each position:
move_reactor_robots_to_add(hardware)
move_reactor_robots_to_evaporate(hardware)
move_reactor_robots_to_transfer(hardware)
move_reactor_robots_to_react1(hardware)
move_reactor_robots_to_react2(hardware)

# Finishing up, return robots to position:
move_reactor_robots_to_install(hardware)

# Disable each reactor robot & set robots up
set_reactor_robot_up(hardware)
disable_reactor_robots(hardware)

log.info("Successfully finished the Reactor Hardware Movement Test!")
    

