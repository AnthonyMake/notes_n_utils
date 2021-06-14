import os, sys
sys.path.append('/slowfs/dcopt105/vasquez/utils/e_run_utils')
from extra_hpd_functions import *

sys.path.append('/slowfs/dcopt105/vasquez/utils/suite_collectors_dev/v_repo/suite_collectors')
from suite_collector_v2 import qor_from_report
from status_collector import status_collector_flow

import shutil
import pprint
pp = pprint.PrettyPrinter(indent = 2, depth = 4)

target_metrics ={
  'DCMvArea'         : [0.5, 1],
  'ICPMvArea'        : [0.5, 1],
  'DCWNS'            : [0.5, 1],
  'ICPWNS'           : [0.5, 1],
  'DCTNSPM'          : [10, 110], 
  'DCTNSPMT'         : [10, 110],
  'DCTNSPF'          : [1,1],
  'ICPTNSPM'         : [10, 110],
  'ICPTNSPMT'        : [10,110],
  'ICPTNSPF'         : [1, 1],
  'DCStdCelDynPow'   : [1,5],
  'DCStdCelLeakPow'  : [1,1],
  'ICPStdCelDynPow'  : [1.0,3],
  'ICPStdCelLeakPow' : [1,1],
  'CLKDCAllOpt'      : [1.0,10, 3],
  'CPUDCAllOpt'      : [1.0,10, 3],
  'DCMem'            : [0.5,1, 3000]
}

execs = {
  'P-2019.03-SP5-CS1-T-20201218': '/remote/swefs/PE/products/spf/p2019.03_sp5_cs1_rel/image/nightly/syn_optimize/D20201218_6111408/Testing/bin/dcnxt_shell',
  'P-2019.03-SP5-CS1-T-20210602': '/remote/swefs/PE/products/spf/p2019.03_sp5_cs1_rel/image/nightly/syn_optimize/D20210602_6557008/Testing/bin/dcnxt_shell'
}

# sign_off_run(
#   execs = execs,
#   title = 'P-2019.03-SP5-CS1-T-20210602_prcsn',
#   baseline = 'P-2019.03-SP5-CS1-T-20201218',
#   target = 'P-2019.03-SP5-CS1-T-20210602',
#   flows = 'SRM_ICC2_spg_timing_opt_area',
#   # designs = 'CortexM3',
#   base_propts = '/slowfs/dcopt036/nightly_prs/s2021.06_ls/DC_ICC2/D20210529_18_01/prs/run/propts.cfg',
#   target_metris = target_metrics,
#   target_dir = '/u/szhang/scratch/24x7/dc/R-2020.09/nightly_prs/baseline/D20200826_5802213/DC_ICC2/sign_off',
#   hs_user = 'rmorale',
#   rt_config = 'PRCSN_CPU',
#   debug = False,
# )

# # r = des_qor_from_report(
# #   '/slowfs/dcopt036/nightly_prs/s2021.06_ls/DC_ICC2/D20210526_15_35/prs_report.diff.srm_icc2_spg_timing_opt_area.out', 
# #   'SRM_ICC2_spg_timing_opt_area',
# #   'SRM_ICC2_spg_timing_opt_area_prev', 
# #   None, 
# #   target_metrics)
r = status_collector_flow(
  'vasquez',
  '/u/szhang/scratch/24x7/dc/R-2020.09/nightly_prs/baseline/D20200826_5802213/DC_ICC2/sign_off/P-2019.03-SP5-CS1-T-20210602_cpu', 
  'SRM_ICC2_spg_timing_opt_area_so0', 
  'SRM_ICC2_spg_timing_opt_area_so1', 
  'html'
  )

pp.pprint(r)


# j = qor_from_report(
#   '/slowfs/dcopt036/nightly_prs/s2021.06_ls/DC_ICC2/D20210526_15_35/prs_report.diff.srm_icc2_spg_timing_opt_area.out', 
#   'SRM_ICC2_spg_timing_opt_area',
#   'SRM_ICC2_spg_timing_opt_area_prev', 
#   None, 
#   target_metrics)

# pp.pprint(j)