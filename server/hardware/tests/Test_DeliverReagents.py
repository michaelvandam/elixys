""" Test.py

Test the Elixys hardware """

### Imports
from HardwareComm import HardwareComm
import time
import random

if __name__ == "__main__":
    # Fire up an instance of the hardware comm layer
    pHardwareComm = HardwareComm()
    pHardwareComm.StartUp()
    pHardwareComm.SetPressureRegulator("1","59")
    time.sleep(0.25)
    pHardwareComm.SetPressureRegulator("2","25")
    time.sleep(0.25)
    pHardwareComm.GripperOpen()
    time.sleep(0.25)
    pHardwareComm.GripperUp()
    time.sleep(0.25)
    random.seed()

    # Move and raise the reactor
    sCommand = raw_input("Press enter to go")
    pHardwareComm.ReactorDown("1")
    sCommand = raw_input("Press enter to go")
    pHardwareComm.MoveReactor("1","Add")
    sCommand = raw_input("Press enter to go")
    pHardwareComm.ReactorUp("1")

    # Load reagent (1,1) to delivery (1,2)
    sCommand = raw_input("Press enter to go")
    pHardwareComm.MoveRobotToReagent("1","1")
    sCommand = raw_input("Press enter to go")
    pHardwareComm.GripperDown()
    sCommand = raw_input("Press enter to go")
    pHardwareComm.GripperClose()
    sCommand = raw_input("Press enter to go")
    pHardwareComm.GripperUp()
    sCommand = raw_input("Press enter to go")
    pHardwareComm.MoveRobotToDelivery("1","2")
    sCommand = raw_input("Press enter to go")
    pHardwareComm.GripperDown()
    sCommand = raw_input("Press enter to go")
    pHardwareComm.ReactorReagentTransferStart("1", "2")
    sCommand = raw_input("Press enter to go")
    pHardwareComm.ReactorReagentTransferStop("1", "2")

    # Return reagent to source position
    sCommand = raw_input("Press enter to go")
    pHardwareComm.GripperUp()
    sCommand = raw_input("Press enter to go")
    pHardwareComm.MoveRobotToReagent("1","1")
    sCommand = raw_input("Press enter to go")
    pHardwareComm.GripperDown()
    sCommand = raw_input("Press enter to go")
    pHardwareComm.GripperOpen()
    sCommand = raw_input("Press enter to go")
    pHardwareComm.GripperUp()
    
    # Load reagent (1,8) to delivery (1,1)
    sCommand = raw_input("Press enter to go")
    pHardwareComm.MoveRobotToReagent("1","8")
    sCommand = raw_input("Press enter to go")
    pHardwareComm.GripperDown()
    sCommand = raw_input("Press enter to go")
    pHardwareComm.GripperClose()
    sCommand = raw_input("Press enter to go")
    pHardwareComm.GripperUp()
    sCommand = raw_input("Press enter to go")
    pHardwareComm.MoveRobotToDelivery("1","1")
    sCommand = raw_input("Press enter to go")
    pHardwareComm.GripperDown()
    sCommand = raw_input("Press enter to go")
    pHardwareComm.ReactorReagentTransferStart("1", "1")
    sCommand = raw_input("Press enter to go")
    pHardwareComm.ReactorReagentTransferStop("1", "1")

    # Return reagent to source position
    sCommand = raw_input("Press enter to go")
    pHardwareComm.GripperUp()
    sCommand = raw_input("Press enter to go")
    pHardwareComm.MoveRobotToReagent("1","8")
    sCommand = raw_input("Press enter to go")
    pHardwareComm.GripperDown()
    sCommand = raw_input("Press enter to go")
    pHardwareComm.GripperOpen()
    sCommand = raw_input("Press enter to go")
    pHardwareComm.GripperUp()

    # Move robot out of the way
    sCommand = raw_input("Press enter to go")
    pHardwareComm.MoveRobotToReagent("3","3")
    sCommand = raw_input("Press enter to go")

    # Clean up the hardware comm layer
    pHardwareComm.ShutDown()
