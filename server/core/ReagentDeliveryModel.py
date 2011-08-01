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
    self.robotXStatus = 0
    self.robotZStatus = 0

  def getAllowedReagentPositions(self):
    """Return a list of allowed reagent positions"""
    return [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

  def getAllowedDeliveryPositions(self):
    """Return a list of allowed delivery positions"""
    return [1, 2]

  def getSetPosition(self, bLockModel = True):
    """Return the set reagent robot position in the format (nReactor, nReagentPosition, nDeliveryPosition)"""
    if bLockModel:
      return self.protectedReturn3(self.getSetPosition)
    else:
      return self.setPositionReactor, self.setPositionReagent, self.setPositionDelivery

  def getSetPositionRaw(self, bLockModel = True):
    """Return the set raw reactor position in the format (X, Z)"""
    if bLockModel:
      return self.protectedReturn2(self.getSetPositionRaw)
    else:
      return self.setPositionRawX, self.setPositionRawZ
    
  def getCurrentPosition(self, bLockModel = True):
    """Return the current reagent robot position in the format (nReactor, nReagentPosition, nDeliveryPosition)"""
    if bLockModel:
      return self.protectedReturn3(self.getCurrentPosition)
    else:
      return self.currentPositionReactor, self.currentPositionReagent, self.currentPositionDelivery
    
  def getCurrentPositionRaw(self, bLockModel = True):
    """Return the current raw reactor position in the format (X, Z)"""
    if bLockModel:
      return self.protectedReturn2(self.getCurrentPositionRaw)
    else:
      return self.currentPositionRawX, self.currentPositionRawZ

  def getSetGripperUp(self, bLockModel = True):
    """Returns True if the gripper is set to up, False otherwise"""
    if bLockModel:
      return self.protectedReturn1(self.getSetGripperUp)
    else:
      return self.setGripperUp

  def getSetGripperDown(self, bLockModel = True):
    """Returns True if the gripper is set to down, False otherwise"""
    if bLockModel:
      return self.protectedReturn1(self.getSetGripperDown)
    else:
      return self.setGripperDown

  def getSetGripperOpen(self, bLockModel = True):
    """Returns True if the gripper is set to open, False otherwise"""
    if bLockModel:
      return self.protectedReturn1(self.getSetGripperOpen)
    else:
      return self.setGripperOpen

  def getSetGripperClose(self, bLockModel = True):
    """Returns True if the gripper is set to close, False otherwise"""
    if bLockModel:
      return self.protectedReturn1(self.getSetGripperClose)
    else:
      return self.setGripperClose

  def getRobotStatus(self, bLockModel = True):
    """Returns the robot axis status code"""
    if bLockModel:
      return self.protectedReturn2(self.getRobotXStatus)
    else:
      return self.robotXStatus, self.robotZStatus
      
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
                  bSetGripperDown, bSetGripperOpen, bSetGripperClose, nRobotXStatus, nRobotZStatus):
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
    self.robotXStatus = nRobotXStatus
    self.robotZStatus = nRobotZStatus
