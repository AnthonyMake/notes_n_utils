#!/slowfs/dcopt105/vasquez/cnda/Conda/bin/python
import sys
sys.path.append('/slowfs/dcopt105/vasquez/utils/suite_collectors_dev/v_repo/suite_collectors')

import os, re, pickle
from bs4 import BeautifulSoup
import yaml
#user functions

from time import sleep


from suite_collector import suite_collector
from suite_excel_dump import suite_excel_dump
from suite_changes_html import suite_changes_html
from suite_design_history import suite_design_history_html
from suite_fm_history import suite_fm_history_html
from suite_fm_history_from_cache import *
from qor_trend import make_trend
from all_metrics_mean_hist import *
from status_collector import status_collector_v2 as status_collector
from suite_pv_view import suite_pv_view_jinja
from suite_collector_v2 import suite_collector_nums
from dask.distributed import Client,wait
from star_board import *
from jinja2 import Template, Environment, FileSystemLoader
import datetime

import pprint
pp = pprint.PrettyPrinter(indent=2)
# collect the data for the reports from baseline
# i think this arguments are the same for Antinopa's scripts
# nightly_max = 8


distributed = False
only_stars = False
no_star_board = False

if len(sys.argv):
    if 'distributed' in sys.argv: 
        print('RUNNING DISTRIBUTED')
        distributed = True
    
    if 'only_stars' in sys.argv: 
        print('STAR Board Only')
        only_stars = True

    if 'no_star_board' in sys.argv: 
        print('No star board')
        no_star_board = True 

else:
    print('Running in local machine, for distributed usage use \'distributed\' flag.' )
    

# put touches to avoid multiple runs
now = datetime.datetime.now() 
running_path = 'collector.running'

if not only_stars:
    if os.path.exists(running_path):
        r_text = open(running_path).read()
        print('there is another collector instance running since %s.'%r_text)
        exit()

    else:
        running_file = open(running_path, 'w')
        running_file.write(str(now))
        running_file.close()


# distributed = False

#c5 = Client('pv128g005:8786')
if distributed:
    c3 = Client('pv128g002:8786')
    c3.upload_file('/slowfs/dcopt105/vasquez/utils/suite_collectors_dev/v_repo/suite_collectors/suite_collector.py')
    c3.upload_file('/slowfs/dcopt105/vasquez/utils/suite_collectors_dev/v_repo/suite_collectors/status_collector.py')
    c3.upload_file('/slowfs/dcopt105/vasquez/utils/suite_collectors_dev/v_repo/suite_collectors/suite_collector_v2.py')

# this is the wrapper

def suite_collector_flow(
    root_path, 
    tool, 
    branch, 
    branch_cname, 
    suite, 
    suite_cname,
    flow, 
    baseline,
    prev_baseline, 
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
    shell,
    cross_flow_dict,
    cross_flow_tab,
    cross_flow_ng):

    ################################################################################
    # Data Gathering
    ################################################################################
    
    # start collection of reports from baseline
    
    if distributed:
        future_status = c3.submit(status_collector,users, root_path, tool, branch, suite, suite_cname,flow, baseline, nightly_max, report, distributed)
        future_base   = c3.submit(suite_collector, root_path, branch, suite, report, flow, baseline, nightly_max)
        future_diff   = c3.submit(suite_collector, root_path, branch, suite, diff_report, flow, prev_baseline, nightly_max)
        future_nums   = c3.submit(suite_collector_nums,root_path, branch, suite, diff_report, flow, prev_baseline, nightly_max, None, ' '.join([*metrics_selection]), True)
        
        # this ones are pkls

        [all_values_pkl_name, mean_values_pkl_name] = future_base.result()
        [all_diff_values_pkl_name, mean_diff_values_pkl_name] = future_diff.result()
        # print('wait a little...')
        # sleep(0.05)
    else:
        # pkls
        [all_values_pkl_name, mean_values_pkl_name] = suite_collector(root_path, branch, suite, report, flow, baseline, nightly_max)
        [all_diff_values_pkl_name, mean_diff_values_pkl_name] = suite_collector(root_path, branch, suite, diff_report, flow, prev_baseline, nightly_max)

    # # the qor_trend: a graph with the numbers from qor_table
    # # some constant settings
    # # will be changed to a new approach using numeric data inside suite_pv_view script
    
    qor_table_html      = '/remote/dcopt077/nightly_prs/p2019.03-SP/DC_ICC2/QoR_tracking/summary.SRM_ICC2_spg_opt_area.html'
    qor_table_html      = os.path.join(root_path, branch, suite, 'QoR_tracking', 'summary.' + flow + '.html')
    qor_trend_title     = branch_cname + ' ' + suite_cname + ' -' + flow + '-'
    avoid_last_image    = False
    show_available      = False
    dup_suffix          = None
    improvement_formula = False
    qor_trend_image     = branch_cname.replace('.','_').replace('-','_') + '_' + report
    #qor_trend_image = None

    # old approach, now the graphic is done using chartjs
    # try:
    #     make_trend(qor_table_html, " ".join(metrics_selection.keys()) , qor_trend_title, qor_trend_image, nightly_max, avoid_last_image, show_available, dup_suffix, improvement_formula)
    # except:
    #     print('fail draw of qor trend for %s'%qor_table_html)
    #     print('moving on...')
    
    # # # lets bring numeric info, this is inneficient because we already have this data,.
    
    if distributed:
        print('awaiting numeric dda...')
        des_numeric_values_pkl, histograms_pkl = future_nums.result()
        # # gather prs_status
        print('awaiting prs_status...')
        prs_status_pkl_name = future_status.result()
    else:
        des_numeric_values_pkl, histograms_pkl = suite_collector_nums(root_path, branch, suite, diff_report, flow, prev_baseline, nightly_max)
        prs_status_pkl_name = status_collector(users, root_path, tool, branch, suite, suite_cname,flow, baseline, nightly_max, report, distributed)
    
    
    # gather the formality reports
    if fm_report != '' or fm_flow != '': 
        # fm_history_dict = suite_fm_history_from_cache(root_path, branch, suite, fm_report, fm_flow, nightly_max)
        # fm_history_name = fm_summary_html(branch, suite, fm_flow, fm_history_dict,all_links_dict)
        
        fm_history_name  = suite_fm_history_html(root_path, branch, suite, fm_report, fm_flow, nightly_max)
    else:
        print('\nNo Fm reports in config, skipping...')


    ################################################################################
    # Almost pure Ui job
    ################################################################################
    
    # make excel report
    # excel_file_name = suite_excel_dump(all_values_pkl_name, mean_values_pkl_name, metrics_selection)
    excel_file_name = ''

    # make an html history report
    html_history_name = branch + '_' + suite + '_' + report + '_history'

    history_html_name_list = suite_design_history_html(branch, suite, flow, baseline, report, all_values_pkl_name, mean_values_pkl_name, metrics_selection, html_history_name)

    # make the main html for the changes
    html_title = branch + '_' + suite + '_' + flow + '_changes'
    n_designs = 2 # to display in the boxes

    ## adding all metrics history,using mean_values_pkl_name
    all_metrics_history      = all_metrics_mean_hist(root_path, branch, suite, report, flow, baseline, mean_values_pkl_name, metrics_selection)
    all_metrics_history_diff = all_metrics_mean_hist(root_path, branch, suite, diff_report, flow, prev_baseline,mean_diff_values_pkl_name,metrics_selection)

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

    #print(links_dict['design_history'])

    # return suite_changes_html(tool, branch, branch_cname, suite, suite_cname, flow, html_title, all_diff_values_pkl_name,
    #                           mean_diff_values_pkl_name, metrics_selection, n_designs, nightly_max, 
    #                           links_dict, qor_trend_image, all_links_dict, report, root_path)
    # for cross_flow_summary aka 'el daily' from prs_status
    # ok this is some silly stuff, but intended to make life easier
    
    if branch_cname not in cross_flow_dict:
        cross_flow_dict[branch_cname] = {}
        
        # this is too optimistic
        cross_flow_tab[branch_cname] = []
        cross_flow_ng[branch_cname] = {}
    
    if suite_cname not in cross_flow_dict[branch_cname]:
        cross_flow_dict[branch_cname][suite_cname] = {}

    # status_dict[branch][suite][nightly][flow]
    if prs_status_pkl_name:
        print('\treading ' + prs_status_pkl_name)
        prs_status_pkl_file = open(prs_status_pkl_name, 'rb')
        prs_status = pickle.load(prs_status_pkl_file)
        prs_status_pkl_file.close()

        if prs_status:
            for nightly in prs_status[branch][suite]:
                if nightly not in cross_flow_dict[branch_cname][suite_cname]:
                    cross_flow_dict[branch_cname][suite_cname][nightly] = {}

                if nightly not in cross_flow_ng[branch_cname]:
                    cross_flow_ng[branch_cname][nightly] = []

                
                for flow in prs_status[branch][suite][nightly]:
                    # check if the flows exists in the nightly
                    # this should be done somewhere else...
                    flow_dir = os.path.join(root_path, branch, suite,nightly,'prs/run',flow)
                    if os.path.exists(flow_dir):
                        if flow not in cross_flow_dict[branch_cname][suite_cname][nightly]:
                            
                            cross_flow_dict[branch_cname][suite_cname][nightly][flow] = {}

                        cross_flow_dict[branch_cname][suite_cname][nightly][flow] = prs_status[branch][suite][nightly][flow]

                        # ugly fix for a not-so-human mistake
                        cross_flow_dict[branch_cname][suite_cname][nightly][flow]['comment_path'] = os.path.join(root_path,branch,suite,'QoR_tracking/image_data',nightly,'comment.%s'%flow)
                        
                        cross_flow_tab[branch_cname].append({
                            'suite': suite_cname,
                            'nightly': nightly,
                            'flow': flow,
                            'status': prs_status[branch][suite][nightly][flow]
                        })

                        cross_flow_ng[branch_cname][nightly].append({
                            'suite': suite_cname,
                            'flow': flow,
                            'diff_report': 'https://clearcase/' + '/'.join([root_path,branch,suite,nightly,'prs_report.'+diff_report+'.out'])
                        })

                    else:
                        pass
                
    pv_summary =  suite_pv_view_jinja(
                        tool, 
                        branch, 
                        branch_cname, 
                        suite, 
                        suite_cname, 
                        flow,
                        html_title, 
                        all_diff_values_pkl_name,
                        mean_diff_values_pkl_name,
                        mean_values_pkl_name, 
                        metrics_selection, 
                        n_designs, 
                        nightly_max,
                        links_dict, 
                        qor_trend_image, 
                        all_links_dict, 
                        report,
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
                        prev_baseline
                        )

    return pv_summary 

def cross_flow_report(tool, branch, cross_flow_dict, cross_flow_tab, cross_flow_ng, all_links_dict):

    #template_text = open('/remote/pv/repo/user/vasquez/v_repo/suite_collectors/mean_hist_base.html', 'r').read()
    
    template_file = '/slowfs/dcopt105/vasquez/utils/suite_collectors_dev/v_repo/suite_collectors/cross_flow_report.jinja'
    #template = Template(template_text)
    env = Environment(loader=FileSystemLoader('/'))
    template = env.get_template(template_file)


    title = 'Cross Flow Report'

    html = template.render(
        html_title = title,
        branch = branch,
        cross_flow_dict = cross_flow_dict[branch],
        cross_flow_tab = cross_flow_tab[branch],
        cross_flow_ng = cross_flow_ng[branch], 
        all_links_dict = all_links_dict,
        tool = tool
        )

    html_name = '%s_cross_flow_report.php'%branch
    report_file = open(html_name, 'w')
    report_file.write(html)
    report_file.close()

    return html_name

#Pending work
def refresh_html_links(tool, dict_yaml, links_dict):
    for branch_cname, branch_dict in links_dict[tool]:
        for suite_cname, suite_dict in branch_dict:
            for flow, flow_dict in branch_dict:
                html = links_dict[tool][branch_cname][suite_cname][flow]

def draw_landing_page(tool,all_links_dict):

        #template_text = open('/remote/pv/repo/user/vasquez/v_repo/suite_collectors/mean_hist_base.html', 'r').read()
    
    template_file = '/slowfs/dcopt105/vasquez/utils/suite_collectors_dev/v_repo/suite_collectors/landing_page.jinja'
    #template = Template(template_text)
    env = Environment(loader=FileSystemLoader('/'))
    template = env.get_template(template_file)

    title = 'Home'

    html = template.render(
        html_title = title,
        all_links_dict = all_links_dict,
        tool = tool
        )

    html_name = 'pv_tracking_hub.php'
    report_file = open(html_name, 'w')
    report_file.write(html)
    report_file.close()

    return html_name
    
# yaml treatment deployed by manu-rama
dict_yaml = {}
cross_flow_dict = {}
cross_flow_tab = {}
cross_flow_ng = {}

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
    if not only_stars:
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


# if not distributed:
#     draw_landing_page(tool,links_dict)
#     exit()

draw_landing_page(tool,links_dict)

####################################################################################
# create star board
if not no_star_board:
    star_dict = star_board_from_jql(team_JQL, 10)
    star_board_html = create_board_html(star_dict, all_links_dict = links_dict)
else:
    star_board_html = 'star_board.php'

if only_stars: exit()
####################################################################################
# append the STAR board as kind of super branch
links_dict[tool]['STAR_board'] = star_board_html

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
            prev_baseline     = flow_dict.get("prev_baseline",flow+'_prev')
            
            if metrics != "":
                metrics_selection = dict_yaml["metrics"][metrics]
            else:
                metrics_selection = dict_yaml["metrics"]["default"]

            # this is the call to the main function
            links_dict[tool][branch_cname][suite_cname][flow] = suite_collector_flow(
                root_path, tool, branch, branch_cname, 
                suite, suite_cname, flow, baseline,prev_baseline, report, diff_report, 
                metrics_selection, fm_report, fm_flow, links_dict, users, ng_execs, cl_execs, _24x7_info, shell, cross_flow_dict,cross_flow_tab, cross_flow_ng)

    # implement cross_flow report as super-suite
    links_dict[tool][branch_cname]['cross_flow'] = cross_flow_report(tool, branch_cname, cross_flow_dict,cross_flow_tab,cross_flow_ng,links_dict)



#refresh_html_links(tool, dict_yaml)

# save dict with links
pkl_file = open(links_pkl , 'wb')
pickle.dump(links_dict, pkl_file)
pkl_file.close()
if not only_stars:
    pp.pprint(links_dict)

if os.path.exists(running_path):
    os.remove(running_path)