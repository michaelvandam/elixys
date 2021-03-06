'''This python script will take in a Python Pickle file name.
This script expects the user to input a file with
a Pickle file and the script shall display the pickle file
inside the command line.
'''
# Import sys, command line args, json and database
# Import pickle
import sys
import argparse
import json
import pickle

# Set up parsers for each command.
parser = argparse.ArgumentParser()
parser.add_argument("-l", "--load", type=str,    
                help="Loads a Pickle file and displays it")

def load_pickle_file(pickle_file):
    try:
        data = pickle.load(open(pickle_file, "r"))
        print "Successfully opened the file"
        #print json.dumps(data, indent=1)
        return data
    except EOFError:
        parser.error("Unable to open pickle (.p) file"
                    "Check that the file exists and isn't empty"
                    "(Run 'ls -l' and check the file)\n\r")
        return None

args = parser.parse_args()
# First open the file.
# Next begin the procedure to update to the database.
if args.load:
    pickle_data = load_pickle_file(str(args.load))
    if pickle_data != None:
        print  json.dumps(pickle_data, indent=1)
    else:
        print "Error reading the pickle file."
