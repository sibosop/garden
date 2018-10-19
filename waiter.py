#!/usr/bin/env python

import specs
import random
import time
import threading
debug = False

waitList = []
    
class waiterThread(threading.Thread):
  def __init__(self):
    super(waiterThread,self).__init__()
    self.done = False
    self.name= "Waiter"
    self.lock = threading.Lock()
    
  def run(self):
    global waitList
    print "%s"%(self.name)
    waitQuant = specs.specs['waitQuant']
    while not self.done:
      time.sleep(waitQuant)
      
      waits = []
      
      #print "%s: doing check loop waitlist size %d"%(self.name,len(waitList))
      for w in waitList:
        #print "%s checking %s"%(self.name,w)
        w['counter'] = w['counter'] + 1
        if w['counter'] >= w['count']:
           w['event'].set()
           w['event'].clear()
        else:
          waits.append(w)
      self.lock.acquire()
      waitList = waits
      self.lock.release()
      
  def wait(self,thread,cs):
    global waitList
    if debug: print "%s wait: %s"%(thread.name,cs)
    wait = None
    if 'wait' in cs:
      wa = cs['wait'];
      if 'choice' in wa:
         wait = random.choice(specs.specs[wa['choice']])
         print("%s: wait %d"%(thread.name,wait))
         
    if wait == None:
      nt = random.randint(specs.specs['eventMin'],specs.specs['eventMax'])/1000.0;
      if debug: print(self.name+"no wait spec: next play:"+str(nt))
      time.sleep(nt)
    else:
       w={}
       w['event'] = threading.Event()
       w['counter'] = 0
       w['count'] = wait
       w['name'] = thread.name
       self.lock.acquire()
       waitList.append(w)
       self.lock.release()
       if debug: print "%s: waiting on %s"%(thread.name,waitList)
       w['event'].wait()
    if debug: print("%s: back from sleep"%(thread.name))
       
     
  
    
    
if __name__ == '__main__':
  import sys
  import os
  import argparse
  import datetime
  import gardenSoundFile
  import random
  
  random.seed()
  pname = sys.argv[0]
  os.environ['DISPLAY']=":0.0"
  os.chdir(os.path.dirname(sys.argv[0]))
  print(pname+" at "+datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S'))  
  parser = argparse.ArgumentParser()
  parser.add_argument('-s', '--spec', nargs=1, help='specify spec file', required=True )
  parser.add_argument('-o','--output', action = 'store_true',help='save session to GardenTakes directory')
  args = parser.parse_args()
  specFile = args.spec[0]
  print "using spec:",specFile
  specs.setup(specFile)
  gardenSoundFile.setup()
  waiter = waiterThread()
  waiter.setDaemon(True)
  waiter.start()
  while True:
    cs = gardenSoundFile.getSoundEntry()
    print cs
    myThread = threading.currentThread()
    entry = random.choice(cs)
    waiter.wait(myThread,entry)
  