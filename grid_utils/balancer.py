#!/slowfs/dcopt105/vasquez/cnda/Conda/bin/python
import os, re
import subprocess
import pprint
pp = pprint.PrettyPrinter(indent = 1, depth= 3)

def get_full_stat(farm ,job_num):
    
    farms = {
        'gala' : 'source /remote/sge/default/galapagos/common/settings.csh; set qstat_real = qstat',
        'snps' : 'source /remote/sge/default/snps/common/settings.csh; set qstat_real = qstat',
    }

    cmd = '%s; qstat -j %s'%(farms[farm],job_num)
    cmd_obj = subprocess.run(cmd, executable= '/bin/csh',shell = True,stdout=subprocess.PIPE)
    cmd_ret = cmd_obj.stdout.decode("utf-8").splitlines()

    stat = {}
    for line in cmd_ret:
        line = line.strip().split(':',1)

        if len(line) == 2:
            key = line[0].split()[0]
            
            stat[key] = str(line[1]).strip()
    
    return stat

def move_job(new_user, job_num, farm, debug):

    farms = {
        'gala' : 'source /remote/sge/default/galapagos/common/settings.csh; set qstat_real = qstat',
        'snps' : 'source /remote/sge/default/snps/common/settings.csh; set qstat_real = qstat',
    }

    old_stat = get_full_stat('gala',job_num)

    if 'job_state' not in old_stat.keys(): old_stat['job_state'] = '' 

    if  old_stat['job_state'] == '' or old_stat['job_state'] == 'Rq' or old_stat['job_state'] == 'qw':
        try:
            old_user = old_stat['owner']
            job_dir  = old_stat['cwd']
            submit_line  = old_stat['submit_cmd']

            design = job_dir.split('/')[-1]

            kill_old_cmd = 'rsh -l %s localhost \"%s; qdel %s; chmod 777 %s; chmod 777 %s/*;rm -rf %s/%s.grd.out;\"'%(old_user,farms[farm],job_num, job_dir, job_dir, job_dir,design)
            print(kill_old_cmd)
            if not debug:
                cmd_obj = subprocess.run(kill_old_cmd, executable= '/bin/csh',shell = True,stdout=subprocess.PIPE)
            
                #cmd_obj = subprocess.run(kill_old_cmd, executable= '/bin/csh',shell = True,stdout=subprocess.PIPE)
                #cmd_ret = cmd_obj.stdout.decode("utf-8").splitlines()

            re_sub_cmd   = 'rsh -l %s localhost \"%s; cd %s; %s \"'%(new_user,farms[farm],job_dir,submit_line)
            print(re_sub_cmd)
            if not debug:
                cmd_obj = subprocess.run(re_sub_cmd, executable= '/bin/csh',shell = True,stdout=subprocess.PIPE)
                cmd_ret = cmd_obj.stdout.decode("utf-8").splitlines()

                new_job = ''

                for line in cmd_ret:
                    line = line.strip().split()

                    if len(line) >= 3:
                        if (line[0]=='Your') and (line[1] == 'job'):
                            new_job = line[2]

                            if new_job != None:
                                new_grd_cmd = 'rsh -l %s localhost \"echo \'%s\'| tee %s/%s.grd.out\"'%(new_user,new_job,job_dir,design)
                                try:
                                    os.system(new_grd_cmd)
                                except:
                                    print('%s didnt work'%new_grd_cmd)
        except:
            pass
    
    else:
        print('%s is not queued. jobstate: %s.'%(job_num, old_stat['job_state']))            

    # Your job 832003 ("SRM_ICC2_timing_dcshell%dcp570_b33") has been submitted

def kill_job(farm,job_num):

    farms = {
        'gala' : 'source /remote/sge/default/galapagos/common/settings.csh; set qstat_real = qstat',
        'snps' : 'source /remote/sge/default/snps/common/settings.csh; set qstat_real = qstat',
    }

    job_info = get_full_stat(farm, job_num)

    if job_info != {}:
        kill_cmd   = 'rsh -l %s localhost \"%s; qdel %s \"'%(job_info['owner'], farms[farm], job_num)
        print(kill_cmd)
        cmd_obj = subprocess.run(kill_cmd, executable= '/bin/csh',shell = True,stdout=subprocess.PIPE)

    else:
        print('%s not exists.'%job_num)    

def get_user_groups(user):
    
    groups_cmd = 'rsh -l %s localhost \"groups\"'%user

    cmd_obj = subprocess.run(groups_cmd, executable= '/bin/csh',shell = True,stdout=subprocess.PIPE)
    cmd_ret = cmd_obj.stdout.decode("utf-8").split()

    # print(user, cmd_ret)
    return cmd_ret

def get_dir_group(user,dir):
    # needs to be consulted with the right user
    cmd = 'rsh -l %s localhost \"ll -d %s\"'%(user,dir)
    try :
        cmd_obj = subprocess.run(cmd, executable= '/bin/csh',shell = True,stdout=subprocess.PIPE)
        cmd_ret = cmd_obj.stdout.decode("utf-8").split()
        
        return cmd_ret[3]
    except:
        print('dir %s not found with user %s'%(dir, user))
        return ''
    
def get_user_load(farm, user):
    
    farms = {
        'gala' : 'source /remote/sge/default/galapagos/common/settings.csh; set qstat_real = qstat',
        'snps' : 'source /remote/sge/default/snps/common/settings.csh; set qstat_real = qstat',
    }

    cmd = '%s; qstat -u %s | wc'%(farms[farm],user)

    try :
        cmd_obj = subprocess.run(cmd, executable= '/bin/csh',shell = True,stdout=subprocess.PIPE)
        cmd_ret = cmd_obj.stdout.decode("utf-8").strip().split()
        
        return int(cmd_ret[0].strip()) - 2
    except:
        print('dir %s not found with user %s'%(dir, user))
        return ''

def change_conf(job_num, farm, config_file):

    farms = {
        'gala' : 'source /remote/sge/default/galapagos/common/settings.csh; set qstat_real = qstat',
        'snps' : 'source /remote/sge/default/snps/common/settings.csh; set qstat_real = qstat',
    }

    new_conf = open(config_file, 'r').read().splitlines()

    ptrn_cfg = 'des\.(\w+)\.grd\.opts:\s*(.+)'

    des_conf = {}

    for line in new_conf:
        
        ptrn_cfg = 'des\.(\w+)\.grd\.opts:\s*(.+)'
        
        m = re.match(ptrn_cfg, line)

        if m:
            des_conf[m.group(1)] = m.group(2)

    old_stat = get_full_stat('gala',job_num)
    

    if 'job_state' not in old_stat.keys(): old_stat['job_state'] = '' 

    print(old_stat['job_state'])

    if  old_stat['job_state'] == '' or old_stat['job_state'] == 'Rq' or old_stat['job_state'] == 'qw':
        try:
            old_user = old_stat['owner']
            new_user = old_user
            job_dir  = old_stat['cwd']
            submit_line  = old_stat['submit_cmd']
            
            design = old_stat['job_name'].split('%')[1] if '%' in old_stat['job_name'] else ''

            if design in des_conf:
                print('OLD: ', submit_line)
                ## lookng for the hconfig
                ptrn = '.+(-l\s*hconfig=\w+).+'
                m = re.match(ptrn, submit_line)

                if m:
                    submit_line = submit_line.replace(m.group(1),des_conf[design])
                    submit_line = submit_line.replace('l arch=glinux,os_bit=64', '')

                    print('NEW: ', submit_line)

                    kill_old_cmd = 'rsh -l %s localhost \"%s; qdel %s; chmod 777 %s; chmod 777 %s/*;rm -rf %s/%s.grd.out;\"'%(old_user,farms[farm],job_num, job_dir, job_dir, job_dir,design)
                    print(kill_old_cmd)
                    cmd_obj = subprocess.run(kill_old_cmd, executable= '/bin/csh',shell = True,stdout=subprocess.PIPE)
                    
                    #cmd_obj = subprocess.run(kill_old_cmd, executable= '/bin/csh',shell = True,stdout=subprocess.PIPE)
                    #cmd_ret = cmd_obj.stdout.decode("utf-8").splitlines()

                    re_sub_cmd   = 'rsh -l %s localhost \"%s; cd %s; %s \"'%(new_user,farms[farm],job_dir,submit_line)
                    print(re_sub_cmd)

                    cmd_obj = subprocess.run(re_sub_cmd, executable= '/bin/csh',shell = True,stdout=subprocess.PIPE)
                    cmd_ret = cmd_obj.stdout.decode("utf-8").splitlines()

                    new_job = ''

                    design = job_dir.split('/')[-1]

                    for line in cmd_ret:
                        line = line.strip().split()

                        if len(line) >= 3:
                            if (line[0]=='Your') and (line[1] == 'job'):
                                new_job = line[2]

                                if new_job != None:
                                    new_grd_cmd = 'rsh -l %s localhost \"echo \'%s\'| tee %s/%s.grd.out\"'%(new_user,new_job,job_dir,design)
                                    try:
                                        os.system(new_grd_cmd)
                                    except:
                                        print('%s didnt work'%new_grd_cmd)

                else:
                    print('No hconfig in submission command for %s %s'%(job_num,design))

            else: 
                print('No config found for %s'%design)


            # kill_old_cmd = 'rsh -l %s localhost \"%s; qdel %s; chmod 777 %s; chmod 777 %s/*;rm -rf %s/%s.grd.out;\"'%(old_user,farms[farm],job_num, job_dir, job_dir, job_dir,design)
            # print(kill_old_cmd)
            # cmd_obj = subprocess.run(kill_old_cmd, executable= '/bin/csh',shell = True,stdout=subprocess.PIPE)
            
            # #cmd_obj = subprocess.run(kill_old_cmd, executable= '/bin/csh',shell = True,stdout=subprocess.PIPE)
            # #cmd_ret = cmd_obj.stdout.decode("utf-8").splitlines()

            # re_sub_cmd   = 'rsh -l %s localhost \"%s; cd %s; %s \"'%(new_user,farms[farm],job_dir,submit_line)
            # print(re_sub_cmd)

            # cmd_obj = subprocess.run(re_sub_cmd, executable= '/bin/csh',shell = True,stdout=subprocess.PIPE)
            # cmd_ret = cmd_obj.stdout.decode("utf-8").splitlines()

            # new_job = ''

            # design = job_dir.split('/')[-1]

            # for line in cmd_ret:
            #     line = line.strip().split()

            #     if len(line) >= 3:
            #         if (line[0]=='Your') and (line[1] == 'job'):
            #             new_job = line[2]

            #             if new_job != None:
            #                 new_grd_cmd = 'rsh -l %s localhost \"echo \'%s\'| tee %s/%s.grd.out\"'%(new_user,new_job,job_dir,design)
            #                 try:
            #                     os.system(new_grd_cmd)
            #                 except:
            #                     print('%s didnt work'%new_grd_cmd)
        except:
            pass

    else:
        print('%s is not queued.'%job_num)            

    # Your job 832003 ("SRM_ICC2_timing_dcshell%dcp570_b33") has been submitted

#####################################################################

#user_ls = 'vasquez rmorale chunwang'.split()

#user_dict = {}

#for user in user_ls:
    # user_dict[user]  = {}
    # user_dict[user]['groups'] = get_user_groups(user)
    # user_dict[user]['load'] = get_user_load('gala',user)

#pp.pprint(user_dict)
#exit()
#job_list = '9569729 9569730 9569731 9569733 9569734 9569737 9569738 9569741 9569744 9569751 9569752 9569754 9569755 9569756 9569758 9833159 9833171 9833176 9833180 2223469 2223470 2223471 2223472 2223473 2223474 2223475 2223476 2223477 2223478 2223479 2223480 2223481 2223482 2223483 2223484 2223485 2223486 2223487 2223488 2223489 2223490 2223491 2223492 2223493 2223494 2223495 2223496 2223497 2223499 2223501 2223502 2223503 2223504 2223507 2223508 2223509 2223510 2223511 2223512 2223513 2223514 2223516 2223517 2223518 2223521 2223522 2223523 2223525 2223526 2223527 2223528 2223531 2223532 2223534 2223535 2223536 2223537 2223538 2223540 2223543 2223544 2223545 2223546 2223548 2223549'.split()
'''
job_list = '4045238'.strip().split()

# config = '/remote/pv/repo/dcnt/dcrt_prs_lib/gala_memusage_4c.cfg'

# print('dealing with %s jobs'%str(len(job_list_1)))

for job in job_list:
    kill_job('gala', job)

'''
#     # print(get_full_stat('snps', job)['submit_cmd'])
#     #move_job(new_user,job,'gala', False)
#     # initial checks before move
#     this_job=  get_full_stat('gala', job)
    
#     if this_job != {}:
#         j_owner = this_job['owner']
#         j_cwd   =  this_job['cwd']
#         dir_group = get_dir_group(j_owner, j_cwd)
        

#         if dir_group != '':
#             for user in user_dict:
#                 if dir_group in user_dict[user]['groups']:
#                     print('%s runnable by %s'%(job, user))
                    
#                     move_job(user,job,'gala', False)
                    
                    
#                     break
#                 else:
#                     print('%s not runnable by %s'%(job, user))

#     else:
#         print('job %s not found'%job)

    
    # print(get_dir_group(j_owner, j_cwd))

'''
rsh -l chunwang localhost "source /remote/sge/default/galapagos/common/settings.csh; set qstat_real = qstat; cd /remote/platform_pv1/Secure_Data_Run/pv_armip/FAST/chunwang/slowfs/pv_scratch18/24x7/dc/P-2019.03-SP/nightly_prs/DC_ICC2_ex/D20191104_20_30/run.24x7_gala-icc2_ex.chunwang/SRMFm_ICC2_spg_opt_area/A57_Non_CPU; qsub -N SRMFm_ICC2_spg_opt_area%A57_Non_CPU -cwd -j y -l arch=glinux,os_bit=64 -ac psp -js 150 -v preexec=./*.cmd0.csh -l 'minslotcpu=4' -l 'minslotmem=2G' -l arch=glinux ./A57_Non_CPU.all.csh
'''
# new_user = 'rmorale'

# job_list =  ''' 87536 87540 87546 87550 87555 87559 87563 87569 87580 87585 87126 87127 87128 87129 87131 87132 87133 87134 87135 87136 87137 87138 87140 87141 87142 87143 87144 87146 87147 87148 87150 87151 87152 87153 87154 87155 87156 87157 87159 87160 87161 87162 87163 87164 87165 87166 87167 87168 87169 87170 87172 87174 87175 87176 87177 87178 87179 87180 87181 87183 87184 87185 87186 87187 87188 87189 87191 87192 87193 87194 87196 87197 87198 87200 87201 87202 87203 87204 87206 87207 87208 87209 87210 87211 87212 87214 87215 87216 87217 87218 87219 87220 87221 87223 87224 87225 87226 87227 87228 87229 87230 87231 87232 87233 87234 87235 87236 87237 87238 87240 87241 87242 87244 87245 87246 87247 87248 87250 87251 87252 87253 87254 87255 87256 87258 87259 87260 87261 87263 87264 87265 87266 87267 87268 87270 87271 87272 87273'''.split()

# for job in job_list:
#     move_job(new_user,job,'gala')
# '''
# rsh -l estebanv localhost "source /remote/sge/default/galapagos/common/settings.csh; set qstat_real = qstat; qdel 87125"
# rsh -l rmorale localhost "source /remote/sge/default/galapagos/common/settings.csh; set qstat_real = qstat; cd /slowfs/pv_scratch18/24x7/dc/P-2019.03-SP/nightly_prs/DC_ICC2/D20191007_20_30/run.24x7_gala-icc2.estebanv/SRM_ICC2_timing_dcshell/dcp570_b33; qsub -N SRM_ICC2_timing_dcshell%dcp570_b33 -cwd -j y -l arch=glinux,os_bit=64 -ac psp -l hconfig=bwl24d2a4 -l arch=glinux ./dcp570_b33.all.csh "
# '''
#print(get_full_stat('gala',job_num)['cwd'])
