#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json

from lib.awscli import *
from conf import *

try:
  #
  # Launch Configs
  #

  # launch configs cannot be updated, delete first
  ret = aws_json(AS, "create-launch-configuration", **{
    'launch-configuration-name': AS_CONFIG_NAME,
    'image-id': IN_AMI_ID,
    'instance-type': IN_TYPE,
    'instance-monitoring': '{"Enabled":false}',
    'security-groups': '["%s"]' % IN_SG,
  })
  print(ret)

  #
  # Auto Scaling Group
  #
  # would fail for duplicate group, try-catch;
  _param = {
    'auto-scaling-group-name': AS_NAME,
    'launch-configuration-name': AS_CONFIG_NAME,
    'min-size': AS_WORKER_MIN,
    'max-size': AS_WORKER_MAX,
    'default-cooldown': AS_COOLDOWN,
    'availability-zones': PROFILE_AZ,
    'load-balancer-names': '["%s"]' % LB_NAME,
    'tags': json.dumps([
      {"Key": "Name", "Value": "[a] dev-web", "PropagateAtLaunch": True},
      {"Key": "role", "Value": "web", "PropagateAtLaunch": True},
      {"Key": "stage", "Value": "dev", "PropagateAtLaunch": True},
      {"Key": "serves", "Value": "shared", "PropagateAtLaunch": True},
    ]),
  }

  try:
    ret = aws_json(AS, "create-auto-scaling-group", **_param)
  except CalledProcessError as e:
    # tags and load-balancer-names cannot be updated by this directive, 
    # call create-or-update-tags for tags instead.
    del _param['load-balancer-names']
    del _param['tags']
    ret = aws_json(AS, "update-auto-scaling-group", **_param)
  finally:
    print(ret)

  #
  # Scaling Policy
  #

  ret = aws_json(AS, "put-scaling-policy", **{
    'auto-scaling-group-name': AS_NAME,
    'policy-name': "%s_up" % AS_NAME,
    'scaling-adjustment': '25',
    'adjustment-type': 'PercentChangeInCapacity',
    'cooldown': AS_COOLDOWN,
    'min-adjustment-step': '1',
  })
  print(ret)

  ret = aws_json(AS, "put-scaling-policy", **{
    'auto-scaling-group-name': AS_NAME,
    'policy-name': "%s_down" % AS_NAME,
    'scaling-adjustment': '-25',
    'adjustment-type': 'PercentChangeInCapacity',
    'cooldown': AS_COOLDOWN,
    'min-adjustment-step': '1',
  })
  print(ret)
except Exception as e:
  raise e
