"""Sequences

Elixys Sequences
"""

import SequenceManager
import UnitOperations
class Sequence:
  def __init__(self,sequenceName):
    self.sequenceManager = SequenceManager.SeqenceManager()
    self.unitOperations = {}
  def setParameters(sequenceParameters):
    self.sequenceID = sequenceParameters['id']
    self.sequenceName = sequenceParameters['name']
    self.sequenceShortName = sequenceParameters['shortName']
    self.sequenceDescription = sequenceParameters['description']
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
    unitOperations = self.Sequence.getUnitOperations(self.sequenceName)
  def getCurrentOperation():
    pass    
 

def test():
  seq1 = Sequence()
  seq1.database.getSequences()
    
if __name__=="__main__":
    test()