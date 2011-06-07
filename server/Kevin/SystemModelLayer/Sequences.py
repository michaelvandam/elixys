"""Sequences

Elixys Sequences
"""

import DBComm
import UnitOperations
class Sequence:
  def __init__(self,SequenceID):
    self.database = DBComm.DBComm()
    self.unitOperations = {}
    self.SequenceID = SequenceID
  def logError():
    pass
  def run():
    pass
  def resume():
    pass
  def pause():
    pass    
  def abort():
    pass    
  def getOperations():
    unitOperations = self.database.getUnitOperations(self.SequenceID)
  def getCurrentOperation():
    pass    
 

def test():
  seq1 = Sequence()
  seq1.database.getSequences()
    
if __name__=="__main__":
    test()