#!/slowfs/dcopt105/vasquez/cnda/Conda/bin/python
import os, re
import subprocess
import pprint
pp = pprint.PrettyPrinter(indent = 1, depth= 2)

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
                    # submit_line = submit_line.replace('l arch=glinux,os_bit=64', '')

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

job_list_1 = '''
2883710 2883695 2883731 2883734 2882640 2883725 2883740 2883716 2883792 2882648 2882619 2882629 2883692 3128064 2883751 2882702 2883728 2882651 2882654 2883743 2882675 2882663 2883763 2883768 2882616 2883737 2883777 2883771 2883789 2883707 2882714 2882626 2882693 2883786 2882745 2882734 2883704 2882672 2883701 2883713 2883719 2883783 2883698 2882660 2883722 9761059 9761029 9761096 9761101 9760767 9761086 9761112 9761069 9761171 9760772 9760746 9760762 9761023 9761141 9761121 9760832 9761090 9760776 9760782 9761116 9760817 9760798 9761127 9761131 9760739 9761106 9761145 9761137 9761165 9761055 9760836 9760758 9760826 9761161 9760856 9760846 9761049 9760813 9761043 9761064 9761075 9761157 9761037 9760792 9761080 9888702 9888676 9888750 9888758 9888515 9888738 9888773 9888715 9888866 9888520 9888483 9888508 9888669 9888821 9888787 9888601 9888744 9888527 9888538 9888781 9888585 9888568 9888795 9888802 9888475 9888766 9888826 9888809 9888857 9888695 9888606 9888502 9888598 9888848 9888636 9888620 9888688 9888582 9888684 9888708 9888720 9888840 9888681 9888560 9888733 635217 635202 635242 635245 635139 635236 635251 635223 635288 635142 635127 635136 635199 635269 635257 635178 635239 635145 635148 635254 635169 635157 635260 635263 635124 635248 635272 635266 635285 635214 635181 635133 635175 635282 635193 635187 635211 635166 635208 635220 635228 635279 635205 635154 635233 920854 920712 649650 649653 648609 649606 649657 649599 649681 648614 648583 648600 649631 649667 649661 648540 649647 648513 648516 649616 648649 648525 649664 649619 648573 649610 649625 649622 649678 649588 648548 648590 648534 649674 648673 648558 649641 648637 920808 920900 921247 649628 649585 648522 649644 770585 770570 770606 770609 770503 770600 770615 770591 770651 770506 770491 770500 770567 770633 770621 770542 770603 770509 770512 770618 770533 770521 770624 770627 770488 770612 770636 770630 770648 770582 770545 770497 770539 770645 770557 770551 770579 770530 770576 770588 770594 770642 770573 770518 770597 1245686 1245645 1245746 1245761 1245133 1245728 1245774 1245698 1245861 1245141 1245088 1245121 1245636 1245821 1245791 1245240 1245739 1245146 1245154 1245783 1245209 1245176 1245798 1245804 1245080 1245767 1245830 1245809 1245856 1245678 1245246 1245109 1245234 1245851 1245281 1245261 1245673 1245201 1245668 1245693 1245708 1245846 1245658 1245171 1245712 2983331 2980570 4653302 3161454 3984905 3184730 3208431 4522971 3102191 3218791 3218084 3236080 1702048 2942938 3228931 3229050 3243977 3220228 4042260 3179196 3220509 3231073 3218848 3432117 4080266 3924272 4036816 3950211 4001113 4226497 3725211 3235721 3236662 3348898 3218792 3223569 3216334 4109523 4080265 3707256 4340932 4194194 3286072 3866149 3832384 2367146 3912096 4490565 3947340 3934243 2367131 3794351 4116648 4109583 4177462 2367222 3759595 4180888 4468976 4161259 4141383 4689879 4166550 4174977 4183275 4183279 4202875 2367162 4577874 2367210 4606612 4579419 2366919 4426554 4159774 2859878 2859910 4278670 4465355 4515936 4668355 4699598 4528085 2367239 2367117 4173683 4366075 4313569 2774806 4496942 2774617 4524848 4528101 2774791 4435284 2774623 2774599 2774613 2774767 2774833 4267876 2774676 2774803 2774628 2774632 2774818 2774665 2774644 2774824 2774827 2774595 2774812 2774836 2774830 2774848 2774782 2774681 2774610 2774672 2774845 2774735 2774726 2774779 2774659 2774776 2774788 2774794 2774842 2774773 2774641 2774797
'''

config = '/remote/pv/repo/dcnt/dcrt_prs_lib/gala_memusage_4c.cfg'

all_jobs = job_list_1.split()

print('dealing with %s jobs'%str(len(all_jobs)))

for jb in all_jobs:
    kill_job('gala', jb)



exit()
for line in job_list_1:
    line = line.strip().split()
    job = line[0]
    
    kill_job('gala', job)
    # print(get_full_stat('snps', job)['submit_cmd'])
    #move_job(new_user,job,'gala', False)
    # initial checks before move
    
    # change_conf(job,'gala',config)

    # this_job=  get_full_stat('gala', job)
    # j_owner = this_job['owner']
    # j_cwd   =  this_job['cwd']
    # dir_group = get_dir_group(j_owner, j_cwd)
    
    # if dir_group != '':
    #     if dir_group in get_user_groups(new_user):
    #         print('%s runnable by %s'%(job, new_user))

    #     else:
    #         print('%s not runnable by %s'%(job, new_user))


    
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
