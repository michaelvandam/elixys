"""TailLogs

Monitors the logs and displays log messages as they occur
"""

import os
import json
import sys
sys.path.append("/opt/elixys/database/")
sys.path.append("/opt/elixys/core/")
from DBComm import *
import Utilities
import time

def PrintUsage():
    print "Log level argument not recognized.  Usage:"
    print "  python TailLogs.py [log level]"
    print "Where messages at or below the specified log level will be displayed:"
    print "  error     Critical error messages"
    print "  warning   Noncritical warnings"
    print "  info      Informational messages (default level)"
    print "  debug     Useful to developers"
    print ""

if __name__ == '__main__':
    # Set the logging level
    if len(sys.argv) > 1:
        nLogLevel = ParseLogLevel(sys.argv[1])
        if nLogLevel == -1:
            PrintUsage()
            exit()
    else:
        nLogLevel = LOG_INFO

    # Create the database layer
    pDBComm = DBComm()
    pDBComm.Connect()

    # Warn if the user wants a high level of logging than the system is using
    if nLogLevel > pDBComm.GetLogLevel():
        print "Warning: the log level specific is higher than what the system is currently using, you may not see messages all the messages you expect."

    # Monitor the logs until the user presses 'q' to quit
    print "Monitoring logs, type 'q' and press enter to quit..."

    # Logging loop
    pLastLogTimestamp = None
    nLastLogID = 0
    while not Utilities.CheckForQuit():
        # Do we have a previous log timestamp?
        if pLastLogTimestamp != None:
            # Yes, so get any recent log messages
            pLogs = pDBComm.GetRecentLogsByTimestamp("System", nLogLevel, pLastLogTimestamp)
        else:
            # No, so obtain up to the 15 most recent log messages
            pLogs = pDBComm.GetRecentLogsByCount("System", nLogLevel, 15)

        # Make a new array of only logs we haven't already shown
        pNewLogs = []
        for pLog in pLogs:
            if pLog["id"] == nLastLogID:
                break
            pNewLogs.append(pLog)

        # Display the log messages
        pNewLogs.reverse()
        for pLog in pNewLogs:
            # Print the text
            sLog = str(pLog["date"]) + " "
            if pLog["level"] == 0:
                sLog += "Error "
            elif pLog["level"] == 1:
                sLog += "Warning "
            elif pLog["level"] == 2:
                sLog += "Info "
            elif pLog["level"] == 3:
                sLog += "Debug "
            sLog += "(" + pLog["username"] + "): " + pLog["message"]
            if (pLog["sequenceid"] != 0) and (pLog["componentid"] != 0):
                sLog += " (sequence " + str(pLog["sequenceid"]) + ", component " + str(pLog["componentid"]) + ")"
            elif pLog["sequenceid"] != 0:
                sLog += " (sequence " + str(pLog["sequenceid"]) + ")"
            print sLog
            pLastLogTimestamp = pLog["date"]
            nLastLogID = pLog["id"]

        # Sleep for a bit
        time.sleep(0.5)

    # Complete
    pDBComm.Disconnect()
    print "Done"

