#!/slowfs/dcopt105/vasquez/cnda/Conda/bin/python

import os, sys, gzip, re, copy, pprint
import pickle as pkl
from dictdiffer import diff, patch, swap, revert
import pandas as pd
from bs_icons import *
from jinja2 import Template

pp=pprint.PrettyPrinter(indent=1)

sys.path.append('/slowfs/dcopt105/vasquez/utils/backp_nd')
from logfile_utils_2nd import *

############################################################################################
# User Arguments
rundir      = '/remote/dcopt077/nightly_prs/r2020.09-SP/DC_ICC2/D20210415_rsp5/prs/run'
flows       = 'SRM_spg_timing_opt_area_nd_0,SRM_spg_timing_opt_area_nd_2'
report_name = 'nd_report'
designs     = 'BART_SG_N5,ARCH_HS38_SG_N5,Deimos_VX_N5,A72_DS_SG_N5,A72_ID_SG_N5,A53,A53_ARM,A57_CPU,A57_Non_CPU,A72_CPU,A73_Non_CPU,ARCHS38_7nm,ARCHS438,BLOCK_BL,Vega20-CB-T,Vega20-CPF-T,Vega20-DSA-T,Vega20-VGT-T,X5376,archipelago_N12_6T,dce_dchp_t,dcp212_Xm_Xttop,dcp245_SPEEDY28_TOP,dcp246_Xm_Xtmem,dcp247_VDD5_mux2,dcp270_enterprise_UPF,dcp275_archipelago,dcp276_xbar,dcp427_DWC_usb3,dcp428_DWC_ddr,dcp514_JDSIIP3A,dcp518_top,dcp519_fdeq_pnrb,dcp520_ccu_msw,dcp522_c8docsis31_rx_top,dcp597_mmu_thdo,dcp599_rgx_tpu_mcu,dcp630_jones,dcp631_mercer,dcp632_teague,dpx_bi_pu_rq_rs_ru_lblk,f4_brw_cisco,f4_dl2ri_cisco,rgx_rasterisation,xpc_fp,CortexM3,dcp564_leon3_mp_20_sset_ssink,dcp569_GORDON,dcp607_mpcore,dcp611_arm926ejs,dcp616_falcon_cpu' # comma separated, if empty will look for designs in rundir/flows
# designs    = 'f4_dl2ri_cisco rgx_rasterisation rgx_usc xpc_fp CortexM3 dcp245_SPEEDY28_TOP'.replace(' ',',')
# designs    = 'A53'
#designs = None
output      = os.path.join(os.getcwd(), 'nd_results') # e.g. here

############################################################################################


# creating output dir if doesn't exists

if not os.path.isdir(output):
    try:
        print('creating %s dir'%output) 
        os.mkdir(output)
    except: 
        print('couldn\'t create %s'%output)
else:
    print('%s already exists'%output)


# # designs = 'Vega20-SP1-T'
# # designs = 'dcp599_rgx_tpu_mcu'
# # designs = 'dcp597_mmu_thdo'
# design  = 'A75_prometheus_PAC16'
# designs = 'ARCHS438'


flow_report_html(rundir, flows, report_name, designs, output, 'checksum', '')




