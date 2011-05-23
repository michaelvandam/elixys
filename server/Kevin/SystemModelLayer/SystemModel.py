"""System Model

Elixys System Model
"""

import time
from threading import Thread


class ElixysSystemModel:
  def __init__(self):
    #Test connection to DB, else fail.
    pass

  def buildSystemModel(self):
    """Create system model from database"""
    SystemComponents={"reactor1":"reactor","reactor2":"reactor","reactor3":"reactor","reagentdelivery":"reagents"}#Read from database
    for key,value in SystemComponents.items():
      key=ElixysComponentModel(key,value)     #Create objects for component threads
      key.start()                             #Start component threads
    
  def initialize():
    pass
    
  def getComponentState(componentId,Parameter):#(String,String="")
    
    return state #Dictionary{name:String => value:Any}
  
  def getSystemState():
  
    return state #Dictionary{name:String => value:Any}

  def getComponentState(componentId,Parameter,Value):#(String,String,Any)
    pass
    
class ElixysComponentModel(Thread):
  def __init__(self,name,type):
    Thread.__init__(self)
    self.name = name
  
  def run(self): #Fake component updater threads output to console to make sure they exist.
    start =  time.time()
    end = 0;
    while (end-start<0.02):
      print ("Thread test %s." % self.name) 
      end = time.time()
      
def test():
  esm=ElixysSystemModel()
  esm.buildSystemModel()
    
if __name__=="__main__":
    test()