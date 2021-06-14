#! /slowfs/dcopt105/vasquez/cnda/Conda/bin/python
import sys
import pprint
import pprint
import time

pp = pprint.PrettyPrinter(indent=4)

sys.path.append('/slowfs/dcopt105/vasquez/utils/e_run_utils')
from extra_hpd_functions import *

fm_cls_dir = '/u/formal/fmid/build/BL'
fm_cls = os.listdir(fm_cls_dir)
fm_cls.sort()

# get fm cls
cl_data = []
for cl in fm_cls:
    fm_exec = os.path.join(fm_cls_dir,cl,'bin-linux64/fm_shell_exec')
    if os.path.exists(fm_exec):
        cl_data.append({'cl': cl ,'exec': fm_exec, 'date':  time.ctime(os.path.getmtime(fm_exec))})


flow_execs = ''
flow_kicks = 'flows:\n'

for data in cl_data:
    flow_execs += 'flow.%s:\n'%data['cl']
    flow_execs += '::tool.fmchk.bin: %s\n'%data['exec']

    flow_kicks += '#:: %s ## %s\n'%(data['cl'],data['date'])

odir = '/remote/platform_pv1/24x7/dc/Q-2019.12-SP/nightly_prs/DC_ICC2_ex/D20200305_20_30/run.24x7_gala-icc2_ex.dcntqor6/culprit/fm_culprit/all_cls'

execs_file = open('%s/flow_execs.cfg'%odir, 'w')
execs_file.write(flow_execs)
execs_file.close()

kicks_file = open('%s/flow_kicks.cfg'%odir, 'w')
kicks_file.write(flow_kicks)
kicks_file.close()






