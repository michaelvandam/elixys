"""SequenceManager

Elixys Sequence Manager
"""

import DBComm
import Sequences
class SequenceManager:
  def __init__(self):
    self.database = DBComm.DBComm()
    self.currentSequence = Sequences.Sequence(SequenceID)
  def logError():
    pass
  def loadSequence():
    sequenceData = self.database.getSequence(SequenceID)
  def createNewSequence():
    pass
  def getCurrentSequence(SequenceID):
    sequenceData = self.database.getSequence(SequenceID)
    
    #Create a sequence using this data
  def getAvailableOperations():
    pass    
  def getAvailableOperationIds():
    pass    
 

def test():
  seq1 = Sequence()
  seq1.database.getSequences()
    
if __name__=="__main__":
    test()