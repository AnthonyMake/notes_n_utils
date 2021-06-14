#!/slowfs/dcopt105/vasquez/cnda/Conda/bin/python
import sys

# utilitary function location
# sys.path.append('/slowfs/dcopt105/vasquez/utils/nd_repo/le_clon/nd_report')

from logfile_utils_2nd import *

#############


branch   = 'q2019.12-SP'
nightly  = 'D20200214_20_30'
design   = 'f4_dl2ri_cisco'
baseline = 

root_dir = '/remote/dcopt077/nightly_prs/%s/DC_ICC2/%s/prs/run'%(branch, nightly)
log1 = '%s/SRM_spg_timing_opt_area_trace_multi_mirror/%s/%s.dcopt.out.gz'%(root_dir,design,design)
log2 = '%s/SRM_spg_timing_opt_area_trace_multi/%s/%s.dcopt.out.gz'%(root_dir,design,design)
print(log1)
print(log2)

lg1 = get_action_dep_rpts(log_to_str(log1), 'checksum')
lg2 = get_action_dep_rpts(log_to_str(log2), 'checksum')
pp.pprint(lg1[-1])
pp.pprint(lg2[-1])
#pp.pprint(lg)
exit()

df_list=get_rpts_diff(log1, log2, 0.0, 'qor')

for i in range(len(df_list)):
     print('index %s'%i)
     pp.pprint(df_list[i])


## just some planning
1 load log_files --> return list of structures
2 for each log check_integrity_run --> return true or false




