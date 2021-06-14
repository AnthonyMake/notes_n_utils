import os, re, pickle
from bs4 import BeautifulSoup
#user functions

from suite_collector import suite_collector
from suite_excel_dump import suite_excel_dump
from suite_changes_html import suite_changes_html
from suite_design_history import suite_design_history_html
from suite_fm_history import suite_fm_history_html
from qor_trend import make_trend

import pprint
pp = pprint.PrettyPrinter(indent=2)
# collect the data for the reports from baseline
# i think this arguments are the same for Antinopa's scripts
nightly_max = 8

root_path   = '/remote/dcopt077/nightly_prs/'
tool        = 'DC' # i dont really use this one
branch   	= 'p2019.03-SP'
suite    	= 'DC_ICC2'
suite_cname = 'DCG RMS'
flow     	= 'SRM_wlm'
baseline    = 'O_SRM_wlm'
report      = 'srm_wlm'
fm_report = ''
fm_flow = ''

# these are the metrics you want to track, you can put all of them if you want,
# the names can be obtained from any histogram html page

metrics_selection = {
                     'DCMvArea'         : 0.0,
                     'DCNBBArea'        : 0.0,
                     'DCWNS'            : 0.0,
                     'DCTNSPM'          : 0.0,
                     'DCTNSPMT'         : 0.0,
                     'CLKDCAllOpt'      : 0.0,
                     'CPUDCAllOpt'      : 0.0,
                     'CPUDCFullOpt'     : 0.0,
                     'DCStdCelTotPow'   : 0.0,
                     'DCNBBLeakPow'     : 0.0,
                     'DCMem'            : 0.0
                     }

# these two should be optionals
# in case there is no fm report use '' as arguments.
# 
# fm_report  	= 'fml_srmfm_spg_ona' # needs to be of the diff kind
# fm_flow     = 'SRMFm_ICC2_spg_opt_area' # column name you want to collect


links_pkl = 'all_links.pkl'

if os.path.isfile(links_pkl):
    links_file = open(links_pkl, 'rb')
    links_dict = pickle.load(links_file)
    links_file.close()
else:
    links_dict = {}
    links_dict[tool] = {}
    links_dict[tool][branch] = {}
    links_dict[tool][branch][suite_cname] = {}

# end of arguments
##################

# this is the wrapper
# it should be in another file
def suite_collector_flow(root_path, branch, suite, suite_cname,flow, baseline, report, metrics_selection, fm_report, fm_flow, all_links_dict):
    
    # start collection of reports from baseline
    [all_values_pkl_name, mean_values_pkl_name] = suite_collector(root_path, branch, suite, report, flow, baseline, nightly_max)

    # make excel report
    excel_file_name = suite_excel_dump(all_values_pkl_name, mean_values_pkl_name, metrics_selection)

    # make an html history report
    html_history_name = branch + '_' + suite + '_' + report + '_history'

    history_html_name_list = suite_design_history_html(branch, suite, flow, baseline, report, all_values_pkl_name, mean_values_pkl_name, metrics_selection, html_history_name)

    # gather the formality reports
    if fm_report != '' or fm_flow != '': 
        fm_history_name = suite_fm_history_html(root_path, branch, suite, fm_report, fm_flow, nightly_max)
    else:
        print('\nNo Fm reports in config, skipping...')

    # now collect the diffs
    [all_diff_values_pkl_name, mean_diff_values_pkl_name] = suite_collector(root_path, branch, suite, 'diff.' + report, flow, flow + '_prev', nightly_max)

    # make the main html for the changes
    html_title = branch + '_' + suite + '_' + flow + '_changes'
    n_designs = 4 # to display in the boxes

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
    # qor_table_html      = '/remote/dcopt077/nightly_prs/p2019.03-SP/DC_ICC2/QoR_tracking/summary.SRM_ICC2_spg_opt_area.html'
    qor_table_html      = os.path.join(root_path, branch, suite, 'QoR_tracking', 'summary.' + flow + '.html')
    qor_trend_title     = branch + ' ' + suite_cname + ' -' + flow + '-'
    avoid_last_image    = False
    show_available      = False
    dup_suffix          = None
    improvement_formula = True
    qor_trend_image     = branch.replace('.','_').replace('-','_') + '_' + report

    make_trend(qor_table_html, " ".join(metrics_selection.keys()) , qor_trend_title, qor_trend_image, nightly_max, avoid_last_image, show_available, dup_suffix, improvement_formula)

    #print(links_dict['design_history'])

    return suite_changes_html(branch, suite, flow, html_title, all_diff_values_pkl_name,
                              mean_diff_values_pkl_name, metrics_selection, n_designs, nightly_max, 
                              links_dict, qor_trend_image, all_links_dict, report, root_path)

# this is the call to the main function
links_dict[tool][branch][suite_cname][flow] = suite_collector_flow(root_path, branch, suite, suite_cname, flow, baseline, report, metrics_selection, fm_report, fm_flow, links_dict)

exit()
# previous config still useful
# root_path   = '/remote/dcopt077/nightly_prs/'
# tool        = 'DC' # i dont really use this one
# branch   	= 'p2019.03-SP'
# suite    	= 'DC_ICC2'
# suite_cname = 'DCG RMS'
flow     	= 'SRM_ICC2'
baseline    = 'O_SRM_ICC2'
report      = 'srm_icc2'
# fm_report = ''
# fm_flow = ''

# metrics_selection = same as above

links_dict[tool][branch][suite_cname][flow] = suite_collector_flow(root_path, branch, suite, suite_cname, flow, baseline, report, metrics_selection, fm_report, fm_flow, links_dict)

# previous config still useful
# root_path   = '/remote/dcopt077/nightly_prs/'
# tool        = 'DC' # i dont really use this one
# branch   	= 'p2019.03-SP'
# suite    	= 'DC_ICC2'
# suite_cname = 'DCG RMS'
flow     	= 'SRM_ICC2_spg_opt_area'
baseline    = 'O_SRM_ICC2_spg_opt_area'
report      = 'srm_icc2_spg_opt_area'
fm_report   = 'fml_srmfm_spg_ona'
fm_flow     = 'SRMFm_ICC2_spg_opt_area'

# metrics_selection = same as above
links_dict[tool][branch][suite_cname][flow] = suite_collector_flow(root_path, branch, suite, suite_cname, flow, baseline, report, metrics_selection, fm_report, fm_flow, links_dict)

# previous config still useful
# root_path   = '/remote/dcopt077/nightly_prs/'
# tool        = 'DC' # i dont really use this one
# branch   	= 'p2019.03-SP'
# suite    	= 'DC_ICC2'
# suite_cname = 'DCG RMS'
flow     	= 'SRM_ICC2_spg_timing_opt_area'
baseline    = 'O_SRM_ICC2_spg_timing_opt_area'
report      = 'srm_icc2_spg_timing_opt_area'
fm_report   = 'fml_srmfm_spg_timing_ona'
fm_flow     = 'SRMFm_ICC2_spg_timing_opt_area'

# metrics_selection = same as above
links_dict[tool][branch][suite_cname][flow] = suite_collector_flow(root_path, branch, suite, suite_cname, flow, baseline, report, metrics_selection, fm_report, fm_flow, links_dict)


# previous config still useful
# root_path   = '/remote/dcopt077/nightly_prs/'
# tool        = 'DC' # i dont really use this one
# branch   	= 'p2019.03-SP'
# suite    	= 'DC_ICC2'
# suite_cname = 'DCG RMS'
flow     	= 'SRM_ICC2_spg_opt_area_nd'
baseline    = 'SRM_ICC2_spg_opt_area'
report      = 'srm_icc2_spg_opt_area_nd'
fm_report   = ''
fm_flow     = ''
metrics_selection_nd = {
                     'DCMvArea'         : 0.0,
                     'DCWNS'            : 0.0,
                     'DCTNSPM'          : 0.0,
                     'DCTNSPMT'         : 0.0,
                     'DCStdCelTotPow'   : 0.0,
                     'DCNBBLeakPow'     : 0.0,
                     'DCMem'            : 0.0
                     }


links_dict[tool][branch][suite_cname][flow] = suite_collector_flow(root_path, branch, suite, suite_cname, flow, baseline, report, metrics_selection_nd, fm_report, fm_flow, links_dict)

#####################################################
# new suite
# previous config still useful
# root_path   = '/remote/dcopt077/nightly_prs/'
# tool        = 'DC' # i dont really use this one
# branch   	= 'p2019.03-SP'
suite    	= 'HPDRT'
suite_cname = 'DCG CSS'
flow     	= 'HPD_DCG_rt'
baseline    = 'N_HPD_DCG_rt'
report      = 'hpdrt_dcg'
fm_report   = ''
fm_flow     = ''


if suite not in links_dict[tool][branch]: 
    links_dict[tool][branch][suite_cname] = {}

links_dict[tool][branch][suite_cname][flow] = suite_collector_flow(root_path, branch, suite, suite_cname, flow, baseline, report, metrics_selection, fm_report, fm_flow, links_dict)

#####################################################
# new suite
# previous config still useful
# root_path   = '/remote/dcopt077/nightly_prs/'
# tool        = 'DC' # i dont really use this one
# branch   	= 'p2019.03-SP'
suite    	= 'DC_ICC2_Platform'
suite_cname = 'PF-DCNXTRoute_opt'
flow     	= 'HPD_cust_DC_ICC2_spg'
baseline    = 'O_HPD_cust_DC_ICC2_spg'
report      = 'HPD_cust_DC_ICC2'
fm_report   = ''
fm_flow     = ''

if suite not in links_dict[tool][branch]: 
    links_dict[tool][branch][suite_cname] = {}

links_dict[tool][branch][suite_cname][flow] = suite_collector_flow(root_path, branch, suite, suite_cname, flow, baseline, report, metrics_selection, fm_report, fm_flow, links_dict)

#####################################################
# a new branch

root_path   = '/remote/dcopt077/nightly_prs/'
tool        = 'DC' # i dont really use this one
branch   	= 'o2018.06-SP'
suite    	= 'DC_ICC2'
suite_cname = 'DCG RMS'
flow     	= 'SRM_wlm'
baseline    = 'N_SRM_wlm'
report      = 'srm_wlm'
fm_report = ''
fm_flow = ''

# this is a new branch, so
# the same in case of new suite
if branch not in links_dict[tool]: 
    links_dict[tool][branch] = {}
    links_dict[tool][branch][suite_cname] = {}
    
# this is the call to the main function
links_dict[tool][branch][suite_cname][flow] = suite_collector_flow(root_path, branch, suite, suite_cname, flow, baseline, report, metrics_selection, fm_report, fm_flow, links_dict)

# previous config still useful
# root_path   = '/remote/dcopt077/nightly_prs/'
# tool        = 'DC' # i dont really use this one
# branch   	= 'O...'
# suite    	= 'DC_ICC2'
# suite_cname = 'DCG RMS'
flow     	= 'SRM_ICC2'
baseline    = 'N_SRM_ICC2'
report      = 'srm_icc2'
# fm_report = ''
# fm_flow = ''

# metrics_selection = same as above

links_dict[tool][branch][suite_cname][flow] = suite_collector_flow(root_path, branch, suite, suite_cname, flow, baseline, report, metrics_selection, fm_report, fm_flow, links_dict)


# previous config still useful
# root_path   = '/remote/dcopt077/nightly_prs/'
# tool        = 'DC' # i dont really use this one
# branch   	= 'O...'
# suite    	= 'DC_ICC2'
# suite_cname = 'DCG RMS'
flow     	= 'SRM_ICC2_spg_opt_area'
baseline    = 'N_SRM_ICC2_spg_opt_area'
report      = 'srm_icc2_spg_opt_area'
fm_report   = 'fml_srmfm_spg_ona'
fm_flow     = 'SRMFm_ICC2_spg_opt_area'

# metrics_selection = same as above
links_dict[tool][branch][suite_cname][flow] = suite_collector_flow(root_path, branch, suite, suite_cname, flow, baseline, report, metrics_selection, fm_report, fm_flow, links_dict)

# previous config still useful
# root_path   = '/remote/dcopt077/nightly_prs/'
# tool        = 'DC' # i dont really use this one
# branch   	= 'O...'
# suite    	= 'DC_ICC2'
# suite_cname = 'DCG RMS'
flow     	= 'SRM_ICC2_spg_timing_opt_area'
baseline    = 'N_SRM_ICC2_spg_timing_opt_area'
report      = 'srm_icc2_spg_timing_opt_area'
fm_report   = 'fml_srmfm_spg_timing_ona'
fm_flow     = 'SRMFm_ICC2_spg_timing_opt_area'

# metrics_selection = same as above
links_dict[tool][branch][suite_cname][flow] = suite_collector_flow(root_path, branch, suite, suite_cname, flow, baseline, report, metrics_selection, fm_report, fm_flow, links_dict)

# previous config still useful
# root_path   = '/remote/dcopt077/nightly_prs/'
# tool        = 'DC' # i dont really use this one
# branch   	= 'O...'
# suite    	= 'DC_ICC2'
# suite_cname = 'DCG RMS'
flow     	= 'SRM_ICC2_spg_opt_area_nd'
baseline    = 'SRM_ICC2_spg_opt_area'
report      = 'srm_icc2_spg_opt_area_nd'
fm_report   = ''
fm_flow     = ''

# metrics_selection = same as above
links_dict[tool][branch][suite_cname][flow] = suite_collector_flow(root_path, branch, suite, suite_cname, flow, baseline, report, metrics_selection_nd, fm_report, fm_flow, links_dict)

#####################################################
# new suite
# previous config still useful
# root_path   = '/remote/dcopt077/nightly_prs/'
# tool        = 'DC' # i dont really use this one
# branch   	= 'O...'
suite    	= 'HPDRT'
suite_cname = 'DCG CSS'
flow     	= 'HPD_DCG_rt'
baseline    = 'N_HPD_DCG_rt'
report      = 'hpdrt_dcg'
fm_report   = ''
fm_flow     = ''


if suite not in links_dict[tool][branch]: 
    links_dict[tool][branch][suite_cname] = {}

links_dict[tool][branch][suite_cname][flow] = suite_collector_flow(root_path, branch, suite, suite_cname, flow, baseline, report, metrics_selection, fm_report, fm_flow, links_dict)

#####################################################
# new suite
# previous config still useful
# root_path   = '/remote/dcopt077/nightly_prs/'
# tool        = 'DC' # i dont really use this one
# branch   	= 'O...'
suite    	= 'DC_ICC2_Platform'
suite_cname = 'PF-DCNXTRoute_opt'
flow     	= 'HPD_cust_DC_ICC2_spg'
baseline    = 'O_HPD_cust_DC_ICC2_spg'
report      = 'HPD_cust_DC_ICC2'
fm_report   = ''
fm_flow     = ''

if suite not in links_dict[tool][branch]: 
    links_dict[tool][branch][suite_cname] = {}

links_dict[tool][branch][suite_cname][flow] = suite_collector_flow(root_path, branch, suite, suite_cname, flow, baseline, report, metrics_selection, fm_report, fm_flow, links_dict)

#/remote/dcopt077/nightly_prs/o2018.06-SP/HPDRT/QoR_tracking/summary.HPD_cust_dc.html
# a new branch
###########################################################################
# this is for QLS
root_path   = '/slowfs/dcopt036/nightly_prs'
tool        = 'DC' # i dont really use this one
branch   	= 'q2019.12_ls'
suite    	= 'DC_ICC2'
suite_cname = 'DCG RMS'
flow     	= 'SRM_ICC2_spg_opt_area'
baseline    = 'O_SRM_ICC2_spg_opt_area'
report      = 'srm_icc2_spg_opt_area'
fm_report   = ''
fm_flow     = ''

# this is a new branch, so
# the same in case of new suite
if branch not in links_dict[tool]: 
    links_dict[tool][branch] = {}
    links_dict[tool][branch][suite_cname] = {}
    
# this is the call to the main function
links_dict[tool][branch][suite_cname][flow] = suite_collector_flow(root_path, branch, suite, suite_cname, flow, baseline, report, metrics_selection, fm_report, fm_flow, links_dict)

root_path   = '/slowfs/dcopt036/nightly_prs'
tool        = 'DC' # i dont really use this one
branch   	= 'q2019.12_ls'
suite    	= 'DC_ICC2'
suite_cname = 'DCG RMS'
flow     	= 'SRM_ICC2_spg_timing_opt_area'
baseline    = 'O_SRM_ICC2_spg_timing_opt_area'
report      = 'srm_icc2_spg_timing_opt_area'
fm_report   = ''
fm_flow     = ''
    
# this is the call to the main function
links_dict[tool][branch][suite_cname][flow] = suite_collector_flow(root_path, branch, suite, suite_cname, flow, baseline, report, metrics_selection, fm_report, fm_flow, links_dict)


# save dict with links
pkl_file = open(links_pkl , 'wb')
pickle.dump(links_dict, pkl_file)
pkl_file.close()

pp.pprint(links_dict)

