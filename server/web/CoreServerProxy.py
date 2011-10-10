"""CoreServer

A proxy to the Python service that communicates with the PLC"""

# Imports
import rpyc
import copy

# Core server proxy
class CoreServerProxy():
    def __init__(self):
        self.__pCoreServer = rpyc.connect("localhost", 18862)

    def GetServerState(self, sUsername):
        return copy.deepcopy(self.__pCoreServer.root.GetServerState(sUsername))

    def exposed_RunSequence(self, sUsername, nSequenceID):
        return self.__pCoreServer.root.RunSequence(sUsername, nSequenceID)

    def exposed_Abort(self, sUsername):
        return self.__pCoreServer.root.Abort(sUsername)

    def exposed_EmergencyStop(self, sUsername):
        return self.__pCoreServer.root.EmergencyStop(sUsername)

    def exposed_Pause(self, sUsername):
        return self.__pCoreServer.root.Pause(sUsername)

    def exposed_Continue(self, sUsername):
        return self.__pCoreServer.root.Continue(sUsername)

    def exposed_PauseTimer(self, sUsername):
        return self.__pCoreServer.root.PauseTimer(sUsername)

    def exposed_ContinueTimer(self, sUsername):
        return self.__pCoreServer.root.ContinueTimer(sUsername)

    def exposed_StopTimer(self, sUsername):
        return self.__pCoreServer.root.StopTimer(sUsername)

