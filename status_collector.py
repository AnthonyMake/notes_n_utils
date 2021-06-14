import sys, os, re, gzip, pickle
from pymongo import MongoClient
sys.path.append('/slowfs/dcopt105/vasquez/utils/suite_collectors_dev/v_repo/suite_collectors')
from health_dict_parallels import create_health_dict
from fail_summary_pretty import fail_check_from_cache
import gc 

import pprint
pp = pprint.PrettyPrinter(indent = 1,depth=4 )


def status_collector(users, root_path, tool, branch, suite, suite_cname,flow, baseline, nightly_max, report,distributed):
    
    user_list = users
    brnch = os.path.join(root_path,branch)
    
    print('\n\nCollecting PRS Status\n')

    health_dict = create_health_dict(
                        os.getcwd(), nightly_max, tool, 
                        brnch, suite, [flow], 
                        user_list, '', distributed)

    short_branch = branch.split('/')[-1]
            
    nightly_amount = 0

    status_dict = {}
    status_dict[branch] = {}
    status_dict[branch][suite] = {}

    for nightly in health_dict[tool][brnch][suite]:

        status_dict[branch][suite][nightly] = {}

        nightly_amount += 1
        n_flows = 0

        if nightly_amount > nightly_max: break              
        
        if not health_dict[tool][brnch][suite][nightly]:
            # del health_dict[tool][brnch][suite][nightly]
            continue 

        for flow in health_dict[tool][brnch][suite][nightly]:
            
            status_dict[branch][suite][nightly][flow] = {}
            
            n_flows += 1 
            # data for daily 
            done    = 0
            failed  = 0
            running = 0
            pending = 0
            n_designs = 0

            # fail_list = []
            pend_list = []
            all_fails = []

            # comment = ''
            # # get comment from QoR Table
            qor_tracking_path = '%s/%s/QoR_tracking/image_data'%(brnch,suite)

            if not os.path.exists(qor_tracking_path):
                if not os.path.exists('%s/%s/QoR_tracking'%(brnch,suite)):
                    os.mkdir('%s/%s/QoR_tracking'%(brnch,suite))
                    os.chmod('%s/%s/QoR_tracking'%(brnch,suite),0o777)
                
                os.mkdir('%s/%s/QoR_tracking/image_data'%(brnch,suite))
                os.chmod('%s/%s/QoR_tracking/image_data'%(brnch,suite), 0o777)

            if not os.path.exists('%s/%s/QoR_tracking/image_data/%s'%(brnch,suite,nightly)):
                os.mkdir('%s/%s/QoR_tracking/image_data/%s'%(brnch,suite,nightly))
                os.chmod('%s/%s/QoR_tracking/image_data/%s'%(brnch,suite,nightly), 0o777)

            comment_path = '%s/%s/QoR_tracking/image_data/%s/comment.%s'%(brnch,suite,nightly,flow)

            # if os.path.exists(comment_path):
            #     try:
            #         comment = open(comment_path, 'r').read()
            #         comment += '<br>\n'
            #     except:
            #         print('cant open comment %s'%comment_path)
            # else:
            #     pass

            # read cache only once
            cache_file = os.path.join(root_path,branch,suite,nightly,'prs/run','rpt_%s'%report, 'prreport.cache')
            if os.path.isfile(cache_file):
                # print('REPORT CACHE FOUND')
                cache_obj = open(cache_file, 'r')
                cache_lines = cache_obj.read().splitlines()
                cache_obj.close()
            else:
                cache_lines = None


                
            for design in health_dict[tool][brnch][suite][nightly][flow]:
                n_designs += 1
                
                job_dict = {}
                job_dict['branch'] = short_branch
                job_dict['suite'] = suite
                job_dict['nightly'] = nightly
                job_dict['flow'] = flow
                job_dict['design'] = design
                job_dict['current_step'] =  health_dict[tool][brnch][suite][nightly][flow][design]['progress_data']['current_step'].split('.')[1]
                
                
                # FAIL_DETECTION:

                for k,v in health_dict[tool][brnch][suite][nightly][flow][design].items():
                    job_dict[k] = v
                
    
                if health_dict[tool][brnch][suite][nightly][flow][design]['all.done'] == 'True': 
                    if 'Fail' in health_dict[tool][brnch][suite][nightly][flow][design]['prreport_status'] \
                        or 'Incmp' in health_dict[tool][brnch][suite][nightly][flow][design]['prreport_status'] \
                        or health_dict[tool][brnch][suite][nightly][flow][design]['prreport_status']== 'PLNoPlc'\
                        or health_dict[tool][brnch][suite][nightly][flow][design]['prreport_status']== '--':

                        # failed += 1    
                        # if '_ex' not in flow:
                        if True:
                            # trying to take a look at the logfiles
                            des_dir = health_dict[tool][brnch][suite][nightly][flow][design]['design_disk_usage'][1]
                            disk_avail = health_dict[tool][brnch][suite][nightly][flow][design]['design_disk_data']['Avail']
                            disk_name = health_dict[tool][brnch][suite][nightly][flow][design]['design_disk_data']['Mounted']
                            fatal_line = ''
                            fatal_file = ''
                            fatal_text = ''
                            stack_trace = ''
                            _status = ''
                            metric = ''
                            mean   = ''
                            value  = ''

                            just_track_trace = ''
                            gz = False

                            # trying new approach to catch fails from reports' cache
                            # cache_file = os.path.join(root_path,branch,suite,nightly,'prs/run','rpt_%s'%report, 'prreport.cache')
                            if cache_lines:
                            #if os.path.isfile(cache_file):
                                # print('REPORT CACHE FOUND')
                                # cache_obj = open(cache_file, 'r')
                                # cache_lines = cache_obj.read().splitlines()
                                # cache_obj.close()

                                on_des = False
                                for line in cache_lines:
                                    line = line.strip().split()

                                    if not on_des and len(line) == 2 \
                                        and 'Path' in line \
                                        and '%s/%s'%(flow,design) in line:

                                        # print('ON DES!!')
                                        on_des = True

                                    if len(line) == 2 and on_des:
                                        if 'Status' in line and len(line) == 2:
                                            _status = line[1]
                                            # updating this
                                            health_dict[tool][brnch][suite][nightly][flow][design]['prreport_status'] = _status
                                            # is the last reported
                                            break

                                        if 'FatalLN' in line and len(line) == 2:
                                            fatal_line = int(line[1])

                                        if 'FatalFile' in line and len(line) == 2:
                                            fatal_file = line[1]

                             


                                ######################################
                                    
                                # cache_file = os.path.join(des_dir, 'prreport.cache')
                                # cache_lines = open(cache_file, 'r').readlines()
                                
                                # for line in cache_lines:

                                #     line = line.strip().split()

                                #     if 'FatalLN' in line and len(line) == 2:
                                #         fatal_line = int(line[1])

                                #     if 'FatalFile' in line and len(line) == 2:
                                #         fatal_file = line[1]
                                    
                                #log_flow_txt = gzip.open(log_flow, 'r').read().decode('utf-8').splitlines()
                                if fatal_file or fatal_line:
                                    fatal_file_loc = des_dir + fatal_file 

                                    if os.path.exists(fatal_file_loc + '.gz'):
                                        gz = True
                                        fatal_log = gzip.open(fatal_file_loc + '.gz').read().decode(encoding='utf-8', errors ='ignore').splitlines()
                                    elif os.path.exists(fatal_file_loc):
                                        try:
                                            fatal_log = open(fatal_file_loc).readlines()
                                        except:
                                            fatal_log = ''
                                    else:
                                        fatal_log = ''

                                    if fatal_log:
                                        try:
                                            fatal_text = fatal_log[fatal_line-1].strip()
                                        except:
                                            fatal_text = 'couldnt read logfile'
                                    else:
                                        fatal_text = "File Error: Logfile not found"
                                    # print(fatal_text)

                                    if ('Error' not in fatal_text) and ('Killed' not in fatal_text):
                                        # lookup for a near error
                                        max_ran = len(fatal_log) if len(fatal_log) < fatal_line+20 else fatal_line+20
                                        min_ran = 0 if fatal_line-20 < 0 else fatal_line -20  
                                    
                                        for i in range(min_ran, max_ran):
                                            if  ('Error' in fatal_log[i]) or \
                                                ('The tool has just encountered a fatal error:' in fatal_log[i]) or \
                                                ('Killed' in fatal_log[i]) or \
                                                ('Segmentation fault' in fatal_log[i]) :
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

                                    print(des_dir + fatal_file + '.gz', fatal_line, fatal_text)
                                    failed += 1
                                    # except:
                                    #    print((des_dir, fatal_file, fatal_line, fatal_text), 'couldn\'t get info')
                            
                                    all_fails.append({
                                        'fatal_file' : fatal_file + '.gz'*gz,
                                        'design'     : design, 
                                        'logfile'    : des_dir + fatal_file + '.gz'*gz, 
                                        'line'       : fatal_line,
                                        'fatal_text' : fatal_text,
                                        'disk_avail' : disk_avail, 'disk_name' : disk_name, 
                                        'status'     : health_dict[tool][brnch][suite][nightly][flow][design]['prreport_status'], 
                                        'stack_trace': just_track_trace,
                                        })

                                else:
                                    done += 1

                            else:
                                print('REPORT CACHE NOT FOUND', cache_file)


                    else : 
                        done += 1

                elif    'monrun_data' not in health_dict[tool][brnch][suite][nightly][flow][design]: 
                    pending += 1
                    pend_list.append(design)
                elif    'monrun_data' in health_dict[tool][brnch][suite][nightly][flow][design]: 
                    running += 1
                    try:
                        job_dict['host']  = health_dict[tool][brnch][suite][nightly][flow][design]['monrun_data']['HOST']
                        job_dict['util']  = health_dict[tool][brnch][suite][nightly][flow][design]['monrun_data']['UTIL']
                        job_dict['hours'] = health_dict[tool][brnch][suite][nightly][flow][design]['monrun_data']['HOURS']
                    except:
                        print('couldnt find some keys in the jobdict')

            # if design == 'dcp607_mpcore' and flow == 'N_SRM_ICC2_spg_opt_area' and nightly == 'D20190423_14_30':
            #     print('DEBUG:!!! %s %s %s'%(design,flow,nightly))
            #     pp.pprint(health_dict[tool][brnch][suite][nightly][flow][design])
                
            # some workarounds to get clearer insights
            
            if n_designs != 0 :
                completion = done/n_designs * 100
                completion = str(int(completion))+'%'
            else:
                completion = '--'

            if 'ex' in flow:
                # is an extra run
                run_type = 'extra'
                extra_total += 1

                if   done == n_designs: extra_dones += 1
                elif running > 0: extra_running += 1
                else: extra_pends += 1
                

            elif re.match(r'^[A-Z]_.+',flow):
                # it's a baseline flow
                run_type = 'baseline'
            
            else:
                # so is a regular run
                run_type = 'regular'
                        
            status_dict[branch][suite][nightly][flow] = {   
                'done'     : done,
                'running'  : running,
                'pending'  : pending,
                'failed'   : failed,
                'n_designs': n_designs,
                'comment_path'  : comment_path,
                'fail_list': all_fails,
            }

    # changing to pkl 
    # lets organize this on pkl_data folders so we can clean up this

    if status_dict:
        if not os.path.exists('pkl_data'):
            os.mkdir('pkl_data') 

        status_pkl_name   = branch + '_' + suite + '_' + report + '_' + baseline + '_status.pkl'
        status_pkl_name   = os.path.join('pkl_data', status_pkl_name)
        file_status   = open(status_pkl_name, 'wb')

        pickle.dump(status_dict, file_status)

        print('\n\tdump status data to ' + status_pkl_name )

        file_status.close()
        
        print('Done!')
                
        return status_pkl_name

    else:
        return None


def status_collector_v2(users, root_path, tool, branch, suite, suite_cname,flow, baseline, nightly_max, report, distributed):
    print('\n\nCollecting PRS Status')
    print('Getting Qstat info...')
    # get data from MongoDB
    client    = MongoClient('pvdc002', 27017)
    dc_db     = client.dcnxt_data
    farm_data = dc_db['farm'].find({})

    snapshots_all = sorted(farm_data, key=lambda i:i['timestamp'])
    last_snapshot = snapshots_all[-1]
    print('\tLast farm snapshot is from %s'%last_snapshot['timestamp'])

    user_list = users
    brnch = os.path.join(root_path,branch)
    
    # we'll not use this
    # health_dict = create_health_dict(
    #                     os.getcwd(), nightly_max, tool, 
    #                     brnch, suite, [flow], 
    #                     user_list, '', distributed)

    # get the nightlys
    suite_path = os.path.join(root_path,branch,suite)
    ng_list = open(os.path.join(suite_path,'images.txt')).read().strip().split()
    # print(ng_list)
    n_count = 0

    status_dict = {}
    status_dict[branch] = {}
    status_dict[branch][suite] = {}
    
    ng_list.reverse()
    for ng in ng_list:
        flow_path = os.path.join(suite_path,ng,'prs/run',flow)
        if not os.path.exists(flow_path):
            continue
        
        status_dict[branch][suite][ng] = {}
        status_dict[branch][suite][ng][flow] = {}

        # get the design list and count
        n_designs = 0
        done      = 0
        pending   = 0
        running   = 0
        failed    = 0
        unknown   = 0
        
        unknown_ls = []
        
        # get the list of fails from cache report
        print('Getting fails from %s rpt_%s'%(ng,report))
        rpt_dir = os.path.join(root_path,branch,suite,ng,'prs/run','rpt_%s'%report)
        cache = os.path.join(rpt_dir,'prreport.cache')
        if os.path.exists(cache):
            fail_ls = fail_check_from_cache(rpt_dir)
            this_flow_fatals = [ft for ft in fail_ls if ft['flow'] == flow]
            this_flow_fatals_names = [ft['design'] for ft in fail_ls if ft['flow'] == flow]
            failed = len(this_flow_fatals)

        else:
            fail_ls = []
            this_flow_fatals = []
            this_flow_fatals_names = []
            failed = 0
        
        # get the list of real designs
        des_list_0 = os.listdir(flow_path)
        for des in des_list_0:
            des_cfg = os.path.join(flow_path,des,'%s.des.cfg'%des)
            if not os.path.exists(des_cfg):
                continue

            n_designs += 1
            # check if fail
            if des in this_flow_fatals_names:
                # already accounted
                continue

            # check if done
            done_file = os.path.join(flow_path,des,'%s.all.done'%des)
            #sprint(done_file)
            if os.path.exists(done_file):
                done += 1
                continue

            # if not done nor fail check the status
            grd_file = os.path.join(flow_path,des,'%s.grd.out'%des)
            if os.path.exists(grd_file):
                g_file  = open(grd_file)
                job_num = g_file.read().strip()
                g_file.close()

                # search for the jb in the last snapshot
                status = [ j['job_state'] for j in last_snapshot['jobs_data'] if j['job_number']==job_num ]

                
                if not status:
                    unknown += 1
                    unknown_ls.append({'design': des, 'issue': 'not_done/not_in_farm'})
                    continue

                elif status[0] in 'r Rr'.split():
                    running += 1
                    continue

                elif status[0] in 'qw Rq'.split():
                    pending += 1
                    continue

            else:
                unknown += 1
                unknown_ls.append({'design': des, 'issue': 'no grd file found'})
                continue
        
        status_dict[branch][suite][ng][flow] = {   
                'done'         : done,
                'running'      : running,
                'pending'      : pending,
                'unknown'      : unknown,
                'unknown_list' : unknown_ls,
                'failed'       : failed,
                'n_designs'    : n_designs,
                'fail_list'    : this_flow_fatals,
            }

        n_count += 1
        if n_count >= nightly_max:
            break

    # changing to pkl 
    # lets organize this on pkl_data folders so we can clean up this
    # pp.pprint(status_dict)

    if status_dict:
        if not os.path.exists('pkl_data'):
            os.mkdir('pkl_data') 

        status_pkl_name   = branch + '_' + suite + '_' + report + '_' + baseline + '_status.pkl'
        status_pkl_name   = os.path.join('pkl_data', status_pkl_name)
        file_status   = open(status_pkl_name, 'wb')

        pickle.dump(status_dict, file_status)

        print('\n\tdump status data to ' + status_pkl_name )

        file_status.close()
        
        del status_dict
        del farm_data
        del last_snapshot
        gc.collect()

        print('Done!')
                
        return status_pkl_name

    else:
        return None

def status_collector_flow(hs_user, target_dir, flow, baseline, report):
    
    print('\n\nCollecting PRS Status')
    print('Getting Qstat info...')
    # get data from MongoDB
    client    = MongoClient('pvdc002', 27017)
    dc_db     = client.dcnxt_data
    farm_data = dc_db['farm'].find({})

    snapshots_all = sorted(farm_data, key=lambda i:i['timestamp'])
    last_snapshot = snapshots_all[-1]
    print('\tLast farm snapshot is from %s'%last_snapshot['timestamp'])

    status_dict = {}
    
    for flw in [flow,baseline]:
        
        flow_path = os.path.join(target_dir,flw)
        if not os.path.exists(flow_path):
            print(flow_path, 'not exists')

        status_dict[flw] = {}

        # get the design list and count
        n_designs = 0
        done      = 0
        pending   = 0
        running   = 0
        failed    = 0
        unknown   = 0
        
        unknown_ls = []
        
        # get the list of fils from cache report
        print('Getting fails from %s'%(report))
        rpt_dir = target_dir
        cache = os.path.join(rpt_dir,'prreport.cache')
        
        if os.path.exists(cache):
            fail_ls = fail_check_from_cache(rpt_dir)
            this_flow_fatals = [ft for ft in fail_ls if ft['flow'] == flow]
            this_flow_fatals_names = [ft['design'] for ft in fail_ls if ft['flow'] == flow]
            failed = len(this_flow_fatals)

        else:
            fail_ls = []
            this_flow_fatals = []
            this_flow_fatals_names = []
            failed = 0
        
        # get the list of real designs
        des_list_0 = os.listdir(flow_path)
        for des in des_list_0:
            #print(des)
            des_cfg = os.path.join(flow_path,des,'%s.des.cfg'%des)
            if not os.path.exists(des_cfg):
                
                continue

            n_designs += 1
            # check if fail
            if des in this_flow_fatals_names:
                # already accounted
                continue

            # check if done
            done_file = os.path.join(flow_path,des,'%s.all.done'%des)
            #sprint(done_file)
            if os.path.exists(done_file):
                
                done += 1
                continue

            # if not done nor fail check the status
            grd_file = os.path.join(flow_path,des,'%s.grd.out'%des)
            if os.path.exists(grd_file):
                g_file  = open(grd_file)
                job_num = g_file.read().strip()
                g_file.close()

                
                # search for the jb in the last snapshot
                status = [ j['job_state'] for j in last_snapshot['jobs_data'] if j['job_number']==job_num ]


                if not status:
                    unknown += 1
                    unknown_ls.append({'design': des, 'issue': 'not_done/not_in_farm'})
                    continue

                elif status[0] in 'r Rr'.split():
                    running += 1
                    continue

                elif status[0] in 'qw Rq'.split():
                    pending += 1
                    continue

            else:
                unknown += 1
                unknown_ls.append({'design': des, 'issue': 'no grd file found'})
                continue
        
        status_dict[flw] = {   
                'done'         : done,
                'running'      : running,
                'pending'      : pending,
                'unknown'      : unknown,
                'unknown_list' : unknown_ls,
                'failed'       : failed,
                'n_designs'    : n_designs,
                'fail_list'    : this_flow_fatals,
            }

    return status_dict

