# UserInput unit operation

# Imports
from UnitOperation import *

class UserInput(UnitOperation):
  def __init__(self,systemModel,params):
    raise Exception("Implement UserInput")
    UnitOperation.__init__(self,systemModel)
    self.setParams(params)
		#Should have parameters listed below:
    #self.userMessage
    #self.isCheckbox
    #self.description
    
  def run(self):
    try:
      self.beginNextStep("Starting User Input Operation")
      self.abortOperation()
      self.beginNextStep("Waiting for user input")
      self.setMessageBox()
      self.beginNextStep("User input recieved")
      self.beginNextStep("User Input Operation Complete")
    except Exception as e:
      self.abortOperation(str(e), False)
  
  def setMessageBox(self):
    self.setDescription("Waiting for user input")
    self.waitForUser = True
    self.waitForCondition(self.getUserInput,True,EQUAL,65535) #timeout = Infinite
    self.setDescription()
    
  def getUserInput(self):
    return not(self.waitForUser)
