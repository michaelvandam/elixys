"""SequenceManager

Elixys Sequence Manager
"""

import DBComm
import Sequences
class SequenceManager:
  def __init__(self):
    self.database = DBComm.DBComm()
    self.currentSequence = Sequences.Sequence()
  def logError(self):
    pass
  def loadSequence(self,name):
    sequenceParameters={"id":"","name":"","shortName":"","description":""}
    sequenceData = self.database.getSequence(name)
    if sequenceData:
      for key in sequenceParameters.keys():
        
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
 

def test():
  seq1 = Sequence()
  seq1.database.getSequences()
    
if __name__=="__main__":
    test()