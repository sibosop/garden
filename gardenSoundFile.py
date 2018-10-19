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

debug=False
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
  
    
  for d in specs.specs['collections']:
      collections.append(d)
  
  if debug: print collections
  currentCollection = collections.pop(0)
  if debug: print "currentCollection:",currentCollection['name']

  timeout = time.time() + currentCollection['time']

      
def testBumpCollection():
  global timeout
  global currentCollection
  #if debug: print "testBumpCollection time",time.time(),"timeout",timeout
  if time.time() > timeout:
    if debug: print "timeout passed"
    if len(collections) == 0:
      return False
    
    currentCollection = collections.pop(0)
    if debug: print "new current collection",currentCollection['name']
    timeout = time.time() + currentCollection['time']
    if debug: print "new timeout",timeout
  return True
    
  




def getSoundEntry():
  global currentCollection
  global fileCollections
  
  keys = specs.fileList(currentCollection['list'])
  if debug: print "collection-list",currentCollection['name'],"-",currentCollection['list'],
  "number of keys:",len(keys)
  done = False
  choices = 0
  numChoices = specs.maxEvents()
  if debug: print "collection:",currentCollection['name']," number of choices:",numChoices," max Events:",maxEvents
  rval = []
  while len(rval) < numChoices:
    choice = random.randint(0,len(keys)-1)
    if debug: print "rval;",rval
    if keys[choice]['name'] in rval:
      continue
    rval.append(keys[choice])
  return rval
  


if __name__ == '__main__':
  while testBumpCollection():
    print "currentCollection:",currentCollection
    time.sleep(1)

