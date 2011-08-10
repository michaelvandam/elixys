""" UnitOperationsWrapper.py

Implements an wrapper around the unit operations class for use by the CLI interface"""

### Imports
import sys
sys.path.append("../core/")
import UnitOperations

class UnitOperationsWrapper:
    def __init__(self, pSystemModel):
        """Unit operations wrapper constructor"""
        self.__pSystemModel = pSystemModel
    
    def Init(self):
        """Initializes Elixys hardware for use"""
        pParams = {}
        pInit = UnitOperations.Initialize(self.__pSystemModel)
        pInit.setDaemon(True)
        pInit.start()
        return pInit

    def TempProfile(self, nReactor, nReactionTemperature):
        """Performs a react unit operation, with a 15 minute heating cycle"""
        pParams = {"ReactorID":nReactor,
                   "reactTemp":nReactionTemperature}
        pTempProfile = UnitOperations.TempProfile(self.__pSystemModel, pParams)
        pTempProfile.setDaemon(True)
        pTempProfile.start()
        return pTempProfile
       
    def React(self, nReactor, nReactionTemperature, nReactionTime, nFinalTemperature, nReactPosition, nStirSpeed):
        """Performs a react unit operation"""
        pParams = {"ReactorID":nReactor,
                   "reactTemp":nReactionTemperature,
                   "reactTime":nReactionTime,
                   "coolTemp":nFinalTemperature,
                   "reactPosition":nReactPosition,
                   "stirSpeed":nStirSpeed}
        print "Starting react unit operation"
        pReact = UnitOperations.React(self.__pSystemModel, pParams)
        pReact.setDaemon(True)
        pReact.start()
        return pReact

      

    def Add(self, nReactor, nReagentReactor, nReagentPosition, nReagentDeliveryPosition):
        """Performs an add unit operation"""
        pParams = {"ReactorID":nReactor,
                   "ReagentReactorID":nReagentReactor,
                   "ReagentPosition":nReagentPosition,
                   "reagentLoadPosition":nReagentDeliveryPosition}
        print "Starting add unit operation"
        pAdd = UnitOperations.AddReagent(self.__pSystemModel, pParams)
        pAdd.setDaemon(True)
        pAdd.start()
        return pAdd


    def Evaporate(self, nReactor, nEvaporationTemperature, nEvaporationTime, nFinalTemperature, nStirSpeed):
        """Performs an evaporation unit operation"""
        pParams = {"ReactorID":nReactor,
                   "evapTemp":nEvaporationTemperature,
                   "evapTime":nEvaporationTime,
                   "coolTemp":nFinalTemperature,
                   "stirSpeed":nStirSpeed}
        print "Starting evaporate unit operation"
        pEvaporate = UnitOperations.Evaporate(self.__pSystemModel, pParams)
        pEvaporate.setDaemon(True)
        pEvaporate.start()
        return pEvaporate

    def Install(self, nReactor):
        """Performs an install unit operation"""
        pParams = {"ReactorID":nReactor}
        print "Starting install unit operation"
        pInstall = UnitOperations.InstallVial(self.__pSystemModel, pParams)
        pInstall.setDaemon(True)
        pInstall.start()
        return pInstall

    def TransferToHPLC(self, nReactor, nStopcockPosition):
        """Performs a transfer to HPLC unit operation"""
        pParams = {"ReactorID":nReactor,
                   "stopcockPosition":nStopcockPosition}
        print "Starting transfer to HPLC unit operation"
        pTransfer = UnitOperations.TransferToHPLC(self.__pSystemModel, pParams)
        pTransfer.setDaemon(True)
        pTransfer.start()
        return pTransfer

    def TransferElute(self, nReactor, nStopcockPosition):
        """Performs a transfer elute unit operation"""
        pParams = {"ReactorID":nReactor,
                   "stopcockPosition":nStopcockPosition}
        print "Starting transfer elute unit operation"
        pTransfer = UnitOperations.TransferElute(self.__pSystemModel, pParams)
        pTransfer.setDaemon(True)
        pTransfer.start()
        return pTransfer
      
    def Transfer(self, nReactor, nStopcockPosition, nTransferReactorID):
        """Performs a transfer elute unit operation"""
        pParams = {"ReactorID":nReactor,
                   "stopcockPosition":nStopcockPosition,
                   "transferReactorID":nTransferReactorID}
        print "Starting transfer unit operation"
        pTransfer = UnitOperations.Transfer(self.__pSystemModel, pParams)
        pTransfer.setDaemon(True)
        pTransfer.start()
        return pTransfer

    def UserInput(self, sUserMessage, bIsCheckBox, sDescription):
        """Performs a user input unit operation"""
        pParams = {"userMessage":sUserMessage,
                   "isCheckbox":bIsCheckBox,
                   "description":sDescription}
        print "Starting user input unit operation"
        pUserInput = UnitOperations.UserInput(self.__pSystemModel, pParams)
        pUserInput.setDaemon(True)
        pUserInput.start()
        return pUserInput

    def DetectRadiation(self):
        """Performs a radiation detection unit operation"""
        pParams = {}
        print "Starting detect radiation unit operation"
        pDetectRadiation = UnitOperations.DetectRadiation(self.__pSystemModel, pParams)
        pDetectRadiation.setDaemon(True)
        pDetectRadiation.start()
        return pDetectRadiation
