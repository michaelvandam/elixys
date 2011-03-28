#!/usr/bin/env python
# (C) 2011-2012 Henry Herman (hherman at ucla dot edu)
# Elixys Radiochem System
# license available in license.txt
""" Elixys state machine Module
    Export Classes:
        StateMacine
"""
import time
import sys

__author__="henry"
__date__ ="$Mar 25, 2011 4:45:17 PM$"

from threading import Thread, Event, Lock
from util.logger import logger
import time



class StateMachineError(Exception):
    pass

class StateData(dict):
    """StateData that can change within a state (thread-safe)"""
    def __init__(self, *args, **kwargs):
        self.lock = Lock()
        self.lock.acquire()
        dict.__init__(self,*args,**kwargs)
        self.lock.release()
        
    def __getitem__(self,y):
        self.lock.acquire()
        value = dict.__getitem__(self,y)
        self.lock.release()
        return value
    
    def __setitem__(self,y,x):
        self.lock.acquire()
        dict.__setitem__(self,y,x)
        self.lock.release()
        
        
class StateUpdateThread(Thread):
    """StateUpdateThread Class"""
    
    threads = []
    
    def __init__(self, tasks, parent=None):
        Thread.__init__(self)
        logger.debug("Initialize StateUpdateThread")
        self.stop_event = Event()
        self.do_tasks= tasks
        StateUpdateThread.threads.append(self)
        self.daemon=True

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
    
    def setParent(self, parent):
        self.parent = parent
    
    def getParent(self, parent):
        return parent
        
class State(object):
    """State Class"""
    def __init__(self, description, update_tasks=None, entryfxn=None, exitfxn=None):

        self.entryfxn = entryfxn
        self.exitfxn = exitfxn
        self.updatethread = StateUpdateThread(update_tasks)
        self.description = description
        logger.debug("Initialize %s" % self)
        self.data = StateData()

    def exit(self):
        if isinstance(self.updatethread, StateUpdateThread):
            self.updatethread.stop()
        if callable(self.exitfxn):
            self.exitfxn()
        logger.debug("Exit %s" % self)
    
    def run(self):
        self.enter()
        self.update()

    def enter(self):
        if callable(self.entryfxn):
            self.entryfxn()
        logger.debug("Enter %s" % self)

    def update(self):
        if isinstance(self.updatethread, StateUpdateThread):
            if not self.updatethread.isAlive():
                self.updatethread.start()
                logger.debug("Start Updating %s" % self)
            else:
                logger.debug("%s Already Active" % self)
        else:
            logger.debug("%s Nothing to update" % self)
        
    def __repr__(self):
        return "<State(description=%s)>" % self.description

    def __str__(self):
        return self.__repr__()
    
    def isActive(self):
        return self.updatethread.isAlive()


class TransitionEvent(object):
    """Transition Class"""
    def __init__(self, fromState, toState):
        self.fromState = fromState
        self.toState = toState
    
    def __call__(self):
        if self.fromState.isActive():
            self.fromState.exit()
        self.toState.enter()
        self.toState.update()
    
if __name__ == "__main__":

    print "Elevator State Machine"

    def enterdown():
        print "Go Down"

    def exitdown():
        print "Exit Down"

    def down_tasks():
        print "We are DOWN"
        time.sleep(5)

    def enterup():
        print "Go Up"
    
    def exitup():
        print "Go Down"
    
    def up_tasks():
        print "We are UP"
        time.sleep(5)
    
    downState = State("Down", down_tasks, enterdown, exitdown)
    upState = State("Up", up_tasks, enterup, exitup)
    
    pushDown = TransitionEvent(upState,downState)
    pushUp = TransitionEvent(downState,upState)
    
    pushUp()
    