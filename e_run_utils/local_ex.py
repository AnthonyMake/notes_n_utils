#! /slowfs/dcopt105/vasquez/cnda/Conda/bin/python

import sys
sys.path.append('/slowfs/dcopt105/vasquez/utils/e_run_utils')
from extra_hpd_functions import *

local_ex_from_prs(
    branch  = '/remote/dcopt077/nightly_prs/q2019.12-SP', 
    suite   = 'DC_ICC2',
    nightly = 'D20200212_20_30',
    flows   = 'SRM_ICC2_spg_timing_opt_area SRM_ICC2_spg_opt_area',
    designs = '',

    #output_dir      = 'some/path', # in case you need to output to another directory,
)

## plan is as follows,
## take nighly propts as base
#  
