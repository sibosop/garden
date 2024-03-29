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
from singleton import Singleton
from debug import Debug


class TrackManager(metaclass=Singleton):
  def __init__(self):
    self.name = "TrackManager"
    self.baseTime = time.time()
    self.currentSound = {'file':""}
    self.numEvents=0
    self.buffers = {}
    self.rootDir = Specs().s['rootDir']
    self.octaves = Specs().s['octaves']
    self.tunings = {}
    self.ecount = 0
    self.eventThreads=[]
    self.speedChangeMax = Specs().s['speedChangeMax']
    self.speedChangeMin = Specs().s['speedChangeMin']
    self.soundMinVol = Specs().s['soundMinVol']
    self.soundMaxVol = Specs().s['soundMaxVol']
    cent = 2 ** (1/1200)
    print (cent)
    for k in Specs().s['tunings'].keys():
      self.tunings[k] = []
      for t in Specs().s['tunings'][k]:
        if "/" in t:
          num,den = t.split("/")
          self.tunings[k].append(float(num)/float(den))
        else:
          val = cent ** float(t)
          print(val)
          self.tunings[k].append(val)
    for c in Specs().s['collections']:
      Debug().p ("c:%s"%c)
      for l in Specs().s[c]:
        Debug().p ("l:%s"%l)
        for f in Specs().s[l['list']]:
          Debug().p ("f:%s"%f['name'])
          try:
            path = self.rootDir + '/' + f['name']
            buffer = pygame.mixer.Sound(file=path)
            if f['name'] in self.buffers:
              Debug().p("skipping %s"%f['name'])
            else:
              self.buffers[f['name']] = buffer
          except Exception as e:
            print ("make Buffers:",e)
            
  
  def startEventThread(self):
    Debug().p("startEventThread")
    self.ecount += 1
    t=gardenTrack(self.ecount)
    self.eventThreads.append(t)
    self.eventThreads[-1].setDaemon(True)
    self.eventThreads[-1].start()

  def stopEventThread(self):
    Debug().p("stopEventThread")
    if len(self.eventThreads) != 0:
      t = self.eventThreads.pop()
      t.stop()
    else:
      print("trying to stop thread when list is empty")


  def changeNumGardenThreads(self,n):
    self.numEvents = n
    print("changing number of threads from "
                      +str(len(self.eventThreads))+ " to "+str(n))
    while len(self.eventThreads) != n:
      if len(self.eventThreads) < n:
        self.startEventThread()
      elif len(self.eventThreads) > n:
        self.stopEventThread()
  
    return True
      
  @staticmethod
  def speedx(sound, factor):
    rval = None
    try:
      Debug().p("speedx factor:"+str(factor))
      sound_array = pygame.sndarray.array(sound)
      """ Multiplies the sound's speed by some `factor` """
      indices = np.round( np.arange(0, len(sound_array), factor) )
      indices = indices[indices < len(sound_array)].astype(int)
      rval = pygame.sndarray.make_sound(sound_array[ indices.astype(int) ])
    except Exception as e:
      print("speedx:"+str(e))
    return rval
    
  @staticmethod
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
    Debug().p("busy channels:"+str(TrackManager.getBusyChannels()))
    Debug().p("l: "+str(l) + " r:"+str(r))
    eventChan.set_volume(l,r)
    eventChan.play(sound)
    eventChan.set_endevent()
    
  @staticmethod
  def getBusyChannels():
    count = 0
    for i in range(pygame.mixer.get_num_channels()):
      if pygame.mixer.Channel(i).get_busy():
        count +=1
    return count
  
  @staticmethod
  def playFile(path):
    Debug().p ("playing %s"%path)
    sound = pygame.mixer.Sound(file=path)
    playSound(sound,.5,.5)

  def getFactor(self,cs):
    Debug().p ("getFactor on: %s"%cs)
    rval = 1.0
    if 'tuning' in cs.keys() and cs['tuning'] in self.tunings.keys():
      ts = self.tunings[cs['tuning']]
      i = 0
      if 'rlist' in cs.keys():
        i = random.choice(cs['rlist'])
      else:
        i = random.randint(0,len(ts)-1)
      tc = ts[i]
      if 'olist' in cs.keys():
        i = random.choice(cs['olist'])
      else:
        i = random.randint(0,len(self.octaves)-1)
      oc = self.octaves[i]
      Debug().p("tc: %f oc: %f"%(tc,oc))
      rval = tc * oc
    else:
      speedChangeMax = self.speedChangeMax;
      speedChangeMin =  self.speedChangeMin;
      if 'speedList' in cs.keys():
        speedChangeMin = cs['speedList'][0];
        speedChangeMax = cs['speedList'][-1];
      Debug().p ("default tuning  min %f max %f"%(speedChangeMin,speedChangeMax))
      rval = ((speedChangeMax-speedChangeMin) * random.random()) + speedChangeMin
    
    Debug().p ("factor: %f"%rval)
    return rval
  

class Msg(object):
  sound=1
  pulse=2
  def __init__(self,type=sound,data=None):
    self.type = type
    self.data = data  
    
    
class gardenTrack(threading.Thread):    
  def __init__(self,c):
    super(gardenTrack,self).__init__()
    
    self.playList = {}
    self.playList['events'] = []
    self.runState = True
    self.name = "GardenTrack-"+str(c)
    self.currentSound=None
    self.queue = queue.Queue()
    self.currentDir = os.getcwd()
    divs = 1.0 / float(TrackManager().numEvents-1)
    self.rRatio = float(c-1) * divs
    self.lRatio = 1.0 - self.rRatio  
    Debug().p ("%s starting with lRatio: %f rRatio %f"%(self.name,self.lRatio,self.rRatio))
    
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
    ts = None
    tsbase = None
    file = None
    isPulser = False
    pulseCount = 1
    tmgr=TrackManager()
    cs = None
    while self.isRunning():
      try:
        try:
          if ts is not None:
            tsbase = ts+time.time()
          msg = self.queue.get(timeout=ts)
          if msg.type == Msg.sound:
            cs = msg.data
            file = cs['name']
            if 'plist' in cs.keys():
              ts = None
              isPulser = True
              pulseCount = random.choice(cs['plist'])
            else:
              isPulser = False
              ts = random.uniform(Specs().s['minStart'],Specs().s['maxStart']);
            Debug().p("%s: changing to %s ts %s"%(self.name,file,ts))
            continue
          if msg.type == Msg.pulse:
            if cs is None:
              continue
            if isPulser:
              pulseCount -= 1
              if pulseCount == 0:
                pulseCount = random.choice(cs['plist'])
                Debug().p("%s: playing pulse"%self.name)
              else:
                continue
            else:
              if ts is not None:
                ts = tsbase - time.time()
                Debug().p("%s: got pulse ts %s"%(self.name,ts))
                continue
          else:
            raise Exception("Bad Queue Type")
        except queue.Empty:
          ts = random.randint(Specs().s['eventMin'],Specs().s['eventMax'])/1000.0;
          if file is None:
            raise Exception("Null File")
        except Exception as e:
          raise e
        #path = rootDir + '/' + file
        Debug().p ("%s: playing: %s"%(self.name,file))
        #sound = pygame.mixer.Sound(file=self.buffers[file])
        factor = tmgr.getFactor(cs);
        sound = None
        nsound = tmgr.speedx(tmgr.buffers[file],factor)
        if nsound is not None:
          sound = nsound
        else:
          sound = tmgr.buffers[file]
        v = random.uniform(tmgr.soundMinVol,tmgr.soundMaxVol);
        lVol = v * self.lRatio
        rVol = v * self.rRatio
        Debug().p (" %s lVol %f rVol %f lRatio %f rRatio %f"%(self.name,lVol,rVol,self.lRatio,self.rRatio))
        event = {}
        event['vol'] = v
        event['factor'] = factor
        event['file'] = file
        Debug().p ("%s: garden baseTime %s"%(self.name,TrackManager().baseTime))
        event['time'] = time.time() - TrackManager().baseTime
        self.playList['events'].append(event)
        tmgr.playSound(sound,lVol,rVol) 
        Debug().p(self.name+": next play:"+str(ts)+"\n----")
      except Exception as e:
        print(self.name+": error on "+file+":"+str(e))
        break
      
    print(self.name + " exiting")
    


  
