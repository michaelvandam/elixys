""" FakePLC.py

Behaves like a PLC for testing and demo purposes """

### Imports
import socket
import select
import configobj
from HardwareComm import HardwareComm

# Handle the read command
def HandleRead(sPacket):
    # Global variables
    global nMemoryLower
    global nMemoryUpper
    global pMemory

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
    pSocket.sendto(pBinaryResponse, ("127.0.0.1", 9601))
    print "Sent read response packet"

# Handle the write command
def HandleWrite(sPacket):
    # Global variables
    global nMemoryLower
    global nMemoryUpper
    global pMemory

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

    # Calculate the memory range we need to emulate
    pHardwareComm = HardwareComm()
    nMemoryLower, nMemoryUpper = pHardwareComm._HardwareComm__CalculateMemoryRange()

    # Create the memory buffer
    pMemory = []
    for x in range(nMemoryLower, nMemoryUpper):
        pMemory.append(0)

    # Create the socket
    pListeningSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    pListeningSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) 
    pListeningSocket.bind(("", 9600))

    # Listen for an incoming socket connection
    pSocket = None
    pListeningSocket.listen(1)

    # Processing loop
    while True:
        # Create a socket array
        if pSocket != None:
            pSocketList = [pListeningSocket, pSocket]
        else:
            pSocketList = [pListeningSocket]
            print "Listening for incoming socket connection..."

        # Wait from one of our socket objects to be available
        pReadList, pWriteList, pErrorList = select.select(pSocketList, pSocketList, [])
        for pReadSocket in pReadList:
            if pReadSocket is pListeningSocket:
                # A new socket connection is available
                pSocket, pAddress = pListeningSocket.accept()
                print "Socket connections received from " + str(pAddress)
            else:
                # Our socket connection has data waiting to be read
                pBinaryPacket = pSocket.recv(1024)
                if pBinaryPacket == "":
                    # Socket connection dropped
                    pSocket.close()
                    pSocket = None
                    print "Socket connection closed"
                    print ""
                else:
                    # Encode and log the packet
                    sPacket = pBinaryPacket.encode("hex")
                    print "Received packet: " + sPacket

                    # Handle read and write messages
                    if sPacket[20:24] == "0101":
                        HandleRead(sPacket)
                    elif sPacket[20:24] == "0102":
                        HandleWrite(sPacket)
                    else:
                        print "Unknown command, ignoring"
        for pWriteSocket in pWriteList:
            # Our socket connection is available for writing data
            pass
