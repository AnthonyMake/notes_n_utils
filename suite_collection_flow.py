import os, re, pickle
from bs4 import BeautifulSoup
import yaml
#user functions

from suite_collector import suite_collector
from suite_excel_dump import suite_excel_dump
from suite_changes_html import suite_changes_html
from suite_design_history import suite_design_history_html
from suite_fm_history import suite_fm_history_html
from qor_trend import make_trend
from all_metrics_mean_hist import *
from status_collector import status_collector
from suite_pv_view import suite_pv_view_html
from suite_collector_v2 import suite_collector_nums

import pprint
pp = pprint.PrettyPrinter(indent=2)
# collect the data for the reports from baseline
# i think this arguments are the same for Antinopa's scripts
nightly_max = 8

# this is the wrapper
# it should be in another file
def suite_collector_flow(
    root_path, 
    tool, 
    branch, 
    branch_cname, 
    suite, 
    suite_cname,
    flow, 
    baseline, 
    report, 
    diff_report, 
    metrics_selection, 
    fm_report, 
    fm_flow, 
    all_links_dict, 
    users,
    ng_execs,
    cl_execs,
    _24x7_info,
    shell):
    
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
    [all_diff_values_pkl_name, mean_diff_values_pkl_name] = suite_collector(root_path, branch, suite, diff_report, flow, flow + '_prev', nightly_max)

    # make the main html for the changes
    html_title = branch + '_' + suite + '_' + flow + '_changes'
    n_designs = 2 # to display in the boxes

    ## adding all metrics history,using mean_values_pkl_name
    all_metrics_history      = all_metrics_mean_hist(root_path, branch, suite, report, flow, baseline,mean_values_pkl_name,metrics_selection)
    all_metrics_history_diff = all_metrics_mean_hist(root_path, branch, suite, diff_report, flow, flow+'_prev',mean_diff_values_pkl_name,metrics_selection)

    if fm_report != '' or fm_flow != '': 
        links_dict = { 
            'design_history': history_html_name_list,
            'fm_history'    : fm_history_name,
            'excel_file_name'  : excel_file_name,
            'all_metrics_hist': all_metrics_history,
            'all_metrics_hist_diff': all_metrics_history_diff,
            }
    else :
        links_dict = { 
            'design_history': history_html_name_list,
            'excel_file_name'  : excel_file_name,
            'all_metrics_hist': all_metrics_history,
            'all_metrics_hist_diff': all_metrics_history_diff,
            }

    # the qor_trend: a graph with the numbers from qor_table
    # some constant settings
    # qor_table_html      = '/remote/dcopt077/nightly_prs/p2019.03-SP/DC_ICC2/QoR_tracking/summary.SRM_ICC2_spg_opt_area.html'
    qor_table_html      = os.path.join(root_path, branch, suite, 'QoR_tracking', 'summary.' + flow + '.html')
    qor_trend_title     = branch_cname + ' ' + suite_cname + ' -' + flow + '-'
    avoid_last_image    = False
    show_available      = False
    dup_suffix          = None
    improvement_formula = False
    qor_trend_image     = branch_cname.replace('.','_').replace('-','_') + '_' + report

    make_trend(qor_table_html, " ".join(metrics_selection.keys()) , qor_trend_title, qor_trend_image, nightly_max, avoid_last_image, show_available, dup_suffix, improvement_formula)

    #print(links_dict['design_history'])

    # gather prs_status
    prs_status = status_collector(users, root_path, tool, branch, suite, suite_cname,flow, baseline, nightly_max)
    # return suite_changes_html(tool, branch, branch_cname, suite, suite_cname, flow, html_title, all_diff_values_pkl_name,
    #                           mean_diff_values_pkl_name, metrics_selection, n_designs, nightly_max, 
    #                           links_dict, qor_trend_image, all_links_dict, report, root_path)

    # lets bring numeric info, this is inneficient because we already have this data,.
    des_numeric_values, histograms = suite_collector_nums(root_path, branch, suite, diff_report, flow, flow+'_prev', nightly_max)

    return suite_pv_view_html(
        tool, 
        branch, 
        branch_cname, 
        suite, 
        suite_cname, 
        flow, 
        html_title, 
        all_diff_values_pkl_name,
        mean_diff_values_pkl_name, 
        metrics_selection, 
        n_designs, 
        nightly_max,
        links_dict, 
        qor_trend_image, 
        all_links_dict, 
        report,
        diff_report,
        root_path, 
        prs_status,
        des_numeric_values,
        ng_execs,
        cl_execs,
        _24x7_info,
        shell,
        histograms
        )

#Pending work
def refresh_html_links(tool, dict_yaml, links_dict):

    for branch_cname, branch_dict in links_dict[tool]:
        for suite_cname, suite_dict in branch_dict:
            for flow, flow_dict in branch_dict:
                html = links_dict[tool][branch_cname][suite_cname][flow]




# yaml treatment deployed by manu-rama
dict_yaml = {}

with open("config.yaml", 'r') as stream:
    try:
        dict_yaml = yaml.safe_load(stream)
        
    except yaml.YAMLError as exc:
        #print("Configuration file error")
        print(exc)

links_pkl = 'all_links.pkl'
links_dict = {}
if os.path.isfile(links_pkl):
    links_file = open(links_pkl, 'rb')
    links_dict = pickle.load(links_file)
    links_file.close()
    pp.pprint(links_dict)
#else:

#if any(links_dict) == False:
#    links_dict = {}
tool = dict_yaml["tool"]
users = dict_yaml["users"]

#tool = 'DC'
#metrics_selection = dict_yaml["metrics"]["default"]
if tool not in links_dict:    
    links_dict[tool] = {}

#if nightly_max not in dict_yaml, default is 8, else is the value in the yaml
nightly_max = dict_yaml.get("nightly_max", 8)


for branch, branch_dict in dict_yaml["branch"].items():
    branch_cname = branch_dict.get("name","")
    root_path    = branch_dict.get("root_path","")
    ng_execs = branch_dict.get("ng_execs","")
    cl_execs = branch_dict.get("cl_execs","")
    

    if branch_cname == "":
        branch_cname = branch
    
    if branch_cname not in links_dict[tool]:
        links_dict[tool][branch_cname] = {}

    for suite, suite_dict in branch_dict["suite"].items():
        suite_cname = suite_dict.get("name","")
        _24x7_info = suite_dict.get("24x7_info", '')
        shell = suite_dict.get('shell', '')
        
        if suite_cname not in links_dict[tool][branch_cname]:
            links_dict[tool][branch_cname][suite_cname] = {}

        for flow , flow_dict in suite_dict["flow"].items():
            baseline          = flow_dict.get("baseline","")
            report            = flow_dict.get("report","")
            diff_report       = flow_dict.get("diff_report","diff.%s"%report)
            fm_report         = flow_dict.get("fm_report","")    
            fm_flow           = flow_dict.get("fm_flow","")
            metrics           = flow_dict.get("metrics","")
            
            if metrics != "":
                metrics_selection = dict_yaml["metrics"][metrics]
            else:
                metrics_selection = dict_yaml["metrics"]["default"]

            # this is the call to the main function
            links_dict[tool][branch_cname][suite_cname][flow] = suite_collector_flow(
                root_path, tool, branch, branch_cname, 
                suite, suite_cname, flow, baseline, report,diff_report, 
                metrics_selection, fm_report, fm_flow, links_dict, users, ng_execs, cl_execs, _24x7_info, shell)


#refresh_html_links(tool, dict_yaml)

# save dict with links
pkl_file = open(links_pkl , 'wb')
pickle.dump(links_dict, pkl_file)
pkl_file.close()



pp.pprint(links_dict)

