import time
from threading import Thread

class MyThread(Thread):
  def __init__(self,name):
    Thread.__init__(self)
    self.name = name
  
  def run(self):
    start =  time.time()
    end = 0;
    while (end-start<1):
      print ("Thread test %s." % self.name)
      end = time.time()
  
        
def test():
  thr1=MyThread("one")
  thr1.start()
  thr2=MyThread("two")
  thr2.start()
  thr1.join()
  thr2.join()
    
if __name__=="__main__":
    test()
    
    
 
"""
def myfunction(string,sleeptime,lock,*args):
    while 1:
	#entering critical section
        lock.acquire() 
        print string," Now Sleeping after Lock acquired for ",sleeptime
        time.sleep(sleeptime) 
        print string," Now releasing lock and then sleeping again"
        lock.release()
	#exiting critical section
        time.sleep(sleeptime) # why?

if __name__=="__main__":

    lock=thread.allocate_lock()
    thread.start_new_thread(myfunction,("Thread No:1",2,lock))
    thread.start_new_thread(myfunction,("Thread No:2",2,lock))

    while 1:pass
"""