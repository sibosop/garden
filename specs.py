#!/usr/bin/env python

import json

debug=True
tunings={}
specs = {}
def setup(path):
  global specs
  global tunings
  with open(path) as f:
    specs = json.load(f)
  for k in specs['tunings'].keys():
    tunings[k] = []
    for t in specs['tunings'][k]:
      num,den = t.split("/")
      tunings[k].append(float(num)/float(den))
    
      
      
def numThreads():
  return specs['numThreads']
  
  
def minChange():
  return specs['minChange']
  
def maxChange():
  return specs['maxChange']
  
def maxEvents():
  return specs['maxEvents']
  
def fileList(name):
  return specs[name]
  
def checkTuning(name):
  rval = [False]
  if name in tunings.keys():
    rval = True
  return rval
    
def tuning(name):
  return tunings[name]
  