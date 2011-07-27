""" Test.py

Test the Elixys hardware """

### Imports
from HardwareComm import HardwareComm
import time

if __name__ == "__main__":
    # Fire up an instance of the hardware comm layer
    pHardwareComm = HardwareComm()
    pHardwareComm.StartUp();
    pHardwareComm.ClearRobotErrors()
    pHardwareComm.HomeRobots()
    time.sleep(3)
    
    while True:
        pHardwareComm.MoveReactor("1","Install")
        pHardwareComm.MoveReactor("2","Install")
        pHardwareComm.MoveReactor("3","Install")
        time.sleep(3);
        pHardwareComm.MoveReactor("1","Transfer")
        pHardwareComm.MoveReactor("2","Transfer")
        pHardwareComm.MoveReactor("3","Transfer")
        time.sleep(1);
        pHardwareComm.MoveReactor("1","React1")
        pHardwareComm.MoveReactor("2","React1")
        pHardwareComm.MoveReactor("3","React1")
        time.sleep(1);
        pHardwareComm.MoveReactor("1","Add")
        pHardwareComm.MoveReactor("2","Add")
        pHardwareComm.MoveReactor("3","Add")
        time.sleep(1);
        pHardwareComm.MoveReactor("1","React2")
        pHardwareComm.MoveReactor("2","React2")
        pHardwareComm.MoveReactor("3","React2")
        time.sleep(1);
        pHardwareComm.MoveReactor("1","Evaporate")
        pHardwareComm.MoveReactor("2","Evaporate")
        pHardwareComm.MoveReactor("3","Evaporate")
        time.sleep(1);

    # Clean up the hardware comm layer
    pHardwareComm.ShutDown()
