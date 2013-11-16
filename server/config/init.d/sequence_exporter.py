'''This python script/file will take in arguments. Based on
these arguments/commands, this file will pull information
from a certain sequence ran from the database and save it
as a PICKLE file.
'''
# Import sys for path to DB
import sys
# Import command line args
import argparse
# Import json

# Import DB usage
sys.path.append("../../database")
sys.path.append("../../core")
from DBComm import DBComm
from Exceptions import SequenceNotFoundException
import pickle

# Set up parsers for each command. 
parser = argparse.ArgumentParser()
parser.add_argument("-s", "--sequenceID", type=int,    
                help="Expects a sequence id to export from the Database")

parser.add_argument("-n", "--name", type=str,    
                help="Expects a name of a sequence to export from the Database")
args = parser.parse_args()

def obtain_database_data(sequence):
    '''Function will take the sequence id given
    and obtain all information about sequence
    from the database.
    '''
    print "\tAttempting to obtain the sequence information..."
    # Check if are given a sequence id or a sequence name.
    if isinstance(sequence, int):
        try:
            sequence_data = db.GetSequence('', sequence)
            #print json.dumps(sequence_data ,indent=1)
            print "\tSucessfully obtained the sequence information."
            return sequence_data
        except SequenceNotFoundException:
            parser.error("ERROR: Unable to find sequence id on database.\n" 
                    "Verify that you supplied the correct "
                    "sequence id.\r\n")
            return None
    else:
        try:
            # Obtain the sequence by the name provided and then obtain
            # the id of the returned sequence.
            sequence_data = db.GetSequencesByName('', sequence)[0]
            sequence_data = db.GetSequence('', sequence_data['id'])
            #print json.dumps(sequence_data,indent=1)
            #print json.dumps(sequence_data,indent=1)
            print "\tSucessfully obtained the sequence information."
            return sequence_data
        except SequenceNotFoundException:
            parser.error("\nERROR: Unable to find sequence id on database.\n" 
                    "Verify that you supplied the correct "
                    "sequence id.\r\n")
            return None
        except IndexError:
            parser.error("\nERROR: Unable to find sequence name on database.\n" 
                    "Verify that you supplied the correct "
                    "sequence name.\r\n")
            return None


def obtain_reagent_values(seq_data):
    '''Function will take the dict object of all sequence information
    and will find all reagent properties based on their ID.
    '''
    # For each components tag in the sequence data, pull each
    # key and value. Check if we obtain the reagentIDs list
    # and traverse through each reagent's id. Pull data
    # from each reagent id and add it to the seq_data object.
    print "\tObtaining all reagent data from the sequence..."
    reagents = []
    if seq_data != None:
        for comp in seq_data['components']:
            for comp_key, comp_value in comp.iteritems():
                if comp_key == 'reagentids':
                    for reagent in comp_value:
                        #reagent = comp_value
                        #print reagent
                        reagents.append(db.GetReagent('', int(reagent)))
                        #print json.dumps(reagent_data,indent=1)
    
    seq_data['reagents'] = reagents
    print "\tSucessfully obtained all reagent data from the sequence."
    return seq_data


# Execution of the core of the code below:
# Set up database connection
db = DBComm()
db.Connect()

if (args.sequenceID != None and args.name != None):
    parser.error("Please only enter a Sequence ID or a Sequence Name.")
    sys.exit(0)
# Check if we were given a sequence id or a sequence name.
if args.sequenceID:
    seq_data = obtain_database_data(args.sequenceID)
    seq_data = obtain_reagent_values(seq_data)
    try:
        pickle.dump(seq_data,
                    open('sequence_' + str(args.sequenceID) + '_dump.p', 'wb'))
        print ("\tSuccessfully exported the sequence %s " 
                "to seqeunce_%s_dump.p" % (args.sequenceID, args.sequenceID))
    except IOError:
        parser.error("\nERROR: Unable to write"
                "pickle file to current directory.\n" 
                "Verify that you have permission "
                "to write to this directory.\r\n")
elif args.name:
    seq_data = obtain_database_data(args.name)
    seq_data = obtain_reagent_values(seq_data)
    try:
        filename = str(args.name).replace(" ", "_")
        pickle.dump(seq_data, open('sequence_' + filename + '_dump.p', 'wb'))
        print ("\tSuccessfully exported the sequence %s "
                "to seqeunce_%s_dump.p" % (filename, filename))
    except IOError:
        parser.error("\nERROR: Unable to write \
                pickle file to current directory.\n" 
                "Verify that you have permission \
                to write to this directory.\r\n")
