import os, re
import subprocess
import pprint


cfgs = '''
INCLUDE /remote/dtdata1/testdata/prs/syn/dcp_suite/propts.cfg
INCLUDE /remote/dtdata1/testdata/prs/syn/dcp_suite/des2cpu.gala.cfg
INCLUDE /remote/dtdata1/testdata/prs/syn/hpd_suite/propts.cfg
INCLUDE /remote/dtdata1/testdata/prs/syn/hpd_suite/optn_area.cfg
INCLUDE /remote/dtdata1/testdata/prs/syn/hpd_suite/24x7_disk.cfg
INCLUDE /remote/pv/repo/dcnt/dcrt_prs/D180318/platform/design_dc_icc2.cfg
INCLUDE /remote/pv/repo/dcnt/dcrt_prs/D180318/platform/node_des.cfg
INCLUDE /remote/pv/repo/dcnt/dcrt_prs/D180318/platform/ccs_des.cfg
INCLUDE /remote/pv/repo/dcnt/dcrt_prs/D180318/platform/dft_des.cfg
INCLUDE /remote/pv/repo/dcnt/dcrt_prs/D180318/platform/upf_des.cfg
INCLUDE /remote/pv/repo/24x7/dcrt/dcrt_icc2_full_suite/ndaroot.cfg
INCLUDE /remote/dtdata1/testdata/prs/syn/hpd_suite/dcicc2_setup.cfg
INCLUDE /remote/dtdata1/testdata/prs/syn/hpd_suite/ndm_setup.cfg
INCLUDE /remote/dtdata1/testdata/prs/syn/dcp_suite/dcicc2_setup.cfg
INCLUDE /remote/dtdata1/testdata/prs/syn/dcp_suite/ndm_setup.cfg
INCLUDE /remote/pv/repo/24x7/dc/PVREG/prod/prs_baseline/ver.20190524/farm/des2cpu.gala.8core.runtime.cfg
INCLUDE __RM_SCRIPTS__/SRM_dcicc2_combined_setup.cfg
INCLUDE /remote/dcopt072/dcprs/D180919/dcp_suite/propts.cfg
INCLUDE /remote/dcopt072/dcprs/D180919/pwr_suite/propts.cfg
INCLUDE /remote/dcopt072/dcprs/D180919/arm_suite/propts.cfg
INCLUDE /remote/dcopt072/dcprs/D171208/dcqor_suite/propts.cfg
INCLUDE /remote/dcopt072/dcprs/D171208/bigchip_suite/propts.cfg
INCLUDE /remote/dcopt072/dcprs/D171208/hpd_suite/propts.cfg
INCLUDE /remote/dcopt072/dcprs/D171208/cong_suite/propts.cfg
INCLUDE /remote/dtdata1/testdata/prs/syn/upf_suite/propts.cfg
INCLUDE /remote/dtdata1/testdata/prs/syn/upf_suite/des2cpu.cfg
INCLUDE /remote/dtdata1/testdata/prs/syn/amd_suite/propts.cfg
INCLUDE /slowfs/dcopt088/prs_baselines/NCR_scripts/cust_flow_des.cfg
INCLUDE /remote/dcopt082/nightly_prs/v1.0/Primary/lib/design.nlib.cfg
INCLUDE /remote/pv/repo/dcnt/dcrt_prs/D190506/platform/design_dc_icc2.cfg
INCLUDE /remote/pv/repo/24x7/dc/PVREG/prod/prs_baseline/node/node.cfg
INCLUDE /remote/pv/repo/dcnt/dcrt_prs/D190506/img_suite/design_dc_icc2.cfg
INCLUDE /remote/dtdata1/testdata/prs/syn/hpd_suite/design_dc_icc2.css2rms.cfg
INCLUDE /remote/pv/repo/24x7/dc/PVREG/prod/prs_baseline/2019.03-SP2/fm_fixes.cfg
INCLUDE /remote/pv/repo/24x7/dc/PVREG/prod/prs_baseline/2019.03-SP2/setup_fixes.cfg
INCLUDE /remote/dcopt072/dcprs/D180919/des2cpu.gala.cfg
INCLUDE /remote/pv/repo/dcnt/dcrt_prs/D190506/img_suite/des2cpu.gala.cfg
INCLUDE /remote/pv/repo/dcnt/dcrt_prs/D190506/platform/des2cpu.gala.cfg
INCLUDE __BASELINE__/suites.cfg
INCLUDE /remote/dtdata1/testdata/prs/syn/upf_suite/suites_upf.cfg
'''.strip().splitlines()

des_ls = []

for fl in cfgs:
    fl = fl.split()[1]

    try : fl_txt = open(fl, 'r').readlines()
    except: pass


    for line in fl_txt:

        des_pattern = r'^des\.([\w-]+)\.*'

        m = re.match(des_pattern, line)

        if m: 
            des = m.group(1)

            if des not in des_ls: des_ls.append(des) 

print('## %s designs found'%str(len(des_ls)))
print('designs : %s '%' '.join(des_ls))


