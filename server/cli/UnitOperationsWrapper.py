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
        pReact.start()

    def Add(self, nReactor, nReagentReactor, nReagentPosition, nReagentDeliveryPosition):
        """Performs an add unit operation"""
        pParams = {"ReactorID":nReactor,
                   "ReagentReactorID":nReagentReactor,
                   "ReagentPosition":nReagentPosition,
                   "reagentLoadPosition":nReagentDeliveryPosition}
        print "Skipping add unit operation"
#        pAdd = UnitOperations.AddReagent(self.__pSystemModel, pParams)
#        pAdd.start()

    def Evaporate(self, nReactor, nEvaporationTemperature, nEvaporationTime, nFinalTemperature, nStirSpeed):
        """Performs an evaporation unit operation"""
        pParams = {"ReactorID":nReactor,
                   "reactTemp":nEvaporationTemperature,
                   "reactTime":nEvaporationTime,
                   "coolTemp":nFinalTemperature,
                   "stirSpeed":nStirSpeed}
        print "Skipping evaporate unit operation"
#        pEvaporate = UnitOperations.Evaporate(self.__pSystemModel, pParams)
#        pEvaporate.start()

    def Install(self, nReactor):
        """Performs an install unit operation"""
        pParams = {"ReactorID":nReactor}
        print "Skipping install unit operation"
#        pInstall = UnitOperations.InstallVial(self.__pSystemModel, pParams)
#        pInstall.start()
        
    def TransferToHPLC(self, nReactor, nStopcockPosition):
        """Performs a transfer to HPLC unit operation"""
        pParams = {"ReactorID":nReactor,
                   "stopcockPosition":nStopcockPosition}
        print "Skipping transfer to HPLC unit operation"
#        pTransfer = UnitOperations.TransferToHPLC(self.__pSystemModel, pParams)
#        pTransfer.start()

    def TransferElute(self, nReactor, nStopcockPosition):
        """Performs a transfer elute unit operation"""
        pParams = {"ReactorID":nReactor,
                   "stopcockPosition":nStopcockPosition}
        print "Skipping transfer elute unit operation"
#        pTransfer = UnitOperations.TransferElute(self.__pSystemModel, pParams)
#        pTransfer.start()
        
    def Transfer(self, nReactor, nStopcockPosition, nTransferReactorID):
        """Performs a transfer elute unit operation"""
        pParams = {"ReactorID":nReactor,
                   "stopcockPosition":nStopcockPosition,
                   "transferReactorID":nTransferReactorID}
        print "Skipping transfer unit operation"
#        pTransfer = UnitOperations.Transfer(self.__pSystemModel, pParams)
#        pTransfer.start()

    def UserInput(self, sUserMessage, bIsCheckBox, sDescription):
        """Performs a user input unit operation"""
        pParams = {"userMessage":sUserMessage,
                   "isCheckbox":bIsCheckBox,
                   "description":sDescription}
        print "Skipping user input unit operation"
#        pUserInput = UnitOperations.UserInput(self.__pSystemModel, pParams)
#        pUserInput.start()

    def DetectRadiation(self):
        """Performs a radiation detection unit operation"""
        pParams = {}
        print "Skipping detect radiation unit operation"
 #       pDetectRadiation = UnitOperations.DetectRadiation(self.__pSystemModel, pParams)
 #       pDetectRadiation.start()
