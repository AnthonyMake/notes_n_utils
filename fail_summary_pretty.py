import sys, os, re, gzip, subprocess, shutil
import pprint
from jinja2 import Template

pp = pprint.PrettyPrinter(indent = 2)

# prs_dir = '/slowfs/pv_scratch57/24x7/dc/Q-2019.12-SP/RMS/sqs/20200416/r20200416'
# prs_dir = os.getcwd()
# s_dir = '/remote/platform_pv1/24x7/dc/R-2020.09-SP/RMS/culprit_automation/D20201005_20_30/joaquinv_req'

def fail_check_from_cache(report_dir):
    
    prs_dir = report_dir
    
    # print('running at %s'%prs_dir)
    case = None
    # print(prs_dir)
    # first try with prreport.cache -- eeeeasy
    cmd = 'egrep "^Path\s|^Fatal|^Status" %s/prreport.cache'%prs_dir
    cmd_obj = subprocess.run(cmd, executable= '/bin/csh',shell = True,stdout=subprocess.PIPE)
    cmd_ret = cmd_obj.stdout.decode("utf-8").splitlines()
    #print(prs_dir)
    #pp.pprint(cmd_ret)

    if len(cmd_ret) < 2:
        print('Problem reading prrerpot.cache, skipping fail analysis')
        # case = 'design_cache'
        return []
    else:
        case = 'report_cache'
        
    # print(case)
    # second try with cache of each designs,
    # requires clean tool 
    if case == 'design_cache':
        cmd = 'cd %s; egrep "^Fatal|^Status" */*/prreport.cache'%prs_dir
        cmd_obj = subprocess.run(cmd, executable= '/bin/csh',shell = True,stdout=subprocess.PIPE)
        cmd_ret = cmd_obj.stdout.decode("utf-8").splitlines()

    data_dict = {}
    columns = 'flow design'.split(' ')
    table_results = []

    for line in cmd_ret:    
        #print(line)
        data = line.replace('/', ' ').replace(':',' ').replace('prreport.cache', '').split()

        # print(data)

        #continue
        # some silly normalization
        dt_list = [ '', '' , '' , '' , '' ]     
        for i in range(len(data)):
            dt_list[i] = data[i]

        # print(dt_list)
        # flow, design, info_key, info_value = data

        info_key = None
        if dt_list[0] == 'Path': 
            # cache update messed up this
            # some_key, flow, design, info_key, info_value = dt_list
            # print(dt_list)
            some_key, flow, design, np, np = dt_list

        else: 
            # pp.pprint(dt_list)
            info_key, info_value, np, np, np = dt_list

        # grabbing the columns,
        
        if info_key and info_key not in columns: columns.append(info_key)

        # populating the dict
        if flow not in data_dict:
            data_dict[flow]  = {}
        else:
            if design not in data_dict[flow]:
                data_dict[flow][design] = {}
            else:
                if info_key not in data_dict[flow][design]:
                    data_dict[flow][design][info_key] = info_value
                else:
                    pass
    
    for f, f_dict in data_dict.items():
        for d, d_dict in f_dict.items():
            if 'FatalFile' in ' '.join(d_dict.keys()):
                 
                # print(f,d,d_dict)

                logfile = os.path.join(prs_dir,f,d,'%s.%s'%(d,d_dict['FatalFileSuffix']))
                logfile_gz = os.path.join(prs_dir,f,d,'%s.%s.gz'%(d,d_dict['FatalFileSuffix']))
                #print(logfile)

                gz = False
                fatal_log = None
                if os.path.isfile(logfile):
                    #print('exists')
                    ft_file = open(logfile)
                    fatal_log = ft_file.readlines()
                    ft_file.close()

                elif os.path.isfile(logfile_gz):
                    gz = True
                    #print('exists as gz')
                    ft_file = gzip.open(logfile_gz)
                    fatal_log = ft_file.read().decode(encoding='utf-8', errors ='ignore').splitlines()
                    ft_file.close()
                else:
                    print('%s/%s cant file logfiles'%(f,d))
                    continue
                
                if fatal_log:
                    fatal_line = int(d_dict['FatalLN'])
                    fatal_text = fatal_log[fatal_line-1].strip()
                    
                    if ('Error' not in fatal_text) and ('Killed' not in fatal_text):
                        # lookup for a near error
                        lookup = 5
                        if len(fatal_log) > fatal_line+2*lookup:
                            for i in range(fatal_line-lookup, fatal_line+lookup):
                                if  ('Error' in fatal_log[i]) or \
                                    ('The tool has just encountered a fatal error:' in fatal_log[i]) or \
                                    ('Killed' in fatal_log[i]) or \
                                    ('Segmentation fault' in fatal_log[i]):
                                    
                                    if 'Error: 0' in fatal_log[i]:
                                        fatal_text += fatal_log[i]
                                    else:
                                        fatal_text = fatal_log[i]

                    stack_trace = ''
                    just_track_trace = ''

                    for i in range(fatal_line,len(fatal_log)):
                        log_line = fatal_log[i]
                        if 'PV-INFO: Fatal URL =' in log_line:
                            stack_trace = fatal_log[i].split()[5]
                            # just for easy include in html
                            just_track_trace = stack_trace

                    d_dict['FatalText'] = fatal_text

                else:
                    d_dict['FatalText'] = '--'

                st = d_dict.get('Status', '--')
                fle = d_dict.get('FatalFileSuffix', '--')
                ln = d_dict.get('FatalLN', '--')
                txt = d_dict.get('FatalText', '--')

                # print(f,d,st,fle,ln,txt)
                try:
                    disk_u = '%.2fGB' % shutil.disk_usage(os.path.join(prs_dir,f,d))[2]/1024 * 1024 * 1024
                except:
                    disk_u = '--'

                table_results.append({
                    'flow': f,
                    'design': d,
                    'status': st,
                    'fatal_file': fle + '.gz'*gz,
                    'logfile' : logfile + '.gz'*gz,
                    'line': ln,
                    'fatal_text': txt,
                    'disk_avail' : disk_u,
                    'stack_trace' : just_track_trace
                    })


    columns = 'flow design status file line_num fatal_text'.split(' ')
    # pp.pprint(data_dict)
    #report = 'FAIL Detector'
    #report += 
    tab_title = 'Fail Status Summary'
    title = tab_title
    output_file = 'fails_summary'
    
    # pp.pprint(table_results)
    
    return table_results
    # print_html_table_results(tab_title,title,columns,table_results,output_file)


def print_html_table_results(tab_title,title,columns,table_list,output_file):
    template_text = open('/slowfs/dcopt105/vasquez/utils/suite_collectors_dev/v_repo/suite_collectors/table_base.jinja', 'r').read()
    # template_text = open('mean_hist_base.html', 'r').read()
    template = Template(template_text)

    html = template.render(
        tab_title = tab_title,
        title = title,
        columns = columns,
        result_table = table_list,
    )

    html_name = '%s.html'%output_file
    report_file = open(html_name, 'w')
    report_file.write(html)
    report_file.close()
        
# fail_check(prs_dir)





                            # des_dir = health_dict[tool][brnch][suite][nightly][flow][design]['design_disk_usage'][1]
                            # disk_avail = health_dict[tool][brnch][suite][nightly][flow][design]['design_disk_data']['Avail']
                            # disk_name = health_dict[tool][brnch][suite][nightly][flow][design]['design_disk_data']['Mounted']
                            # fatal_line = ''
                            # fatal_file = ''
                            # fatal_text = ''
                            # stack_trace = ''
                            # metric = ''
                            # mean   = ''
                            # value  = ''

                            # just_track_trace = ''
                            # gz = False
                            # try:
                                    
                            #     cache_file = os.path.join(des_dir, 'prreport.cache')
                            #     cache_lines = open(cache_file, 'r').readlines()
                                
                            #     for line in cache_lines:

                            #         line = line.strip().split()

                            #         if 'FatalLN' in line and len(line) == 2:
                            #             fatal_line = int(line[1])

                            #         if 'FatalFile' in line and len(line) == 2:
                            #             fatal_file = line[1]
                                    
                            #     #log_flow_txt = gzip.open(log_flow, 'r').read().decode('utf-8').splitlines()
                            #     fatal_file_loc = des_dir + fatal_file 

                            #     if os.path.exists(fatal_file_loc + '.gz'):
                            #         gz = True
                            #         fatal_log = gzip.open(fatal_file_loc + '.gz').read().decode(encoding='utf-8', errors ='ignore').splitlines()
                            #     else:
                            #         fatal_log = open(fatal_file_loc).readlines()

                                # fatal_text = fatal_log[fatal_line-1].strip()
                                # # print(fatal_text)
                                # if ('Error' not in fatal_text) and ('Killed' not in fatal_text):
                                #     # lookup for a near error
                                
                                #     for i in range(fatal_line-20, fatal_line+20):
                                #         if ('Error' in fatal_log[i]) or ('The tool has just encountered a fatal error:' in fatal_log[i]) or ('Killed' in fatal_log[i]):
                                #             if 'Error: 0' in fatal_log[i]:
                                #                 fatal_text += fatal_log[i]
                                #             else:
                                #                 fatal_text = fatal_log[i]

                            #     stack_trace = ''
                            #     just_track_trace = ''

                            #     for i in range(fatal_line,len(fatal_log)):
                            #         log_line = fatal_log[i]
                            #         if 'PV-INFO: Fatal URL =' in log_line:
                            #             stack_trace = fatal_log[i].split()[5]
                            #             # just for easy include in html
                            #             just_track_trace = stack_trace

                            #     print(des_dir + fatal_file + '.gz', fatal_line, fatal_text)
                            
                            # except:
                            #    print((des_dir, fatal_file, fatal_line, fatal_text), 'couldn\'t get info')
    
