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
    
    while (1):
        pHardwareComm.ReactorStopcockOpen("1","1")
        pHardwareComm.ReactorStopcockOpen("1","2")
        pHardwareComm.ReactorStopcockOpen("1","3")
        time.sleep(3)
        pHardwareComm.ReactorStopcockClose("1","1")
        pHardwareComm.ReactorStopcockClose("1","2")
        pHardwareComm.ReactorStopcockClose("1","3")
        time.sleep(3)

    # Clean up the hardware comm layer
    pHardwareComm.ShutDown()
