# -*- coding: utf-8 -*-
from lib import TS_ISO

CONF = {
  'NAME': 'dev-web',
  'REGION': 'us-west-1',
  'BRANCH': 'develop',

  # Launch Configuration
  'LC': {
    'name': '%(name)s_' + TS_ISO,
    'image_id': 'ami-0c536749',
    # SG, ID only, managed elsewhere
    'security_groups': ['sg-021eff6d', 'sg-b09c70df'],
    'instance_type': 't1.micro',
    'instance_monitoring': False,
    'user_data': '#!/bin/sh\n/data/bin/cloud_init.sh dev',
  },
  # Auto Scaling Group
  'ASG': {
    'group_name': "%(name)s" , # Auto Scaling Group name
    'load_balancers': ['dev-web'], # ELB, managed elseware
    'availability_zones': ['us-west-1a'],
    'vpc_zone_identifier': 'subnet-7c0e7114',
    'health_check_type': 'ELB',
    'health_check_period': 60,
    'default_cooldown': 60,
    'min_size': 1,
    'max_size': 12,
  },
  'ASG_TAGS': [
    {'key': 'Name', 'value': '[a] %(name)s'},
    {'key': 'stage', 'value': 'dev'},
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
