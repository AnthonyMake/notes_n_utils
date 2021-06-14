#! /slowfs/dcopt105/vasquez/cnda/Conda/bin/python

from extra_hpd_functions import *

# this will make dirs and reports in the official prs directories,
# It would be great to have a similar version which puts the report and scripts wherever you want.
# - vasquez - 

# branch	      = '/remote/dcopt077/nightly_prs/r2020.09-SP'
branch	      = '/remote/dcopt077/nightly_prs/q2019.12-SP'
suite         = 'DC_ICC2'	 
nightly       = 'D20210215_16_05'
debug         =  False	# if true just gonna tell you what it's the plan, make it true once sure
report_script = 'subreport_srm_icc2_spg_timing_opt_area.csh' # this one must exissts at branch/suite/nightly/prs/run
report_name   = 'ila_exp' # the name for your new report
flows         = 'SRM_ICC2_spg_timing_opt_area  SRM_ICC2_spg_timing_opt_area_ila_exp' 
# space separated flow list, first will be the baseline

add_regular_report(
        branch        = branch,
        suite         = suite,
        nightly       = nightly,
        debug         = debug,
        baseline      = flows[0],
        flows         = ' '.join(flows.split()), #don't judge me
        report_name   = report_name,
        report_script = report_script,
)
