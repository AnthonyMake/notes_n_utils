#! /slowfs/dcopt105/vasquez/cnda/Conda/bin/python

from extra_hpd_functions import *

#################################################
# common settings                               #
#################################################

# branch          = '/remote/dcopt077/nightly_prs/q2019.12-SP'
# branch          = '/slowfs/dcopt036/nightly_prs/r2020.09_ls'
# branch          = '/remote/dcopt077/nightly_prs/p2019.03-SP'
branch          = '/remote/dcopt077/nightly_prs/r2020.09-SP'
suite           = 'DC_ICC2'
accounts        = 'dcntqor7 dcntqor6 vasquez' # space separated - must have 24x7.gala dir at <nightly>/prs/
nightly         = 'D20201016_20_30'
launcher_scripts= '/remote/dtdata1/testdata/prs/syn/scripts/nightly/run_scripts'
launcher        = 'gala-icc2_ex'
suffix          = '_vx_m3'
title           = 'Skip DFT + compile_convergent_back_to_back_incr'
flows           = 'SRM_ICC2_spg_timing_opt_area'
fm_flow         = ''
# this design list excludes DEIMOS
designs         = '' # if empty inherits original list
stages          = 'DC ICC2'

extra_settings  = '''
set compile_convergent_back_to_back_incr TRUE
'''

raw_settings  = ''

# controls
run             = True
debug           = False	# if true doesnt submit, just print a buch of messages 
avoid_submit    = True # if true do all propts and report stuff without submit
do_report       = True # do dirs, links'n scripts for report
check_baseline  = False # check'n run the baseline

# reporting
report_script   = 'subreport_srm_icc2_spg_timing_opt_area.csh'
report_name     = 'arun_ex'
baseline        = 'SRM_ICC2_spg_timing_opt_area_vx_m1'
rep_flows       = 'SRM_ICC2_spg_timing_opt_area_vx_m1 SRM_ICC2_spg_timing_opt_area_vx_m2 SRM_ICC2_spg_timing_opt_area_vx_m3'

# raw_settings = ''
# raw_settings    = '''
# tool.nwpopt.opts::
# :: set_app_options -list {place_opt.flow.do_spg false}
# '''
dc_bin = ''
icc2_bin = ''
#dc_bin = '/slowfs/dcopt115/duraisam/dcg_karthi/objs/dcg_qsp_apple4//bin-linux64/common_shell_exec_exp2  -r /u/immgr/spf_q2019.12_sp4_cs1_rel/image/D20200718_02_00/ -shell dcnxt_shell -topo'
# dc_bin= '/u/immgr/spf_main_ls/image_NIGHTLY/D20200626_12_01/bin/dcnxt_shell'
# dc_bin = '/u/immgr/spf_n2017.09_sp4_cs1_rel/image/D20200509_03_00/bin/dc_shell'
# raw_settings = ''

if dc_bin:
        print('*************************************************')
        print('************ RUNNING WITH CUSTOM BIN ************')
        print('*************************************************')
        print(dc_bin)
        print('*************************************************')

########################################
# i'd like to make all below 
# just a function, but there is a bunch 
# of arguments. Yup
########################################

if check_baseline:
        base_dir = os.path.join(branch, suite, nightly, 'prs/run', baseline)
        if os.path.exists(base_dir):
                print('-%s exists on this nightly image. So far so good.'%baseline)
        else:
                print('-%s doesn\'t exists in this run. Kicking it off.'%baseline)
                if not debug:
                        submit_regular (
                                branch = branch,
                                launcher = launcher,
                                launcher_scripts = launcher_scripts,
                                users = accounts,
                                suite = suite,
                                nightly = nightly,
                                flow = baseline,
                                designs = designs,
                        )
                else:
                        print('plan to kickoff baseline for %s at %s'%(baseline,nightly))

# -----------------------------------
flow_ls = []
if run:
        for flow in flows.split():
                submit_extra_run(
                        launcher_scripts = launcher_scripts,
                        launcher = launcher,
                        users = accounts,
                        branch = branch,
                        suite = suite,
                        nightly = nightly,
                        debug = debug,
                        suffix = suffix,
                        flow = flow,
                        title = title,
                        dc_bin = dc_bin,
                        dc_extra_settings = extra_settings,
                        raw_extra_settings = raw_settings,
                        stages = stages,
                        designs = designs,
                        fm_flow = fm_flow,
                        avoid_submit = avoid_submit,
                        icc2_bin = icc2_bin
                )
                
        #         flow_ls.append(flow + suffix)

if do_report:
        print(' '.join(flow_ls))
        add_regular_report(
                branch = branch,
                suite = suite,
                nightly = nightly,
                debug = debug,
                baseline = baseline,
                #baseline = baseline,
                # flows = ' '.join(flow_ls) + ' ' + flows,
                flows = rep_flows,
                report_name= report_name,
                report_script = report_script,
        )

        print('\nreport will be at:\n')
        print('https://clearcase%s/%s/%s/prs_report.%s.out\n'%(branch,suite,nightly,report_name))