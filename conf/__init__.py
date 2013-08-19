import datetime as _dt
TS_ISO = _dt.datetime.strftime(_dt.datetime.now(), '%Y%m%d_%H%M%S')

# aws-cli & related configs
PROFILE_NAME = 'wf'
PROFILE_REGIONS = 'us-west-1'
PROFILE_AZ = 'us-west-1a'

# ELB
LB_NAME = 'devweb'

# Auto Scaling
AS_NAME = 'devweb'
AS_CONFIG_NAME = '%s_%s' % (AS_NAME, TS_ISO)

AS_WORKER_MIN = '1'
AS_WORKER_MAX = '12'

AS_COOLDOWN = '60'

AS_THRESHOLD_LOW = '35'
AS_THRESHOLD_HIGH = '85'

# Initiated Instances
IN_AMI_ID = 'ami-f686adb3'
IN_TYPE = 't1.micro'
IN_SG = 'dev-web'
IN_KEY = 'Web-Dev-20120531'

# Consts
AS = 'autoscaling'
