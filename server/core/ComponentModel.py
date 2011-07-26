"""Component Model

Component Model Base Class
"""

# Imports
import sys
sys.path.append("../hardware/")
from HardwareComm import HardwareComm

# Component model base class
class ComponentModel():
  def __init__(self, name, hardwareComm, modelLock):
    """ComponentModel base class constructor"""
    self.type = self.__class__.__name__
    self.name = name
    self.hardwareComm = hardwareComm
    self.modelLock = modelLock

  def protectedReturn(self, pVariable, bLockModel):
    """Returns the value of the variable as protected by the model lock"""
    if bLockModel:
      self.modelLock.acquire()
    pReturn = pVariable
    if bLockModel:
      self.modelLock.release()
    return pReturn

  def protectedReturn2(self, pVariable1, pVariable2, bLockModel):
    """Returns the value of the variables as protected by the model lock"""
    if bLockModel:
      self.modelLock.acquire()
    pReturn1 = pVariable1
    pReturn2 = pVariable2
    if bLockModel:
      self.modelLock.release()
    return pReturn1, pReturn2

  def protectedReturn3(self, pVariable1, pVariable2, pVariable3, bLockModel):
    """Returns the value of the variables as protected by the model lock"""
    if bLockModel:
      self.modelLock.acquire()
    pReturn1 = pVariable1
    pReturn2 = pVariable2
    pReturn3 = pVariable3
    if bLockModel:
      self.modelLock.release()
    return pReturn1, pReturn2, pReturn3
