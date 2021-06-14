import gzip, re, copy, pprint
from dictdiffer import diff, patch, swap, revert

pp=pprint.PrettyPrinter(indent=3)

# des_ = 'f4_brw_cisco'
# log_file_1 = '/slowfs/dcopt036/nightly_prs/q2019.12_ls/DC_ICC2/D20191125_18_01/prs/run/SRM_spg_timing_opt_area_trace_multi/%s/%s.dcopt.out.gz'%(des_,des_)
# log_file_2 = '/slowfs/dcopt036/nightly_prs/q2019.12_ls/DC_ICC2/D20191125_18_01/prs/run/SRM_spg_timing_opt_area_trace_multi_mirror/%s/%s.dcopt.out.gz'%(des_,des_)

design = 'dcp780_cbs_pollux_tx_dig'
log_file_1 = '/remote/dcopt077/nightly_prs/p2019.03-SP/DC_ICC2/D20191216_14_30/prs/run/SRM_spg_timing_opt_area_trace_single_mirror/%s/%s.dcopt.out.gz'%(design,design)
log_file_2 = '/remote/dcopt077/nightly_prs/p2019.03-SP/DC_ICC2/D20191216_14_30/prs/run/SRM_spg_timing_opt_area_trace_single/%s/%s.dcopt.out.gz'%(design,design)



def log_to_str(log_file):

    # takes some logfile and covert it to string
    # doesnt matter if compressed or not.

    log_str = ''

    if log_file.strip().split('.')[-1] == 'gz':
        # it's compresed
        print('')
        try: log_str = gzip.open(log_file).read().decode(encoding='utf-8', errors ='ignore')
        except: print('Couldn\'t open logfile %s'%log_file)
    else:
        try: log_str = open(log_file).read()
        except: print('Couldn\'t open logfile %s'%log_file)

    return log_str

def get_action_dep_rpts(str_log):
    
    action_deps    = []
    step_index     = 0
    step_level_chk = 0
    step_stack_chk = []

    step_level_qor = 0
    step_stack_qor = []

    if str_log == '': return trace_stats

    log_lines = str_log.splitlines()
    
    # flag to spot if we are inside the report
    on_action_dep = False
    current_step     = ''
    current_des      = ''
    current_action   = ''                    
    
    report_type = {
        'qor'     : 'OPTO_STEP_ACTION_TRACE_STATS',
        'checksum': 'OPTO_STEP_ACTION_REPORT_CHECKSUM',
        'dcxref'  : 'OPTO_STEP_ACTION_REPORT_DCXREF',
    }

    level_counter = {
        'qor'     : 0,
        'checksum': 0,
        'dcxref'  : 0,
    }

    step_stack = {
        'qor'      : [],
        'checksum' : [],
        'dcxref'   : [],
    }
    # regex to spot start and end of action deployment reports
    # step - design - action
    ptrn_action_dep_open  = r'^ACTION\sDEPLOYMENT\sv{4}\s\*{3}\s([a-zA-Z0-9\s\-_]+)\*{3}\s[0-9\:]+\s\*{3}\sdesign\:\s(\w+),\saction\:\s([A-Z_]+)'
    ptrn_action_dep_close = r'^ACTION\sDEPLOYMENT\s\^{4}\s\*{3}\s([a-zA-Z0-9\s\-_]+)\*{3}'
    # regex to spot checksum
    ptrn_checksum         = r'^Design\sCheckSum\s([A-Za-z0-9_\-]+)\s\:\s([0-9\:]+)\s\s.+'


    for i in range(len(log_lines)):

        line = log_lines[i]
        line_num  = i + 1
        
        if not on_action_dep:
            
            m_act_dep_start = re.match(ptrn_action_dep_open,line)
            if m_act_dep_start:
                on_action_dep  = True
                
                current_step   = m_act_dep_start.group(1).strip()
                current_des    = m_act_dep_start.group(2).strip()
                current_action = m_act_dep_start.group(3).strip()
                
                rpt_type = ''
                for k,v in report_type.items(): 
                    if v == current_action: rpt_type = k

                step_part = current_step.split()[1] if len(current_step.split()) == 2 else ''

                # raise counter and push on Stack
                if    step_part == 'begin': 
                    level_counter[rpt_type] += 1 if rpt_type in level_counter else 0
                    
                    if rpt_type in step_stack: 
                        step_stack[rpt_type].append(current_step.replace(' begin',''))


                action_deps.append({
                    'line'   : line_num,
                    'step'   : current_step,
                    'design' : current_des,
                    'action' : current_action,
                    'step_level': level_counter[rpt_type],
                    'step_stack'  : ' > '.join(step_stack[rpt_type])
                })

                # down counter on exit
                if  step_part == 'end': 
                    level_counter[rpt_type] -= 1 if rpt_type in level_counter else 0
                    
                    if rpt_type in step_stack: 
                            step_stack[rpt_type].pop()


                step_index = len(action_deps) - 1

        else:
            
            # detects end of action_deployment report
            m_act_dep_close = re.match(ptrn_action_dep_close,line)
            if m_act_dep_close:
                on_action_dep = False 
                current_step     = ''
                current_des      = ''
                current_action   = ''         
            
            # qor report case
            elif current_action == report_type['qor']:    

                is_key = True       
                last_key = ''
                
                if 'qor' not in action_deps[step_index]: action_deps[step_index]['qor'] = {}

                # traverse each line as key/value pair
                for w in line.strip().split():
                    if is_key:
                        action_deps[step_index]['qor'][w] = {}
                        last_key = w
                        is_key = not is_key

                    else:
                        action_deps[step_index]['qor'][last_key] = float(w) if w.isnumeric() else w
                        is_key = not is_key

            # checksum report case
            elif current_action == report_type['checksum']:

                # this it's supposed to always happen
                m_checksum = re.match(ptrn_checksum, line)
                if m_checksum:
                    action_deps[step_index]['checksum'] = m_checksum.group(2)
                
            else:
                pass

    return action_deps

#pp.pprint(get_action_dep_rpts(log_to_str(log_file_1))[:10])


str= '''
[{  'action': 'OPTO_STEP_ACTION_REPORT_CHECKSUM',
    'checksum': '1121708103:1876323992:687158460:2371672270:1839456305:2957159936:0:0:0:0',
    'design': 'f4_brw',
    'line': 9388,
    'step': 'simp-in-pass1-1 begin '},
{  'action': 'OPTO_STEP_ACTION_TRACE_STATS',
    'design': 'f4_brw'
    'line': 9392,
    'qor': { 'area': '178744.52356',
            'buf-inv': '71643',
            'drc': '2499700.00000',
            'leak-pwr': '0.00000',
            'tns': '0.00000',
            'trace-stats-cpu': '0.185972',
            'tvi-current-scenario': 'default',
            'wns': '0.00000'},
    'step': 'simp-in-pass1-1 end '}]
'''

def get_rpts_diff(log1, log2, tol):
    # gather action deployment report lists
    rpt_1 = get_action_dep_rpts(log_to_str(log1))
    rpt_2 = get_action_dep_rpts(log_to_str(log2))

    # compute max iterable lenght
    mx1 = len(rpt_1) > len(rpt_2)
    max_len = (not mx1)*len(rpt_1) + mx1*len(rpt_2)

    # compute differences
    change = None

    for i in range(max_len):

        change = diff(rpt_1[i], rpt_2[i], tolerance = tol)

        ## here i can find several types of difference,
        ## when difference in step_stack, I need to start a convergence lookup,
        ## which eventually will happens at the close of the upper level step.
        print('index: %d'%i)
        pp.pprint(list(change))
        
get_rpts_diff(log_file_1, log_file_2, 0.1)