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

    def RunSequenceFromComponent(self, sUsername, nSequenceID, nComponentID):
        return self.__pCoreServer.root.RunSequenceFromComponent(sUsername, nSequenceID, nComponentID)

    def PauseSequence(self, sUsername):
        return self.__pCoreServer.root.PauseSequence(sUsername)

    def ContinueSequence(self, sUsername):
        return self.__pCoreServer.root.ContinueSequence(sUsername)

    def AbortSequence(self, sUsername):
        return self.__pCoreServer.root.AbortSequence(sUsername)

    def WillSequencePause(self, sUsername):
        return self.__pCoreServer.root.WillSequencePause(sUsername)

    def IsSequencePaused(self, sUsername):
        return self.__pCoreServer.root.IsSequencePaused(sUsername)

    def DeliverUserInput(self, sUsername):
        return self.__pCoreServer.root.DeliverUserInput(sUsername)

    def PauseTimer(self, sUsername):
        return self.__pCoreServer.root.PauseTimer(sUsername)

    def ContinueTimer(self, sUsername):
        return self.__pCoreServer.root.ContinueTimer(sUsername)

    def StopTimer(self, sUsername):
        return self.__pCoreServer.root.StopTimer(sUsername)

    def CLIExecuteCommand(self, sUsername, sCommand):
        return self.__pCoreServer.root.CLIExecuteCommand(sUsername, sCommand)

    def CLISendCommand(self, sUsername, sCommand):
        return self.__pCoreServer.root.CLISendCommand(sUsername, sCommand)

    def CLIAbortUnitOperation(self, sUsername):
        return self.__pCoreServer.root.CLIAbortUnitOperation(sUsername)

    def CLIGetState(self, sUsername):
        return self.__pCoreServer.root.CLIGetState(sUsername)

