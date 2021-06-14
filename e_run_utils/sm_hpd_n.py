#! /slowfs/dcopt105/vasquez/cnda/Conda/bin/python

from extra_hpd_functions import *

#################################################
# common settings                               #
#################################################
branch	 = '/remote/dcopt077/nightly_prs/q2019.12-SP' 
suite = 'DC_ICC2'	 
accounts = 'dcntqor6 dcntqor7' # space separated - must have 24x7.gala dir at <nightly>/prs/
nightly  = 'D20191120_20_30'
launcher_scripts = '/remote/dtdata1/testdata/prs/syn/scripts/nightly/run_scripts'
launcher = 'gala-icc2'
debug    = True	# if true doesnt submit, just print a buch of messages 
# suffix = '_vex'
report_script = 'subreport_srm_jacob.csh'
report_name = '<b>lod_move_iplace_hfn_net_threshold 250 -jrminz-</b>'
flow = 'SRM_ICC2_spg_timing_opt_area'
fm_flow = ''
designs = ''

bins_list  = [
        '/remote/swefs/PE/products/spf/main/image/nightly/syn_optimize/D20190524_4845904/Testing/linux64/syn/bin/dcnxt_shell',
        '/remote/swefs/PE/products/spf/main/image/nightly/syn_optimize/D20190712_4939435/Testing/linux64/syn/bin/dcnxt_shell',
        '/remote/swefs/PE/products/spf/main/image/nightly/syn_optimize/D20190825_5022334/Testing/linux64/syn/bin/dcnxt_shell',
        '/remote/swefs/PE/products/spf/main/image/nightly/syn_optimize/D20190911_5051286/Testing/linux64/syn/bin/dcnxt_shell',
        '/remote/swefs/PE/products/spf/main/image/nightly/syn_optimize/D20190913_5055169/Testing/linux64/syn/bin/dcnxt_shell',
        '/remote/swefs/PE/products/spf/main/image/nightly/syn_optimize/D20191023_5119634/Testing/linux64/syn/bin/dcnxt_shell',
]

flow_ls = []
for i in range(len(bins_list)):

        n_name = bins_list[i].strip().split('/')[10]

        submit_extra_run(
                launcher_scripts = launcher_scripts,
                launcher = launcher,
                users = accounts,
                branch = branch,
                suite = suite,
                nightly = nightly,
                debug = debug,
                suffix = '_' + n_name,
                flow = flow,
                title = n_name,
                dc_bin = bins_list[i],
                stages = 'DC FM',
                designs = designs,
                fm_flow = fm_flow
        )

        flow_ls.append(flow + '_' + n_name)

add_regular_report(
        branch = branch,
        suite = suite,
        nightly = nightly,
        debug = debug,
        baseline = flow_ls[0],
        flows = ' '.join(flow_ls),
        report_name= report_name,
        report_script = report_script,
)






