""" ElixysCLI.py

Implements a CLI interface to the Elixys system"""

### Imports
import time
import rpyc
import socket
import sys
sys.path.append("../hardware/")
sys.path.append("../core/")
from HardwareComm import HardwareComm
from SystemModel import SystemModel
from UnitOperationsWrapper import UnitOperationsWrapper
import BaseCLI

# Elixys CLI class
class ElixysCLI(BaseCLI.BaseCLI):
    def __init__(self):
        """Constructor"""
        # Initialize variables
        self.pHardwareComm = None
        self.pSystemModel = None
        self.pUnitOperationsWrapper = None
        self.pStateMonitor = None
    
    def ExecuteCommand(self, sCommand):
        """Parses and executes the given command"""
        sResult = BaseCLI.ExecuteCommandImpl(sCommand, self.pUnitOperationsWrapper, self.pSystemModel, self.pHardwareComm)
        if sResult != "":
            print sResult

    def SendCommand(self, sCommand):
        """Parses and sends the raw command"""
        sResult = BaseCLI.SendCommandImpl(sCommand, self.pHardwareComm)
        if sResult != "":
            print sResult

    def GetState(self):
        """Formats the state as a string"""
        return BaseCLI.GetStateImpl(self.pSystemModel)

    def AbortUnitOperation(self):
        """Abort the current unit operation"""
        # Get the current unit operation
        pCurrentUnitOperation = self.pSystemModel.GetUnitOperation()
        if pCurrentUnitOperation != None:
            # Abort the current unit operation
            pCurrentUnitOperation.setAbort()
        else:
            print "No current unit operation"

    def DeliverUserInput(self):
        """Deliver user input to the current unit operation"""
        # Get the current unit operation
        pCurrentUnitOperation = self.pSystemModel.GetUnitOperation()
        if pCurrentUnitOperation != None:
            # Deliver user input to the current user operation
            pCurrentUnitOperation.deliverUserInput()
        else:
            print "No current unit operation"

    def PauseTimer(self):
        """Pauses the currently running unit operation timer"""
        # Get the current unit operation
        pCurrentUnitOperation = self.pSystemModel.GetUnitOperation()
        if pCurrentUnitOperation != None:
            # Pause the currently running unit operation timer
            pCurrentUnitOperation.pauseTimer()
        else:
            print "No current unit operation"

    def ContinueTimer(self):
        """Continues the paused unit operation timer"""
        # Get the current unit operation
        pCurrentUnitOperation = self.pSystemModel.GetUnitOperation()
        if pCurrentUnitOperation != None:
            # Continue the currently paused unit operation timer
            pCurrentUnitOperation.continueTimer()
        else:
            print "No current unit operation"

    def StopTimer(self):
        """Stops the unit operation timer"""
        # Get the current unit operation
        pCurrentUnitOperation = self.pSystemModel.GetUnitOperation()
        if pCurrentUnitOperation != None:
            # Stop the unit operation timer
            pCurrentUnitOperation.stopTimer()
        else:
            print "No current unit operation"

    def Run(self):
        """Main CLI function"""
        # Initialize variables
        self.pHardwareComm = HardwareComm("../")
        self.pHardwareComm.StartUp()
        self.pSystemModel = SystemModel(self.pHardwareComm, None, "../core/")
        self.pSystemModel.StartUp()
        self.pUnitOperationsWrapper = UnitOperationsWrapper(self.pSystemModel)
    
        # Create an RPC connection to the state monitoring window
        try:
            self.pStateMonitor = rpyc.connect("localhost", 18861)
            self.pSystemModel.SetStateMonitor(self.pStateMonitor)
        except socket.error, ex:
            print "Warning: failed to connect to state monitor, no output will be displayed"

        # Call the base run function
        BaseCLI.BaseCLI.Run(self)

        # Clean up
        self.pSystemModel.ShutDown()
        self.pHardwareComm.ShutDown()

# Main function
if __name__ == "__main__":
    # Create and run the CLI
    pElixysCLI = ElixysCLI()
    pElixysCLI.Run()

