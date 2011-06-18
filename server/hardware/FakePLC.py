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
    nOffset = nMemoryLower
    for nOffset in range(nMemoryLower, nMemoryUpper):
        if nOffset >= nReadOffsetByte:
            # Stop when complete
            if nOffset >= (nReadOffsetByte + nReadLength):
                break

            # Append the next byte of data
            sResponse += ("%0.2X" % pMemory[nOffset - nMemoryLower])

    # Send the response
    pBinaryResponse = sResponse.decode("hex")
    pSocket.sendto(pBinaryResponse, ("127.0.0.1", 9600))
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
        pass
    else:
        print "Invalid I/O memory area code"
        return

    # Send a success packet
    sResponse = "0000000000000000000001020000"
    pBinaryResponse = sResponse.decode("hex")
    pSocket.sendto(pBinaryResponse, ("127.0.0.1", 9600))
    print "Wrote data and sent response packet"

# Main CLI function
if __name__ == "__main__":
    # Global variables
    global nMemoryLower
    global nMemoryUpper
    global pMemory
    global pSocket

    # Determine the memory range we need to emulate
    pHardwareComm = HardwareComm()
    sMemoryRange = pHardwareComm._HardwareComm__DetermineMemoryRange()
    pMemoryRangeComponents = sMemoryRange.split(",")
    nMemoryLower = int(pMemoryRangeComponents[0])
    nMemoryUpper = int(pMemoryRangeComponents[1])

    # Create the memory buffer
    pMemory = []
    for x in range(nMemoryLower, nMemoryUpper):
        pMemory.append(0)

    # Create the socket
    pSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    pSocket.bind(("", 9601))

    # Packet processing loop
    while True:
        # Listen for a packet
        print ""
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


#192.168.251.1
#9600

#Byte:
#Read:  0101 80 0020 00 0001
#Write: 0102 80 0001 00 0001 FFFF
#               Addr    qty  data
#               byte bit

#Bit:
#Write: 0102 30 000F 03 0001 01 

#0101800020000001
