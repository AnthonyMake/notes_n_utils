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

    
    if len(branch) >3:
        branch = branch
    else:
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

branch   = 'sls'
suite    = 'DC_ICC2'
nightly  = 'D20210529_18_01'
# flow     = 'SRM_ICC2_spg_timing_power_opt_area'
# # raw_failed = '''
# #      SRM_ICC2_spg_timing_opt_area/Vega20-VGT-T     
# # '''

# # rerun_as_in_prs(branch,suite,nightly,raw_failed)

# #nightly  = 'D20201204_20_30'

raw_failed = '''
'''

#rerun_as_in_prs(branch,suite,nightly,raw_failed)

rerun('sls', 'DC_ICC2', 'D20210529_18_01', 'SRM_ICC2_spg_timing_power_opt_area_scib_all', 'dcp427_DWC_usb3 dcp519_fdeq_pnrb dcp631_mercer dcp632_teague')
# #############
# # A57_Non_CPU
# # A73_CPU
# # A72_CPU
# # A57_CPU
# # A75_prome
