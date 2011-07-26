"""Component Model

Component Model Base Class
"""

# Imports
import sys
sys.path.append("../hardware/")
from HardwareComm import HardwareComm

# Component model base class
class ComponentModel():
  def __init__(self, name, hardwareComm):
    """ComponentModel base class constructor"""
    self.type = self.__class__.__name__
    self.name = name
    self.hardwareComm = hardwareComm
