""" FakePLC.py

Behaves like a PLC for testing and demo purposes """

### Imports
import socket
import configobj
import select
import sys
sys.path.append("../../hardware/")
sys.path.append("../../core/")
sys.path.append("../../cli/")
from HardwareComm import HardwareComm
from SystemModel import SystemModel
import Utilities
from CoolingThread import CoolingThread
from PressureRegulatorThread import PressureRegulatorThread
from MoveReagentRobotThread import MoveReagentRobotThread
from MoveReactorLinearThread import MoveReactorLinearThread
from MoveReactorVerticalThread import MoveReactorVerticalThread
from HeatingThread import HeatingThread

# Fake PLC class
class FakePLC():
    def __init__(self):
        """Fake PLC class constructor"""
        # Initialize variables
        self.__pCoolingThread = None
        self.__pPressureRegulator1Thread = None
        self.__pPressureRegulator2Thread = None
        self.__pMoveReagentRobotThread = None
        self.__pReactor1LinearMovementThread = None
        self.__pReactor2LinearMovementThread = None
        self.__pReactor3LinearMovementThread = None
        self.__pReactor1VerticalMovementThread = None
        self.__pReactor2VerticalMovementThread = None
        self.__pReactor3VerticalMovementThread = None
        self.__pReactor1HeatingThread = None
        self.__pReactor2HeatingThread = None
        self.__pReactor3HeatingThread = None
        
    def StartUp(self):
        """Starts up the fake PLC"""
        # Create the hardware layer
        self.__pHardwareComm = HardwareComm("../../hardware/")
  
        # Determine the memory range we need to emulate
        self.__nMemoryLower, self.__nMemoryUpper = self.__pHardwareComm.CalculateMemoryRange()

        # Create and fill the memory buffer with zeros
        self.__pMemory = []
        for x in range(self.__nMemoryLower, self.__nMemoryUpper + 1):
            self.__pMemory.append(0)
            
        # Fill the memory buffer from the PLC memory dump
        self.__FillMemoryBuffer("PLC.MEM")

        # Pass a reference to the memory buffer to the HardwareComm so we can read from it and write to it at a higher level
        self.__pHardwareComm.FakePLC_SetMemory(self.__pMemory, self.__nMemoryLower, self.__nMemoryUpper)
        
        # Create the system model
        self.__pSystemModel = SystemModel(self.__pHardwareComm)
        self.__pSystemModel.StartUp()

        # Create the socket
        self.__pSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.__pSocket.setblocking(False)
        self.__pSocket.bind(("", 9600))
        
        # Create the utilities class
        self.__pUtilities = Utilities.Utilities()
            
    def Run(self):
        """Runs the fake PLC"""
        # Packet processing loop
        print "Listening for packets (press q to quit)..."
        while True:
            # Check if the user pressed 'q' to quit
            if self.__pUtilities.CheckForQuit():
                return
        
            # Check socket availability
            pRead, pWrite, pError = select.select([self.__pSocket], [], [], 0.25)
            for pReadable in pRead:
                if pReadable == self.__pSocket:
                    # Data is available for receiving
                    pBinaryPacket = self.__pSocket.recv(1024)
                    sPacket = pBinaryPacket.encode("hex")
                    print "Received packet: " + sPacket

                    # Check the message length
                    if len(sPacket) >= 36:
                        # Handle read and write messages
                        if sPacket[20:24] == "0101":
                            self.__HandleRead(sPacket)
                        elif sPacket[20:24] == "0102":
                            self.__HandleWrite(sPacket)
                        else:
                            print "Unknown command, ignoring"
                    else:
                        print "Packet too short, discarding"
            
            # Update the state of the PLC
            self.__UpdatePLC()

    def ShutDown(self):
        """Shuts down the fake PLC"""
        # Clean up
        self.__pSocket.close()
        self.__pSocket = None
        self.__pSystemModel.ShutDown()

    def __FillMemoryBuffer(self, sFilename):
        """Fill the buffer from the file containing a dump of the actual PLC memory"""
        # Open the PLC memory file
        pMemoryFile = open(sFilename, "r")
        pMemoryFileLines = pMemoryFile.readlines()
    
        # Search for the CIO memory
        sCIO = None
        for sLine in pMemoryFileLines:
            if sLine.startswith("CIO="):
                sCIO = sLine
                break
    
        # Handle error
        if sCIO == None:
            raise Exception("Failed to find CIO memory")
    
        # Trim off the "CIO=" string and split into components
        sCIO = sCIO[4:]
        pCIO = sCIO.split(",")
    
        # Fill the memory
        for pComponent in pCIO:
            # Extract the memory range
            sRange = pComponent.split(":")[0]
            pRangeComponents = sRange.split("-")
            nRangeStart = int(pRangeComponents[0])
            if len(pRangeComponents) > 1:
                nRangeEnd = int(pRangeComponents[1])
            else:
                nRangeEnd = nRangeStart
            
            # Extract the value
            nValue = int(pComponent.split(":")[1], 16)
        
            # Fill in the memory array
            for nOffset in range(nRangeStart, nRangeEnd + 1):
                if (nOffset >= self.__nMemoryLower) and (nOffset <= self.__nMemoryUpper):
                    self.__pMemory[nOffset - self.__nMemoryLower] = nValue
        
        # Clean up
        pMemoryFile.close()

    def __HandleRead(self, sPacket):
        """Handle the read command"""
        # We only read words
        if sPacket[24:26] != "b0":
            print "Invalid I/O memory area code"
            return

        # Determine the read offset and length
        nReadOffsetWord = int(sPacket[26:30], 16)
        nReadLength = int(sPacket[32:36], 16)
        
        # Read the memory
        sMemory = self.__pHardwareComm.FakePLC_ReadMemory(nReadOffsetWord, nReadLength)

        # Create and send the response
        sResponse = "0000000000000000000001010000" + sMemory
        pBinaryResponse = sResponse.decode("hex")
        self.__pSocket.sendto(pBinaryResponse, ("127.0.0.1", 9601))
        print "Sent read response packet"

    def __HandleWrite(self, sPacket):
        """Handle the write command"""
        # Determine the write offsets and length
        nWriteOffsetWord = int(sPacket[26:30], 16)
        nWriteOffsetBit = int(sPacket[30:32], 16)
        nWriteLength = int(sPacket[32:36], 16)

        # Are we writing bits or bytes?
        if sPacket[24:26] == "30":
            # Bits.  We're only writing this for a single bit at this time
            if nWriteLength != 1:
                print "Implement multibit writing if needed"
                return
                
            # Verify the packet length
            if len(sPacket) != 38:
                print "Invalid packet length"
                return

            # Extract the boolean value
            bValue = (sPacket[37] == "1")

            # Set the target bit
            self.__pHardwareComm.FakePLC_SetBinaryValue(nWriteOffsetWord, nWriteOffsetBit, bValue)
        elif sPacket[24:26] == "b0":
            # Bytes.  We're only writing this for a single byte at this time
            if nWriteLength != 1:
                print "Implement multibyte writing if needed"
                return
                
            # Verify the packet length
            if len(sPacket) != 40:
                print "Invalid packet length"
                return

            # Extract the integer value
            nValue = int(sPacket[36:40], 0x10)

            # Set the target word
            self.__pHardwareComm.FakePLC_SetWordValue(nWriteOffsetWord, nValue)
        else:
            print "Invalid I/O memory area code"
            return

        # Send a success packet
        sResponse = "0000000000000000000001020000"
        pBinaryResponse = sResponse.decode("hex")
        self.__pSocket.sendto(pBinaryResponse, ("127.0.0.1", 9601))
        print "Wrote data and sent response packet"

    def __UpdatePLC(self):
        """Updates the PLC in response to any changes to system changes"""
        # Update the various system components
        self.__UpdateVacuumPressure()
        self.__UpdateCoolingSystem()
        self.__UpdatePressureRegulator(1)
        self.__UpdatePressureRegulator(2)
        self.__UpdateCoolingSystem()
        self.__UpdateReagentRobotPosition()
        self.__UpdateReactorPosition(1)
        self.__UpdateReactorPosition(2)
        self.__UpdateReactorPosition(3)
        self.__UpdateReactorHeating(1)
        self.__UpdateReactorHeating(2)
        self.__UpdateReactorHeating(3)

    def __UpdateVacuumPressure(self):
        """Updates the vacuum pressure in response to system changes"""
        # Get the current state of the vacuum valves and vacuum pressure
        nEvaporationValvesOpen = 0
        if self.__pSystemModel.model["Reactor1"]["Valves"].getEvaporationVacuumValveOpen():
            nEvaporationValvesOpen += 1
        if self.__pSystemModel.model["Reactor2"]["Valves"].getEvaporationVacuumValveOpen():
            nEvaporationValvesOpen += 1
        if self.__pSystemModel.model["Reactor3"]["Valves"].getEvaporationVacuumValveOpen():
            nEvaporationValvesOpen += 1
        nActualPressure = self.__pSystemModel.model["VacuumSystem"].getVacuumSystemPressure()

        # Calculate the target vacuum pressure
        if nEvaporationValvesOpen == 0:
            nTargetPressure = -71.6
        elif nEvaporationValvesOpen == 1:
            nTargetPressure = -12.4
        elif nEvaporationValvesOpen == 2:
            nTargetPressure = -8.1
        else:
            nTargetPressure = -5.9
        
        # Compare the pressures.  Add leeway to account for rounding errors
        if ((nActualPressure + 1) < nTargetPressure) or ((nActualPressure - 1) > nTargetPressure):
            # Update the actual pressure to the target pressure
            self.__pHardwareComm.FakePLC_SetVacuumPressure(nTargetPressure)
            
    def __UpdateCoolingSystem(self):
        """Updates the cooling system in response to system changes"""
        # Check if the cooling system is on
        bCoolingSystemOn = self.__pSystemModel.model["CoolingSystem"].getCoolingSystemOn()
        if bCoolingSystemOn:
            # Yes.  Check if the cooling thread is running
            if (self.__pCoolingThread == None) or not self.__pCoolingThread.is_alive():
                # No, so kill any running heating threads
                if (self.__pReactor1HeatingThread != None) and self.__pReactor1HeatingThread.is_alive():
                    self.__pReactor1HeatingThread.Stop()
                    self.__pReactor1HeatingThread.join()
                if (self.__pReactor2HeatingThread != None) and self.__pReactor2HeatingThread.is_alive():
                    self.__pReactor2HeatingThread.Stop()
                    self.__pReactor2HeatingThread.join()
                if (self.__pReactor3HeatingThread != None) and self.__pReactor3HeatingThread.is_alive():
                    self.__pReactor3HeatingThread.Stop()
                    self.__pReactor3HeatingThread.join()
 
                # Kick off the cooling thread
                nReactor1CurrentTemperature = self.__pSystemModel.model["Reactor1"]["Thermocouple"].getCurrentTemperature(False)
                nReactor2CurrentTemperature = self.__pSystemModel.model["Reactor2"]["Thermocouple"].getCurrentTemperature(False)
                nReactor3CurrentTemperature = self.__pSystemModel.model["Reactor3"]["Thermocouple"].getCurrentTemperature(False)
                self.__pCoolingThread = CoolingThread()
                self.__pCoolingThread.SetParameters(self.__pHardwareComm, nReactor1CurrentTemperature, nReactor2CurrentTemperature, nReactor3CurrentTemperature)
                self.__pCoolingThread.start()
        else:
            # No, so kill the cooling thread if it is running
            if (self.__pCoolingThread != None) and self.__pCoolingThread.is_alive():
                self.__pCoolingThread.Stop()
                self.__pCoolingThread.join()
        
    def __UpdatePressureRegulator(self, nPressureRegulator):
        """Updates the pressure regulator in response to system changes"""
        # Get the set and actual pressures
        nSetPressure = self.__pSystemModel.model["PressureRegulator" + str(nPressureRegulator)].getSetPressure()
        nActualPressure = self.__pSystemModel.model["PressureRegulator" + str(nPressureRegulator)].getCurrentPressure()

        # Compare the pressures.  Add leeway to account for rounding errors
        if ((nActualPressure + 1) < nSetPressure) or ((nActualPressure - 1) > nSetPressure):
            # Get a reference to the pressure regulator thread
            if nPressureRegulator == 1:
                pThread = self.__pPressureRegulator1Thread
            else:
                pThread = self.__pPressureRegulator2Thread

            # Check if the pressure regulator thread is running
            if (pThread == None) or not pThread.is_alive():
                # No, so kick off the thread
                pThread = PressureRegulatorThread()
                pThread.SetParameters(self.__pHardwareComm, nPressureRegulator, nActualPressure, nSetPressure)
                pThread.start()
                
                # Save the new reference
                if nPressureRegulator == 1:
                    self.__pPressureRegulator1Thread = pThread
                else:
                    self.__pPressureRegulator2Thread = pThread

    def __UpdateReagentRobotPosition(self):
        """Updates the reagent robot position in response to system changes"""
        # Get the set and actual positions
        nReagentRobotSetPositionRawX, nReagentRobotSetPositionRawZ = self.__pSystemModel.model["ReagentDelivery"].getSetPositionRaw()
        nReagentRobotActualPositionRawX, nReagentRobotActualPositionRawZ = self.__pSystemModel.model["ReagentDelivery"].getCurrentPositionRaw()

        # Compare the positions.  Add leeway to account for motor positioning errors
        if ((nReagentRobotSetPositionRawX + 5) < nReagentRobotActualPositionRawX) or ((nReagentRobotSetPositionRawX - 5) > nReagentRobotActualPositionRawX) or \
           ((nReagentRobotSetPositionRawZ + 5) < nReagentRobotActualPositionRawZ) or ((nReagentRobotSetPositionRawZ - 5) > nReagentRobotActualPositionRawZ):
            # Check if the reagent robot movement thread is running
            if (self.__pMoveReagentRobotThread == None) or not self.__pMoveReagentRobotThread.is_alive():
                # No, so kick off the thread
                self.__pMoveReagentRobotThread = MoveReagentRobotThread()
                self.__pMoveReagentRobotThread.SetParameters(self.__pHardwareComm, nReagentRobotActualPositionRawX, nReagentRobotActualPositionRawZ, \
                    nReagentRobotSetPositionRawX, nReagentRobotSetPositionRawZ)
                self.__pMoveReagentRobotThread.start()

    def __UpdateReactorPosition(self, nReactor):
        """Updates the reactor position in response to system changes"""
        # Get the set and actual linear positions
        nReactorSetPositionZ = self.__pSystemModel.model["Reactor" + str(nReactor)]["Motion"].getSetPositionRaw()
        nReactorActualPositionZ = self.__pSystemModel.model["Reactor" + str(nReactor)]["Motion"].getCurrentPositionRaw()

        # Compare the linear positions.  Add leeway to account for motor positioning errors
        if ((nReactorSetPositionZ + 5) < nReactorActualPositionZ) or ((nReactorSetPositionZ - 5) > nReactorActualPositionZ):
            # Get a reference to the reactor linear movement thread
            if nReactor == 1:
                pThread = self.__pReactor1LinearMovementThread
            elif nReactor == 2:
                pThread = self.__pReactor2LinearMovementThread
            else:
                pThread = self.__pReactor3LinearMovementThread

            # Check if the reactor linear movement thread is running
            if (pThread == None) or not pThread.is_alive():
                # No, so kick off the thread
                pThread = MoveReactorLinearThread()
                pThread.SetParameters(self.__pHardwareComm, nReactor, nReactorActualPositionZ, nReactorSetPositionZ)
                pThread.start()
                
                # Save the new reference
                if nReactor == 1:
                    self.__pReactor1LinearMovementThread = pThread
                elif nReactor == 2:
                    self.__pReactor2LinearMovementThread = pThread
                else:
                    self.__pReactor3LinearMovementThread = pThread

        # Get the set and actual vertical positions
        bReactorSetUp = self.__pSystemModel.model["Reactor" + str(nReactor)]["Motion"].getSetReactorUp()
        bReactorSetDown = self.__pSystemModel.model["Reactor" + str(nReactor)]["Motion"].getSetReactorDown()
        bReactorActualUp = self.__pSystemModel.model["Reactor" + str(nReactor)]["Motion"].getCurrentReactorUp()
        bReactorActualDown = self.__pSystemModel.model["Reactor" + str(nReactor)]["Motion"].getCurrentReactorDown()
            
        # Compare the vertical positions
        if (bReactorSetUp != bReactorActualUp) or (bReactorSetDown != bReactorActualDown):
            # Get a reference to the reactor vertical movement thread
            if nReactor == 1:
                pThread = self.__pReactor1VerticalMovementThread
            elif nReactor == 2:
                pThread = self.__pReactor2VerticalMovementThread
            else:
                pThread = self.__pReactor3VerticalMovementThread

            # Check if the reactor linear movement thread is running
            if (pThread == None) or not pThread.is_alive():
                # No, so kick off the thread
                pThread = MoveReactorVerticalThread()
                pThread.SetParameters(self.__pHardwareComm, nReactor, bReactorSetUp)
                pThread.start()
                
                # Save the new reference
                if nReactor == 1:
                    self.__pReactor1VerticalMovementThread = pThread
                elif nReactor == 2:
                    self.__pReactor2VerticalMovementThread = pThread
                else:
                    self.__pReactor3VerticalMovementThread = pThread
        
    def __UpdateReactorHeating(self, nReactor):
        """Updates the reactor heating in response to system changes"""
        # Check if the heater is on
        bHeaterOn = self.__pSystemModel.model["Reactor" + str(nReactor)]["Thermocouple"].getHeaterOn()
        if bHeaterOn:
            # Yes.  Check if the cooling system is on and return if it is
            bCoolingSystemOn = self.__pSystemModel.model["CoolingSystem"].getCoolingSystemOn()
            if bCoolingSystemOn:
                return

            # Get the set and actual temperatures
            nReactorSetTemperature = self.__pSystemModel.model["Reactor" + str(nReactor)]["Thermocouple"].getSetTemperature()
            nReactorActualTemperature = self.__pSystemModel.model["Reactor" + str(nReactor)]["Thermocouple"].getCurrentTemperature()

            # Compare the temperatures to see if we need to turn on the heater.  Add leeway to account for small variations
            if (nReactorSetTemperature + 2) > nReactorActualTemperature:
                # Get a reference to the heating thread
                if nReactor == 1:
                    pThread = self.__pReactor1HeatingThread
                elif nReactor == 2:
                    pThread = self.__pReactor2HeatingThread
                else:
                    pThread = self.__pReactor3HeatingThread

                # Check if the heating thread is running
                if (pThread == None) or not pThread.is_alive():
                    # No, so kick off the thread
                    pThread = HeatingThread()
                    pThread.SetParameters(self.__pHardwareComm, nReactor, nReactorActualTemperature, nReactorSetTemperature)
                    pThread.start()
                
                    # Save the new reference
                    if nReactor == 1:
                        self.__pReactor1HeatingThread = pThread
                    elif nReactor == 2:
                        self.__pReactor2HeatingThread = pThread
                    else:
                        self.__pReactor3HeatingThread = pThread
        else:
            # No, so kill the heating thread if it is running
            if nReactor == 1:
                pThread = self.__pReactor1HeatingThread
            elif nReactor == 2:
                pThread = self.__pReactor2HeatingThread
            else:
                pThread = self.__pReactor3HeatingThread
            if (pThread != None) and pThread.is_alive():
                pThread.Stop()
                pThread.join()
        
# Main entry function
if __name__ == "__main__":
    # Create the fake PLC and run
    pFakePLC = FakePLC()
    pFakePLC.StartUp()
    pFakePLC.Run()
    pFakePLC.ShutDown()
    