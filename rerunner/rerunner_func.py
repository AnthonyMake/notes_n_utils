from pathlib import Path
import os, re, sys


def rerun(branch,suite,nightly,flow,designs):
    branch_map = {}

    if len(branch)>3:
        branch = branch
    else:
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

# branch   = 'sls'
# suite    = 'DC_ICC2'
# nightly  = 'D20210414_12_01'
# flow     = 'SRM_ICC2_spg_timing_power_opt_area'
# designs  = 'A57_Non_CPU'

# rerun(branch, suite, nightly,flow , designs)

# exit()
# # # raw_failed = '''
# # #      SRM_ICC2_spg_timing_opt_area/Vega20-VGT-T     
# # # '''

# # # rerun_as_in_prs(branch,suite,nightly,raw_failed)

# # #nightly  = 'D20201204_20_30'

# raw_failed = '''
#     SRM_ICC2_spg_timing_power_opt_area_scib_all_ex18/dcp245_SPEEDY28_TOP:DRFail (dcp245_SPEEDY28_TOP.dcrpt.out:747)
#     SRM_ICC2_spg_timing_power_opt_area_scib_all_ex18/dcp564_leon3_mp_20_sset_ssink:HIIncmp (dcp564_leon3_mp_20_sset_ssink.hinfo.out:2)
#     SRM_ICC2_spg_timing_power_opt_area_scib_all_ex18/ARCHS38_7nm:PLIncmp
#     SRM_ICC2_spg_timing_power_opt_area_scib_all_ex16/archipelago_N12_6T:PLFail (archipelago_N12_6T.nwprpt.out:592)
#     SRM_ICC2_spg_timing_power_opt_area_scib_all_ex18/archipelago_N12_6T:HIIncmp (archipelago_N12_6T.hinfo.out:2)
#     SRM_ICC2_spg_timing_power_opt_area_scib_all_ex16/dcp428_DWC_ddr:PLIncmp (dcp428_DWC_ddr.icprpt.out:2)
#     SRM_ICC2_spg_timing_power_opt_area_scib_all_ex17/dcp428_DWC_ddr:PLFail (dcp428_DWC_ddr.nwpopt.out:11369)
#     SRM_ICC2_spg_timing_power_opt_area_scib_all_ex18/dcp428_DWC_ddr:DRFail (dcp428_DWC_ddr.dcrpt.out:527)
#     SRM_ICC2_spg_timing_power_opt_area_scib_all_ex19/dcp428_DWC_ddr:NDBIncmp (dcp428_DWC_ddr.nw2nlib.out:2)
#     SRM_ICC2_spg_timing_power_opt_area_scib_all_ex16/X5376:PLIncmp
#     SRM_ICC2_spg_timing_power_opt_area_scib_all_ex18/X5376:DRFail (X5376.dcrpt.out:430)
#     SRM_ICC2_spg_timing_power_opt_area_scib_all_ex19/X5376:PLIncmp
#     SRM_ICC2_spg_timing_power_opt_area_scib_all_ex16/dcp427_DWC_usb3:CMFail (dcp427_DWC_usb3.dccmd.out:124)
#     SRM_ICC2_spg_timing_power_opt_area_scib_all_ex17/dcp427_DWC_usb3:PLIncmp
#     SRM_ICC2_spg_timing_power_opt_area_scib_all_ex18/dcp427_DWC_usb3:PCIncmp
#     SRM_ICC2_spg_timing_power_opt_area_scib_all_ex19/dcp427_DWC_usb3:PLIncmp
#     SRM_ICC2_spg_timing_power_opt_area_scib_all_ex16/dcp569_GORDON:NDBIncmp (dcp569_GORDON.nw2nlib.out:2)
#     SRM_ICC2_spg_timing_power_opt_area_scib_all_ex18/dcp569_GORDON:RTFail (dcp569_GORDON.rtlopt.out:4588)
#     SRM_ICC2_spg_timing_power_opt_area_scib_all_ex19/dcp569_GORDON:PLIncmp
#     SRM_ICC2_spg_timing_power_opt_area_scib_all_ex16/dcp212_Xm_Xttop:CMFail (dcp212_Xm_Xttop.dccmd.out:609)
#     SRM_ICC2_spg_timing_power_opt_area_scib_all_ex17/dcp212_Xm_Xttop:PLIncmp
#     SRM_ICC2_spg_timing_power_opt_area_scib_all_ex18/dcp212_Xm_Xttop:PLIncmp (dcp212_Xm_Xttop.icprpt.out:2)
#     SRM_ICC2_spg_timing_power_opt_area_scib_all_ex19/dcp212_Xm_Xttop:PLFail (dcp212_Xm_Xttop.nwpopt.out:1007)
#     SRM_ICC2_spg_timing_power_opt_area_scib_all_ex16/dcp597_mmu_thdo:DRFail (dcp597_mmu_thdo.dprrpt.out:1)
#     SRM_ICC2_spg_timing_power_opt_area_scib_all_ex17/dcp597_mmu_thdo:PLIncmp (dcp597_mmu_thdo.icpopt.out:2)
#     SRM_ICC2_spg_timing_power_opt_area_scib_all_ex18/dcp597_mmu_thdo:HIIncmp (dcp597_mmu_thdo.hinfo.out:1)
#     SRM_ICC2_spg_timing_power_opt_area_scib_all_ex19/dcp597_mmu_thdo:PLIncmp (dcp597_mmu_thdo.icprpt.out:2)
#     SRM_ICC2_spg_timing_power_opt_area_scib_all_ex16/dcp246_Xm_Xtmem:PLIncmp (dcp246_Xm_Xtmem.icpopt.out:2)
#     SRM_ICC2_spg_timing_power_opt_area_scib_all_ex17/dcp246_Xm_Xtmem:DRFail (dcp246_Xm_Xtmem.dcrpt.out:1072)
#     SRM_ICC2_spg_timing_power_opt_area_scib_all_ex18/dcp246_Xm_Xtmem:DRFail (dcp246_Xm_Xtmem.dcrpt.out:1072)
#     SRM_ICC2_spg_timing_power_opt_area_scib_all_ex19/dcp246_Xm_Xtmem:PLFail (dcp246_Xm_Xtmem.nwpopt.out:8689)
#     SRM_ICC2_spg_timing_power_opt_area_scib_all_ex16/dcp247_VDD5_mux2:PLIncmp (dcp247_VDD5_mux2.icprpt.out:2)
#     SRM_ICC2_spg_timing_power_opt_area_scib_all_ex18/dcp247_VDD5_mux2:HIIncmp (dcp247_VDD5_mux2.hinfo.out:1)
#     SRM_ICC2_spg_timing_power_opt_area_scib_all_ex16/ARCHS438:DRIncmp
#     SRM_ICC2_spg_timing_power_opt_area_scib_all_ex17/ARCHS438:DRFail (ARCHS438.dprrpt.out:1)
#     SRM_ICC2_spg_timing_power_opt_area_scib_all_ex18/ARCHS438:DRFail (ARCHS438.dcrpt.out:196)
#     SRM_ICC2_spg_timing_power_opt_area_scib_all_ex19/ARCHS438:CMFail (ARCHS438.dccmd.out:238)
#     SRM_ICC2_spg_timing_power_opt_area_scib_all_ex16/dcp514_JDSIIP3A:CMFail (dcp514_JDSIIP3A.dccmd.out:302)
#     SRM_ICC2_spg_timing_power_opt_area_scib_all_ex17/dcp514_JDSIIP3A:DRFail (dcp514_JDSIIP3A.dcrpt.out:44)
#     SRM_ICC2_spg_timing_power_opt_area_scib_all_ex16/dcp599_rgx_tpu_mcu:DRFail (dcp599_rgx_tpu_mcu.dcrpt.out:44)
#     SRM_ICC2_spg_timing_power_opt_area_scib_all_ex17/dcp599_rgx_tpu_mcu:DRFail (dcp599_rgx_tpu_mcu.dcrpt.out:51)
#     SRM_ICC2_spg_timing_power_opt_area_scib_all_ex18/dcp599_rgx_tpu_mcu:DRFail (dcp599_rgx_tpu_mcu.dprrpt.out:1)
#     SRM_ICC2_spg_timing_power_opt_area_scib_all_ex19/dcp599_rgx_tpu_mcu:PLFail (dcp599_rgx_tpu_mcu.nwpopt.out:4159)
#     SRM_ICC2_spg_timing_power_opt_area_scib_all_ex16/dcp270_enterprise_UPF:DRFail (dcp270_enterprise_UPF.dcrpt.out:1281)
#     SRM_ICC2_spg_timing_power_opt_area_scib_all_ex17/dcp270_enterprise_UPF:DRFail (dcp270_enterprise_UPF.dprrpt.out:1)
#     SRM_ICC2_spg_timing_power_opt_area_scib_all_ex18/dcp270_enterprise_UPF:DRFail (dcp270_enterprise_UPF.dcrpt.out:1452)
#     SRM_ICC2_spg_timing_power_opt_area_scib_all_ex19/dcp270_enterprise_UPF:PLIncmp (dcp270_enterprise_UPF.icprpt.out:2)
#     SRM_ICC2_spg_timing_power_opt_area_scib_all/dcp276_xbar:PLIncmp
#     SRM_ICC2_spg_timing_power_opt_area_scib_all_ex16/dcp276_xbar:DRFail (dcp276_xbar.dcrpt.out:2255)
#     SRM_ICC2_spg_timing_power_opt_area_scib_all_ex17/dcp276_xbar:DRFail (dcp276_xbar.dcrpt.out:177)
#     SRM_ICC2_spg_timing_power_opt_area_scib_all_ex18/dcp276_xbar:DRIncmp
#     SRM_ICC2_spg_timing_power_opt_area_scib_all_ex19/dcp276_xbar:PLFail (dcp276_xbar.nwpopt.out:16465)
#     SRM_ICC2_spg_timing_power_opt_area_scib_all_ex16/dcp522_c8docsis31_rx_top:CMFail (dcp522_c8docsis31_rx_top.dccmd.out:355)
#     SRM_ICC2_spg_timing_power_opt_area_scib_all_ex17/dcp522_c8docsis31_rx_top:DRFail (dcp522_c8docsis31_rx_top.dcrpt.out:5047)
#     SRM_ICC2_spg_timing_power_opt_area_scib_all_ex18/dcp522_c8docsis31_rx_top:CMFail (dcp522_c8docsis31_rx_top.dccmd.out:355)
#     SRM_ICC2_spg_timing_power_opt_area_scib_all_ex19/dcp522_c8docsis31_rx_top:DRFail (dcp522_c8docsis31_rx_top.dcrpt.out:76728)
#     SRM_ICC2_spg_timing_power_opt_area_scib_all_ex16/dcp519_fdeq_pnrb:DRFail (dcp519_fdeq_pnrb.dcrpt.out:10952)
#     SRM_ICC2_spg_timing_power_opt_area_scib_all_ex18/dcp519_fdeq_pnrb:CMFail (dcp519_fdeq_pnrb.dccmd.out:198)
#     SRM_ICC2_spg_timing_power_opt_area_scib_all_ex19/dcp519_fdeq_pnrb:DRFail (dcp519_fdeq_pnrb.dcrpt.out:13484)
#     SRM_ICC2_spg_timing_power_opt_area_scib_all/BLOCK_BL:PLIncmp
#     SRM_ICC2_spg_timing_power_opt_area_scib_all_ex16/BLOCK_BL:DRFail (BLOCK_BL.dcrpt.out:4673)
#     SRM_ICC2_spg_timing_power_opt_area_scib_all_ex17/BLOCK_BL:DRFail (BLOCK_BL.dcrpt.out:4673)
#     SRM_ICC2_spg_timing_power_opt_area_scib_all_ex18/BLOCK_BL:DRFail (BLOCK_BL.dcrpt.out:4669)
#     SRM_ICC2_spg_timing_power_opt_area_scib_all_ex19/BLOCK_BL:PLIncmp (BLOCK_BL.icpopt.out:2)
#     SRM_ICC2_spg_timing_power_opt_area_scib_all/dcp630_jones:PLIncmp
#     SRM_ICC2_spg_timing_power_opt_area_scib_all_ex16/dcp630_jones:DRFail (dcp630_jones.dcrpt.out:2046)
#     SRM_ICC2_spg_timing_power_opt_area_scib_all_ex17/dcp630_jones:DRFail (dcp630_jones.dcrpt.out:2046)
#     SRM_ICC2_spg_timing_power_opt_area_scib_all_ex18/dcp630_jones:PLFail (dcp630_jones.nwpopt.out:1458)
#     SRM_ICC2_spg_timing_power_opt_area_scib_all_ex19/dcp630_jones:DRFail (dcp630_jones.dcrpt.out:49)
#     SRM_ICC2_spg_timing_power_opt_area_scib_all_ex16/dcp631_mercer:CMFail (dcp631_mercer.dccmd.out:500)
#     SRM_ICC2_spg_timing_power_opt_area_scib_all_ex17/dcp631_mercer:DRFail (dcp631_mercer.dprrpt.out:1)
#     SRM_ICC2_spg_timing_power_opt_area_scib_all_ex18/dcp631_mercer:DRFail (dcp631_mercer.dcrpt.out:458)
#     SRM_ICC2_spg_timing_power_opt_area_scib_all_ex19/dcp631_mercer:DRFail (dcp631_mercer.dcrpt.out:2041)
#     SRM_ICC2_spg_timing_power_opt_area_scib_all/dcp632_teague:DRFail (dcp632_teague.dcrpt.out:2049)
#     SRM_ICC2_spg_timing_power_opt_area_scib_all_ex16/dcp632_teague:DRFail (dcp632_teague.dprrpt.out:1)
#     SRM_ICC2_spg_timing_power_opt_area_scib_all_ex17/dcp632_teague:CMFail (dcp632_teague.dccmd.out:3867)
#     SRM_ICC2_spg_timing_power_opt_area_scib_all_ex18/dcp632_teague:CMFail (dcp632_teague.dccmd.out:794)
#     SRM_ICC2_spg_timing_power_opt_area_scib_all_ex19/dcp632_teague:DRFail (dcp632_teague.dprrpt.out:1)
# '''

# rerun_as_in_prs(branch,suite,nightly,raw_failed)

# # #############
# # A57_Non_CPU
# # A73_CPU
# # A72_CPU
# # A57_CPU
# # A75_prome
