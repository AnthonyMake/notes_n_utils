#! /slowfs/dcopt105/vasquez/cnda/Conda/bin/python

from extra_hpd_functions import *
from pathlib import Path
import shutil

#################################################
# common settings                               #
#################################################

# branch          = '/remote/dcopt077/nightly_prs/q2019.12-SP'
# branch          = '/slowfs/dcopt036/nightly_prs/r2020.09_ls'
# branch          = '/remote/dcopt077/nightly_prs/p2019.03-SP'


output_dir = '/slowfs/dcopt105/vasquez/utils/local_profile'
new_dir_name = 'kotian_0602_2'

flows_loc = '/slowfs/dcopt036/nightly_prs/s2021.06_ls/DC_ICC2/D20210602_18_01/prs/run'
flow1 = 'SRM_ICC2_spg_timing_opt_area'
flow2 = 'SRM_ICC2_spg_timing_opt_area_ex4'
exec_bin = '/u/immgr/spf_s2021.06_rel/image_NIGHTLY/D20210602_18_01/linux64/syn/bin/dcnxt_shell'


# assuring the dirs
profile_dir = os.path.join(output_dir, new_dir_name)
if not os.path.exists(output_dir):
    print('target dir doesn\'t exists')
    exit()
else:
    if not os.path.exists(profile_dir):
        os.mkdir(profile_dir)

# making the links and setting permissions
# if not os.path.exists(os.path.join(profile_dir, flow1)):
#     os.symlink(
#         os.path.join(flows_loc, flow1),
#         os.path.join(profile_dir, flow1)
#     )

#     path_owner = Path(os.path.join(flows_loc, flow1)).owner()
#     os.system('rsh -l %s localhost "chmod 777 %s"' % (path_owner,os.path.join(flows_loc, flow1)))

if not os.path.exists(os.path.join(profile_dir, flow1)):
    os.mkdir(os.path.join(profile_dir,flow1))

    for des in os.listdir(os.path.join(flows_loc, flow1)):
        if 'exec.symb' not in des:
            os.symlink(
                os.path.join(flows_loc, flow1,des),
                os.path.join(profile_dir, flow1, des)
                )

if not os.path.exists(os.path.join(profile_dir, flow2)):
    os.mkdir(os.path.join(profile_dir,flow2))
    for des in os.listdir(os.path.join(flows_loc, flow2)):
        if 'exec.symb' not in des:
            os.symlink(
                os.path.join(flows_loc, flow2,des),
                os.path.join(profile_dir, flow2, des)
                )

# if not os.path.exists(os.path.join(profile_dir, flow2)):
#     os.symlink(
#         os.path.join(flows_loc, flow2),
#         os.path.join(profile_dir, flow2)
#     )

#     path_owner = Path(os.path.join(flows_loc, flow2)).owner()
#     os.system('rsh -l %s localhost "chmod 777 %s"' % (path_owner,os.path.join(flows_loc, flow2)))

# path = Path(os.path.join(flows_loc, flow1))
# print(path.owner())

if os.path.exists(os.path.join(profile_dir,'profile.html')):
    shutil.rmtree(os.path.join(profile_dir,'profile.html'))

# running the profile
profile_cmd = '/slowfs/dcopt105/vasquez/utils/local_profile/prprofile.pl '
profile_cmd += '-exec %s '%exec_bin
profile_cmd += '-dir profile.html ' 
profile_cmd += '-ocompare "%s,%s" ' % (flow1, flow2)
profile_cmd += '-tool "dcopt" '
profile_cmd += '-threshold 0.1 -fthreshold 0.5 -cthreshold 0.5 -prcache'

os.system('cd %s; %s' % (profile_dir,profile_cmd))

