#!/usr/bin/env python
import pygame
import os
import threading
import random
import time
import numpy as np
import gardenSoundFile

debug = False
currentSound = {'file':""}
soundMaxVol = .3
soundMinVol = 0.1
speedChangeMax = 4.0
speedChangeMin = .25
eventMin=100
eventMax=10000
debug=False
numEvents=0

def setup():
  pygame.mixer.pre_init(frequency=44100, size=-16, channels=2, buffer=4096)
  pygame.init()
  
def speedx(sound, factor):
  rval = None
  try:
    if debug: print("speedx factor:"+str(factor))
    sound_array = pygame.sndarray.array(sound)
    """ Multiplies the sound's speed by some `factor` """
    indices = np.round( np.arange(0, len(sound_array), factor) )
    indices = indices[indices < len(sound_array)].astype(int)
    rval = pygame.sndarray.make_sound(sound_array[ indices.astype(int) ])
  except Exception as e:
    print("speedx:"+str(e))
  return rval

def playSound(sound,l,r):
  eventChan = None
  eventChan=pygame.mixer.find_channel()
  if eventChan is None:
    pygame.mixer.set_num_channels(pygame.mixer.get_num_channels()+1);
    eventChan=pygame.mixer.find_channel()
  if debug: print("busy channels:"+str(getBusyChannels()))
  if debug: print("l: "+str(l) + " r:"+str(r))
  eventChan.set_volume(l,r)
  eventChan.play(sound)
  eventChan.set_endevent()
  
def getBusyChannels():
  count = 0
  for i in range(pygame.mixer.get_num_channels()):
    if pygame.mixer.Channel(i).get_busy():
      count +=1
  return count

def playFile(path):
  if debug: print "playing",path
  sound = pygame.mixer.Sound(file=path)
  playSound(sound,.5,.5)

def doJpent():
  rval = ((speedChangeMax-speedChangeMin) 
                        * random.random()) + speedChangeMin
  if debug: print("doJpent")
  return rval

tunings = {
  'jpent' : [1.0,32.0/27.0,4.0/3.0,3.0/2.0,16.0/9.0]
  ,'bfarabi' : [1.0,9.0/8.0,45.0/32.0,131.0/90.0,3.0/2.0,15.0/8.0,31.0/16.0]
  ,'sheng' : [1.0,8.0/7.0,6.0/5.0,5.0/4.0,3.0/2.0,5.0/3.0]
  ,'joy' : [1.0,9.0/8.0,5.0/4.0,3.0/2.0,5.0/3.0,15.0/8.0]
}

octaves = [0.25,0.5,1.0,2.0,4.0]

def getFactor(path):
  rval = 1.0
  try:
    pos = path.find("__");
    
    if pos == -1:
      raise NameError
    
    epos = path.find(".",pos)
    
    if epos == -1:
      raise NameError

    tuning = path[pos+2:epos]
    if debug: print("tuning:"+tuning);
    if tuning not in tunings:
      if debug: print("bad tuning:"+tuning)
      raise NameError
    rval = random.choice(tunings[tuning]) * random.choice(octaves)
  except NameError as exp:
    if debug: print("default tuning for path:"+path)
    rval = ((speedChangeMax-speedChangeMin) * random.random()) + speedChangeMin
  if debug: print("factor:"+str(rval))
  return rval
  
  
class gardenTrack(threading.Thread):
  def __init__(self,c):
    global numEvents
    super(gardenTrack,self).__init__()
    self.runState = True
    self.name = "GardenTrack-"+str(c)
    self.currentSound={'file' : ""}
    self.currentDir = os.getcwd()
    self.rRatio = float(c) / float(numEvents)
    self.lRatio = 1.0 - self.rRatio  
    if debug: print self.name,"starting with lRatio:",self.lRatio, "rRatio",self.rRatio
    
    self.soundMutex = threading.Lock()
    self.runMutex = threading.Lock()
    self.dirMutex = threading.Lock()
    
  def setCurrentDir(self,dir):
    self.dirMutex.acquire()
    self.soundDir = dir
    self.dirMutex.release()
  
  def getCurrentDir(self):
    self.dirMutex.acquire()
    dir = self.soundDir
    self.dirMutex.release()
    return dir
    
  def setCurrentSound(self,cs):
    self.soundMutex.acquire()
    self.currentSound = cs
    self.soundMutex.release()
  
  def getCurrentSound(self):
    self.soundMutex.acquire()
    cs = self.currentSound 
    self.soundMutex.release()
    return cs
    
 
  
    
  def isRunning(self):
    self.runMutex.acquire()
    rval = self.runState
    self.runMutex.release()
    return rval

  def stop(self):
    self.runMutex.acquire()
    self.runState = False
    self.runMutex.release()
    
    
  def run(self):
    print("Garden Track:"+self.name)
    while self.isRunning():
      
      try:
        cs = self.getCurrentSound()
        file=""
        file = cs['file']
        if file == "":
          if debug: print(self.name+": waiting for currentSoundFile");
          time.sleep(2)
          continue
        if debug: print self.name,": playing:",file
        sound = pygame.mixer.Sound(file=file)
        factor = getFactor(file);
        nsound = speedx(sound,factor)
        if nsound is not None:
          sound = nsound
        v = random.uniform(soundMinVol,soundMaxVol);
        lVol = v * self.lRatio
        rVol = v * self.rRatio
        if debug: print self.name,"lVol",lVol,"rVol",rVol,"lRatio",self.lRatio,"rRatio",self.rRatio
        playSound(sound,lVol,rVol)
      except Exception as e:
        print(self.name+": error on "+file+":"+str(e))
      nt = random.randint(eventMin,eventMax)/1000.0;
      if debug: print(self.name+": next play:"+str(nt))
      time.sleep(nt)
      if debug: print(self.name+":back from sleep")
    print("schlub thread " + self.name + " exiting")
    
ecount = 0
eventThreads=[]
def startEventThread():
  if debug: print("startEventThread")
  global eventThreads
  global ecount
  ecount += 1
  t=gardenTrack(ecount)
  eventThreads.append(t)
  eventThreads[-1].setDaemon(True)
  eventThreads[-1].start()

def stopEventThread():
  global eventThreads
  if debug: print("stopEventThread")
  if len(eventThreads) != 0:
    t = eventThreads.pop()
    t.stop()
  else:
    print("trying to stop thread when list is empty")


def changeNumGardenThreads(n):
  global eventThreads
  global numEvents
  numEvents = n
  print("changing number of threads from "
                    +str(len(eventThreads))+ " to "+str(n))
  while len(eventThreads) != n:
    if len(eventThreads) < n:
      startEventThread()
    elif len(eventThreads) > n:
      stopEventThread()
  
  return True

  
