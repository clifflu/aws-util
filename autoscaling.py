#!/usr/bin/env python
# -*- coding: utf-8 -*-

from lib import *

from boto.ec2.autoscale import LaunchConfiguration
from boto.ec2.autoscale import AutoScalingGroup
from boto.ec2.autoscale import AutoScaleConnection
from boto.ec2.autoscale import Tag
from boto.ec2.autoscale import ScalingPolicy

from boto.ec2.cloudwatch import connect_to_region
from boto.ec2.cloudwatch import MetricAlarm

conn = AutoScaleConnection()

NAME = 'dev-web' # Name, General
REGION = 'us-west-1'

#
# Launch Configuration
#
LC = {
  'name': '%s_%s' % (NAME, TS_ISO),
  'image_id': "ami-f25d77b7",
  'security_groups': ['sg-021eff6d'], # SG, ID only, managed elsewhere
  'instance_type': 't1.micro',
  'instance_monitoring': False,
}

lc = LaunchConfiguration(**LC)
conn.create_launch_configuration(lc)

#
# Auto Scaling Group
#
ASG = {
  'group_name': NAME, # Auto Scaling Group name
  'load_balancers': [NAME], # ELB, managed elseware
  'availability_zones': ['us-west-1a'],
  'vpc_zone_identifier': 'subnet-7c0e7114',
  'launch_config':lc,
  'health_check_type': 'ELB',
  'health_check_period': 60,
  'default_cooldown': 60,
  'min_size': 1,
  'max_size': 12,
}

groups = conn.get_all_groups(names=[NAME])
if (len(groups) > 0):
  # update
  asg = groups[0]
  for k in ASG :
    # asg not iterable, try-except to make sure asg[k] exists
    try: asg.__getattribute__(k)
    except: continue
    asg.__setattr__(k, ASG[k])

  asg.launch_config_name = LC['name']
  asg.update()
else:
  #create
  asg = AutoScalingGroup(**ASG)
  conn.create_auto_scaling_group(asg)

#
# ASG Tags
#
ASG_TAGS = [
  {
    'key': 'Name',
    'value': '[a] %s' % NAME,
    'propagate_at_launch': True,
  },
  {
    'key': 'serves',
    'value': 'shared',
    'propagate_at_launch': True,
  },
  {
    'key': 'stage',
    'value': 'dev',
    'propagate_at_launch': True,
  },
  {
    'key': 'Role',
    'value': 'web',
    'propagate_at_launch': True,
  },
]
tags = [
    Tag(**dict(x.items() + [('resource_id', ASG['group_name'])])) for x in ASG_TAGS
]
conn.create_or_update_tags(tags)

#
# Triggers (Scaling Policy / Cloudwatch Alarm)
#
conn_cw = connect_to_region(REGION)
alarm_dim = {'AutoScalingGroupName': ASG['group_name']}

TRIGGERS = [
  {
    'policy': {
      'name': "%s-down" % NAME, # Handles cloudwatch alarms of the same name
      'as_name': NAME,
      'adjustment_type': 'PercentChangeInCapacity',
      'scaling_adjustment': '-25',
      'cooldown': '60',
      'min-adjustment-step': '1',
    },
    'alarm': {
      'name':'%s-down' % NAME,
      'namespace': 'AWS/EC2',
      'metric': 'CPUUtilization',
      'statistic': 'Average',
      'comparison' : '<=',
      'threshold': '30',
      'period': '60',
      'evaluation_periods': '2',
      'alarm_actions': None,
      'dimensions': alarm_dim,
    }
  },
  {
    'policy': {
      'name': "%s-up" % NAME, # Handles cloudwatch alarms of the same name
      'as_name': NAME,
      'adjustment_type': 'PercentChangeInCapacity',
      'scaling_adjustment': '25',
      'cooldown': '60',
      'min-adjustment-step': '1',
    },
    'alarm': {
      'name':'%s-up' % NAME,
      'namespace': 'AWS/EC2',
      'metric': 'CPUUtilization',
      'statistic': 'Average',
      'comparison' : '>=',
      'threshold': '80',
      'period': '60',
      'evaluation_periods': '1',
      'alarm_actions': None,
      'dimensions': alarm_dim,
    }
  },
]

for T in TRIGGERS:
  # Policies are safely overwritten, so not checked for existence
  conn.create_scaling_policy(ScalingPolicy(**T['policy']))
  policy = conn.get_all_policies(as_group=ASG['group_name'], policy_names=[T['policy']['name']])[0]

  T['alarm']['alarm_actions'] = [policy.policy_arn]
  hits = conn_cw.describe_alarms(alarm_names=[T['alarm']['name']])

  conn_cw.create_alarm(MetricAlarm(**T['alarm']))




