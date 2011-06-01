"""Sequences

Elixys Sequences
"""

import DBComm

class Sequence:
  def __init__(self):
    self.database = DBComm.DBComm()
    
  def logError():
    pass
  def loadSequence():
    pass
  def createSequence():
    pass
  def getCurrentSequence():
    pass    
  def getAvailableOperations():
    pass    
  def getAvailableOperationIds():
    pass    
 

def test():
  seq1 = Sequence()
  seq1.database.getSequences()
    
if __name__=="__main__":
    test()