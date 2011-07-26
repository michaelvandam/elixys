"""Reagent Delivery Model

Reagent Delivery Model Class
"""

# Imports
import sys
sys.path.append("../hardware/")
from HardwareComm import HardwareComm
from ComponentModel import ComponentModel

# Reagent delivery model
class ReagentDeliveryModel(ComponentModel):
  def __init__(self, name, hardwareComm, modelLock):
    """Reagent delivery model constructor"""
    ComponentModel.__init__(self, name, hardwareComm, modelLock)
    self.setPositionReactor = 0
    self.setPositionReagent = 0
    self.setPositionDelivery = 0
    self.currentPositionReactor = 0
    self.currentPositionReagent = 0
    self.currentPositionDelivery = 0
    self.setPositionRawX = 0
    self.setPositionRawZ = 0
    self.currentPositionRawX = 0
    self.currentPositionRawZ = 0
    self.setGripperUp = False
    self.setGripperDown = False
    self.setGripperOpen = False
    self.setGripperClose = False

  def getAllowedReagentPositions(self):
    """Return a list of allowed reagent positions"""
    return [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

  def getAllowedDeliveryPositions(self):
    """Return a list of allowed delivery positions"""
    return [1, 2]

  def getSetPosition(self, bLockModel = True):
    """Return the set reagent robot position in the format (nReactor, nReagentPosition, nDeliveryPosition)"""
    return self.protectedReturn3(self.setPositionReactor, self.setPositionReagent, self.setPositionDelivery, bLockModel)

  def getSetPositionRaw(self, bLockModel = True):
    """Return the set raw reactor position in the format (X, Z)"""
    return self.protectedReturn2(self.setPositionRawX, self.setPositionRawZ, bLockModel)
    
  def getCurrentPosition(self, bLockModel = True):
    """Return the current reagent robot position in the format (nReactor, nReagentPosition, nDeliveryPosition)"""
    return self.protectedReturn3(self.currentPositionReactor, self.currentPositionReagent, self.currentPositionDelivery, bLockModel)
    
  def getCurrentPositionRaw(self, bLockModel = True):
    """Return the current raw reactor position in the format (X, Z)"""
    return self.protectedReturn2(self.currentPositionRawX, self.currentPositionRawZ, bLockModel)

  def getSetGripperUp(self, bLockModel = True):
    """Returns True if the gripper is set to up, False otherwise"""
    return self.protectedReturn(self.setGripperUp, bLockModel)

  def getSetGripperDown(self, bLockModel = True):
    """Returns True if the gripper is set to down, False otherwise"""
    return self.protectedReturn(self.setGripperDown, bLockModel)

  def getSetGripperOpen(self, bLockModel = True):
    """Returns True if the gripper is set to open, False otherwise"""
    return self.protectedReturn(self.setGripperOpen, bLockModel)

  def getSetGripperClose(self, bLockModel = True):
    """Returns True if the gripper is set to close, False otherwise"""
    return self.protectedReturn(self.setGripperClose, bLockModel)

  def moveToReagentPosition(self, nReactor, nReagentPosition):
    """Moves the reagent robot to the given reagent position"""
    self.hardwareComm.MoveRobotToReagent(nReactor, nReagentPosition)
    
  def moveToDeliveryPosition(self, nReactor, nDeliveryPosition):
    """Moves the reagent robot to the given delivery position"""
    self.hardwareComm.MoveRobotToDelivery(nReactor, nDeliveryPosition)

  def setGripperUp(self):
    """Raise the gripper"""
    self.hardwareComm.GripperUp()
    
  def setGripperDown(self):
    """Lower the gripper"""
    self.hardwareComm.GripperDown()

  def setGripperOpen(self):
    """Open the gripper"""
    self.hardwareComm.GripperOpen()

  def setGripperClose(self):
    """Close the gripper"""
    self.hardwareComm.GripperClose()

  def updateState(self, nSetPositionReactor, nSetPositionReagent, nSetPositionDelivery, nCurrentPositionReactor, nCurrentPositionReagent,
                  nCurrentPositionDelivery, nSetPositionRawX, nSetPositionRawZ, nCurrentPositionRawX, nCurrentPositionRawZ, bSetGripperUp,
                  bSetGripperDown, bSetGripperOpen, bSetGripperClose):
    """Updates the internal state"""
    self.setPositionReactor = nSetPositionReactor
    self.setPositionReagent = nSetPositionReagent
    self.setPositionDelivery = nSetPositionDelivery
    self.currentPositionReactor = nCurrentPositionReactor
    self.currentPositionReagent = nCurrentPositionReagent
    self.currentPositionDelivery = nCurrentPositionDelivery
    self.setPositionRawX = nSetPositionRawX
    self.setPositionRawZ = nSetPositionRawZ
    self.currentPositionRawX = nCurrentPositionRawX
    self.currentPositionRawZ = nCurrentPositionRawZ
    self.setGripperUp = bSetGripperUp
    self.setGripperDown = bSetGripperDown
    self.setGripperOpen = bSetGripperOpen
    self.setGripperClose = bSetGripperClose
