#!/usr/bin/env python
'''Python Script shall connect to a proxy to the server.
Upon connection, this script shall test the cooling system
by turning the system up to a fixed temperature and
running for a fixed amount of time. If the temperature
changes (+/-) from the fixed temp, script shall raise an
alert.
'''
import sys
import logging
sys.path.append("/var/www/wsgi/")
import CoreServerProxy
import csv
import time
import json
import argparse

# Set the move delay for the robot for a half second.
movedelay = 0.5

# Check if user supplied arguments.
if len(sys.argv) == 1:
    print "Please input '-h' to see all options for script."
    sys.exit(0)

# Set up parsers for each command.
parser = argparse.ArgumentParser()
parser.add_argument("-l", "--load",     
                help="Loads a CSV file and runs \
                        the test on the file's coordinates")

parser.add_argument("-r", "--run", action="store_true", 
                help="Runs through each reactor and reagent position")

args = parser.parse_args()

# Functions

def set_cooling_system_on(cooling):
    '''Function shall set the cooling system on.
    '''
    cooling.hardwareComm.CoolingSystemOn()
    log.info("Set cooling system on")

def set_heating_system_off(hardware, temp):
    '''Sets the heaters temp to default 26 C 
    for each reactor'''
    for reactor in range(1,4):
        hardware.SetHeaterTemp(reactor, int(temp))
        log.info('Set reactor ' + str(reactor)
                + ' to temperature ' + str(temp))

    '''Turns off the heater for each reactor'''
    for reactor in range(1,4):
        hardware.HeaterOff(reactor)
        log.info('Turned on reactor ' + str(reactor))

def turn_off_heating_system(hardware):
    '''Turns off the heater temp for each reactor'''
    for reactor in range(1,4):
        hardware.HeaterOff(reactor)
        log.info('Turned off reactor ' + str(reactor))

def is_cooled_to_correct_temp(hardware, model, temp):
    '''Function shall verify the coolers hits
    the correct temperature(the variable "temp").
    This function shall allow the system to safely
    cool to the "temp" value and return once each
    reactor has hit the temperature.
    There shall be a timer of 2 minutes to allow
    the system to cool down.
    If all reactors hit the value, return true.
    Else, return false.
    '''
    # Set up reference for each reactor dict lookup.
    # Set up a dict lookup with booleans.
    reactor_names = ['Reactor1', 'Reactor2', 'Reactor3']
    is_correct_temp = {}
    for reactor in reactor_names:
        is_correct_temp[reactor] = False

    # Set up a timer to keep trace of 2 minutes
    # Go through each reactor and check if the
    # reactor's temp is within +/- 2 C of
    # the 'temp' value.
    # If all are set to true, exit out of timer
    # and return true.
    # Else, return false.

    start_time = time.time()
    while (time.time() - start_time  < 120 and 
           not is_correct_temp['Reactor1'] and
           not is_correct_temp['Reactor2'] and
           not is_correct_temp['Reactor3']):
        for reactor in reactor_names:
            if reactor in model:
                if 'Thermocouple' in model[reactor]:
                    therm = model[reactor]['Thermocouple'].getCurrentTemperature()
                    if (therm > temp-2 or therm < temp-2):
                        is_correct_temp[reactor] = True
                    else:
                        is_correct_temp[reactor] = False
    # After waiting two minutes. Check the boolean values.
    if (is_correct_temp['Reactor1'] and
            is_correct_temp['Reactor2'] and
            is_correct_temp['Reactor3']):
        log.info("Successfully set Reactor 1, 2, and 3 to " + str(temp))
        return True
    else:
        log.error('Error: Heating System could not reach ' + \
                'the temperature of ' + str(temp))
        log.error('Turning off all heaters...')
        return False

def check_temperatures_hold(hardware, model, temp):
    '''Function shall check the temperature
    of each reactor to verify system is holding
    the temperature proprly.
    If a temperature goes +/- 3 C, the system
    shall produce a warning.
    If a temperature goes +/- 5 C, the system
    shall produce a error message and turn off
    all heaters.
    '''
    # Store the model object and store an array of 
    # the name of each reactor to reference for
    # the thermocouple.
    reactor_names = ['Reactor1', 'Reactor2', 'Reactor3']
    
    # Set up a timer to keep trace of 2 minutes
    start_time = time.time()
    # Loop for two minutes.
    # Loop through each reactor and check to see
    # if the model contains the reactor name and
    # a 'Thermocouple' field.
    # Obtain the current temperature of reactor
    # and compare against temp.
    log.info("Starting verification of reactors hold the temperature...")
    while time.time() - start_time  < 180:
        for reactor in reactor_names:
            if reactor in model:
                if 'Thermocouple' in model[reactor]:
                    therm = model[reactor]['Thermocouple'].getCurrentTemperature()
                    if (therm > temp+5 or therm < temp-5):
                        log.error('Error: A reading of ' + str(therm) + \
                                ' was found in ' + str(reactor) + \
                                ' and was not in range of +/- 5 of ' + \
                                str(temp))
                        log.error('Turning off all heaters...')
                        turn_off_heating_system(hardware)
                        sys.exit(0)
                    elif (therm > temp+2 or therm < temp-2):
                        log.warning("Warning: A reading of " + str(therm) + \
                                " was found in " + str(reactor) + \
                                " and was not in ragne of +/- 2 of " + \
                                str(temp))

log = logging.getLogger("elixys.admin")
log.setLevel(logging.DEBUG)

ch = logging.StreamHandler(sys.stdout)
ch.setLevel(logging.DEBUG)

formatter = logging.Formatter(
    '%(asctime)s-%(name)s-%(levelname)s-%(message)    s')
ch.setFormatter(formatter)

log.addHandler(ch)
log.info("Initializing Proxy Instance")

# Connect and robot
proxy = CoreServerProxy.CoreServerProxy()
log.info("Connecting to Elixys Core Sever")
proxy.Connect()

# Try to get the Hardware Object to find the positions of the robot.
log.info("Attempting to obtain the System Model object...")
# Obtain the Core Server from the proxy
proxy_core_server = proxy._CoreServerProxy__pCoreServer.root.exposed_GetSystemModel()

# Obatin Hardware object
hardware = proxy_core_server.hardwareComm
# Obtain the model object
model = proxy_core_server.model

if args.run:
    # Set the cooling system on then constantly
    # check if the temperature of 26 C is reached.
    # If reached, check if the system maintains the
    # temperature.
    temp = 26
    set_heating_system_off(hardware, temp)
    turn_off_heating_system(hardware)
    set_cooling_system_on(hardware)
   
    if is_cooled_to_correct_temp(hardware, model, temp):
        check_temperatures_hold(hardware, model, temp)
    else:
        turn_off_heating_system(hardware)
        sys.exit(0)

    log.info("Successfully finished the System Heating Test!") 
