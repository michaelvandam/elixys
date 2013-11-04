'''This python script will take in arguments.
Based on these commands, this file will load
information from a Pickle (.p) file. That Pickle
file will contain a dicionary object and will
store the sequence information onto the database.
'''
# Import sys, command line args, json and database
# Import pickle
import sys
import argparse
import json
sys.path.append("../database")
sys.path.append("../core")
from DBComm import DBComm
import pickle

# Set up parsers for each command.
parser = argparse.ArgumentParser()
parser.add_argument("-l", "--load", type=str,    
                help="Loads a pickle file and displays the contents of the file.")

def load_pickle_file(pickle_file):
    try:
        data = pickle.load(open(pickle_file, "rb"))
        print "Successfully opened the file"
        #print json.dumps(data, indent=1)
        return data
    except EOFError:
        parser.error("Unable to open pickle (.p) file"
                    "Check that the file exists and isn't empty"
                    "(Run 'ls -l' and check the file)\n\r")
        return None
    
def insert_sequence_data(seq_data):
    '''Function will insert onto the database the sequence.
    Returns the sequence id of the newly created sequence.
    '''
    print "\tInserting components onto the database..."
    # Obtain the number of Cassettes in the Components.
    cassette_count = 0
    for comp in seq_data['components']:
        for key, value in comp.iteritems():
            if (key == 'componenttype' and value == 'CASSETTE'):
                cassette_count += 1
    
    # Create a new sequence on the DB and store all the 
    # information.
    metadata = seq_data['metadata']
    seq_id = database.CreateSequence(metadata['creator'],
                                    metadata['name'],
                                    metadata['comment'],
                                    metadata['sequencetype'],
                                    cassette_count,
                                len(seq_data['components'][0]['reagentids'])) 
    print "\tSucessfully inserted all components onto the database."
    return seq_id

def update_reagents(sequence_id, seq_data):
    '''Function will update the reagent's values from
    the old database reagent into the new database reagents.
    '''
    print "\tUpdating reagent data from sequence onto current database..."
    # Obtain the new "empty" reagent data in the database.
    metadata = seq_data['metadata']
    dest_reagents = database.GetReagentsBySequence(metadata['creator'], int(sequence_id))
    src_reagents = seq_data['reagents']

    # Created a dict and a list object to store the new values.
    # Loop through all the list elements of the destination(current DB)
    # and the source(old DB sequence data that we are importing).
    # Loop through all dict elements and append to a new destination
    # dictionary. Append the dict elements to the list, then move
    # to the next list object. Keep all componentIDs and reagentIDs
    # the same as they are on the destination(current DB)
    new_reagent_data_for_dest = {}
    new_reagent_data_list = []
    for (dest),(src) in zip(dest_reagents, src_reagents):
        for (dest_key, dest_value), (src_key, src_value) in zip(dest.iteritems(), src.iteritems()):
            if dest_key != 'componentid' and dest_key != 'reagentid':
                new_reagent_data_for_dest[dest_key] = src_value
            else:
                new_reagent_data_for_dest[dest_key] = dest_value
        new_reagent_data_list.append(new_reagent_data_for_dest)
        new_reagent_data_for_dest = {}

    #print json.dumps(new_reagent_data_list, indent=1)
    print "\tSucessfully updated reagent data from sequence on database."
    return new_reagent_data_list
           
def update_to_database(new_reagent_data):
    '''Function will update to the database the new
    reagent data and replace the current(empty) reagent values
    '''
    print "\tUpdating all reagent values on database from sequence..."
    for reag in new_reagent_data:
        database.UpdateReagent('', reag['reagentid'],
                                    reag['name'],
                                    reag['description'])
        #print json.dumps(reag,indent=1)
    print "\tSucessfully updated the reagent values on the database from sequence."

def get_component_id(components, specific_component):
    '''Function will find a matching component and return
    the id of the matching component on the database. This
    is done to update the id in the 'details' field on the
    Components database.
    '''
    #for comp in components:
    #    if comp['componenttype'] != 'CASSETTE':
    #        print "FOUND MATCH: "
    
    print json.dumps(components, indent=1)
    print "\nBREAK:\n"
    print json.dumps(specific_component, indent=1)

def insert_component_data(seq_data, sequence_id):
    '''
    '''
    # Obtain all components from the sequence data.
    # Traverse through all components, skipping Cassettes
    # Then update the contents before create the component.
    # 1) Update the seqeuence id 
    # 2) Update any reagents
    #   2.1) Find reagent information on the destination 
    #   (current DB) that matches the sequence component's
    #   reagent info.
    # 3) Update the id for the component
    print "\tStoring all non-cassette component data onto the database..."
    comp_data = seq_data['components']
    for comp in comp_data:
        if comp['componenttype'] != 'CASSETTE':
            if 'sequenceid' in comp:
                comp['sequenceid'] = sequence_id                
            if 'reagent' in comp:
                if 'note' in comp:
                    current_reag_data = database.GetReagentsByName('',
                                            sequence_id,
                                            comp['note'])
                    if current_reag_data[0] != None:
                        comp['reagent'] = current_reag_data[0]['reagentid']
                 
            comp_id = database.CreateComponent('',
                                    sequence_id,
                                    comp['componenttype'],
                                    comp['note'], 
                                    json.dumps(comp))
            # Now update the id
            #if 'id' in comp:
            #    comp['id'] = comp_id
            #    database.UpdateComponent('',
            #                        comp_id,
            #                        comp['componenttype'],
            #                        comp['note'],
            #                        json.dumps(comp))

    
    print "\tSucessfully stored all component data onto database."


def store_to_database(seq_data):
    '''Top level procedure that will call various functions'''
    # Insert the sequence into the Database.
    print "Attempting to store the new sequence information to the database..."
    if seq_data != None:
        sequence_id = insert_sequence_data(seq_data)
        new_reagent_data = update_reagents(sequence_id, seq_data)
        update_to_database(new_reagent_data)
        insert_component_data(seq_data, sequence_id)
        print "Sucessfully loaded the sequence onto the database!"


# Establish the database connection.
database = DBComm()
database.Connect()

args = parser.parse_args()
# First open the file.
# Next begin the procedure to update to the database.
if args.load:
    seq_data = load_pickle_file(str(args.load))
    store_to_database(seq_data)
