"""CoreServer

The main executable for the Python service that communicates with the PLC"""

# Imports
import sys
sys.path.append("/opt/elixys/core")
sys.path.append("/opt/elixys/database")
import os
import signal
import subprocess
import time
from daemon import daemon
from DBComm import *

# rtmpd daemon exit function
gRtmpdDaemon = None
def OnExit(pRtmpdDaemon, signal, func=None):
    if gRtmpdDaemon != None:
        gRtmpdDaemon.bTerminate = True

# rtmpd daemon
class RtmpdDaemon(daemon):
    def __init__(self, sPidFile):
        """Initializes the rtmpd daemon"""
        global gRtmpdDaemon
        daemon.__init__(self, sPidFile, "/opt/elixys/logs/rtmpdDaemon.log")
        self.bTerminate = False
        gRtmpdDaemon = self

    def run(self):
        """Runs the rtmpd daemon"""
        global gRtmpdDaemon
        pDatabase = None
        pRtmpdProcess = None
        while not self.bTerminate:
            try:
                # Create the database
                pDatabase = DBComm()
                pDatabase.Connect()
                pDatabase.SystemLog(LOG_INFO, "System", "rtmpd started")

                # Install the kill signal handler
                signal.signal(signal.SIGTERM, OnExit)

                # Spawn rtmpd
                pLogFile = file("/opt/elixys/logs/rtmpdProcess.log","w")
                if not os.path.isfile("/opt/elixys/demomode"):
                    sLuaFile = "crtmpserver.lua"
                else:
                    sLuaFile = "crtmpdemoserver.lua"
                pRtmpdProcess = subprocess.Popen(["crtmpserver", sLuaFile], stdin = pLogFile, stdout = pLogFile, cwd = "/opt/elixys/rtmpd")

                # Run until we get the signal to stop
                while not self.bTerminate and (pRtmpdProcess.returncode == None):
                    pRtmpdProcess.poll()
                    time.sleep(1)
                pDatabase.SystemLog(LOG_INFO, "System", "rtmpd stopping")
            except Exception as ex:
                if pDatabase != None:
                    pDatabase.SystemLog(LOG_ERROR, "System", "rtmpd failed: " + str(ex))
            finally:
                if (pRtmpdProcess != None) and (pRtmpdProcess.returncode == None):
                    pDatabase.SystemLog(LOG_INFO, "System", "terminating")
                    pRtmpdProcess.terminate()
                if pDatabase != None:
                    pDatabase.SystemLog(LOG_INFO, "System", "rtmpd stopped")

            # Sleep for a second before we respawn
            if not self.bTerminate:
                time.sleep(1)
        gRtmpdDaemon = None

# Main function
if __name__ == "__main__":
    if len(sys.argv) == 3:
        pDaemon = RtmpdDaemon(sys.argv[2])
        if 'start' == sys.argv[1]:
            pDaemon.start()
        elif 'stop' == sys.argv[1]:
            pDaemon.stop()
        elif 'restart' == sys.argv[1]:
            pDaemon.restart()
        else:
            print "Unknown command"
            sys.exit(2)
        sys.exit(0)
    else:
        print "usage: %s start|stop|restart pidfile" % sys.argv[0]
        sys.exit(2)

