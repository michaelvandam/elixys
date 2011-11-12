""" CoreServerCLI.py

Implements a CLI interface to the core server"""

### Imports
import rpyc
import socket
import sys
sys.path.append("/var/www/wsgi/")
import CoreServerProxy
import BaseCLI

# Core server CLI class
class CoreServerCLI(BaseCLI.BaseCLI):
    def __init__(self):
        """Constructor"""
        # Initialize variables
        self.pCoreServer = None

    def ExecuteCommand(self, sCommand):
        """Parses and executes the given command"""
        # Ask the core server execute the command
        sResult = self.pCoreServer.CLIExecuteCommand("CLI", sCommand)
        if sResult != "":
            print sResult

    def SendCommand(self, sCommand):
        """Parses and sends the raw command"""
        # Ask the core server send the command
        sResult = self.pCoreServer.CLISendCommand("CLI", sCommand)
        if sResult != "":
            print sResult

    def GetState(self):
        """Formats the state as a string"""
        # Ask the core server for the state
        return self.pCoreServer.CLIGetState("CLI")

    def AbortUnitOperation(self):
        """Abort the current unit operation"""
        # Ask the core server to abort the current unit operation
        sResult = self.pCoreServer.CLIAbortUnitOperation("CLI")
        if sResult != "":
            print sResult

    def Run(self):
        """Main CLI function"""
        # Initialize the proxy
        self.pCoreServer = CoreServerProxy.CoreServerProxy()

        # Create an RPC connection to the state monitoring window
        sResult = self.pCoreServer.CLIConnectToStateMonitor("CLI")
        if sResult != "":
            print sResult

        # Call the base run function
        BaseCLI.BaseCLI.Run(self)

# Main function
if __name__ == "__main__":
    # Create and run the CLI
    pCoreServerCLI = CoreServerCLI()
    pCoreServerCLI.Run()

