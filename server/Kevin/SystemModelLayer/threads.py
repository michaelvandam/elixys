import time
import threading

class baseClass(threading.Thread):
  def __init__(self):
    threading.Thread.__init__(self)
    self.name = "test"
class fakeClass(baseClass):
  def __init__(self):
    baseClass.__init__(self)

  def run(self):
    x = 0
    while x < 5:
      time.sleep(2)
      print "This is the run thread."
      x += 1
    time.sleep(2)
    print "Run thread completed."

class fakeUnitOp():
  def __init__(self):
    pass #not a thread
  def run(self):
    x = 0
    print threading.enumerate()
    while x < 5:
      time.sleep(2)
      print "This is the run thread."
      x += 1


def run_threaded_class():
  thread1 = fakeClass()
  thread1.start()
  x = 0
  while x <10:
    time.sleep(1)
    print "This is the main thread."
    x+=1
  print "Main Thread Completed."
  thread1.join()
  print "Threads joined."
    
def run_threaded_function():
  unitoper = fakeUnitOp()
  mythread = thread.start_new_thread(unitoper.run,())
  x = 0
  print threading.enumerate()
  while x <10:
    time.sleep(1)
    print "This is the main thread."
    x+=1
    
if __name__=="__main__":
  print "Threaded class:"
  run_threaded_class()
  print "Threaded function:"
  #run_threaded_function()
    
 
