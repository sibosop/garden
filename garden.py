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

numThreads = 5

if __name__ == '__main__':
  random.seed()
  pname = sys.argv[0]
  os.environ['DISPLAY']=":0.0"
  os.chdir(os.path.dirname(sys.argv[0]))
  print(pname+" at "+datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S'))  
  
  gardenTrack.setup()
  gardenTrack.changeNumGardenThreads(numThreads)
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

