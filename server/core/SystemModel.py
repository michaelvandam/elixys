"""System Model

Elixys System Model
"""

from threading import Thread
from threading import Lock
import sys
sys.path.append("../database/")
sys.path.append("../hardware/")
#import DBComm
from HardwareComm import HardwareComm

class ElixysSystemModel:
  def __init__(self, pSQL, pHardwareComm):
    # Remember the database and hardware layers
    self.sql = pSQL
    self.hardwareComm = pHardwareComm
    
    # Create the empty system model and a lock to protect it
    self.model = {}
    self.modelLock = Lock()
    
    # Pass a pointer to the system model so the hardware layer can update our state
    self.hardwareComm.SetSystemModel(self)
  
  def buildSystemModel(self):
    """Create system model from database"""
    #Line below would be read from DB.
    self.SystemComponents={'Reactors':['Reactor1','Reactor2','Reactor3'],'ReagentDelivery':['Reagents',],'CoolingSystem':['Cooling',],'VacuumSystem':['Vacuum',]}#Read from database
    for key,value in self.SystemComponents.items():
      if key == 'Reactors':
        for item in value:
          self.model[item]={}
          self.model[item]['Thermocouple']= TemperatureControlModel(item)
          self.model[item]['Motion']= MotionModel(item)
          self.model[item]['Stir']= StirMotorModel(item)
          self.model[item]['Radiation']= RadiationDetectorModel(item)	
          self.model[item]['Stopcock']= StopcockValveModel(item)
      elif key == 'ReagentDelivery':
        for item in value:
          self.model[item]={}
          self.model[item][key]= ReagentDeliveryModel(item)
      elif key == 'CoolingSystem':
        for item in value:
          self.model[item]={}
          self.model[item][key]= CoolingSystemModel(item)
      elif key == 'VacuumSystem':
        for item in value:
          self.model[item]={}
          self.model[item][key]= VacuumSystemModel(item)
  
  def lockSystemModel(self):
    # Acquire the mutex lock and return the system model
    self.modelLock.acquire()
    return self.model
    
  def unlockSystemModel(self):
    # Release the system model lock
    self.modelLock.release()
    
  def initialize():
    for each in "Reactor"+(1,2,3):
      pass
    #self.model['Reactors'][
    
  def getComponentState(componentId,Parameter):#(String,String="")
    return state #Dictionary{name:String => value:Any}
  
  def getSystemState(self):
    print "SQL output:"
    self.sql.getFromDB('sequences','placeholder')
    #return state #Dictionary{name:String => value:Any}

  def getComponentState(self,componentId,Parameter,Value):#(String,String,Any)
    pass
    
# Component model base class
class ElixysComponentModel():
  def __init__(self,name):
    self.type = self.__class__.__name__
    self.name = name
  
  def run(self):
    print ('You called %s.%s.run()' % (self.name,self.__class__.__name__))
  def stop(self):
    print ('You called %s.%s.stop()' % (self.name,self.__class__.__name__))

# Reactor motion model
class MotionModel(ElixysComponentModel):
  def __init__(self,name):
    ElixysComponentModel.__init__(self,name)
  def getAllowedPositions(self):
    pass
  def setPosition(self, sPosition):
    pass
  def getCurrentPosition(self):
    pass
  def isMoving(self):
    pass

# Reactor stir model
class StirMotorModel(ElixysComponentModel):
  def __init__(self,name):
    ElixysComponentModel.__init__(self,name)
    
class TemperatureControlModel(ElixysComponentModel):
  def __init__(self,name):
    ElixysComponentModel.__init__(self,name)

class RadiationDetectorModel(ElixysComponentModel):
  def __init__(self,name):
    ElixysComponentModel.__init__(self,name)
    
class StopcockValveModel(ElixysComponentModel):
  def __init__(self,name):
    ElixysComponentModel.__init__(self,name)
    
class ReagentDeliveryModel(ElixysComponentModel):
  def __init__(self,name):
    ElixysComponentModel.__init__(self,name)    
    
class CoolingSystemModel(ElixysComponentModel):
  def __init__(self,name):
    ElixysComponentModel.__init__(self,name)     
    
class VacuumSystemModel(ElixysComponentModel):
  def __init__(self,name):
    ElixysComponentModel.__init__(self,name)   
    
# Main test function
if __name__ == "__main__":
  # Create and initialize database layer
  pSQL = None
  #pSQL = DBComm.DBComm()
  #try:
  #  self.sql.test()
  #except:
  #  print "SQL connection failure"
  #  quit()

  # Create and initialize hardware layer
  pHardwareComm = HardwareComm()
  pHardwareComm.StartUp()

  # Create and build the system model
  pSystemModel = ElixysSystemModel(pSQL, pHardwareComm)
  pSystemModel.buildSystemModel()

  quit()
  for key,value in x.SystemComponents.items(): #Print out built system model(pretty text)
      for item in value:
        print item
        for k,v in x.model[item].items():
          print '\t',k,":",v.__class__.__name__,'object'
  print '\nExample call, Reactor1 motion model:'
  print '\t',x.model['Reactor1']['Motion'] #Example of single object.
  x.model['Reactor1']['Motion'].run()
  x.model['Reactor1']['Motion'].stop()       
