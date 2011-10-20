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

    ###
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
        pReact = UnitOperations.React(self.__pSystemModel, pParams)
        pReact.setDaemon(True)
        pReact.start()
        return pReact

    def Move(self, nReactor, nReactPosition):
        """Performs a move unit operation"""
        pParams = {"ReactorID":nReactor,
                   "reactPosition":nReactPosition}
        pMove = UnitOperations.Move(self.__pSystemModel, pParams)
        pMove.setDaemon(True)
        pMove.start()
        return pMove

    def Add(self, nReactor, nReagentReactor, nReagentPosition, nReagentDeliveryPosition):
        """Performs an add unit operation"""
        pParams = {"ReactorID":nReactor,
                   "ReagentReactorID":nReagentReactor,
                   "ReagentPosition":nReagentPosition,
                   "reagentLoadPosition":nReagentDeliveryPosition}
        pAdd = UnitOperations.Add(self.__pSystemModel, pParams)
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
        pEvaporate = UnitOperations.Evaporate(self.__pSystemModel, pParams)
        pEvaporate.setDaemon(True)
        pEvaporate.start()
        return pEvaporate

    def Install(self, nReactor):
        """Performs an install unit operation"""
        pParams = {"ReactorID":nReactor}
        pInstall = UnitOperations.Install(self.__pSystemModel, pParams)
        pInstall.setDaemon(True)
        pInstall.start()
        return pInstall
        
    ###
    def DeliverF18(self, nTrapTime, nTrapPressure, nEluteTime, nElutePressure):
        """Performs a Deliver F18 unit operation"""
        pParams = {"trapTime":nTrapTime,"trapPressure":nTrapPressure,"eluteTime":nEluteTime,"elutePressure":nElutePressure}
        pDeliverF18 = UnitOperations.DeliverF18(self.__pSystemModel, pParams)
        pDeliverF18.setDaemon(True)
        pDeliverF18.start()
        return pDeliverF18

    ###
    def TransferToHPLC(self, nReactor, nStopcockPosition):
        """Performs a transfer to HPLC unit operation"""
        pParams = {"ReactorID":nReactor,
                   "stopcockPosition":nStopcockPosition}
        pTransfer = UnitOperations.TransferToHPLC(self.__pSystemModel, pParams)
        pTransfer.setDaemon(True)
        pTransfer.start()
        return pTransfer

    def Transfer(self, nReactor, nTransferReactor, nTransferType, nTransferTimer, nTransferPressure):
        """Performs a transfer unit operation"""
        pParams = {"ReactorID":nReactor,
                   "transferReactorID":nTransferReactor,
                   "transferType":nTransferType,
                   "transferTimer":nTransferTimer,
                   "transferPressure":nTransferPressure}
        pTransfer = UnitOperations.Transfer(self.__pSystemModel, pParams)
        pTransfer.setDaemon(True)
        pTransfer.start()
        return pTransfer

    ###
    def UserInput(self, sUserMessage, bIsCheckBox, sDescription):
        """Performs a user input unit operation"""
        pParams = {"userMessage":sUserMessage,
                   "isCheckbox":bIsCheckBox,
                   "description":sDescription}
        pUserInput = UnitOperations.UserInput(self.__pSystemModel, pParams)
        pUserInput.setDaemon(True)
        pUserInput.start()
        return pUserInput

    ###
    def DetectRadiation(self):
        """Performs a radiation detection unit operation"""
        pParams = {}
        pDetectRadiation = UnitOperations.DetectRadiation(self.__pSystemModel, pParams)
        pDetectRadiation.setDaemon(True)
        pDetectRadiation.start()
        return pDetectRadiation

    ###
    def RampPressure(self, nPressureRegulator, fTargetPressure, nDuration):
        """Performs a ramp pressure unit operation"""
        pParams = {"pressureRegulator":nPressureRegulator,
                   "pressure":fTargetPressure,
                   "duration":nDuration}
        pRampPressure = UnitOperations.RampPressure(self.__pSystemModel, pParams)
        pRampPressure.setDaemon(True)
        pRampPressure.start()
        return pRampPressure

    def Mix(self, nReactor, nStirSpeed, nDuration):
        """Performs a mix unit operation"""
        pParams = {"ReactorID":nReactor,
                   "stirSpeed":nStirSpeed,
                   "duration":nDuration}
        pMix = UnitOperations.Mix(self.__pSystemModel, pParams)
        pMix.setDaemon(True)
        pMix.start()
        return pMix
