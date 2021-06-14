from extra_hpd_functions import *

target_dir = '/slowfs/dcopt105/vasquez/utils/testcases/1223_tim_deg'
target_propts = '/remote/dcopt077/nightly_prs/q2019.12-SP/DC_ICC2/D20191223_20_30/prs/run/propts.cfg'
designs = ''
flows = 'SRM_ICC2_spg_timing_opt_area'.split(' ')

repeat             = 1
dc_extra_settings  = ''
raw_extra_settings = ''
fm_extra_settings  = ''
stages             = 'DC FM'
dc_bin_list        = ''
icc2_bin           = ''
fm_bin             = 'some_fancy_fm_bin'
fm_flow            = 'SRMFm_ICC2_spg_timing_opt_area'

debug = True
# copy propts
new_t_propts = '%s/prs_propts.cfg'%target_dir
shutil.copy2(target_propts, new_t_propts)

flist = []
dlist = []

for dc_bin in dc_bin_list:
    
    for flow in flows:
        
        suffix = '_' + dc_bin.split('/')[6] + '_'
        title = '%s %s'%(dc_bin.split('/')[6],dc_bin.split('/')[10])
 
        names, des = make_extra(
        
        flow, suffix, title, dc_extra_settings, raw_extra_settings, stages, dc_bin, icc2_bin, fm_bin, fm_flow, designs, new_t_propts, debug, fm_extra_settings

        )

        flist.append(names )
        
        if designs != '':
            for d in designs.strip().split():
                if d not in dlist: dlist.append(d) 
        else:
            for d in des.strip().split():
                if d not in dlist: dlist.append(d) 
        

# add_regular_report(
#     branch = branch,
#     suite = suite,
#     nightly = nightly,
#     debug = debug,
#     baseline = flist[0],
#     flows = ' '.join(flist),
#     report_name= report_name,
#     report_script = report_script,
# )

# for i in range(len(flist)):
#      print('-----kick lines -----\n')
print('flows: %s'%' '.join(flist))
print('designs: %s'%' '.join(dlist))

# create propts for kick-off
propts_kick = '''
INCLUDE %s

flows: %s
designs: %s
'''%('%s/prs_propts.cfg'%target_dir, ' '.join(flist), ' '.join(dlist))

if not debug:
    propts_kick_file = open('%s/propts.cfg'%target_dir, 'w')
    propts_kick_file.write(propts_kick)
    propts_kick_file.close()











