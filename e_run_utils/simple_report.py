#! /slowfs/dcopt105/vasquez/cnda/Conda/bin/python

from extra_hpd_functions import *

#################################################
# common settings                               #
#################################################
# /remote/dcopt077/nightly_prs/p2019.03-SP/DC_ICC2/D20200515_09_40/prs/run
# branch          = '/remote/dcopt077/nightly_prs/r2020.09-SP'
branch          = '/slowfs/dcopt036/nightly_prs/r2020.09_ls'
suite           = 'DC_ICC2'
nightly         = 'D20200826_21_11'
debug           = False	# if true doesnt submit, just print a buch of messages 
report_script   = 'subreport_srm_icc2_spg_timing_opt_area.csh'
report_name     = 'nsp4_cs1'
flows           = '''
SRM_ICC2_spg_timing_opt_area_ex19
SRM_ICC2_spg_timing_opt_area_ex11
'''.split()

add_regular_report(
        branch = branch,
        suite = suite,
        nightly = nightly,
        debug = debug,
        baseline = flows[0],
        flows = ' '.join(flows),
        report_name= report_name,
        report_script = report_script,
)


# report_name     = 'karthi_power_ex'
# flows           = 'SRM_ICC2_spg_power_opt_area SRM_ICC2_spg_power_opt_area_vex_01 SRM_ICC2_spg_power_opt_area_vex_02'.split()

# add_regular_report(
#         branch = branch,
#         suite = suite,
#         nightly = nightly,
#         debug = debug,
#         baseline = flows[0],
#         flows = ' '.join(flows),
#         report_name= report_name,
#         report_script = report_script,
# )


