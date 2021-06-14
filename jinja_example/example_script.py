#!/slowfs/dcopt105/vasquez/cnda/Conda/bin/python
 
import os, re
import datetime, subprocess
from jinja2 import Template, Environment, FileSystemLoader

import pprint
pp = pprint.PrettyPrinter(indent = 1, depth= 2)

#####################################################################################
# This is a simple example on how to draw fancy webpages 
# with ordinary snps environment data
#
# This particular case display the list of directories containing "prs_report"
# in the name, inside of a classic nightly directory. 
# The table is done with datatables.js which provides sorting, searching and paging 
# functionalities. 
# The html layout and design is the "example_view.jinja" file. It uses W3.css as 
# look n feel standar.
#
# Antonio Vasquez
##################################################################################### 


def draw_view():
    
    # get the list of dirs inside a nightly path
    loc      = '/slowfs/dcopt036/nightly_prs/s2021.06_ls/DC_ICC2/D20210507_14_15'
    loc_dirs =  os.listdir(loc)

    # split useful data
    nightly = loc.split('/')[-1]
    suite   = loc.split('/')[-2]
    branch  = loc.split('/')[-3]

    # pp.pprint(loc_dirs)

    report_list = []
    
    # look for the files with 'prs_report' in the name
    for file_name in loc_dirs: 
        if 'prs_report.' in file_name:
            report_list.append(file_name)

    pp.pprint(report_list)

    # redering the template
    template_file = '/slowfs/dcopt105/vasquez/utils/cony_example/example_view.jinja'
    
    env = Environment(loader=FileSystemLoader('/'))
    template = env.get_template(template_file)

    page = template.render({
      'nightly': nightly,
      'suite' : suite,
      'branch' : branch,
      'rpt_list' : report_list
    })

    # writing the  html file
    page_file = open('cony_Example.html', 'w')
    page_file.write(page)
    page_file.close()
    
draw_view()


