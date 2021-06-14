#! /slowfs/dcopt105/vasquez/cnda/Conda/bin/python
import sys

sys.path.append('/slowfs/dcopt105/vasquez/utils/e_run_utils')
from extra_hpd_functions import *

culprit_by_date(
    target_dir    = os.getcwd(),
    flow          = 'SRM_ICC2_spg_timing_opt_area',
    branch        = 'Q2019.12-SP',
    debug         = False,
    image_only    = False,
    start_date    = '2020/01/01',
    end_date      = '2020/01/04',
    shell         = 'dcnxt_shell',
    root_path     = '/u/re/spf_q2019.12_sp_dev/image_NIGHTLY/D20200103_20_30 ',
    repeat        = 1,
    designs       = 'dcp246_Xm_Xtmem ARCHS438',
    stages        = 'DC',
    target_propts = '/remote/dcopt077/nightly_prs/q2019.12-SP/DC_ICC2/D20200103_20_30/prs/run/propts.cfg',
    fm_flow       = '',
)
