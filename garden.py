#!/usr/bin/env python
import os
import datetime
import gardenTrack
import gardenPlayer
import gardenSoundFile
import sys
import random
import pygame

import time
import gardenPlayer
import specs



def usage():
  print "usage:",sys.argv[0]," spec file"
  os._exit(-1)

if __name__ == '__main__':
  random.seed()
  pname = sys.argv[0]
  os.environ['DISPLAY']=":0.0"
  os.chdir(os.path.dirname(sys.argv[0]))
  print(pname+" at "+datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S'))  
  if len (sys.argv) < 2:
    usage()
  specs.setup(sys.argv[1])
  pygame.mixer.pre_init(frequency=44100, size=-16, channels=2, buffer=4096)
  pygame.init()
  gardenSoundFile.setup()
  gardenTrack.changeNumGardenThreads(specs.numThreads())
  threads = gardenTrack.eventThreads
  pt = gardenPlayer.playerThread(threads)
  pt.setDaemon(True)
  pt.start()
  while True:
    time.sleep(1)
    if pt.done:
      break
      
  print "waiting for channels to be done"
  while True:
    n = pygame.mixer.get_busy()
    print "number busy channels",n
    if n == 0:
      break;
    time.sleep(1)
  print "garden done"

