#!/usr/bin/env python
import os
import random
import parser
import sys
import time
import argparse
import datetime
import signal
import traceback
import pygame
    
pname = sys.argv[0]
os.environ['DISPLAY']=":0.0"
home = os.environ['HOME']
os.chdir(os.path.dirname(sys.argv[0]))
sys.path.append("sibcommon")
defaultSpecFile = "%s/%s"%("speclib","improv.json")
from specs import Specs
from utils import print_dbg
from utils import setDebug
from soundFile import SoundFile
from threadPlayer import ThreadPlayer
from soundTrack import SoundTrackManager
from midiHandler import MidiHandler
defaultSoundDir = "%s/%s"%(home,"Users/brian/sibosopLocal/music/Music20161008/Clips/schlubFull/")

takesDir = ""

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


class ServiceExit(Exception):
    """
    Custom exception which is used to trigger the clean exit
    of all running threads and the main program.
    """
    pass

def service_shutdown(signum, frame):
    print_dbg('Caught signal %d' % signum)
    raise ServiceExit


signal.signal(signal.SIGTERM, service_shutdown)
signal.signal(signal.SIGINT, service_shutdown)

def slider(e):
  print_dbg("%s callback num %d value %d"%(e.event,e.num,e.value))
  
if __name__ == '__main__':
  try:
    random.seed()
    print_dbg(pname+" at "+datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')) 
    pygame.mixer.pre_init(frequency=44100, size=-16, channels=2, buffer=4096)
    pygame.init()
     
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--spec', nargs=1, help='specify spec file', default=[defaultSpecFile])
    parser.add_argument('-v','--verbose', action = 'store_true',help='set verbose mode')
    parser.add_argument('-o','--output', action = 'store_true',help='save session to GardenTakes directory')
    parser.add_argument('-d','--soundDir',nargs=1,help='specify sound directory')
    args = parser.parse_args()
    setDebug(args.verbose)
    if args.output:
      makeTakesDir()   
    print "takesDir:",takesDir 
    
      
  
# Singletons
    print_dbg("using spec: %s"%args.spec[0])
    Specs(args.spec[0])
    soundDir = Specs().s["defaultSoundDir"]
    if args.soundDir is not None:
      soundDir = args.soundDir[0]
      
    SoundFile()
    SoundTrackManager(soundDir)
    mh = MidiHandler(['nano'])
    mh.setDaemon(True)
    mh.start()
    pt = ThreadPlayer()
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
      for t in SoundTrackManager().eventThreads:
        desc = json.dumps(t.playList)
        fname = takesDir+"/"+t.name+".json"
        print "saving:",fname
        f = open(fname,"w")
        f.write(desc)
        f.close()
    print "garden done"

    
  except ServiceExit:
    print("Exiting on interrupt")
  except Exception, e:
    traceback.print_exc()
  
