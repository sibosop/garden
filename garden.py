#!/usr/bin/env python
import os
import sys
sys.path.append("sibcommon")
sys.path.append("seqlib")
sys.path.append("SpecFiles")
import datetime

import gardenTrack 
import gardenPlayer
from soundFile import SoundFile
from pulser import Pulser

import random
import pygame
import json
import argparse
import glob

import time
import gardenPlayer
from specs import Specs
import signal

from debug import Debug

takesDir = ""
      

def usage():
  print ("usage:",sys.argv[0]," spec file")
  os._exit(-1)
  
def makeTakesDir():
  global takesDir
  print ("creating takes dir")
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
      print ("making",takesDir)
      os.mkdir(takesDir)
      break
    
class ServiceExit(Exception):
    """
    Custom exception which is used to trigger the clean exit
    of all running threads and the main program.
    """
    pass

def service_shutdown(signum, frame):
    Debug().p('Caught signal %d' % signum)
    raise ServiceExit
    
    

if __name__ == '__main__':
  pname = sys.argv[0]
  signal.signal(signal.SIGTERM, service_shutdown)
  signal.signal(signal.SIGINT, service_shutdown)
  print("%s at %s"%(pname,datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')))
  random.seed()
 
  os.environ['DISPLAY']=":0.0"
  os.chdir(os.path.dirname(sys.argv[0]))
  print(pname+" at "+datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S'))  
  parser = argparse.ArgumentParser()
  parser.add_argument('-s', '--spec', nargs=1, help='specify spec file', required=True )
  parser.add_argument('-o','--output', action = 'store_true',help='save session to GardenTakes directory')
  args = parser.parse_args()
  specFile = args.spec[0]
  print ("using spec:",specFile)
  specs = Specs(specFile)
  if args.output:
    makeTakesDir()   
  print ("takesDir:",takesDir)
  
  
  Debug().enable(specs.s['debug'])
  
  pygame.mixer.pre_init(frequency=44100, size=-16, channels=2, buffer=4096)
  pygame.init()
  SoundFile().setCurrentCollection()
  
  
  
  gardenTrack.TrackManager().changeNumGardenThreads(specs.s["numThreads"])
  threads = gardenTrack.TrackManager().eventThreads
  pulser=Pulser()
  pulser.setDaemon(True)
  pulser.start()
  
  pt = gardenPlayer.playerThread(threads)
  pt.setDaemon(True)
  pt.start()
  while True:
    time.sleep(1)
    if pt.done:
      break
  
  print ("waiting for channels to be done")
  while True:
    n = gardenTrack.TrackManager().getBusyChannels()
    b = pygame.mixer.get_busy()
    print ("number busy channels %d  busy %d"%(n,b))
    if n == 0:
      break;
    time.sleep(1)
    
  if takesDir != "":
    for t in threads:
      desc = json.dumps(t.playList)
      fname = takesDir+"/"+t.name+".json"
      print ("saving:",fname)
      f = open(fname,"w")
      f.write(desc)
      f.close()
  print ("garden done")

