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

# Fake PLC class
class FakePLC():
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

# Main entry function
if __name__ == "__main__":
    # Create the fake PLC and run
    pFakePLC = FakePLC()
    pFakePLC.StartUp()
    pFakePLC.Run()
    pFakePLC.ShutDown()
    