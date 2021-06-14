# #from status_collector import detect_fails
# from fail_summary_pretty import fail_check_from_cache
from status_collector import status_collector_v2

cache_file = '/slowfs/dcopt036/nightly_prs/s2021.06_ls/DC_ICC2/D20210507_14_15/prs/run/rpt_srm_icc2_spg_timing_opt_area/prreport.cache'
flow_dir = '/slowfs/dcopt036/nightly_prs/s2021.06_ls/DC_ICC2/D20210507_14_15/prs/run/SRM_ICC2_spg_timing_opt_area'

prs_dir = '/slowfs/dcopt036/nightly_prs/s2021.06_ls/DC_ICC2/D20210507_14_15/prs/run/rpt_srm_icc2_spg_timing_power_opt_area'
# detect_fails(cache_file, flow_dir)
# fail_check_from_cache(prs_dir)


users = None
root_path = '/slowfs/dcopt036/nightly_prs'
tool = None
branch = 's2021.06_ls'
suite = 'DC_ICC2'
n_max = 10
report = 'srm_icc2_spg_timing_opt_area_scib_all'
flow = 'SRM_ICC2_spg_timing_power_opt_area_scib_all'
status_collector_v2(None, root_path, None, branch, suite, None,flow,'somebase', n_max, report, None)

