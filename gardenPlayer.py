#!/usr/bin/env python

import threading
import time
import subprocess
import glob
import random
import json
import os
import sys
import gardenSoundFile
import pygame
import specs

debug = False

playerMutex=threading.Lock()

def enable(val):
  global enabled
  playerMutex.acquire()
  enabled = val
  playerMutex.release()
  if debug: print("player enabled:"+str(enabled))

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
    while gardenSoundFile.testBumpCollection():
      try:
        #print self.name,"time",time.time(),"stime",stime
        if time.time() > stime:
          entry = gardenSoundFile.getSoundEntry()
          if debug: print "player choosing ",entry,
          count = 0
          for t in self.tList:
            choice = random.choice(entry)
            #choice = entry[count]
            #count += 1
            #if count == len(entry):
              #count = 0
            if debug: print "sending ",choice," request to ",t.name
            t.setCurrentSound(choice)
          offset = random.randint(specs.minChange(),specs.maxChange())
          stime = time.time() + offset
          if debug: print "next change:",offset
          n = pygame.mixer.get_busy()
          if debug: print "number busy channels",n
        time.sleep(1)
      except Exception as e:
        print("player error: "+repr(e))
        os._exit(3)
    for t in self.tList:
      t.stop()
    self.done = True
