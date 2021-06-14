import os , re, random

propts_file = 'propts.cfg' 

def get_flow_def(**kwargs):

    propts      = kwargs.get('propts_cfg')
    target_flow = kwargs.get('target_flow') 

    propts_lines = open(propts).readlines()

    #flow_ptrn = r'^flow\.'+ target_flow + '\.*|^flow\.'+ target_flow + '::\s*|^flow\.'+ target_flow + ':\s*'
    flow_ptrn = '^flow\.(\w+).+'
    in_flow = False

    flow_def = ''
    for line in propts_lines:
        
        m_flow_start = re.match(flow_ptrn, line)
        m_append = re.match('^::*', line)

        if m_flow_start:
            if m_flow_start.group(1) == target_flow:
                flow_def += line
                in_flow = True
        elif in_flow and  m_append:
            flow_def += line
        else:
            in_flow = False

    return flow_def

def append_to_propts(propts, extra_def):

    try:
        propts_file = open(propts,'a+')
        propts_file.write('\n### extra run flows definition ###')
        propts_file.write(extra_def)
        propts_file.close()
        print('extra def appended to %s'%propts)
        return True

    except:
        print('Could\'t append extra def to %s'%propts)
        return False

def make_extra(
    flow, suffix, title, dc_extra_settings, raw_extra_settings, stages, dc_bin, icc2_bin, fm_bin, fm_flow, designs, propts
    ):
    
    extra_name = '%s%s'%(flow,suffix)
    fm_extra_name = '%s%s'%(fm_flow,suffix)

    flow_def = get_flow_def(propts_cfg = propts, target_flow = flow)

    extra_def = '\n\n# copy of %s for extra run settings #\n'%flow
    extra_def += flow_def.replace(flow, extra_name)
    extra_def += '\n# override settings for extra run #\n'
        
    if title != '': 
        extra_def += 'flow.%s.title: <b> %s</b>\n'%(extra_name, title)
    
    # tools     
    add_fm = False

    if stages == 'DC' or stages == 'DC FM':
        
        extra_def += 'flow.%s::\n'%extra_name
        extra_def += ':: tools: rtlopt dcopt dcrpt\n'
        
        if 'FM' in stages:
            add_fm = True

    elif stages == 'DC ICC2' or stages == 'DC ICC2 FM':
        
        extra_def += 'flow.%s::\n'%extra_name
        extra_def += ':: tools: rtlopt dcopt dcrpt dccmd nw2nlib nwpopt nwprpt\n'
        
        if 'FM' in stages:
            add_fm = True
    elif stages == '':
        pass
    else:
        pass
    
    # bins 
    if dc_bin != '':
        extra_def += 'flow.%s::\n'%extra_name
        extra_def += ':: tool.rtlopt.bin: %s\n'%dc_bin
        extra_def += ':: tool.dcopt.bin: %s\n'%dc_bin
        extra_def += ':: tool.dcrpt.bin: %s\n'%dc_bin

    if icc2_bin != '':
        extra_def += 'flow.%s::\n'%extra_name
        extra_def += ':: tool.nw2nlib.bin: %s\n'%icc2_bin
        extra_def += ':: tool.nwpopt.bin: %s\n'%icc2_bin
        extra_def += ':: tool.nwprpt.bin: %s\n'%icc2_bin

    # extra settings    
    if dc_extra_settings != '':
        extra_def += 'flow.%s::\n'%extra_name
        extra_def += ':: tool.dcopt.opts::\n'

        for line in dc_extra_settings.splitlines(): 
            extra_def += ':: :: %s\n'%line.strip()

    if raw_extra_settings != '':
        # extra_def += 'flow.%s::\n'%extra_name

        for line in raw_extra_settings.splitlines(): 
            extra_def += ':: %s'%line.strip()

    # fm
    if fm_flow != '':
        fm_flow_def = get_flow_def(propts_cfg = propts, target_flow = fm_flow) 
        fm_extra_flow_def = fm_flow_def.replace(fm_flow, fm_extra_name)
        
        fm_extra_flow_def = fm_extra_flow_def.replace(flow, extra_name)
        # print(fm_extra_flow_def)

    if designs != '':
        extra_def += 'flow.%s:: designs: %s\n'%(extra_name,designs)
    
    if add_fm:
        extra_def += '\n\n'
        extra_def += '# FM verification for extra run %s\n'%extra_name
        extra_def += fm_extra_flow_def
        extra_def += '# override title of FM verification\n'
        extra_def += 'flow.%s.title: Fm verification for %s <i>%s</i>\n'%(fm_extra_name,extra_name,title)

        if designs != '':
            extra_def += 'flow.%s:: designs: %s\n'%(fm_extra_name,designs)
            
    # print(extra_def)

    # append to the original propts
    append_to_propts(propts, extra_def)
    
    return extra_name

def make_extra_prbench(
    flow, suffix, title, dc_extra_settings, raw_extra_settings, stages, dc_bin, icc2_bin, fm_bin, fm_flow, designs, propts
    ):
    
    extra_name = '%s%s'%(flow,suffix)
    fm_extra_name = '%s%s'%(fm_flow,suffix)

    flow_def = get_flow_def(propts_cfg = propts, target_flow = flow)

    extra_def = '\n\n# copy of %s for extra run settings #\n'%flow

    # replacing names
    extra_def += flow_def.replace(flow, extra_name)
    # # extra settings
    # # redefined above for prbench flavour
    t_tag_presto      = ':: :: ##-- START PRESTO: INSERT YOUR EXPERIMETAL SWITCHES/SETTINGS FOR MAIN COMPILE (PLESE DO NOT REMOVE/MODIFY THIS LINE)'
    t_tag_compile     = ':: :: ##-- START COMPILE: INSERT YOUR EXPERIMETAL SWITCHES/SETTINGS FOR MAIN COMPILE (PLESE DO NOT REMOVE/MODIFY THIS LINE)'
    t_tag_incremental = ':: :: ##-- START INCREMENTAL: INSERT YOUR EXPERIMETAL SWITCHES/SETTINGS FOR INCREMENTAL COMPILE (PLESE DO NOT REMOVE/MODIFY THIS LINE)'
    t_tag_post        = ':: :: ##-- START POST: INSERT YOUR EXPERIMETAL SWITCHES/SETTINGS FOR MAIN COMPILE (PLESE DO NOT REMOVE/MODIFY THIS LINE)'
    
    if dc_extra_settings != '':

        e_set = ''
        for line in dc_extra_settings.splitlines(): 
            e_set += ':: :: %s\n'%line.strip()

        extra_def = extra_def.replace(t_tag_compile, t_tag_compile + '\n' + e_set)
        
    # if raw_extra_settings != '':
    #     # extra_def += 'flow.%s::\n'%extra_name

    #     for line in raw_extra_settings.splitlines(): 
    #         extra_def += ':: %s'%line.strip()
    
    extra_def += '\n# override settings for extra run #\n'
        
    if title != '': 
        extra_def += 'flow.%s.title: <b> %s</b>\n'%(extra_name, title)
    
    # tools     
    add_fm = False

    # if stages == 'DC' or stages == 'DC FM':
        
    #     extra_def += 'flow.%s::\n'%extra_name
    #     extra_def += ':: tools: rtlopt dcopt dcrpt\n'
        
    #     if 'FM' in stages:
    #         add_fm = True

    # elif stages == 'DC ICC2' or stages == 'DC ICC2 FM':
        
    #     extra_def += 'flow.%s::\n'%extra_name
    #     extra_def += ':: tools: rtlopt dcopt dcrpt dccmd nw2nlib nwpopt nwprpt\n'
        
    #     if 'FM' in stages:
    #         add_fm = True
    # elif stages == '':
    #     pass
    # else:
    #     pass
    
    # bins 
    if dc_bin != '':
        # extra_def += 'flow.%s::\n'%extra_name
        extra_def += ':: tool.cmd_dcopt.bin: %s\n'%dc_bin

    # NOT needed in HPD
    # if icc2_bin != '':
    #     # extra_def += 'flow.%s::\n'%extra_name
    #     extra_def += ':: tool.nw2nlib.bin: %s\n'%icc2_bin
    #     extra_def += ':: tool.nwpopt.bin: %s\n'%icc2_bin
    #     extra_def += ':: tool.nwprpt.bin: %s\n'%icc2_bin

    # # extra settings
    # redefined above for prbench flavour
    # if dc_extra_settings != '':
    #     # extra_def += 'flow.%s::\n'%extra_name
    #     extra_def += ':: tool.dcopt.opts::\n'

    #     for line in dc_extra_settings.splitlines(): 
    #         extra_def += ':: :: %s\n'%line.strip()

    # if raw_extra_settings != '':
    #     # extra_def += 'flow.%s::\n'%extra_name

    #     for line in raw_extra_settings.splitlines(): 
    #         extra_def += ':: %s'%line.strip()

    # fm
    if fm_flow != '':
        fm_flow_def = get_flow_def(propts_cfg = propts, target_flow = fm_flow) 
        fm_extra_flow_def = fm_flow_def.replace(fm_flow, fm_extra_name)
        
        fm_extra_flow_def = fm_extra_flow_def.replace(flow, extra_name)
        # print(fm_extra_flow_def)

    if designs != '':
        extra_def += 'flow.%s:: designs: %s\n'%(extra_name,designs)
    
    if add_fm:
        extra_def += '\n\n'
        extra_def += '# FM verification for extra run %s\n'%extra_name
        extra_def += fm_extra_flow_def
        extra_def += '# override title of FM verification\n'
        extra_def += 'flow.%s.title: Fm verification for %s <i>%s</i>\n'%(fm_extra_name,extra_name,title)

        if designs != '':
            extra_def += 'flow.%s:: designs: %s\n'%(fm_extra_name,designs)
            
    # print(extra_def)

    # append to the original propts
    append_to_propts(propts, extra_def)
    
    return extra_name

def submit_extra_run(**kwargs):
    # arguments
    #-----------------------------------------#
    # configs
    users    = kwargs.get('users', '').split()
    launcher = kwargs.get('launcher', '')
    branch   = kwargs.get('branch')
    suite    = kwargs.get('suite')

    launcher_scripts = kwargs.get('launcher_scripts')
    #-----------------------------------------#
    # user args
    nightly  = kwargs.get('nightly') 
    flow     = kwargs.get('flow')
    suffix   = kwargs.get('suffix', '_ex')
    title    = kwargs.get('title')
    dc_extra_settings  = kwargs.get('dc_extra_settings', '')
    raw_extra_settings = kwargs.get('raw_extra_settings', '')
    stages   = kwargs.get('stages', '')
    dc_bin   = kwargs.get('dc_bin', '')
    icc2_bin = kwargs.get('icc2_bin', '')
    fm_bin   = kwargs.get('fm_bin', '')
    fm_flow = kwargs.get('fm_flow', '')
    designs = kwargs.get('designs', '')
    prbench = kwargs.get('prbench', False)
    #-----------------------------------------#
    
    propts = '%s/%s/%s/prs/run/propts.cfg'%(branch,suite,nightly)
    
    if not prbench:
        extra_name = make_extra(
            flow, suffix, title, dc_extra_settings, raw_extra_settings, stages, dc_bin, icc2_bin, fm_bin, fm_flow, designs, propts
        )
    else:
        extra_name = make_extra_prbench(
            flow, suffix, title, dc_extra_settings, raw_extra_settings, stages, dc_bin, icc2_bin, fm_bin, fm_flow, designs, propts
        )

    # prepare kick-off from 24x7 disk
    kick_lines  = '\n## added for extra run kick-off ##\n'
    kick_lines += 'flows:   %s\n'%extra_name

    if designs != '':
        kick_lines += 'designs: %s\n'%designs
    kick_lines += '####################################\n'

    # pick a random user 
    user            = random.choice(users)
        
    run_disk_propts_file = os.readlink('%s/%s/%s/prs/run.24x7_%s.%s/propts.cfg'%(branch,suite,nightly,launcher,user))
    
    try:
        run_disk_propts = open(run_disk_propts_file, 'a+')
        run_disk_propts.write(kick_lines)
        run_disk_propts.close()
    except:
        pass

    real_run_dir = os.path.dirname(run_disk_propts_file)
    # print(real_run_dir) 

    # kick-off from 24x7
    cmd = 'rsh -l %s localhost \"cd %s ; %s/run_prs_%s.csh\"'%(user,real_run_dir,launcher_scripts,launcher)
    print('Kicking-off!!')
    try:
        print(cmd)
        os.system(cmd)
    except:
        print('wasn\'t possible kick-off your ex.')

    # link from run disk to report disk
    os.symlink('%s/%s'%(real_run_dir,extra_name), '%s/%s/%s/prs/run/%s'%(branch,suite,nightly,extra_name))

def submit_regular(**kwargs):
    # arguments
    #-----------------------------------------#
    # configs
    users    = kwargs.get('users', '').split()
    launcher = kwargs.get('launcher', '')
    branch   = kwargs.get('branch')
    suite    = kwargs.get('suite')

    launcher_scripts = kwargs.get('launcher_scripts')
    #-----------------------------------------#
    # user args
    nightly  = kwargs.get('nightly') 
    flow     = kwargs.get('flow')
    designs  = kwargs.get('designs', '')
    #-----------------------------------------#
    
    propts = '%s/%s/%s/prs/run/propts.cfg'%(branch,suite,nightly)
    
    # prepare kick-off from 24x7 disk
    if get_flow_def( propts_cfg = propts, target_flow = flow) != '':
        
        kick_lines  = '\n## adding flows to regular run ##\n'
        kick_lines += 'flow.%s:: designs: %s\n'%(flow,designs)
        kick_lines += 'flows:   %s\n'%flow
        kick_lines += 'designs: %s\n'%designs
        kick_lines += '####################################\n'

        # pick a random user 
        user            = random.choice(users)
            
        run_disk_propts_file = os.readlink('%s/%s/%s/prs/run.24x7_%s.%s/propts.cfg'%(branch,suite,nightly,launcher,user))
        
        
        try:
            run_disk_propts = open(run_disk_propts_file, 'a+')
            run_disk_propts.write(kick_lines)
            run_disk_propts.close()
        except:
            print('propts not written')

        real_run_dir = os.path.dirname(run_disk_propts_file)
        # print(real_run_dir) 

        # kick-off from 24x7
        cmd = 'rsh -l %s localhost \"cd %s ; %s/run_prs_%s.csh\"'%(user,real_run_dir,launcher_scripts,launcher)
        print('Kicking-off!!')
        try:
            print(cmd)
            os.system(cmd)
        except:
            print('wasn\'t possible kick-off your ex.')

        # link from run disk to report disk
        run_disk_flow = '%s/%s'%(real_run_dir,flow)
        rep_disk_flow = '%s/%s/%s/prs/run/%s'%(branch,suite,nightly,flow)
        
        try:
            os.symlink(run_disk_flow, rep_disk_flow )
            print('flow linked to report disk')
        except:
            print('Couldn\'t link\n %s -> %s'%(run_disk_flow,rep_disk_flow))    
    else:
        print('flow %s not in the propts.cfg'%flow)

def add_regular_report(**kwargs):
    # arguments
    #-----------------------------------------#
    # configs
    branch   = kwargs.get('branch')
    suite    = kwargs.get('suite')
    # user args

    nightly     = kwargs.get('nightly') 
    flows       = kwargs.get('flows').split()
    baseline    = kwargs.get('baseline')
    report_name   = kwargs.get('report_name')
    report_script = kwargs.get('report_script')

    #-----------------------------------------#

    # make report dir
    prs_run_dir = '%s/%s/%s/prs/run'%(branch,suite,nightly)
    rep_dir     = '%s/rpt_%s'%(prs_run_dir,report_name)
    
    try:
        os.mkdir(rep_dir)
        os.symlink('../propts.cfg','%s/propts.cfg'%(rep_dir))
    except:
        pass

    for flow in flows:
        try:
            os.symlink('../%s'%flow,'%s/%s'%(rep_dir,flow))

        except:
            pass    
    print('report dir and links done.')
    # write subreport script
    script_file  = '%s/%s/%s/prs/run/%s'%(branch,suite,nightly,report_script)
    
    if os.path.exists(script_file):
        
        script_fl = open(script_file, 'r')
        script_lines = script_fl.readlines()
        script_fl.close()

        ptrn_setting = '\s+set\s+(\w+)\s+=\s+\"(.+)\"'
    
        new_script = ''

        for line in script_lines:

            m = re.match(ptrn_setting, line)
            if m:
                setting = m.group(1)
                
                if   setting == 'dir':
                    new_script += '\tset dir = \"rpt_%s\"\n'%report_name
                elif setting == 'base_flow':
                    new_script += '\tset base_flow = \"%s\"\n'%baseline
                elif setting == 'flows':
                    new_script += '\tset flows = \"%s\"\n'%','.join(flows)
                elif setting == 'report_name':
                    new_script += '\tset report_name = \"%s\"\n'%report_name
                else:
                    new_script +=  line
            else:
                new_script += line

        new_script_path = '%s/subreport_%s.csh'%(prs_run_dir,report_name)

        try:
            new_script_file = open(new_script_path, 'w')
            new_script_file.write(new_script)
            new_script_file.close()
            os.chmod(new_script_path,0o777)
        except:
            pass

        print('report script %s has been added.'%report_name)

    else:
        print('script %s not found'%report_script)

def add_virtual_flow(**kwargs):
    # arguments
    #-----------------------------------------#
    # configs
    branch   = kwargs.get('branch')
    suite    = kwargs.get('suite')
    # user args

    nightly     = kwargs.get('nightly') 
    flows       = kwargs.get('flows').split()
    virtual_flow = kwargs.get('virtual_flow')
    virtual_title = kwargs.get('virtual_title')
    #-----------------------------------------#

    # put title in propts
    prs_run_dir = '%s/%s/%s/prs/run'%(branch,suite,nightly)
    propts = '%s/%s/%s/prs/run/propts.cfg'%(branch,suite,nightly)

    v_title  = '## virtual flow title ##\n'
    v_title += '## contains %s\n'%','.join(flows)
    v_title += 'flow.%s.title: %s\n'%(virtual_flow,virtual_title)
    v_title += '########################'
    
    try:
        propts_file = open(propts, 'a+')
        propts_file.write(v_title)
        propts_file.close()
    
    except:
        print('Couldn\'t open %s for append.'%propts)

    # make dir n links
    v_flow_dir = '%s/%s'%(prs_run_dir,virtual_flow)

    try:
        # dir for the v_flow
        os.mkdir(v_flow_dir)
    except:
        pass
    
    # now put the links from the original flows
    for flow in flows:
        flow_dir = '%s/%s'%(prs_run_dir,flow)

        #print(flow_dir)

        designs = []
        if os.path.exists(flow_dir):
            designs = os.listdir(flow_dir)
        
        #print(designs)

        if designs != []:
            pass
            for design in designs:
                try:
                    os.symlink('../%s/%s'%(flow,design),'%s/%s'%(v_flow_dir,design))
                except:
                    pass

    print('links done')



# submit_extra_run(
#     launcher_scripts = '/remote/dtdata1/testdata/prs/syn/scripts/nightly/run_scripts',
#     users            = 'rmorale',
#     launcher         = 'gala',
#     branch           = '/remote/dcopt077/nightly_prs/p2019.03-SP',
#     suite            = 'HPDRT',
#     title            = '<b> Do not stop after first move type</b>',
#     nightly          = 'D20191010_20_30',
#     flow             = _flow,
#     suffix           = '_vex_00',
#     dc_extra_settings = 'set lnc_flow_gbuf_loop_engine_stop_after_first_move false',
#     designs          = flows[_flow],
#     prbench          = True if _flow == 'HPD_prbench' else False
# )


# ######################################
# add_virtual_flow(
#     branch           = '/remote/dcopt077/nightly_prs/p2019.03-SP',
#     suite            = 'HPDRT',
#     nightly          = 'D20191010_20_30',
#     flows            = 'HPD_cust_dc_vex_00 HPD_cust_DC_Platform_vex_00 HPD_prbench_vex_00',
#     virtual_flow     = 'HPD_DCG_rt_vex_00',
#     virtual_title    = '<b> Do not stop after first move type</b>',
# )


# add_regular_report(
#     branch           = '/remote/dcopt077/nightly_prs/p2019.03-SP',
#     suite            = 'HPDRT',
#     nightly          = 'D20191010_20_30',
#     baseline         = 'HPD_DCG_rt',
#     flows            = 'HPD_DCG_rt HPD_DCG_rt_vex_00 N_HPD_DCG_rt',
#     report_name      = 'dongjin_00',
#     report_script    = 'subreport_hpd_dcg.csh',
# )


e_switches ='''
set glo_power_wlm_run_lvt_legalize_force_disable_lvt TRUE
set cgopt_reinit_lvt_info TRUE
'''
same_des = 'dcp236_dhm_ram dcp245_SPEEDY28_TOP dcp259_morpheus dcp269_rob dcp280_avd_top dcp427_DWC_usb3 dcp428_DWC_ddr dcp431_Sc6 dcp432_CORTEXA7 dcp516_bayonet dcp552_disk dcp556_DSH dcp558_gif_fp dcp567_mse_block1 dcp569_GORDON dcp570_b33 dcp571_hrp_xb_m dcp572_slh_fp dcp573_legato_mx dcp575_emif dcp578_bim_fp dcp579_pba_fp dcp580_idc dcp585_lcn40_top dcp586_ip2 dcp587_sxw dcp591_ip5 dcp595_gra_ushader dcp596_ibe dcp597_mmu_thdo dcp606_tig_neon dcp609_CORTEXA8 dcp611_arm926ejs dcp615_CortexM3 dcp616_falcon_cpu dcp778_datapath dcp780_cbs_pollux_tx_dig dcp800_ip4 dcp801_sm15_port dcp804_nu_tils dcp805_accelerator dcp806_hd_chnl'

submit_regular(
    launcher_scripts = '/remote/dtdata1/testdata/prs/syn/scripts/nightly/run_scripts',
    users            = 'dcntqor6 dcntqor7',
    launcher         = 'gala-icc2',
    branch           = '/remote/dcopt077/nightly_prs/p2019.03-SP',
    suite            = 'DC_ICC2',
    nightly          = 'D20191009_20_30',
    flow             = 'SRM_hplvt_spg',
    designs          = same_des,
)


submit_extra_run(
    launcher_scripts = '/remote/dtdata1/testdata/prs/syn/scripts/nightly/run_scripts',
    users            = 'dcntqor6 dcntqor7',
    launcher         = 'gala-icc2',
    branch           = '/remote/dcopt077/nightly_prs/p2019.03-SP',
    stages           = '',
    suite            = 'DC_ICC2',
    dc_bin           = '',
    icc2_bin         = '',
    title            = '<b>  pLVT flow fixes</b>',
    nightly          = 'D20191009_20_30',
    flow             = 'SRM_hplvt_spg',
    suffix           = '_vex_jon',
    dc_extra_settings = e_switches,
    designs          = same_des,
)

add_regular_report(
    branch           = '/remote/dcopt077/nightly_prs/p2019.03-SP',
    suite            = 'DC_ICC2',
    nightly          = 'D20191009_20_30',
    baseline         = 'SRM_hplvt_spg',
    flows            = 'SRM_hplvt_spg_vex_jon SRM_hplvt_spg',
    report_name      = 'vex_jon',
    report_script    = 'subreport_diff.srm_icc2_spg_opt_area.csh',
)

# submit_extra_run(
#     launcher_scripts = '/remote/dtdata1/testdata/prs/syn/scripts/nightly/run_scripts',
#     users            = 'dcntqor6 dcntqor7',
#     launcher         = 'gala-icc2',
#     branch           = '/slowfs/dcopt036/nightly_prs/q2019.12_ls',
#     stages           = 'DC ICC2',
#     suite            = 'DC_ICC2',
#     dc_bin           = '/u/re/spf_p2019.03_sp_dev/image_NIGHTLY/D20190918_20_30/linux64/syn/bin/dcnxt_shell',
#     icc2_bin         = '/global/apps/icc2_2019.03-SP1/linux64/nwtn/bin/icc2_exec',
#     title            = '<b> DCNXT P2019.03 (09/18) + ICC2 P-2019.03-SP1 </b>',
#     nightly          = 'D20190918_12_01',
#     flow             = 'SRM_ICC2_spg_timing_opt_area',
#     suffix           = '_icc2_ex_02',
#     dc_extra_settings = '',
#     designs          = 'dcp275_archipelago',
# )

# submit_extra_run(
#     launcher_scripts = '/remote/dtdata1/testdata/prs/syn/scripts/nightly/run_scripts',
#     users            = 'dcntqor6 dcntqor7',
#     launcher         = 'gala-icc2',
#     branch           = '/slowfs/dcopt036/nightly_prs/q2019.12_ls',
#     stages           = 'DC ICC2',
#     suite            = 'DC_ICC2',
#     dc_bin           = '/u/re/spf_p2019.03_sp_dev/image_NIGHTLY/D20190918_20_30/linux64/syn/bin/dcnxt_shell',
#     icc2_bin         = '/u/nwtnmgr/image/O-2018.06-SP3/D20181026_4464631/Testing/linux64/nwtn/bin/icc2_exec',
#     title            = '<b> DCNXT P2019.03 (09/18) + ICC2 O-2018.06-SP3 </b>',
#     nightly          = 'D20190918_12_01',
#     flow             = 'SRM_ICC2_spg_timing_opt_area',
#     suffix           = '_icc2_ex_03',
#     dc_extra_settings = '',
#     designs          = 'dcp275_archipelago',
# )

# add_regular_report(
#     branch           = '/slowfs/dcopt036/nightly_prs/q2019.12_ls',
#     suite            = 'DC_ICC2',
#     nightly          = 'D20190927_12_01',
#     baseline         = 'P_UPF_SRM_ICC2_spg',
#     flows            = 'P_UPF_SRM_ICC2_spg SRM_ICC2_spg_timing_opt_area_des_upf UPF_SRM_ICC2_spg',
#     report_name      = '_des_upf',
#     report_script    = 'subreport_UPF.srm_spg.csh',
# )