#!/slowfs/dcopt105/vasquez/cnda/Conda/bin/python

import os, re, json, argparse
import gzip
from datetime import datetime
import pprint
pp=pprint.PrettyPrinter(indent=2)

desc = '''
Report checksum and qor differences for a given flow and their _mirror version. (-vasquez-)
'''
parser = argparse.ArgumentParser(description=desc)

parser.add_argument('-rundir', type=str,
                    help='directory where the flows are located. Example: \'/remote/dcopt077/nightly_prs/p2019.03-SP/DC_ICC2/D20190613_20_30/prs/run\'')

parser.add_argument('-flow',  type =str, help = 'Name of the flow you want to compare against baseline flow.')
## parser.add_argument('-baseline', type =str, help = 'Name of the flow you want to use as reference for comparison.')
parser.add_argument('-designs', type =str,nargs = '+', help = 'List of designs to analyze. This could be a long list, please consider use a .csh wrapper.')
parser.add_argument('-result_dir', type =str, help = 'output directory') 
parser.add_argument('-report_name', type =str, help = 'name for report') 

args = parser.parse_args()

rundir   = args.rundir

#dirty workaround to do stuff in a PRSish way
flow     = args.flow
baseline = flow
flow     = '%s_mirror'%baseline
result_dir   = args.result_dir
#############################################

designs  = args.designs
report_name = args.report_name

verbose = True

# rpt_dir = '/slowfs/dcopt036/nightly_prs/q2019.12_ls/DC_ICC2/test2/prs/run/rpt_srm_icc2_spg_opt_area'
# rpt_dir = '/remote/pv/24x7/dc/P-2019.03-SP/nightly_prs/culprit/D20190306_20_30/DC_ICC2/SRM_ICC2_spg_opt_area_4683236_4687623_galapagos'
# rundir   = '/remote/dcopt077/nightly_prs/p2019.03-SP/DC_ICC2/D20190612_20_30/prs/run'
# rundir = '/remote/dcopt077/nightly_prs/p2019.03-SP/DC_ICC2/D20190613_20_30.trace/prs/run'
# flow     = 'SRM_ICC2_spg_opt_area_trace_mirror'
# baseline = 'SRM_ICC2_spg_opt_area_trace'
# designs  = 'A53 A53_ARM A57_Non_CPU A73_CPU ARCHS38_16nm ARCHS38_7nm ARCHS438 CortexM3 X5376 archipelago_N12_6T dcp212_Xm_Xttop dcp245_SPEEDY28_TOP dcp246_Xm_Xtmem dcp247_VDD5_mux2 dcp269_rob dcp270_enterprise_UPF dcp275_archipelago dcp276_xbar dcp426_opf_fp dcp427_DWC_usb3 dcp428_DWC_ddr dcp514_JDSIIP3A dcp517_PMA dcp518_top dcp519_fdeq_pnrb dcp520_ccu_msw dcp521_DWC_pcie_dm dcp522_c8docsis31_rx_top dcp550_memoir dcp556_DSH dcp557_opb_fp dcp564_leon3_mp_20_sset_ssink dcp568_mmu2 dcp569_GORDON dcp570_b33 dcp579_pba_fp dcp589_vd32043_top dcp596_ibe dcp597_mmu_thdo dcp599_rgx_tpu_mcu dcp607_mpcore dcp611_arm926ejs dcp615_CortexM3 dcp616_falcon_cpu dcp630_jones dcp631_mercer dcp632_teague dcp778_datapath dcp780_cbs_pollux_tx_dig dcp571_hrp_xb_m'.split(' ')
# designs = ['A73_CPU','dcp275_archipelago']
# designs = 'dcp631_mercer dcp632_teague dcp778_datapath dcp780_cbs_pollux_tx_dig dcp571_hrp_xb_m'.split(' ')

# major milestones in SRM flow
# eval compile_ultra -scan $rm_ultra_opt #firstcompile
# preview_dft
# insert_dft
# eval compile_ultra -incremental -scan $rm_incr_opt #incremental
# eval optimize_netlist -area #optimize

def parselog(**kwargs):
    
    ## parse the log passed as argument,
    ## return the following elements
    ## flow_paths: list of tuples with the full path to the steps (user_cmd, flow1, flow2,...flow6)
    ## chechsums : list of tuples with checksum results (user_cmd, step, design, checksum_value)
    ## qor_stats: list of tuples with qor numbers (user_cmd, step, {qor_dic})
    ## qor_dict: {metric1: value1, metric2: value2,... metricN: valueN}
    
    log = kwargs.get('log','')
    
    #report = kwargs.get('report','flow_paths')
    # user milestone cmds
    srm_milestones = {}
    # store action deployment data
    action_deployment = {}
    flow_depths = {}
    
    # useful patterns
    ptrn_first_compile    = r'^eval\scompile_ultra\s\-scan*'
    ptrn_preview_dft      = r'^preview_dft*'
    ptrn_insert_dft       = r'^insert_dft*'
    ptrn_incremental      = r'^eval\scompile_ultra\s\-incremental*'
    ptrn_optimize_net     = r'^eval\soptimize_netlist\s\-area'
    ptrn_action_dep_open  = r'^ACTION\sDEPLOYMENT\sv{4}\s\*{3}\s([a-zA-Z0-9\s\-_]+)\*{3}\s[0-9\:]+\s\*{3}\s.+action\:\s([A-Z_]+)'
    ptrn_trace            = '\s([a-z\-]+)\s([0-9\.]+)'
    ptrn_action_dep_close = r'^ACTION\sDEPLOYMENT\s\^{4}\s\*{3}\s([a-zA-Z0-9\s\-_]+)\*{3}'
    ptrn_flow_trace_begin = r'^FLOW\s([0-9])[\|\s]*([A-Za-z0-9_\-]+\sbegin).*'
    ptrn_flow_trace_end   = r'^FLOW\s([0-9])[\|\s]*([A-Za-z0-9_\-]+\send).*'
    ptrn_checksum         = r'^Design\sCheckSum\s([A-Za-z0-9_\-]+)\s\:\s([0-9\:]+)\s\s.+'

    flow_paths = []
    check_sums = []
    qor_stats = []

    if log != '':
        line_num = 1
        on_action_deploy = False
        
        # get action deployments
        
        current_user_cmd = ''
        current_fl = ['','','','','','']

        current_step = ''
        current_action = ''

        for line in log:
            # capturing user milestones cmds
            if re.match(ptrn_first_compile,line):
                current_user_cmd = 'first_compile'
                srm_milestones[current_user_cmd] = line_num
            if re.match(ptrn_preview_dft,line):
                current_user_cmd = 'preview_dft'
                srm_milestones[current_user_cmd] = line_num
            if re.match(ptrn_insert_dft,line):
                current_user_cmd = 'insert_dft'    
                srm_milestones[current_user_cmd] = line_num
            if re.match(ptrn_incremental,line):
                current_user_cmd = 'incremental_compile' 
                srm_milestones[current_user_cmd] = line_num
            if re.match(ptrn_optimize_net,line):
                current_user_cmd = 'optimize_netlist'
                srm_milestones[current_user_cmd] = line_num
            
            # capturing flow
            
            # capturing on beginnings
            m_flow_trace_begin = re.match(ptrn_flow_trace_begin, line)
            if m_flow_trace_begin:
                step_name = m_flow_trace_begin.group(2)
                depth = int(m_flow_trace_begin.group(1))
                
                current_fl[depth - 1] = step_name

                for i in range(depth,len(current_fl)):
                    current_fl[i] = ''
                
                #if verbose: print('%s %s'%(current_user_cmd, str(current_fl)) )

                result_tup_a = (  current_user_cmd,
                                current_fl[0],
                                current_fl[1],
                                current_fl[2],
                                current_fl[3],
                                current_fl[4],
                                current_fl[5],
                                line_num)
                
                ## first result!!
                ## if verbose: print(result_tup_a)
                flow_paths.append(result_tup_a)

            # the end's
            m_flow_trace_end = re.match(ptrn_flow_trace_end, line)
            if m_flow_trace_end:
                step_name = m_flow_trace_end.group(2)
                depth = int(m_flow_trace_end.group(1))
                
                flow_depths[step_name] = {}
                flow_depths[step_name]['depth'] = depth
                flow_depths[step_name]['line'] = line_num

                current_fl[depth - 1] = step_name

                for i in range(depth,len(current_fl)):
                    current_fl[i] = ''

                result_tup_b = (  current_user_cmd,
                                current_fl[0],
                                current_fl[1],
                                current_fl[2],
                                current_fl[3],
                                current_fl[4],
                                current_fl[5],
                                line_num)
                
                ## first result!!
                ## if verbose: print(result_tup_b)
                flow_paths.append(result_tup_b)
            
                # if verbose: print('%s %s'%(current_user_cmd, str(current_fl)) )

            #################################################################################
            # capturing action deployments
            if not on_action_deploy:
                m_act_dep_start = re.match(ptrn_action_dep_open,line)
                
                if m_act_dep_start:
                    current_step   = m_act_dep_start.group(1)
                    current_action = m_act_dep_start.group(2)
                    on_action_deploy = True

                    action_deployment[current_step] = {}
                    action_deployment[current_step]['action'] = current_action
                    # if verbose: print('%s %s'%(current_step,current_action))
            else:

                if current_action == 'OPTO_STEP_ACTION_TRACE_STATS':
                    m_trace = re.findall(ptrn_trace,line)
                    
                    if m_trace:

                        trace_line = line_num
                        if 'trace' not in action_deployment[current_step]:
                            action_deployment[current_step]['trace'] = {}
                        
                        for metric in m_trace:
                            if (metric[0] != 'trace-stats-cpu') and (metric[0] != 'mem-gb') :
                                action_deployment[current_step]['trace'][metric[0]] = metric[1]

                    #if verbose: print('%s %s %s'%(current_step, ))

                if current_action == 'OPTO_STEP_ACTION_REPORT_CHECKSUM':
                    # check the regex for checksum
                    m_checksum = re.match(ptrn_checksum, line)

                    if m_checksum:
                        checksum_line = line_num
                        action_deployment[current_step]['checksum'] = {}
                        action_deployment[current_step]['checksum']['design'] = m_checksum.group(1)
                        action_deployment[current_step]['checksum']['chksm']  = m_checksum.group(2)

                m_act_dep_close = re.match(ptrn_action_dep_close,line)
                if m_act_dep_close:
                    #if verbose: print(m_act_dep_close)
                    #if verbose: print(action_deployment[current_step]['data'])
                    
                    # not all the steps got checksum
                    if 'checksum' in action_deployment[current_step]:
                        #if verbose: print('%s %s %s'%(current_step, 'checksum',action_deployment[current_step]['checksum']))
                        
                        # store the checksum
                        res_tup = (current_user_cmd,current_step,action_deployment[current_step]['checksum']['design'],action_deployment[current_step]['checksum']['chksm'],checksum_line) 
                        #if verbose: print(res_tup)
                        check_sums.append(res_tup)
                    # not all the steps got trace
                    if 'trace' in action_deployment[current_step]:
                        # if verbose: print('%s %s %s'%(current_step, 'trace',action_deployment[current_step]['trace']))
                        # store trace
                        res_qor_tup = (current_user_cmd,current_step,action_deployment[current_step]['trace'],line_num)
                        # if verbose: print(res_qor_tup)
                        qor_stats.append(res_qor_tup)
                    # this is the end of the action deploy paragraph
                    on_action_deploy = False
            line_num += 1

    return [flow_paths,check_sums,qor_stats]

# look for qor difs and return data per design,
# qor numbers are available, but nobody cares so far,
# however i'll keep it in case of apocalypse.
def qor_diff_summary(**kwargs):

    base_data = kwargs.get('base_data', [[],[],[]])
    flow_data = kwargs.get('flow_data', [[],[],[]])
    design    = kwargs.get('design_name','')

    flow_paths_base = base_data[0]
    flow_paths_flow = flow_data[0]

    checksum_base   = base_data[1]
    checksum_flow   = flow_data[1]

    qor_trace_base  = base_data[2]
    qor_trace_flow  = flow_data[2]
    
    got_qor_diff  = False
    first_diff    = ''
    diff_user_cmd = ''
    diff_step     = ''

    #structure qor_trace*, it's a list of this:
    #('first_compile', 'compile-1 begin ', 
    #   {   'wns': '0.00000', 'tns': '0.00000', 'drc': '20173.67578', 'area': '18.50688', 
    #       'buf-inv': '22846', 'leak-pwr': '0.00000', 'trace-stats-cpu': '0.447932'}, line_num)
    
    # look for comparable lenghts
    len_base = len(qor_trace_base)
    len_flow = len(qor_trace_flow)

    if   len_base < len_flow:
        if verbose: print('\tDifferent amount of steps between runs')
        max_len = len_base
    elif len_base > len_flow:
        if verbose: print('\tDifferent amount of steps between runs')
        max_len = len_flow
    else:
        max_len  = len_base

    for i in range(max_len):
        to_compare_base = (qor_trace_base[i][0],qor_trace_base[i][1],qor_trace_base[i][2])
        to_compare_flow = (qor_trace_flow[i][0],qor_trace_flow[i][1],qor_trace_flow[i][2])

        if to_compare_base != to_compare_flow and not got_qor_diff:
                first_diff    = '\t\tbase: ' + str(qor_trace_base[i]) + '\n\t\tmirror: ' + str(qor_trace_flow[i])
                diff_user_cmd = qor_trace_flow[i][0]
                diff_step     = qor_trace_flow[i][1]
                qor_diff_line = qor_trace_flow[i][3]

                got_qor_diff = True
        
        elif to_compare_base == to_compare_flow  and got_qor_diff:
            first_diff = ''
            got_qor_diff = False

    
    # prepare a dict to further report

    des_diff = {}

    if got_qor_diff:
        # we will look for a steps paths that meets 
        # the difference we've found.

        if verbose: print('\t%s first qor diff at:\n%s'% (design,first_diff))
        if verbose: print('near line %s'% qor_diff_line)
        if verbose: print('\n\tpossible paths to the step:')
    
        possibles = []

        # for path in flow_paths_flow:
            # if verbose: print(path)

        path_id = 0
        for path in flow_paths_flow:
            path_id += 1
            got_step = False
            got_user_cmd = False
            
            for i in range(len(path)):
                # if verbose: print(str(diff_user_cmd).strip(),str(path[i]).strip())
                if not got_user_cmd:
                    got_user_cmd= (str(diff_user_cmd).strip() in str(path[i]).strip())
                #if got_usr_cmd: break
            
            for i in range(len(path)):
                # if verbose: print(str(diff_step).strip(),str(path[i]).strip())
                if not got_step:
                    got_step = (str(diff_step).strip() in str(path[i]).strip())
                #if got_step: break


            if got_user_cmd and got_step:
                # if verbose: print('SUCCESS!!')
                possibles.append(path)
            else:
                pass
                #if verbose: print(got_user_cmd,got_step)

        # use diffstep
        
        des_diff['design'] = design
        des_diff['user_cmd'] = diff_user_cmd
        des_diff['end_step'] = diff_step
        des_diff['line_near'] =  qor_diff_line

        des_diff['path_to_step'] = ''
        des_diff['line_near_step'] = ''
 
        near_line = ''

        if possibles != []:
            path_to = ''
            for _tup in possibles:
                # if verbose: print(_tup)
                new_path = ''

                for i in range(7):
                    if _tup[i] != '':
                        new_path += ' > ' + _tup[i]
                        if (_tup[i].strip() in diff_step.strip()): break
                        
                near_line = _tup[7]

            if new_path != path_to:
                path_to = new_path
                if verbose: print('\t'+ path_to + '. start near line ' + str(near_line))
                des_diff['path_to_step'] = path_to
                des_diff['line_near_step'] =  near_line
        else:
            if verbose: print('\t\tnone found or flow level more than 6.')
            des_diff['path_to_step'] = 'none found or flow level more than 6'
            des_diff['line_near_step'] =  '--'

    
    ######################################################################################################################################    
    ## look for checksum diffs
    got_check_diff  = False
    first_check_diff    = ''
    diff_check_user_cmd = ''
    diff_check_step     = ''


    len_check_base = len(checksum_base)
    len_check_flow = len(checksum_flow)

    if   len_check_base < len_check_flow:
        if verbose: print('\tDifferent amount of steps between runs')
        max_check_len = len_check_base
    elif len_check_base > len_check_flow:
        if verbose: print('\tDifferent amount of steps between runs')
        max_check_len = len_check_flow
    else:
        max_check_len  = len_check_base

    for i in range(max_check_len):
    
        if (str(checksum_base[i][3]) != str(checksum_flow[i][3])) and not got_check_diff:
                first_check_diff    = '\t\tbase: ' + str(checksum_base[i]) + '\n\t\tmirror: ' + str(checksum_flow[i])
                diff_check_user_cmd = checksum_flow[i][0]
                diff_check_step     = checksum_flow[i][1]
                check_diff_line = checksum_flow[i][4]

                got_check_diff = True
        
        if (str(checksum_base[i][3]) == str(checksum_flow[i][3])) and got_check_diff:
            first_check_diff = ''
            got_check_diff = False

    # prepare a dict to further report

    des_diff_check = {}

    if got_check_diff:
        # we will look for a steps paths that meets 
        # the difference we've found.

        if verbose: print('\t%s first checksum diff at:\n%s'% (design,first_check_diff))
        if verbose: print('\tnear line %s'% check_diff_line)
        if verbose: print('\n\tpossible paths to the step:')
    
        possibles_check = []

        # for path in flow_paths_flow:
            # if verbose: print(path)

        path_id = 0
        for path in flow_paths_flow:
            path_id += 1
            got_check_step = False
            got_check_user_cmd = False
            
            for i in range(len(path)):
                # if verbose: print(str(diff_user_cmd).strip(),str(path[i]).strip())
                if not got_check_user_cmd:
                    got_check_user_cmd= (str(diff_check_user_cmd).strip() in str(path[i]).strip())
                #if got_usr_cmd: break
            
            for i in range(len(path)):
                # if verbose: print(str(diff_step).strip(),str(path[i]).strip())
                if not got_check_step:
                    got_check_step = (str(diff_check_step).strip() in str(path[i]).strip())
                #if got_step: break


            if got_check_user_cmd and got_check_step:
                # if verbose: print('SUCCESS!!')
                possibles_check.append(path)
            else:
                pass
                #if verbose: print(got_user_cmd,got_step)

        # use diffstep
        
        des_diff_check['design'] = design
        des_diff_check['user_cmd'] = diff_check_user_cmd
        des_diff_check['end_step'] = diff_check_step
        des_diff_check['line_near'] =  check_diff_line

        des_diff_check['path_to_step'] = ''
        des_diff_check['line_near_step'] = ''
 
        near_check_line = ''

        if possibles_check != []:
            path_to_check = ''
            for _tup in possibles_check:
                # if verbose: print(_tup)
                new_path = ''

                for i in range(7):
                    if _tup[i] != '':
                        new_path += ' > ' + _tup[i]
                        if (_tup[i].strip() in diff_check_step.strip()): break
                        
                near_check_line = _tup[7]

            if new_path != path_to_check:
                path_to_check = new_path
                if verbose: print('\t'+ path_to_check + '. start near line ' + str(near_check_line))
                des_diff_check['path_to_step'] = path_to_check
                des_diff_check['line_near_step'] =  near_check_line
        else:
            # if verbose: print('\tnone found or flow level more than 6.')
            des_diff_check['path_to_step'] = 'none found or flow level more than 6'
            des_diff_check['line_near_step'] =  '--'    

    if not got_check_diff and not got_qor_diff:
        print('\t\tno differences found.')


    return (des_diff,des_diff_check)

# this one doesnt work
def get_divergence(**kwargs):
    base_data = kwargs.get('base_data', [[],[],[]])
    flow_data = kwargs.get('flow_data', [[],[],[]])
    design    = kwargs.get('design_name','')
    
    flow_paths_base = base_data[0]
    flow_paths_flow = flow_data[0]

    ## flow_paths* are lists of this
    # result_tup_b = (  current_user_cmd,
    #                             current_fl[0],
    #                             current_fl[1],
    #                             current_fl[2],
    #                             current_fl[3],
    #                             current_fl[4],
    #                             current_fl[5],
    #                             line_num)

    len_base = len(flow_paths_base)
    len_flow = len(flow_paths_flow)

    if   len_base < len_flow:
        if verbose: print('Different amount of steps between runs')
        max_len = len_base
    elif len_base > len_flow:
        if verbose: print('Different amount of steps between runs')
        max_len = len_flow
    else:
        max_len  = len_base

    diff_index = None
    for i in range(max_len):
        
        base_path = flow_paths_base[i][0:6]
        flow_path = flow_paths_flow[i][0:6]

        prev_path = ''
        diff_path = ''

        got_diff_path = False
        
        if base_path != flow_path and not got_diff_path:
            got_diff_path = True
            diff_index = i
            break

    if got_diff_path:
        print('last equal %s'%flow_paths_base[diff_index -1])
        print('First diff:')
        print('%s\n%s'%(flow_paths_base[diff_index],flow_paths_flow[diff_index]))
    else:
        print('No steps diffs found')

############################################################################################################
# store results
qor_diff = []
# this one contains the checksums and qor diffs
# copy logs and iterate

# keep track of what it's beaing analyzed and what's not
# (design, status)
design_status = []

for design in designs:

    print(design, end = ' ')
    
    design_dir = os.path.join(rundir,baseline,design)
    has_dir = os.path.isdir(design_dir)

    # print(done_file)
    status = ''
    result = ''

    if has_dir:

        done_file = os.path.join(rundir,baseline,design,design + '.all.done')
        all_done   = os.path.isfile(done_file)

        dcopt_done_file = os.path.join(rundir,baseline,design,design+'.dcopt.done')
        dcopt_is_done = os.path.isfile(dcopt_done_file)

        print('\tgathering logfiles...')
        if all_done:
            status = 'all.done'

            log_base = os.path.join(rundir,baseline,design,design+'.dcopt.out.gz')
            log_flow = os.path.join(rundir,flow,design,design+'.dcopt.out.gz')

            try:
                log_base_txt = gzip.open(log_base, 'r').read().decode('utf-8').splitlines()
                log_flow_txt = gzip.open(log_flow, 'r').read().decode('utf-8').splitlines()
            except:
                if verbose: print("not able open text version of the log files. -gz-")
                continue

            base_info = parselog(log=log_base_txt)
            flow_info = parselog(log=log_flow_txt)

            
            print('\tlooking for differences...')
            temp_diff = qor_diff_summary(base_data=base_info, flow_data=flow_info, design_name = design)
            
            if temp_diff != ({},{}) :
                qor_diff.append(qor_diff_summary(base_data=base_info, flow_data=flow_info, design_name = design))
                result = 'nd issue'
            else:
                result = 'pass'

        else:
            status = 'pending'
            
            log_base = os.path.join(rundir,baseline,design,design+'.dcopt.out')
            log_flow = os.path.join(rundir,flow,design,design+'.dcopt.out')

            has_log_base = os.path.isfile(log_base)
            has_log_flow = os.path.isfile(log_flow)

            if dcopt_is_done: 
                status = 'dcopt.done'
                      
            if has_log_base and has_log_flow and not dcopt_is_done:
                status = 'dcopt.running'
            
            if has_log_base and has_log_flow:
                try:
                    log_base_txt = open(log_base, 'r').readlines()
                    log_flow_txt = open(log_flow, 'r').readlines()
                except Exception as e:
                    if verbose: print("not able open text version of the log files.")
                    print(e)
                    continue
    
                # [flow_paths_base, checksum_base, qor_trace_base] = parselog(log=log_base_txt)
                # [flow_paths_flow, checksum_flow, qor_trace_flow] = parselog(log=log_flow_txt)

                base_info = parselog(log=log_base_txt)
                flow_info = parselog(log=log_flow_txt)

                
                print('\tlooking for differences...')
                temp_diff = qor_diff_summary(base_data=base_info, flow_data=flow_info, design_name = design)
                
                if temp_diff != ({},{}) :
                    qor_diff.append(qor_diff_summary(base_data=base_info, flow_data=flow_info, design_name = design))
                    result = 'nd issue'
                else:
                    if status == 'dcopt.running':
                        result = 'pass -partial-'
                    else: 
                        results = 'pass'

            else:
                print('No dc logs found.-yet-')
                result = '--'

        # compute the divergence
        # get_divergence(base_data=base_info, flow_data=base_info, design_name = design)
        # ...this didn't work...

    else:
        status = 'not in flow'

    design_status.append((design, status, result))

        
# print(design_status)

# list of tupples (qor_dict, checksum_diff)
# if any(qor_diff):
#     qor_diff_json = json.dumps(qor_diff)
#     diff_json_f = open('diff_data.js', 'w')
#     diff_json_f.write('var diff_data =%s;'%str(qor_diff_json))
#     diff_json_f.close()

    #pp.pprint(qor_diff)



# ## qor_diff example tupple
# '''
# [ ( { 'design': 'A73_CPU',
#       'end_step': 'abo_pass1-80 end ',
#       'line_near': 1746007,
#       'line_near_step': 1746011,
#       'path_to_step': ' > insert_dft > insert_dft-1 begin > '
#                       'dft_map_tip_insts-1 begin > pass1-80 begin > botup-80 '
#                       'begin > abo_pass1-80 end',
#       'user_cmd': 'insert_dft'},
#     { 'design': 'A73_CPU',
#       'end_step': 'mbm_pack-1 end ',
#       'line_near': 1444443,
#       'line_near_step': 1444445,
#       'path_to_step': ' > first_compile > compile-1 begin > pass2-1 begin > '
#                       'rbo-1 begin > mbm_pack-1 end',
#       'user_cmd': 'first_compile'}),
#   ( { 'design': 'dcp245_SPEEDY28_TOP',
#       'end_step': 'xor_sharing-48 end ',
#       'line_near': 126224,
#       'line_near_step': 126228,
#       'path_to_step': ' > insert_dft > insert_dft-1 begin > '
#                       'dft_map_tip_insts-1 begin > pass1-48 begin > botup-48 '
#                       'begin > xor_sharing-48 end',
#       'user_cmd': 'insert_dft'},
#     { 'design': 'dcp245_SPEEDY28_TOP',
#       'end_step': 'rtl_clock_gating-1 begin ',
#       'line_near': 1599,
#       'line_near_step': 1593,
#       'path_to_step': ' > first_compile > compile-1 begin > rtl_clock_gating-1 '
#                       'begin',
#       'user_cmd': 'first_compile'})]
# '''

# ## make a report
print('making a beautiful html report...')
# ##
check_summary = '''
<table class="w3-table-all">
<tr class=w3-deep-purple>
  <th class="w3-border-left w3-border-right">Design</th>
  <th class="w3-border-left w3-border-right">User Command</th>
  <th class="w3-border-left w3-border-right">Compile Step</th>
  <th class="w3-border-left w3-border-right">Path to the step</th>
  <th class="w3-border-left w3-border-right">Step traced near line</th>
  <th class="w3-border-left w3-border-right">Checksum difference near line</th>
</tr>
'''
qor_summary = '''
<table class="w3-table-all">
<tr class=w3-deep-purple>
  <th class="w3-border-left w3-border-right">Design</th>
  <th class="w3-border-left w3-border-right">User Command</th>
  <th class="w3-border-left w3-border-right">Compile Step</th>
  <th class="w3-border-left w3-border-right">Path to the step</th>
  <th class="w3-border-left w3-border-right">Step traced near line</th>
  <th class="w3-border-left w3-border-right">QoR difference near line</th>
</tr>
'''
# keep track of what it's beaing analyzed and what's not
# design_status = (design, status)
## build design status summary

status_tab =  '''
<table class="w3-table w3-bordered">
<tr class=w3-deep-purple>
    <th class="w3-border-left w3-border-right">Design</th>
    <th class="w3-border-left w3-border-right">Status</th>
    <th class="w3-border-left w3-border-right">Result</th>
</tr>
'''
for i in range(len(design_status)):
    _color_ = ''

    if   design_status[i][2] == 'nd issue'      : _color_ = 'w3-pale-red'
    elif design_status[i][2] == 'pass'          : _color_ = 'w3-pale-green'
    elif design_status[i][2] == 'pass -partial-': _color_ = 'w3-pale-yellow'
    else:
        pass
    
    status_tab += '''
    <tr>
        <td class="w3-border-left w3-border-right">%s</td>
        <td class="w3-border-left w3-border-right">%s</td>
        <td class="w3-border-left w3-border-right %s">%s</td>
    </tr>
    '''%(design_status[i][0],design_status[i][1], _color_, design_status[i][2])

status_tab += '</table>'

got_qor_diff = False
got_chk_diff = False

for tup in qor_diff:

    qor_dict = tup[0]
    check_dict = tup[1]

    if qor_dict != {}:
        qor_summary += '''
        <tr>
            <th class="w3-border-left w3-border-right">%s</td>
            <th class="w3-border-left w3-border-right">%s</td>
            <th class="w3-border-left w3-border-right">%s</td>
            <th class="w3-border-left w3-border-right">%s</td>
            <th class="w3-border-left w3-border-right">%s</td>
            <th class="w3-border-left w3-border-right">%s</td>
        </tr>
        '''%(qor_dict['design'],qor_dict['user_cmd'],qor_dict['end_step'],qor_dict['path_to_step'],qor_dict['line_near_step'],qor_dict['line_near'])
        got_qor_diff = True

    ## watch here
    ## previous was th's
    if check_dict != {}:
        check_summary += '''
        <tr>
            <td class="w3-border-left w3-border-right">%s</td>
            <td class="w3-border-left w3-border-right">%s</td>
            <td class="w3-border-left w3-border-right">%s</td>
            <td class="w3-border-left w3-border-right">%s</td>
            <td class="w3-border-left w3-border-right">%s</td>
            <td class="w3-border-left w3-border-right">%s</td>
        </tr>
        '''%(check_dict['design'],check_dict['user_cmd'],check_dict['end_step'],check_dict['path_to_step'],check_dict['line_near_step'],check_dict['line_near'])
        got_chk_diff = True

qor_summary += '</table>'
check_summary += '</table>'


final_report = '''
<!DOCTYPE html>
<html>
<title>ND Summary</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<link rel="stylesheet" href="https://www.w3schools.com/w3css/4/w3.css">
<body>'''

final_report += '''
<div class="w3-panel w3-padding">
    <h2>Non-Determinism Issues Summary</h2>
    <p>
    <b>Rundir:  </b>%s<br>
    <b>Flow:    </b>%s<br>
    <b>Baseline: </b>%s<br>
    </p>
    <p class= "w3-small"><b>Last update by:</b> %s</p>
</div>'''%(rundir,flow,baseline,datetime.now().strftime('%Y-%m-%d %H:%M:%S'))


final_report +='''
    <div class="w3-container">
    <a href="%s/prs_report.%s.out" class="w3-button w3-deep-purple">PRS Report</a>
    </div>
'''%(result_dir,report_name)


if got_qor_diff:
    final_report += '''
    <div class="w3-panel w3-padding">
        <h3>QoR Differences Summary</h3>
        <p>The following <i>non-back-to-zero</i> QoR differences have been found:</p>
        %s
    </div>'''%qor_summary
else:
    final_report +='''
    <div class="w3-panel w3-padding">
    <h3>QoR Differences Summary</h3>
    <p>No QoR differences have been found.</p>
    </div>'''

if got_chk_diff:
    final_report += '''
    <div class="w3-panel w3-padding">
        <h3>Checksum Differences Summary</h3>
        <p>The following checksum differences have been found:</p>
            %s
    </div>'''%check_summary
else:
    final_report += '''
    <div class="w3-panel w3-padding">
    <h3>Checksum Differences Summary</h3>
    <p>No check differences have been found.</p>
    </div>'''

final_report += '''
<div class="w3-panel w3-padding">
    <h3>Designs List Analysis Summary</h3>
    <p>Full list of designs included in the analysis</p>
    %s
</div>'''%status_tab


final_report+='''
</body>
    <style>
    body {
        transform: scale(0.8);
        transform-origin: 0 0;
        padding-right: 160px;
        padding-left: 160px;
    }

    th {
        font-weight: normal;
    }
    </style>
</html>
'''
# may be for the future
# report_name = "nd_report_%s.html"%flow
report_file_name = 'index.html'
report_path = os.path.join(result_dir,'prs_report.ndsum_%s.out'%report_name)

if not os.path.isdir(report_path):
    os.mkdir(report_path)

report_file = os.path.join(report_path,report_file_name)

nd_report = open(report_file, "w")
nd_report.write(final_report)
nd_report.close()

print('report written to %s  , Thank You!'%report_path)
