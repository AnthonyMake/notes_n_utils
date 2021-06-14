#!/slowfs/dcopt105/vasquez/cnda/Conda/bin/python
 
import pickle, os, re
import datetime, subprocess
import pandas as pd
from pandas import ExcelWriter
import xml.etree.ElementTree as et
import datetime
from balancer import *
from datetime import datetime
from jinja2 import Template, Environment, FileSystemLoader
# Mongo db
from pymongo import MongoClient


import pprint
pp = pprint.PrettyPrinter(indent = 1, depth= 2)


def draw_summary():
    client    = MongoClient('pvdc002', 27017)
    dc_db     = client.dcnxt_data
    farm_data = dc_db['farm'].find({})

    snapshots_all = sorted(farm_data, key=lambda i:i['timestamp'])
    last_snapshot = snapshots_all[-1]

    tab_headers = [*last_snapshot['jobs_data'][0]]
    tab_headers.pop(2)

    run_tot  = [snp['extra_reg_summary']['running']['total'] for snp in snapshots_all][-350:]
    run_ext  = [snp['extra_reg_summary']['running']['ext'] for snp in snapshots_all][-350:]
    run_reg  = [snp['extra_reg_summary']['running']['reg'] for snp in snapshots_all][-350:]

    pend_tot = [snp['extra_reg_summary']['pending']['total'] for snp in snapshots_all][-350:]
    pend_ext = [snp['extra_reg_summary']['pending']['ext'] for snp in snapshots_all][-350:]
    pend_reg = [snp['extra_reg_summary']['pending']['reg'] for snp in snapshots_all][-350:]

    labels   = [snp['timestamp'].strftime('%m%d-%H:%M') for snp in snapshots_all][-350:]
    
    template_file = '/slowfs/dcopt105/vasquez/utils/job_pusher/farm_summary.jinja'
    env = Environment(loader=FileSystemLoader('/'))
    template = env.get_template(template_file)

    all_jobs_ETA = (last_snapshot['extra_reg_summary']['running']['total'] + last_snapshot['extra_reg_summary']['pending']['total']) / last_snapshot['avg_outflow'] / 24 # days

    page = template.render({
      'last_snapshot' : last_snapshot,
      'tab_headers'   : tab_headers,
      'run_tot'       : run_tot,
      'run_ext'       : run_ext,
      'run_reg'       : run_reg,
      'pend_tot'      : pend_tot,
      'pend_ext'      : pend_ext,
      'pend_reg'      : pend_reg,
      'labels'        : labels,
      'all_jobs_ETA'  : all_jobs_ETA
    })

    page_file = open('farm_summary.html', 'w')
    page_file.write(page)
    page_file.close()
    

draw_summary()




'''
# # Mongo Stuff
client    = MongoClient('pvdc002', 27017)
dc_db     = client.dcnxt_data
farm_data = dc_db['farm'].find({})






obj    = sorted(farm_data, key=lambda i:i['timestamp'])
latest = obj[-1]
pp.pprint(obj[-1]['inflow'])
pp.pprint(obj[-1]['outflow'])

exit()

# jb_num = '1793472'
# for j in d['jobs_data']:
#     if j['job_number']== jb_num:
#         pp.pprint(j['job_state'])
         
# exit()
le_stamp = d['timestamp'].strftime('%Y%m%d_%H%M')
print(le_stamp)

print('\n\nUSERS')
pp.pprint(d['users_summary'])

print('\nMACHINES')
pp.pprint(d['hconfig_summary'])

print('\nExtra vs Regular')
pp.pprint(d['extra_reg_summary'])

#pp.pprint(d)



headers = [*d['jobs_data'][0]]
#print(headers)

# pp.pprint(d['jobs_data'])
# exit()

csv = ''
csv_hline = []
for h in headers: 
    csv_hline.append('"%s"'%h)

csv += '%s\n'%(','.join(csv_hline))


for jb in d['jobs_data']:
    csv_line = []
    for h in headers:
        csv_line.append('"%s"'%jb[h])
    csv += '%s\n'%(','.join(csv_line))


le_stamp = d['timestamp'].strftime('%Y%m%d_%H%M')

print('writting csv...')
csv_file = open('snapshots/qstat_%s.csv'%le_stamp, 'w')
csv_file.write(csv)
csv_file.close()

print('done.')
#(2021,03,23,22,07,54,160501)
#obj_time = datetime(2021, 3, 23, 22, 13, 3, 479000)
#farm_dict = farm_data.find({})
# farm_data.delete_one({'timestamp':'20210322_0911'})
# exit()
#pp.pprint(farm_dict)

# exit()
#index = []
#for coll in farm_dict:
#      pp.pprint(coll['timestamp'])
      
#      index.append(coll['timestamp'])
#index.sort()

#print(index[-1])

'''