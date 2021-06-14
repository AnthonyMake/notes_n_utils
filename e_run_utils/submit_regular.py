#! /slowfs/dcopt105/vasquez/cnda/Conda/bin/python

from extra_hpd_functions import *

#################################################
# common settings                               #
#################################################
branch          = '/remote/dcopt077/nightly_prs/q2019.12-SP'
suite           = 'DC_ICC2'
nightly         = 'D20200908_16_16'
launcher_scripts= '/remote/dtdata1/testdata/prs/syn/scripts/nightly/run_scripts'
launcher        = 'gala-icc2'
accounts        = 'dcntqor6 dcntqor7 vasquez' # space separated - must have 24x7.<launcher> dir at <nightly>/prs/
flows           = 'SRM_ICC2_spg_timing_power_opt_area SRM_ICC2_spg_timing_power_opt_area_baseline'.split()
designs         = '' # empty for take the current configuration

for flow in flows:
    submit_regular(
        branch   = branch,
        users    = accounts,
        suite    = suite,
        nightly  = nightly,
        launcher_scripts = launcher_scripts,
        launcher = launcher,
        flow     = flow,
        designs  = designs, 
    )

add_regular_report(
    branch        = branch,
    suite         = suite,
    nightly       = nightly,
    flows         = 'SRM_ICC2_spg_timing_power_opt_area SRM_ICC2_spg_timing_power_opt_area_baseline',
    baseline      = 'SRM_ICC2_spg_timing_power_opt_area_baseline',
    designs       = designs,
    report_script = 'subreport_srm_icc2_spg_timing_power_opt_area.csh',
    report_name   = 'srm_icc2_spg_timing_power_opt_area',
    debug         = False,
)
