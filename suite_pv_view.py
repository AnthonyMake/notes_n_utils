import pprint, os, sys, subprocess, json
import pickle
import datetime
from mini_hist import mini_hist
from jinja2 import Template, Environment, FileSystemLoader
from shutil import copyfile

now = datetime.datetime.now()

pp = pprint.PrettyPrinter(indent = 2)

# suite_changes_html.py -vasquez-
# 
# Look for relevant changes for provided pkl files from a suite
# uses both design values and mean values
#
# when used as function, returns the analysis results dict and the html filename 
# 
# usage example
#
# html_title        = 'relevant_changes'
# all_pkl_name      = 'diff.srm_icc2_spg_opt_area_all.pkl'
# means_pkl_name    = 'diff.srm_icc2_spg_opt_area_means.pkl'
# n_designs         = 4
# metrics_selection = {
#                     'DCMvArea' : 0.3,
#                     'DCWNS': 0.3,
#                     'DCTNSPMT': 1,
#                     'CLKDCAllOpt' : 0.4,
#                     'DCStdCelTotPow' : 0.3,
#                     'DCMem' : 0.1
#                     }
#
# suite_changes_html(html_title, all_pkl_name, means_pkl_name, metrics_selection, n_designs)
#

def analyze_qor(suite_means, suite_all,des_numeric_values,metrics_selection,flow,n_designs, histograms):
  special_formula_cases = 'CLKDCAllOpt CPUDCAllOpt'
  max_outliers = 500

  result = {}
  
  for nightly in suite_means :

      result[nightly] = []
      if nightly not in des_numeric_values:
        continue

      for report in suite_means[nightly]:
          for metric in metrics_selection:
              if metric in suite_means[nightly][report]:
                  if suite_means[nightly][report][metric] != '--':
                      current_mean = float(suite_means[nightly][report][metric])
                  
                      # look if the metric is out of threshold
                      # if  abs(current_mean) > metrics_selection[metric][0]:
                      if 0:
                        # then we sort this
                        # clean NaN values before sorting
                        cleanList = []
                        for design in suite_all[nightly][report][metric]:
                            
                            current_design_value = suite_all[nightly][report][metric][design]

                            if current_design_value != '--':
                                cleanList.append((design,float(current_design_value)))
                        
                        # sort designs from min to max
                        sor = sorted(cleanList, key=lambda x: x[1])
                        #print(nightly+' '+report+' '+metric)
                        #print(sor)
                        #if  k > (len(sor) - 1):
                        #    k = len(sor) - 1

                        best = sor[0:n_designs] # the first k designs tuples (design,value)
                        lenSor=len(sor)
                        worst = sor[lenSor-n_designs:lenSor] # last k designs tuples (design,value)

                        #turn best list to dict
                        bestDict = {}
                        for design in best:
                            bestDict[design[0]] = design[1]
                        # turn worst list to dict
                        worstDict = {}
                        for design in worst:
                            worstDict[design[0]] = design[1]
                        
                        #result[nightly][report][metric]['mean'] = suite_means[nightly][report][metric] 
                        des_to_append = worstDict if current_mean > 0 else bestDict
                        tp = 'mean degrad.' if current_mean >0 else 'mean improv.'
                        
                        for dsg in des_to_append:
                          # print('THIS LEN', len(des_to_append))
                          # exit()
                          if dsg in des_numeric_values[nightly][flow]:
                            
                            # workaround for strange names
                            if metric not in des_numeric_values[nightly][flow][dsg]:
                              print('\t\tcant find numeric data for', metric)
                              print('\t\ttrying something else...')

                              # if metric in special_formula_cases:
                              #   for m in des_numeric_values[nightly][flow][dsg].keys():
                              #     if metric in m:
                              #       metric = m 

                            try:
                              base_val = des_numeric_values[nightly][flow][dsg][metric]['base_val'] # if metric in des_numeric_values[nightly][flow][dsg] else '--'
                              flow_val = des_numeric_values[nightly][flow][dsg][metric]['flow_val'] # if metric in des_numeric_values[nightly][flow][dsg] else '--'
                            except: 
                              print('\t\tcant find numeric data for', metric)
                              base_val = '--'
                              flow_val = '--'
                          else:
                            base_val = '--'
                            flow_val = '--'
                          
                          result[nightly].append({
                            'Metric': metric.split('_')[0],
                            'Design': dsg,
                            'Mean Value %' : current_mean,
                            'Design Value %': des_to_append[dsg],
                            'Histogram Location': histograms[nightly][flow][metric] if metric in histograms[nightly][flow] else None,
                            'Numeric Value Base' : base_val,
                            'Numeric Value Flow' : flow_val,
                            'Issue Type': tp,
                          })

                      #else:
                      if 1:
                        # store outliers on both sides and sort
                        des_deg = []
                        des_imp = []

                        for design in des_numeric_values[nightly][flow]:
                          if metric in des_numeric_values[nightly][flow][design]:
                            des_val = des_numeric_values[nightly][flow][design][metric]['diff_percent']
                            if des_val and des_val != '--':
                              if des_val > metrics_selection[metric][1]:
                                des_deg.append((design,des_val))

                              elif des_val < -1*metrics_selection[metric][1]:
                                des_imp.append((design,des_val))

                        # sort the lists
                        deg_srtd = sorted(des_deg, key=lambda x: x[1]) if des_deg else []
                        deg_srtd.reverse()

                        imp_srtd = sorted(des_imp, key=lambda x: x[1]) if des_imp else []

                        max_deg = max_outliers if len(deg_srtd) >= max_outliers else len(deg_srtd)
                        max_imp = max_outliers if len(imp_srtd) >= max_outliers else len(imp_srtd)

                        for i in range(max_deg):
                          tp = 'outlier degrad.'
                            
                          if metric in special_formula_cases:
                            for m in des_numeric_values[nightly][flow][deg_srtd[i][0]].keys():
                              if metric in m:
                                metric = m

                          try:
                            base_val = des_numeric_values[nightly][flow][deg_srtd[i][0]][metric]['base_val'] if metric in des_numeric_values[nightly][flow][deg_srtd[i][0]] else '--'
                            flow_val = des_numeric_values[nightly][flow][deg_srtd[i][0]][metric]['flow_val'] if metric in des_numeric_values[nightly][flow][deg_srtd[i][0]] else '--'
                          except:
                            print('\t\tcant find numeric data for', metric)
                            base_val = '--'
                            flow_val = '--'

                          # last check for numeric difference
                          # help to avoid runtime paranoid values
                          sub_metric = metric.split('_')[0]
                          print('evaluating numdiff')
                          if len(metrics_selection[sub_metric]) == 3:
                            try:
                              num_diff = float(base_val) -float(flow_val)
                              print("evaluating %s difference"%metric, num_diff)
                              if abs(num_diff) < metrics_selection[sub_metric][2]:
                                # values are in range so,
                                continue
                            except:
                              print('counldn\'t avaluate numerical diffrence')
                          
                          result[nightly].append({
                            'Metric': metric.split('_')[0],
                            'Design'      : deg_srtd[i][0],
                            'Mean Value %' : current_mean,
                            'Design Value %': deg_srtd[i][1],
                            'Histogram Location' : histograms[nightly][flow][metric] if metric in histograms[nightly][flow] else None,
                            'Numeric Value Base' : base_val,
                            'Numeric Value Flow' : flow_val,
                            'Issue Type'     : tp, #outlier or mean improv or degrad#
                          })                      

                        for i in range(max_imp):
                          tp = 'outlier improv.'
                            
                          if metric in special_formula_cases:
                            for m in des_numeric_values[nightly][flow][imp_srtd[i][0]].keys():
                              if metric in m:
                                metric = m

                          try:
                            base_val = des_numeric_values[nightly][flow][imp_srtd[i][0]][metric]['base_val'] if metric in des_numeric_values[nightly][flow][imp_srtd[i][0]] else '--'
                            flow_val = des_numeric_values[nightly][flow][imp_srtd[i][0]][metric]['flow_val'] if metric in des_numeric_values[nightly][flow][imp_srtd[i][0]] else '--'
                          except:
                            print('\t\tcant find numeric data for', metric)
                            
                            base_val = '--'
                            flow_val = '--'
                          
                          if 'degrad' in tp:
                            result[nightly].append({
                              'Metric': metric.split('_')[0],
                              'Design'      : imp_srtd[i][0],
                              'Mean Value %' : current_mean,
                              'Design Value %': imp_srtd[i][1],
                              'Histogram Location' : histograms[nightly][flow][metric] if metric in histograms[nightly][flow] else None,
                              'Numeric Value Base' : base_val,
                              'Numeric Value Flow' : flow_val,
                              'Issue Type'     : tp, #outlier or mean improv or degrad#
                            })  

  # pp.pprint(result)
                             
  return result
  # the analysis ends here
  #####################################################################

def prepare_culprits(result_qor, prs_status, root_path, branch, suite, flow, ng_execs, cl_execs, _24x7_info, shell):
  
  ng_list = open(os.path.join(root_path,branch,suite,'images.txt'), 'rb').read().decode('UTF-8').splitlines()
  
  culprits = {}
  # 'metric': metric.split('_')[0],
  # 'mean_val' : current_mean,
  # 'des': dsg,
  # 'perc_diff': des_to_append[dsg],
  # 'base_val' : base_val,
  # 'flow_val' : flow_val,
  # 'type': tp,
  
  for nightly in result_qor:

    print(nightly)
    status = ''
    
    en_nightly = nightly
    ng_index = ng_list.index(nightly)

    prev_flow = os.path.join(root_path,branch,suite,en_nightly,'prs/run','%s_prev'%flow)
    if os.path.exists(prev_flow):
      print('getting start nightly from prev flow. Yay!')
      st_nightly = os.readlink(prev_flow).split('/')[-4]
    else:
      st_nightly = ng_list[ng_index - 1] # we should look for prev flow instead


    
    ## getting real images
    end_stp_file = os.path.join(root_path,branch,suite,en_nightly, 'setup')
    if not os.path.exists(end_stp_file): continue

    end_setup = open(end_stp_file)
    
    for l in end_setup.readlines():
      if 'image_dir' in l.split():
        end_nightly = l.split()[2].split('/')[-1]
    end_setup.close()

    st_stp_file = os.path.join(root_path,branch,suite,st_nightly, 'setup')
    if not os.path.exists(st_stp_file): continue

    start_setup = open(st_stp_file)
    for l in start_setup.readlines():
      if 'image_dir' in l.split():
        start_nightly = l.split()[2].split('/')[-1]
    start_setup.close()

    # # get nightly of _prev flow 
    # culprits[nightly] = ('','')

    # # this could be improved
    # prev_dir = os.path.join(root_path,branch,suite,nightly, 'prs/run', '%s_prev'%flow)
    # if os.path.exists(prev_dir):
    #   prev_nightly = os.readlink(prev_dir).split('/')[-4]
    #   if prev_nightly in ng_list:
    #       start_nightly =  prev_nightly 
    #   else:
    #     print('previous flow %s_prev is not an official nightly image -on images.txt-'%flow)
    #     # return '#','prev flow not found'
    #     culprits[nightly]  = ('#', 'prev flow not found')
    #     continue

    # else:
    #   print('previous flow %s_prev is not an official nightly image -on images.txt-'%flow)
    #   # return '#','prev flow not found'
    #   culprits[nightly]  = ('#', 'prev flow not found')
    #   continue

    comment = ''
    culprit_comment = ''
    culprit_des = [] 
    n_for_culprit = 3

    designs = {}
    designs_degrad = {}
    # designs_improv = {}

    # issues_sum = '## Designs with issues'
    # degrad_sum = '\n## degraded designs'
    # improv_sum = '\n## improved designs'

    # qor issues
    qor_issues = True
    
    print('iterating the Qoqr issues')
    if nightly in result_qor: 
      # pp.pprint(result_qor[nightly])
      for issue in result_qor[nightly]:  

        # comment += '## ' + str(issue) + '\n'

        # accounting issues in designs 
        if issue['Design'] not in designs:
          designs[issue['Design']] = 1
        else:
          designs[issue['Design']] += 1

        # separated counts for improvements and degradations.
        # we aare not counting the imporvements anymore since nobody cares
        # if 'improv' in issue['Issue Type']:
        #   if issue['Design'] not in designs_improv:
        #     designs_improv[issue['Design']] = 1
        #   else:
        #     designs_improv[issue['Design']] += 1

        # if 'degrad' in issue['Issue Type']:
        #   if issue['Design'] not in designs_degrad:
        #     designs_degrad[issue['Design']] = {} 
        #   else:
        #     designs_degrad[issue['Design']] += 1
        
        if 'degrad' in issue['Issue Type']:
          if issue['Design'] not in designs_degrad:
            designs_degrad[issue['Design']] = {}
            designs_degrad[issue['Design']]['count'] = 1
            designs_degrad[issue['Design']]['changes'] = [(issue['Metric'],issue['Design Value %'])] 
          else:
            designs_degrad[issue['Design']]['count'] += 1
            designs_degrad[issue['Design']]['changes'].append((issue['Metric'],issue['Design Value %']))
        
    else: 
      qor_issues = False

    # fails 
    print('analyzing fails')
    fails = False

    comment += '## Fatals summary\n'
    culprit_fail_comment = ''
    complete_ratio = 0

    if nightly in  prs_status[branch][suite]:
      if flow in prs_status[branch][suite][nightly]:
        #complete_ratio = (prs_status[branch][suite][nightly][flow]['failed'] + prs_status[branch][suite][nightly][flow]['done'])/prs_status[branch][suite][nightly][flow]['n_designs']
        #print(complete_ratio)
        try:
          complete_ratio = (prs_status[branch][suite][nightly][flow]['failed'] + prs_status[branch][suite][nightly][flow]['done'])/prs_status[branch][suite][nightly][flow]['n_designs']
        except:
          pass
          
        if 'fail_list' in prs_status[branch][suite][nightly][flow] and prs_status[branch][suite][nightly][flow]['fail_list']:
          fails = True
          for f in prs_status[branch][suite][nightly][flow]['fail_list']:
            comment += '## %s:%s: %s\n'%(
                f['fatal_file'],
                f['line'],
                f['fatal_text']
              )

            culprit_fail_comment += '<br>-Fail need review %s:%s: %s\n'%(
                f['fatal_file'],
                f['line'],
                f['fatal_text']
              )
            
            comment += '## %s\n\n'%f['logfile']
            # if f['design'] not in designs:
            #    designs[f['design']] = 1
      else:
        fails = False
    else:
      fails = False

    if not designs:
      #skips the whole thing
      continue
    else:
      comment += '\n## QoR issues summary'

      print('summarizing....')
      nmax = 10
      comment += '\n## Top %s Most degraded designs summary\n'%str(nmax)
      n=0

      des_sort = []
      for des in designs_degrad:
        des_sort.append((des,designs_degrad[des]['count']))

      des_sort = sorted(des_sort, key = lambda x: x[1], reverse = True)


      metric_focus = {}
      is_rt_needed = False

      for des in des_sort:
        comment += '## %s %s metrics /'%(des[0],des[1])
        
        # for comment in the QoR table
        if len(culprit_des) < n_for_culprit:
          culprit_des.append(des[0])
          culprit_comment += '\n<br>-%s: '%des[0]
          for change in designs_degrad[des[0]]['changes']:
            culprit_comment += ' %s: %s / '%(change[0],change[1])
            if ('CPU' in change[0]) or ('CLK' in change[0]):
              is_rt_needed = True

          # culprit_comment += '\n'
          
        # comment += '## '
        for change in designs_degrad[des[0]]['changes']:
          comment += ' %s: %s / '%(change[0],change[1])
          if change[0] in metric_focus:
            metric_focus[change[0]] += 1
          else:
            metric_focus[change[0]] = 1

        comment += '\n'

        n += 1
        if n > nmax:
          comment += '## ...\n'
          break

      # metric_focus = sorted(metric_focus.items(), key = lambda x: x[1], reverse = True)
      
      comment += '## Metrics Summary\n'
      comment += '## '
      for m,c in sorted(metric_focus.items(), key = lambda x: x[1], reverse = True):
        comment += ' %s: %s / '%(m,c)
      comment += '\n'
      
      # will not count the impros anymore, yup... apocalyptical times
      # comment += '\n\n## improvements sum'
      # n=0
      # for k, v in sorted(designs_improv.items(), key=lambda item: item[1], reverse = True):
      #   comment += '\n## %s: \t%s'%(k,v)
      #   n += 1
      #   if n > 5:
      #     comment += '\n## ...'
      #     break
      # comment += '## Candidate Coincidence\n'
      # comment += '## %s\n \n'%(str(designs))
    have_cls = False

    tg_propts = os.path.join(root_path,branch,suite,nightly,'prs/run/propts.cfg')

    if (start_nightly and os.path.exists(os.path.join(ng_execs,start_nightly)))\
      and (end_nightly and os.path.exists(os.path.join(ng_execs,end_nightly))):
  
      print(os.path.join(ng_execs,start_nightly))
      print(start_nightly)
      print('#########################')
      start_cl  = os.readlink(os.path.join(ng_execs,start_nightly)).split('/')[-2].split('_')[1]
      end_cl    = os.readlink(os.path.join(ng_execs,end_nightly)).split('/')[-2].split('_')[1]
      cl_ls     = get_cl_ls(cl_execs,start_cl,end_cl)  
      tg_propts = os.path.join(root_path,branch,suite,nightly,'prs/run/propts.cfg')
      have_cls = True

    else:
      have_cls = False
      msg = '\t\tcouldn\'t get cls asociated to %s or %s'%(start_nightly,end_nightly)
      print(msg)
      culprits[nightly] = ('#',msg)
      # continue  

    # dealing with 24x7 disks
    dsk_root = '/remote/pv/24x7'    
    dsk_tool, dsk_branch, dsk_sub, dsk_proj = _24x7_info.split('/')    
    dsk_run_ng_dir = os.path.join(dsk_root,_24x7_info, nightly)
    
    # linking to rpt nightly dir
    ng_dir_ln = os.path.join(root_path,branch,suite,nightly,'culprit_automation')
    if not os.path.lexists(ng_dir_ln):
      os.symlink(dsk_run_ng_dir,ng_dir_ln)

    if os.path.isdir(dsk_run_ng_dir):

      dsk_run_fl_dir = os.path.join(dsk_run_ng_dir,flow)
      if not os.path.isdir(dsk_run_fl_dir):
        print('\t\tcreated dir for %s/%s in 24x7'%(nightly,flow))
        os.mkdir(dsk_run_fl_dir)  
      tg_dir = dsk_run_fl_dir
    
    else:
      # ask for 24x7 space ufff...
      print('\t\trequesting 24x7 disk space...')
      cmd = '/u/szhang/pv/bin/pone 24x7 mkdir "%s" "%s/%s/%s" "%s"'%(nightly,dsk_tool,dsk_sub,dsk_proj,dsk_branch)
      cmd_obj = subprocess.run(cmd, executable= '/bin/csh',shell = True,stdout=subprocess.PIPE)
      cmd_ret = cmd_obj.stdout.decode("utf-8")

      # testing if it works
      if os.path.isdir(dsk_run_ng_dir):
      
        print('\t\t24x7 space allocated.')
        dsk_run_fl_dir = os.path.join(dsk_run_ng_dir,flow)
        os.mkdir(dsk_run_fl_dir)
        tg_dir = dsk_run_fl_dir
        print('\t\tcreated dir for %s/%s in 24x7'%(nightly,flow))
      
      else:

        print('24x7 space was not created.')
        status = 'fail to allocate 24x7 space for culprit'

    # drawing cl page
    # doesnt if it already exists -time consuming-

    if have_cls and not os.path.exists(os.path.join(tg_dir,'cl_list.html')):
      cl_page = render_cl_page(cl_ls, os.path.join(ng_dir_ln,flow), 'cl_list', branch, st_nightly, end_nightly)
    else:
      print('Skipping creation of CL list, it\'s already there, or nightly names are tricky')
    
    # drawing a culprit cfg
    print('Writing propts.cfg for culprit')
    template_file = '/slowfs/dcopt105/vasquez/utils/suite_collectors_dev/v_repo/suite_collectors/culprit_cfg.jinja'
    env = Environment(loader=FileSystemLoader('/'))
    culprit_template = env.get_template(template_file)

    culprit_script = culprit_template.render({
      'tg_propts'     : tg_propts,
      'tg_dir'        : tg_dir,
      'suite_run_dir' : os.path.join(root_path,branch,suite),
      'ng_execs'      : ng_execs,
      'root_path'     : os.path.join(ng_execs,nightly),
      'start_nightly' : start_nightly,
      'end_nightly'   : end_nightly,
      'shell'         : shell,
      'flow'          : flow,
      'designs'       : ' '.join(culprit_des),
      # 'designs'       : ' '.join([*designs]),
      'comment'       : comment,
      'cls_execs_dir' :  cl_execs,
      'QTab_comment'  : culprit_comment + culprit_fail_comment,
      'rt_accurate'   : is_rt_needed
    })

    if 1:

      try:
        culprit_script_file = open('%s/culprit.py'%tg_dir, 'w')
        culprit_script_file.write(culprit_script)
        culprit_script_file.close()

        # skip it if already launched
        # not sure if this belongs here...
        ack_file = os.path.join(tg_dir,'culprit.launched')
        grd_file = os.path.join(tg_dir,'grd.jobs')

        if os.path.isfile(ack_file) or os.path.isfile(grd_file):
          print('\t\tCulprit was already kicked-off')
          status = 'launched'
        else:
          status = 'Ready to run'

      except:
        print('Not hable to write culprit script at %s'%tg_dir)
        status = 'unable to write culprit script'

    if status == 'Ready to run' and complete_ratio > 0.8:
      # EXPERIMENTAL
      try:
        print('EXPERIMENTAL: KICKING OFF THE CULPRIT :O')
        # cmd = 'cd %s; /slowfs/dcopt105/vasquez/cnda/Conda/bin/python culprit.py; /remote/dtdata1/testdata/prs/syn/scripts/nightly/run_scripts/run_prs_gala-icc2.csh'%tg_dir
        cmd = 'cd %s; /slowfs/dcopt105/vasquez/cnda/Conda/bin/python culprit.py'%tg_dir
        print(cmd)
        # os.system(cmd)

        if os.path.isfile(ack_file) or os.path.isfile(grd_file):
          print('\t\tCulprit has been kicked-off; Yay!!')
          status = 'launched'

      except:
        pass
    else:
      print('Still not ready for culprit, completion is %s'%str(complete_ratio))
      
    # except:
    #   status = 'Cannot write script'

    cp_link = os.path.join(ng_dir_ln,flow)
    

    culprits[nightly] = (cp_link,status)
  
  return culprits

def get_cl_ls(cl_execs_dir, start_cl, end_cl):

  cl_ls = []
  cl_culprit = []
  if os.path.isdir(cl_execs_dir):
    cl_ls = sorted(os.listdir(cl_execs_dir))
  else:
    print('\t\tCan\'t access to CL\'s directory %s'%cl_execs_dir)

  if cl_ls:
    for cl in cl_ls:
      try: cl_num = int(cl.split('_')[1])
      except: continue

      if cl_num >= int(start_cl) and cl_num <= int(end_cl):
        cl_culprit.append(cl)
  else:
    return []

  if cl_culprit:
    return cl_culprit
  else:
    print('Couln\'t find especified cl\'s %s and %s in dir %s'%(start_cl, end_cl, cl_execs_dir))
    return None

def write_culprit_cfg(culprit_dict):
    # for make_Extra utiliy]
    sys.path.append('/slowfs/dcopt105/vasquez/utils/e_run_utils')
    from extra_hpd_functions import make_extra, report_local
    
    
    target_dir    = culprit_dict.get('target_dir')
    debug         = culprit_dict.get('debug', False)
    start_date    = culprit_dict.get('start')
    end_date      = culprit_dict.get('end')
    flow          = culprit_dict.get('flow')
    shell         = culprit_dict.get('shell', 'dcnxt_shell')
    _designs      = culprit_dict.get('designs', '')
    stages        = culprit_dict.get('stages', 'DC ICC2')
    target_propts = culprit_dict.get('target_propts')
    comments      = culprit_dict.get('comment')
    cl_list       = culprit_dict.get('cl_list')
    cl_execs      = culprit_dict.get('cls_execs_dir')
    root_path     = culprit_dict.get('root_path')
    ng_execs      = culprit_dict.get('ng_execs')
    rt_accurate   = culprit_dict.get('rt_accurate', False)

    new_propts = '%s/prs_propts.cfg'%target_dir

    if not cl_list:
      return 'Couldn\'t find valid CL\'s'

    # skip everything if was already launched
    ack_file = os.path.join(target_dir,'culprit.launched')
    grd_file = os.path.join(target_dir,'grd.jobs')
    if os.path.isfile(ack_file) or os.path.isfile(grd_file):
      print('\t\tCulprit was already kicked-off')
      return 'launched'

    try :
      copyfile(target_propts, new_propts)
    except:
      print('Couldn\'t make the copy of nightly propts %s'%target_propts)
      return 'Couldn\'t make the copy of nightly propts'
    
    # ack_file = os.path.join(target_dir,'culprit.launched')
    # if os.path.isfile(ack_file):
    #   print('\t\tCulprit was already kicked-off')
    #   return 'launched'

    cl_bin_dict = {}

    for cl in cl_list:
      cl_num = cl.split('_')[1]
      cl_owner = cl.split('_')[2]
      cl_name = '%s_%s'%(cl_num,cl_owner)
      # cl_name = '_'.join(cl.split('_')[1:2])
      cl_bin_dict[cl_name] = os.path.join(cl_execs,cl)
    
    fl_ls = []
    ds_ls = []
        
    for cl_name,cl_bin in cl_bin_dict.items():

        suffix = '_%s'%(cl_name)
        title  = '<a href="http://clearcase/%s/cl_list.html#%s">%s</a>'%(target_dir,cl_name,cl_name)
        extra  = ''
        raw    = ''
        stages = stages
        dc_bin = '%s/snps/synopsys/bin/%s -r %s'%(cl_bin, shell, root_path)
        icc2_bin = ''
        fm_bin = ''
        fm_flow = ''
        designs = ' '.join(_designs)
        propts = new_propts
        debug = debug
        fm_extra_settings = ''

        flow_name, orig_des = make_extra(
            flow, suffix, title, extra, raw, stages, dc_bin, icc2_bin, fm_bin, fm_flow, designs, propts, debug, fm_extra_settings
        )

        fl_ls.append(flow_name)

    # adding nightly runs to replicate the issue.
    # start nightly
    suffix = '_%s'%(start_date)
    title  = start_date
    extra  = ''
    raw    = ''
    stages = stages
    dc_bin = '%s/%s/bin/%s'%(ng_execs,start_date,shell)
    icc2_bin = ''
    fm_bin = ''
    fm_flow = ''
    designs = ' '.join(_designs)
    propts = new_propts
    debug = debug
    fm_extra_settings = ''

    flow_name, orig_des = make_extra(
        flow, suffix, title, extra, raw, stages, dc_bin, icc2_bin, fm_bin, fm_flow, designs, propts, debug, fm_extra_settings
    )

    fl_ls.append(flow_name)

  # end nightly
    suffix = '_%s'%(end_date)
    title  = end_date
    extra  = ''
    raw    = ''
    stages = stages
    dc_bin = '%s/%s/bin/%s'%(ng_execs,end_date,shell)
    icc2_bin = ''
    fm_bin = ''
    fm_flow = ''
    designs = ' '.join(_designs)
    propts = new_propts
    debug = debug
    fm_extra_settings = ''

    flow_name, orig_des = make_extra(
        flow, suffix, title, extra, raw, stages, dc_bin, icc2_bin, fm_bin, fm_flow, designs, propts, debug, fm_extra_settings
    )

    fl_ls.append(flow_name)


    # just catching some particular error
    # due to corrupted propts
    # no time for fancy stuff
    try:
      ffffs = 'flows: %s\n\n'%' '.join(fl_ls)
    except:
      return 'unable to get flow def'
    
    # make propts for Kick-off
    kick_propts  = 'INCLUDE %s\n\n'%new_propts
    kick_propts += '## comment below line for runtime accuracy\n'
    # kick_propts += 'INCLUDE /remote/pv/repo/dcnt/dcrt_prs_lib/gala_memusage_4c.cfg\n'
    if rt_accurate:
      kick_propts += '# INCLUDE /remote/pv/repo/dcnt/dcrt_prs_lib/gala_memusage_4c.cfg\n'
      kick_propts += '# THIS CULPRIT IS RUNTIME ACCURATE - uncomment above ans rerun for no-rt\n'
    else:
      kick_propts += 'INCLUDE /remote/pv/repo/dcnt/dcrt_prs_lib/gala_memusage_4c.cfg\n'

    kick_propts += comments + '\n'
    kick_propts += 'flows:\n'
    for ff in fl_ls:
      kick_propts += ':: %s\n'%ff

    kick_propts += '\ndesigns: %s\n'%' '.join(_designs)

    if not debug:
        propts_kick_file = open('%s/propts.cfg'%target_dir, 'w')
        propts_kick_file.write(kick_propts)
        propts_kick_file.close()

        report_local(fl_ls, _designs, target_dir, '%s_%s'%(flow,start_date))

    print('\t\tCulprit propts written at %s'%target_dir)

    return 'ready to launch'

def write_culprit_propts(culprit_dict):
    
    # for make_Extra utiliy
    sys.path.append('/slowfs/dcopt105/vasquez/utils/e_run_utils')
    from extra_hpd_functions import make_extra, report_local
    
    target_dir    = culprit_dict.get('target_dir')
    debug         = culprit_dict.get('debug', False)
    start_date    = culprit_dict.get('start_nightly')
    end_date      = culprit_dict.get('end_nightly')
    flow          = culprit_dict.get('flow')
    shell         = culprit_dict.get('shell', 'dcnxt_shell')
    _designs      = culprit_dict.get('designs', '').split()
    stages        = culprit_dict.get('stages', 'DC ICC2')
    target_propts = culprit_dict.get('target_propts')
    comments      = culprit_dict.get('comment')
    suite_run_dir = culprit_dict.get('suite_run_dir')
    # cl_list       = culprit_dict.get('cl_list')
    cl_execs      = culprit_dict.get('cls_execs_dir')
    root_path     = culprit_dict.get('root_path')
    ng_execs      = culprit_dict.get('ng_execs')
    QTab_comment  = culprit_dict.get('QTab_comment', '')
    rt_accurate   = culprit_dict.get('rt_accurate', False)

    start_cl      = os.readlink(os.path.join(ng_execs,start_date)).split('/')[-2].split('_')[1]
    end_cl        = os.readlink(os.path.join(ng_execs,end_date)).split('/')[-2].split('_')[1]

    cl_list       = get_cl_ls(cl_execs,start_cl,end_cl)

    new_propts = '%s/prs_propts.cfg'%target_dir

    if not cl_list:
      return 'Couldn\'t find valid CL\'s'

    # skip everything if was already launched
    # ack_file = os.path.join(target_dir,'culprit.launched')
    # grd_file = os.path.join(target_dir,'grd.jobs')
    # if os.path.isfile(ack_file) or os.path.isfile(grd_file):
    #   print('\t\tCulprit was already kicked-off')
    #   return 'launched'

    try :
      copyfile(target_propts, new_propts)

    except:
      print('Couldn\'t make the copy of nightly propts %s'%target_propts)
      return 'Couldn\'t make the copy of nightly propts'
    
    # ack_file = os.path.join(target_dir,'culprit.launched')
    # if os.path.isfile(ack_file):
    #   print('\t\tCulprit was already kicked-off')
    #   return 'launched'

    # link the original runs and reports
    print('linking original runs')
    ng_start_flow = os.path.join(suite_run_dir, start_date, 'prs/run', flow)
    ng_end_flow   = os.path.join(suite_run_dir, end_date,   'prs/run', flow)

    culp_start_flow = os.path.join(target_dir,'%s_nightly'%start_date)
    culp_end_flow = os.path.join(target_dir,'%s_nightly'%end_date)

    if not os.path.exists(culp_start_flow): 
      os.mkdir(culp_start_flow)
    else:
      os.remove(culp_start_flow)
      os.mkdir(culp_start_flow)

    if not os.path.exists(culp_end_flow): 
      os.mkdir(culp_end_flow)
    else:
      os.remove(culp_end_flow)
      os.mkdir(culp_end_flow)

    for des in _designs:
        target_start = os.path.join(ng_start_flow,des)
        sm_ln_start  = os.path.join(culp_start_flow,des)

        if not os.path.exists(sm_ln_start):
          os.symlink(target_start,sm_ln_start)

        target_end = os.path.join(ng_end_flow,des)
        sm_ln_end  = os.path.join(culp_end_flow,des)

        if not os.path.exists(sm_ln_end):
          os.symlink(target_end,sm_ln_end)
    
    # done with the links
    #######################################

    cl_bin_dict = {}

    for cl in cl_list:
      cl_num = cl.split('_')[1]
      cl_owner = cl.split('_')[2]
      cl_name = '%s_%s'%(cl_num,cl_owner)
      # cl_name = '_'.join(cl.split('_')[1:2])
      cl_bin_dict[cl_name] = os.path.join(cl_execs,cl)
    
    fl_ls = []
    ds_ls = []
        
    for cl_name,cl_bin in cl_bin_dict.items():

        suffix = '_%s'%(cl_name)
        title  = '<a href="http://clearcase/%s/cl_list.html#%s">%s</a>'%(target_dir,cl_name,cl_name)
        extra  = ''
        raw    = ''
        stages = stages
        dc_bin = '%s/snps/synopsys/bin/%s -r %s'%(cl_bin, shell, root_path) if root_path else '%s/snps/synopsys/bin/%s'%(cl_bin, shell)
        icc2_bin = ''
        fm_bin = ''
        fm_flow = ''
        designs = ' '.join(_designs)
        propts = new_propts
        debug = debug
        fm_extra_settings = ''

        flow_name, orig_des = make_extra(
            flow, suffix, title, extra, raw, stages, dc_bin, icc2_bin, fm_bin, fm_flow, designs, propts, debug, fm_extra_settings
        )

        fl_ls.append(flow_name)

    # adding nightly runs to replicate the issue.
    # start nightly
    suffix = '_%s'%(start_date)
    title  = start_date
    extra  = ''
    raw    = ''
    stages = stages
    dc_bin = '%s/%s/bin/%s'%(ng_execs,start_date,shell)
    icc2_bin = ''
    fm_bin = ''
    fm_flow = ''
    designs = ' '.join(_designs)
    propts = new_propts
    debug = debug
    fm_extra_settings = ''

    flow_name, orig_des = make_extra(
        flow, suffix, title, extra, raw, stages, dc_bin, icc2_bin, fm_bin, fm_flow, designs, propts, debug, fm_extra_settings
    )

    fl_ls.append(flow_name)


  # end nightly
    suffix = '_%s'%(end_date)
    title  = end_date
    extra  = ''
    raw    = ''
    stages = stages
    dc_bin = '%s/%s/bin/%s'%(ng_execs,end_date,shell)
    icc2_bin = ''
    fm_bin = ''
    fm_flow = ''
    designs = ' '.join(_designs)
    propts = new_propts
    debug = debug
    fm_extra_settings = ''

    flow_name, orig_des = make_extra(
        flow, suffix, title, extra, raw, stages, dc_bin, icc2_bin, fm_bin, fm_flow, designs, propts, debug, fm_extra_settings
    )

    fl_ls.append(flow_name)

    # just catching some particular error
    # due to corrupted propts
    # no time for fancy stuff
    try:
      ffffs = 'flows: %s\n\n'%' '.join(fl_ls)
    except:
      return 'unable to get flow def'
    
    # make propts for Kick-off
    kick_propts  = 'INCLUDE %s\n\n'%new_propts
    kick_propts += '## comment below line for runtime accuracy\n'
    # kick_propts += 'INCLUDE /remote/pv/repo/dcnt/dcrt_prs_lib/gala_memusage_4c.cfg\n'
    if rt_accurate:
      kick_propts += 'DEFINE BATCH_CPU\n'
      kick_propts += 'INCLUDE /remote/pv/repo/pvutil/dcprs/suite/hw_cfg/machine/propts.gala.farm_selection.cfg\n'
      
    else:
      kick_propts += 'DEFINE BATCH_MEM\n'
      kick_propts += 'INCLUDE /remote/pv/repo/pvutil/dcprs/suite/hw_cfg/machine/propts.gala.farm_selection.cfg\n'
    kick_propts += comments + '\n'
    kick_propts += 'flows:\n'
    for ff in fl_ls:
      kick_propts += ':: %s\n'%ff

    kick_propts += '\ndesigns: %s\n'%' '.join(_designs)

    if not debug:
        propts_kick_file = open('%s/propts.cfg'%target_dir, 'w')
        propts_kick_file.write(kick_propts)
        propts_kick_file.close()

            # appending the original runs links
        fl_ls.insert(0,'%s_nightly'%start_date)
        fl_ls.append('%s_nightly'%end_date)
        report_local(fl_ls, _designs, target_dir, fl_ls[0])

    print('\t\tCulprit propts written at %s'%target_dir)

    # lets be nice and append a comment in the QoR table
    qor_table_comment_path = os.path.join(suite_run_dir,'QoR_tracking/image_data',end_date,'comment.%s'%flow)

    if QTab_comment:
      if not os.path.exists(qor_table_comment_path):
        qor_table_comment_file = open(qor_table_comment_path,'w')
        tracking_msg  = 'Running investigations : [<a href="https://clearcase%s">culprit_dir</a>]\n'%target_dir
        tracking_msg += QTab_comment
      else:
        tracking_msg  = 'Running investigations : [<a href="https://clearcase%s">culprit_dir</a>]\n'%target_dir
        tracking_msg += QTab_comment
        qor_table_comment_file = open(qor_table_comment_path,'a+')
      
      qor_table_comment_file.write(tracking_msg)
      qor_table_comment_file.close()

    return 'ready to launch'

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
  # pp.pprint(cl_dict)
  # print(html_name)

def suite_pv_view_jinja(
  tool, 
  branch, 
  branch_cname, 
  suite, 
  suite_cname, 
  flow, 
  html_title, 
  all_pkl_name, 
  means_pkl_name,
  mean_values_pkl_name,
  metrics_selection, 
  n_designs, 
  nightly_max, 
  sum_links_dict, 
  qor_trend_image, 
  all_links_dict, 
  report_name,
  diff_report, 
  root_path, 
  prs_status_pkl_name, 
  des_numeric_values_pkl,
  ng_execs,
  cl_execs,
  _24x7_info,
  shell,
  histograms_pkl,
  baseline,
  prev_baseline):
  
  print('\nsuite_pv.py')
  print('\nLooking for noticeable changes in suite.')
  
  # readinf pkl stuff
  print('\treading ' + all_pkl_name)
    
  suite_all_file = open(all_pkl_name, 'rb')
  suite_all = pickle.load(suite_all_file)
  suite_all_file.close()

  # thise are the diff values
  print('\treading ' + means_pkl_name)
  suite_means_file = open(means_pkl_name, 'rb')
  suite_means = pickle.load(suite_means_file)
  suite_means_file.close();

  # this are the base values
  print('\treading ' + mean_values_pkl_name)
  suite_means_base_file = open(mean_values_pkl_name, 'rb')
  suite_means_base = pickle.load(suite_means_base_file)
  suite_means_base_file.close();


  print('\treading ' + des_numeric_values_pkl)
  des_numeric_values_file = open(des_numeric_values_pkl, 'rb')
  des_numeric_values = pickle.load(des_numeric_values_file)
  des_numeric_values_file.close()

  print('\treading ' + histograms_pkl)
  histograms_pkl = open(histograms_pkl, 'rb')
  histograms = pickle.load(histograms_pkl)
  histograms_pkl.close()

  print('\treading ' + prs_status_pkl_name)
  prs_status_pkl = open(prs_status_pkl_name, 'rb')
  prs_status = pickle.load(prs_status_pkl)
  prs_status_pkl.close()

  print('\n\tAnalyzing QoR results')

  result_qor = analyze_qor(suite_means,suite_all,des_numeric_values,metrics_selection,flow,n_designs,histograms)
  
  culprits = None
  if _24x7_info:
    print('\n\tAnalyzing PRS status and preparing culprit runs.')
    culprits = prepare_culprits(result_qor, prs_status, root_path, branch, suite, flow, ng_execs, cl_execs, _24x7_info, shell)
    
  # print('DO WE HAVE CULPRITS?')
  # pp.pprint(culprits)
    
  ## make the html to render in jinja
  # https://clearcase/remote/dcopt077/nightly_prs/p2019.03-SP/DC_ICC2/QoR_tracking/summary.SRM_wlm.html
  qor_table_file = os.path.join(root_path,branch,suite,'QoR_tracking','summary.' + flow + '.html')
  qor_table_link = 'https://clearcase' + qor_table_file if os.path.isfile(qor_table_file) else None

  # grab the comments and look for asociated STARS
  '''
  qor_table_dir = os.path.join(root_path,branch,suite,'QoR_tracking','image_data')
  qor_table_dir = qor_table_dir if os.path.isdir(qor_table_dir) else None
  
  print('\tAnalyzing comment for STARS...')
  star_keys_json = os.path.join('STARs_comments','jira_keys.json')
  star_keys = json.load(star_keys_json)

  flow_txt_summary = {}

  if qor_table_dir:
    for n in [*result_qor]:

      comment_file = os.path.join(qor_table_dir,n, 'comment.%s'%flow)
      jira_ptrn = 'jira.internal.synopsys.com/browse/(P[0-9]+-[0-9]+)'

      if os.path.exists(comment_file):
        flow_txt_summary[n] = {}

        comment_txt = open(comment_file, 'r').read()
        flow_txt_summary['comment'] = comment_txt 
        stars = re.findall(jira_ptrn,comment_txt)
        
        for st in stars:
          st_id = star_keys[st]
          st_comm_file = os.path.join('STARs_comments','%s.comment'%st_id)
          st_comment = open(st_comm_file).read()

          flow_txt_summary[st] = st_comment 

  pp.pprint(flow_txt_summary)
  '''

  template_file = '/slowfs/dcopt105/vasquez/utils/suite_collectors_dev/v_repo/suite_collectors/suite_pv_view.jinja'
  env = Environment(loader=FileSystemLoader('/'))
  template = env.get_template(template_file)
  template.globals['mini_hist'] = mini_hist

  # pp.pprint(prs_status)
  # data for graphic

  m_list = [*metrics_selection]
  nightlies = [*result_qor]
  nightlies.reverse()
  mt_g_data = {}
  for m in m_list:
    mt_g_data[m] = []
    for n in nightlies:
      try:
        mt_g_data[m].append(
          float(suite_means_base[n][flow][m])
        )
      except:
        mt_g_data[m].append(
          'null'
        )
  
  # checking for report existence
  rpt_status = {}
  for n in nightlies:
    
    rpt_status[n] = {'base': False, 'diff': False}
    
    rpt_status[n]['base'] = os.path.exists(
      os.path.join(
        root_path,branch,suite,n,'prs_report.'+report_name+'.out/index.html'
      )
    )

    print(diff_report)
    rpt_status[n]['diff'] = os.path.exists(
      os.path.join(
        root_path,branch,suite,n,'prs_report.'+diff_report+'.out/index.html'
      )
    )

  fail_hdrs = 'design status fatal_file line fatal_text disk_avail stack_trace'.split()

  print('Rendering')
  html = template.render(
        m_list = m_list,
        nightlies = nightlies,
        mt_g_data = mt_g_data,
        html_title = html_title,
        tool = tool,
        root_path = root_path,
        branch = branch,
        suite = suite,
        branch_cname = branch_cname,
        suite_cname = suite_cname,
        flow = flow,
        all_links_dict = all_links_dict,
        nightly_max = nightly_max,
        metrics_selection = metrics_selection,
        sum_links_dict = sum_links_dict,
        qor_table_link = qor_table_link,
        qor_trend_image = qor_trend_image,
        result_qor = result_qor,
        report_name = report_name,
        diff_report = diff_report,
        prs_status = prs_status,
        culprits = culprits,
        hdrs = fail_hdrs,
        now = now,
        baseline = baseline,
        prev_baseline = prev_baseline,
        suite_means = suite_means,
        rpt_status = rpt_status,
        )

  html_name = '%s.php'%html_title
  report_file = open(html_name, 'w')
  report_file.write(html)
  report_file.close()

  print('-Beautiful html created at: \n %s'%os.path.join(os.getcwd(),html_name))
  return html_name
