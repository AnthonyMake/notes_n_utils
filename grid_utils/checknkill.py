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
        
        return int(cmd_ret[0].strip())
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

# user_ls = 'chunwang rmorale'.split()

# user_dict = {}

# for user in user_ls:
#     user_dict[user]  = {}
#     user_dict[user]['groups'] = get_user_groups(user)
#     user_dict[user]['load'] = get_user_load('gala',user)

# pp.pprint(user_dict)
#exit()
#job_list = '9569729 9569730 9569731 9569733 9569734 9569737 9569738 9569741 9569744 9569751 9569752 9569754 9569755 9569756 9569758 9833159 9833171 9833176 9833180 2223469 2223470 2223471 2223472 2223473 2223474 2223475 2223476 2223477 2223478 2223479 2223480 2223481 2223482 2223483 2223484 2223485 2223486 2223487 2223488 2223489 2223490 2223491 2223492 2223493 2223494 2223495 2223496 2223497 2223499 2223501 2223502 2223503 2223504 2223507 2223508 2223509 2223510 2223511 2223512 2223513 2223514 2223516 2223517 2223518 2223521 2223522 2223523 2223525 2223526 2223527 2223528 2223531 2223532 2223534 2223535 2223536 2223537 2223538 2223540 2223543 2223544 2223545 2223546 2223548 2223549'.split()

job_list_1 = '''
1579069 dcntqor6   normal     african851        0%   63h     0.0   7644   5098  SRM_ICC2_spg_opt_area%dcp246_Xm_Xtmem
1579588 dcntqor7   normal     african835        0%   94h     0.0   4523   1971  *pt_area_rc_correlation%dcp611_arm926ejs
2160598 dcntqor6   normal     african173        0%   25h     0.0   4532   2007  UPF_SRM%dcp611_arm926ejs_snet_diff
2161752 dcntqor6   normal     african839        0%   40h     0.0   7682   5120  *CC2_spg_timing_opt_area%dcp246_Xm_Xtmem
2145718 dcntqor6   normal     african809        0%   32h     0.0   4555   2038  UPF_SRM%dcp611_arm926ejs_sset
1579043 dcntqor6   normal     rock100           0%   85h     0.0   7287   4753  *g_opt_area_rc_correlation%dcp569_GORDON
1109912 dcntqor6   normal     african202        0%  101h     0.0   7670   5097  *spg_timing_opt_area_ex4%dcp246_Xm_Xtmem
2145757 dcntqor6   normal     rock158           0%   35h     0.0   6911   4784  *shell_spg_timing_opt_area%dcp569_GORDON
2161962 dcntqor7   normal     african833        0%   45h     0.0   4570   2024  *C2_spg_timing_opt_area%dcp611_arm926ejs
2160489 dcntqor6   normal     african810        0%   25h     0.0   4559   2042  UPF_SRM_libsetup%dcp611_arm926ejs
1051880 dcntqor7   normal     chin245           0%  103h     0.0  14055  11531  SRM_ICC2_timing%dcp270_enterprise_UPF
1579595 dcntqor7   normal     african087        0%   50h     0.0   4555      2  SRM_ICC2_spg_opt_area%dcp611_arm926ejs
1350414 dcntqor6   normal     rock151           0%   87h     0.0   8619   6075  *_opt_area%dcp564_leon3_mp_20_sset_ssink
2148239 dcntqor7   normal     african211        0%   48h     0.0   4550   2026  *C2_spg_timing_opt_area%dcp611_arm926ejs
1580812 dcntqor6   normal     african852        0%   88h     0.0   7677      0  *CC2_spg_timing_opt_area%dcp246_Xm_Xtmem
1960659 dcntqor6   normal     african097        0%   60h     0.0   4553   1975  *timing_opt_area_vex_02%dcp611_arm926ejs
155523 dcntqor7   normal     rock163           0%    7h     0.0   5490   2979  UPF_SRM_libsetup%upf564_leon3_01_sc
1557060 dcntqor7   normal     african859        0%   50h     0.0   4553   2026  *_timing_power_opt_area%dcp611_arm926ejs
1960622 dcntqor6   normal     chin234           0%   56h     0.0   9573   7363  *g_opt_area_vex_02%dcp270_enterprise_UPF
2147825 dcntqor6   normal     rock091           0%   35h     0.0   7290   4764  *_ICC2_spg_timing_opt_area%dcp569_GORDON
2147116 dcntqor7   normal     chin111           0%   21h     0.0  14104  11515  UPF_SRM%dcp270_enterprise_UPF
2147292 dcntqor7   normal     african091        0%   24h     0.0   4539   2031  SRM_ICC2_spg_opt_area%dcp611_arm926ejs
2160600 dcntqor6   normal     african224        0%   25h     0.0   4530      0  *SRM_libsetup%dcp611_arm926ejs_snet_diff
2147295 dcntqor7   normal     african079        0%   24h     0.0   4553   2040  SRM_ICC2%dcp611_arm926ejs
2161860 dcntqor6   normal     rock222           0%   14h     0.0   8546   6019  *_opt_area%dcp564_leon3_mp_20_sset_ssink
2145874 dcntqor6   normal     african206        0%   29h     0.0   4534      0  UPF_SRM%dcp611_arm926ejs_sset_ssink
2161137 dcntqor7   normal     african068        0%   23h     0.0   4543   2027  SRM_ICC2_spg_opt_area%dcp611_arm926ejs
2160644 dcntqor6   normal     african061        0%   25h     0.0   4531   2009  UPF_SRM_gupf%dcp611_arm926ejs_sset_diff
2145926 dcntqor6   normal     african850        0%   29h     0.0   4523   2008  *SRM_libsetup%dcp611_arm926ejs_sset_diff
2160547 dcntqor6   normal     african227        0%   25h     0.0   4559   2032  UPF_SRM_libsetup%dcp611_arm926ejs_iss
2145876 dcntqor6   normal     african823        0%   29h     0.0   4562   2050  UPF_SRM_gupf%dcp611_arm926ejs_sset_ssink
2160584 dcntqor6   normal     african851        0%   25h     0.0   4565   2036  *RM_libsetup%dcp611_arm926ejs_sset_ssink
2160480 dcntqor6   normal     african191        0%   25h     0.0   4561   2039  UPF_SRM_gupf%dcp611_arm926ejs_sset
2147123 dcntqor7   normal     chin209           0%   21h     0.0  14029  11518  SRM_ICC2%dcp270_enterprise_UPF
2147111 dcntqor7   normal     chin240           0%   20h     0.0  14097  11972  SRM_ICC2_dcshell%dcp270_enterprise_UPF
2147117 dcntqor7   normal     chin117           0%   21h     0.0  14019  11507  UPF_SRM_libsetup%dcp270_enterprise_UPF
154901 dcntqor6   normal     rock221           0%    9h     0.0   7277   4764  *spg_timing_power_opt_area%dcp569_GORDON
2160645 dcntqor6   normal     african049        0%   25h     0.0   4529   2006  *SRM_libsetup%dcp611_arm926ejs_sset_diff
2148067 dcntqor7   normal     rock225           0%    5h     0.0  37822  35324  *pg_timing_opt_area%A75_prometheus_PAC16
1104984 dcntqor7   normal     chin106           0%   65h     0.0  14047  11522  SRM_ICC2_ex1%dcp270_enterprise_UPF
2147717 dcntqor6   normal     african175        0%   23h     0.0   7020     80  *M_ICC2_spg_opt_area_NDM%dcp246_Xm_Xtmem
2160509 dcntqor6   normal     african095        0%   21h     0.0   7620   5088  SRM_ICC2_spg_opt_area%dcp246_Xm_Xtmem
1558437 dcntqor6   normal     african803        0%   64h     0.1   7619   5096  SRMFm_ICC2_spg_opt_area%dcp246_Xm_Xtmem
2147727 dcntqor6   normal     african843        0%   21h     0.0   7361   4819  SRM_ICC2_spg_opt_area_NDM%X5376
2147718 dcntqor6   normal     african227        0%   43h     0.1   7676   5141  *CC2_spg_timing_opt_area%dcp246_Xm_Xtmem
2160128 dcntqor7   normal     chin251           0%   24h     0.1  12301   9746  SRM_plvt_spg%dcp523_rds_testpd_topio
155514 dcntqor7   normal     rock067           0%    7h     0.0   5493   2980  UPF_SRM%upf564_leon3_01_sc
155568 dcntqor7   normal     rock123           0%    5h     0.1   7327   4813  UPF_SRM_gupf%dcp569_GORDON
155569 dcntqor7   normal     rock134           1%    5h     0.1   7286   4746  UPF_SRM_libsetup%dcp569_GORDON
9415546 dcntqor6   normal     white015          1%    7d     2.7   281g   165g  SRM_ICC2_spg_timing_opt_area_ex7%xpc_fp
1051820 dcntqor7   normal     white044          1%  101h     1.6   281g   163g  *ing_opt_area_link_placer_ATCnBAP%xpc_fp
9399807 dcntqor7   normal     white098          1%    7d     3.1   280g   140g  SRM_ICC2_spg_timing_opt_area_ex4%xpc_fp
1051814 dcntqor7   normal     white068          2%  101h     2.3   306g   154g  *nk_placer_ATCnBAP_rc_correlation%xpc_fp
1051821 dcntqor7   normal     white037          2%  102h     2.4   288g   157g  *pt_area_link_placer_All_features%xpc_fp
'''.strip().splitlines()

config = '/remote/pv/repo/dcnt/dcrt_prs_lib/gala_memusage_4c.cfg'

print('dealing with %s jobs.'%str(len(job_list_1)))

for job in job_list_1:
    # kill_job('gala', job)
    # print(get_full_stat('snps', job)['submit_cmd'])
    #move_job(new_user,job,'gala', False)
    # initial checks before move

    job = job.strip().split()[0]

    this_job=  get_full_stat('gala', job)
    
    if this_job != {}:
        j_owner = this_job['owner']
        j_cwd   =  this_job['cwd']
        dir_group = get_dir_group(j_owner, j_cwd)
        

        # check where its hanged
        # tailored for dcrpt - write plots case
        design = j_cwd.split('/')[-1]
        dcrpt_file = os.path.join(j_cwd, design +'.dcrpt.out')

        if os.path.isfile(dcrpt_file):
            dcrpt_end = open(dcrpt_file, 'rb').read().decode(encoding='utf-8', errors ='ignore').splitlines()[-5:]
            #dcrpt_end = 

            for line in dcrpt_end:
                print(line)
                
                if 'prs_write_plots' in line:
                    print('%s job %s is writing plots, going to kill...'%(design, job), end=' ')

                    kill_job('gala', job)

                    print('killed!')
                    break

                else:
                    print('%s job %s is not writing plots. doing nothing.'%(design,job))
                    print('last line was: %s'%line)

    else:
        print('job %s not found'%job)

    
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
