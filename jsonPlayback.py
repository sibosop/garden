#!/usr/bin/env python
import os
import json
import sys
import time
import datetime
import gardenTrack
import pygame
import random

debug=True

def usage():
  print "usage:",sys.argv[0]," spec file"
  os._exit(-1)

def playSound(sound):
  eventChan = None
  eventChan=pygame.mixer.find_channel()
  if eventChan is None:
    pygame.mixer.set_num_channels(pygame.mixer.get_num_channels()+1);
    eventChan=pygame.mixer.find_channel()
  v = random.uniform(.3,.5);
  eventChan.set_volume(v)
  eventChan.play(sound)
  eventChan.set_endevent()
  
if __name__ == '__main__':
  pname = sys.argv[0]
  os.environ['DISPLAY']=":0.0"
  os.chdir(os.path.dirname(sys.argv[0]))
  print(pname+" at "+datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S'))  

  if len (sys.argv) < 2:
    usage()
  pygame.mixer.pre_init(frequency=44100, size=-16, channels=1, buffer=4096)
  pygame.init()
  rootDir = os.environ['GARDEN_ROOT_DIR']
  path = rootDir + '/' + "tudor1.wav"
  sound = pygame.mixer.Sound(file=path)
  playSound(sound)
  
  with open(sys.argv[1]) as f:
    specs = json.load(f)
  baseTime = time.time()
  for e in specs['events']:
    while e['time'] > (time.time() - baseTime):
      time.sleep(0)
    print "playing",e['file']
    path = rootDir + '/' + e['file']
    sound = pygame.mixer.Sound(file=path)
    factor = e['factor']
    nsound = gardenTrack.speedx(sound,factor)
    if nsound is not None:
      sound = nsound
    playSound(sound)  
  print "waiting for channels to be done"
  while True:
    n = pygame.mixer.get_busy()
    print "number busy channels",n
    if n == 0:
      break;
    time.sleep(1)