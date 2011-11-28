import time
import threading
#!/usr/bin/env python
import signal
import sys


class baseClass(threading.Thread):
  def __init__(self):
    threading.Thread.__init__(self)
    self.name = "test"
class fakeClass(baseClass):
  def __init__(self):
    baseClass.__init__(self)
    self.name = self.__class__.__name__
    daemon = True

  def run(self):
    print self
    x = 0
    while 1:
      time.sleep(2)
      print "\t%s: thread iteration: %s" % (self.name,(x+1))
      x+=1
    print "\t%s: commit suicide." % self.name
    exit()
    print "failed to exit thread"


def run_threaded_class():
  thread1 = fakeClass()
  thread1.setDaemon(True)
  thread1.start()
  
  
  name = thread1.__class__.__name__
  x=1
  while x:
    time.sleep(2)
    x=0
    print "MainThread: I am running."
    for thread in threading.enumerate():
      if thread.__class__.__name__ == name:
        x+=1
        print "MainThread: %s is running." % name
  print "MainThread: %s has died." % name
  
    
if __name__=="__main__":

  try:
    run_threaded_class() 
  except KeyboardInterrupt as k:
    print "Main thread keyboard interrupt."
    exit()
