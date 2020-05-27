#!/usr/bin/env python
import os
import threading
import time
from specs import Specs
import gardenTrack

import queue
from singleton import Singleton
from debug import Debug

class Pulser(threading.Thread):
  def __init__(self):
    super(Pulser,self).__init__()
    self.name = "Pulser"
    self.pulseTime = None
    self.running = True
    self.threads = gardenTrack.TrackManager().eventThreads
    
    if "pulseTime" in Specs().s.keys():
      self.pulseTime = Specs().s["pulseTime"]
  
  def stop(self):
    self.running = False
    
  
  def run(self):
    if self.pulseTime is None:
      Debug().p("%s: no pulse time, exiting"%(self.name))
      return
    Debug().p("%s: starting thread with pulse time %f"%(self.name,self.pulseTime))
    while self.running:
      for t in self.threads:
        Debug().p("%s: sending pulse"%(self.name))
        t.queue.put(gardenTrack.Msg(type=gardenTrack.Msg.pulse))
      time.sleep(self.pulseTime)
    Debug().p("%s: exiting"%(self.name))   
      
      
      
      
    
  
    