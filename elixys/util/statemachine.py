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
        self._modified = True
        self.lock = Lock()
        self.lock.acquire()
        dict.__init__(self,*args,**kwargs)
        self.lock.release()
        
    def __getitem__(self,y):
        
        self.lock.acquire()
        try:
            value = dict.__getitem__(self,y)
        finally:
            self.lock.release()
        return value
    
    def __setitem__(self,y,x):
        self.lock.acquire()
        dict.__setitem__(self,y,x)
        self._modified = True
        self.lock.release()
    
    def isModified(self):
        self.lock.acquire()
        value = self._modified
        self.lock.release()
        return value
        
    def clearModified(self):
        self.lock.acquire()
        self._modified = False
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

    states = []
    def __init__(self, description, update_thread_tasks=None, updatefxn=None, entryfxn=None, exitfxn=None, data=None):

        self.entryfxn = entryfxn
        self.exitfxn = exitfxn
        if not updatefxn is None:
            self._update = updatefxn
        if not update_thread_tasks is None:
            self._update = StateUpdateThread(update_thread_tasks)      
        if not hasattr(self,"_update"):
            self._update=None
        
        self.description = description
        logger.debug("Initialize %s" % self)
        self.data = data
        self.active = False
        State.states.append(self)
        self.substates = []
        self._needs_to_run = False
        self._entry_has_run = False
    
    def addSubstate(self, state):
        self.substates.append(state)

    def removeSubstate(self, state):
        self.substates.remove(state)

    def exit(self):
        if isinstance(self._update, StateUpdateThread):
            self._update.stop()
        if callable(self.exitfxn):
            self.exitfxn()
        
        if callable(self.update):
            logger.debug("FXN type update, deactivate")
            
        logger.debug("Exit %s" % self)
        self.active=False
        self._entry_has_run = False
        
        
    def run(self):
        if self._needs_to_run:
            self.enter()
            self.update()
        elif self.isActive():
            self.exit()
        
        for substate in self.substates:
            substate.run()
        
    def enter(self):
        if self._entry_has_run:
            logger.debug("No Need to Run Enter %s" % self)
            return
        if callable(self.entryfxn):
            self.entryfxn()
            logger.debug("Enter %s" % self)
        else:
            logger.debug("Nothing to Call on Enter %s" % self)
        
        self.active = True

    def update(self, no_enter=False):
        
        if no_enter and not self.active:
            logger.debug("%s Not active, nothing to update" % self)
            return
        
        if isinstance(self._update, StateUpdateThread):
            if not self._update.isAlive():
                self._update.start()
                logger.debug("Start Updating %s" % self)
            else:
                logger.debug("%s Already Active" % self)
        elif callable(self._update):
            self._update()
        else:
            logger.debug("%s Nothing to update" % self)
        
        
    def __repr__(self):
        return "<State(description=%s)>" % self.description

    def __str__(self):
        return self.__repr__()
    
    def isActive(self):
        if isinstance(self._update,  StateUpdateThread):
            active = self._update.isAlive()
        else:
            active = False
        if self.active or active:
            return True
        else:
            return 

    def activate(self):
        self._needs_to_run = True
    
    def deactivate(self):
        self._needs_to_run = False

        
class TransitionEvent(object):
    """Transition Class"""
    def __init__(self, fromState, toState):
        self.fromState = fromState
        self.toState = toState
    
    def __call__(self):
        if self.fromState.isActive():
            self.fromState.deactivate()
            self.fromState.exit()
        self.toState.activate()
        self.toState.run()
    
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
    
    
    
    downData = StateData()
    upData = StateData()
    downState = State("Down", down_tasks, None,enterdown, exitdown, downData)
    upState = State("Up", None,up_tasks, enterup, exitup, upData)
    upStateDoorOpen = State("UpStateDoorOpen", None, None, None, None, None)
    upStateDoorClosed = State("UpStateDoorClosed", None,None,None,None,None)
    
    upState.addSubstate(upStateDoorOpen)
    upState.addSubstate(upStateDoorClosed)
    
    pushDown = TransitionEvent(upState,downState)
    pushUp = TransitionEvent(downState,upState)
    
    pushUp()
    