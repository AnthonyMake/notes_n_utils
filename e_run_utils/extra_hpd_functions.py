####################################
# A bunch of utilities to handle 
# daily PRS related tasks in a 
# semi-automated way
# -vasquez-
####################################

import os , sys, re, random, sys
import shutil
from datetime import date, timedelta, datetime
from jinja2 import Template, Environment, FileSystemLoader



import pprint
pp = pprint.PrettyPrinter(indent=2)

def get_flow_def(**kwargs):
    # Not intended for final user usage, it's called by function
    # returns string with desired  target flow definition and 
    # list of designs on it as a tuple (flow_def, designs_list)
    # for a given propts file

    propts      = kwargs.get('propts_cfg')
    target_flow = kwargs.get('target_flow') 

    
    propts_lines = ''
    
    if os.path.exists(propts):
        propts_lines = open(propts).readlines()
    else:
        print('Could\'t open %s\nit exists?'%propts)
        exit()

    #flow_ptrn = r'^flow\.'+ target_flow + '\.*|^flow\.'+ target_flow + '::\s*|^flow\.'+ target_flow + ':\s*'
    flow_ptrn = '^flow\.(\w+).+'
    des_patt = '^flow\.'+ target_flow +'\s*\:\:\s*designs\:\s(.+)'
    in_flow = False

    orig_designs = ''

    flow_def = ''
    got_flow = False
    for line in propts_lines:
        m_flow_start = re.match(flow_ptrn, line)
        m_append = re.match('^::*', line)
        m_comment = re.match('^#.+',line)
        if m_flow_start:
            if m_flow_start.group(1) == target_flow:
                got_flow = True
                flow_def += line
                in_flow = True
        elif in_flow and  m_append:
            flow_def += line
        elif in_flow and m_comment:
            pass
        else:
            in_flow = False

        m_des = re.match(des_patt,line)
        if m_des:
            orig_designs = m_des.group(1)


    if not got_flow: 
        print('Could\'t find %s in %s'%(target_flow, propts))
        return False, ''
    else:
        return flow_def, orig_designs

def append_to_propts(propts, extra_def):
    # just append strings to a given propts 
    # could be any text file too 
    try:
        propts_file = open(propts,'a+')
        propts_file.write('\n### extra run flows definition ###')
        propts_file.write(extra_def)
        propts_file.close()
        # print('extra def appended to %s'%propts)
        return True

    except:
        print('Could\'t append extra def to %s'%propts)
        return False

def flow_to_file(flow, propts):
    # ??? dont remember this one
    flow_def, orig_des = get_flow_def(propts_cfg = propts, target_flow = flow)

    flow_file_name = '%s.cfg'%flow
    if flow_def:

        flow_file = open(flow_file_name, 'w')
        flow_file.write(flow_def)
        flow_file.close()
        return flow_file_name
    else:
        print('couldn\'t extract %s'%flow)
        return ''

def make_extra(
    flow, suffix, title, dc_extra_settings, raw_extra_settings, stages, dc_bin, icc2_bin, fm_bin, fm_flow, designs, propts, debug, fm_extra_settings):

    # Not intended for final user usage, it's called by function
    # writes an experimental flow based on an existing one definition
    # with provided settings and put it in a given propts file
    # 
    # args 
    # -flow: target flow wich one you want to append extra settings
    # -suffix: suffix for the new experimental version of the flow
    # -title: Title you want for the name of the new flow
    # -dc_extra_settings/fm_extra_settings: switches you want to append as tool.dcopt/fmchk.opts::
    #                    new_line separated, no colons.
    # -raw_extra_settings: Could be anything you ant to append to this flow
    # -stages: could be 'DC', 'DC ICC2' or 'DC ICC2 FM' it maps to
    #          rtlopt dcopt dcrpt startdb nwpopt nwrpt fmchk clean
    #          respectively...
    # -dc_bin/icc2_bin/fm_bin: any specific exec/shell you want to use with this experimental flow
    #          it must be able to be opnened from a terminal
    # -fm_flow: name of the flow you want to use to verify Fm over your experimental flow
    # -designs: list of designs to run, if empy will inherit the hardcoded ones from original propts file
    # -debug: if true, will just print some messages
    
    extra_name = '%s%s'%(flow,suffix)
    fm_extra_name = '%s%s'%(fm_flow,suffix)

    flow_def, orig_des = get_flow_def(propts_cfg = propts, target_flow = flow)

    if flow_def:

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
            extra_def += ':: tool.dccmd.bin: %s\n'%dc_bin

        if icc2_bin != '':
            extra_def += 'flow.%s::\n'%extra_name
            extra_def += ':: tool.nw2nlib.bin: %s\n'%icc2_bin
            extra_def += ':: tool.nwpopt.bin: %s\n'%icc2_bin
            extra_def += ':: tool.nwprpt.bin: %s\n'%icc2_bin

        # extra settings    
        if dc_extra_settings != '':
            extra_def += 'flow.%s::\n'%extra_name
            extra_def += ':: tool.dcopt.opts::\n'


            for line in dc_extra_settings.strip().splitlines(): 
                extra_def += ':: :: %s\n'%line.strip()

        if raw_extra_settings != '':
            #extra_def += 'flow.%s::\n'%extra_name

            for line in raw_extra_settings.splitlines(): 
                extra_def += ':: %s\n'%line.strip()

        # fm
        if fm_flow != '':
            fm_flow_def, des_fm = get_flow_def(propts_cfg = propts, target_flow = fm_flow) 
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

            if fm_bin:
                extra_def += 'flow.%s::\n'%fm_extra_name
                extra_def += ':: tool.fmchk.bin: %s\n'%fm_bin

            # extra settings
            if fm_extra_settings != '':
                extra_def += 'flow.%s::\n'%fm_extra_name
                extra_def += ':: tool.fmchk.opts::\n'

                for line in fm_extra_settings.strip().splitlines(): 
                    extra_def += ':: :: %s\n'%line.strip()


            if designs != '':
                extra_def += 'flow.%s:: designs: %s\n'%(fm_extra_name,designs)
        # print(extra_def)
        # append to the original propts
        if not debug: append_to_propts(propts, extra_def)
        else : print('\n-------------\n%s\n-------------\n'%extra_def)
        
        if 'FM' in stages:
            return extra_name, fm_extra_name, orig_des
        else:
            return extra_name, orig_des
    else:
        return False, ''

def make_extra_custom(
    flow, suffix, title, dc_extra_settings, raw_extra_settings, stages, dc_bin, icc2_bin, fm_bin, fm_flow, designs, propts, debug, custom_flow = False
    ):
    
    # Not intended for final user usage, it's called by function
    # experimental function, it saves me once but it's not intended for wide usage.
    # same as make_extra() plus capability of source certain flow definition from a file named flow_name.cfg 

    extra_name = '%s%s'%(flow,suffix)
    fm_extra_name = '%s%s'%(fm_flow,suffix)

    if custom_flow: 
        if os.path.isfile('%s.cfg'%flow):
            new_propts = '%s.cfg'%flow
        else:
            print('no custom flow .cfg file for %s'%flow)
            return ''
    
    flow_def, orig_des = get_flow_def(propts_cfg = new_propts, target_flow = flow)

    if flow_def:

        extra_def = '\n\n# copy of %s for extra run settings #\n'%flow
        extra_def += flow_def.replace(flow, extra_name)
        extra_def += '\n# override settings for extra run #\n'
            
        if title != '': 
            extra_def += 'flow.%s.title: <b> %s</b>\n'%(extra_name, title)
        
        # tools     
        add_fm = False

        if stages == 'DC' or stages == 'DC FM':
            
            extra_def += 'flow.%s::\n'%extra_name
            extra_def += ':: tools: rtlopt dcopt dcrpt clean\n'
            
            if 'FM' in stages:
                add_fm = True

        elif stages == 'DC ICC2' or stages == 'DC ICC2 FM':
            
            extra_def += 'flow.%s::\n'%extra_name
            extra_def += ':: tools: rtlopt dcopt dcrpt dccmd nw2nlib nwpopt nwprpt clean\n'
            
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


            for line in dc_extra_settings.strip().splitlines(): 
                extra_def += ':: :: %s\n'%line.strip()

        if raw_extra_settings != '':
            #extra_def += 'flow.%s::\n'%extra_name

            for line in raw_extra_settings.splitlines(): 
                extra_def += ':: %s\n'%line.strip()

        # fm
        if fm_flow != '':
            fm_flow_def, des_fm = get_flow_def(propts_cfg = propts, target_flow = fm_flow) 
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

            if fm_bin != '':
                extra_def += 'flow.%s::\n'%fm_extra_name
                extra_def += ':: tool.fmchk.bin: %s\n'%fm_bin


            if designs != '':
                extra_def += 'flow.%s:: designs: %s\n'%(fm_extra_name,designs)
                
        # print(extra_def)

        # append to the original propts
        if not debug: append_to_propts(propts, extra_def)
        else : print('\n-------------\n%s\n-------------\n'%extra_def)
        
        return extra_name, orig_des

    else:
        return False, ''

def make_extra_prbench(
    flow, suffix, title, dc_extra_settings, raw_extra_settings, stages, dc_bin, icc2_bin, fm_bin, fm_flow, designs, propts, debug
    ):
    
    # Not intended for final user usage, it's called by function
    # deals with prbench flow used in CSS runs, its bases on hardcoded tags to deal with css flows,
    # 
    extra_name = '%s%s'%(flow,suffix)
    fm_extra_name = '%s%s'%(fm_flow,suffix)

    flow_def, orig_des = get_flow_def(propts_cfg = propts, target_flow = flow)

    if flow_def:

        extra_def = '\n\n# copy of %s for extra run settings #\n'%flow

        # replacing names
        extra_def += flow_def.replace(flow, extra_name)
        # # extra settings
        # # redefined above for prbench flavour
        t_tag_presto      = ':: :: ##-- START PRESTO: INSERT YOUR EXPERIMETAL SWITCHES/SETTINGS FOR MAIN COMPILE (PLESE DO NOT REMOVE/MODIFY THIS LINE)\n'
        t_tag_compile     = ':: :: ##-- START COMPILE: INSERT YOUR EXPERIMETAL SWITCHES/SETTINGS FOR MAIN COMPILE (PLESE DO NOT REMOVE/MODIFY THIS LINE)\n'
        t_tag_incremental = ':: :: ##-- START INCREMENTAL: INSERT YOUR EXPERIMETAL SWITCHES/SETTINGS FOR INCREMENTAL COMPILE (PLESE DO NOT REMOVE/MODIFY THIS LINE)\n'
        t_tag_post        = ':: :: ##-- START POST: INSERT YOUR EXPERIMETAL SWITCHES/SETTINGS FOR MAIN COMPILE (PLESE DO NOT REMOVE/MODIFY THIS LINE)\n'
        
        if dc_extra_settings != '':

            e_set = ''
            for line in dc_extra_settings.strip().splitlines():
                e_set += ':: :: %s\n'%line.strip()

            extra_def = extra_def.replace(t_tag_compile, t_tag_compile + e_set)
            
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
        if not debug : append_to_propts(propts, extra_def)
        else : print('\n-------------\n%s\n-------------\n'%extra_def)
        
        return extra_name, orig_des
    else:
        return False, ''

def submit_extra_run(**kwargs):
    # intended to be used by final user

    # submits an experimental run using regular prs directories of an actual nightly run
     # 
    # args 
    # -users: poll of user to kick-off jobs to farm, must have 24x7 folder at
    #         <Branch>/<Suite>/<Nightly>/prs/ directory
    # -launcher: name of the launcher script used to submit, should match 24x7.<launcher>.<user> directory names.
    # -flow: target flow wich one you want to append extra settings
    # -suffix: suffix for the new experimental version of the flow
    # -title: Title you want for the name of the new flow
    # -dc_extra_settings/fm_extra_settings: switches you want to append as tool.dcopt.opts::/tool.fmchk.out
    #                    new_line separated, no colons.
    # -raw_extra_settings: Could be anything you ant to append to this flow
    # -stages: could be 'DC', 'DC ICC2' or 'DC ICC2 FM' it maps to
    #          rtlopt dcopt dcrpt startdb nwpopt nwrpt fmchk clean
    #          respectively...
    # -dc_bin/icc2_bin/fm_bin: any specific exec/shell you want to use with this experimental flow
    #          it must be able to be opnened from a terminal
    # -fm_flow: name of the flow you want to use to verify Fm over your experimental flow
    # -designs: list of designs to run, if empy will inherit the hardcoded ones from original propts file
    # -debug: if true, will just print some messages
    # -custom_flow: flag fo source flow definition from custom file named <flow>.cfg in the current working directory
    
    
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
    fm_extra_settings = kwargs.get('fm_extra_settings','')
    designs = kwargs.get('designs', '')
    prbench = kwargs.get('prbench', False)
    debug   = kwargs.get('debug',True)
    custom_flow = kwargs.get('custom_flow', False)
    avoid_submit = kwargs.get('avoid_submit', False)
    #-----------------------------------------#
    
    propts = '%s/%s/%s/prs/run/propts.cfg'%(branch,suite,nightly)
    
    if not prbench:
        if not custom_flow:
            extra_name, orig_des = make_extra(
                flow, suffix, title, dc_extra_settings, raw_extra_settings, stages, dc_bin, icc2_bin, fm_bin, fm_flow, designs, propts, debug, fm_extra_settings)
        else:
            extra_name, orig_des = make_extra_custom(
                flow, suffix, title, dc_extra_settings, raw_extra_settings, stages, dc_bin, icc2_bin, fm_bin, fm_flow, designs, propts, debug, custom_flow
            )
    else:
        extra_name, orig_des = make_extra_prbench(
            flow, suffix, title, dc_extra_settings, raw_extra_settings, stages, dc_bin, icc2_bin, fm_bin, fm_flow, designs, propts, debug
        )

    if extra_name:
        # prepare kick-off from 24x7 disk
        kick_lines  = '\n## added for extra run kick-off ##\n'
        kick_lines += 'flows:   %s\n'%extra_name

        if designs != '':
            kick_lines += 'designs: %s\n'%designs

        else:
            kick_lines += 'designs: %s\n'%orig_des
        
        kick_lines += '####################################\n'

        # pick a random user 
        user            = random.choice(users)

        if not debug:    
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
                if not avoid_submit:
                    print(cmd)
                    os.system(cmd)
                else:
                    print('skipping submission of jobs')
            except:
                print('wasn\'t possible kick-off your ex.')

            # link from run disk to report disk
            os.symlink('%s/%s'%(real_run_dir,extra_name), '%s/%s/%s/prs/run/%s'%(branch,suite,nightly,extra_name))
            print('%s added to %s'%(extra_name,propts))
        else:
            print('---in 24x7 propts ---\n%s-----------'%kick_lines) 
    else:
        print('flow %s not found. Nothing to submit.'%flow)
        
def submit_regular(**kwargs):

    # Submits a flow already written in propts cfg but not kicked off,
    # Arguments works similar to submit_extra_run

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
    fl, designs = get_flow_def( propts_cfg = propts, target_flow = flow) 

    if fl != '':
        
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
            print('propts not written', run_disk_propts_file)

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
    # Append some desired report to working nightly run directory,
    # it deals with creation of rpt_ dir link to desired flows and subreport.csh script

    # arguments
    # flows: space separated list of flow to report
    # report_name : name for csh and report files
    # report_scripts: subreport.csh to use as template
    # debug: if true just prints the plan of things to do but does nothing

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
    debug = kwargs.get('debug', True)

    #-----------------------------------------#

    # make report dir
    prs_run_dir = '%s/%s/%s/prs/run'%(branch,suite,nightly)
    rep_dir     = '%s/rpt_%s'%(prs_run_dir,report_name)
    
    try:
        if not debug:
            os.mkdir(rep_dir)
            os.symlink('../propts.cfg','%s/propts.cfg'%(rep_dir))
        else:
            print('make this dir %s'%rep_dir)
            print('sym link ../propts.cfg at %s/propts.cfg'%rep_dir )
    except:
        pass

    for flow in flows:
        try:

            if not debug: os.symlink('../%s'%flow,'%s/%s'%(rep_dir,flow))
            else: print('sym link ../%s at %s/%s'%(flow,rep_dir,flow))

        except:
            pass    

    if not debug: print('report dir and links done.')
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
            if not debug:
                new_script_file = open(new_script_path, 'w')
                new_script_file.write(new_script)
                new_script_file.close()
                os.chmod(new_script_path,0o777)

            else:
                print('Just debug not make the report script %s'% new_script_path)
        except:
            pass

        if not debug: print('report script %s has been added.'%report_name)

    else:
        print('script %s not found'%report_script)

def local_report_from_prs(**kwargs):
    # makes the required infrastructure to report desired flows,
    # on your desired local directory

    # arguments
    #-----------------------------------------#
    # configs
    branch   = kwargs.get('branch')
    suite    = kwargs.get('suite')
    # user args
    nightly     = kwargs.get('nightly') 
    flows       = kwargs.get('flows').split()
    debug = kwargs.get('debug', True)
    output_dir = kwargs.get('output_dir', os.getcwd())
    baseline = kwargs.get('baseline', None)

    #-----------------------------------------#

    # make report dir
    prs_run_dir = '%s/%s/%s/prs/run'%(branch,suite,nightly)
    rep_dir     = output_dir    
    
    
    if not debug:
        if not os.path.exists(rep_dir):
            os.mkdir(rep_dir)
        # os.symlink('%s/propts.cfg'%prs_run_dir,'%s/propts.cfg'%(rep_dir))
        shutil.copyfile('%s/propts.cfg'%prs_run_dir,'%s/propts.cfg'%(rep_dir))
    else:
            print('make this dir %s'%rep_dir)
            print('sym link %s/propts.cfg at %s/propts.cfg'%(prs_run_dir,rep_dir))
    
    for flow in flows:
        try:
            if not debug: os.symlink('%s/%s'%(prs_run_dir,flow),'%s/%s'%(rep_dir,flow))
            else: print('sym link %s/%s at %s/%s'%(prs_run_dir,flow,rep_dir,flow))

        except:
            pass    

    if not debug: print('report dir and links done.')

    report_local(flows, '', output_dir, base = baseline)

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
    debug = kwargs.get('debug', True)
    #-----------------------------------------#

    # put title in propts
    prs_run_dir = '%s/%s/%s/prs/run'%(branch,suite,nightly)
    propts = '%s/%s/%s/prs/run/propts.cfg'%(branch,suite,nightly)

    v_title  = '## virtual flow title ##\n'
    v_title += '## contains %s\n'%','.join(flows)
    v_title += 'flow.%s.title: %s\n'%(virtual_flow,virtual_title)
    v_title += '########################'
    
    try:
        if not debug:
            propts_file = open(propts, 'a+')
            propts_file.write(v_title)
            propts_file.close()
        else:
            print('add v_flow title to propts.')
    except:
        print('Couldn\'t open %s for append.'%propts)

    # make dir n links
    v_flow_dir = '%s/%s'%(prs_run_dir,virtual_flow)

    try:
        # dir for the v_flow
        if not debug: os.mkdir(v_flow_dir)
        else: print('make this dir %s'%v_flow_dir)
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
                    if not debug: os.symlink('../%s/%s'%(flow,design),'%s/%s'%(v_flow_dir,design))
                    else:  print('this link ../%s/%s at %s/%s'%(flow,design,v_flow_dir,design))
                except:
                    pass

    if not debug: print('links done')

def get_branch_by_name(branch_name):

    avail_branches ={
        'S2021.06'         : { 'p4': 'main/ls'             ,'bin': 'spf_main'},
        'R2020.09-SP'      : { 'p4': 'r2020.09_sp/dev'     ,'bin': 'spf_r2020.09_sp_dev'},
        'R2020.09'         : { 'p4': 'r2020.09/rel'        ,'bin': 'spf_r2020.09_rel'},
        'Q2019.12-SP4_rel' : { 'p4': 'q2019.12_sp4/rel'    ,'bin': 'spf_q2019.12_sp4_rel'},
        'Q2019.12-SP_apple': { 'p4': 'q2019.12_sp4_cs1/rel','bin': 'spf_q2019.12_sp4_cs1_rel'},
        'Q2019.12-SP'      : { 'p4': 'q2019.12_sp/dev'     ,'bin': 'spf_q2019.12_sp_dev'},
        'Q2019.12'         : { 'p4': 'q2019.12/rel'        ,'bin': 'spf_q2019.12_rel'},
        'P2019.03-SP'      : { 'p4': 'p2019.03_sp/dev'     ,'bin': 'spf_p2019.03_sp_dev'},
        'N2017.09_SP4_CS1' : { 'p4': 'n2017.09_sp4_cs1/rel','bin': 'spf_n2017.09_sp4_cs1_rel'},
        'R2020.09-SP5_rel' : { 'p4': 'r2020.09_sp5/rel'    ,'bin': 'spf_r2020.09_sp5_rel'},
    }

    if branch_name in avail_branches:
        return avail_branches[branch_name]
    else:
        print('branch %s is not suported.\nuse one of the following available branches:'%branch_name)
        print(' '.join(avail_branches.keys()))
        return []

def get_cl_list(branch_name, start_date, end_date): 
        
    cls_cmd     = 'p4 changes -L //synthesis/spf/%s...@%s,%s'%(get_branch_by_name(branch_name)['p4'],start_date,end_date)
    print('get cls by using:\n%s'%cls_cmd)
    p4_output   = os.popen(cls_cmd).readlines()

    cl_list = []

    for line in p4_output:
        line = line.split()

        #print(line)

        if len(line) > 2:
            
            if line[0] == 'Change':
                cl = line[1].strip()
                if cl.isnumeric(): cl_list.append(cl)

    print('there are %s cls between %s and %s'%(len(cl_list), start_date, end_date))            
    return cl_list

# returns {name: cl_bin}
def get_cl_bin_dict(branch_name, start_date, end_date):

    bins_dir = '/remote/swefs/PE/products/spf/common/btracer/backups/%s/linux64'%get_branch_by_name(branch_name)['bin']
    cl_bin_list = os.listdir(bins_dir)
    # print(cl_bin_list)

    cl_nums = get_cl_list(branch_name, start_date, end_date)
    # print(cl_nums)
    
    cl_bin_paths = {}
    avail_cl_dirs = []

    for cl_dir in cl_bin_list:
        
        cl_dir_num = cl_dir.split('_')[1]
        cl_rnd     = cl_dir.split('_')[2]
        cl_name = 'cl_%s_%s'%(cl_dir_num,cl_rnd)

        avail_cl_dirs.append(cl_dir_num)
        
        if cl_dir_num  in cl_nums:
            cl_bin_path = '%s/%s'%(bins_dir,cl_dir)
            cl_bin_paths[cl_name] = cl_bin_path
        else:
            pass
                
    #print('%s not in cl list'%cl_dir_num )
    missing_cl_dirs = []
    for cl in cl_nums:
        if cl not in avail_cl_dirs:
            missing_cl_dirs.append(cl)

    if missing_cl_dirs != []: print('Couldn\'t find below cl directories in %s:\n%s'%(bins_dir,' '.join(missing_cl_dirs)))

    return cl_bin_paths

def report_local(fl_ls, ds_ls, target_dir, base = None ):
    # makes an ugly subreport script that works most of the time
    # fl_ls = list of flows -python list- Fist element will be the baseline
    # ds_ls = list of design -python list- can be None

    fl_ls.sort() # important for culprits 
    flows  = ','.join(fl_ls)
    designs = ','.join(ds_ls)
    if not base:
        baseline = fl_ls[0]
    elif base == 'all_base':
        baseline = '%s -allbase '%fl_ls[0]
    else:
        baseline = base
    
    report_csh = '#!/bin/csh\n'
    report_csh += 'cd %s\n'%target_dir
    report_csh += 'echo "Generating PRS report"\n'
    report_csh += '/u/prsuite/prs/bin/prreport.pl '
    report_csh += '-pairwise_wns -filterwns 0.015 -filterpg_useflow -units_conversion -update ' 
    # report_csh += '-O/%s/- '%flows
    report_csh += '-rows "MeanVal Mean Min Max 95%High 95%Low StdDev SDMean NSDMean Count Histgrm" '
    report_csh += '-out report.local.out -base %s -html -success "^(Done|FM.*)" '%baseline

    report_csh += '-O/%s/%s '%(flows,designs) if ds_ls else '-O/%s/- '%flows
    report_csh += '-stack -filterpg -filtercor '
    report_csh += '-columns \'FlowLong DCMvArea ICPMvArea DCICPMvAreaE Gap DCWNS DCTNSPM DCTNSPMT DCTNSPF ICPWNS ICPTNSPM ICPTNSPMT ICPTNSPF DCICPWNSE DCICPTNSE Gap DCStdCelDynPow DCStdCelTotPow DCStdCelLeakPow DCNoClkStdCelDynPow Gap ICPStdCelDynPow ICPStdCelTotPow ICPStdCelLeakPow ICPNoClkStdCelDynPow DCGNBBLVth ICPGNBBLVth Gap DCVio ICPVio Gap DCBufInvCnt DCBufInvCntP DCSeqInst DCCombInst DCInst ICPInst Gap ICPBufInvCnt ICPBufInvCntP Gap CPUDCAllOpt*(max(CValAllFlows("CPUDCFullOpt"))>3) CPUDCFullOpt*(max(CValAllFlows("CPUDCFullOpt"))>3) CPUDCInsrtDFT*(max(CValAllFlows("CPUDCFullOpt"))>3) CPUDCIncrOpt*(max(CValAllFlows("CPUDCFullOpt"))>3) CPUDCOptnArea*(max(CValAllFlows("CPUDCFullOpt"))>3) CPUDCIncrOptP*(max(CValAllFlows("CPUDCFullOpt"))>3) Gap CLKDCAllOpt*(max(CValAllFlows("CPUDCFullOpt"))>3) CLKDCFullOpt*(max(CValAllFlows("CPUDCFullOpt"))>3) CLKDCInsrtDFT*(max(CValAllFlows("CPUDCFullOpt"))>3) CLKDCIncrOpt*(max(CValAllFlows("CPUDCFullOpt"))>3) CLKDCOptnArea*(max(CValAllFlows("CPUDCFullOpt"))>3) Gap CPUDCCngRpt CLKDCCngRpt Gap ICPCPU*(max(CValAllFlows("CPUDCFullOpt"))>3) ICPCLK*(max(CValAllFlows("CPUDCFullOpt"))>3) DCICPCPU DCMem DCMCPkMem MemDCFullOpt MemDCIncrOpt ICPMem Gap PCNBBArea PCWNS PCTNSPM PCTNSPMT PCStdCelDynPow PCStdCelTotPow PCStdCelLeakPow PCNoClkStdCelDynPow Gap DPPMvArea DPPWNS DPPTNSPM DPPTNSPMT DPPStdCelDynPow DPPStdCelTotPow DPPStdCelLeakPow DPPNoClkStdCelDynPow Gap DCAGWirLn DCAGGRC*(max(CValAllFlows("DCAGPOvGC"))>0) DCAGPOvGC*(max(CValAllFlows("DCAGPOvGC"))>0) ICPAGGRC*(max(CValAllFlows("ICPAGPOvGC"))>0) ICPAGPOvGC*(max(CValAllFlows("ICPAGPOvGC"))>0) Gap DCCPUclk-gate DCNClkGate DCNGateReg DCPGateReg DCNumReg Gap CLKplace Gap CLKplace_0 CLKplace_1 CLKplace_2 CLKplace_3 Gap CLKDCICC2Ovr Gap DPRNBBArea DPRWNS DPRTNSPM DPRTNSPMT Gap\' '  
    report_csh += '-rows \'MeanVal Mean Mean1/X Min Max 95%High 95%Low StdDev SDMean NSDMean Count Histgrm\'\n'
    #report_csh += '>&! ./LOG.prreport.local'
    
    rpt_local = open('%s/rpt_local.csh'%target_dir,'w+')
    rpt_local.write(report_csh)
    rpt_local.close()

    os.chmod('%s/rpt_local.csh'%target_dir, 0o777)

    print('report script generated at %s/rpt_local.csh'%target_dir)

def prepare_culprit(**kwargs):

    # for make_extra utility
    sys.path.append('/slowfs/dcopt105/vasquez/utils/e_run_utils')

    target_dir = kwargs.get('target_dir')
    branch     = kwargs.get('branch')
    debug      = kwargs.get('debug', True)
    start_date = kwargs.get('start_date')
    end_date   = kwargs.get('end_date')
    flow       = kwargs.get('flow')
    shell      = kwargs.get('shell', 'dcnxt_shell')
    root_path  = kwargs.get('root_path')
    repeat     = kwargs.get('repeat', 1)
    designs    = kwargs.get('designs', '')
    stages     = kwargs.get('stages', 'DC')
    target_propts = kwargs.get('target_propts')
    image_only = kwargs.get('image_only', False)
    fm_flow = kwargs.get('fm_flow', '')
    custom_bin = kwargs.get('custom_bin', None)

    new_propts = '%s/prs_propts.cfg'%target_dir

    if not debug: 
        shutil.copyfile(target_propts, new_propts)
        target_propts = new_propts


    if not image_only:
        cl_bin_dict = get_cl_bin_dict(branch,start_date,end_date)
    else:
        if not custom_bin:
            nm = root_path.split('/')[-1]
            cl_bin_dict = {}
            cl_bin_dict[nm] = root_path
        
        else:
            cl_bin_dict= {}
            cl_bin_dict['custom_bin'] = custom_bin

    fl_ls = []
    ds_ls = []

    for i in range(repeat):
              
        for cl_name,cl_bin in cl_bin_dict.items():

            suffix = '_%s_%s'%(cl_name,str(i))
            title  = cl_name
            extra  = ''
            raw    = ''
            stages = stages
            # dc_bin = '%s/snps/synopsys/bin/%s -r %s'%(cl_bin, shell, root_path) if not image_only else '%s/bin/%s'%(cl_bin,shell)
            dc_bin = cl_bin,
            icc2_bin = ''
            fm_bin = ''
            fm_flow = fm_flow
            designs = designs
            propts = target_propts
            debug = debug
            fm_extra_settings = ''

            flow_name, orig_des = make_extra(
                flow, suffix, title, extra, raw, stages, dc_bin, icc2_bin, fm_bin, fm_flow, designs, propts, debug, fm_extra_settings
            )

            fl_ls.append(flow_name)

            if designs != '':
                for d in designs.strip().split():
                    if d not in ds_ls: ds_ls.append(d) 
            else:
                for d in orig_des.strip().split():
                    if d not in ds_ls: ds_ls.append(d) 

    # make propts for Kick-off
    kick_propts  = 'INCLUDE %s\n\n'%new_propts
    kick_propts += 'flows: %s\n\n'%' '.join(sorted(fl_ls))
    kick_propts += 'designs: %s\n'%' '.join(ds_ls)

    if not debug:
        propts_kick_file = open('%s/propts.cfg'%target_dir, 'w')
        propts_kick_file.write(kick_propts)
        propts_kick_file.close()

        report_local(sorted(fl_ls), ds_ls, target_dir)

    print('###############################################################')
    print(kick_propts)
    
    # write local report

def render_cl_page(cl_list, output, name, branch, st_nightly, end_nightly):
  
  cl_dict = {}
  
  if not cl_list:
    return None

  print('Making a beautiful html to take a look at the changes of this Nightly\n%s'%output)
  for cl in cl_list:
    
    cl_num = cl.split('_')[1]
    cl_owner = cl.split('_')[2]
    cl_verb_cmd = 'rsh -l dcqor localhost "p4 describe -s %s"'%cl_num
    
    title = '%s_%s'%(cl_num,cl_owner)

    short_desc = ''

    cl_dict[title]  =  {}
    try:
      lns = os.popen(cl_verb_cmd).readlines()
      cl_dict[title]['short'] = lns[2] if len(lns) >= 3 else ''
      cl_dict[title]['long'] = os.popen(cl_verb_cmd).read().replace('\n', '<br>')
      # cl_dict[title]  =  os.popen(cl_verb_cmd).read()
    except:
      cl_dict[title]['short'] = 'Couldn\'t find any coincidence.'
      cl_dict[title]['long'] = ''
  
  template_file = '/slowfs/dcopt105/vasquez/utils/suite_collectors_dev/v_repo/suite_collectors/cl_list.jinja'
  env = Environment(loader=FileSystemLoader('/'))
  template = env.get_template(template_file)


  ordered_cls = [*cl_dict]

  print('Rendering')
  html = template.render(
        cl_dict = cl_dict,
        branch = branch,
        st_nightly = st_nightly,
        end_nightly = end_nightly,
        ordered_cls = sorted(ordered_cls)
        )

  html_name = '%s.html'%name
  try :
    report_file = open(os.path.join(output,html_name), 'w')
    report_file.write(html)
    report_file.close()
    return html_name
  except:
    return None

def culprit_by_date(**kwargs):

    # for make_extra utility
    sys.path.append('/slowfs/dcopt105/vasquez/utils/e_run_utils')

    target_dir = kwargs.get('target_dir')
    branch     = kwargs.get('branch')
    debug      = kwargs.get('debug', True)
    start_date = kwargs.get('start_date')
    end_date   = kwargs.get('end_date')
    flow       = kwargs.get('flow')
    shell      = kwargs.get('shell', 'dcnxt_shell')
    root_path  = kwargs.get('root_path')
    repeat     = kwargs.get('repeat', 1)
    designs    = kwargs.get('designs', '')
    stages     = kwargs.get('stages', 'DC')
    target_propts = kwargs.get('target_propts')
    image_only = kwargs.get('image_only', False)
    fm_flow    = kwargs.get('fm_flow', '')
    custom_bin = kwargs.get('custom_bin', None)
    icc2_bin   = kwargs.get('icc2_bin', '')
    fm_bin     = kwargs.get('fm_bin', None)
    extra      = kwargs.get('dc_extra_settings','')
    fm_extra_settings = kwargs.get('fm_extra_settings','')
    raw        = kwargs.get('dc_raw_settings','')

    new_propts = '%s/prs_propts.cfg'%target_dir

    if not debug: 
        shutil.copyfile(target_propts, new_propts)
        target_propts = new_propts


    if not image_only:
        cl_bin_dict = get_cl_bin_dict(branch,start_date,end_date)
    else:
        if not custom_bin:
            nm = root_path.split('/')[-1]
            cl_bin_dict = {}
            cl_bin_dict[nm] = root_path
        
        else:
            cl_bin_dict= {}
            cl_bin_dict['custom_bin'] = custom_bin

    # draw cl page
    if not image_only:
        cl_list_ = [*cl_bin_dict] # this sintx return kesys as a list .... weird!
        render_cl_page(cl_list_, target_dir, 'cl_list', branch, start_date, end_date)

    fl_ls = []
    ds_ls = []
    fm_fl_ls = []

    for i in range(repeat):
              
        for cl_name,cl_bin in cl_bin_dict.items():

            suffix = '_%s_%s'%(cl_name,str(i))
            title  = '<a href="http://clearcase/%s/cl_list.html#%s">%s</a>'%(target_dir,cl_name.replace('cl_',''),cl_name)
            extra  = extra
            raw    = raw
            stages = stages
            dc_bin = '%s/snps/synopsys/bin/%s -r %s'%(cl_bin, shell, root_path) if not image_only else '%s/bin/%s'%(cl_bin,shell)
            # dc_bin = cl_bin,
            icc2_bin = icc2_bin
            fm_bin = fm_bin
            fm_flow = fm_flow
            designs = designs
            propts = target_propts
            debug = debug
            fm_extra_settings = fm_extra_settings

            print(dc_bin)
            
            if 'FM' in stages:
                flow_name, fm_flow_name, orig_des = make_extra(
                    flow, suffix, title, extra, raw, stages, dc_bin, icc2_bin, fm_bin, fm_flow, designs, propts, debug, fm_extra_settings
                )
                fm_fl_ls.append(fm_flow_name)
            else:
                flow_name, orig_des = make_extra(
                    flow, suffix, title, extra, raw, stages, dc_bin, icc2_bin, fm_bin, fm_flow, designs, propts, debug, fm_extra_settings
                )

            fl_ls.append(flow_name)

            if designs != '':
                for d in designs.strip().split():
                    if d not in ds_ls: ds_ls.append(d) 
            else:
                for d in orig_des.strip().split():
                    if d not in ds_ls: ds_ls.append(d) 

    # make propts for Kick-off
    kick_propts  = 'INCLUDE %s\n\n'%new_propts
    kick_propts += '## Comment below for runtime accuracy. Only mem and CPU is the default.\n'
    kick_propts += 'INCLUDE /remote/pv/repo/dcnt/dcrt_prs_lib/gala_memusage_4c.cfg\n\n'


    if 'FM' in stages:
        kick_propts += 'tool.cmd0.csh::\n:: set rundir = %s\n\ntool.startdb.csh::\n:: set rundir = %s\n\n'%(target_dir,target_dir)
    
    #kick_propts += 'flows: %s\n\n'%' '.join(sorted(fl_ls))
    kick_propts += 'flows:\n'
    for fff in sorted(fl_ls):
        kick_propts += ':: %s\n'%fff
    kick_propts += '\n'

    if 'FM' in stages:
        kick_propts += '#flows: %s\n\n'%' '.join(sorted(fm_fl_ls))
    kick_propts += 'designs: %s\n'%' '.join(ds_ls)

    if not debug:
        propts_kick_file = open('%s/propts.cfg'%target_dir, 'w')
        propts_kick_file.write(kick_propts)
        propts_kick_file.close()

        report_local(fl_ls, ds_ls, target_dir)

    print('###############################################################')
    print(kick_propts)
    
    # write local report

def get_next_nightly(**kwargs):

    ########################################################################################### 
    # returns a tuple with the next expected nightly and their flows, like:
    # ('D20190726', ['SRM_ICC2_spg_opt_area', 'SRM_ICC2_spg_timing_opt_area', 'SRM_wlm'])
    # 
    # EXAMPLE USAGE:
    # next_nightly = get_next_nightly( 
    #     suite_path = '/remote/dcopt077/nightly_prs/p2019.03-SP/DC_ICC2',
    #     flows      = 'SRM_ICC2_spg_opt_area SRM_ICC2_spg_timing_opt_area SRM_wlm'            
    # ) 
    # #########################################################################################

    suite_path = kwargs.get('suite_path', '')
    ## deprecated
    ## flows = kwargs.get('flows', '')
    ##flows = flows.split()
    # print(flows)

    schedule_html = os.path.join(suite_path, 'nightly_flows.html')
    images_txt    = os.path.join(suite_path, 'images.txt')

    weekdays = 'Mon Tue Wed Thu Fri Sat Sun'.split()
    day = timedelta(days = 1) 

    today         = date.today()
    #just for test
    #today = date(2019,7,25)
    
    # check if today was kicked or not
    today_is_kicked = False

    if os.path.isfile(images_txt):
        last_image = open(images_txt, 'r').readlines()[-1][1:9]
        last_image_date = datetime.strptime(last_image, "%Y%m%d").date()
        #print(last_image, last_image_date)

        if today == last_image_date: today_is_kicked = True
    else:
        print('images.txt not found')

    if os.path.isfile(schedule_html):

        schedule_df = pd.read_html(schedule_html)
        schedule_df = schedule_df[0]
        # set appropiate column names
        # instead of just numbers
        schedule_df.columns = schedule_df.loc[0]
        schedule_df.drop(schedule_df.index[0], inplace = True)

        #print(schedule_df)
    else:
        print('suite_path seems not valid. It has not nightly_flows.html')
    
    # prepare a dict with our schedule
    extra_sch = {}
    for d in weekdays:
        extra_sch[d] = schedule_df[schedule_df[d]=='Xv']['Flow'].tolist()

    # check the next days

    next_flows = []
    next_date  = None
    next_nightly = None
    
    for d in weekdays[today.weekday() + today_is_kicked:]:
        ## the old way
        # for flow in flows:
        #     if flow in extra_sch[d]:
        #         next_flows.append(flow)
        
        for flow in extra_sch[d]:
            next_flows.append(flow)

        if next_flows != []:
            next_date = today + (weekdays.index(d)-today.weekday())*day
            next_nightly = 'D%s'%next_date.strftime("%Y%m%d")
            break
    
    # now check next week
    if next_flows == []:
        for d in weekdays[: today.weekday() + today_is_kicked]:
            ## the old way again
            # for flow in flows:
            #     if flow in extra_sch[d]:
            #         next_flows.append(flow)
            
            for flow in extra_sch[d]:
                next_flows.append(flow)
        
            if next_flows != []:
                next_date = today + (weekdays.index('Sun')-today.weekday() + weekdays.index(d) + 1)*day
                next_nightly = 'D%s'%next_date.strftime("%Y%m%d")
                break


    return next_nightly, next_flows

# prs utils    
def get_nightly_list(n_max, suite_path):

    img_file = os.path.join(suite_path, 'images.txt')

    n_list = []
    if os.path.isfile(img_file):
        n_list = open(img_file, 'r').read().strip().split('\n')

        return n_list[-n_max:]
    else:
        print('cant find %s'%img_file)
        return n_list

def look_flows(cache_list):

    common_flows = []
    for cache in cache_list:
        
        if os.path.isfile(cache):
            cache_txt = open(cache, 'r').readlines()

            ptrn_flow = r'^Path\s+([A-Za-z0-9_]+)/.+'


            for line in cache_txt:
                m = re.match(ptrn_flow,line)
                if m:
                    flow = m.group(1)
                    
                    if flow not in common_flows:
                        common_flows.append(flow)
        else:
            print('%s is not a file?'%cache)
    
    print(common_flows)

def report_from_cache(suite_path, nightly_list, report, flows, report_name, designs):

    cache_files    = []
    flow_prefixes  = []
    flow_name_w_prefix = []

    dirname = 'day2day_%s'%report_name

    if os.path.exists(dirname) and os.path.isdir(dirname):
        print('%s dir already exists...'%dirname)
    else:
        print('creating %s...'%dirname)
        os.mkdir(dirname, 0o777)

    for nightly in nightly_list:
        report_dir_name = 'prs_report.%s.out'%report
        cache_gz        = os.path.join(suite_path,nightly,report_dir_name,'prreport.cache.gz')

        ng_dir_cpy = os.path.join(dirname,nightly)

        if os.path.isfile(cache_gz):
            cmd_mk_ln = 'ln -s %s %s/prreport.cache.gz'%(cache_gz,ng_dir_cpy)
            cmd_unzip = 'zcat %s/prreport.cache.gz > %s/prreport.cache'%(ng_dir_cpy,ng_dir_cpy)

            if os.path.exists(ng_dir_cpy) and os.path.isdir(ng_dir_cpy):
                shutil.rmtree(ng_dir_cpy)
                print('deleting previous data for %s > %s'%(ng_dir_cpy,report))

            os.mkdir(ng_dir_cpy,0o777)
            os.system(cmd_mk_ln)
            os.system(cmd_unzip)
            print('copying n uncompresing cache for %s > %s'%(ng_dir_cpy,report))

            cache_files.append('%s/%s'%(nightly,'prreport.cache'))
            flow_prefixes.append('%s_'%nightly)
            
            for f in flows: flow_name_w_prefix.append('%s_%s'%(nightly,f))

        else:
            print('Error: Couldn\'t locate %s'%cache_gz)

    look_flows(cache_files)

    prrreport_cmd = "cd %s ;/u/prsuite/prs/bin/prreport.pl -showall -rows \"%s\" -allbase -htmlbrief -success \"^(Done|FM.*|NDBFail|PR*|PL*)\" -filterpg -stack -columns \'%s\' -rcache -cachefiles \"%s\" -flowprefixes \"%s\" -O/%s/%s"%(dirname,rows,columns,' '.join(cache_files),' '.join(flow_prefixes),','.join(flow_name_w_prefix),designs)

    print('\n')
    print(prrreport_cmd)

    try:
        os.system('set PRSUITE_HOME=/u/prsuite/prs')
        os.system(prrreport_cmd)
        # print(prreport_cmd)
    except:
        print('Error: Couldn\'t run prreport.')

def day2day_report(**kwargs):

    suite_path = kwargs.get('suite_path', '')
    n_max = kwargs.get('n_max', '10')
    report = kwargs.get('prs_report','')
    flow = kwargs.get('flow', '').split()
    report_name = kwargs.get('report_name', '')
    designs = kwargs.get('designs', '')
    columns = kwargs.get('columns', '')
    rows = kwargs.get('rows', '')
    append_baseline = kwargs.get('add_base','').split()


    nightly_list = get_nightly_list(n_max, suite_path)

    if append_baseline != '':
        for base in append_baseline:
            nightly_list.append(base)

    report_from_cache(suite_path, nightly_list, report, flow, report_name, designs)

def culprit_by_date_2(**kwargs): 

    # for make_extra utility
    sys.path.append('/slowfs/dcopt105/vasquez/utils/e_run_utils')

    target_dir = kwargs.get('target_dir')
    branch     = kwargs.get('branch')
    debug      = kwargs.get('debug', True)
    start_date = kwargs.get('start_date')
    end_date   = kwargs.get('end_date')
    flow       = kwargs.get('flow')
    shell      = kwargs.get('shell', 'dcnxt_shell')
    root_path  = kwargs.get('root_path')
    repeat     = kwargs.get('repeat', 1)
    designs    = kwargs.get('designs', '')
    stages     = kwargs.get('stages', 'DC')
    target_propts = kwargs.get('target_propts')
    image_only = kwargs.get('image_only', False)
    fm_flow    = kwargs.get('fm_flow', '')
    custom_bin = kwargs.get('custom_bin', None)
    icc2_bin   = kwargs.get('icc2_bin', '')
    fm_bin     = kwargs.get('fm_bin', None)
    extra      = kwargs.get('dc_extra_settings','')
    fm_extra_settings = kwargs.get('fm_extra_settings','')
    raw        = kwargs.get('dc_raw_settings','')

    new_propts = '%s/prs_propts.cfg'%target_dir

    if not debug: 
        shutil.copyfile(target_propts, new_propts)
        target_propts = new_propts


    if not image_only:
        cl_bin_dict = get_cl_bin_dict(branch,start_date,end_date)
    else:
        if not custom_bin:
            
            prev_bins = os.listdir('/'.join(root_path.split('/')[:-1]))
            stt_date = datetime.strptime(start_date,'%Y/%m/%d')
            ndd_date = datetime.strptime(end_date,'%Y/%m/%d')

            pp.pprint(prev_bins)
            # exit()
            cl_bin_dict = {}

            for bl in prev_bins:

                if bl[0] == 'D':
                    bl_t = bl.split('_')[0]
                    #print(bl_t)
                    bl_date = datetime.strptime(bl_t,'D%Y%m%d')
                    #print(bl_date)
                    #print(bl)
                else: 
                    continue

                print(stt_date, bl_date, ndd_date)

                if bl_date >= stt_date and bl_date <= ndd_date :
                    # print(stt_date, bl_date, ndd_date)
                    cl_bin_dict[bl] = os.path.join('/'.join(root_path.split('/')[:-1]), bl)
                    
        else:
            cl_bin_dict= {}
            cl_bin_dict['custom_bin'] = custom_bin

    pp.pprint(cl_bin_dict)

    fl_ls = []
    ds_ls = []
    fm_fl_ls = []

    for i in range(repeat):
              
        for cl_name,cl_bin in cl_bin_dict.items():

            suffix = '_%s_%s'%(cl_name,str(i))
            title  = cl_name
            extra  = extra
            raw    = raw
            stages = stages
            dc_bin = '%s/snps/synopsys/bin/%s -r %s'%(cl_bin, shell, root_path) if not image_only else '%s/bin/%s'%(cl_bin,shell)
            # dc_bin = cl_bin,
            icc2_bin = icc2_bin
            fm_bin = fm_bin
            fm_flow = fm_flow
            designs = designs
            propts = target_propts
            debug = debug
            fm_extra_settings = fm_extra_settings

            print(dc_bin)
            
            if 'FM' in stages:
                flow_name, fm_flow_name, orig_des = make_extra(
                    flow, suffix, title, extra, raw, stages, dc_bin, icc2_bin, fm_bin, fm_flow, designs, propts, debug, fm_extra_settings
                )
                fm_fl_ls.append(fm_flow_name)
            else:
                flow_name, orig_des = make_extra(
                    flow, suffix, title, extra, raw, stages, dc_bin, icc2_bin, fm_bin, fm_flow, designs, propts, debug, fm_extra_settings
                )

            fl_ls.append(flow_name)
            print(flow_name)

            if designs != '':
                for d in designs.strip().split():
                    if d not in ds_ls: ds_ls.append(d) 
            else:
                for d in orig_des.strip().split():
                    if d not in ds_ls: ds_ls.append(d) 

    # make propts for Kick-off
    kick_propts  = 'INCLUDE %s\n\n'%new_propts
    if 'FM' in stages:
        kick_propts += 'tool.cmd0.csh::\n:: set rundir = %s\n\ntool.startdb.csh::\n:: set rundir = %s\n\n'%(target_dir,target_dir)
    kick_propts += 'flows: %s\n\n'%' '.join(sorted(fl_ls))
    if 'FM' in stages:
        kick_propts += '#flows: %s\n\n'%' '.join(sorted(fm_fl_ls))
    kick_propts += 'designs: %s\n'%' '.join(ds_ls)

    if not debug:
        propts_kick_file = open('%s/propts.cfg'%target_dir, 'w')
        propts_kick_file.write(kick_propts)
        propts_kick_file.close()

        report_local(fl_ls, ds_ls, target_dir)

    print('###############################################################')
    print(kick_propts)

def get_cl_html(**kwargs):

    # for make_extra utility
    sys.path.append('/slowfs/dcopt105/vasquez/utils/e_run_utils')

    target_dir = kwargs.get('target_dir')
    branch     = kwargs.get('branch')
    start_date = kwargs.get('start_date')
    end_date   = kwargs.get('end_date')
    
    cl_bin_dict = get_cl_bin_dict(branch,start_date,end_date)
    
    # draw cl page
    cl_list_ = [*cl_bin_dict] # this sintx return kesys as a list .... weird!
    render_cl_page(cl_list_, target_dir, 'cl_list', branch, start_date, end_date)

def get_cl_description(cl_num):

    cl_verb_cmd = 'rsh -l dcqor localhost "p4 describe -s %s"'%cl_num
    cl_verb_cmd = 'p4 describe -s %s'%cl_num

    description = None
    owner       = None
    try:
      description = os.popen(cl_verb_cmd).read()
      owner       = description.split('\n')[0].split()[3].split('@')[0]
    except:
      pass

    return owner, description

def sign_off_run(**kwargs):
  
  execs = kwargs.get('execs', None)
  baseline = kwargs.get('baseline', None)
  target = kwargs.get('target', None)
  flows = kwargs.get('flows', None).split()
  designs = kwargs.get('designs', '')
  base_propts = kwargs.get('base_propts', None)
  base_report = kwargs.get('base_report', None)
  target_metrics = kwargs.get('target_metrics', None)
  target_dir = kwargs.get('target_dir', None)
  debug = kwargs.get('debug',True)
  hs_user = kwargs.get('hs_user', 'vasquez')
  rt_config = kwargs.get('rt_config','BATCH_CPU')
  title = kwargs.get('title', None)

  dir_name = title if title else target
  soff_dir = os.path.join(target_dir, dir_name)
  if not os.path.exists(soff_dir):
      os.mkdir(soff_dir)

  # copying base propts
  new_propts = os.path.join(soff_dir,'prs_propts.cfg')
  shutil.copyfile(base_propts, new_propts)
  

  # adding the flows with the config
  id = 0
  n_flows = []
  for bin in execs:
    for flow in flows:
      # make_extra(flow, suffix, title, dc_extra_settings, raw_extra_settings, stages, dc_bin, icc2_bin, fm_bin, fm_flow, designs, propts, debug, fm_extra_settings)
      new_flow, orig_des = make_extra(
          flow, 
          '_so%s'%str(id),
          bin,
          '',
          '',
          'DC ICC2',
          execs[bin],
          '',
          '',
          '',
          designs,
          new_propts,
          debug,
          ''
      )
      n_flows.append(new_flow)
      id += 1

      if not designs:
        designs = orig_des

  # Make wrapper propts for Kick-off
  kick_propts = '# Base propts taken from %s\n' % base_propts
  kick_propts += 'INCLUDE %s\n' % new_propts

  kick_propts += 'DEFINE %s\n' % rt_config
  kick_propts += 'INCLUDE /remote/pv/repo/pvutil/dcprs/suite/hw_cfg/machine/propts.gala.farm_selection.cfg\n\n'


  kick_propts += 'flows:\n'
  for fl in n_flows:
    kick_propts += ':: %s\n' % fl
  kick_propts += '\ndesigns: %s' % designs

  if not debug:
    propts_kick_file = open('%s/propts.cfg'%soff_dir, 'w')
    propts_kick_file.write(kick_propts)
    propts_kick_file.close()

  if not debug:
    # kick-off the run
    launcher_script = '/remote/dtdata1/testdata/prs/syn/scripts/nightly/run_scripts/run_prs_gala-icc2.csh'
    os.system('rsh -l %s localhost "cd %s; %s"' % (hs_user, soff_dir, launcher_script))

  # make report
  report_local(n_flows, designs.split(), soff_dir)
  
  # make summary script
  #...
