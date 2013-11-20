#!/usr/bin/env python
'''Python Script shall connect to the CLI and CoreServer so
commands can be sent outside of the CLI and client side.
'''
import sys
import logging
sys.path.append("/var/www/wsgi/")
import CoreServerProxy
import csv
import time
import json
import argparse

# Check if user supplied arguments.
if len(sys.argv) == 1:
    print "Please input '-h' to see all options for script."
    sys.exit(0)

# Set up parsers for each command.
parser = argparse.ArgumentParser()
parser.add_argument("-l", "--load", type=str,    
                help="Loads a CSV file and runs the test on the file's coordinates")

parser.add_argument("-r", "--run", action="store_true", 
                help="Runs through each reactor and reagent position")

args = parser.parse_args()

def read_CSV_file():
    ''' Attempt to read the CVS file and store the contents of
    file in a two dim array. Function shall return a two dim.
    array as coordinates.
    '''
    log.info("Running the Hardware Movement Test...")
    log.info("Reading the CVS file for the coordinates...")
    coords = []
    with open('coords.csv', 'rb') as csvfile:
        line = csv.reader(csvfile, delimiter=',', quotechar='|')
        for row in line:
            two_coords = []
            for point in row:
                two_coords.append(int(point))
            coords.append(two_coords)
    log.info("Finished reading the CVS file!")
    return coords

def set_gripper_and_gas_transfer_up(proxy, log):
    log.info("Setting Gripper to up position...")
    proxy.CLIExecuteCommand("System","GripperUp()")
    log.info("Setting Gas Transfer to up position...")
    proxy.CLIExecuteCommand("System","GasTransferUp()")
    log.info("Successfully set the Gripper and Gas Transfer up!")

def obtain_robot_position(reagent_delivery):
    '''Obtains the robot position and formats the (x,y)
    as a dictionary object. Function shall return the
    dictionary object.
    '''
    x_and_y_positions = {}
    current_robot_position = str(reagent_delivery.getCurrentPositionRaw())
    
    # Format string
    current_robot_position = current_robot_position.replace("(", "")
    current_robot_position = current_robot_position.replace(")", "")
    
    # Split x and y position based on ','
    x_and_y_array = current_robot_position.split(',')
    x_and_y_positions['x'] = x_and_y_array[0]
    x_and_y_positions['y'] = x_and_y_array[1]

    return x_and_y_positions

def is_in_correct_position(current_robot_position, coord):
    '''Function shall return a boolean.
    Function shall compare the current robot position to
    the coordinates provided to see if the robot is in the right position.
    '''
    if ('x' in current_robot_position.keys() and
            'y' in current_robot_position.keys()):
        if int(current_robot_position['x']) != int(coord[0]):
            print str(current_robot_position['x'])
            print str(coord[0])
            return False
        if int(current_robot_position['y']) != int(coord[1]):
            return False
        # If the current robot's position matches the coordinates, return true.
        return True
    # If there isn't an X and Y key in current_robot_position.
    return False
    
def robot_movement_test(reagent_delivery, coords, proxy, log):
    log.info("Now moving robot to each position")
    for coord in coords:
        if coord:
            if (coord[0] != None and coord[1] != None):
                # coord[0] is x, coord[1] is y.
                log.info("Attempting to move robot to (" + str(coord[0]) + ", " + str(coord[1]) + ")")
                proxy.CLIExecuteCommand("System","MoveRobotToX(" + str(coord[0]) + ")")
                proxy.CLIExecuteCommand("System","MoveRobotToY(" + str(coord[1]) + ")")
                log.info("Successfully sent the move command. Waiting 10 seconds to verify robot is in position.")
                time.sleep(10)
                current_robot_position = obtain_robot_position(reagent_delivery)
                if not is_in_correct_position(current_robot_position, coord):
                    print 'Robot is in an incorrect position. Flagging error and exiting...'
                    log.error('Coordinates in CVS file that failed: ' + str(coord))
                    log.error("Robot's current position: " + json.dumps(current_robot_position, indent=1))
                    sys.exit(0)
                else:
                    print '\nRobot successfully moved to the correct position!\n'

def robot_movement_test_reactors_and_reagents(reagent_delivery, proxy_hardware, log):
    log.info("Now moving robot to each reactor position with each reagent position")
    for reactor_position in range(1,4):
        for reagent_position in range(1,13):
            log.info("\n\nAttempting to move robot to Reactor: " + str(reactor_position) + 
                    ", Reagent: " + str(reagent_position))

            proxy_hardware.hardwareComm.MoveRobotToReagent(reactor_position, reagent_position)
            #proxy.CLIExecuteCommand("System","MoveRobotToReagent(" + 
            #        str(reactor_position) + ", " +
            #        str(reagent_position) + ")")
            # Check if robot is in the right position. Display error and exit out.
            log.info("Successfully sent the move command. Waiting 10 seconds to verify robot is in position.")
            current_robot_position = obtain_robot_position(reagent_delivery)
            time.sleep(1.5)
            print str(current_robot_position) 
            if 'Unkown' in reagent_delivery.getCurrentPositionRaw():
                print 'Robot is in an incorrect position. Flagging error and exiting...'
                log.error('Coordinates in CVS file that failed: ' + str(coord))
                log.error("Robot's current position: " + json.dumps(current_robot_position, indent=1))
                sys.exit(0)
            else:
                print '\nRobot successfully moved to the correct position!\n'

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

# Try to get the Hardware Object to find the positions of the robot.
log.info("Attempting to obtain the Hardware object...")
# Obtain the Core Server from the proxy
proxy_core_server = proxy._CoreServerProxy__pCoreServer

# Obtain the System model for the Core Server
proxy_hardware = proxy_core_server.root.exposed_GetSystemModel()

# Obtain the Reagent Delivery value
reagent_delivery = proxy_hardware.model['ReagentDelivery']

# Obtain the robot's current position
reagent_delivery.getCurrentPositionRaw()
log.info("Successfully obtained the Hardware object!")

# Set Gripper and Gas Transfer in UP position.
set_gripper_and_gas_transfer_up(proxy, log)

if args.load:
    # Read CSV file and store contents in coords.
    coords = read_CSV_file()
    # Begin the Robot Movement Test.
    robot_movement_test(reagent_delivery, coords, proxy, log)

if args.run:
    # Run through each reactor and reagent position.
    robot_movement_test_reactors_and_reagents(reagent_delivery, proxy_hardware, log)



log.info("Successfully finished the Hardware Movement Test!")
    

