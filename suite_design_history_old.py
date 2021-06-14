import pickle
import pandas as pd
from jinja2 import Template, Environment, FileSystemLoader

#import plotly
import pprint
pp = pprint.PrettyPrinter(indent=2)

# suite_design_history.py - vasquez
# 
# Make and html report for each metric provided in a list from a pkl_all file, please be caution 
# the metrics should be valid ones.
# If used as function, returns the name of the html file. 
#
# usage example

# all_pkl_name = 'srm_icc2_spg_opt_area_all.pkl'
# mean_pkl_name = 'srm_icc2_spg_opt_area_means.pkl'
# 
# metrics_selection = ['DCWNS',
#                       'DCTNSPMT',
#                       'DCTNSPM',
#                       'CLKDCAllOpt',
#                       'DCStdCelTotPow',
#                       'DCMem']
# html_title = 'Some_title_for_this'
#
# suite_design_history_html(all_pkl_name, mean_pkl_name, metrics_selection, html_title)

def suite_design_history_html(branch, suite, flow, baseline, report,all_pkl_name, mean_pkl_name, metrics_selection, html_title):

  print('\nsuite_design_history.py')
  print('\nreading ' + all_pkl_name)
  
  suite_all_file = open(all_pkl_name, 'rb')
  suite_all = pickle.load(suite_all_file)
  suite_all_file.close()

  print('reading ' + mean_pkl_name)
  suite_mean_file = open(mean_pkl_name, 'rb')
  suite_mean = pickle.load(suite_mean_file)
  suite_mean_file.close()

  html_names = {}

  for metric in metrics_selection:
    
    # lets try to draw a table  
    des_rows = {}
    head_row = []
    head_col = []

    for nightly in suite_all:
      if nightly not in head_row: head_row.append(nightly)
      for report in suite_all[nightly]:
        if metric in suite_all[nightly][report]:
          for design in suite_all[nightly][report][metric]:
            if design not in des_rows:
              # use the design as temporary key
              des_rows[design] = {}
              des_rows[design]['design'] = design # dont judge me
            if design not in head_col: head_col.append(design)
            des_rows[design][nightly] = suite_all[nightly][report][metric][design]
          if 'Mean' not in des_rows:
            des_rows['Mean'] = {}
            des_rows['Mean']['design'] = 'Mean' #... yup, so ugly
          des_rows['Mean'][nightly] = suite_mean[nightly][report][metric] if metric in suite_mean[nightly][report] else '--'
        else:
          print('\t' + metric + ' is not present in ' + nightly + '/' + report)
    # lets sort hour hedings and h_col
    head_row.sort()
    head_row.insert(0,'design')
    head_col.sort()
    head_col.append('Mean')

    # lets render the pages
    
    # available data at this point (Ng_i : nightly, des_i: design name , val_i : QoR percentage value )
    # head_row : list with the headers of the table in order [design, Ng_1, Ng_2, ... Ng_n] (just strings)
    # head_col : list with the first colum elments in order [des_1, des_2, ..., des_N, Mean] (just strings)
    # des_rows : contain the values for each design-nightly in this way
    # 
    # des_rows = {
    #   des_1 : {
    #     Ng_1 : val_1,
    #     Ng_2 : val_2,
    #     ...
    #     Ng_n : val_n,
    #   },
    #   des_2 : {...},
    #   ...
    #   des_n : {...}
    # }
    
    template_file = '/slowfs/dcopt105/vasquez/utils/suite_collectors_dev/v_repo/suite_collectors/suite_design_history.jinja'
    env = Environment(loader=FileSystemLoader('/'))
    template = env.get_template(template_file)

    title = metric

    html = template.render(
        html_title = metric,
        metric = metric,
        branch = branch,
        suite = suite,
        flow = flow,
        report = report,
        baseline = baseline,
        head_row = head_row,
        head_col = head_col,
        des_rows = des_rows
        )

    html_name   = metric+ '_' + html_title + '.html'
    report_file = open(html_name, 'w')
    report_file.write(html)
    report_file.close()

    html_names[metric] = html_name

  return html_names