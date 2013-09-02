# -*- coding: utf-8 -*-

from lib import *

from boto.ec2.autoscale import LaunchConfiguration
from boto.ec2.autoscale import AutoScalingGroup
from boto.ec2.autoscale import AutoScaleConnection
from boto.ec2.autoscale import Tag
from boto.ec2.autoscale import ScalingPolicy

from boto.ec2.cloudwatch import connect_to_region
from boto.ec2.cloudwatch import MetricAlarm

out = {}

def setup(CONF):
  global out

  lookup_tbl = {
    'name': CONF['NAME'],
  }

  conn = AutoScaleConnection()

  out['conn'] = conn

  # Launch Configurations
  LC = CONF['LC']
  LC['name'] = LC['name'] % lookup_tbl

  lc = LaunchConfiguration(**LC)
  conn.create_launch_configuration(lc)
  out['lc'] = lc

  # Auto Scaling Group
  ASG = CONF['ASG']
  ASG['group_name'] = ASG['group_name'] % lookup_tbl
  ASG['launch_config'] = lc

  groups = conn.get_all_groups(names=[ASG['group_name']])
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
    out['asg'] = asg
  else:
    #create
    asg = AutoScalingGroup(**ASG)
    conn.create_auto_scaling_group(asg)

  # ASG Tags
  ASG_TAGS = CONF['ASG_TAGS']
  for i in ASG_TAGS:
    if 'propagate_at_launch' not in i:
      i['propagate_at_launch'] = True
    i.key = i.key % lookup_tbl
    i.value = i.value % lookup_tbl

  tags = [
      Tag(**dict(x.items() + [('resource_id', ASG['group_name'])])) for x in ASG_TAGS
  ]
  conn.create_or_update_tags(tags)

  # Triggers (Scaling Policy / Cloudwatch Alarm)
  conn_cw = connect_to_region(REGION)

  TRIGGERS = CONF['TRIGGERS']
  for T in TRIGGERS:
    T['policy']['name'] = T['policy']['name'] % lookup_tbl
    T['policy']['as_name'] = ASG['group_name']
    T['alarm']['dimensions'] = {'AutoScalingGroupName': ASG['group_name']}
    T['alarm']['alarm_actions'] = None

    if 'name' in T['alarm']:
      T['alarm']['name'] = T['alarm']['name'] % lookup_tbl
    else:
      T['alarm']['name'] = T['policy']['name']

    # Policies are safely overwritten, so not checked for existence
    conn.create_scaling_policy(ScalingPolicy(**T['policy']))
    policy = conn.get_all_policies(as_group=ASG['group_name'], policy_names=[T['policy']['name']])[0]

    T['alarm']['alarm_actions'] = [policy.policy_arn]
    hits = conn_cw.describe_alarms(alarm_names=[T['alarm']['name']])

    conn_cw.create_alarm(MetricAlarm(**T['alarm']))
