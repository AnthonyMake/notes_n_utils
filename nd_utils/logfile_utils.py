import gzip, re, copy, pprint
from dictdiffer import diff, patch, swap, revert

pp=pprint.PrettyPrinter(indent=3)

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

def log_complete():
    pass   

def get_action_dep_rpts(str_log, fltr = None):
    
    action_deps    = []
    step_index     = 0
    step_level_chk = 0
    step_stack_chk = []

    step_level_qor = 0
    step_stack_qor = []

    if str_log == '': return ''

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
    ptrn_action_dep_open  = r'^ACTION\sDEPLOYMENT\sv{4}\s\*{3}\s([\w\s-]+)\*{3}\s[0-9\:]+\s\*{3}\sdesign\:\s([\w\s-]+),\saction\:\s([A-Z_]+)'
    ptrn_action_dep_close = r'^ACTION\sDEPLOYMENT\s\^{4}\s\*{3}\s([\w\s-]+)\*{3}'
    # regex to spot checksum
    ptrn_checksum         = r'^Design\sCheckSum\s([\w\s-]+)\s\:\s([0-9\:]+)\s\s.+'

    matches_0 = []
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
                if step_part == 'begin' and rpt_type != 'dcxref': 
                    if rpt_type in level_counter:
                        level_counter[rpt_type] += 1   
                    else:
                        print('skipping lv countel')

                    if rpt_type in step_stack:
                        if current_action == report_type['qor']:
                            matches_0.append((line_num,line))
                            step_stack[rpt_type].append(current_step.replace(' begin',''))
                            # print(step_stack)
                            # if level_counter[rpt_type] == 1 and len(step_stack[rpt_type]) > 1 :
                                
                            #     print(step_stack[rpt_type])
                            #     print('\nlatest log lines:')
                            #     print('\n'.join(log_lines[i-8:i]))
                                
                            #     print('\nLatest Matches:')
                            #     for tp in matches_0[-8:]:
                            #         print(tp)
                            #     #print('\n'.join(matches_0[-8:]))
                            #     # something is happening 
                            #     # btwn 883911  and
                            #     exit()

                action_deps.append({
                    'line'   : line_num,
                    'step'   : current_step,
                    'design' : current_des,
                    'action' : current_action,
                    'step_level': level_counter[rpt_type],
                    'step_stack'  : ' > '.join(step_stack[rpt_type])
                })

                # down counter on exit
                if  step_part == 'end' and rpt_type != 'dcxref': 

                    # print(line, step_stack[rpt_type])
                    level_counter[rpt_type] -= 1 if rpt_type in level_counter else 0
                    
                    if rpt_type in step_stack:
                        #step_stack[rpt_type].pop()

                        try:
                            step_stack[rpt_type].pop()
                        except:
                            
                            latest = action_deps[-8:]
                            # for rp in latest:
                            #     if rp['action'] == report_type[rpt_type]:
                            #         print(rp['step'])
                            #         print(rp['step_stack'])

                            # print(line_num, line, current_step, rpt_type)
                            # print(step_stack)
                            # print('\n')

                step_index = len(action_deps) - 1

        else:
            # detects end of action_deployment report
            m_act_dep_close = re.match(ptrn_action_dep_close,line)
            if m_act_dep_close:
                on_action_dep  = False 
                current_step   = ''
                current_des    = ''
                current_action = ''         
            
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
                        m = re.match(r'[0-9\.\+\-]+',w.strip())
                        if m:
                            action_deps[step_index]['qor'][last_key] = float(w)
                        else:
                            action_deps[step_index]['qor'][last_key] = w
                        
                        is_key = not is_key
                        

            # checksum report case
            elif current_action == report_type['checksum']:

                # this it's supposed to always happen
                m_checksum = re.match(ptrn_checksum, line)
                if m_checksum:
                    action_deps[step_index]['checksum'] = m_checksum.group(2)
                
            else:
                pass

    ## enable some filtering for some peers request
    if fltr == None:
        return action_deps
    else:
        rpts = []
        if fltr not in report_type:
            print('%s type reports are not supported.'%fltr)
            return rpts
        else:
            for rp in action_deps:
                if rp['action'] == report_type[fltr]:        
                    rpts.append(rp)
                    
            return rpts

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

def get_rpts_diff(log1, log2, tol, fltr=None):
    # gather action deployment report lists
    
    rpt_1 = get_action_dep_rpts(log_to_str(log1),fltr)
    rpt_2 = get_action_dep_rpts(log_to_str(log2),fltr)

    # compute max iterable lenght
    mx1 = len(rpt_1) > len(rpt_2)
    max_len = (not mx1)*len(rpt_1) + mx1*len(rpt_2)

    full_diff = []
    # compute differences
    change = None

    for i in range(max_len):

        change = diff(rpt_1[i], rpt_2[i], tolerance = tol)

        ## here i can find several types of difference,
        ## when difference in step_stack, I need to start a convergence lookup,
        ## which eventually will happens at the close of the upper level step.
        
        # print('index: %d'%i)
        full_diff.append(list(change))
    
    return full_diff

############################################
# bootsrap icons
pass_icon = '''
<svg class="bi bi-check-all text-success" width="1em" height="1em" viewBox="0 0 16 16" fill="currentColor" xmlns="http://www.w3.org/2000/svg">
  <path fill-rule="evenodd" d="M12.354 3.646a.5.5 0 010 .708l-7 7a.5.5 0 01-.708 0l-3.5-3.5a.5.5 0 11.708-.708L5 10.293l6.646-6.647a.5.5 0 01.708 0z" clip-rule="evenodd"/>
  <path d="M6.25 8.043l-.896-.897a.5.5 0 10-.708.708l.897.896.707-.707zm1 2.414l.896.897a.5.5 0 00.708 0l7-7a.5.5 0 00-.708-.708L8.5 10.293l-.543-.543-.707.707z"/>
</svg>
'''

warning_icon = '''
<svg class="bi bi-exclamation-triangle text-warning" width="1em" height="1em" viewBox="0 0 16 16" fill="currentColor" xmlns="http://www.w3.org/2000/svg">
  <path fill-rule="evenodd" d="M7.938 2.016a.146.146 0 00-.054.057L1.027 13.74a.176.176 0 00-.002.183c.016.03.037.05.054.06.015.01.034.017.066.017h13.713a.12.12 0 00.066-.017.163.163 0 00.055-.06.176.176 0 00-.003-.183L8.12 2.073a.146.146 0 00-.054-.057A.13.13 0 008.002 2a.13.13 0 00-.064.016zm1.044-.45a1.13 1.13 0 00-1.96 0L.165 13.233c-.457.778.091 1.767.98 1.767h13.713c.889 0 1.438-.99.98-1.767L8.982 1.566z" clip-rule="evenodd"/>
  <path d="M7.002 12a1 1 0 112 0 1 1 0 01-2 0zM7.1 5.995a.905.905 0 111.8 0l-.35 3.507a.552.552 0 01-1.1 0L7.1 5.995z"/>
</svg>
'''

issue_icon = '''
<svg class="bi bi-x-circle-fill text-danger" width="1em" height="1em" viewBox="0 0 16 16" fill="currentColor" xmlns="http://www.w3.org/2000/svg">
  <path fill-rule="evenodd" d="M16 8A8 8 0 110 8a8 8 0 0116 0zm-4.146-3.146a.5.5 0 00-.708-.708L8 7.293 4.854 4.146a.5.5 0 10-.708.708L7.293 8l-3.147 3.146a.5.5 0 00.708.708L8 8.707l3.146 3.147a.5.5 0 00.708-.708L8.707 8l3.147-3.146z" clip-rule="evenodd"/>
</svg>
'''

done_icon = '''
<svg class="bi bi-check text-success" width="1em" height="1em" viewBox="0 0 16 16" fill="currentColor" xmlns="http://www.w3.org/2000/svg">
  <path fill-rule="evenodd" d="M13.854 3.646a.5.5 0 010 .708l-7 7a.5.5 0 01-.708 0l-3.5-3.5a.5.5 0 11.708-.708L6.5 10.293l6.646-6.647a.5.5 0 01.708 0z" clip-rule="evenodd"/>
</svg>
'''

fail_icon = '''
<svg class="bi bi-x text-danger" width="1em" height="1em" viewBox="0 0 16 16" fill="currentColor" xmlns="http://www.w3.org/2000/svg">
  <path fill-rule="evenodd" d="M11.854 4.146a.5.5 0 010 .708l-7 7a.5.5 0 01-.708-.708l7-7a.5.5 0 01.708 0z" clip-rule="evenodd"/>
  <path fill-rule="evenodd" d="M4.146 4.146a.5.5 0 000 .708l7 7a.5.5 0 00.708-.708l-7-7a.5.5 0 00-.708 0z" clip-rule="evenodd"/>
</svg>
'''

info_icon = '''
<svg class="bi bi-info-circle-fill text-secondary" width="1em" height="1em" viewBox="0 0 16 16" fill="currentColor" xmlns="http://www.w3.org/2000/svg">
  <path fill-rule="evenodd" d="M8 16A8 8 0 108 0a8 8 0 000 16zm.93-9.412l-2.29.287-.082.38.45.083c.294.07.352.176.288.469l-.738 3.468c-.194.897.105 1.319.808 1.319.545 0 1.178-.252 1.465-.598l.088-.416c-.2.176-.492.246-.686.246-.275 0-.375-.193-.304-.533L8.93 6.588zM8 5.5a1 1 0 100-2 1 1 0 000 2z" clip-rule="evenodd"/>
</svg>
'''

pending_icon= '''
<svg class="bi bi-stopwatch text-warning" width="1em" height="1em" viewBox="0 0 16 16" fill="currentColor" xmlns="http://www.w3.org/2000/svg">
  <path fill-rule="evenodd" d="M8 15A6 6 0 108 3a6 6 0 000 12zm0 1A7 7 0 108 2a7 7 0 000 14z" clip-rule="evenodd"/>
  <path fill-rule="evenodd" d="M8 4.5a.5.5 0 01.5.5v4a.5.5 0 01-.5.5H4.5a.5.5 0 010-1h3V5a.5.5 0 01.5-.5zM5.5.5A.5.5 0 016 0h4a.5.5 0 010 1H6a.5.5 0 01-.5-.5z" clip-rule="evenodd"/>
  <path d="M7 1h2v2H7V1z"/>
</svg>
'''



