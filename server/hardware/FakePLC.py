""" FakePLC.py

Behaves like a PLC for testing and demo purposes """

### Imports
import socket
import configobj
from HardwareComm import HardwareComm

# Handle the read command
def HandleRead(sPacket):
    # Global variables
    global nMemoryLower
    global nMemoryUpper
    global pMemory
    global pSocket

    # Make sure the message is long enough
    if len(sPacket) != 36:
        print "Invalid packet length"
        return

    # We only read bytes
    if sPacket[24:26] != "b0":
        print "Invalid I/O memory area code"
        return

    # Determine the read offset and length
    nReadOffsetByte = int(sPacket[26:30], 16)
    nReadLength = int(sPacket[32:36], 16)

    # Create the response
    sResponse = "0000000000000000000001010000"
    for nOffset in range(nMemoryLower, nMemoryUpper + 1):
        if nOffset >= nReadOffsetByte:
            # Stop when complete
            if nOffset > (nReadOffsetByte + nReadLength):
                break

            # Append the next byte of data
            sResponse += ("%0.4X" % pMemory[nOffset - nMemoryLower])

    # Send the response
    pBinaryResponse = sResponse.decode("hex")
    pSocket.sendto(pBinaryResponse, ("127.0.0.1", 9601))
    print "Sent read response packet"

# Handle the write command
def HandleWrite(sPacket):
    # Global variables
    global nMemoryLower
    global nMemoryUpper
    global pMemory
    global pSocket

    # Make sure the message is long enough
    if len(sPacket) < 36:
        print "Invalid packet length"
        return

    # Determine the write offsets and length
    nReadOffsetByte = int(sPacket[26:30], 16)
    nReadOffsetBit = int(sPacket[30:32], 16)
    nReadLength = int(sPacket[32:36], 16)

    # Validate range
    if (nReadOffsetByte < nMemoryLower) or ((nReadOffsetByte + nMemoryLower) >= nMemoryUpper):
        print "Invalid byte offset"
        return
    if nReadOffsetBit > 7:
        print "Invalid bit offset"
        return

    # Are we writing bits or bytes?
    if sPacket[24:26] == "30":
        # Bits.  I'm only writing this for a single bit at this time.  Check the lengths
        if nReadLength != 1:
            print "Implement multibit writing if needed"
            return
        if len(sPacket) != 38:
            print "Invalid packet length"
            return

        # Extract the boolean value
        bValue = (sPacket[37] == "0")

        # Update the target bit
        pMemory[nReadOffsetByte] = pMemory[nReadOffsetByte] | (bValue << nReadOffsetBit)
    elif sPacket[24:26] == "b0":
        # Bytes
        print "Implement byte writing if needed"
    else:
        print "Invalid I/O memory area code"
        return

    # Send a success packet
    sResponse = "0000000000000000000001020000"
    pBinaryResponse = sResponse.decode("hex")
    pSocket.sendto(pBinaryResponse, ("127.0.0.1", 9601))
    print "Wrote data and sent response packet"

# Fill the buffer from the file containing a dump of the actual PLC memory
def FillMemoryBuffer():
    # Global variables
    global nMemoryLower
    global nMemoryUpper
    global pMemory
    
    # Open the PLC memory file
    pMemoryFile = open("PLC_MEM.MEM", "r")
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
            if (nOffset >= nMemoryLower) and (nOffset <= nMemoryUpper):
                pMemory[nOffset - nMemoryLower] = nValue
        
    # Clean up
    pMemoryFile.close()

# Main CLI function
if __name__ == "__main__":
    # Global variables
    global nMemoryLower
    global nMemoryUpper
    global pMemory
    global pSocket

    # Determine the memory range we need to emulate
    pHardwareComm = HardwareComm()
    nMemoryLower, nMemoryUpper = pHardwareComm._HardwareComm__CalculateMemoryRange()
    
    # Create and fill the memory buffer
    pMemory = []
    for x in range(nMemoryLower, nMemoryUpper + 1):
        pMemory.append(0)
    FillMemoryBuffer()
    
    # Create the socket
    pSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    pSocket.bind(("", 9600))

    # Packet processing loop
    while True:
        # Listen for a packet
        print "Listening for packet..."
        pBinaryPacket = pSocket.recv(1024)
        sPacket = pBinaryPacket.encode("hex")
        print "Received packet: " + sPacket

        # Handle read and write messages
        if sPacket[20:24] == "0101":
            HandleRead(sPacket)
        elif sPacket[20:24] == "0102":
            HandleWrite(sPacket)
        else:
            print "Unknown command, ignoring"

    # Here is where we would close the socket if there was a way to exit
    pSocket.close()
    pSocket = None
