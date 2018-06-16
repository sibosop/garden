#!/usr/bin/env python
import collections
import csv
import os
import sys
import glob
import random
import syslog
import copy
import threading
import json
import shutil
import gardenTrack
import time
import specs

debug=True
listMutex=threading.Lock()
maxEvents = 2
collections = []
currentCollection = ""
timeout = 0
rootDir = ""


def setup():
  global currentCollection
  global collections
  global timeout
  global rootDir
  currentCollection = ""
  rootDir = os.environ['GARDEN_ROOT_DIR']
    
  if 'dirs' not in specs.specs:
    raise Exception("no dirs in specs")
  for d in specs.specs['dirs']:
    if 'time' not in d:
      raise Exception("no time spec in "+d)
    if 'name' not in d:
      raise Exception("no name spec in "+d) 
    collections.append(d)
  
  if debug: print collections
  currentCollection = collections.pop(0)
  if debug: print "currentCollection:",currentCollection

  timeout = time.time() + currentCollection['time']


def setMaxEvents(m):
  global maxEvents
  test = int(m)
  if test > 0:
    maxEvents = test
  if debug: print("setMaxEvents maxEvents:"+str(maxEvents))
  status = { 'status' : 'ok' }
  rval = json.dumps(status)
  return rval 
      
def testBumpCollection():
  global timeout
  global currentCollection
  #if debug: print "testBumpCollection time",time.time(),"timeout",timeout
  if time.time() > timeout:
    if debug: print "timeout passed"
    if len(collections) == 0:
      return False
    
    currentCollection = collections.pop(0)
    if debug: print "new current collection",currentCollection
    timeout = time.time() + currentCollection['time']
    if debug: print "new timeout",timeout
  return True
    
  




def getSoundEntry():
  global currentCollection
  global fileCollections
  
  colDir = rootDir + "/" + currentCollection['name']
  if debug: print "colDir:",colDir
  keys = glob.glob(colDir+"/*.wav")
  
  if debug: print "currentCollection:",currentCollection,"number of keys:",len(keys)
  done = False
  choices = 0
  numChoices = maxEvents
  if debug: print "collection:",currentCollection," number of choices:",numChoices," max Events:",maxEvents
  rval = []
  while len(rval) < numChoices:
    choice = random.randint(0,len(keys)-1)
    if debug: print "rval;",rval
    if keys[choice] in rval:
      continue
    rval.append(keys[choice])
  return rval
  


if __name__ == '__main__':
  while testBumpCollection():
    print "currentCollection:",currentCollection
    time.sleep(1)

