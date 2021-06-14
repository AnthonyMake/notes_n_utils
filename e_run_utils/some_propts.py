from extra_hpd_functions import *


# branch = '/slowfs/dcopt036/nightly_prs/q2019.12_ls'
# suite = 'DC_ICC2'
# nightly = 'D20191023_18_01'


# flows = []
# flows.append({'flow' : 'SRM_ICC2_opt_area',  
#     'title' :  '<b> anniejo  DCT base line</b>',
#     'suffix' :  '_base',
# })

# flows.append({'flow' : 'SRM_ICC2_opt_area',  
#     'title' :  '<b> anniejo  DCT with embedded ONA for incr</b>',
#     'suffix' :  '_ex1',
# })

# flows.append({
#     'flow' : 'SRM_wlm',  
#     'title' :  '<b> anniejo SRM_wlm with opt area baseline</b>',
#     'suffix' :  '_base',
# })

# flows.append({
#     'flow' : 'SRM_wlm',  
#     'title' :  '<b> anniejo SRM_wlm with opt area baseline</b>',
#     'suffix' :  '_ex1',
# })


repeat = 5
dc_extra_settings = '' 
raw_extra_settings = ''
stages = 'DC ICC2'
dc_bin = ''
icc2_bin = ''
fm_bin = ''
fm_flow = ''
fm_extra_settings = ''

designs = 'A57_Non_CPU'
flow = 'SRM_ICC2_spg_opt_area'
# propts = os.path.join(branch,suite,nightly,'prs/r:un/propts.cfg')
propts = '/slowfs/dcopt105/vasquez/utils/testcases/mem_small_alloc/1126_mem_dbg/prs_propts.cfg'
debug = False
# report_name = 'dct_n_wlm_ona_mbed'
# report_script = 'subreport_srm_icc2_spg_opt_area.csh'

flist = []
dlist = []

for i in range(repeat):

    suffix = '_%s'%str(i)
    title = '%s + pwr_cg_activate_clkgt_data_rewiring false  #%s'%(flow, str(i))
 
    names, des = make_extra(
    
    flow, suffix, title, dc_extra_settings, raw_extra_settings, stages, dc_bin, icc2_bin, fm_bin, fm_flow, designs, propts, debug, fm_extra_settings
    
    )

    flist.append(names)
    dlist.append(des)

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
print('designs: %s'%designs)

propts_kick = '''
INCLUDE %s

flows: %s
designs: %s
'''%('%s/prs_propts.cfg'%target_dir, ' '.join(flist), ' '.join(dlist))

if not debug:
    propts_kick_file = open('%s/propts.cfg'%target_dir, 'w')
    propts_kick_file.write(propts_kick)
    propts_kick_file.close()










