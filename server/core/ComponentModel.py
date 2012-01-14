"""Component Model

Component Model Base Class
"""

# Imports
import sys
sys.path.append("/opt/elixys/hardware/")
from HardwareComm import HardwareComm

# Component model base class
class ComponentModel():
  def __init__(self, name, hardwareComm, modelLock):
    """ComponentModel base class constructor"""
    self.type = self.__class__.__name__
    self.name = name
    self.hardwareComm = hardwareComm
    self.modelLock = modelLock

  def protectedReturn1(self, pGetFunction):
    """Returns the value of the variable as protected by the model lock"""
    self.modelLock.Acquire()
    pReturn1 = pGetFunction(False)
    self.modelLock.Release()
    return pReturn1

  def protectedReturn2(self, pGetFunction):
    """Returns the value of the variables as protected by the model lock"""
    self.modelLock.Acquire()
    pReturn1, pReturn2 = pGetFunction(False)
    self.modelLock.Release()
    return pReturn1, pReturn2

  def protectedReturn3(self, pGetFunction):
    """Returns the value of the variables as protected by the model lock"""
    self.modelLock.Acquire()
    pReturn1, pReturn2, pReturn3 = pGetFunction(False)
    self.modelLock.Release()
    return pReturn1, pReturn2, pReturn3

  def protectedReturn4(self, pGetFunction):
    """Returns the value of the variables as protected by the model lock"""
    self.modelLock.Acquire()
    pReturn1, pReturn2, pReturn3, pReturn4 = pGetFunction(False)
    self.modelLock.Release()
    return pReturn1, pReturn2, pReturn3, pReturn4

