"""CoreServer

A proxy to the Python service that communicates with the PLC"""

# Imports
import rpyc
import json

# Core server proxy
class CoreServerProxy():
    def __init__(self):
        self.__pCoreServer = rpyc.connect("localhost", 18862)

    def GetServerState(self, sUsername):
        return json.loads(self.__pCoreServer.root.GetServerState(sUsername))

    def RunSequence(self, sUsername, nSequenceID):
        return self.__pCoreServer.root.RunSequence(sUsername, nSequenceID)

    def Abort(self, sUsername):
        return self.__pCoreServer.root.Abort(sUsername)

    def EmergencyStop(self, sUsername):
        return self.__pCoreServer.root.EmergencyStop(sUsername)

    def Pause(self, sUsername):
        return self.__pCoreServer.root.Pause(sUsername)

    def Continue(self, sUsername):
        return self.__pCoreServer.root.Continue(sUsername)

    def PauseTimer(self, sUsername):
        return self.__pCoreServer.root.PauseTimer(sUsername)

    def ContinueTimer(self, sUsername):
        return self.__pCoreServer.root.ContinueTimer(sUsername)

    def StopTimer(self, sUsername):
        return self.__pCoreServer.root.StopTimer(sUsername)

    def CLIConnectToStateMonitor(self, sUsername):
        return self.__pCoreServer.root.CLIConnectToStateMonitor(sUsername)

    def CLIExecuteCommand(self, sUsername, sCommand):
        return self.__pCoreServer.root.CLIExecuteCommand(sUsername, sCommand)

    def CLISendCommand(self, sUsername, sCommand):
        return self.__pCoreServer.root.CLISendCommand(sUsername, sCommand)

    def CLIGetState(self, sUsername):
        return self.__pCoreServer.root.CLIGetState(sUsername)

    def CLIAbortUnitOperation(self, sUsername):
        return self.__pCoreServer.root.CLIAbortUnitOperation(sUsername)

