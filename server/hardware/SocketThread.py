""" SocketThread.py

Socket thread class spawned by HardwareComm """

### Imports
import socket
import threading
import select
import Queue
# Import loging capabilities
import logging.config
import logging
import traceback

logging.config.fileConfig("/opt/elixys/config/elixyslog.conf")
log = logging.getLogger("elixys.hw")
log.debug("Starting Socket Thread -- Socket Thread")

# This exception will be thrown in a runaway heater is detected
class RunawayHeaterException(Exception):
    pass

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
        self.__sError = ""

        # Create our outgoing packet queue
        self.__pOutgoingPackets = Queue.Queue()

    # Send packet
    def SendPacket(self, sBinaryPacket):
        # Add the packet to our queue
        self.__pOutgoingPackets.put(sBinaryPacket)

    # Returns any error
    def GetError(self):
        return self.__sError

    # Thread function
    def run(self):
        log.debug("Starting a socket thread run")
        try:
            # Create a socket connection to the PLC
            pSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            pSocket.setblocking(0)
            pSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            pSocket.bind(("", self.__nServerPort))
            pSockets = [pSocket]

            # Loop until the terminate event is set
            bRunawayHeater = False
            while not self.__pTerminateEvent.is_set():
                # Raise an exception if a runaway heater was detected
                # and we've sent all our outgoing packets
                if bRunawayHeater and self.__pOutgoingPackets.empty():
                    log.error("Runaway Heater detected and all Packets were sent out.")
                    raise Exception(sRunawayHeaterError)

                # Call select() to wait until the socket is ready
                if self.__pOutgoingPackets.empty():
                    pReadySockets = select.select(pSockets, [], [], 0.05)
                else:
                    pReadySockets = select.select(pSockets, pSockets, [], 0.05)
                if len(pReadySockets[0]) > 0:
                    # The socket has data available to be read.
                    # Pass the data to the HardwareComm for processing
                    log.debug("Reading Socket Thread packets")
                    pBinaryResponse = pSocket.recv(10240)
                    sResponse = pBinaryResponse.encode("hex")
                    try:
                        self.__pHardwareComm._HardwareComm__ProcessRawResponse(sResponse)
                    except RunawayHeaterException, ex:
                        # A runaway heater has been detected.
                        # We need to run the message pump a bit longer
                        # so the queued heater stop commands can be sent.
                        log.error("Caught exception: Runaway Heater was detected.\
                                    Queued the stop heater commands.")
                        log.error("Exception: %s" %ex)
                        bRunawayHeater = True
                        sRunawayHeaterError = "Runaway heater in reactor " + str(ex.args[0])
                elif len(pReadySockets[1]) > 0:
                    # The socket is available for writing.
                    # Do we have any packets in our outgoing queue?
                    if not self.__pOutgoingPackets.empty():
                        log.debug("Writing Socket Thread packets")
                        # Yes, so pop the next one off and send it
                        pSocket.sendto(self.__pOutgoingPackets.get(),
                                    (self.__sPLCIP, self.__nPLCPort))

            # Close the socket connection
            pSocket.close()
            pSocket = None
            log.debug("Finished socket thread session")
        except Exception, ex:
            log.error("Exception caught in Socket Thread: %s" % ex)
            log.error("Traceback:\r\n%s\r\n" % traceback.format_exc())
            self.__sError = str(ex)
