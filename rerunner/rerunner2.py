from pathlib import Path
import os, re, sys


def rerun(branch,suite,nightly,flow,designs):

    branch_map = {}
    branch_map['psp'] = '/remote/dcopt077/nightly_prs/p2019.03-SP'
    branch_map['osp'] = '/remote/dcopt077/nightly_prs/o2018.06-SP'
    branch_map['qls'] = '/slowfs/dcopt036/nightly_prs/q2019.12_ls'
    branch_map['qsp'] = '/remote/dcopt077/nightly_prs/q2019.12-SP'
    branch_map['rls'] = '/slowfs/dcopt036/nightly_prs/r2020.09_ls'
    branch_map['rsp'] = '/remote/dcopt077/nightly_prs/r2020.09-SP'
    branch_map['sls'] = '/slowfs/dcopt036/nightly_prs/s2021.06_ls'
    ## branch_map['psp_base'] = '/slowfs/dcopt086/prs_baselines/2018.06/dc2icc2.base.181130'

    branch = branch_map[branch]
    designs = designs.split()

    for design in designs:
        
        des_dir_str = '%s/%s/%s/prs/run/%s/%s'%(branch,suite,nightly,flow,design)
        des_dir = Path(des_dir_str)
        
        print(des_dir_str)

        try: 
            if des_dir.exists():

                cmd = 'rsh -l %s localhost \"cd %s; /remote/us01home47/rmorale/bin/relaunch_design.pl gala-icc2\"'%(des_dir.owner(), des_dir_str)
                print(cmd)
                os.system(cmd)
            else:
                print('%s doesn\'t exists.'%des_dir_str )

        except:

            print('\nPermissionError: Applying brute force...\n')

            user_poll = 'vasquez rmorale'.split()

            for user in user_poll:
                try:

                    print('Trying with %s...'%user)            
                    cmd = 'rsh -l %s localhost \"cd %s; /remote/us01home47/rmorale/bin/relaunch_design.pl gala-icc2\"'%(user, des_dir_str)
                    print(cmd)
                    
                    ret = os.popen(cmd).readlines()
                    # print(ret)

                    if ret[-1] == 'Done.\n':
                        print('Success with %s, moving forward'%user)
                        break

                except :
                    print('not possible with %s'%user)

def rerun_fast(des_table):

    table = des_table.strip().replace('\t',' ').splitlines()
    
    branch_map = {}
    branch_map['p2019.03-SP'] = '/remote/dcopt077/nightly_prs/p2019.03-SP'
    branch_map['o2018.06-SP'] = '/remote/dcopt077/nightly_prs/o2018.06-SP'
    branch_map['q2019.12_ls'] = '/slowfs/dcopt036/nightly_prs/q2019.12_ls'
    branch_map['q2019.12-SP'] = '/remote/dcopt077/nightly_prs/q2019.12-SP'
    branch_map['r2020.09_ls'] = '/slowfs/dcopt036/nightly_prs/r2020.09_ls'
    branch_map['r2020.09-SP'] = '/remote/dcopt077/nightly_prs/r2020.09-SP'
    branch_map['s2021.06_ls'] = '/slowfs/dcopt036/nightly_prs/s2021.06_ls'

    for line in table:

        branch,suite,nightly,flow,design = line.split()

        print(branch,suite,nightly,flow,design)      
        branch = branch_map[branch]

        des_dir_str = '%s/%s/%s/prs/run/%s/%s'%(branch,suite,nightly,flow,design)
        des_dir = Path(des_dir_str)
        
        print(des_dir_str)

        try: 
            if des_dir.exists():

                cmd = 'rsh -l %s localhost \"cd %s; /remote/us01home47/rmorale/bin/relaunch_design.pl gala-icc2\"'%(des_dir.owner(), des_dir_str)
                print(cmd)
                os.system(cmd)
            else:
                print('%s doesn\'t exists.'%des_dir_str )

        except:

            print('\nPermissionError: Applying brute force...\n')

            #user_poll = 'chunwang dcntqor6 dcntqor7 rmorale'.split()
            user_poll = ['rmorale']    
            for user in user_poll:
                try:

                    print('Trying with %s...'%user)            
                    cmd = 'rsh -l %s localhost \"cd %s; /remote/us01home47/rmorale/bin/relaunch_design.pl gala-icc2\"'%(user, des_dir_str)
                    print(cmd)
                    
                    ret = os.popen(cmd).readlines()
                    # print(ret)

                    if ret[-1] == 'Done.\n':
                        print('Success with %s, moving forward'%user)
                        break

                except :
                    print('not possible with %s'%user)     

def rerun_as_in_prs(branch,suite,nightly,prs_text):

    for line in prs_text.splitlines():
        if line != '': 
            line = line.strip().split('/')[:2] 
        else:
            continue
        flow   = line[0] 
        design = line[1].split(':')[0]
        
        rerun(branch,suite,nightly,flow,design)
        #print(branch,suite,nightly,flow,design)

# rerun('sls', 'DC_ICC2', 'D20210201_12_01', 'SRM_ICC2_spg_timing_opt_area', 'Vega20-CB-T dcp427_DWC_usb3 dcp428_DWC_ddr dcp520_ccu_msw')
# rerun('rsp', 'DC_ICC2', 'D20210129_20_30', 'SRMFm_ICC2_spg_timing_opt_area', 'BLOCK_BL dcp632_teague rgx_rasterisation dpx_bi_pu_rq_rs_ru_lblk dcp519_fdeq_pnrb A57_Non_CPU dcp599_rgx_tpu_mcu')
# rerun('psp', 'DC_ICC2', 'D20190920_20_30', 'SRMFm_ICC2_spg_opt_area', 'dcp427_DWC_usb3')

# rerun('osp', 'DC_ICC2', 'D20190904_14_30', 'SRMFm_ICC2_spg_opt_area ', 'dcp514_JDSIIP3A dcp514_JDSIIP3A')
# rerun('osp', 'DC_ICC2', 'D20190904_14_30', 'SRM_ICC2_spg_timing_opt_area ', 'dcp246_Xm_Xtmem')
# rerun('osp', 'DC_ICC2', 'D20190904_14_30', 'SRM_ICC2_spg_opt_area ', 'dcp571_hrp_xb_m')


# rerun('psp', 'DC_ICC2', 'D20190828_20_30.dc_shell', 'SRM_ICC2', 'dcp514_JDSIIP3A dcp631_mercer dcp632_teague dcp276_xbar dcp270_enterprise_UPF')
# rerun('osp', 'DC_ICC2', 'D20190829_14_30', 'SRM_ICC2_spg_timing_opt_area', 'dcp569_GORDON ARCHS438 dcp426_opf_fp dcp579_pba_fp')

# exit()
# branch   = 'psp'
# suite    = 'DC_ICC2'
# nightly  = 'D20190918_20_30'

# rerun(branch,suite,nightly,'SRM_ICC2_spg_timing_opt_area', 'A53_ARM')
# rerun(branch,suite,nightly,'SRM_ICC2_spg_opt_area', 'ARCHS38_16nm')
# rerun(branch,suite,nightly,'SRMFm_ICC2_spg_opt_area', 'ARCHS38_16nm')

# branch   = 'qls'
# suite    = 'DC_ICC2'
# nightly  = 'D20190920_12_01'

# rerun(branch,suite,nightly, 'SRM_wlm', 'dcp599_rgx_tpu_mcu')
# rerun(branch,suite,nightly, 'SRM_ICC2', 'dcp599_rgx_tpu_mcu')
# /p2019.03-SP/DC_ICC2/D20190927_20_30/prs/run/rpt_UPF.srm_spg/UPF_SRM_ICC2_spg/dcp615_CortexM3/dcp615_CortexM3.rtlopt.out

# branch   = 'sls'
# suite    = 'DC_ICC2'
# nightly  = 'D20201009_12_01 '
# flows    = 'SRM_ICC2_spg_timing_opt_area SRMFm_ICC2_spg_timing_opt_area'.split()
# designs  = 'dcp632_teague'

# for flow in flows:
#     rerun(branch,suite,nightly, flow, designs)

# rerun('sls', 'DC_ICC2', 'D20210507_14_15', 'SRM_ICC2_spg_timing_opt_area', 'dcp569_GORDON')
# rerun('sls', 'DC_ICC2', 'D20210507_14_15', 'SRM_ICC2_spg_timing_power_opt_area', 'dcp632_teague')
# rerun('sls', 'DC_ICC2', 'D20210507_14_15', 'SRM_ICC2_spg_timing_power_opt_area', 'dcp246_Xm_Xtmem')
# rerun('sls', 'DC_ICC2', 'D20210507_14_15', 'SRM_ICC2_spg_timing_power_opt_area', 'archipelago_N12_6T')

raw = '''
    SRM_ICC2_spg_timing_opt_area_ex4/dcp245_SPEEDY28_TOP:HIIncmp (dcp245_SPEEDY28_TOP.hinfo.out:1)
    SRM_ICC2_spg_timing_opt_area_ex6/dcp245_SPEEDY28_TOP:HIIncmp (dcp245_SPEEDY28_TOP.hinfo.out:1)
    SRM_ICC2_spg_timing_opt_area_ex4/dcp564_leon3_mp_20_sset_ssink:HIIncmp (dcp564_leon3_mp_20_sset_ssink.hinfo.out:2)
    SRM_ICC2_spg_timing_opt_area_ex5/dcp564_leon3_mp_20_sset_ssink:PLFail (dcp564_leon3_mp_20_sset_ssink.nwpopt.out:2508)
    SRM_ICC2_spg_timing_opt_area_ex6/dcp564_leon3_mp_20_sset_ssink:DRFail (dcp564_leon3_mp_20_sset_ssink.dprrpt.out:1)
    SRM_ICC2_spg_timing_opt_area_ex4/ARCHS38_7nm:DRFail (ARCHS38_7nm.dcrpt.out:503)
    SRM_ICC2_spg_timing_opt_area_ex6/ARCHS38_7nm:NDBFail (ARCHS38_7nm.nw2nlib.out:26)
    SRM_ICC2_spg_timing_opt_area_ex4/archipelago_N12_6T:DRFail (archipelago_N12_6T.dcrpt.out:587)
    SRM_ICC2_spg_timing_opt_area_ex6/archipelago_N12_6T:NDBIncmp (archipelago_N12_6T.nw2nlib.out:2)
    SRM_ICC2_spg_timing_opt_area_ex4/dcp428_DWC_ddr:HIIncmp (dcp428_DWC_ddr.hinfo.out:1)
    SRM_ICC2_spg_timing_opt_area_ex6/dcp428_DWC_ddr:HIIncmp (dcp428_DWC_ddr.hinfo.out:1)
    SRM_ICC2_spg_timing_opt_area_ex4/X5376:HIIncmp (X5376.hinfo.out:1)
    SRM_ICC2_spg_timing_opt_area_ex6/X5376:HIIncmp (X5376.hinfo.out:1)
    SRM_ICC2_spg_timing_opt_area_ex4/dcp427_DWC_usb3:HIIncmp (dcp427_DWC_usb3.hinfo.out:1)
    SRM_ICC2_spg_timing_opt_area_ex6/dcp427_DWC_usb3:DRFail (dcp427_DWC_usb3.dprrpt.out:1)
    R_SRM_ICC2_spg_timing_opt_area/A73_Non_CPU:NDBFail (A73_Non_CPU.nw2nlib.out:2026)
    R_SRM_ICC2_spg_timing_opt_area/dcp569_GORDON:NDBFail (dcp569_GORDON.nw2nlib.out:12020)
    SRM_ICC2_spg_timing_opt_area_ex4/dcp569_GORDON:HIIncmp (dcp569_GORDON.hinfo.out:2)
    SRM_ICC2_spg_timing_opt_area_ex6/dcp569_GORDON:PCIncmp
    SRM_ICC2_spg_timing_opt_area_ex4/dcp212_Xm_Xttop:HIIncmp (dcp212_Xm_Xttop.hinfo.out:1)
    SRM_ICC2_spg_timing_opt_area_ex6/dcp212_Xm_Xttop:HIIncmp (dcp212_Xm_Xttop.hinfo.out:1)
    SRM_ICC2_spg_timing_opt_area_ex4/dcp597_mmu_thdo:HIIncmp (dcp597_mmu_thdo.hinfo.out:1)
    SRM_ICC2_spg_timing_opt_area_ex6/dcp597_mmu_thdo:HIIncmp (dcp597_mmu_thdo.hinfo.out:1)
    SRM_ICC2_spg_timing_opt_area_ex4/dcp246_Xm_Xtmem:HIIncmp (dcp246_Xm_Xtmem.hinfo.out:1)
    SRM_ICC2_spg_timing_opt_area_ex6/dcp246_Xm_Xtmem:HIIncmp (dcp246_Xm_Xtmem.hinfo.out:1)
    SRM_ICC2_spg_timing_opt_area_ex4/dcp247_VDD5_mux2:HIIncmp (dcp247_VDD5_mux2.hinfo.out:1)
    SRM_ICC2_spg_timing_opt_area_ex6/dcp247_VDD5_mux2:HIIncmp (dcp247_VDD5_mux2.hinfo.out:1)
    SRM_ICC2_spg_timing_opt_area_ex5/ARCHS438:DRFail (ARCHS438.dprrpt.out:1)
    SRM_ICC2_spg_timing_opt_area_ex4/dcp514_JDSIIP3A:HIIncmp (dcp514_JDSIIP3A.hinfo.out:1)
    SRM_ICC2_spg_timing_opt_area_ex6/dcp514_JDSIIP3A:HIIncmp (dcp514_JDSIIP3A.hinfo.out:1)
    SRM_ICC2_spg_timing_opt_area_ex4/dcp599_rgx_tpu_mcu:HIIncmp (dcp599_rgx_tpu_mcu.hinfo.out:1)
    SRM_ICC2_spg_timing_opt_area_ex6/dcp599_rgx_tpu_mcu:HIIncmp (dcp599_rgx_tpu_mcu.hinfo.out:1)
    SRM_ICC2_spg_timing_opt_area_ex6/dcp270_enterprise_UPF:PLIncmp (dcp270_enterprise_UPF.icprpt.out:2)
    SRM_ICC2_spg_timing_opt_area_ex6/dcp522_c8docsis31_rx_top:PLIncmp (dcp522_c8docsis31_rx_top.icprpt.out:2)
    SRM_ICC2_spg_timing_opt_area_ex5/dcp519_fdeq_pnrb:DRFail (dcp519_fdeq_pnrb.dcrpt.out:10982)
    SRM_ICC2_spg_timing_opt_area_ex4/dcp630_jones:DRFail (dcp630_jones.dcrpt.out:2047)
    SRM_ICC2_spg_timing_opt_area_ex6/dcp631_mercer:DRFail (dcp631_mercer.dcrpt.out:2041)
    SRM_ICC2_spg_timing_opt_area_ex4/dcp632_teague:HIIncmp (dcp632_teague.hinfo.out:2)
'''

rerun_as_in_prs('sls','DC_ICC2','D20210507_14_15',raw)
# table ='''
# q2019.12_ls	DC_ICC2	D20191118_18_01	SRM_ICC2_spg_timing_opt_area   A57_CPU
# q2019.12_ls	DC_ICC2	D20191118_18_01	SRMFm_ICC2_spg_timing_opt_area   A57_CPU
# q2019.12_ls	DC_ICC2	D20191115_18_01	SRM_ICC2_spg_timing_opt_area   A57_CPU
# q2019.12_ls	DC_ICC2	D20191115_18_01	SRMFm_ICC2_spg_timing_opt_area   A57_CPU
# '''

# table ='''
# r2020.09-SP	DC_ICC2	D20210113_20_30  SRM_ICC2_spg_timing_opt_area	dcp632_teague
# r2020.09-SP	DC_ICC2	D20210113_20_30  SRM_ICC2_spg_timing_opt_area   dcp564_leon3_mp_20_sset_ssink
# r2020.09-SP	DC_ICC2	D20210113_20_30  SRMFm_ICC2_spg_timing_opt_area	dcp632_teague
# r2020.09-SP	DC_ICC2	D20210113_20_30  SRMFm_ICC2_spg_timing_opt_area   dcp564_leon3_mp_20_sset_ssink
# '''


# rerun_fast(table)

# branch   = 'rsp'
# suite    = 'DC_ICC2'
# nightly  = 'D20210430_20_30'
# flow     = 'SRM_ICC2_spg_timing_opt_area'
# designs  = 'dcp564_leon3_mp_20_sset_ssink'

# # rerun(branch, suite, nightly,flow , designs)
# # # raw_failed = '''
# # #      SRM_ICC2_spg_timing_opt_area/Vega20-VGT-T     
# # # '''

# # # rerun_as_in_prs(branch,suite,nightly,raw_failed)

# # #nightly  = 'D20201204_20_30'

# raw_failed = '''
#     SRM_ICC2_spg_timing_opt_area_link_placer_baseline/dcp520_ccu_msw:PLIncmp (dcp520_ccu_msw.icprpt.out:1)
#     SRM_ICC2_spg_timing_opt_area_link_placer_ATCnBAP/dcp520_ccu_msw:PLIncmp (dcp520_ccu_msw.icprpt.out:1)
#     RSP1_SRM_ICC2_spg_timing_opt_area_link_placer_ATCnBAP/A73_Non_CPU:DCFail (A73_Non_CPU.dcopt.out:299058)
#     RSP2_SRM_ICC2_spg_timing_opt_area_link_placer_ATCnBAP/A73_Non_CPU:DCFail (A73_Non_CPU.dcopt.out:299058)
#     SRM_ICC2_spg_timing_opt_area_link_placer_baseline/dcp616_falcon_cpu:PLIncmp (dcp616_falcon_cpu.icprpt.out:1)
#     SRM_ICC2_spg_timing_opt_area_link_placer_ATCnBAP/dcp616_falcon_cpu:PLIncmp (dcp616_falcon_cpu.icprpt.out:1)
#     SRM_ICC2_spg_timing_opt_area_link_placer_baseline/dce_dchp_t:PLIncmp (dce_dchp_t.icprpt.out:1)
#     SRM_ICC2_spg_timing_opt_area_link_placer_ATCnBAP/dce_dchp_t:PLIncmp (dce_dchp_t.icprpt.out:1)
#     SRM_ICC2_spg_timing_opt_area_link_placer_baseline/A53:PLIncmp (A53.icprpt.out:2)
#     SRM_ICC2_spg_timing_opt_area_link_placer_ATCnBAP/A53:PLIncmp (A53.icprpt.out:1)
#     SRM_ICC2_spg_timing_opt_area_link_placer_baseline/A53_ARM:PLIncmp (A53_ARM.nwprpt.out:1)
#     SRM_ICC2_spg_timing_opt_area_link_placer_ATCnBAP/A53_ARM:PLIncmp (A53_ARM.icprpt.out:1)
#     SRM_ICC2_spg_timing_opt_area_link_placer_ATCnBAP/Vega20-VGT-T:PLIncmp (Vega20-VGT-T.icprpt.out:1)
#     SRM_ICC2_spg_timing_opt_area_link_placer_baseline/Vega20-DSA-T:PLIncmp (Vega20-DSA-T.icprpt.out:1)
#     SRM_ICC2_spg_timing_opt_area_link_placer_ATCnBAP/Vega20-DSA-T:PLIncmp (Vega20-DSA-T.nwprpt.out:1)
#     SRM_ICC2_spg_timing_opt_area_link_placer_ATCnBAP/dcp270_enterprise_UPF:PLIncmp (dcp270_enterprise_UPF.icprpt.out:1)
#     SRM_ICC2_spg_timing_opt_area_link_placer_baseline/Vega20-CPF-T:DCFail (Vega20-CPF-T.dcopt.out:213601)
#     SRM_ICC2_spg_timing_opt_area_link_placer_ATCnBAP/Vega20-CPF-T:DCFail (Vega20-CPF-T.dcopt.out:213671)
#     SRM_ICC2_spg_timing_opt_area_link_placer_baseline/dcp276_xbar:PLIncmp (dcp276_xbar.icprpt.out:1)
#     SRM_ICC2_spg_timing_opt_area_link_placer_ATCnBAP/xpc_fp:PLIncmp (xpc_fp.icprpt.out:1)
#     SRM_ICC2_spg_timing_opt_area_link_placer_ATCnBAP/dcp522_c8docsis31_rx_top:PLIncmp (dcp522_c8docsis31_rx_top.icprpt.out:1)
#     SRM_ICC2_spg_timing_opt_area_link_placer_ATCnBAP/dcp519_fdeq_pnrb:DCFail (dcp519_fdeq_pnrb.dcopt.out:27126)
#     SRM_ICC2_spg_timing_opt_area_link_placer_ATCnBAP/BLOCK_BL:PLIncmp (BLOCK_BL.icprpt.out:1)
#     SRM_ICC2_spg_timing_opt_area_link_placer_ATCnBAP/dcp630_jones:DCFail (dcp630_jones.dcopt.out:474348)
#     SRM_ICC2_spg_timing_opt_area_link_placer_ATCnBAP/dcp631_mercer:DCFail (dcp631_mercer.dcopt.out:95757)
#     SRM_ICC2_spg_timing_opt_area_link_placer_baseline/dcp632_teague:DCFail (dcp632_teague.dcopt.out:290519)
# '''

# rerun_as_in_prs(branch,suite,nightly,raw_failed)

# # #############
# # # A57_Non_CPU
# # # A73_CPU
# # # A72_CPU
# # # A57_CPU
# # # A75_prome
