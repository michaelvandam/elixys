"""System Model

Elixys System Model
"""

import DBComm
from threading import Thread


class ElixysSystemModel:
  def __init__(self):
    self.sql = DBComm.DBComm()
    try:
      self.sql.test()
    except:
      print "SQL connection failure."
    #Test connection to DB, else fail.
    pass

  def buildSystemModel(self):
    """Create system model from database"""
    self.SystemComponents={'Reactors':['Reactor1','Reactor2','Reactor3'],'ReagentDelivery':['Reagents',],'CoolingSystem':['Cooling',],'VacuumSystem':['Vacuum',]}#Read from database
    self.model = {}
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
          
  def initialize():
    pass
    
  def getComponentState(componentId,Parameter):#(String,String="")
    
    return state #Dictionary{name:String => value:Any}
  
  def getSystemState(self):
    print "SQL output:"
    self.sql.getFromDB('sequences','placeholder')
    #return state #Dictionary{name:String => value:Any}

  def getComponentState(self,componentId,Parameter,Value):#(String,String,Any)
    pass
    
class ElixysComponentModel():
  def __init__(self,name):
    self.type = self.__class__.__name__
    self.name = name
  
  def run(self):
    print ('You called %s.%s.run()' % (self.name,self.__class__.__name__))
  def stop(self):
    print ('You called %s.%s.stop()' % (self.name,self.__class__.__name__))


class MotionModel(ElixysComponentModel):
  def __init__(self,name):
    ElixysComponentModel.__init__(self,name)
    
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
    
def test():
  x = ElixysSystemModel() #Create ESM Object
  x.buildSystemModel()    #Build System Model
  for key,value in x.SystemComponents.items(): #Print out built system model(pretty text)
      for item in value:
        print item
        for k,v in x.model[item].items():
          print '\t',k,":",v.__class__.__name__,'object'
  print '\nExample call, Reactor1 motion model:'
  print '\t',x.model['Reactor1']['Motion'] #Example of single object.
  x.model['Reactor1']['Motion'].run()
  x.model['Reactor1']['Motion'].stop()       
if __name__=="__main__":
    test()