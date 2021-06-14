#!/slowfs/dcopt105/vasquez/cnda/Conda/bin/python
import os, re, argparse
##import pprint

## pp = pprint.PrettyPrinter(indent = 1, depth= 2)

parser = argparse.ArgumentParser(description='move qw jobs from the local flow to the specified user')

parser.add_argument('-user', type=str,
                    help='new user to re-submit jobs')

args = parser.parse_args()


new_user = args.user        
this_dir = os.getcwd() 

designs = os.listdir(this_dir)

for design in designs:

    print(design, end = ' ')
    grd_file = os.path.join(this_dir, design,'%s.grd.out'%design)

    if os.path.isfile(grd_file):


        print('is design', end = ' ')
        job_num = ''
        
        try: 
            job_num = open(grd_file, 'r').readlines()[0].strip()
        except: 
            print('couldnt open grd file')

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

            print('current state is %s'%short_state)

            if short_state == 'qw':    
                    
                print('re-submitting with %s...'%new_user)
                kill_cmd = 'rsh -l %s localhost \"/remote/sge3/default/bin/lx-amd64/qdel %s\"'%(owner,job_num)
                try:
                    #print(kill_cmd)
                    os.system(kill_cmd)
                except:
                    print('%s didnt work.'%kill_cmd)

                # resubmit the job with a new user

                re_sub_cmd = 'rsh -l %s localhost \"cd %s/%s; %s \"| tee submit_log'%(new_user,this_dir,design,submit_cmd) 
                
                try:
                    #print(re_sub_cmd)
                    os.system(re_sub_cmd)
                    #print(re_sub_cmd)
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
                    new_grd_cmd = 'echo \"%s\"> %s/%s/%s.grd.out'%(new_job,this_dir,design,design)
                    try:
                        os.system(new_grd_cmd)
                        #print(new_grd_cmd)
                    except:
                        print('%s didnt work'%new_grd_cmd)
            else:
                pass
                #print('the job %s is in %s state '%(job_num,short_state))

        else:
            print('%s has no job in farm'%design)

    else: 
        print('is not a valid designs dir. Skip')