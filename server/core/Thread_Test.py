import threading
import rpyc

def setThread():
    global aThread
    
    try:
        aThread.acquire(3)
    except Exception as e:
        print e
