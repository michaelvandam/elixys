"""
  Test
  
"""

import time
from threading import Thread 
class seqMgr():
  def __init__(self):
    self.currentSequence = seq() #This will come from DB
  def loadSequence(self):
    pass #This would populate the sequence.
  def runSequence(self):
    self.currentSequence.start()

class seq(Thread):
  def __init__(self):
    Thread.__init__(self)
    self.operationData = ("operationOne","operationTwo","operationThree") #This will come from DB
    self.operations = {}
    for operation in self.operationData: #This won't happen here.
      self.operations[operation] = SpecialOperation(operation)
    self.currentOperation = self.operations[self.operationData[0]]
    self.currentOperationState = None
    
  def run(self):
    if self.operations:
      print self.operations
    for operationName in self.operationData:
      self.operationObject = self.operations[operationName]
      try:
        self.operationObject.start()
      except:
        print ("Error: Failed to run unit operation %s." % operationName)
      while not(self.operationObject.isCompleted):
        time.sleep(5)
        self.currentOperationState = self.operationObject.state
        print ("\t Operation: %s\n\t State: %s" % (self.currentOperationState,operationName))
        
    
  def resume(self):
    self.operationObject.resume()
    while self.operationObject.isPaused:
      pass
    print "System has resumed."    
  def pause(self):
    self.operationObject.pause()
    while not(self.operationObject.isPaused):
      pass
    print "System is paused."    
  def abort(self):
    print "Aborting sequence."
      

class UnitOperation(Thread):
  def __init__(self):
    Thread.__init__(self)

class SpecialOperation(UnitOperation):
  def __init__(self,name):
    UnitOperation.__init__(self)
    self.name = name
    self.isPaused = False
    self.isCompleted = False
    self.state = "Created"
  def run(self):
    self.state = "Runninng"
    x=0
    while x<5:
      time.sleep(8)
      x+=1
      print ("Special operation %s, iteration %s" % (self.name,x))
      print ("Is paused: %s" % str(self.isPaused))
      while self.isPaused:
        time.sleep(2)
    print "Special operation %s has ended" % self.name
    self.isCompleted = True
    self.state = "Complete"
  def pause(self):
    self.isPaused = True
    self.state = "Paused"
  def resume(self):
    self.isPaused = False
    self.state = "Running"