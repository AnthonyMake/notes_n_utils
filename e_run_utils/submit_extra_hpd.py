#! /slowfs/dcopt105/vasquez/cnda/Conda/bin/python

import sys

sys.path.append('/slowfs/dcopt105/vasquez/utils/e_run_utils')
from extra_hpd_functions import *

#################################################
# put the settings here
#
branch	 = '/remote/dcopt077/nightly_prs/p2019.03-SP' 	 
#branch   = '/slowfs/dcopt036/nightly_prs/q2019.12_ls' # suite is already hardcoded as HPDRT
accounts = 'rmorale' # space separated - must have 24x7.gala dir at <nightly>/prs/
nightly  = 'D20190930_20_30'
suffix   = '_ex4' 
vflow    = 'HPD_DCG_rt' # only work with this one 
title    = 'Run4' # for report
report_name = 'hpd_dcg_ex4' # just the name, subreport_hpd_dcg.csh is already hardcoded 
baseline = 'N_HPD_DCG_rt'
_4_core  = False # for switch to 4 core
debug    = False 	# if true doesnt submit, just print a buch of messagesof what gonna do 

extra_settings = '''
set psynopt_tns_high_effort true
set compile_timing_high_effort_tns true
set compile_timing_high_effort true
'''

################################################
def submit_extra_hpd(accounts, branch, nightly, suffix, vflow,title,report_name,_4_core, debug, extra_settings):

    flows = {
        'HPD_prbench': '', 
        'HPD_cust_dc': '',
        'HPD_cust_DC_Platform' : ''
        }


    flow_names = []

    for _flow in flows:
        submit_extra_run(
            launcher_scripts  = '/remote/dtdata1/testdata/prs/syn/scripts/nightly/run_scripts',
            users             = accounts,
            launcher          = 'gala',
            branch            = branch,
            suite             = 'HPDRT',
            title             = title,
            nightly           = nightly,
            flow              = _flow + '_4core' if _4_core else _flow,
            suffix            = suffix,
            dc_extra_settings = extra_settings,
            designs           = flows[_flow],
            prbench           = True if _flow == 'HPD_prbench' else False,
            debug             = debug, 
        )

        flow_names.append('%s%s'%(_flow,suffix))

    vflow_name = ''

    if _4_core: vflow_name = vflow + '_4core' + suffix
    else : vflow_name = vflow + suffix

    add_virtual_flow(
        branch           = branch,
        suite            = 'HPDRT',
        nightly          = nightly,
        flows            = ' '.join(flow_names),
        virtual_flow     = vflow_name,
        virtual_title    = title,
        debug           = debug
    )


    add_regular_report(
        branch           = branch,
        suite            = 'HPDRT',
        nightly          = nightly,
        baseline         = 'HPD_DCG_rt',
        flows            = 'HPD_DCG_rt ' + baseline + ' ' + vflow_name,
        report_name      = report_name,
        report_script    = 'subreport_hpdrt_dcg.csh',
        debug            = debug
    )

submit_extra_hpd(accounts, branch, nightly, suffix, vflow,title,report_name,_4_core, debug, extra_settings)
