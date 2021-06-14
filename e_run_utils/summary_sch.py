# coding=utf-8
from LM.settings import DATABASES
from management.models import *
import pandas as pd
import pprint
pp = pprint.PrettyPrinter(indent = 2, depth = 3)

def do_summary():
    
    branches = ['dc-q2019.12_sp', 'dc-p2019.03_sp', 'dc-r2020.09_ls']

    summary = []

    for br in branches:
        ng_rns = NightlyRun.objects.using(br).all()
        for ng in ng_rns:
            extras = ng.scheduled_flows.all()
            for ex in extras:
                # print(br,ng.name, ex.name, ex.requestor, ex.approver, ex.title, ex.fm, ex.preferred_farm)
                job_load = len(ex.design_list.split())
                
                short_title = ex.title
                short_title = short_title.replace('(%s/%s)'%(ex.requestor, ex.approver),'')
                short_title = short_title.replace('(%s)'%ex.requestor, '')
                short_title = short_title.replace('(%s designs)'%str(job_load), '')

                rt_free = "(WARNING: not accurate for runtime comparison due to no machine assignment)"
                if rt_free not in short_title: rt_accurate = True
                else: 
                    rt_accurate = False
                    short_title = short_title.replace(rt_free, '')    
                
                # pp.pprint({
                #     'branch' : br,
                #     'nightly': ng.name.encode('utf-8'),
                #     'flow': ex.name.encode('utf-8'), 
                #     'RnD': ex.requestor.encode('utf-8'),
                #     'approver': ex.approver.encode('utf-8') if ex.approver else '', 
                #     'title': short_title, 
                #     'RT_accurate' : 'yes' if rt_accurate else 'no',   
                #     'Fm verication': 'yes' if ex.fm else 'no',
                #     'job load': job_load * 2 if ex.fm else job_load,
                # })

                summary.append({
                    'branch' : br,
                    'nightly': ng.name.encode('utf-8'),
                    'flow': ex.name.encode('utf-8'), 
                    'requestor': ex.requestor.encode('utf-8'),
                    'approver': ex.approver.encode('utf-8') if ex.approver else '', 
                    'title': short_title.encode('utf-8'), 
                    'rt_accurate' : 'yes' if rt_accurate else 'no',   
                    'fm_verification': 'yes' if ex.fm else 'no',
                    'job_load': job_load * 2 if ex.fm else job_load,
                    'sched_date': str(ex.scheduled_time)
                })

    
                    # print(ex.fm, ex.preferred_farm)
    ## writing insights    
    writer = pd.ExcelWriter('/slowfs/dcopt105/vasquez/utils/e_run_utils/scheduler_usage_summary.xlsx', engine='xlsxwriter')

    df = pd.DataFrame(summary)    
    mask = (df['sched_date'] > '2019-01-15') & (df['sched_date'] <= '2020-02-15')
    
    df = df.loc[mask]
    
    df[['branch','nightly','flow','requestor','approver','title','rt_accurate','fm_verification','job_load','sched_date']].to_excel(writer, sheet_name = 'all_data')

    df['requestor'].value_counts().to_excel(writer, sheet_name = 'flows_per_user')
    df['approver'].value_counts().to_excel(writer, sheet_name = 'flows_per_approvers')
    df['nightly'].value_counts().to_excel(writer, sheet_name = 'flows_per_nightly')
    df.groupby('requestor')['job_load'].agg('sum').sort_values(ascending=False).to_excel(writer, sheet_name = 'jobs_per_user')
    df.groupby('approver')['job_load'].agg('sum').sort_values(ascending=False).to_excel(writer, sheet_name = 'jobs_per_approver')
    df.groupby('nightly')['job_load'].agg('sum').sort_values(ascending=False).to_excel(writer, sheet_name = 'jobs_per_nightly')

    df.groupby('approver')['requestor'].value_counts().to_excel(writer, sheet_name = 'flows_group_by_approver')
    df.groupby(['approver', 'requestor'])['job_load'].agg('sum').to_excel(writer, sheet_name = 'jobs_group_by_approver')

    df['fm_verification'].value_counts().to_excel(writer, sheet_name = 'fm_usage')
    df['rt_accurate'].value_counts().to_excel(writer, sheet_name = 'rt_accuracy_usage')

    

    writer.save()
    print('written')
    return df
    #pp.pprint(result_df)


