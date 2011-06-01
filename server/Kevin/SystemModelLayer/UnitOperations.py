"""Unit operations

Elixys Unit Operations
"""
class UnitOperation:
  def __init__(self):
    pass
  def logError():
    """Get current error from hardware comm."""
    #error.log(blahblahblah)
    pass
  def run(self):
    for step in self.steps:
      exec("self."+step)
  def resume(self):
    pass
  def pause(self):
    pass
  def abort():
    pass
  def getTotalSteps(self):
    return self.steps #Integer

  def isRunning():
    pass
  def getCurrentStepNumber():
    pass
  def getCurrentStepName():
    pass
  def setParam(name,value): #(String,Any)
    pass
  def getParam(name): #String
    return param #Any
    
  def moveTo(self,position):
    print position
  def heat(self,temp,time,cooltemp):
    print temp,time,cooltemp
class Evaporate(UnitOperation):
  def __init__(self):
    UnitOperation.__init__(self)
    self.steps = 8#Down->Evap_Position->Seal->Ramp N2->Vac_On->Heat_On(Temp)->Timer->Cool(Temp)
    self.currentStep=""
class React(UnitOperation):
  def __init__(self):
    UnitOperation.__init__(self)
    
    self.steps = ['moveTo(\'position1\')','heat(\'400C\',\'2min\',\'40C\')'] #Make sure we can still see steps
    #self.steps = 6#Down->React_Position(1 or 2)->Seal->Heat_On(Temp)->Timer->Cool(Temp)


def test():
  react1 = React()
  react1.run()

    
if __name__=="__main__":
    test()