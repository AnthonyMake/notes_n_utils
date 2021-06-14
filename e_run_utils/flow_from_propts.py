import os , re

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

# flow_def = get_flow_def(propts = propts_file, target_flow = 'SRM_ICC2_spg_opt_area_ex1')

def append_to_propts(propts, extra_def):

    propts_file = open(propts,'a+')

    propts_file.write('\n### extra run flows definition ###')
    propts_file.write(extra_def)

    print('extra def appended to %s'%propts)



def make_extra(**kwargs):
    #shared
    flow   = kwargs.get('flow')
    #extra
    suffix = kwargs.get('suffix')
    title  = kwargs.get('title')
    designs = kwargs.get('designs', '')
    dc_extra_settings = kwargs.get('dc_extra_settings', '')
    raw_extra_settings      = kwargs.get('raw_extra_settings', '')
    
    stages   = kwargs.get('stages', 'DC')
    
    dc_bin   = kwargs.get('dc_bin', '')
    icc2_bin = kwargs.get('icc2_bin', '')
    fm_bin   = kwargs.get('fm_bin', '')
    
    #regular
    fm_flow = kwargs.get('fm_flow', '')
    propts  = kwargs.get('propts')
    
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
    else:
        pass
    
    # bins 
    if dc_bin != '':
        # extra_def += 'flow.%s::\n'%extra_name
        extra_def += ':: tool.rtlopt.bin: %s\n'%dc_bin
        extra_def += ':: tool.dcopt.bin: %s\n'%dc_bin
        extra_def += ':: tool.dcrpt.bin: %s\n'%dc_bin

    if icc2_bin != '':
        # extra_def += 'flow.%s::\n'%extra_name
        extra_def += ':: tool.nw2nlib.bin: %s\n'%icc2_bin
        extra_def += ':: tool.nwpopt.bin: %s\n'%icc2_bin
        extra_def += ':: tool.nwprpt.bin: %s\n'%icc2_bin

    # extra settings    
    if dc_extra_settings != '':
        # extra_def += 'flow.%s::\n'%extra_name
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
        print(fm_extra_flow_def)

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
            

        

    print(extra_def)

    # append to the original propts
    append_to_propts(propts, extra_def)
    
    return extra_def

make_extra(
    propts   = 'propts.cfg' ,
    flow     = 'SRM_ICC2_spg_timing_opt_area',
    suffix   = '_ex_A',
    title    = 'my super fancy flow',
    dc_extra_settings = 'set_some_fancy_setting TRUE',
    stages   = 'DC FM',
    dc_bin   = '/some/fancy/dc_bin -r /and/some/fancy/root/path',
    fm_flow  = 'SRMFm_ICC2_spg_timing_opt_area',
    designs  = 'd1 d2'
)


