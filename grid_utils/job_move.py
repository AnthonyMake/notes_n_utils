#!/slowfs/dcopt105/vasquez/cnda/Conda/bin/python
import os

import pprint
pp = pprint.PrettyPrinter(indent = 1, depth= 2)


new_user = 'estebanv'
branch  = '/remote/dcopt077/nightly_prs/p2019.03-SP/DC_ICC2'
nightly = 'D20190701_20_30'
flow    = 'SRM_ICC2_spg_opt_area'
designs = 'dcp564_leon3_mp_20_sset_ssink dcp579_pba_fp dcp426_opf_fp dcp569_GORDON dcp571_hrp_xb_m dcp778_datapath'.split(' ')

designs = '''
dcp522_c8docsis31_rx_top
dcp631_mercer
dcp632_teague
dcp517_PMA
dcp270_enterprise_UPF
dcp518_top
dcp519_fdeq_pnrb
dcp520_ccu_msw
'''.split('\n')

flow_path = os.path.join(branch,nightly,'prs/run',flow)


 # leaving a *.grd.out
            # Your job 8880921 ("SRM_ICC2_spg_opt_area%dcp579_pba_fp") has been submitted

# 8720895 ol_job


for design in designs:
    if os.path.isdir(flow_path):
        job_num = ''
        des_path = os.path.join(flow_path,design)
        try: 
            job_num = open('%s/%s/%s.grd.out'%(flow_path,design,design), 'r').readlines()[0].strip()
        except: 
            print('no grd file')

        cmd = 'qstat -j %s > old_job'%job_num
        # print(cmd)

        try : 
            os.system(cmd)
        except: 
            print("could not run <<<%s>>>"%cmd)

        qstat = open('old_job', 'r').readlines()

        qstat_dict ={}
        for line in qstat:
            line = line.strip()
            data = line.split(':')
            qstat_dict[data[0]] = ' '.join(data[1:]).strip()

        # no need to keep the old_job thing
        try: 
            os.system('rm -rf old_job')
        except:
            print('couldnt delete old_job file')

        #pp.pprint(qstat_dict)
        
        if qstat_dict != {}:
            print(design)
            #job_num : we already got this one
            owner      = qstat_dict['owner']
            submit_cmd = qstat_dict['submit_cmd']

            # look if qeued
            # qstat -u dcntqor6 | grep 8411133
            state_cmd = 'qstat -u %s | grep %s | tee short_state_job'%(owner,job_num)
            try:
                os.system(state_cmd)
            except:
                print('%s didnt work'%state_cmd)

            short_state = open('short_state_job','r').readlines()
            if short_state != []:
                short_state = short_state[0].split(' ')[11]

            print(short_state)

            if short_state == 'qw':    
                    
                # kill the job
                kill_cmd = 'rsh -l %s localhost \"qdel %s\"'%(owner,job_num)
                try:
                    #print(kill_cmd)
                    os.system(kill_cmd)
                except:
                    print('%s didnt work.'%kill_cmd)


                # resubmit the job with a new user
                re_sub_cmd = 'rsh -l %s localhost \"cd %s; %s\"| tee submit_log'%(new_user,des_path,submit_cmd) 
                try:
                    #print(re_sub_cmd)
                    os.system(re_sub_cmd)
                    # print(re_sub_cmd)
                except:
                    print('%s didnt work.'%re_sub_cmd)


                # leaving a *.grd.out
                # Your job 8880921 ("SRM_ICC2_spg_opt_area%dcp579_pba_fp") has been submitted
                new_job = open('submit_log', 'r').readlines()
                if new_job != []:
                    new_job = new_job[0].split(' ')[2]

                    new_grd_cmd = 'echo \"%s\"| tee %s/%s.grd.out'%(new_job,des_path,design)
                    try:
                        os.system(new_grd_cmd)
                    except:
                        print('%s didnt work'%new_grd_cmd)
            else:
                print('the job %s is in %s state '%(job_num,short_state))

        else:
            print('%s has no job in farm'%design)
            


