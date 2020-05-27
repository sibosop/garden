#!/usr/bin/env python
import threading
import time
import subprocess
import glob
import random
import json
import os
import sys
from soundFile import SoundFile
import pygame
from specs import Specs
from debug import Debug
debug = False

playerMutex=threading.Lock()

def enable(val):
  global enabled
  playerMutex.acquire()
  enabled = val
  playerMutex.release()
  Debug().p("player enabled:"+str(enabled))

def isEnabled():
  global enabled
  playerMutex.acquire()
  rval = enabled
  playerMutex.release()
  return rval

class playerThread(threading.Thread):
  def __init__(self,tList):
    super(playerThread,self).__init__()
    self.tList = tList
    self.done = False
    self.name= "Player"
    
  def run(self):
    stime = time.time()
    while SoundFile().testBumpCollection():
      try:
        #print (self.name,"time",time.time(),"stime",stime)
        if time.time() > stime:
          entry = SoundFile().getSoundEntry()
          Debug().p ("player choosing %s "%entry)
          count = 0
          for t in self.tList:
            choice = entry[count]
            count += 1
            if count == len(entry):
              count = 0
            Debug().p ("sending %s to %s"%(choice,t.name))
            t.setCurrentSound(choice)
          offset = random.randint(Specs().s['minChange'],Specs().s['maxChange'])
          stime = time.time() + offset
          Debug().p ("next change: %d"%offset)
          n = pygame.mixer.get_busy()
          Debug().p ("number busy channels %d"%n)
        time.sleep(1)
      except Exception as e:
        print("player error: "+repr(e))
        os._exit(3)
    for t in self.tList:
      t.stop()
    self.done = True
