""" UnitOperationsWrapper.py

Implements an wrapper around the unit operations class for use by the CLI interface"""

### Imports
import sys
sys.path.append("../core/unitoperations")
from UnitOperation import *
from Initialize import Initialize
from React import React
from Move import Move
from Add import Add
from Evaporate import Evaporate
from Install import Install
from TrapF18 import TrapF18
from EluteF18 import EluteF18
from Transfer import Transfer
from TempProfile import TempProfile
from RampPressure import RampPressure
from Mix import Mix

class UnitOperationsWrapper:
    def __init__(self, pSystemModel):
        """Unit operations wrapper constructor"""
        self.__pSystemModel = pSystemModel
    
    def Init(self):
        """Initializes Elixys hardware for use"""
        pParams = {}
        pInit = Initialize(self.__pSystemModel, pParams)
        pInit.setDaemon(True)
        pInit.start()
        return pInit
       
    def React(self, sReactor, nReactionTemperature, nReactionTime, nFinalTemperature, sReactPosition, nStirSpeed):
        """Performs a react unit operation"""
        pParams = {"ReactorID":sReactor,
                   "reactTemp":nReactionTemperature,
                   "reactTime":nReactionTime,
                   "coolTemp":nFinalTemperature,
                   "reactPosition":sReactPosition,
                   "stirSpeed":nStirSpeed}
        pReact = React(self.__pSystemModel, pParams)
        pReact.setDaemon(True)
        pReact.start()
        return pReact

    def Move(self, sReactor, sReactPosition):
        """Performs a move unit operation"""
        pParams = {"ReactorID":sReactor,
                   "reactPosition":sReactPosition}
        pMove = Move(self.__pSystemModel, pParams)
        pMove.setDaemon(True)
        pMove.start()
        return pMove

    def Add(self, sReactor, sReagentReactor, nReagentPosition, nReagentDeliveryPosition):
        """Performs an add unit operation"""
        pParams = {"ReactorID":sReactor,
                   "ReagentReactorID":sReagentReactor,
                   "ReagentPosition":nReagentPosition,
                   "reagentLoadPosition":nReagentDeliveryPosition,
                   "duration":DEFAULT_ADD_DURATION,
                   "pressure":DEFAULT_ADD_PRESSURE}
        pAdd = Add(self.__pSystemModel, pParams)
        pAdd.setDaemon(True)
        pAdd.start()
        return pAdd

    def Evaporate(self, sReactor, nEvaporationTemperature, nEvaporationTime, nFinalTemperature, nStirSpeed):
        """Performs an evaporation unit operation"""
        pParams = {"ReactorID":sReactor,
                   "evapTemp":nEvaporationTemperature,
                   "evapTime":nEvaporationTime,
                   "coolTemp":nFinalTemperature,
                   "stirSpeed":nStirSpeed,
                   "pressure":DEFAULT_EVAPORATE_PRESSURE}
        pEvaporate = Evaporate(self.__pSystemModel, pParams)
        pEvaporate.setDaemon(True)
        pEvaporate.start()
        return pEvaporate

    def Install(self, sReactor):
        """Performs an install unit operation"""
        pParams = {"ReactorID":sReactor,
                   "userMessage":""}
        pInstall = Install(self.__pSystemModel, pParams)
        pInstall.setDaemon(True)
        pInstall.start()
        return pInstall
        
    def TrapF18(self, bCyclotronFlag, nTrapTime, nTrapPressure):
        """Performs a Trap F18 unit operation"""
        pParams = {"cyclotronFlag":int(bCyclotronFlag),
                   "trapTime":nTrapTime,
                   "trapPressure":nTrapPressure}
        pTrapF18 = TrapF18(self.__pSystemModel, pParams)
        pTrapF18.setDaemon(True)
        pTrapF18.start()
        return pTrapF18

    def EluteF18(self, nEluteTime, nElutePressure, sReagentReactor, nReagentPosition):
        """Performs an Elute F18 unit operation"""
        pParams = {"eluteTime":nEluteTime,
                   "elutePressure":nElutePressure,
                   "ReagentReactorID":sReagentReactor,
                   "ReagentPosition":nReagentPosition}
        pEluteF18 = EluteF18(self.__pSystemModel, pParams)
        pEluteF18.setDaemon(True)
        pEluteF18.start()
        return pEluteF18

    def Transfer(self, sSourceReactor, sTransferReactor, sTransferType, nTransferTimer, nTransferPressure):
        """Performs a transfer unit operation"""
        pParams = {"ReactorID":sSourceReactor,
                   "transferReactorID":sTransferReactor,
                   "transferType":sTransferType,
                   "transferTimer":nTransferTimer,
                   "transferPressure":nTransferPressure}
        pTransfer = Transfer(self.__pSystemModel, pParams)
        pTransfer.setDaemon(True)
        pTransfer.start()
        return pTransfer

    def TempProfile(self, sReactor, nProfileTemperature, nProfileTime, nFinalTemperature, nLiquidTCReactor, nLiquidTCCollet, nStirSpeed):
        """Heats the reactor in the transfer position for temperature profiling"""
        pParams = {"ReactorID":sReactor,
                   "reactTemp":nProfileTemperature,
                   "reactTime":nProfileTime,
                   "coolTemp":nFinalTemperature,
                   "liquidTCReactor":nLiquidTCReactor,
                   "liquidTCCollet":nLiquidTCCollet,
                   "stirSpeed":nStirSpeed}
        pTempProfile = TempProfile(self.__pSystemModel, pParams)
        pTempProfile.setDaemon(True)
        pTempProfile.start()
        return pTempProfile

    def RampPressure(self, nPressureRegulator, nTargetPressure, nDuration):
        """Performs a ramp pressure unit operation"""
        pParams = {"pressureRegulator":nPressureRegulator,
                   "pressure":nTargetPressure,
                   "duration":nDuration}
        pRampPressure = RampPressure(self.__pSystemModel, pParams)
        pRampPressure.setDaemon(True)
        pRampPressure.start()
        return pRampPressure

    def Mix(self, sReactor, nStirSpeed, nDuration):
        """Performs a mix unit operation"""
        pParams = {"ReactorID":sReactor,
                   "stirSpeed":nStirSpeed,
                   "duration":nDuration}
        pMix = Mix(self.__pSystemModel, pParams)
        pMix.setDaemon(True)
        pMix.start()
        return pMix

    def UserInput(self, sUserMessage, bIsCheckBox, sDescription):
        """Performs a user input unit operation
        raise Exception("Implement UserInput unit operation")
        pParams = {"userMessage":sUserMessage,
                   "isCheckbox":bIsCheckBox,
                   "description":sDescription}
        pUserInput = UserInput(self.__pSystemModel, pParams)
        pUserInput.setDaemon(True)
        pUserInput.start()
        return pUserInput"""
        return None

    def DetectRadiation(self):
        """Performs a radiation detection unit operation
        raise Exception("Implement DetectRadiation unit operation")
        pParams = {}
        pDetectRadiation = DetectRadiation(self.__pSystemModel, pParams)
        pDetectRadiation.setDaemon(True)
        pDetectRadiation.start()
        return pDetectRadiation"""
        return None
