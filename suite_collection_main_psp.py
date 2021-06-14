import os, re, pickle
from bs4 import BeautifulSoup
#user functions

from suite_collector import suite_collector
from suite_excel_dump import suite_excel_dump
from suite_changes_html import suite_changes_html
from suite_design_history import suite_design_history_html
from suite_fm_history import suite_fm_history_html
from qor_trend import make_trend
#  I plan to make the following reports:
#  - Suite relevant changes with QoR trend and links to: 
#       - each metric design history
#       - Fm reports if needed.


import pprint

# collect the data for the reports from baseline
# i think this arguments are the same for Antinopa's scripts
nightly_max = 10


root_path   = '/remote/dcopt077/nightly_prs/'
tool        = 'DC' # i dont really use this one
branch   	= 'p2019.03-SP'
suite    	= 'DC_ICC2'
flow     	= 'SRM_ICC2_spg_opt_area'
# until here

# This seems exclusive for Antonio's reports
# QoR reports data
baseline    = 'O_SRM_ICC2_spg_opt_area'
report      = 'srm_icc2_spg_opt_area'

# qor table html
qor_table_html = '/remote/dcopt077/nightly_prs/p2019.03-SP/DC_ICC2/QoR_tracking/summary.SRM_ICC2_spg_opt_area.html'

# these are the metrics you want to track, you can put all of them if you want,
# the names can be obtained from any histogram html page

metrics_selection = {
                     'DCMvArea'         : 0.3,
                     'DCWNS'            : 0.3,
                     'DCTNSPM'          : 1,
                     'DCTNSPMT'         : 1,
                     'CLKDCAllOpt'      : 0.4,
                     'DCStdCelTotPow'   : 0.3,
                     'DCMem'            : 0.1
                     }

# these two should be optionals
# in case there is no fm report use '' as arguments.
fm_report  	= 'fml_srmfm_spg_ona' # needs to be of the diff kind
fm_flow     = 'SRMFm_ICC2_spg_opt_area' # column name you want to collect

# end of arguments
######################################

# the following shuld be part of a wrapper script

# this is the wrapper


def suite_collector_main(root_path, branch, suite, flow, baseline, report, metrics_selection, fm_report, fm_flow):

    # start collection of reports from baseline
    [all_values_pkl_name, mean_values_pkl_name] = suite_collector(root_path, branch, suite, report, flow, baseline, nightly_max)

    # make excel report
    excel_file_name = suite_excel_dump(all_values_pkl_name, mean_values_pkl_name, metrics_selection)

    # make an html history report
    html_history_name = report + '_history'

    history_html_name_list = suite_design_history_html(branch, suite, flow, baseline, report, all_values_pkl_name, mean_values_pkl_name, metrics_selection, html_history_name)

    # gather the formality reports
    if fm_report != '' or fm_flow != '': 
        fm_history_name = suite_fm_history_html(root_path, branch, suite, fm_report, fm_flow, nightly_max)
    else:
        print('\nNo Fm reports in config, skipping...')

    # now collect the diffs
    [all_diff_values_pkl_name, mean_diff_values_pkl_name] = suite_collector(root_path, branch, suite, 'diff.' + report, flow, flow + '_prev', nightly_max)

    # make the main html for the changes
    html_title = 'Main QoR Changes'
    n_designs = 4

    if fm_report != '' or fm_flow != '': 
        links_dict = { 
            'design_history': history_html_name_list,
            'fm_history'    : fm_history_name,
            'excel_file_name'  : excel_file_name
            }
    else :
        links_dict = { 
            'design_history': history_html_name_list,
            'excel_file_name'  : excel_file_name
            }

    # the qor_trend: a graph with the numbers from qor_table
    # some constant settings
    qor_trend_title     = branch + ' DCG RMS -' + flow + '-'
    avoid_last_image    = False
    show_available      = False
    dup_suffix          = None
    improvement_formula = True
    qor_trend_image     = report

    make_trend(qor_table_html, " ".join(metrics_selection.keys()) , qor_trend_title, qor_trend_image, nightly_max, avoid_last_image, show_available, dup_suffix, improvement_formula)

    print(links_dict['design_history'])

    suite_changes_html(branch, suite, flow, html_title, all_diff_values_pkl_name, mean_diff_values_pkl_name, metrics_selection, n_designs, nightly_max, links_dict, qor_trend_image)


# this is the call to the main function
suite_collector_main(root_path, branch, suite, flow, baseline, report, metrics_selection, fm_report, fm_flow)
