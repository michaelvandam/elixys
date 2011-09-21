#!/usr/bin/python26

# Imports
import sys
import os
import os.path
import time
import errno
import json
import random
sys.path.append('/var/www/wsgi')
import DummyData

### Implementation of Elixys interface with dummy data ###

class Elixys:

    ### Interface functions ###

    def SetDatabase(self, pDatabase):
        self.pDatabase = pDatabase

    def GetConfiguration(self, sUsername):
        return {"name":"Mini cell 3",
            "version":"2.0",
            "debug":"false"}

    def GetSupportedOperations(self, sUsername):
        return ["Add",
            "Evaporate",
            "Transfer",
            "Elute",
            "React",
            "Prompt",
            "Install",
            "Comment"]

    def GetServerState(self, sUsername):
        # Update and return the default system state
        return DummyData.GetDefaultSystemState(sUsername)

    def GetSystemState(self, sUsername):
        return "NONE"

    def GetRunState(self, sUsername):
        return "NONE"

    def SaveRunState(self, sUsername, sSystemState):
        return True

    def GetRunUser(self, sUsername):
        return "NONE"

    def RunSequence(self, sUsername, nSequenceID):
        return True

    def AbortRun(self, sUsername):
        return True

    def ContinueRun(self, sUsername):
        return True

    def StartManualRun(self, sUsername):
        return True

    def PerformOperation(self, sUsername, nComponentID, nSequenceID):
        return True

    def AbortOperation(self, sUsername):
        return False

    def ContinueOperation(self, sUsername):
        return True

    def FinishManualRun(self, sUsername):
        return True

