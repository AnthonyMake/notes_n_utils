#!/slowfs/dcopt105/vasquez/cnda/Conda/bin/python3.6
import yaml, sys, os, re, pickle, xml.etree.ElementTree, copy, subprocess, datetime, time
from pathlib import Path
from dask.distributed import Client,wait

#c5 = Client('pv128g005:8786')
c3 = Client('pv128g002:8786')

def create_health_dict(WORK_DIR, nightly_amount, tool, branch, suite, flows, users, opt, distributed):
	# Output dictionary
	health_dict = {tool: {branch:{suite:{}}}}
	### PARAMETERS ###
	T_FORMAT = "%Y-%m-%d %H:%M:%S"
	snapshot = datetime.datetime.now().strftime('%Y%m%d_%H%M')

	branch_name = branch.split("/")[-1]

	# Getting nightly images up to <nightly_amount>
	nightly_image_file = open('{}/{}/images.txt'.format(branch, suite))
	nightly_images = nightly_image_file.read().split('\n')
	nightly_image_file.close()

	while '' in nightly_images:
		nightly_images.remove('')
	nightly_images.reverse()  # for displaying purposes

	# Listing all '...prs/run' paths of designs in a nightly:
	nightly_path_list = []
	for nightly in nightly_images:
		if os.path.isdir('{}/{}/{}/prs/run'.format(branch, suite, nightly)):
			nightly_path_list.append('{}/{}/{}/prs/run'.format(branch, suite, nightly))


	# Gathering job data of <users> by using monrun :
	users_jobs = {}
	for u in users:
		print('issuing call to monrun for %s'%u)
		monrun_jobs = os.popen('/usr/bin/tcsh /remote/sge/default/galapagos/common/settings.csh; monrun -all -sort swap -wide -u {} -raw'.format(u)).read().split('\n')
		
		for u_job in monrun_jobs:
			u_job_listed = u_job.replace('\n',"").split(':')
			users_jobs[u_job_listed[0]] = dict(zip(['JOBID', 'USER','PROJECT','HOST','UNKNOWN','UTIL','TIME','HOURS','SWAP','RAM','JOB'],u_job_listed))

	# Only reading up to <nightly_amount> nightlies:
	nightly_count = 0

	for nightly_path in nightly_path_list:
		nightly = nightly_path.split("/")[-3]

		###################################################
		# inside nightly iteration
		# here i pretend to parallelize
		###################################################
		print('submitting collection of prs status for nightly %s...'%nightly)
		
		if distributed:
			health_dict[tool][branch][suite][nightly] = c3.submit(health_collection_nightly,nightly_amount, nightly_path, nightly_count, opt, flows, users_jobs, tool, branch, suite, nightly, T_FORMAT)
		
		else:
			health_dict[tool][branch][suite][nightly] = health_collection_nightly(nightly_amount, nightly_path, nightly_count, opt, flows, users_jobs, tool, branch, suite, nightly, T_FORMAT)
		
		nightly_count += 1
		if nightly_count >= nightly_amount:
			break
		# if not health_dict[tool][branch][suite][nightly]:
		# 		del health_dict[tool][branch][suite][nightly]

	if distributed:
		# await results
		for nightly in health_dict[tool][branch][suite]:
			# print('awaiting %s results to complete...', end = '')
			try:
				health_dict[tool][branch][suite][nightly] = health_dict[tool][branch][suite][nightly].result(30)
				print(nightly, 'Data Received')
			except:
				print(nightly, 'Timeout exceeded, continue...')
				health_dict[tool][branch][suite][nightly] = None

	print('all done!')

	return health_dict;


def health_collection_nightly(nightly_amount, nightly_path, nightly_count, opt, flows, users_jobs, tool, branch, suite, nightly, T_FORMAT):
	
	mid_dict = {}
	if os.path.isdir(nightly_path) and nightly_count < int(nightly_amount) and '.link' not in nightly_path:
		print('Gathering info from {}'.format(nightly_path))
		nightly_count += 1
		
		# Gathering job number:
		print('Collecting data from nightly...')
		#mid_dict = {}
		# mid_dict = {}
		
		# just some workaround to avoid burocracy 
		for flow in flows:
			print('\t{}...'.format(flow))
			mid_dict[flow] = {}
			design_dir = '{}/{}'.format(nightly_path, flow)
			if os.path.isdir(design_dir):
				designs = os.listdir(design_dir)
				if designs and designs[0]=='propts.cfg':
					designs.remove('propts.cfg')
				design_job_dict = {}
				for design in designs:

					DESIGN_DIR = '{}/{}/{}'.format(nightly_path, flow, design)
					# .grd.out file, which contains job number
					design_grd_path = '{}/{}.grd.out'.format(DESIGN_DIR, design)
					if os.path.isdir(DESIGN_DIR) and os.path.isfile(design_grd_path):
						#print('\t\t{}...'.format(design))
						# Getting job number 
						job_file = open(design_grd_path)
						job_number = re.sub('\n', '', job_file.read())
						job_file.close()
						mid_dict[flow][design] = {}
						#adding job numbers -vasquez-
						mid_dict[flow][design]['grd_job_num'] = job_number
						
						if job_number in users_jobs:
							### Job data:
							mid_dict[flow][design]['monrun_data'] = users_jobs[job_number].copy()

						else:
							### No job data available:
							mid_dict[flow][design] = {}
							mid_dict[flow][design]['grd_job_num'] = job_number
						
						## change this to native python utility -vasquez-
						
						### Design output directory owner ###
						# process = os.popen('stat -c "%U" {}'.format(DESIGN_DIR))
						# design_dir_owner = process.read().replace('\n',"")
						# process.close()
						# mid_dict[flow][design]['owner'] = design_dir_owner
						
						des_path = Path(DESIGN_DIR)
						design_dir_owner = des_path.owner()
						mid_dict[flow][design]['owner'] = design_dir_owner
						##################################################


						### Disk usage from this job's directory: stat -c "%U"
						process = os.popen('du -sh {}/'.format(DESIGN_DIR))
						design_disk_usage = process.read().split()
						mid_dict[flow][design]['design_disk_usage'] = design_disk_usage
						process.close()

						### Design disk data from this job's directory:
						process = os.popen('df -Ph {}/'.format(DESIGN_DIR))
						design_disk_data = process.read().replace("Mounted on", "Mounted").split()
						process.close()
						mid_dict[flow][design]['design_disk_data'] = dict(zip(design_disk_data[0:6], design_disk_data[6:12]))

						### all.csh steps ###
						if os.path.isfile('{}/{}.all.csh'.format(DESIGN_DIR, design)):
							file = open('{}/{}.all.csh'.format(DESIGN_DIR, design),'r')
							allcsh_lines = file.read().split('\n')
							file.close()
							# list containing all.csh <steps>.out filenames:
							allcsh_out = []
							for line in allcsh_lines:
								if './' in line and len(line.split(" >& ")) > 1:
									# name of <step>.out file:
									allcsh_out.append(line.split(" >& ")[1])
							if allcsh_out:
								progress = 0
								current_step = allcsh_out[0]
								total_steps = len(allcsh_out)
								for step in allcsh_out:
									if os.path.isfile('{}/{}'.format(DESIGN_DIR, step)) or os.path.isfile('{}/{}.gz'.format(DESIGN_DIR, step)):
										progress += 1
										current_step = step
							mid_dict[flow][design]['progress_data'] = {}
							mid_dict[flow][design]['progress_data']['total_steps'] = total_steps
							mid_dict[flow][design]['progress_data']['current_step'] = current_step
							mid_dict[flow][design]['progress_data']['progress'] = progress
						### prreport.cache Status info ###
						if os.path.isfile(DESIGN_DIR+'/prreport.cache'):

							## change it to native python -vasquez-
							## just trying this thing to be faster

							process = os.popen('grep ^Status {}/prreport.cache'.format(DESIGN_DIR))
							mid_dict[flow][design]['prreport_status'] = process.read().replace('\t',"").replace('Status',"").replace('\n',"")
							process.close()
						else:
							# this step seems create a lot of issues
							if os.path.isfile('{}/{}.all.done'.format(DESIGN_DIR, design)):
								
								print(DESIGN_DIR, 'this is a case with all.done and no prreport.cache')

								# process_prev = os.popen('cd %s; /u/prsuite/prs/etc/cachelog.pl -prefix %s'%(DESIGN_DIR, design))
								# process_prev.close()

								# process = os.popen('grep ^Status {}/prreport.cache'.format(DESIGN_DIR))
								# mid_dict[flow][design]['prreport_status'] = process.read().replace('\t',"").replace('Status',"").replace('\n',"")
								# process.close()
							else:
								pass
								# print(DESIGN_DIR, 'we have cache but not all.done??')

							mid_dict[flow][design]['prreport_status'] = '--'
						
						# im not using crash status
						# ### stacktrace info ###
						# mid_dict[flow][design]['crash_status'] = []
						# for file in os.listdir(DESIGN_DIR):
						# 	if 'stack_trace' in file or 'crte_' in file or '.stacktrace' in file:
						# 		mid_dict[flow][design]['crash_status'].append(file)
								
						# if not mid_dict[flow][design]['crash_status']:
						# 	del mid_dict[flow][design]['crash_status']
						# else:
						# 	print('\t\t'+str(mid_dict[flow][design]['crash_status']))
						### SUBMISION TIME hinfo timestamp:

						if os.path.isfile('{}/{}.hinfo.out'.format(DESIGN_DIR, design)):
							farm_entrance = time.strftime(T_FORMAT, time.localtime(os.path.getmtime('{}/{}.hinfo.out'.format(DESIGN_DIR, design))))
						else:
							farm_entrance = 'no'
						
						mid_dict[flow][design]['Farm entrance'] = str(farm_entrance).replace("\n","")
						### INGRESS TO FARM grd timestamp:
						if os.path.isfile('{}/{}.grd.out'.format(DESIGN_DIR, design)):
							qw_entrance = time.strftime(T_FORMAT, time.localtime(os.path.getmtime('{}/{}.grd.out'.format(DESIGN_DIR, design))))
						else:
							qw_entrance = 'no'
						mid_dict[flow][design]['QW entrance'] = str(qw_entrance).replace("\n","")
						### FINISHED JOB all.done timestamp:
						if os.path.isfile('{}/{}.all.done'.format(DESIGN_DIR, design)):
							mid_dict[flow][design]['all.done'] =  str(os.path.isfile('{}/{}.all.done'.format(DESIGN_DIR, design)))
							finish = time.strftime(T_FORMAT, time.localtime(os.path.getmtime('{}/{}.all.done'.format(DESIGN_DIR, design))))
						else:
							mid_dict[flow][design]['all.done'] = 'False'
							finish = 'no'
						mid_dict[flow][design]['Finish'] = str(finish).replace("\n","")
		
	return mid_dict
