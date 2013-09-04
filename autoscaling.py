#!/usr/bin/env python
# -*- coding: utf-8 -*-

import importlib
import lib.autoscaling

PROFILES = [
  'dev-web',
]

for P in PROFILES:
  ns = importlib.import_module('conf.autoscaling.%s' % P)
  
  conf = ns.CONF
  print('Executing %s' % P)
  lib.autoscaling.setup(ns.CONF)
