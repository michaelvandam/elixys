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
    pHardwareComm.GripperOpen()
    pHardwareComm.GripperUp()
    time.sleep(0.5)
    random.seed()
    
    while True:
        nReactor = random.randint(1, 3)
        nPosition = random.randint(1, 12)
        if nPosition <= 10:
            pHardwareComm.MoveRobotToReagent(str(nReactor), str(nPosition))
        else:
            pHardwareComm.MoveRobotToDelivery(str(nReactor), str(nPosition - 10))
        time.sleep(0.5);

    # Clean up the hardware comm layer
    pHardwareComm.ShutDown()
