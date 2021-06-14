#!/slowfs/dcopt105/vasquez/cnda/Conda/bin/python
import os, re 

import pprint
pp = pprint.PrettyPrinter(indent = 1, depth= 2)


new_user = 'rmorale'
branch  = '/slowfs/dcopt036/nightly_prs/q2019.12_ls/DC_ICC2'
nightly = 'D20190703_12_01'
flow_list = 'SRM_ICC2_spg_timing_opt_area'.split(' ')
designs = 'dcp570_b33 dcp569_GORDON dcp426_opf_fp A73_CPU dcp579_pba_fp A57_Non_CPU dcp778_datapath dcp564_leon3_mp_20_sset_ssink dcp571_hrp_xb_m archipelago_N12_6T'.split(' ')
designs = 'A72_CPU A73_CPU A57_CPU A57_Non_CPU BLOCK_CSN archipelago_N12_6T'.split(' ') 

#new_user = 'estebanv'
#branch  = '/slowfs/dcopt036/nightly_prs/q2019.12_ls/DC_ICC2'
#nightly = 'D20190701_12_01'
#flow_list  = 'SRM_ICC2_spg_timing_opt_area SRM_ICC2_spg_opt_area'.split(' ')
# designs = 'dcp564_leon3_mp_20_sset_ssink dcp579_pba_fp dcp426_opf_fp dcp569_GORDON dcp571_hrp_xb_m dcp778_datapath'.split(' ')

# designs = 'f4_dl2ri_cisco SC15_DS A72_CPU xpc_fp A73_CPU A57_CPU A57_Non_CPU A73_Non_CPU Vega20-CB-T BLOCK_CSN annapurna_maia_cpu f4_brw_cisco archipelago_N12_6T'.split(' ')
# designs = 'dcp570_b33 dcp609_CORTEXA8 dcp569_GORDON dcp426_opf_fp dcp778_datapath dcp571_hrp_xb_m'.split(' ')
# designs = 'dcp570_b33 dcp569_GORDON dcp426_opf_fp dcp579_pba_fp dcp778_datapath dcp564_leon3_mp_20_sset_ssink dcp571_hrp_xb_m'.split(' ')
 # leaving a *.grd.out:
            # Your job 8880921 ("SRM_ICC2_spg_opt_area%dcp579_pba_fp") has been submitted
        

for flow in flow_list:

    flow_path = os.path.join(branch,nightly,'prs/run',flow)

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
                    short_state = short_state[0].split()[4]

                #print(short_state)

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
                    # it's more tricky for some fancy accounts
                    # Your job 8880921 ("SRM_ICC2_spg_opt_area%dcp579_pba_fp") has been submitted

                    new_job_log = open('submit_log', 'r').readlines()
                    
                    ptrn_sub_job = r'Your\sjob\s([0-9]+)\s.+has\sbeen\ssubmitted'

                    new_job = None

                    for line in new_job_log:
                        m = re.match(ptrn_sub_job, line)    
                        if m: new_job = m.group(1)


                    if new_job != None:
                        new_grd_cmd = 'echo \"%s\"| tee %s/%s.grd.out'%(new_job,des_path,design)
                        try:
                            os.system(new_grd_cmd)
                        except:
                            print('%s didnt work'%new_grd_cmd)
                else:
                    print('the job %s is in %s state '%(job_num,short_state))

            else:
                print('%s has no job in farm'%design)