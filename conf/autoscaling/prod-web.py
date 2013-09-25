# -*- coding: utf-8 -*-
from lib import TS_ISO

CONF = {
  'NAME': 'prod-web',
  'REGION': 'us-west-1',

  # Launch Configuration
  'LC': {
    'name': '%(name)s_' + TS_ISO,
    'image_id': 'ami-9e6450db',
    'security_groups': ['sg-7eed0f11'], # SG, ID only, managed elsewhere
    'instance_type': 'm1.small',
    'instance_monitoring': False,
    'user_data': '#!/bin/sh\n/data/bin/update_project.sh prod',
  },
  # Auto Scaling Group
  'ASG': {
    'group_name': "%(name)s" , # Auto Scaling Group name
    'load_balancers': ['prod-web'], # ELB, managed elseware
    'availability_zones': ['us-west-1a'],
    'vpc_zone_identifier': 'subnet-8b3517e3',
    'health_check_type': 'ELB',
    'health_check_period': 60,
    'default_cooldown': 60,
    'min_size': 1,
    'max_size': 12,
  },
  'ASG_TAGS': [
    {'key': 'Name', 'value': '[a] %(name)s'},
    {'key': 'stage', 'value': 'prod'},
    {'key': 'role', 'value': 'web'},
  ],
  'TRIGGERS': [
    {
      'policy': {
        'name': "%(name)s-down", # Handles cloudwatch alarms of the same name
        'adjustment_type': 'PercentChangeInCapacity',
        'scaling_adjustment': '-25',
        'cooldown': '60',
        'min-adjustment-step': '1',
      },
      'alarm': {
        'namespace': 'AWS/EC2',
        'metric': 'CPUUtilization',
        'statistic': 'Average',
        'comparison' : '<=',
        'threshold': '30',
        'period': '60',
        'evaluation_periods': '2',
        'alarm_actions': None,
      }
    },
    {
      'policy': {
        'name': "%(name)s-up", # Handles cloudwatch alarms of the same name
        'adjustment_type': 'PercentChangeInCapacity',
        'scaling_adjustment': '25',
        'cooldown': '60',
        'min-adjustment-step': '1',
      },
      'alarm': {
        'namespace': 'AWS/EC2',
        'metric': 'CPUUtilization',
        'statistic': 'Average',
        'comparison' : '>=',
        'threshold': '75',
        'period': '60',
        'evaluation_periods': '1',
        'alarm_actions': None,
      }
    },
  ], # Triggers
}
