""" Test.py

Test the Elixys hardware """

### Imports
from HardwareComm import HardwareComm
import time

def StateCallback(nR1T1, nR1T2, nR1T3, nR2T1, nR2T2, nR2T3, nR3T1, nR3T2, nR3T3):
    global nStartTime
    nCurrentTime = time.clock()
    sState = "%.1f, %i, %i, %i, %i, %i, %i, %i, %i, %i"%(nCurrentTime - nStartTime, nR1T1, nR1T2, nR1T3, nR2T1, nR2T2, nR2T3, nR3T1, nR3T2, nR3T3)
    pFile = open('C:\\Elixys\\tempprofile.txt', 'a')
    pFile.write(sState + "\n")
    pFile.close()
    print sState
    
if __name__ == "__main__":
    # Fire up an instance of the hardware comm layer
    sReactor = "3"
    pHardwareComm = HardwareComm()
    pHardwareComm.StartUp()

    # Get the run start time
    global nStartTime
    nStartTime = time.clock()
    
    # Set the state callback and get 30 seconds worth of baseline
    pHardwareComm.SetStateCallback(StateCallback)
    nCount = 0
    while nCount < 30:
        pHardwareComm.UpdateState()
        time.sleep(1)
        nCount += 1
    
    # Turn on the heaters
    pHardwareComm.HeaterOn(sReactor, "1")
    pHardwareComm.HeaterOn(sReactor, "2")
    pHardwareComm.HeaterOn(sReactor, "3")
    pHardwareComm.SetHeater(sReactor, "1", "165")
    pHardwareComm.SetHeater(sReactor, "2", "165")
    pHardwareComm.SetHeater(sReactor, "3", "165")
    
    # Wait for the reactor to heat
    nCount = 0
    while nCount < 600:
        pHardwareComm.UpdateState()
        time.sleep(1)
        nCount += 1

    # Turn off the heaters
    pHardwareComm.SetHeater(sReactor, "1", "0")
    pHardwareComm.SetHeater(sReactor, "2", "0")
    pHardwareComm.SetHeater(sReactor, "3", "0")
    pHardwareComm.HeaterOff(sReactor, "1")
    pHardwareComm.HeaterOff(sReactor, "2")
    pHardwareComm.HeaterOff(sReactor, "3")
    pHardwareComm.CoolingSystemOn()

    # Wait for the reactor to cool
    nCount = 0
    while nCount < 200:
        pHardwareComm.UpdateState()
        time.sleep(1)
        nCount += 1

    # Clean up the hardware comm layer
    pHardwareComm.CoolingSystemOff()
    pHardwareComm.ShutDown()
