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
import copy

__author__="henry"
__date__ ="$Mar 25, 2011 4:45:17 PM$"

from threading import Thread, Event, Lock, Condition
import Queue
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
        except:
            value = None
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
    
class StateThread(Thread):
    """State Thread"""    
    threads = []
    pause_event = Event()
    pause_event.set()
    
    def __init__(self, fxn=None):
        Thread.__init__(self)
        logger.debug("Initialize %s" % self)
        self.stop_event = Event()
        StateThread.threads.append(self)
        self.daemon=True
        self.fxn = fxn
        
    def run(self):
        logger.debug("Running %s" % self)
        while(not self.stop_event.isSet()):
            StateThread.pause_event.wait()
            if callable(self.fxn):
                self.fxn()
        self.stop_event.clear()
        logger.info("Exiting %s" % self)

    def stop(self):
        logger.debug("Stop %s" % self)
        self.stop_event.set()
        self.join()
        self.stop_event.clear()
        Thread.__init__(self)
    
    def pause(self):
        StateThread.pause_event.clear()
    
    def resume(self):
        StateThread.pause_event.set()
    
    def isPaused(self):
        return StateThread.pause_event.isSet()

class StateUpdateThread(StateThread):
    """StateUpdateThread Class"""
    
    def __init__(self, tasks, parent=None):
        StateThread.__init__(self)
        self.fxn = tasks
        self.parent = parent
    
    def setParent(self, parent):
        self.parent = parent
    
    def getParent(self, parent):
        return parent
        
class State(object):
    """State Class"""
    states = []
    def __init__(self, description, updatefxn=None, enterfxn=None, exitfxn=None, data=None):
        self.enterfxn = enterfxn
        self.exitfxn = exitfxn
        self.updatefxn = updatefxn
        self.description = description
        logger.debug("Initialize %s" % self)
        self.data = data
        self.active = False
        State.states.append(self)
        self.substates = []
        self._needs_to_run = False
        self._entry_has_run = False
    
    def setUpdate(self, updatefxn, isThread=False):
        if not isThread:
            self._update = updatefxn
        else:
            self._update = StateUpdateThread(updatefxn)      
        
    def getUpdate(self):
        return self._update
        
    updatefxn = property(getUpdate, setUpdate) 
    
    def addSubstate(self, state, initial=False):
        self.substates.append(state)
        if initial:
            state.activate()

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
        elif callable(self.enterfxn):
            self.enterfxn()
            self._entry_has_run = True
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
            return False

    def activate(self):
        self._needs_to_run = True
    
    def deactivate(self):
        self._needs_to_run = False


class FSMThread(StateThread):
    def __init__(self, fsm, refresh=.5):
        StateThread.__init__(self)
        self.fsm = fsm
        self.statesToRun = copy.copy(fsm.states)
        self.refresh = refresh
        self.fxn = self.runStates
    
    def run(self):
        logger.debug("Running %s" % self)
        while(not self.stop_event.isSet()):
            StateThread.pause_event.wait()
            if callable(self.fxn):
                self.fxn()
        self.stop_event.clear()
        logger.info("Exiting %s" % self)
        
    def runStates(self):
        for state in self.statesToRun:
            state.run() 
        time.sleep(self.refresh)
        try:
            event = self.fsm.events.get(False)
            event()
        except Queue.Empty:
            pass
            
        
        

        
class FSM(object):
    """Finite State Machine Thread"""
    
    def __init__(self, states = [], events = []):
        self.states = states
        self.possible_events = events
        self.statethread = FSMThread(self)
        self.events = Queue.Queue()
    
    def _getAllStates(self):
        pass
    
    def run(self):
        self.statethread.start()
    
    def pause(self):
        self.statethread.pause()
    
    def resume(self):
        self.statethread.resume()
    
    def stop(self):
        self.statethread.stop()
        
    def addEvent(self,event):
        self.events.put(event)
    
    def isPaused(self):
        return self.statethread.isPaused()
    
    def isInState(self, state):
        if state in State.states:
            return state.isActive()
        else:
            return False
        
        
class TransitionEvent(object):
    """Transition Class"""
    def __init__(self, fromState, toState):
        self.fromState = fromState
        self.toState = toState
    
    def __call__(self):
        self.fromState.deactivate()
        self.toState.activate()
    
    
if __name__ == "__main__":

    print "Elevator State Machine"
    
    downData = StateData()
    upData = StateData()
    
    downState = State("Down")
    downState.activate()
    upState = State("Up")
    movingDownState = State("MovingDown")
    movingUpState = State("MovingUp")
    doorOpen = State("StateDoorOpen")
    doorClosed = State("StateDoorClosed")
    
    
    upState.addSubstate(doorOpen)
    upState.addSubstate(doorClosed, initial=True)
    
    downState.addSubstate(doorOpen)
    downState.addSubstate(doorClosed, initial=True)
    
    states = [downState, upState, movingDownState, movingUpState]
    
    
    goUp = TransitionEvent(downState, movingUpState)
    goDown = TransitionEvent(upState, movingDownState)
    
    arrivedUp = TransitionEvent(movingUpState, upState)
    arrivedDown = TransitionEvent(movingDownState, downState)
    
    pushDown = TransitionEvent(upState,movingDownState)
    pushUp = TransitionEvent(downState,movingUpState)
    
    
    transitions = [goUp, goDown, arrivedUp, arrivedDown, pushDown, pushUp]
    
    elevator = FSM(states, transitions)
    
    
    def enterdown():
        print "Go Down"

    def exitdown():
        print "Exit Down"

    def down_tasks():
        print "We are DOWN"
        time.sleep(2)
        
    downState.setUpdate(down_tasks,True)
    downState.enterfxn = enterdown
    downState.exitfxn = exitdown
    
    def enterup():
        print "Go Up"
        
    
    def exitup():
        print "Go Down"
    
    def up_tasks():
        print "We are UP"
        time.sleep(2)
        
    upState.updatefxn = up_tasks
    upState.enterfxn = enterup
    upState.exitfxn = exitup
    
    def openDoor():
        print "Closing Door"
        
    
    doorOpen.updatefxn = openDoor
    
    def doorClosed():
        print "Door closed"
    
    doorClosed.updatfxn = doorClosed
    
    def moving_up():
        time.sleep(3)
        print "Moving Up"
        elevator.addEvent(arrivedUp)
        
    movingUpState.updatefxn = moving_up
    
    def moving_down():
        time.sleep(3)
        print "Moving Down"
        elevator.addEvent(arrivedDown)
    
    movingDownState.updatefxn = moving_down
    
    elevator.run()
    
    