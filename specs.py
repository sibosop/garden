#!/usr/bin/env python

import json



specs = {}
def setup(path):
  global specs
  with open(path) as f:
    specs = json.load(f)
  