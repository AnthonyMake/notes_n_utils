import os, gzip, re, copy, pprint
import pickle as pkl
from dictdiffer import diff, patch, swap, revert
import pandas as pd
from bs_icons import *
from jinja2 import Template

pp=pprint.PrettyPrinter(indent=1)

from logfile_utils_2nd import *
# initial arguments

nightlies = 'D20200417_20_30'

for nightly in nightlies.split():
    rundir = '/remote/dcopt077/nightly_prs/q2019.12-SP/DC_ICC2/%s/prs/run'%nightly
    flows  = 'SRM_spg_timing_opt_area_trace_multi,SRM_spg_timing_opt_area_trace_multi_mirror'
    report_name = 'nd_%s'%nightly
    output = os.path.join(os.getcwd(),nightly)

    if not os.path.isdir(output):
        try:
            print('creating %s dir'%nightly) 
            os.mkdir(output)
        except: 
            print('couldn\'t create %s'%output)
    else:
        print('%s already exists'%nightly)

    #designs     = 'f4_dl2ri_cisco rgx_rasterisation rgx_usc xpc_fp CortexM3'.replace(' ',',')
   
    designs = ''
    
    # designs = 'A57_Non_CPU'
    # # designs = 'Vega20-SP1-T'
    # # designs = 'dcp599_rgx_tpu_mcu'
    # # designs = 'dcp597_mmu_thdo'
    # design  = 'A75_prometheus_PAC16'
    # designs = 'ARCHS438'


    flow_report_html(rundir, flows, report_name, designs, output, '', '')




