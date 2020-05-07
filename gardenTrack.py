#!/usr/bin/env python
import pygame
import os
import threading
import random
import time
import numpy as np
import gardenSoundFile
from specs import Specs
import garden
import queue



debug = True
currentSound = {'file':""}

numEvents=0

buffers = {}

def makeBuffers():
  rootDir = os.environ['GARDEN_ROOT_DIR']
  for c in Specs().s['collections']:
    if debug: print ("c:",c)
    for l in Specs().s[c]:
      if debug: print ("l:",l)
      for f in Specs().s[l['list']]:
        if debug: print ("f:",f['name'])
        try:
          path = rootDir + '/' + f['name']
          buffer = pygame.mixer.Sound(file=path)
          if f['name'] in buffers:
            if debug: print("skipping %s"%f['name'])
          else:
            buffers[f['name']] = buffer
        except Exception as e:
          print ("make Buffers:",e)
      
  
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
  errCount = 0
  while eventChan is None:
    pygame.mixer.set_num_channels(pygame.mixer.get_num_channels()+1);
    print("increased num channels to %d"%pygame.mixer.get_num_channels())
    eventChan=pygame.mixer.find_channel()
    if eventChan is None:
      errCount += 1
      if errCount == 6:
        raise Exception("Can't allocate a pygame channel")
      print("channel grabbed by other thread, trying again")
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
  if debug: print ("playing",path)
  sound = pygame.mixer.Sound(file=path)
  playSound(sound,.5,.5)

def doJpent():
  speedChangeMax = Specs().s['speedChangeMax']
  speedChangeMin = Specs().s['speedChangeMin']
  rval = ((speedChangeMax-speedChangeMin) 
                        * random.random()) + speedChangeMin
  if debug: print("doJpent")
  return rval



octaves = [0.25,0.5,1.0,2.0,4.0]

def getFactor(cs):
  if debug: print ("getFactor on:",cs)
  rval = 1.0
  if 'tuning' in cs.keys() and cs['tuning'] in Specs().s['tunings'].keys():
    ts = Specs().s['tunings'][cs['tuning']]
    tc = random.choice(ts)
    num,den = tc.split("/")
    td = float(num) / float(den)
    oc = random.choice(octaves)
    if debug: print ("td:",td,"oc:",oc)
    rval = td * oc
  else:
    if debug: print ("default tuning for cs:",cs)
    speedChangeMax = Specs().s['speedChangeMax']
    speedChangeMin = Specs().s['speedChangeMin']
    rval = ((speedChangeMax-speedChangeMin) * random.random()) + speedChangeMin
    
  if debug: print ("factor:",rval)
  return rval
  

class Msg(object):
  def __init__(self,type="sound",data=None):
    self.type = type
    self.data = data  
    
    
class gardenTrack(threading.Thread):    
  def __init__(self,c):
    global numEvents
    super(gardenTrack,self).__init__()
    self.playList = {}
    self.playList['events'] = []
    self.runState = True
    self.name = "GardenTrack-"+str(c)
    self.currentSound=None
    self.queue = queue.Queue()
    self.currentDir = os.getcwd()
    if numEvents <= 1:
      self.rRatio = .5
      self.lRatio = .5
    else:
      divs = 1.0 / float(numEvents-1)
      self.rRatio = float(c-1) * divs
      self.lRatio = 1.0 - self.rRatio  
    if debug: print (self.name,"starting with lRatio:",self.lRatio, "rRatio",self.rRatio)
    
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
    self.queue.put(Msg(data=cs))
  
    
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
    #rootDir = os.environ['GARDEN_ROOT_DIR']
    ts = None
    file = None
    while self.isRunning():
      try:
        try:
          msg = self.queue.get(timeout=ts)
          if msg.type == 'sound':
            cs = msg.data
            file = cs['name']
          else:
            raise Exception("Bad Queue Type")
        except queue.Empty:
          if file is None:
            raise Exception("Null File")
        #path = rootDir + '/' + file
        if debug: print (self.name,": playing:",file)
        #sound = pygame.mixer.Sound(file=buffers[file])
        factor = getFactor(cs);
        sound = None
        nsound = speedx(buffers[file],factor)
        if nsound is not None:
          sound = nsound
        else:
          sound = buffers[file]
        v = random.uniform(Specs().s['soundMinVol'],Specs().s['soundMaxVol']);
        lVol = v * self.lRatio
        rVol = v * self.rRatio
        if debug: print (self.name,"lVol",lVol,"rVol",rVol,"lRatio",self.lRatio,"rRatio",self.rRatio)
        event = {}
        event['vol'] = v
        event['factor'] = factor
        event['file'] = file
        if debug: print ("garden baseTime",garden.baseTime)
        event['time'] = time.time() - garden.baseTime
        self.playList['events'].append(event)
        playSound(sound,lVol,rVol)
        ts = random.randint(Specs().s['eventMin'],Specs().s['eventMax'])/1000.0;
        if debug: print(self.name+": next play:"+str(ts))
      except Exception as e:
        print(self.name+": error on "+file+":"+str(e))
        break
      
    print(self.name + " exiting")
    
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

  
