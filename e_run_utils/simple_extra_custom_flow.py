#! /slowfs/dcopt105/vasquez/cnda/Conda/bin/python

from extra_hpd_functions import *

#################################################
# common settings                               #
#################################################
branch          = '/remote/dcopt077/nightly_prs/q2019.12-SP' 
suite           = 'DC_ICC2'	 
accounts        = 'dcntqor6 dcntqor7' # space separated - must have 24x7.gala dir at <nightly>/prs/
nightly         = 'D20200203_20_30.power'
launcher_scripts= '/remote/dtdata1/testdata/prs/syn/scripts/nightly/run_scripts'
launcher        = 'gala-icc2'
debug           = False # if true doesnt submit, just print a buch of messages 
suffix          = '_vex_psp5'
flows           = 'SRM_ICC2_spg_timing_power_opt_area_baseline SRM_ICC2_spg_timing_power_opt_area SRM_ICC2_spg_power_opt_area_baseline SRM_ICC2_spg_power_opt_area'
fm_flow         = ''
designs         = ''
stages          = 'DC'
extra_settings  = ''
raw_settings    = 'INCLUDE /remote/pv/repo/dcnt/dcrt_prs_lib/gala_memusage_4c.cfg'

dc_bin = '/remote/swefs/PE/products/spf/p2019.03_sp_dev/image/nightly/syn_optimize/P-2019.03-SP5/D20191017_5108082/Testing/bin/dcnxt_shell '
#dc_bin = ''

# reporting
report_script   = 'subreport_srm_icc2_spg_timing_power_opt_area.csh'
report_name     = 'infer_sa_nightly_vs_psp5'
title           = 'Infer SA with P2019.03-SP5'
baseline        = 'SRM_ICC2_spg_timing_power_opt_area'

flow_ls = []

propts = '%s/%s/%s/prs/run/propts.cfg'%(branch,suite,nightly)


# for flow in flows.split():
#         if not os.path.isfile('%s.cfg'%flow):
#                 f = flow_to_file(flow, propts)
#         else:
#                 submit_extra_run(
#                         launcher_scripts = launcher_scripts,
#                         launcher = launcher,
#                         users = accounts,
#                         branch = branch,
#                         suite = suite,
#                         nightly = nightly,
#                         debug = debug,
#                         suffix = suffix,
#                         flow = flow,
#                         title = title,
#                         dc_bin = dc_bin,
#                         dc_extra_settings = extra_settings,
#                         raw_extra_settings = raw_settings,
#                         stages = stages,
#                         designs = designs,
#                         fm_flow = fm_flow,
#                         custom_flow = True,
#                 )
                        
        
# for flow in flows.split():

#         submit_extra_run(
#                 launcher_scripts = launcher_scripts,
#                 launcher = launcher,
#                 users = accounts,
#                 branch = branch,
#                 suite = suite,
#                 nightly = nightly,
#                 debug = debug,
#                 suffix = suffix,
#                 flow = flow,
#                 title = title,
#                 dc_bin = dc_bin,
#                 dc_extra_settings = extra_settings,
#                 raw_extra_settings = raw_settings,
#                 stages = stages,
#                 designs = designs,
#                 fm_flow = fm_flow,
#                 custom_flow = True,
#         )
        
#         flow_ls.append(flow + suffix)

# print(' '.join(flow_ls))
add_regular_report(
        branch = branch,
        suite = suite,
        nightly = nightly,
        debug = debug,
        baseline = baseline,
        flows = 'SRM_ICC2_spg_power_opt_area_baseline_vex_10 SRM_ICC2_spg_power_opt_area_baseline_vex_psp5 SRM_ICC2_spg_power_opt_area_vex_10 SRM_ICC2_spg_power_opt_area_vex_psp5 SRM_ICC2_spg_timing_power_opt_area_baseline_vex_10 SRM_ICC2_spg_timing_power_opt_area_baseline_vex_psp5 SRM_ICC2_spg_timing_power_opt_area_vex_10 SRM_ICC2_spg_timing_power_opt_area_vex_psp5',
        report_name= report_name,
        report_script = report_script,
)



