#!/usr/bin/env python
# -*- coding: utf-8 -*-

import importlib
import lib.autoscale

PROFILES = [
  'dev-web',
  'prod-web',
]

for P in PROFILES:
  ns = importlib.import_module('conf.autoscale.%s' % P)
  
  conf = ns.CONF
  print('Executing %s' % P)
  lib.autoscale.setup(ns.CONF)
