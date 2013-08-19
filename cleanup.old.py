#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Delete all (unused) launch configurations
#
import sys
import json

from lib.awscli import *
from conf import *


#
# Auto Scaling Groups
#
print("\n[%s]: Truncating empty auto scaling groups " % sys.argv[0])
bucket = aws_json(AS, 'describe-auto-scaling-groups')

for item in bucket['AutoScalingGroups']:
  name = item['AutoScalingGroupName']
  print("\t* Deleting %s" % name)
  try: aws_json(AS, 'delete-auto-scaling-group', **{'auto-scaling-group-name': name})
  except: pass

#
# Launch Configs
#
print("\n[%s]: Truncating (unsed) launch configs" % sys.argv[0])
lcs = aws_json(AS, 'describe-launch-configurations')

for lc in lcs['LaunchConfigurations']:
  name = lc['LaunchConfigurationName']
  print("\t* Deleting %s" % name)
  try: aws_json(AS, 'delete-launch-configuration', **{'launch-configuration-name': name})
  except: pass

#
# Scaling Policy
#
# Policies with alarms attached gets deleted, 
# so requires extra check
#
print("\n[%s]: Truncating (unsed) scaling policies" % sys.argv[0])
bucket = aws_json(AS, 'describe-policies')

for item in bucket['ScalingPolicies']:
  name = item['PolicyName']
  if (len(item['Alarms']) > 0):
    print('\t* Found %s in use' % name)
  else:
    print('\t* Found %s unused, deleting' % name)
    try: aws_json(AS, 'delete-policy', **{'policy-name': name, 'auto-scaling-group-name': item['AutoScalingGroupName']})
    except: pass

##
# Security Group
#
if False:
  print("\n[%s]: Truncating (unsed) security groups" % sys.argv[0])
  bucket = aws_json('ec2', 'describe-security-groups')

  for item in bucket['SecurityGroups']:
    name = item['GroupName']
    print("\t* Deleting %s" % name)
    try: aws_json('ec2', 'delete-security-group', **{'group-name': name})
    except: pass

