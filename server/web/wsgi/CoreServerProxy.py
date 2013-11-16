"""CoreServer

A proxy to the Python service that communicates with the PLC"""

# Imports
import rpyc
import json

# Core server proxy
class CoreServerProxy():
    def __init__(self):
        self.__pCoreServer = None

    def Connect(self):
        try:
            self.__pCoreServer = rpyc.connect("localhost", 18862)
            return True
        except Exception, ex:
            print "## Failed to connect to core server"
            self.__pCoreServer = None
            return False

    def GetServerState(self, sUsername):
        try:
            if self.__pCoreServer != None:
                pGetServerState = self.__pCoreServer.root.GetServerState(sUsername)
                if pGetServerState["success"]:
                    return json.loads(pGetServerState["return"])
        except Exception, ex:
            print "## Failed to get server state"
            pass
        return None
    
        try:
            if self.__pCoreServer != None:
                pGetHardwareState = self.__pCoreServer.root.GetHardwareState()
                return pGetHardwareState
        except Exception, ex:
            print "## Failed to get server state"
            pass
        return None

    def RunSequence(self, sUsername, nSequenceID):
        pRunSequence = self.__pCoreServer.root.RunSequence(sUsername, nSequenceID)
        if not pRunSequence["success"]:
            raise Exception("Core server failed to run sequence")

    def RunSequenceFromComponent(self, sUsername, nSequenceID, nComponentID):
        pRunSequenceFromComponent = self.__pCoreServer.root.RunSequenceFromComponent(sUsername, nSequenceID, nComponentID)
        if not pRunSequenceFromComponent["success"]:
            raise Exception("Core server failed to run sequence from component")

    def PauseSequence(self, sUsername):
        pPauseSequence = self.__pCoreServer.root.PauseSequence(sUsername)
        if not pPauseSequence["success"]:
            raise Exception("Core server failed to pause sequence")

    def ContinueSequence(self, sUsername):
        pContinueSequence = self.__pCoreServer.root.ContinueSequence(sUsername)
        if not pContinueSequence["success"]:
            raise Exception("Core server failed to continue sequence")

    def ShowAbortSequencePrompt(self, sUsername, bShowAbortPrompt):
        pShowAbortSequencePrompt = self.__pCoreServer.root.ShowAbortSequencePrompt(sUsername, bShowAbortPrompt)
        if not pShowAbortSequencePrompt["success"]:
            raise Exception("Core server failed to show abort sequence prompt")

    def AbortSequence(self, sUsername):
        pAbortSequence = self.__pCoreServer.root.AbortSequence(sUsername)
        if not pAbortSequence["success"]:
            raise Exception("Core server failed to abort sequence")

    def WillSequencePause(self, sUsername):
        pWillSequencePause = self.__pCoreServer.root.WillSequencePause(sUsername)
        if pWillSequencePause["success"]:
            return pWillSequencePause["return"]
        else:
            raise Exception("Core server failed to return will sequence pause flag")

    def IsSequencePaused(self, sUsername):
        pIsSequencePaused = self.__pCoreServer.root.IsSequencePaused(sUsername)
        if pIsSequencePaused["success"]:
            return pIsSequencePaused["return"]
        else:
            raise Exception("Core server failed to return is sequence paused flag")

    def OverrideTimer(self, sUsername):
        pOverrideTimer = self.__pCoreServer.root.OverrideTimer(sUsername)
        if not pOverrideTimer["success"]:
            raise Exception("Core server failed to override timer")

    def StopTimer(self, sUsername):
        pStopTimer = self.__pCoreServer.root.StopTimer(sUsername)
        if not pStopTimer["success"]:
            raise Exception("Core server failed to stop timer")

    def CheckSoftError(self, sUsername):
        pCheckSoftError = self.__pCoreServer.root.CheckSoftError(sUsername)
        if pCheckSoftError["success"]:
            return pCheckSoftError["return"]
        else:
            raise Exception("Core server failed to check soft error")

    def SetSoftErrorDecision(self, sUsername, sDecision):
        pSetSoftErrorDecision = self.__pCoreServer.root.SetSoftErrorDecision(sUsername, sDecision)
        if not pSetSoftErrorDecision["success"]:
            raise Exception("Core server failed to set soft error decision")

    def DeliverUserInput(self, sUsername):
        pDeliverUserInput = self.__pCoreServer.root.DeliverUserInput(sUsername)
        if not pDeliverUserInput["success"]:
            raise Exception("Core server failed to deliver user input")

    def CLIExecuteCommand(self, sUsername, sCommand):
        return self.__pCoreServer.root.CLIExecuteCommand(sUsername, sCommand)

    def CLISendCommand(self, sUsername, sCommand):
        return self.__pCoreServer.root.CLISendCommand(sUsername, sCommand)

    def CLIAbortUnitOperation(self, sUsername):
        return self.__pCoreServer.root.CLIAbortUnitOperation(sUsername)

    def CLIGetState(self, sUsername):
        return self.__pCoreServer.root.CLIGetState(sUsername)

    def CLIBroadcast(self, sUsername, sMessage):
        return self.__pCoreServer.root.CLIBroadcast(sUsername, sMessage)

