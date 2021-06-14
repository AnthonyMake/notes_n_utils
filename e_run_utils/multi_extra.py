import os, sys

sys.path.append('/slowfs/dcopt105/vasquez/utils/e_run_utils')
from extra_hpd_functions import *

# common args
flow = 'SRM_ICC2_spg_timing_power_opt_area'
repeat             = 1
raw_extra_settings = ''
stages             = 'DC ICC2'
dc_bin             = '/u/re/spf_q2019.12_sp_dev/image_NIGHTLY/D20200714_20_30/linux64/syn/bin/dcnxt_shell -no_home_init'
icc2_bin           = ''
fm_bin             = ''
fm_flow            = ''
fm_extra_settings = ''

designs = ''

target_dir = '/slowfs/dcopt105/vasquez/utils/project_repos/run_dirs/tpo/D20200710/run3'
target_propts = '/slowfs/dcopt105/vasquez/utils/project_repos/run_dirs/tpo/D20200710/p_propts.cfg'




extras = []

rs1 = '''
set compile_enable_total_power_optimization TRUE
set optimize_netlist_run_area_and_high_effort_dynamic_power_recovery TRUE
'''

extras.append({
    'flow': flow,
    'title': 'TPO_HIGH_EFFORT', 
    'suff': '_vex_01',
    'dc_bin': dc_bin,
    'dc_extra_settings' : rs1
    })


rs2 = '''
set compile_enable_total_power_optimization TRUE
set lnc_flow_gpower_use_tpo_cost TRUE
'''

extras.append({
    'flow': flow,
    'title': 'TPO_COST', 
    'suff': '_vex_02',
    'dc_bin': dc_bin,
    'dc_extra_settings' : rs2
    })

debug = False
# copy propts
new_t_propts = '%s/prs_propts.cfg'%target_dir
shutil.copy2(target_propts, new_t_propts)

flist = []
dlist = []

for ex in extras:

    flow              = ex['flow'] if 'flow' in ex else ''
    title             = ex['title'] if 'title' in ex else ''
    dc_extra_settings = ex['dc_extra_settings'] if 'dc_extra_settings' in ex else ''
    suffix            = ex['suff'] if 'suff' in ex else ''
    dc_bin            = ex['dc_bin'] if 'dc_bin' in ex else ''

    names, des = make_extra(
    
    flow, suffix, title, dc_extra_settings, raw_extra_settings, stages, dc_bin, icc2_bin, fm_bin, fm_flow, designs, new_t_propts, debug, fm_extra_settings

    )

    flist.append(names)
    
    if designs != '':
        for d in designs.strip().split():
            if d not in dlist: dlist.append(d) 
    else:
        for d in des.strip().split():
            if d not in dlist: dlist.append(d) 
        

# add_regular_report(
#     branch = branch,
#     suite = suite,
#     nightly = nightly,
#     debug = debug,
#     baseline = flist[0],
#     flows = ' '.join(flist),
#     report_name= report_name,
#     report_script = report_script,
# )

# for i in range(len(flist)):
#      print('-----kick lines -----\n')


print('flows: %s'%' '.join(flist))
print('designs: %s'%' '.join(dlist))

# create propts for kick-off
propts_kick = '''
INCLUDE %s

flows: %s
designs: %s
'''%('%s/prs_propts.cfg'%target_dir, ' '.join(flist), ' '.join(dlist))

if not debug:
    propts_kick_file = open('%s/propts.cfg'%target_dir, 'w')
    propts_kick_file.write(propts_kick)
    propts_kick_file.close()

else:
    try: os.remove(new_t_propts)
    except: print('cannot remove %s'%new_t_propts)
    pass










