#! /slowfs/dcopt105/vasquez/cnda/Conda/bin/python
import sys, os
import pprint
import pprint
import time

pp = pprint.PrettyPrinter(indent=4)

sys.path.append('/slowfs/dcopt105/vasquez/utils/e_run_utils')
from extra_hpd_functions import *


# fm_cls_dir = '/slowfs/dcopt105/vasquez/utils/e_run_utils/cp_raw'
fm_cls_dir = '/slowfs/dcopt105/vasquez/utils/e_run_utils/cp_raw/cl_restore'
root_path = '/u/re/spf_q2019.12_sp_dev/image_NIGHTLY/D20201026_20_58'
shell = 'dcnxt_shell'

fm_cls = os.listdir(fm_cls_dir)
fm_cls.sort()

# start = '5953008'
# end = '6007414'
# print('start',start, fm_cls.index(start))
# print('end',start, fm_cls.index(end), '\n\n')

# target_cls = []

# for i in range(fm_cls.index(start),fm_cls.index(end)):
#     target_cls.append(fm_cls[i])

# print(len(target_cls))

# print(' '.join(target_cls))


#rdir = '/slowfs/dcopt105/vasquez/utils/e_run_utils/cp_raw/

# for cl in target_cls:
#     print('rebuilding %s'%cl)
#     os.system("/remote/swefs/PE/products/spf/main/clientstore/spf_main_ls/PEtools/ls/buildscripts/recover_backup.pl -cl %s  -branch q2019.12_sp_dev -output %s -accurate"%(cl,rdir))
#     print('done\n')


# get fm cls
cl_data = []
for cl in fm_cls:
    fm_exec = os.path.join(fm_cls_dir,cl,'common_shell_exec')
    if os.path.exists(fm_exec):
        cl_data.append({'cl': cl ,'exec': fm_exec, 'date':  time.ctime(os.path.getmtime(fm_exec))})

flow_execs = ''
flow_kicks = 'flows:\n'

for data in cl_data:
    flow_execs += 'flow.%s:\n'%data['cl']
    flow_execs += '::tool.rtlopt.bin: %s -r %s -shell %s\n'%(data['exec'],root_path,shell)
    flow_execs += '::tool.dcopt.bin:  %s -r %s -shell %s\n'%(data['exec'],root_path,shell)
    flow_execs += '::tool.dcrpt.bin:  %s -r %s -shell %s\n'%(data['exec'],root_path,shell)


    flow_kicks += '#:: %s ## %s\n'%(data['cl'],data['date'])

odir = '/slowfs/dcopt105/vasquez/utils/e_run_utils/cp_raw/test1'

execs_file = open('%s/flow_execs.cfg'%odir, 'w')
execs_file.write(flow_execs)
execs_file.close()

kicks_file = open('%s/flow_kicks.cfg'%odir, 'w')
kicks_file.write(flow_kicks)
kicks_file.close()



'''
Pressure pushing down on me,
pressing down un you, no men ask for

Under pressure,
that burns a building dowm
splits a family in two,
puts peple on streets,

thats the terror of  knwoing 

cause lov
such an old fashion word
and love dares you to care for
the people on the edge of the night,
and love dares you to change our way of 
carign about ourselves
this is our last dance
this is our last dance
this is ourselves
Under pressure
'''