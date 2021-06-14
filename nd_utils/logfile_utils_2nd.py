import gzip, re, copy, pprint
from dictdiffer import diff, patch, swap, revert
import pandas as pd
import os, gzip, re, copy, pprint
import pickle as pkl
from dictdiffer import diff, patch, swap, revert
import pandas as pd
from bs_icons import *
from jinja2 import Template


pp=pprint.PrettyPrinter(indent=1,depth = 6)

def log_to_str(log_file):

    # takes some logfile and covert it to string
    # doesnt matter if compressed or not.

    log_str = ''

    if log_file.strip().split('.')[-1] == 'gz':
        # it's compresed
        #print('')
        try: log_str = gzip.open(log_file).read().decode(encoding='utf-8', errors ='ignore')
        except: print('Couldn\'t open logfile %s'%log_file)
    else:
        try: log_str = open(log_file).read()
        except: print('Couldn\'t open logfile %s'%log_file)

    return log_str

def log_complete():
    pass   

def get_action_dep_rpts(str_log, tp):
    action_deps    = []
    step_index     = 0

    if str_log == '': return ''

    log_lines = str_log.splitlines()
    
    # flag to spot if we are inside the report
    on_action_dep = False
    current_step     = ''
    step_name        = ''
    current_des      = ''
    current_action   = ''                    
    
    print('-parsing action deployment reports for %s'%tp)

    report_type = {
        'qor'     : 'OPTO_STEP_ACTION_TRACE_STATS',
        'checksum': 'OPTO_STEP_ACTION_REPORT_CHECKSUM',
    }

    if tp not in report_type:
        print('%s report type, is not supported, does it really exists?'%tp)
        return ''

    level_counter = 0
    step_stack    = []

    dbg = []
    
    for i in range(len(log_lines)):

        line = log_lines[i]
        line_num  = i + 1
        
        if not on_action_dep:
            # pattern to look action deployment report oppenning,
            ptrn  = r'^\s*ACTION\sDEPLOYMENT\sv{4}\s\*{3}\s([\w\s-]+)\*{3}\s[0-9\:]+\s\*{3}\sdesign\:\s([\w\s-]+),\saction\:\s%s'%report_type[tp]
            m_act_dep_start = re.match(ptrn,line)
            
            if m_act_dep_start:
                on_action_dep  = True
            
                current_step   = m_act_dep_start.group(1).strip()
                current_des    = m_act_dep_start.group(2).strip()

                if len(current_step.split()) == 2:
                
                    step_part = current_step.split()[1]
                    step_name = current_step.split()[0]                    
                
                else:
                    print('Step name: %s \n it\'s a little bit weird. Aborting...')
                    return ''

                # raise counter and push on Stack
                if step_part == 'begin': 
                    level_counter += 1
                    step_stack.append(current_step)

                elif step_part == 'end':
                    if step_stack[-1] == current_step.replace('end','begin'):
                                step_stack.pop()
                                # level_counter -= 1
                                step_stack.append(current_step)
                    #else: 
                    #    print('missing begin for <<%s>>, line: %s'%(current_step,line_num))
                    #    step_stack.append(current_step)

                        # # pp.pprint(action_deps[-20:])
                        # for st in action_deps[-20:]:
                        #     print(st['step'], st['step_stack'])
                        # print('\n\n')
                        # print(step_stack, current_step)
                        # exit()


                action_deps.append({
                    'line'       : line_num,
                    'step'       : current_step,
                    'design'     : current_des,
                    'action'     : current_action,
                    'step_level' : level_counter,
                    #'step_stack' : ' > '.join(step_stack),
                    'step_stack' : copy.deepcopy(step_stack)
                })

                step_index = len(action_deps) - 1

                # down counter on exit and pop from stack

                    
                    # else:
                    #     print("Correcting, it should close <<%s>> but it's closing <<%s>>>"%(step_stack[-1],current_step))
                    #     level_counter -= 1
                    #     step_stack.pop()



                dbg.append((line_num, ' > '.join(step_stack)))
                #print(dbg[-1])
                # #97692 
                # if len(dbg) >= bacon:
                #     for d in dbg[-30:]: 
                #         print(d)
                    
                #     input('')
                #     bacon += 30

                
                if  step_part == 'end':
                    step_stack.pop()
                    level_counter -= 1
                    #input('')
                    
        else:
            # detects end of action_deployment report
            ptrn = '^\s*ACTION\sDEPLOYMENT\s\^{4}\s\*{3}\s%s\s\*{3}'%current_step
            
            m_act_dep_close = re.match(ptrn,line)
            
            if m_act_dep_close:
                on_action_dep  = False          
            else: 
                if tp == 'qor':    

                    is_key = True       
                    last_key = ''
                    
                    if 'qor' not in action_deps[step_index]: 
                        action_deps[step_index]['qor'] = {}

                    # traverse each line as key/value pair
                    for w in line.strip().split():

                        # lets toggle a value to switch between key and value
                        if is_key:
                            action_deps[step_index]['qor'][w] = {}
                            last_key = w
                            is_key = not is_key

                        else:
                            m = re.match(r'[0-9\.\+\-]+$',w.strip())
                            if m:
                                action_deps[step_index]['qor'][last_key] = float(w)
                            else:
                                action_deps[step_index]['qor'][last_key] = w
                            
                            # toggle the key thing
                            is_key = not is_key
                            

                # checksum report case
                elif tp == 'checksum':
                    # this it's supposed to always happen
                    ptrn = r'^Design\sCheckSum\s([\w\s-]+)\s\:\s([0-9\:]+)\s\s.+'
                    m_checksum = re.match(ptrn, line)
                    
                    if m_checksum:
                        action_deps[step_index]['checksum'] = m_checksum.group(2)
                    
                else:
                    # no thoughts for this
                    print('this is not expected.')
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

def nd_check(log1, log2, tol, fltr):
    # gather action deployment report lists
    # log1 and log2 must be action dep rpt lists

    excepts_ls = 'line'

    rpt_1 = log1
    rpt_2 = log2
    real = 'No'

    last_base = rpt_1[-1]
    last_flow = rpt_2[-1]

    if last_base['step_level'] > 1 : return 'base_incomp'
    if last_flow['step_level'] > 1 : return 'test_incomp'

    last_diff = diff(rpt_1[-1], rpt_2[-1])
    
    l_diff = list(last_diff)

    if l_diff != []:
        for change in l_diff:
            if change[0] == 'change' and change[1] not in excepts_ls:
                real = 'Yes'
    return real

def nd_log_check(log1, log2, tol, fltr):
    # log1 and log2 must be action dep rpt lists

    rpt_1 = log1
    rpt_2 = log2

    last_base = rpt_1[-1]
    last_flow = rpt_2[-1]

    result = ''
    
    if last_base['step_level'] > 1 : result = 'baseline logfile is incomplete'
    if last_flow['step_level'] > 1 : result = 'flow logfile is incomplete'

    return result

def non_rep_analysis(rpt_base, rpt_flow, tol, tp):
    
    # computing a lind of divergence map,
    # it returns a patched list of tupples with 
    #  base_info, flow_info and diff in between when applies
    # pp.pprint(rpt_base[-1])
    # exit()

    result = []
    log_offset = 0

    for i in range(len(rpt_base)):
        
        if rpt_base[i]['step_stack'] == rpt_flow[i + log_offset]['step_stack']:
            base_data = rpt_base[i]
            flow_data = rpt_flow[i + log_offset]
            diff_data = list(diff(base_data, flow_data))
            result.append((base_data, flow_data, diff_data))

        else:
            found_it = False
            partial = []

            for j in range(i + log_offset, len(rpt_flow)):
                if rpt_base[i]['step_stack'] == rpt_flow[j]['step_stack']:
                    result = result + partial
                    
                    base_data = rpt_base[i]
                    flow_data = rpt_flow[j]
                    diff_data = list(diff(base_data, flow_data))
                    
                    result.append((base_data, flow_data, diff_data))
                    
                    found_it = True
                    log_offset = j - i 
                    
                    break
                
                else:
                    partial.append((None,rpt_flow[j],[]))
                    
            # catch the end of the list without find nothing
            if not found_it:
                log_offset = log_offset - 1
                result.append((rpt_base[i],None, []))

            else:
                pass
            
    # pp.pprint(result)
    # print('-reporting')
    # non_rep_report(result, tp)
    
    return result

def non_rep_report2(non_rep_result):

    result = []

    on_step_diff = False
    on_nd_diff   = False

    for i in range(len(non_rep_result)):
        tup = non_rep_result[i]
        base_data = tup[0]
        flow_data = tup[1]
        diff_data = tup[2]

        # no step diff - go check diffs
        if base_data != None and flow_data != None:
            if base_data['step_level'] == 1:
                result.append(tup)

            if not on_nd_diff:
                # has any difference?
                for chng in diff_data: 
                    if chng[0] == 'change' and chng[1] != 'line':
                        on_nd_diff = True
                        break
                
                if on_nd_diff:                    
                    result.append(non_rep_result[i-1])
                    result.append(tup)

            else:
                # is diff over??
                if len(diff_data) == 1 and diff_data[1] == 'line':
                    on_nd_diff = False
                    result.append(tup)
                else:
                    if result[-1] != '...':
                        result.append('...')
        
        else:
            if base_data == None and flow_data != None:
                if not on_step_diff:
                    result.append(non_rep_result[i-1])
                    result.append(tup)                
                    on_step_diff = True
                else:
                    if result[-1] != '...':
                        result.append('...')


    pp.pprint(result)

def non_rep_report_old(non_rep_result, tp):

    # retuns DF with detailed information.

    result = [] # stores (index, tuple of data)
    table  = []
    issues = []
    exceptions = 'line qor.trace-stats-cpu'

    on_diff = False
    last_comparable = 0 

    msg_nd = ''
    for i in range(len(non_rep_result)):
        # the actual data we are reviewing
        tup = non_rep_result[i]
        base_data = tup[0]
        flow_data = tup[1]
        diff_data = tup[2]

        comparable = base_data and flow_data

        if comparable: 
            step_level = base_data['step_level']
            step_stack = base_data['step_stack']

            # check if we are backing from step diff
            if result \
                and len(result[-1]) == 3 \
                and (result[-1][1] == None or result[-1][2] == None):
                
                if result and result[-1][0] != i-1:
                    result.append((i-2,'...'))
                    table.append({
                        'step_stack': '...', 
                        'log_base': '--', 
                        'log_flow': '--',
                        'comment' : 'open %s difference in between'%tp if on_diff else 'nothing else to report in between', 
                    })

                b_data = non_rep_result[i-1][0]['step_stack'] if non_rep_result[i-1][0] != None else None
                f_data = non_rep_result[i-1][1]['step_stack'] if non_rep_result[i-1][1] != None else None
                
                has_data = 'base_flow' if b_data else 'test_flow'

                result.append((i-1, b_data, f_data))
                table.append({
                        'step_stack': '>'.join(b_data) if b_data else '>'.join(f_data),
                        'log_base'  : non_rep_result[i-1][0]['line'] if b_data else '--',
                        'log_flow'  : non_rep_result[i-1][1]['line'] if f_data else '--',
                        'comment'   : 'un-comparable step, only present in %s'%has_data , 
                    })

                result.append((i,step_stack))
                table.append({
                        'step_stack': '>'.join(step_stack),
                        'log_base'  : non_rep_result[i][0]['line'] ,
                        'log_flow'  : non_rep_result[i][1]['line'] ,
                        'comment'   : 'open %s difference: \n %s'%(tp,diff_data)  if on_diff else 'nothing to report', 
                    })


            elif   step_level == 1 : 
                # check if there was info in between
                if result and result[-1][0] != i-1:
                    result.append((i-2,'...'))
                    table.append({
                        'step_stack': '...', 
                        'log_base': '--', 
                        'log_flow': '--',
                        'comment' : 'open %s difference in between'%tp if on_diff else 'nothing else to report in between', 
                    })

                result.append((i,step_stack))
                table.append({
                        'step_stack': '>'.join(step_stack), 
                        'log_base'  : non_rep_result[i][0]['line'] ,
                        'log_flow'  : non_rep_result[i][1]['line'] ,
                        'comment'   : 'open %s difference: \n %s'%(tp,diff_data) if on_diff else 'nothing to report', 
                    })

            elif diff_data and not on_diff:
                # discard if only line diff
                for diff in diff_data:
                    if diff[1] not in exceptions:

                        # check if there was info in between
                        if result[-1][0] != i-1:
                            result.append((i-2,'...'))
                            table.append({
                                'step_stack': '...', 
                                'log_base': '--', 
                                'log_flow': '--',
                                'comment' : 'open %s difference in between'%tp if on_diff else 'nothing else to report in between', 
                            })

                        previous_stack = non_rep_result[last_comparable][0]['step_stack']
                        result.append((i-1,previous_stack))
                        table.append({
                            'step_stack': '>'.join(previous_stack), 
                            'log_base'  : non_rep_result[last_comparable][0]['line'], 
                            'log_flow'  : non_rep_result[last_comparable][1]['line'],
                            'comment'   : 'latest %s match, %s'%(tp,non_rep_result[last_comparable][0][tp]), 
                        })
                        
                        
                        result.append((i,step_stack, diff_data))
                        table.append({
                            'step_stack': '>'.join(step_stack), 
                            'log_base'  : non_rep_result[i][0]['line'], 
                            'log_flow'  : non_rep_result[i][1]['line'],
                            'comment'   : 'initial %s diff, %s'%(tp,diff_data), 
                        })
                        
                        on_diff = True
                        msg_nd  = '<b>inner %s difference</b><br>%s<br>'%(tp,'>'.join(step_stack))
                        msg_nd += '<tt><b>base_log line:</b> %s, <b>%s</b> = %s<br></tt>'%(non_rep_result[i][0]['line'],tp, non_rep_result[i][0][tp])
                        msg_nd += '<tt><b>test_log line:</b> %s, <b>%s</b> = %s<br></tt>'%(non_rep_result[i][1]['line'],tp, non_rep_result[i][1][tp])

                        break

            elif diff_data == [] and on_diff:
                previous_stack = non_rep_result[last_comparable][0]['step_stack']
                previous_diff = non_rep_result[last_comparable][2]

                # check if there was info in between
                if result[-1][0] != i-1:
                    result.append((i-2,'...'))
                    table.append({
                                'step_stack': '...', 
                                'log_base': '--', 
                                'log_flow': '--',
                                'comment' : 'open %s difference in between'%tp if on_diff else 'nothing else to report in between', 
                            })

                result.append((i-1,previous_stack, previous_diff))
                table.append({
                            'step_stack': '>'.join(previous_stack), 
                            'log_base'  : non_rep_result[last_comparable][0]['line'], 
                            'log_flow'  : non_rep_result[last_comparable][1]['line'],
                            'comment'   : 'latest %s diff, %s'%(tp, non_rep_result[last_comparable][2]), 
                        })

                result.append((i,step_stack))
                table.append({
                        'step_stack': '>'.join(step_stack), 
                        'log_base'  : non_rep_result[i][0]['line'] ,
                        'log_flow'  : non_rep_result[i][1]['line'] ,
                        'comment'   : 'closing %s diff\n, %s_base: %s\n %s_flow: %s\n%s'%(tp,tp,non_rep_result[i][0][tp],tp,non_rep_result[i][1][tp], diff_data), 
                    })

                on_diff = False

            elif diff_data and on_diff:
                # check if data is irrelevant
                all_exceptions = True
                for diff in diff_data:
                    if diff[1] not in exceptions:
                        all_exceptions = False

                if all_exceptions:
                    # now we are closing previous differences
                    previous_stack = non_rep_result[last_comparable][0]['step_stack']
                    previous_diff = non_rep_result[last_comparable][2]

                    # check if there was info in between
                    if result[-1][0] != i-1:
                        result.append((i-2,'...'))
                        table.append({
                                'step_stack': '...', 
                                'log_base': '--', 
                                'log_flow': '--',
                                'comment' : 'open %s difference in between'%tp if on_diff else 'nothing else to report in between', 
                            })

                    result.append((i-1,previous_stack, previous_diff))
                    table.append({
                                'step_stack': '>'.join(previous_stack), 
                                'log_base'  : non_rep_result[last_comparable][0]['line'], 
                                'log_flow'  : non_rep_result[last_comparable][1]['line'],
                                'comment'   : 'latest %s diff, %s'%(tp, non_rep_result[last_comparable][2]), 
                            })

                    result.append((i,step_stack))
                    table.append({
                            'step_stack': '>'.join(step_stack), 
                            'log_base'  : non_rep_result[i][0]['line'] ,
                            'log_flow'  : non_rep_result[i][1]['line'] ,
                            'comment'   : 'closing %s diff\n, %s_base: %s\n %s_flow: %s\n%s'%(tp,tp,non_rep_result[i][0][tp],tp,non_rep_result[i][1][tp], diff_data), 
                        })

                    on_diff = False

            else:
                # probablye there are more conditions to meet
                pass

            last_comparable = i
        else:
            # we've got uncomparable steps,
            # so we must to report it
            msg = 'inner %s trajectory differences, uncomparable steps'%tp
            if msg not in issues:
                issues.append(msg)

            # check if previous one is comparable
            if len(result[-1]) == 2 and result[-1][1] != '...':
                # check if there was info in between
                if result[-1][0] != i-1:
                    result.append((i-2,'...'))
                    table.append({
                                'step_stack': '...', 
                                'log_base': '--', 
                                'log_flow': '--',
                                'comment' : 'open %s difference in between'%tp if on_diff else 'nothing else to report in between', 
                            })

                b_data = base_data['step_stack'] if base_data != None else None
                f_data = flow_data['step_stack'] if flow_data != None else None
                has_data = 'base_flow' if b_data else 'test_flow'
                msg_suffix = ', with %s diff'%tp if on_diff else ''

                result.append((last_comparable, non_rep_result[last_comparable][0]['step_stack']))
                table.append({
                        'step_stack': '>'.join(non_rep_result[last_comparable][0]['step_stack']), 
                        'log_base'  : non_rep_result[last_comparable][0]['line'],
                        'log_flow'  : non_rep_result[last_comparable][1]['line'],
                        'comment'   : 'latest comparable step' + msg_suffix, 
                    })


                result.append((i, b_data, f_data))
                table.append({
                        'step_stack': '>'.join(b_data) if b_data else '>'.join(f_data),
                        'log_base'  : non_rep_result[i][0]['line'] if b_data else '--',
                        'log_flow'  : non_rep_result[i][1]['line'] if f_data else '--',
                        'comment'   : 'un-comparable step, only present in %s'%has_data , 
                    })
            
    if on_diff: 
        msg_nd = msg_nd.replace('inner ','')
    
    if msg_nd: issues.append(msg_nd)

    # pp.pprint(result)
    df_table = pd.DataFrame(table)
    
    print('--analysis done')
    return issues, df_table

def non_rep_report(non_rep_result, tp):

    # retuns DF with detailed information.

    result = [] # stores (index, tuple of data)
    table  = []
    issues = []
    exceptions = 'line qor.trace-stats-cpu'

    on_diff = False
    last_comparable = 0 

    msg_nd = ''
    for i in range(len(non_rep_result)):
        # the actual data we are reviewing
        tup = non_rep_result[i]
        base_data = tup[0]
        flow_data = tup[1]
        diff_data = tup[2]

        comparable = base_data and flow_data

        


        if comparable: 
            step_level = base_data['step_level']
            step_stack = base_data['step_stack']


            if   step_level == 1 : 
                # check if there was info in between
                if result and result[-1][0] != i-1:
                    result.append((i-2,'...'))
                    table.append({
                        'step_stack': '...', 
                        'log_base': '--', 
                        'log_flow': '--',
                        'comment' : 'open %s difference in between'%tp if on_diff else 'nothing else to report in between', 
                    })

                result.append((i,step_stack))
                table.append({
                        'step_stack': '>'.join(step_stack), 
                        'log_base'  : non_rep_result[i][0]['line'] ,
                        'log_flow'  : non_rep_result[i][1]['line'] ,
                        'comment'   : 'open %s difference'%tp if on_diff else 'nothing to report',
                        'base_data' : non_rep_result[i][0][tp],
                        'flow_data' : non_rep_result[i][1][tp],
                    })


            # check if we are backing from un-comparable
            if result \
                and len(result[-1]) == 3 \
                and (result[-1][1] == None or result[-1][2] == None):
                
                if result and result[-1][0] != i-1:
                    result.append((i-2,'...'))

                    table.append({
                        'step_stack': '...', 
                        'log_base': '', 
                        'log_flow': '',
                        'comment' : 'open %s difference in between'%tp if on_diff else 'nothing else to report in between',
                    })

                b_data = non_rep_result[i-1][0]['step_stack'] if non_rep_result[i-1][0] != None else None
                f_data = non_rep_result[i-1][1]['step_stack'] if non_rep_result[i-1][1] != None else None
                
                has_data = 'base_flow' if b_data else 'test_flow'

                result.append((i-1, b_data, f_data))
                table.append({
                        'step_stack': '>'.join(b_data) if b_data else '>'.join(f_data),
                        'log_base'  : non_rep_result[i-1][0]['line'] if b_data else '--',
                        'log_flow'  : non_rep_result[i-1][1]['line'] if f_data else '--',
                        'comment'   : 'un-comparable step, only present in %s'%has_data , 
                    })

                result.append((i,step_stack))
                table.append({
                        'step_stack': '>'.join(step_stack),
                        'log_base'  : non_rep_result[i][0]['line'] ,
                        'log_flow'  : non_rep_result[i][1]['line'] ,
                        'comment'   : 'open %s difference'%tp  if on_diff else 'nothing to report',
                        'base_data' : non_rep_result[i][0][tp],
                        'flow_data' : non_rep_result[i][1][tp],
                    })


            # elif   step_level == 1 : 
            #     # check if there was info in between
            #     if result and result[-1][0] != i-1:
            #         result.append((i-2,'...'))
            #         table.append({
            #             'step_stack': '...', 
            #             'log_base': '--', 
            #             'log_flow': '--',
            #             'comment' : 'open %s difference in between'%tp if on_diff else 'nothing else to report in between', 
            #         })

            #     result.append((i,step_stack))
            #     table.append({
            #             'step_stack': '>'.join(step_stack), 
            #             'log_base'  : non_rep_result[i][0]['line'] ,
            #             'log_flow'  : non_rep_result[i][1]['line'] ,
            #             'comment'   : 'open %s difference'%tp if on_diff else 'nothing to report',
            #             'base_data' : non_rep_result[i][0][tp],
            #             'flow_data' : non_rep_result[i][1][tp],
            #         })

            elif diff_data and not on_diff:
                # discard if only line diff
                for diff in diff_data:
                    if diff[1] not in exceptions:

                        # check if there was info in between
                        if result[-1][0] != i-1:
                            result.append((i-2,'...'))
                            table.append({
                                'step_stack': '...', 
                                'log_base': '--', 
                                'log_flow': '--',
                                'comment' : 'open %s difference in between'%tp if on_diff else 'nothing else to report in between', 
                            })

                        previous_stack = non_rep_result[last_comparable][0]['step_stack']
                        result.append((i-1,previous_stack))
                        table.append({
                            'step_stack': '>'.join(previous_stack), 
                            'log_base'  : non_rep_result[last_comparable][0]['line'], 
                            'log_flow'  : non_rep_result[last_comparable][1]['line'],
                            'comment'   : 'latest %s match'%(tp),
                            'base_data' : non_rep_result[last_comparable][0][tp],
                            'flow_data' : non_rep_result[last_comparable][1][tp],                                
                        })
                        
                        
                        result.append((i,step_stack, diff_data))
                        table.append({
                            'step_stack': '>'.join(step_stack), 
                            'log_base'  : non_rep_result[i][0]['line'], 
                            'log_flow'  : non_rep_result[i][1]['line'],
                            'comment'   : 'initial %s difference'%(tp),
                            'base_data' : non_rep_result[i][0][tp],
                            'flow_data' : non_rep_result[i][1][tp],
                        })
                        
                        on_diff = True
                        msg_nd  = '<b>inner %s difference</b><br>%s<br>'%(tp,'>'.join(step_stack))
                        msg_nd += '<tt><b>base_log line:</b> %s, <b>%s</b> = %s<br></tt>'%(non_rep_result[i][0]['line'],tp, non_rep_result[i][0][tp])
                        msg_nd += '<tt><b>test_log line:</b> %s, <b>%s</b> = %s<br></tt>'%(non_rep_result[i][1]['line'],tp, non_rep_result[i][1][tp])

                        break

            elif diff_data == [] and on_diff:
                previous_stack = non_rep_result[last_comparable][0]['step_stack']
                previous_diff = non_rep_result[last_comparable][2]

                # check if there was info in between
                if result[-1][0] != i-1:
                    result.append((i-2,'...'))
                    table.append({
                                'step_stack': '...', 
                                'log_base': '--', 
                                'log_flow': '--',
                                'comment' : 'open %s difference in between'%tp if on_diff else 'nothing else to report in between', 
                            })

                result.append((i-1,previous_stack, previous_diff))
                table.append({
                            'step_stack': '>'.join(previous_stack), 
                            'log_base'  : non_rep_result[last_comparable][0]['line'], 
                            'log_flow'  : non_rep_result[last_comparable][1]['line'],
                            'comment'   : 'latest %s diff'%(tp),
                            'base_data' : non_rep_result[last_comparable][0][tp],
                            'flow_data' : non_rep_result[last_comparable][1][tp],
                        })

                result.append((i,step_stack))
                table.append({
                        'step_stack': '>'.join(step_stack), 
                        'log_base'  : non_rep_result[i][0]['line'] ,
                        'log_flow'  : non_rep_result[i][1]['line'] ,
                        'comment'   : 'closing %s diff'%(tp),
                        'base_data' : non_rep_result[i][0][tp],
                        'flow_data' : non_rep_result[i][1][tp], 
                    })

                on_diff = False

            elif diff_data and on_diff:
                # check if data is irrelevant
                all_exceptions = True
                for diff in diff_data:
                    if diff[1] not in exceptions:
                        all_exceptions = False

                if all_exceptions:
                    # now we are closing previous differences
                    previous_stack = non_rep_result[last_comparable][0]['step_stack']
                    previous_diff = non_rep_result[last_comparable][2]

                    # check if there was info in between
                    if result[-1][0] != i-1:
                        result.append((i-2,'...'))
                        table.append({
                                'step_stack': '...', 
                                'log_base': '--', 
                                'log_flow': '--',
                                'comment' : 'open %s difference in between'%tp if on_diff else 'nothing else to report in between', 
                            })

                    result.append((i-1,previous_stack, previous_diff))
                    table.append({
                                'step_stack': '>'.join(previous_stack), 
                                'log_base'  : non_rep_result[last_comparable][0]['line'], 
                                'log_flow'  : non_rep_result[last_comparable][1]['line'],
                                'comment'   : 'latest %s diff'%(tp),
                                'base_data' : non_rep_result[last_comparable][0][tp],
                                'flow_data' : non_rep_result[last_comparable][1][tp], 
                            })

                    result.append((i,step_stack))
                    table.append({
                            'step_stack': '>'.join(step_stack), 
                            'log_base'  : non_rep_result[i][0]['line'] ,
                            'log_flow'  : non_rep_result[i][1]['line'] ,
                            'comment'   : 'closing %s diff'%(tp),
                            'base_data' : non_rep_result[i][0][tp],
                            'flow_data' : non_rep_result[i][1][tp], 
                        })

                    on_diff = False

            else:
                # probablye there are more conditions to meet
                pass

            
            last_comparable = i
        else:
            # we've got uncomparable steps,
            # so we must to report it
            msg = 'inner %s trajectory differences, uncomparable steps'%tp
            if msg not in issues:
                issues.append(msg)

            # check if previous one is comparable
            if len(result[-1]) == 2 and result[-1][1] != '...':
                # check if there was info in between
                if result[-1][0] != i-1:
                    result.append((i-2,'...'))
                    table.append({
                                'step_stack': '...', 
                                'log_base'  : '--', 
                                'log_flow'  : '--',
                                'comment'   : 'open %s difference in between'%tp if on_diff else 'nothing else to report in between', 
                            })

                b_data = base_data['step_stack'] if base_data != None else None
                f_data = flow_data['step_stack'] if flow_data != None else None
                has_data = 'base_flow' if b_data else 'test_flow'

                msg_suffix = ', with %s diff'%tp if on_diff else ''

                result.append((last_comparable, non_rep_result[last_comparable][0]['step_stack']))
                table.append({
                        'step_stack': '>'.join(non_rep_result[last_comparable][0]['step_stack']), 
                        'log_base'  : non_rep_result[last_comparable][0]['line'],
                        'log_flow'  : non_rep_result[last_comparable][1]['line'],
                        'comment'   : 'latest comparable step' + msg_suffix,
                        'base_data' : non_rep_result[last_comparable][0][tp],
                        'flow_data' : non_rep_result[last_comparable][1][tp],
                    })

                result.append((i, b_data, f_data))
                table.append({
                        'step_stack': '>'.join(b_data) if b_data else '>'.join(f_data),
                        'log_base'  : non_rep_result[i][0]['line'] if b_data else '--',
                        'log_flow'  : non_rep_result[i][1]['line'] if f_data else '--',
                        'comment'   : 'un-comparable step, only present in %s'%has_data , 
                    })
            
    if on_diff: 
        msg_nd = msg_nd.replace('inner ','')
    
    if msg_nd: issues.append(msg_nd)

    # pp.pprint(result)
    #df_table = pd.DataFrame(table)
    
    print('--analysis done')
    return issues, table

def get_fail_info(des_dir):
    result = {}
    
    cache_file = os.path.join(des_dir, 'prreport.cache')
    if os.path.exists(cache_file) and os.path.isfile(cache_file):
        
        cache_lines = open(cache_file, 'r').readlines()
        for line in cache_lines:

            line = line.strip().split()

            if 'Status' in line and len(line) == 2:
                result['prs_status'] = line[1]

            if 'FatalLN' in line and len(line) == 2:
                result['fatal_line'] = int(line[1])

            if 'FatalFile' in line and len(line) == 2:
                result['fatal_file'] = line[1]
    
    else: 
        print('there is no prreport.cache file for this design.')


    if result['prs_status'] != 'Done':

        fatal_file_loc = os.path.join(des_dir,result['fatal_file'])

        if os.path.exists(fatal_file_loc + '.gz'):
            fatal_log = gzip.open(fatal_file_loc + '.gz').read().decode(encoding='utf-8', errors ='ignore').splitlines()
        else:
            fatal_log = open(fatal_file_loc).readlines()

        try:
            result['fatal_text'] = fatal_log[result['fatal_line']-1].strip()
        except:
            result['fatal_text'] = 'couldn\'t read logfile at %d'%result['fatal_line']
            
            return result

        
        if ('Error' not in result['fatal_text']) and ('Killed' not in result['fatal_text']):
            
            # lookup for a near error
            for i in range(result['fatal_line']-10, result['fatal_line']+10):
                if ('Error' in fatal_log[i]) or ('The tool has just encountered a fatal error:' in fatal_log[i]) or ('Killed' in fatal_log[i]):
                    if 'Error: 0' in fatal_log[i]:
                        result['fatal_text'] += fatal_log[i]
                    else:
                        result['fatal_text'] = fatal_log[i]


        for i in range(result['fatal_line'],len(fatal_log)):
            log_line = fatal_log[i]
            if 'PV-INFO: Fatal URL =' in log_line:
                result['stack_trace'] = fatal_log[i].split()[5]

    return result

def get_run_status(run_dir, flows, designs):
    # check status of designs of a prs_flow
    # it's focused on dc logfiles and detects fails with help of dcrpt from prreport.cache
    rundir = run_dir

    result = {}
    if os.path.exists(rundir) and os.path.isdir(rundir):
        
        flows = flows.split(',')

        for flow in flows:
            flow_dir = os.path.join(rundir,flow)
            
            if os.path.exists(flow_dir) and os.path.isdir(flow_dir):
                result[flow] = {}

                des_list = os.listdir(flow_dir) if designs == '' else designs.split(',')
                
                for d in des_list:
                        des_dir = os.path.join(flow_dir,d)        
                        des_flag_file = os.path.join(des_dir, '%s.des.cfg'%d)
                        
                        if os.path.isfile(des_flag_file):
                            result[flow][d] = {}

                            done_file  = os.path.join(des_dir, '%s.all.done'%d)
                            hinfo_file = os.path.join(des_dir, '%s.hinfo.out'%d)

                            if    os.path.isfile(done_file) : 
                                
                                result[flow][d]['status'] = 'all_done'
                                result[flow][d]['prs_info'] = get_fail_info(des_dir)
                            
                            elif  os.path.isfile(hinfo_file): result[flow][d]['status'] = 'running'
                            else: result[flow][d]['status'] = 'queued'

                        else:
                            if os.path.isdir(des_dir): print('%s seems not a valid design. ...continue'%d)
                        
            else:
                print('can\'t locate flow %s, skipping...'%flow)
    else:
        print('can\'t locate path %s'%rundir)
        print('aborting...')
        exit()

    return result

def non_rep_flow_report(rundir, flows, report_name, designs, tp, output):

    
    tp = 'checksum'

    print('getting prs_status')
    status_dict = get_run_status(rundir, flows, designs)
    
    base_flow = flows.split(',')[0]

    base_des_dict = status_dict[base_flow]

    writer = pd.ExcelWriter('%s.xlsx'%output, engine='xlsxwriter')

    for flow, flow_des_dict in status_dict.items():
        if flow == base_flow: continue

        print('comparing', flow, 'with', base_flow)
        # get max list of designs
        flow_des_ls = list(flow_des_dict.keys())
        base_des_ls = list(base_des_dict.keys())
        
        result = []

        des_ls = flow_des_ls if len(flow_des_ls) > len(base_des_ls) else base_des_ls


        for d in des_ls:
            print(d)

            ready = (base_des_dict[d]['status'] == 'all_done') and (flow_des_dict[d]['status'] == 'all_done')
            
            log_flow = os.path.join(rundir,flow,d,'%s.dcopt.out.gz'%d)
            log_base = os.path.join(rundir,base_flow,d,'%s.dcopt.out.gz'%d)

            result_des = {}
            result_des['design'] = d
            
            if ready:

                base_prs_st = base_des_dict[d]['prs_info']['prs_status']
                flow_prs_st = flow_des_dict[d]['prs_info']['prs_status']

                failed = (base_prs_st != 'Done') or (flow_prs_st != 'Done')
                
                if not failed:

                    rpt_base = get_action_dep_rpts(log_to_str(log_base),tp)
                    rpt_flow = get_action_dep_rpts(log_to_str(log_flow),tp)

                    print('-checking for last %s differences'%tp)
                    nd_check_result = nd_check(rpt_base, rpt_flow, 0.3, tp)

                    
                    if nd_check_result == 'Yes':
                        result_des[base_flow] = base_prs_st
                        result_des[flow] = 'ND_issue'

                        # this is a dataframe
                        print('-comparing data')
                        nd_des_report = non_rep_report(non_rep_analysis(rpt_base, rpt_flow, 0.3))
                        nd_des_report.to_excel(writer, sheet_name=d)

                    elif nd_check_result == 'No':
                        result_des[base_flow] = base_prs_st
                        result_des[flow] = flow_prs_st

                    else:
                        result_des[base_flow] = base_prs_st if nd_check_result != 'base_incomp' else 'incomplete run'
                        result_des[flow] = flow_prs_st if nd_check_result != 'test_incomp' else 'incomplete run'

                else:
                    print('failed runs: base_status : %s | flow_status : %s'%(base_prs_st, flow_prs_st))
                    result_des[base_flow] = base_prs_st
                    result_des[flow] = flow_prs_st
            
            else:
                print('not ready')
                result_des[base_flow] = base_des_dict[d]['status']
                result_des[flow] = flow_des_dict[d]['status']

            print(result_des)
            result.append(result_des)

        df = pd.DataFrame(result)
        df.to_excel(writer, 'summary')

        writer.save()

#non_rep_flow_report(rundir, flows, report_name, designs,'', 'ND_sum_x')
def non_rep_flow_report_all_old(rundir, flows, report_name, designs, output, tp):

    summary = []

    if tp:
        analysis_type = [tp]
    else:    
        analysis_type = ['qor', 'checksum']

    print('getting prs_status')
    status_dict = get_run_status(rundir, flows, designs)
    
    base_flow = flows.split(',')[0]
    base_des_dict = status_dict[base_flow]

    for flow, flow_des_dict in status_dict.items():
        if flow == base_flow: continue
        # get max list of designs
        
        flow_des_ls = list(flow_des_dict.keys())
        base_des_ls = list(base_des_dict.keys())
        
        des_ls = flow_des_ls if len(flow_des_ls) > len(base_des_ls) else base_des_ls

        for d in des_ls:
            print(d)

            summary_des_dict = {
                'design'  : d ,
                base_flow : '',
                flow      : '',
                'results' : '<ul class="list-group">',
                'reports' : '<div class="list-group">',
            }

            log_flow = os.path.join(rundir,flow,d,'%s.dcopt.out.gz'%d)
            log_base = os.path.join(rundir,base_flow,d,'%s.dcopt.out.gz'%d)

            result_des = {}
            result_des['design'] = d

            ready  = (base_des_dict[d]['status'] == 'all_done') and (flow_des_dict[d]['status'] == 'all_done')
            if ready:

                base_prs_st = base_des_dict[d]['prs_info']['prs_status']
                flow_prs_st = flow_des_dict[d]['prs_info']['prs_status']
                failed = (base_prs_st != 'Done') or (flow_prs_st != 'Done')

                summary_des_dict[base_flow] = base_des_dict[d]['prs_info']['prs_status']
                summary_des_dict[flow] = flow_des_dict[d]['prs_info']['prs_status']

                # some aesthetical name change
                if summary_des_dict[base_flow] == 'all_done': summary_des_dict[base_flow] == 'Done'
                if summary_des_dict[flow]      == 'all_done': summary_des_dict[flow] == 'Done'

                if not failed:
                    for analysis in analysis_type:
                        tp = analysis
                        rpt_base = get_action_dep_rpts(log_to_str(log_base),tp)
                        rpt_flow = get_action_dep_rpts(log_to_str(log_flow),tp)
                        
                        print('-checking logfiles completeness for %s'%tp)
                        # returns empty if all_good
                        logfile_issue = nd_log_check(rpt_base, rpt_flow, 0.3, tp)
                        
                        if not logfile_issue :
                            # all good so we'll ananlyze
                            print('-comparing data')
                            nd_issues_list, nd_df  = non_rep_report(non_rep_analysis(rpt_base, rpt_flow, 0.0, tp), tp)
                            
                            # pp.pprint(nd_issues_list)

                            # do html_report in case of any issue and append file to results
                            if nd_issues_list:
                                des_report_name = '%s_%s_report.html'%(d,tp)
                                html = nd_df.to_html()

                                des_report_file = open(des_report_name,'w')
                                des_report_file.write(html)
                                des_report_file.close()

                                # this is the final idea
                                # des_report_name = nd_report_design(df, log_base, log_test)
                                summary_des_dict['reports'] += '<a href="%s" class="list-group-item list-group-item-action list-group-item-primary">%s_report</a>'%(des_report_name,tp)

                                for issue in nd_issues_list:
                                    if 'inner' in issue:
                                        msg = '\n <li class="list-group-item list-group-item-warning">%s%s</li>'%(warning_icon,issue)
                                    else:
                                        msg = '\n <li class="list-group-item list-group-item-danger">%s%s</li>'%(issue_icon,issue)

                                    if msg not in summary_des_dict['results']:
                                        summary_des_dict['results'] += msg

                            else:
                                summary_des_dict['results'] += '<li class="list-group-item list-group-item-success">%srepeatable %s results.</li>'%(pass_icon,tp)
   
                        else:
                            # Incomplete log case handling
                            m_result = '\n<li class="list-group-item list-group-item-secondary">%a<b>%s:</b> %s.</li>'%(info_icon,flow,logfile_issue)
                            if m_result not in summary_des_dict['results']:
                                summary_des_dict['results'] += m_result
                            else:
                                pass
                
                else:
                    # fail cases handling:
                    got_it = False

                    if base_prs_st != 'Done': 
                        got_it = True
                        m_result = '\n<li class="list-group-item list-group-item-danger">%s<i>%s</i> unable to analyze due to fail.<br>'%(issue_icon,base_flow)
                        m_result += '<tt><b>%s</b>'%base_des_dict[d]['prs_info']['fatal_file'] if 'fatal_file' in base_des_dict[d]['prs_info'] else ''
                        m_result += ': %s: '%base_des_dict[d]['prs_info']['fatal_line'] if 'fatal_line' in base_des_dict[d]['prs_info'] else ''
                        m_result += '<i>%s.</i>'%base_des_dict[d]['prs_info']['fatal_text'] if 'fatal_text' in base_des_dict[d]['prs_info'] else ''
                        m_result += '<a href="%s" class="badge badge-danger">stack_trace</a>'%base_des_dict[d]['prs_info']['stack_trace'] if 'stack_trace' in base_des_dict[d]['prs_info'] else ''
                        m_result += '</tt></li>'
                        if m_result not in  summary_des_dict['results']:
                            summary_des_dict['results'] += m_result
                            
                    if flow_prs_st != 'Done':
                        got_it =True 
                        m_result = '\n<li class="list-group-item list-group-item-danger">%s<i>%s</i> unable to analyze due to fail.<br>'%(issue_icon,flow)
                        m_result += '<tt><b>%s</b>'%flow_des_dict[d]['prs_info']['fatal_file'] if 'fatal_file' in flow_des_dict[d]['prs_info'] else '' 
                        m_result += ':%s:'%flow_des_dict[d]['prs_info']['fatal_line'] if 'fatal_line' in flow_des_dict[d]['prs_info'] else '' 
                        m_result += '<i>%s.</i>'%flow_des_dict[d]['prs_info']['fatal_text'] if flow_des_dict[d]['prs_info']['fatal_text'] else ''
                        
                        m_result += '<a href="%s" class="badge badge-info">stack_trace</a>'%flow_des_dict[d]['prs_info']['stack_trace'] if 'stack_trace' in flow_des_dict[d]['prs_info'] else ''

                        m_result += '</tt></li>'
                        if m_result not in  summary_des_dict['results']:
                            summary_des_dict['results'] += m_result

                    if not got_it:
                        m_result = '\n<li class="list-group-item list-group-item-danger">%sunable to analize due to fail.</li>'%issue_icon
                        if m_result not in  summary_des_dict['results']:
                            summary_des_dict['results'] += m_result

                    summary_des_dict[base_flow] = base_prs_st
                    summary_des_dict[flow] = flow_prs_st
                    
                
            
            else:
                print('not ready')
                summary_des_dict[base_flow] = base_des_dict[d]['status']
                summary_des_dict[flow] = flow_des_dict[d]['status']
                # (base_des_dict[d]['status'] == 'all_done') and (flow_des_dict[d]['status'] == 'all_done')
                
                if base_des_dict[d]['status'] != 'all_done': 
                    m_result = '\n<li class="list-group-item list-group-item-secondary">%s<b>%s</b> is not finished.</div>'%(info_icon,base_flow)
                    if m_result not in  summary_des_dict['results']:
                        summary_des_dict['results'] += m_result

                if flow_des_dict[d]['status'] != 'all_done': 
                    m_result = '\n<li class="list-group-item list-group-item-secondary">%s<b>%s</b> is not finished.</div>'%(info_icon,flow)
                    if m_result not in  summary_des_dict['results']:
                        summary_des_dict['results'] += m_result

            summary_des_dict['reports'] += '\n</div>\n'
            summary_des_dict['results'] += '\n</ul>\n'
            #print(result_des)
            #result.append(result_des)
            # pp.pprint(summary_des_dict)
            summary.append(summary_des_dict)

            # just speeding a up the thing
            flow_report_html(rundir, flows, report_name, designs, output, tp, summary)

        return summary 

def non_rep_flow_report_all(rundir, flows, report_name, designs, output, tp):

    summary = []

    if tp:
        analysis_type = tp.split()
    else:    
        analysis_type = ['qor', 'checksum']

    print('getting prs_status')
    status_dict = get_run_status(rundir, flows, designs)
    
    base_flow = flows.split(',')[0]
    base_des_dict = status_dict[base_flow]

    for flow, flow_des_dict in status_dict.items():
        if flow == base_flow: continue
        # get max list of designs
        
        flow_des_ls = list(flow_des_dict.keys())
        base_des_ls = list(base_des_dict.keys())
        
        des_ls = flow_des_ls if len(flow_des_ls) > len(base_des_ls) else base_des_ls
        des_ls.sort()

        for d in des_ls:
            print(d)

            summary_des_dict = {
                'design'  : d ,
                base_flow : '',
                flow      : '',
                'results' : '<ul class="list-group">',
                'reports' : '<div class="list-group">',
            }

            log_flow = os.path.join(rundir,flow,d,'%s.dcopt.out.gz'%d)
            log_base = os.path.join(rundir,base_flow,d,'%s.dcopt.out.gz'%d)

            result_des = {}
            result_des['design'] = d

            ready  = (base_des_dict[d]['status'] == 'all_done') and (flow_des_dict[d]['status'] == 'all_done')
            if ready:

                base_prs_st = base_des_dict[d]['prs_info']['prs_status']
                flow_prs_st = flow_des_dict[d]['prs_info']['prs_status']
                failed = (base_prs_st != 'Done') or (flow_prs_st != 'Done')

                summary_des_dict[base_flow] = base_des_dict[d]['prs_info']['prs_status']
                summary_des_dict[flow] = flow_des_dict[d]['prs_info']['prs_status']

                # some aesthetical name change
                if summary_des_dict[base_flow] == 'all_done': summary_des_dict[base_flow] == 'Done'
                if summary_des_dict[flow]      == 'all_done': summary_des_dict[flow] == 'Done'

                if not failed:
                    for analysis in analysis_type:
                        tp = analysis
                        rpt_base = get_action_dep_rpts(log_to_str(log_base),tp)
                        rpt_flow = get_action_dep_rpts(log_to_str(log_flow),tp)
                        
                        print('-checking logfiles completeness for %s'%tp)
                        # returns empty if all_good
                        logfile_issue = nd_log_check(rpt_base, rpt_flow, 0.3, tp)
                        
                        if not logfile_issue :
                            # all good so we'll ananlyze
                            print('-comparing data')
                            try:            
                                nd_issues_list, table  = non_rep_report(non_rep_analysis(rpt_base, rpt_flow, 0.0, tp), tp)
                            except:
                                nd_issues_list =  'unable to analyze'
                                table = None

                            # pp.pprint(nd_issues_list)

                            # do html_report in case of any issue and append file to results
                            #if nd_issues_list and table:
                            if 1 and table:
                                html = des_report_html(table, log_flow, log_base, tp)
                                des_report_name = '%s_%s_%s_report.html'%(flow,d,tp)
                                # html = nd_df.to_html()
                                des_report_file = open(os.path.join(output,des_report_name),'w')
                                des_report_file.write(html)
                                des_report_file.close()

                                # this is the final idea
                                # des_report_name = nd_report_design(df, log_base, log_test)
                                summary_des_dict['reports'] += '<a href="%s" class="list-group-item list-group-item-action list-group-item-primary">%s_report</a>'%(des_report_name,tp)

                                for issue in nd_issues_list:
                                    if 'inner' in issue:
                                        msg = '\n <li class="list-group-item list-group-item-warning">%s%s</li>'%(warning_icon,issue)
                                    else:
                                        msg = '\n <li class="list-group-item list-group-item-danger">%s%s</li>'%(issue_icon,issue)

                                    if msg not in summary_des_dict['results']:
                                        summary_des_dict['results'] += msg

                            elif nd_issues_list == 'unable to analyze' and not table:
                                summary_des_dict['results'] += '<li class="list-group-item list-group-item-warning"> unable to analyze.</li>'
                            else:
                                summary_des_dict['results'] += '<li class="list-group-item list-group-item-success">%srepeatable %s results.</li>'%(pass_icon,tp)
   
                        else:
                            # Incomplete log case handling
                            m_result = '\n <li class="list-group-item list-group-item-secondary"> %a <b> %s: </b> %s.</li>'%(info_icon,flow,logfile_issue)
                            if m_result not in summary_des_dict['results']:
                                summary_des_dict['results'] += m_result
                            else:
                                pass
                
                else:
                    # fail cases handling:
                    got_it = False

                    if base_prs_st != 'Done': 
                        got_it = True
                        m_result = '\n<li class="list-group-item list-group-item-danger">%s<i>%s</i> unable to analyze due to fail.<br>'%(issue_icon,base_flow)
                        m_result += '<tt><b>%s</b>'%base_des_dict[d]['prs_info']['fatal_file'] if 'fatal_file' in base_des_dict[d]['prs_info'] else ''
                        m_result += ': %s: '%base_des_dict[d]['prs_info']['fatal_line'] if 'fatal_line' in base_des_dict[d]['prs_info'] else ''
                        m_result += '<i>%s.</i>'%base_des_dict[d]['prs_info']['fatal_text'] if 'fatal_text' in base_des_dict[d]['prs_info'] else ''
                        m_result += '<a href="%s" class="badge badge-danger">stack_trace</a>'%base_des_dict[d]['prs_info']['stack_trace'] if 'stack_trace' in base_des_dict[d]['prs_info'] else ''
                        m_result += '</tt></li>'
                        if m_result not in  summary_des_dict['results']:
                            summary_des_dict['results'] += m_result
                            
                    if flow_prs_st != 'Done':
                        got_it =True 
                        m_result = '\n<li class="list-group-item list-group-item-danger">%s<i>%s</i> unable to analyze due to fail.<br>'%(issue_icon,flow)
                        m_result += '<tt><b>%s</b>'%flow_des_dict[d]['prs_info']['fatal_file'] if 'fatal_file' in flow_des_dict[d]['prs_info'] else '' 
                        m_result += ':%s:'%flow_des_dict[d]['prs_info']['fatal_line'] if 'fatal_line' in flow_des_dict[d]['prs_info'] else '' 
                        m_result += '<i>%s.</i>'%flow_des_dict[d]['prs_info']['fatal_text'] if flow_des_dict[d]['prs_info']['fatal_text'] else ''
                        
                        m_result += '<a href="%s" class="badge badge-info">stack_trace</a>'%flow_des_dict[d]['prs_info']['stack_trace'] if 'stack_trace' in flow_des_dict[d]['prs_info'] else ''

                        m_result += '</tt></li>'
                        if m_result not in  summary_des_dict['results']:
                            summary_des_dict['results'] += m_result

                    if not got_it:
                        m_result = '\n<li class="list-group-item list-group-item-danger">%sunable to analize due to fail.</li>'%issue_icon
                        if m_result not in  summary_des_dict['results']:
                            summary_des_dict['results'] += m_result

                    summary_des_dict[base_flow] = base_prs_st
                    summary_des_dict[flow] = flow_prs_st
                    
                
            
            else:
                print('not ready')
                summary_des_dict[base_flow] = base_des_dict[d]['status']
                summary_des_dict[flow] = flow_des_dict[d]['status']
                # (base_des_dict[d]['status'] == 'all_done') and (flow_des_dict[d]['status'] == 'all_done')
                
                if base_des_dict[d]['status'] != 'all_done': 
                    m_result = '\n<li class="list-group-item list-group-item-secondary">%s<b>%s</b> is not finished.</div>'%(info_icon,base_flow)
                    if m_result not in  summary_des_dict['results']:
                        summary_des_dict['results'] += m_result

                if flow_des_dict[d]['status'] != 'all_done': 
                    m_result = '\n<li class="list-group-item list-group-item-secondary">%s<b>%s</b> is not finished.</div>'%(info_icon,flow)
                    if m_result not in  summary_des_dict['results']:
                        summary_des_dict['results'] += m_result

            summary_des_dict['reports'] += '\n</div>\n'
            summary_des_dict['results'] += '\n</ul>\n'
            #print(result_des)
            #result.append(result_des)
            # pp.pprint(summary_des_dict)
            summary.append(summary_des_dict)

            # just speeding a up the thing
            flow_report_html(rundir, flows, report_name, designs, output, tp, summary)

        return summary 

def flow_report_html(rundir, flows, report_name, designs, output, tp, summary):

    template_text = open('base.html', 'r').read()
    template = Template(template_text)
    
    if not summary:
        summary = non_rep_flow_report_all(rundir, flows, report_name, designs, output, tp)

    #print(df.columns)
    title = 'Non-Repeatability Report'
    base_flow = flows.split(',')[0]
    test_flow = flows.split(',')[1]
    
    headers = list(summary[0].keys()).copy() if summary else []
    
    for i in range(len(headers)):
        if headers[i] == base_flow: headers[i] = 'base_flow<br>status'
        if headers[i] == test_flow: headers[i] = 'test_flow<br>status'
        if headers[i] == 'design' : headers[i] = 'Design'
        if headers[i] == 'results': headers[i] = 'Opto-Step level diff results'
        if headers[i] == 'reports': headers[i] = 'Opto-Step level diff reports'
    
    rows = []

    for i in range(len(summary)):
        row = []
        for k,v in summary[i].items():
            row.append(v)
        rows.append(row)

    html = template.render(
        page_title = 'ND Report',
        report_title = title,
        rundir = rundir,
        base_flow = base_flow,
        test_flow = test_flow,
        headers = headers,
        rows = rows,
        done_icon = done_icon,
        pend_icon = pending_icon,
        fail_icon = fail_icon,
    )

    report_file = open(os.path.join(output,'%s.html'%report_name), 'w')
    report_file.write(html)
    report_file.close()
    # return summary, rows
    # for in summary:
    #     pass

    return summary

#flow_report_html(rundir, flows, report_name, designs, 'ND_sum_2x')

def des_report_html(table, log_flow, log_base, tp):

    template_text = open('base_des.html', 'r').read()
    template = Template(template_text)

    title = 'Opto-Step Diff Report (%s)'%tp

    html = template.render(
        page_title = 'Opto-step %s diff'%tp,
        report_title = title,
        base_logfile = log_flow,
        flow_logfile = log_base,
        table = table, 
        pass_icon = pass_icon,
        issue_icon = issue_icon,
        warning_icon = warning_icon,
        info_icon = info_icon,
        tp = tp,
    )

    return html
###########################################################
# testing utilities non_rep_analysis
def generate_pkls(tp):
    rundir = '/remote/dcopt077/nightly_prs/q2019.12-SP/DC_ICC2/D20200305_20_30/prs/run'
    base  = 'SRM_spg_timing_opt_area_trace_multi'
    flow  = 'SRM_spg_timing_opt_area_trace_multi_mirror'
    d     = 'A73_CPU'
    
    
    log_flow = os.path.join(rundir,flow,d,'%s.dcopt.out.gz'%d)
    log_base = os.path.join(rundir,base,d,'%s.dcopt.out.gz'%d)

    rpt_flow = get_action_dep_rpts(log_to_str(log_flow),tp)
    rpt_base = get_action_dep_rpts(log_to_str(log_base),tp)    

    # exporting 
    rpt_file_flow = open('rpt_flow_%s.pkl'%tp, 'wb')
    rpt_file_base = open('rpt_base_%s.pkl'%tp, 'wb')

    pkl.dump(rpt_flow, rpt_file_flow)
    pkl.dump(rpt_base, rpt_file_base)

    rpt_file_flow.close()
    rpt_file_base.close()

def load_from_pkl(file_name):
    
    file = open(file_name, 'rb')
    var  = pkl.load(file)
    file.close()

    return var

def unit_test_analysis():
    tp = 'qor'
    rpt_base = load_from_pkl('rpt_base_%s.pkl'%tp)
    rpt_flow = load_from_pkl('rpt_flow_%s.pkl'%tp)

    return non_rep_analysis(rpt_base, rpt_flow, 0.0, tp)


                    

                






            

        


            





