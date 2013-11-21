'''This python script will take in a file name.
This script expects the user to input a file with
a JSON object and will convert the object into a
Python pickle file. 
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
                help="Loads a JSON file and converts JSON to a Pickle file")

def load_JSON_file(json_file):
    try:
        json_data = ''
        file = open(json_file, "r")
	print "Successfully opened the file\nAttempting to open file as a JSON object"
        for line in file:
            json_data = json_data + line
	print "Successfully read the JSON object"
        return json_data
    except EOFError:
        parser.error("Unable to open pickle (.p) file"
                    "Check that the file exists and isn't empty"
                    "(Run 'ls -l' and check the file)\n\r")
        return None
  
def write_to_pickle(json_data, old_filename):
    try:
        filename = str(old_filename).replace(" ", "_")
	filename = str(filename).replace("/", "_")
        # Obtain the name of the file excluding the extension.
        filename = filename.split('.')[0]
        #print json_data
        pickle.dump(json_data, open(filename + '_sequence_dump.p', 'wb'))
        print ("\tSuccessfully exported the sequence %s "
                "to %s_sequence_dump.p" % (filename, filename))
    except IOError:
        parser.error("\nERROR: Unable to write \
                pickle file to current directory.\n" 
                "Verify that you have permission \
                to write to this directory.\r\n")

args = parser.parse_args()
# First open the file.
# Next begin the procedure to update to the database.
if args.load:
    json_data = json.loads(load_JSON_file(str(args.load)))
    write_to_pickle(json_data, args.load)

