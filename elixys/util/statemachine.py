#!/usr/bin/env python
# (C) 2011-2012 Henry Herman (hherman at ucla dot edu)
# Elixys Radiochem System
# license available in license.txt
""" Elixys state machine Module
    Export Classes:
        StateMacine
"""
import time

__author__="henry"
__date__ ="$Mar 25, 2011 4:45:17 PM$"

from threading import Thread, Event
from util.logger import logger
import time

class StateMachineError(Exception):
    pass

class StateUpdateThread(Thread):
    """StateUpdateThread Class"""
    def __init__(self, tasks):
        Thread.__init__(self)
        logger.debug("Initialize StateUpdateThread")
        self.stop_event = Event()
        self.do_tasks= tasks

    def run(self):
        logger.debug("Running StateUpdateThread")
        while(not self.stop_event.isSet()):
            self.do_tasks()
        self.stop_event.clear()
        logger.info("Exiting StateUpdateThread")

    def stop(self):
        logger.debug("Stop StateUpdateThread")
        self.stop_event.set()
        self.join()
        self.stop_event.clear()
        Thread.__init__(self)


class State(object):
    """State Class"""
    def __init__(self, description, updatethread=None, entryfxn=None, exitfxn=None):

        self.updatethread = updatethread
        self.entryfxn = entryfxn
        self.exitfxn = exitfxn
        self.description = description
        logger.debug("Initialize %s" % self)

    def exit(self):
        if isinstance(self.updatethread, StateUpdateThread):
            self.updatethread.stop()
        if callable(self.exitfxn):
            self.exitfxn()
        logger.debug("Exit %s" % self)

    def enter(self):
        if callable(self.entryfxn):
            self.entryfxn()
        logger.debug("Enter %s" % self)

    def update(self):
        if isinstance(self.updatethread, StateUpdateThread):
            if not self.updatethread.isAlive():
                self.updatethread.start()

        logger.debug("Start Updating %s" % self)
        
    def __repr__(self):
        return "<State(description=%s)>" % self.description

    def __str__(self):
        return self.__repr__()


class TransitionEvent(object):
    """Transition Class"""
    def __init__(self, parent, toState):
        pass
    
if __name__ == "__main__":

    print "Elevator State Machine"

    def enter():
        print "Go Down"

    def exit_():
        print "Exit Down"

    def down_tasks():
        print "We are DOWN"
        time.sleep(5)

    downTaskThread = StateUpdateThread(down_tasks)

    downState = State("Down", downTaskThread, enter, exit_)
    