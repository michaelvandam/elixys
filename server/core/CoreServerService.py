"""CoreServer

Implements the core server interface"""

# Imports
import rpyc
import json
import CoreServer

# Suppress rpyc warning messages
import logging
logging.basicConfig(level=logging.ERROR)

# Core server service
class CoreServerService(rpyc.Service):
    def on_connect(self):
        """Invoked when a client connects"""
        CoreServer.gDatabase.Log("System", "CoreServerService.connect()")

        # Allow pickling on this connection for proper data transfer
        self._conn._config["allow_pickle"] = True
 
    def on_disconnect(self):
        """Invoked when a client disconnects"""
        CoreServer.gDatabase.Log("System", "CoreServerService.disconnect()")

    def exposed_GetServerState(self, sUsername):
        """Returns the state of the server"""
        CoreServer.gDatabase.Log(sUsername, "CoreServerService.GetServerState()")

        # Return the dummy server state
        pServerState = {"type":"serverstate",
            "runstate":{"type":"runstate",
                "status":"Idle",
                "username":"",
                "sequenceid":0,
                "componentid":0,
                "prompt":{"type":"promptstate",
                    "show":False}},
            "hardwarestate":{"type":"hardwarestate",
                "pressureregulators":[{"type":"pressureregulatorstate",
                    "name":"Pneumatics",
                    "pressure":59.7},
                    {"type":"pressureregulatorstate",
                    "name":"Gas",
                    "pressure":4.3}],
                "cooling":False,
                "vacuum":-43.6,
                "reagentrobot":{"type":"reagentrobotstate",
                    "position":{"type":"reagentrobotposition",
                        "cassette":1,
                        "reagent":3,
                        "delivery":0},
                    "actuator":"up",
                    "gripper":"open"},
                "reactors":[{"type":"reactorstate",
                    "number":1,
                    "temperature":165.0,
                    "position":{"type":"reactorposition",
                         "horizontal":"React1",
                        "vertical":"Up"},
                    "activity":515.9,
                    "activitytime":"18:23.31",
                    "evaporation":False,
                    "transfer":False,
                    "transferposition":"waste",
                    "reagent1transfer":False,
                    "reagent2transfer":False,
                    "stirspeed":500,
                    "video":"",
                    "columnposition":"Load",
                    "f18transfer":False,
                    "eluenttransfer":False},
                    {"type":"reactorstate",
                    "number":2,
                    "temperature":32.1,
                    "position":{"type":"reactorposition",
                        "horizontal":"Install",
                        "vertical":"Down"},
                    "activity":45.2,
                    "activitytime":"18:23.31",
                    "evaporation":False,
                    "transfer":False,
                    "transferposition":"waste",
                    "reagent1transfer":False,
                    "reagent2transfer":False,
                    "stirspeed":0,
                    "video":""},
                    {"type":"reactorstate",
                    "number":3,
                    "temperature":32.1,
                    "position":{"type":"reactorposition",
                        "horizontal":"Install",
                        "vertical":"Down"},
                    "activity":645.1,
                    "activitytime":"18:23.31",
                    "evaporation":False,
                    "transfer":False,
                    "transferposition":"waste",
                    "reagent1transfer":False,
                    "reagent2transfer":False,
                    "stirspeed":0,
                    "video":""}]}}
        return json.dumps(pServerState)

    def exposed_RunSequence(self, sUsername, nSequenceID):
        """Loads a sequence from the database and runs it"""
        CoreServer.gDatabase.Log(sUername, "CoreServerService.RunSequence(" + str(nSequenceID) + ")")
        return False

    def exposed_Abort(self, sUsername):
        """Gently aborts the run that is in progress, cooling the system and shutting down cleanly"""
        CoreServer.gDatabase.Log(sUsername, "CoreServerService.Abort()")
        return False

    def exposed_EmergencyStop(self, sUsername):
        """Quickly turns off the heaters and terminates the run, leaving the system in its current state"""
        CoreServer.gDatabase.Log(sUsername, "CoreServerService.EmergencyStop()")
        return False

    def exposed_Pause(self, sUsername):
        """Causes the system to pause after the current unit operation is complete"""
        CoreServer.gDatabase.Log(sUsername, "CoreServerService.Pause()")
        return False

    def exposed_Continue(self, sUsername):
        """Continues a paused run"""
        CoreServer.gDatabase.Log(sUsername, "CoreServerService.Continue()")
        return False

    def exposed_PauseTimer(self, sUsername):
        """Pauses the timer if the unit operation has one running"""
        CoreServer.gDatabase.Log(sUsername, "CoreServerService.PauseTimer()")
        return False

    def exposed_ContinueTimer(self, sUsername):
        """Continues the timer if the unit operation has one paused"""
        CoreServer.gDatabase.Log(sUsername, "CoreServerService.ContinueTimer()")
        return False

    def exposed_StopTimer(self, sUsername):
        """Cuts the timer short if the unit operation has one running"""
        CoreServer.gDatabase.Log(sUsername, "CoreServerService.StopTimer()")
        return False

