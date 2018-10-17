#!/usr/bin/env python
import os
import datetime
import gardenTrack
import gardenPlayer
import gardenSoundFile
import sys
import random
import pygame
import json
import argparse
import glob

import time
import gardenPlayer
import specs
debug = True
baseTime = time.time()
takesDir = ""

      

def usage():
  print "usage:",sys.argv[0]," spec file"
  os._exit(-1)
  
def makeTakesDir():
  global takesDir
  print "creating takes dir"
  rootDir = "GardenTakes/*.*"
  i = 0
  done = False
  files = glob.glob(rootDir)
  while True:
    found = False
    for f in files:
      #print f
      try:
        n = f.rindex(".")
      except:
        continue
      test = int(f[n+1:])
      #print "test:",test
      if test == i:
        found = True
        i += 1
        break
    if not found:
      takesDir = "GardenTakes/Take.%d"%i
      print "making",takesDir
      os.mkdir(takesDir)
      break
    
    
    
      
  

if __name__ == '__main__':
  random.seed()
  pname = sys.argv[0]
  os.environ['DISPLAY']=":0.0"
  os.chdir(os.path.dirname(sys.argv[0]))
  print(pname+" at "+datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S'))  
  parser = argparse.ArgumentParser()
  parser.add_argument('-s', '--spec', nargs=1, help='specify spec file', required=True )
  parser.add_argument('-o','--output', action = 'store_true',help='save session to GardenTakes directory')
  args = parser.parse_args()
  specFile = args.spec[0]
  print "using spec:",specFile
  specs.setup(specFile)
  if args.output:
    makeTakesDir()   
  print "takesDir:",takesDir
  
  pygame.mixer.pre_init(frequency=44100, size=-16, channels=2, buffer=4096)
  pygame.init()
  gardenSoundFile.setup()
  gardenTrack.makeBuffers()
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
    
  if takesDir != "":
    for t in threads:
      desc = json.dumps(t.playList)
      fname = takesDir+"/"+t.name+".json"
      print "saving:",fname
      f = open(fname,"w")
      f.write(desc)
      f.close()
  print "garden done"

