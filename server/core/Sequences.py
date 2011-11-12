"""Sequences

Elixys Sequences
"""

import sys
sys.path.append("unitoperations")
import UnitOperations
import CoreServer
from threading import Thread 
import time

class Sequence(Thread):
  def __init__(self, sRemoteUser, nSequenceID, pSequenceManager, pSystemModel):
    """Constructor"""
    # Call base class init
    Thread.__init__(self)

    # Initialize variables
    self.username = sRemoteUser
    self.sequenceID = nSequenceID
    self.sequenceManager = pSequenceManager
    self.systemModel = pSystemModel
    self.componentID = 0
    self.running = False

    # Fetch the sequence from the database
    self.sequence = self.sequenceManager.GetSequence(sRemoteUser, nSequenceID)

    # Make sure the sequence is valid
    if not self.sequence["metadata"]["valid"]:
      raise Exception("Cannot run an invalid sequence")

  def run(self):
    """Thread entry point"""
    # Main sequence run loop
    self.running = True
    for pComponent in self.sequence["components"]:
      # Create and run the next unit operation
      self.componentID = pComponent["id"]
      pUnitOperation = UnitOperations.createFromComponent(self.sequenceID, pComponent, self.username, self.sequenceManager.database, self.systemModel)
      pUnitOperation.setDaemon(True)
      pUnitOperation.start()
      self.systemModel.SetUnitOperation(pUnitOperation)

      # Wait until the operation completes
      while pUnitOperation.is_alive():
        time.sleep(0.25)

    # Run complete
    self.running = False

    """self.pOperations = []
    self.nOperationIndex = 0
    for pComponent in self.sequenceData['components']:
      pComponentData = (nOperationIndex,pComponent['id'],pComponent['name'],pComponent['componenttype'])
      self.pOperations.append(pComponentData)
      self.nOperationIndex +=1
    self.nCurrentOperationIndex = 0 # Current operation index, starts at zero.
    self.nTotalOperations = len(self.pOperations) #Grab total number of operations
    self.sCurrentOperationName = None #String describing current operation."""
    
  def setParameters(sequenceParameters):
    self.sequenceID = sequenceParameters['id']
    self.sequenceName = sequenceParameters['name']
    self.sequenceShortName = sequenceParameters['shortName']
    self.sequenceDescription = sequenceParameters['description']
  def logError(self,sErrorMessage):
    CoreServer.gDatabase.Log(sUername, "Sequences Error:(" +(sErrorMessage) + ")")
    
  def RunSequence(self):
    print "running the sequence!"
    for index in range(self.nOperationIndex):
      #print self.pOperations[index][1]  ##This pulls out the OperationID at the current index.
      if self.CheckExpectedOperation(index): #If this returns true, our expected operation matches. Otherwise our data has changed!
        #self.CheckForPause() 
        self.nCurrentOperationIndex = index #Each iteration update operation variable.
        
      else:
        abort()
        
  def CheckExpectedOperation(self,index):
    #Check for expected operation at current index
    expectedOperation = self.pOperations[index] #Grab the expected operation tuple
    #if expectedOperation[1] = self.sequenceData['components'][expectedOperation[1]]['id']:
    #  if expectedOperation[2] = self.sequenceData['components'][expectedOperation[1]]['name']:
    #    if expectedOperation[3] = self.sequenceData['components'][expectedOperation[1]]['componenttype']:
    #      return True #If they all match return true
    return False
  def resume(self):
    pass
  def pauseSequence(self):
    pass
  def abort(self):
    pass    
  def getOperations(self):
    unitOperations = self.Sequence.getUnitOperations(self.sequenceName)
  def getCurrentOperation(self):
    return self.pOperations[self.nCurrentOperationIndex] # You can return any details you want here, currently has (Index,ID,name,componenttype)
    
  def GetReagent(self, sRemoteUser, nReagentID):
    """ Gets a reagent from the database """
    # Fetch the reagent from the databse
    return self.database.GetReagent(sRemoteUser, nReagentID)
 

def test():
  seq1 = Sequence()
  seq1.database.getSequences()
    
if __name__=="__main__":
    test()
