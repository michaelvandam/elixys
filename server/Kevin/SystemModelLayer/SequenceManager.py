"""SequenceManager

Elixys Sequence Manager
"""

import DBComm
import Sequences
class SequenceManager:
  def __init__(self):
    self.database = DBComm.DBComm()
    self.currentSequence = Sequences.Sequence(SequenceID)
  def logError(self):
    pass
  def loadSequence(self):
    sequenceData = self.database.getSequence(SequenceID)
  def createNewSequence(self,name,shortName):
    #Check database for sequences to deter collision
    #lastID = self.database.runQuery('SELECT id FROM sequences ORDER BY id DESC LIMIT 1; #Get last ID')
    if (shortName = ""):
      shortName = name[:4]
    self.database.runQuery('INSERT INTO sequences (seq_name,seq_shortname) VALUES(%s,%s);' % (name,shortName))#Create a new ID, add to DB.
    
    
    self.currentSequence = newSequence
  def getSequenceNames(self):
    try:
      self.database.getSequences()
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