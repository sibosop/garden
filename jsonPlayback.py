#!/usr/bin/env python
import os
import json
import sys
import time
import datetime
import gardenTrack
import pygame
import random
import argparse
import glob
import threading

debug=True
numEvents = 0
baseTime = time.time()
takesDir = "GardenTakes/"
threads = []


def usage():
  print ("usage:",sys.argv[0]," spec file")
  os._exit(-1)

def playSound(sound,l,r):
  eventChan = None
  eventChan=pygame.mixer.find_channel()
  if eventChan is None:
    pygame.mixer.set_num_channels(pygame.mixer.get_num_channels()+1);
    eventChan=pygame.mixer.find_channel()
  if numEvents == 1:
    eventChan.set_volume(l)
  else:
    eventChan.set_volume(l,r)
  eventChan.play(sound)
  eventChan.set_endevent()
  
class Playback(threading.Thread):
  def __init__(self,c,specs):
    global numEvents
    super(Playback,self).__init__()
    self.runState = True
    self.name = "Playback-"+str(c)
    self.currentDir = os.getcwd()
    self.specs = specs
    if numEvents == 1:
      self.lRatio = 1.0
      self.rRatio = 0
    elif numEvents == 2:
      if c == 1:
        self.lRatio = 1.0
        self.rRatio = 0
      else:
        self.lRatio = 0
        self.rRatio = 1.0
    else:
      print ("numEvents %d thread number %d"%(numEvents,c))
      div = 1.0 / float(numEvents-1)
      self.rRatio = float(c-1) * div
      self.lRatio = 1.0 - self.rRatio  
    if debug: print (self.name,"starting with lRatio:",self.lRatio, "rRatio",self.rRatio)
    
  def run(self):
    global baseTime
    for e in self.specs['events']:
      while e['time'] > (time.time() - baseTime):
        time.sleep(0)
      path = rootDir + '/' + e['file']
      print ("%s: playing %s"%(self.name,path))
      sound = pygame.mixer.Sound(file=path)
      factor = e['factor']
      nsound = gardenTrack.TrackManager.speedx(sound,factor)
      if nsound is not None:
        sound = nsound
      v = e['vol']
      l = v * self.lRatio
      r = v * self.rRatio
      playSound(sound,l,r)
    print ("%s: exiting"%self.name)
    
def waitForThreads():
  print ("waiting for threads to be done")
  done = False
  while True:
    test = []
    for t in threads:
      if t.is_alive():
        test.append(t)
    if len(test) == 0:
        break
    time.sleep(0.25)
  print ("threads done")
    
    
if __name__ == '__main__':
  pname = sys.argv[0]
  os.environ['DISPLAY']=":0.0"
  os.chdir(os.path.dirname(sys.argv[0]))
  print(pname+" at "+datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S'))  
  parser = argparse.ArgumentParser()
  parser.add_argument('-d', '--dir', nargs=1, help='target directory', required=True )
  parser.add_argument('-v', '--voices', nargs='*', default=[], help='voice list [defaults to all]')
  args = parser.parse_args()
  takesDir = "%s/%s"%(takesDir,args.dir[0])
  voices = []
  if len(args.voices) == 0:
    d = "%s/GardenTrack*json"%takesDir
    print ("adding all voices from",d)
    files = glob.glob(d)
    print (files)
    for i in range(1,len(files)+1):
      voices.append(i)
  else:
    for v in args.voices:
      voices.append(int(v))
  print ("voices",voices)
  chans = 2
  if len(voices) == 1:
    chans = 1
  numEvents = len(voices)
  pygame.mixer.pre_init(frequency=44100, size=-16, channels=chans, buffer=4096)
  pygame.init()
  rootDir = os.environ['GARDEN_ROOT_DIR']
  
  # mark
  path = rootDir + '/' + "tudor1.wav"
  sound = pygame.mixer.Sound(file=path)
  playSound(sound,1.0,1.0)
  
  count = 1
  for i in voices:
    with open("%s/GardenTrack-%d.json"%(takesDir,i)) as f:
      specs = json.load(f)
      f.close()
      t = Playback(count,specs)
      t.setDaemon(True)
      count += 1 
      threads.append(t)
  for t in threads:
    t.start()
  
  waitForThreads()
    
  while True:
    n = gardenTrack.TrackManager.getBusyChannels()
    print ("number busy channels",n)
    if n == 0:
      break;
    time.sleep(1)
  