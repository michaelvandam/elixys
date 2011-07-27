""" Test.py

Test the Elixys hardware """

### Imports
from HardwareComm import HardwareComm
import time

def StateCallback(nR1T1, nR1T2, nR1T3, nR2T1, nR2T2, nR2T3, nR3T1, nR3T2, nR3T3):
    global nStartTime
    nCurrentTime = time.clock()
    print "%.1f, %i, %i, %i, %i, %i, %i, %i, %i, %i"%(nCurrentTime - nStartTime, nR1T1, nR1T2, nR1T3, nR2T1, nR2T2, nR2T3, nR3T1, nR3T2, nR3T3)

def StartHeat(pHardwareComm, nReactor, nTemperature):
    global nStartTime
    nStateTime = time.clock()
    pHardwareComm.HeaterOn(nReactor, 1)
    pHardwareComm.HeaterOn(nReactor, 2)
    pHardwareComm.HeaterOn(nReactor, 3)
    pHardwareComm.SetHeater(nReactor, 1, nTemperature)
    pHardwareComm.SetHeater(nReactor, 2, nTemperature)
    pHardwareComm.SetHeater(nReactor, 3, nTemperature)
    
def StopHeat(pHardwareComm, nReactor):
    pHardwareComm.SetHeater(nReactor, 1, 0)
    pHardwareComm.SetHeater(nReactor, 2, 0)
    pHardwareComm.SetHeater(nReactor, 3, 0)
    pHardwareComm.HeaterOff(nReactor, 1)
    pHardwareComm.HeaterOff(nReactor, 2)
    pHardwareComm.HeaterOff(nReactor, 3)

def Sleep(nSeconds):
    nCount = 0
    while nCount < nSeconds:
        pHardwareComm.UpdateState()
        time.sleep(1)
        nCount += 1

def Pause(sStep):
    raw_input(sStep)

if __name__ == "__main__":
    # Fire up an instance of the hardware comm layer
    nReactor = 1
    pHardwareComm = HardwareComm()
    pHardwareComm.StartUp()
    
    # Moving reactor to add
    print "1. Moving reactor " + str(nReactor) + " to add position"
    Pause("Move reactor")
    pHardwareComm.MoveReactor(nReactor, "Add")
    Pause("Reactor up")
    pHardwareComm.DisableReactorRobot(nReactor)
    pHardwareComm.ReactorUp(nReactor)
    time.sleep(0.1)
    pHardwareComm.ReactorUp(nReactor)
    Pause("Stop complete")

    # Elute F18
    print "3. Eluting F18"
    Pause("Open stopcocks")
    pHardwareComm.ReactorStopcockOpen(nReactor, 1)
    pHardwareComm.ReactorStopcockClose(nReactor, 2)
    Pause("Start eluting")
    pHardwareComm.EluteF18Start()
    Pause("Stop eluting")
    pHardwareComm.EluteF18Stop()
    Pause("Step complete")
    
    # Moving reactor to evaporate
    print "4. Moving reactor " + str(nReactor) + " to evaporate position"
    Pause("Reactor down")
    pHardwareComm.ReactorDown(nReactor)
    time.sleep(0.1)
    pHardwareComm.ReactorDown(nReactor)
    Pause("Enable robot")
    pHardwareComm.EnableReactorRobot(nReactor)
    Pause("Moev reactor")
    pHardwareComm.MoveReactor(nReactor, "Evaporate")
    Pause("Reactor up")
    pHardwareComm.DisableReactorRobot(nReactor)
    pHardwareComm.ReactorUp(nReactor)
    time.sleep(0.1)
    pHardwareComm.ReactorUp(nReactor)
    Pause("Step complete")
    
    # Evaporate
    print "5. Evaporating"
    Pause("Heating start")
    pHardwareComm.ReactorEvaporateStart(nReactor)
    StartHeat(pHardwareComm, nReactor, 165)
    pHardwareComm.SetMotorSpeed(nReactor, 500)
    #Sleep(600)
    Pause("Skipping sleep")
    pHardwareComm.ReactorEvaporateStop(nReactor)
    StopHeat(pHardwareComm, nReactor)
    pHardwareComm.SetMotorSpeed(nReactor, 0)
    pHardwareComm.CoolingSystemOn()
    #Sleep(100)
    Pause("Skipping sleep")
    pHardwareComm.CoolingSystemOff()
    Pause("Step complete")
    
    # Moving reactor to add
    print "2. Moving reactor " + str(nReactor) + " to add position"
    Pause("Reactor down")
    pHardwareComm.ReactorDown(nReactor)
    time.sleep(0.1)
    pHardwareComm.ReactorDown(nReactor)
    Pause("Enable robot")
    pHardwareComm.EnableReactorRobot(nReactor)
    Pause("Move reactor")
    pHardwareComm.MoveReactor(nReactor, "Add")
    Pause("Reactor up")
    pHardwareComm.DisableReactorRobot(nReactor)
    pHardwareComm.ReactorUp(nReactor)
    time.sleep(0.1)
    pHardwareComm.ReactorUp(nReactor)
    Pause("Step complete")

    # Add reagent
    print "6. Adding reagent"
    Pause("Gripper up")
    pHardwareComm.GripperUp()
    time.sleep(0.1)
    pHardwareComm.GripperUp()
    Pause("Gripper open")
    pHardwareComm.GripperOpen()
    time.sleep(0.1)
    pHardwareComm.GripperOpen()
    Pause("Moving robot")
    pHardwareComm.MoveRobotToReagent(nReactor, 1)
    Pause("Gripper down")
    pHardwareComm.GripperDown()
    time.sleep(0.1)
    pHardwareComm.GripperDown()
    Pause("Gripper close")
    pHardwareComm.GripperClose()
    time.sleep(0.1)
    pHardwareComm.GripperClose()
    Pause("Gripper up")
    pHardwareComm.GripperUp()
    time.sleep(0.1)
    pHardwareComm.GripperUp()
    Pause("Moving robot")
    pHardwareComm.MoveRobotToDelivery(nReactor, 1)
    Pause("Gripper down")
    pHardwareComm.GripperDown()
    time.sleep(0.1)
    pHardwareComm.GripperDown()
    Pause("Transfer start")
    pHardwareComm.ReactorReagentTransferStart(nReactor, 1)
    Pause("Transfer stop")
    pHardwareComm.ReactorReagentTransferStop(nReactor, 1)
    Pause("Gripper up")
    pHardwareComm.GripperUp()
    time.sleep(0.1)
    pHardwareComm.GripperUp()
    Pause("Moving robot")
    pHardwareComm.MoveRobotToReagent(nReactor, 1)
    Pause("Gripper down")
    pHardwareComm.GripperDown()
    time.sleep(0.1)
    pHardwareComm.GripperDown()
    Pause("Gripper open")
    pHardwareComm.GripperOpen()
    time.sleep(0.1)
    pHardwareComm.GripperOpen()
    Pause("Gripper up")
    pHardwareComm.GripperUp()
    time.sleep(0.1)
    pHardwareComm.GripperUp()
    Pause("Move robot")
    pHardwareComm.MoveRobotToReagent(3, 3)
    Pause("Step complete")

    # Moving reactor to react1
    print "7. Moving reactor " + str(nReactor) + " to react position"
    Pause("Reactor down")
    pHardwareComm.ReactorDown(nReactor)
    time.sleep(0.1)
    pHardwareComm.ReactorDown(nReactor)
    Pause("Enable robot")
    pHardwareComm.EnableReactorRobot(nReactor)
    Pause("Move reactor")
    pHardwareComm.MoveReactor(nReactor, "React1")
    Pause("Reactor up")
    pHardwareComm.DisableReactorRobot(nReactor)
    pHardwareComm.ReactorUp(nReactor)
    time.sleep(0.1)
    pHardwareComm.ReactorUp(nReactor)
    Pause("Step complete")
    
    # React
    print "8. Reacting"
    Pause("Starting to heat")
    StartHeat(pHardwareComm, nReactor, 105)
    pHardwareComm.SetMotorSpeed(nReactor, 500)
    #Sleep(600)
    Pause("Skipping sleep")
    StopHeat(pHardwareComm, nReactor)
    pHardwareComm.SetMotorSpeed(nReactor, 0)
    pHardwareComm.CoolingSystemOn()
    #Sleep(100)
    Pause("Skipping sleep")
    pHardwareComm.CoolingSystemOff()
    Pause("Step complete")

    # Moving reactor to transfer
    print "9. Moving reactor " + str(nReactor) + " to transfer position"
    Pause("Reactor down")
    pHardwareComm.ReactorDown(nReactor)
    time.sleep(0.1)
    pHardwareComm.ReactorDown(nReactor)
    Pause("Enable robot")
    pHardwareComm.EnableReactorRobot(nReactor)
    Pause("Moving reactor")
    pHardwareComm.MoveReactor(nReactor, "Transfer")
    Pause("Reactor up")
    pHardwareComm.DisableReactorRobot(nReactor)
    pHardwareComm.ReactorUp(nReactor)
    time.sleep(0.1)
    pHardwareComm.ReactorUp(nReactor)
    Pause("Step complete")

    # Transfer
    print "10. Transfer"
    Pause("Start transfer")
    pHardwareComm.ReactorTransferStart(nReactor)
    Pause("Stop transfer")
    pHardwareComm.ReactorTransferStop(nReactor)
    Pause("Step complete")

    # Moving reactor to install
    print "11. Moving reactor " + str(nReactor) + " to install position"
    Pause("Reactor down")
    pHardwareComm.ReactorDown(nReactor)
    time.sleep(0.1)
    pHardwareComm.ReactorDown(nReactor)
    Pause("Enable robot")
    pHardwareComm.EnableReactorRobot(nReactor)
    Pause("Moving reactor")
    pHardwareComm.MoveReactor(nReactor, "Install")
    Pause("Reactor up")
    pHardwareComm.DisableReactorRobot(nReactor)
    pHardwareComm.ReactorUp(nReactor)
    time.sleep(0.1)
    pHardwareComm.ReactorUp(nReactor)
    Pause("Step complete")
    
    # Done!
    pHardwareComm.ShutDown()
