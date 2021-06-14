import os, re, pickle
from bs4 import BeautifulSoup
import pprint
from suite_collector import suite_collector
from prettytable import PrettyTable
from jinja2 import Template, Environment, FileSystemLoader
pp = pprint.PrettyPrinter(indent = 2, depth = 4)
import gc

gc.set_threshold(2000, 40, 40)
# suite_collector.py - vasquez
# 
# Collects al metrics and designs values for a certain report across a certain quantity
# of nightly images, as output return the following two dicts:
# 
# - suite_dict_all   : all the design values
# - suite_dict_means : all mean values
# 
# also dumps pickle files of those dicts with the following names:
#
# report_name + '_all.pkl'
# report_name + '_means.pkl'
# 
# Usage example
# 
# branch   		= '/slowfs/dcopt036/nightly_prs/p2019.03_ls'
# suite    		= 'DC_ICC2'
# report_name	= 'srm_icc2_spg_opt_area'
# flow     		= 'SRM_ICC2_spg_opt_area'
# baseline 		=  'O_SRM_ICC2_spg_opt_area'
# all_base 		= True
# nightly_max 	= 5
# suite_collector(branch, suite, report_name, flow, baseline, all_base, nightly_max)

def suite_collector_nums(root_path, branch, suite, report_name, flow, baseline, nightly_max, target_designs = None, target_metrics = None, pickle_mode = True):

  print('\nsuite_collector_V2.py')

  #branch = branch_path.split('/')[-1]	
  
  print('\nStart collecting data for ' + branch + ' '  + suite + ' ' +flow + ' for last ' + str(nightly_max) + ' nightly-images...')
  # get nightly images list for the desired suite
  branch_path = os.path.join(root_path, branch)
  nightlys_path = os.path.join(root_path, branch, suite)
  nightly_images = open(os.path.join(nightlys_path,'images.txt')).read().split('\n')

  report = 'prs_report.' + report_name + '.out'

  # workaround to remove spaces or nulls 
  # sometimes appears multiple times
  while '' in nightly_images:
    nightly_images.remove('')

  # sort from newest to oldest
  nightly_images.reverse()


  suite_dict_all_values = {}

  # in this dicts we will store the data
  suite_dict_all = {}
  suite_dict_histograms = {}


  # counter to avoid ancient nightly images
  nightly_count = 0

  for nightly in nightly_images:

    target_report_path = os.path.join(branch_path, suite, nightly, report, baseline)
    
    # detect if the report is all base.
    if os.path.isdir(target_report_path) == False:
      target_report_path = os.path.join(branch_path, suite, nightly, report)
    
    print('\t%s %s'%(nightly, report))

    if os.path.isdir(target_report_path):
      
      # so the report exist
      suite_dict_all_values[nightly] = {}
      suite_dict_all_values[nightly][flow] = {}
      
      suite_dict_histograms[nightly] = {}
      suite_dict_histograms[nightly][flow] = {}
      
      # List of available designs in report files
      design_list = []

      for fl in os.listdir(target_report_path):
        
        design_file_ptrn = '^design_(.+)\.html'
        
        m_design = re.match(design_file_ptrn, fl)
        
    
        if m_design and ('profiles' not in m_design.group(1)):
        
          design = m_design.group(1)

          # only pick the target design in case of apocalypse
          if target_designs and design not in target_designs.split(): 
            continue

          design_list.append(design)
          des_all_page = os.path.join(target_report_path,fl)

          suite_dict_all_values[nightly][flow][design] = {}

          if not os.path.exists(des_all_page):
            print('No available %s'%des_all_page)
            continue
          
          des_page_file_obj = open(des_all_page)
          soup_obj = BeautifulSoup(des_page_file_obj, "html.parser")
          des_page_file_obj.close()

          span_tags = soup_obj.find_all('span')



          for tag in span_tags:
            if tag.get('id') != None:
              
              flow_ptrn = '^%s_%s_(.+)'%(flow,design)
              base_ptrn = '^%s_%s_(.+)'%(baseline,design)
              val_ptrn  = '([0-9.\%\+-]+)'

              # metric_base = ''
              # metric_flow = ''
              # percentdiff = ''

              m_flow = re.match(flow_ptrn,tag.get('id').strip())
              m_base = re.match(base_ptrn,tag.get('id').strip())
              m_val  = re.match(val_ptrn, tag.getText().strip())
              
              #print(tag.getText())

              if m_flow and m_val:
                metric = m_flow.group(1)
                value  = m_val.group(1)

                
                if '_value' not in metric:
                  if target_metrics and  metric not in target_metrics.split():
                    continue

                  if metric not in suite_dict_all_values[nightly][flow][design]:	
                    suite_dict_all_values[nightly][flow][design][metric] = {}
                  
                  value = value.replace('%', '').replace('e','E')
                  value = float(value) if value != '--' else None
                  suite_dict_all_values[nightly][flow][design][metric]['diff_percent'] = value
                  
                else:
                  metric = metric.replace('_value','')

                  if target_metrics and  metric not in target_metrics.split():
                    continue


                  if metric not in suite_dict_all_values[nightly][flow][design]:
                    suite_dict_all_values[nightly][flow][design][metric] = {}

                  value = value.replace('%', '')
                  value = float(value) if value != '--' else None
                  suite_dict_all_values[nightly][flow][design][metric]['flow_val'] = value

              if m_base and m_val:
                metric = m_base.group(1).replace('_value','')
                value  = m_val.group(1)
  
                
                if target_metrics and  metric not in target_metrics.split():
                  continue

                if metric not in suite_dict_all_values[nightly][flow][design]:
                  suite_dict_all_values[nightly][flow][design][metric] = {}
                
                value = value.replace('%', '')
                value = float(value) if value != '--' else None
                suite_dict_all_values[nightly][flow][design][metric]['base_val'] = value

      
      # scrap the histograms!
      report_file = os.path.join(target_report_path, 'index.html')
      
      if os.path.isfile(report_file):
        soup_obj = BeautifulSoup(open(report_file), "html.parser")
        span_tags = soup_obj.find_all('span')

        for tag in span_tags:
          hist_ptrn = '(\w+)_Histgrm_(\w+)'
          #print(tag.get('id'))
          m_hist = re.match(hist_ptrn,str(tag.get('id')))

          if m_hist:
            
            hist_flow   = m_hist.group(1)
            hist_metric = m_hist.group(2)
            hist_value  = tag.text.strip()
            
            if target_metrics and hist_metric not in target_metrics.split():
                  continue

            #print(hist_flow, hist_metric, hist_value)
            if hist_flow == flow and hist_metric != 'Gap':

              suite_dict_histograms[nightly][flow][hist_metric] = hist_value
        
      else:
        print('index.html file not present for ' + report + '/' + nightly )
      
            
    else:
      print('\t\t\tnot present')
      nightly_count -= 1
    
    # just count to avoid ancient nightly images
    nightly_count += 1
    if nightly_count >= nightly_max:
      break;

  # save the colected data in pkl dicts
  # you can test the output with some nightly and metric
  
  # return suite_dict_all_values, suite_dict_histograms 


  # chaning to pkl approach
  # lets organize this on pkl_data folders so we can clean up this
  if not pickle_mode:
    return suite_dict_all_values, suite_dict_histograms

  if not os.path.exists('pkl_data'):
    os.mkdir('pkl_data')

  all_nums_pkl_name   = branch + '_' + suite + '_' + report_name + '_' + baseline + '_all_nums.pkl'
  histograms_pkl_name = branch + '_' + suite + '_' + report_name + '_' + baseline + '_histograms.pkl'

  all_nums_pkl_name   = os.path.join('pkl_data', all_nums_pkl_name)
  histograms_pkl_name = os.path.join('pkl_data', histograms_pkl_name)
  
  file_all = open(all_nums_pkl_name , 'wb')
  file_hist = open(histograms_pkl_name ,'wb')

  pickle.dump(suite_dict_all_values, file_all)
  pickle.dump(suite_dict_histograms, file_hist)


  print('\n\tdump metrics design values data to ' + all_nums_pkl_name )
  print('\tdump histograms data to ' + histograms_pkl_name )


  file_all.close()
  file_hist.close()

  
  del suite_dict_all_values
  del suite_dict_all
  del suite_dict_histograms
  gc.collect()

  return all_nums_pkl_name, histograms_pkl_name 

# #end of function suite_collector 
# root_path 	= '/remote/dcopt077/nightly_prs'
# branch = 'q2019.12-SP'
# suite    		= 'DC_ICC2'
# report_name	    = 'diff.srm_icc2_spg_timing_opt_area'
# flow     		= 'SRM_ICC2_spg_timing_opt_area'
# baseline 		= 'SRM_ICC2_spg_timing_opt_area_prev'
# all_base 		= True
# nightly_max 	= 1

#                                                               # root_path, branch, suite, report_name, flow, baseline, nightly_max
# suite_dict_all_values, suite_dict_histograms = suite_collector_nums(root_path, branch, suite, report_name, flow, baseline, nightly_max)

# #pp.pprint(suite_dict_all_values)
# pp.pprint(suite_dict_histograms)

def design_history_tables(
                      suite_dir,
                      report_name,
                      flow,
                      baseline,
                      metric_list, 
                      design_list,
                      nightly_max,
                      html = False
                    ):

  branch = suite_dir.split('/')[-2]
  suite  = suite_dir.split('/')[-1]
  root_path = os.path.join(suite_dir.replace(branch, '').replace(suite, ''))

  dummy, mean_values = suite_collector(
                            root_path, 
                            branch, 
                            suite, 
                            report_name, 
                            flow, 
                            baseline, 
                            nightly_max,
                            target_metrics = metric_list,
                            only_mean = True, 
                            pickle_mode = False)


  des_values, other_dummy = suite_collector_nums(
                        root_path, 
                        branch, 
                        suite, 
                        report_name, 
                        flow, 
                        baseline, 
                        nightly_max, 
                        target_designs  = design_list, 
                        target_metrics = metric_list, 
                        pickle_mode    = False
                      )

  # pp.pprint(mean_values)
  # pp.pprint(des_values)

  for design in design_list.split():
    for metric in metric_list.split():
      
      tab = PrettyTable()
      headers = 'Nightly Mean des Flow Base Diff Comment'.split()
      tab.field_names = headers    
      data = []

      old_flow_val = None
      for nightly in des_values:
        
        try: 
          des_values[nightly][flow][design][metric]
        except:
          continue

        try:
          diff_val=abs(
              des_values[nightly][flow][design][metric]['base_val']\
              -des_values[nightly][flow][design][metric]['flow_val']
            )
        except:
          diff_val = None

        mean_val     = str(mean_values[nightly][flow][metric])+'%' if mean_values[nightly][flow][metric] else '--'
        diff_percent = str(des_values[nightly][flow][design][metric]['diff_percent'])+'%' if des_values[nightly][flow][design][metric]['diff_percent'] else '--'
        flow_val     = des_values[nightly][flow][design][metric]['flow_val']     if des_values[nightly][flow][design][metric]['flow_val']     else '--'
        base_val     = des_values[nightly][flow][design][metric]['base_val']     if des_values[nightly][flow][design][metric]['base_val']     else '--'

        tab_comment_pth = os.path.join(root_path,branch,suite,'QoR_tracking/image_data',nightly,'comment.%s'%flow)
        if os.path.exists(tab_comment_pth):
          tab_comment_file = open(tab_comment_pth,'r')
          tab_comment = tab_comment_file.read()
          tab_comment_file.close()
        else:
          tab_comment = '--'
        
        tab.add_row([
              nightly,
              mean_val,
              diff_percent,
              flow_val,
              base_val,
              round(diff_val,2) if diff_val else '--',
              tab_comment
            ])


        if flow_val != old_flow_val:
          data.append([
                nightly,
                mean_val,
                diff_percent,
                flow_val,
                base_val,
                round(diff_val,2) if diff_val else '--',
                tab_comment
              ])

          old_flow_val = flow_val

      if not html:
        report  = '\nDesign History Report\n\n'
        report += 'Design: %s\n'%design
        report += 'Metric: %s\n'%metric
        report += 'Flow: %s\n'%flow
        report += 'Baseline: %s\n'%baseline
        report += 'Report: %s\n'%report_name
        report += 'Suite dir: %s\n'%suite_dir

        report += str(tab)

        del tab
        rpt_name = '%s_%s.txt'%(metric,design)

      else:
        template_file = '/slowfs/dcopt105/vasquez/utils/suite_collectors_dev/v_repo/suite_collectors/des_hist_tab.jinja'
        env = Environment(loader=FileSystemLoader('/'))
        template = env.get_template(template_file)

        print('Rendering')
        report = template.render(
              design = design,
              metric = metric,
              flow = flow,
              baseline = baseline,
              suite_dir = suite_dir,
              headers = headers,
              data = data
              )

        rpt_name = '%s_%s.html'%(metric,design)

      # dump text/html files
      history_loc      = os.path.join(os.getcwd(),'history_reports')
      des_history_loc  = os.path.join(history_loc,design)

      if not os.path.exists(history_loc):     os.mkdir(history_loc)
      if not os.path.exists(des_history_loc): os.mkdir(des_history_loc)

      rpt_loc  = os.path.join(des_history_loc,rpt_name)
      rpt_file = open(rpt_loc, 'w')
      rpt_file.write(report)
      rpt_file.close()

      print(rpt_name, '...Done')

def des_qor_from_report(report, flow, baseline, target_designs = None, target_metrics = None):

  print('\nGetting design QoR values from report')

  # detect if the report is all base.
  target_report_path = os.path.join(report, baseline)  
  if not os.path.isdir(target_report_path):
    target_report_path = report
  
    if os.path.isdir(target_report_path):
      # so the report exist
      results = {}

      # flow_rpt_dir = os.path.join(target_report_path,baseline)
      # print(flow_rpt_dir)

      if os.path.exists(target_report_path):
        for fl in os.listdir(target_report_path):
          design_file_ptrn = '^design_(.+)\.html'
          m_design = re.match(design_file_ptrn, fl)
          
          if m_design and ('profiles' not in m_design.group(1)):
            design = m_design.group(1)

            # only pick the target design in case of apocalypse
            if target_designs and design not in target_designs.split(): 
              continue

            des_all_page = os.path.join(target_report_path,fl)
            results[design] = {}

            if not os.path.exists(des_all_page):
              print('No des_all page')
              return results
          
            des_page_file_obj = open(des_all_page)
            soup_obj = BeautifulSoup(des_page_file_obj, "html.parser")
            des_page_file_obj.close()

            span_tags = soup_obj.find_all('span')

            for tag in span_tags:
              if tag.get('id') != None:
                
                flow_ptrn = '^%s_%s_(.+)'%(flow,design)
                base_ptrn = '^%s_%s_(.+)'%(baseline,design)
                val_ptrn  = '([0-9.\%\+-]+)'

                # metric_base = ''
                # metric_flow = ''
                # percentdiff = ''

                m_flow = re.match(flow_ptrn,tag.get('id').strip())
                m_base = re.match(base_ptrn,tag.get('id').strip())
                m_val  = re.match(val_ptrn, tag.getText().strip())
                
                #print(tag.getText())

                if m_flow and m_val:
                  metric = m_flow.group(1)
                  value  = m_val.group(1)
                
                  if '_value' not in metric:
                    if target_metrics and  metric not in target_metrics:
                      continue

                    if metric not in results[design]:	
                      results[design][metric] = {}
                    
                    value = value.replace('%', '').replace('e','E')
                    value = float(value) if value != '--' else None
                    results[design][metric]['diff_percent'] = value
                    
                  else:
                    metric = metric.replace('_value','')

                    if target_metrics and  metric not in target_metrics:
                      continue

                    if metric not in results[design]:
                      results[design][metric] = {}

                    value = value.replace('%', '')
                    value = float(value) if value != '--' else None
                    results[design][metric]['flow_val'] = value

                if m_base and m_val:
                  metric = m_base.group(1).replace('_value','')
                  value  = m_val.group(1)
    
                  if target_metrics and  metric not in target_metrics:
                    continue

                  if metric not in results[design]:
                    results[design][metric] = {}
                  
                  value = value.replace('%', '')
                  value = float(value) if value != '--' else None
                  results[design][metric]['base_val'] = value
  print('\tDone.')

  return results

def mean_qor_from_report(report, flow, baseline, target_designs = None, target_metrics = None):
  print('\nGetting Mean QoR values from report...')

  results = {}
  # detect if the report is all base.
  target_report_path = os.path.join(report, baseline)  
  if not os.path.isdir(target_report_path):
    target_report_path = report

  if os.path.isdir(target_report_path):
    report_file = os.path.join(report,'index.html')
    
    if os.path.isfile(report_file):
      soup_obj = BeautifulSoup(open(report_file), "html.parser")
      span_tags = soup_obj.find_all('span')
    
      for tag in span_tags:
        # the formula thing again ...
        mean_ptrn_form = flow + '_Mean_([A-Za-z0-9]+)__.+'
        mean_ptrn_no_form = flow + '_Mean_([A-Za-z0-9_]+)'
      
        # when metric comes with formula
        m_mean_form = re.match(mean_ptrn_form, str(tag.get('id')))
      
        # when metric comes with no formula
        m_mean_no_form = re.match(mean_ptrn_no_form, str(tag.get('id')))
      
        if m_mean_form:
          
          mean_metric = m_mean_form.group(1)
          mean_metric_value = tag.contents[0]
          
          if target_metrics and mean_metric not in target_metrics:
            continue
          # normalize the value to parse as float
          mean_metric_value = mean_metric_value.replace(' ', '')
          mean_metric_value = mean_metric_value.replace('%', '')
          
          results[mean_metric] = mean_metric_value
          
        elif m_mean_no_form: 
          
          mean_metric = m_mean_no_form.group(1)
          mean_metric_value = tag.contents[0]
          
          if mean_metric != 'Gap' and mean_metric != 'FlowLong':
            
            if target_metrics and mean_metric not in target_metrics:
              continue
            # normalize the value to parse as float
            mean_metric_value = mean_metric_value.replace(' ', '')
            mean_metric_value = mean_metric_value.replace('%', '')
            
            results[mean_metric] = mean_metric_value
  print('\tDone.')

  return results

def detect_qor_issues(qor_dict, target_metrics):
  
  # for mean degradations
  n_des = 2

  # max outliers for design value analysis
  max_outliers = 500 # just want to pick everything

  results = []
  for metric in target_metrics:
    if metric in qor_dict['mean']:
      if qor_dict['mean'][metric] != '--':
        current_mean = float(qor_dict['mean'][metric])

      # look if the metric is out of threshold
      # if  abs(current_mean) > metrics_selection[metric][0]:
      if 0:
        # then we sort this
        # clean NaN values before sorting
        cleanList = []
        for design in qor_dict['des']:
            current_design_value = qor_dict['des'][design][metric]['flow_val']

            if current_design_value != '--':
                cleanList.append((design,float(current_design_value)))
        
        # sort designs from min to max
        sor = sorted(cleanList, key=lambda x: x[1])
        
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
        
        des_to_append = worstDict if current_mean > 0 else bestDict
        tp = 'mean degrad.' if current_mean >0 else 'mean improv.'
        
        for dsg in des_to_append:
          if dsg in qor_dict['des']:
            
            # workaround for strange names
            if metric not in qor_dict['des'][dsg]:
              print('\t\tcant find numeric data for', metric)
              print('\t\ttrying something else...')

              # if metric in special_formula_cases:
              #   for m in des_numeric_values[nightly][flow][dsg].keys():
              #     if metric in m:
              #       metric = m 

            try:
              base_val = qor_dict['des'][dsg][metric]['base_val'] # if metric in des_numeric_values[nightly][flow][dsg] else '--'
              flow_val = qor_dict['des'][dsg][metric]['flow_val'] # if metric in des_numeric_values[nightly][flow][dsg] else '--'
            except: 
              print('\t\tcant find numeric data for', metric)
              base_val = '--'
              flow_val = '--'
          else:
            base_val = '--'
            flow_val = '--'
          
          results.append({
            'Metric': metric.split('_')[0],
            'Design': dsg,
            'Mean Value %' : current_mean,
            'Design Value %': des_to_append[dsg],
            # 'Histogram Location': histograms[nightly][flow][metric] if metric in histograms[nightly][flow] else None,
            'Numeric Value Base' : base_val,
            'Numeric Value Flow' : flow_val,
            'Issue Type': tp,
          })

      #else:
      if 1:
        # store outliers on both sides and sort
        des_deg = []
        des_imp = []

        for design in qor_dict['des']:
          if metric in qor_dict['des'][design]:
            des_val = qor_dict['des'][design][metric]['diff_percent']
            if des_val and des_val != '--':
              if des_val > target_metrics[metric][1]:
                des_deg.append((design,des_val))

              elif des_val < -1*target_metrics[metric][1]:
                des_imp.append((design,des_val))

        # sort the lists
        deg_srtd = sorted(des_deg, key=lambda x: x[1]) if des_deg else []
        deg_srtd.reverse()

        imp_srtd = sorted(des_imp, key=lambda x: x[1]) if des_imp else []

        max_deg = max_outliers if len(deg_srtd) >= max_outliers else len(deg_srtd)
        max_imp = max_outliers if len(imp_srtd) >= max_outliers else len(imp_srtd)

        for i in range(max_deg):
          tp = 'outlier degrad.'
            
          # if metric in special_formula_cases:
          #   for m in des_numeric_values[nightly][flow][deg_srtd[i][0]].keys():
          #     if metric in m:
          #       metric = m

          try:
            base_val = qor_dict['des'][deg_srtd[i][0]][metric]['base_val'] if metric in qor_dict['des'][deg_srtd[i][0]] else '--'
            flow_val = qor_dict['des'][deg_srtd[i][0]][metric]['flow_val'] if metric in qor_dict['des'][deg_srtd[i][0]] else '--'
          except:
            print('\t\tcant find numeric data for', metric)
            base_val = '--'
            flow_val = '--'

          # last check for numeric difference
          # help to avoid runtime paranoid values
          sub_metric = metric.split('_')[0]
          print('evaluating numdiff...')
          if len(target_metrics[sub_metric]) == 3:
            try:
              num_diff = float(base_val) -float(flow_val)
              print("evaluating %s difference"%metric, num_diff)
              if abs(num_diff) < target_metrics[sub_metric][2]:
                # values are in range so,
                continue
            except:
              print('counldn\'t avaluate numerical diffrence')
          
          results.append({
            'Metric': metric.split('_')[0],
            'Design'      : deg_srtd[i][0],
            'Mean Value %' : current_mean,
            'Design Value %': deg_srtd[i][1],
            # 'Histogram Location' : histograms[nightly][flow][metric] if metric in histograms[nightly][flow] else None,
            'Numeric Value Base' : base_val,
            'Numeric Value Flow' : flow_val,
            'Issue Type'     : tp, #outlier or mean improv or degrad#
          })                      

        # not tracking impros
        # for i in range(max_imp):
        #   tp = 'outlier improv.'
            
        #   # if metric in special_formula_cases:
        #   #   for m in des_numeric_values[nightly][flow][imp_srtd[i][0]].keys():
        #   #     if metric in m:
        #   #       metric = m

        #   try:
        #     base_val = qor_dict['des'][imp_srtd[i][0]][metric]['base_val'] if metric in qor_dict['des'][imp_srtd[i][0]] else '--'
        #     flow_val = qor_dict['des'][imp_srtd[i][0]][metric]['flow_val'] if metric in qor_dict['des'][imp_srtd[i][0]] else '--'
        #   except:
        #     print('\t\tcant find numeric data for', metric)
            
        #     base_val = '--'
        #     flow_val = '--'
          
        #   if 'degrad' in tp:
        #     results.append({
        #       'Metric': metric.split('_')[0],
        #       'Design'      : imp_srtd[i][0],
        #       'Mean Value %' : current_mean,
        #       'Design Value %': imp_srtd[i][1],
        #       # 'Histogram Location' : histograms[nightly][flow][metric] if metric in histograms[nightly][flow] else None,
        #       'Numeric Value Base' : base_val,
        #       'Numeric Value Flow' : flow_val,
        #       'Issue Type'     : tp, #outlier or mean improv or degrad#
        #     })

  return results

def qor_from_report(report, flow, baseline, target_designs = None, target_metrics = None):
  results = {}
  results['report'] = report
  results['flow'] = report
  results['baseline'] = baseline
  results['mean'] = mean_qor_from_report(report, flow, baseline, target_designs, target_metrics)
  results['des'] = des_qor_from_report(report, flow, baseline, target_designs, target_metrics)
  results['qor_issues'] = detect_qor_issues(results, target_metrics)

  return results

