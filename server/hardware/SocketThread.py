""" SocketThread.py

Socket thread class spawned by HardwareComm """

### Imports
import socket
import threading
import select
import Queue

class SocketThread(threading.Thread):
    ### Functions ###

    # Set parameters
    def SetParameters(self, sPLCIP, nPLCPort, pHardwareComm, pTerminateEvent):
        # Remember the parameters
        self.__sPLCIP = sPLCIP
        self.__nPLCPort = nPLCPort
        self.__nServerPort = 9601
        self.__pHardwareComm = pHardwareComm
        self.__pTerminateEvent = pTerminateEvent

        # Create our outgoing packet queue
        self.__pOutgoingPackets = Queue.Queue()

    # Send packet
    def SendPacket(self, sBinaryPacket):
        # Add the packet to our queue
        self.__pOutgoingPackets.put(sBinaryPacket)

    # Thread function
    def run(self):
        # Create a socket connection to the PLC
        pSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        pSocket.setblocking(0)
        pSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        pSocket.bind(("", self.__nServerPort))
        pSockets = [pSocket]

        # Loop until the terminate event is set
        while not self.__pTerminateEvent.is_set():
            # Call select() to wait until the socket is ready
            if self.__pOutgoingPackets.empty():
                pReadySockets = select.select(pSockets, [], [], 0.05)
            else:
                pReadySockets = select.select(pSockets, pSockets, [], 0.05)
            if len(pReadySockets[0]) > 0:
                # The socket has data available to be read.  Pass the data to the HardwareComm for processing
                pBinaryResponse = pSocket.recv(10240)
                sResponse = pBinaryResponse.encode("hex")
                self.__pHardwareComm._HardwareComm__ProcessRawResponse(sResponse)
            elif len(pReadySockets[1]) > 0:
                # The socket is available for writing.  Do we have any packets in our outgoing queue?
                if not self.__pOutgoingPackets.empty():
                   # Yes, so pop the next one off and send it
                   pSocket.sendto(self.__pOutgoingPackets.get(), (self.__sPLCIP, self.__nPLCPort))

        # Close the socket connection
        pSocket.close()
        pSocket = None
        return
