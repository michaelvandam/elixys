"""SequenceManager

Elixys Sequence Manager
"""

import sys
sys.path.append("../database/")
import DBComm
import Sequences
import json

class SequenceManager:
  def __init__(self):
    self.database = DBComm.DBComm()
    self.database.Connect()
    #self.currentSequence = Sequences.Sequence()
  def logError(self):
    pass
  def loadSequence(self,name):
    sequenceParameters={"id":"","name":"","shortName":"","description":""}
    sequenceData = self.database.getSequence(name)
    if sequenceData:
      for key in sequenceParameters.keys():
        pass
      self.CurrentSequence.setParameters(sequenceParameters)
  def createNewSequence(self,name,shortName,description):
    if not(self.sequenceExists(name)): #Check database for sequence name to deter collision
      if not(shortName):
        if (len(name)>4):
          shortName = name[:4]
        else:
          shortName = name
      if not(description):
        description = "No description entered."
      self.database.runQuery('INSERT INTO sequences (seq_name,seq_shortname,seq_description) VALUES("%s","%s","%s");' % (name,shortName,description))#Create a new ID, add to DB.
      self.currentSequence = self.loadSequence(name)
    else:
      print "Error: Sequence already exists!"
    ###
    ### self.database.runQuery('SELECT id FROM sequences ORDER BY id DESC LIMIT 1;') #Get last ID
    ### self.database.runQuery('UPDATE sequences SET seq_description="%s" WHERE name="%s";' % (description,name))#Set description in DB
    ###
    
    self.currentSequence = newSequence
  def sequenceExists(self,name):
    try:
      if self.database.runQuery('SELECT id FROM sequences WHERE seq_name="%";') % name:
        return True
      else:
        return False
    except:
      print "Failed to get sequences"
      
    return
  def getCurrentSequence(self):
    return self.currentSequence
    
    #Create a sequence using this data
  def getAvailableOperations(self):
    pass    
  def getAvailableOperationIds(self):
    pass    

  def ListSequences(self):
    """List all sequences in the database"""
    pSequenceList = self.database.GetAllSequences("System")
    print str(pSequenceList)

  def ImportSequence(self, sFilename):
    """Imports the specified sequence into the database"""
    # Open the file and read the contents
    pSequenceFile = open(sFilename)
    sSequence = pSequenceFile.read()
    pSequence = json.loads(sSequence)

    # Create the sequence
    if (pSequence["type"] == "sequence") and (pSequence["name"] != "") and (pSequence["reactors"] != 0) and \
        (pSequence["reagentsperreactor"] != 0) and (pSequence["columnsperreactor"] != 0):
      nSequenceID = self.database.CreateSequence("System", pSequence["name"], pSequence["description"], "Saved", pSequence["reactors"],
        pSequence["reagentsperreactor"], pSequence["columnsperreactor"])
    else:
      raise Exception("Invalid sequence parameters")

    # Add the reagents
    nCurrentCassette = 0
    for pReagent in pSequence["reagents"]:
      if (pReagent["type"] == "reagent") and (pReagent["cassette"] != 0) and (pReagent["position"] != "") and (pReagent["name"] != ""):
        self.database.UpdateReagentByPosition("System", nSequenceID, pReagent["cassette"], pReagent["position"], True, pReagent["name"],
          pReagent["description"])
        if nCurrentCassette != pReagent["cassette"]:
          self.database.EnableCassette("System", nSequenceID, pReagent["cassette"] - 1)
          nCurrentCassette = pReagent["cassette"]
      else:
        raise Exception("Invalid reagent parameters in \"" + str(pReagent) + "\"")

    # Process each component
    for pComponent in pSequence["components"]:
      if (pComponent["type"] != ""):
        # Add the component
        self.database.CreateComponent("System", nSequenceID, pComponent["componenttype"], "", json.dumps(pComponent))
      else:
        raise Exception("Invalid reagent parameters in \"" + str(pReagent) + "\"")

  def ExportSequence(self, nSequenceID, sFilename):
    print "Implement ExportSequence()"

"""

        # Convert any reagent entries to IDs
        if pComponent.has_key("reagent"):
          # Remove the reagent from our local list
          pLocalReagents = []
          for pReagent in pSequence["reagents"]:
            # Add reagents that match the target name
            if pReagent["name"] == pComponent["reagent"]:
              pLocalReagents.append(pReagent)
          if len(pLocalReagents) == 0:
            raise Exception("Missing reagent " + pComponent["reagent"])
          pSequence["reagents"].remove(pLocalReagents[0])

          # Get a list of reagents from the database
          pDatabaseReagents = self.database.GetReagentsByName("System", nSequenceID, pComponent["reagent"])
          if len(pDatabaseReagents) == 0:
            raise Exception("Database missing reagent " + pComponent["reagent"])

          # Look up the desired reagent and update the component
          pComponent["reagent"] = pDatabaseReagents[len(pDatabaseReagents) - len(pLocalReagents)]

        # Convert any targets to IDs
        if pComponent.has_key("target"):
          # Get a list of reagents from the database
          pDatabaseReagents = self.database.GetReagentsByName("System", nSequenceID, pComponent["target"])
          if len(pDatabaseReagents) == 0:
            # Check again to see if this is a reserved reagent
            pDatabaseReagents = self.database.GetReservedReagentsByName("System", pComponent["target"])
            if len(pDatabaseReagents) == 0:
              # OK, now it's a problem
              raise Exception("Database missing target " + pComponent["target"])

            # Update the component
            pComponent["target"] = pDatabaseReagents[0][0]
          else:
            # Targets always go with the current reactor
            for pReagent in pDatabaseReagents:
              if pReagent["componentid"] == pComponent["reactor"]:
                # Update the component
                print "Updating component with reagent " + str(pReagent)
                pComponent["target"] = pReagent["reagentid"]
"""

def test():
  seq1 = Sequence()
  seq1.database.getSequences()
    
if __name__=="__main__":
    test()
