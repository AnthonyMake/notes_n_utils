import os, re, pickle, gzip
from bs4 import BeautifulSoup
from jinja2 import Template, Environment, FileSystemLoader
import pandas as pd
import pprint
import subprocess
pp = pprint.PrettyPrinter(indent=2)

## from pyecharts import Line

# suite_fm_history.py - vasquez
# 
# reads the formality reports for a certain branch and flow across 
# a desired number of nightly-images
# 
# # examples usage
# root_path = '/remote/dcopt077/nightly_prs'
# branch   	= 'o2018.06-SP'
# suite    	= 'DC_ICC2'
# report_name	= 'fml_srmfm_spg_ona'
# flow     	= 'SRMFm_ICC2_spg_opt_area'
# baseline 	= 'N_SRM_ICC2_spg_opt_area'
# nightly_max = 20
# 
# suite_fm_history_html(rooth_path, branch, suite, report_name, flow, nightly_max)
# when used as fucntion, returns the name of the html file.
# 
# excel file, pkl, and passing rate graphics capabilities could be enabled on demand.

# def suite_fm_history_from_cache(root_path, branch, suite, report_name, flow, nightly_max):
def suite_fm_history_from_cache(root_path, branch, suite, fm_report, fm_flow, nightly_max):
	nightly_max = 5
	print('\nsuite_fm_history_from_cache_html.py - vasquez')
	print('\tgetting verification results for last ' + str(nightly_max) + ' nightly images from:')
	print('\t' + branch + '>' + suite + '>' + fm_report + '\n')

	# get nightly images list for the desired suite

	suite_path = os.path.join(root_path, branch, suite)
	
	nightly_images = open(os.path.join(suite_path,'images.txt')).read().split('\n')
	# workaround to remove spaces or nulls 
	# sometimes appears multiple times
	while '' in nightly_images:
		nightly_images.remove('')
	nightly_images.reverse()

	nightly_count = 0

	fm_history_dict = {}

	for nightly in nightly_images:
		print('gathering fm status for', nightly)
		rpt_dir    = os.path.join(suite_path, nightly, 'prs/run','rpt_%s'%fm_report)
		cache_file = os.path.join(rpt_dir, 'prreport.cache')
		run_dir    = os.path.join(rpt_dir, fm_flow)

		if not os.path.exists(rpt_dir): 
			print('\t cant find rpt dir.')
			continue

		# get the cache
		if os.path.isfile(cache_file):
			cache_obj = open(cache_file, 'r') 
			cache_lines = cache_obj.read().splitlines()
			cache_obj.close()
			if nightly not in fm_history_dict:
				fm_history_dict[nightly]= {}
				fm_history_dict[nightly]['fm_results']= {}

		else:
			# cache_lines = None
			print('FM cache not found')
			continue

		# get the designs
		des_dirs = os.listdir(run_dir)
		count_data = {}
		count_data['SUCCEEDED'] = 0
		count_data['total'] = 0

		tool_fails = []

		for des in des_dirs:
			des_cfg_file = os.path.join(run_dir,des,'%s.des.cfg'%des)
			des_dir = os.path.join(run_dir,des)
			# check if real designs dir
			if not os.path.exists(des_cfg_file): continue
			
			count_data['total'] += 1
			# print(des)
			verification = None
			verif_line = None
			fatal_file = None
			fatal_line = None
			status = None
			log_file = None

			result = '--'

			if cache_lines:
				on_des = False
				for line in cache_lines:
					line = line.strip().split()

					if not on_des and len(line) == 2 \
						and 'Path' in line \
						and '%s/%s'%(fm_flow,des) in line:

						# print('ON DES!!')
						on_des = True

					if len(line) <= 4 and on_des:
						if 'Formal' in line : 
							verification = line[1]
							verif_line = line[2] 
						if 'FatalFile' in line: fatal_file = line[1] 
						if 'FatalLN' in line: fatal_line = int(line[1])
						if 'Status' in line: 
							status = line[1]
							# is the last one reported
							break

				if verification:
					if verification == '1':
						result = 'SUCCEEDED'
					else:
						# need to check for inconclusive
						logfile = os.path.join(run_dir,des,'%s.fmchk.out'%des)
						if os.path.isfile(logfile) or os.path.isfile('%s.gz'%logfile):
							cmd = 'zegrep ^Verification %s'%logfile
							# print(cmd)
							cmd_obj = subprocess.run(cmd, executable='/bin/csh',shell = True, stdout=subprocess.PIPE)
							cmd_ret = cmd_obj.stdout.decode("utf-8").splitlines()[0].split()

							result = cmd_ret[1]
						else:
							result = 'can\'t open logfile'


						
						# old slow approach
						# logfile = os.path.join(run_dir,des,'%s.fmchk.out.gz'%des)
						# if os.path.isfile(logfile):
						# 	log_lines = gzip.open(logfile).read().decode(encoding='utf-8', errors ='ignore').splitlines()
						# 	result = log_lines[int(verif_line) +1].split()[1]
						# else:
						# 	result = 'can\'t open logfile'
			
				else:
					result = status

				if result in count_data:
					count_data[result] += 1
				else:
					count_data[result] = 1

				fm_history_dict[nightly]['fm_results'][des] = result
				fm_history_dict[nightly]['count_data'] = count_data

				if fatal_file or fatal_line:

					fatal_file_loc = os.path.join(des_dir,fatal_file)

					if os.path.exists(fatal_file_loc + '.gz'):
						gz = True
						fatal_log = gzip.open(fatal_file_loc + '.gz').read().decode(encoding='utf-8', errors ='ignore').splitlines()
					else:
						fatal_log = open(fatal_file_loc).readlines()

					fatal_text = fatal_log[fatal_line-1].strip()
					# print(fatal_text)
					if ('Error' not in fatal_text) and ('Killed' not in fatal_text):
						# lookup for a near error
					
						for i in range(fatal_line-20, fatal_line+20):
							if ('Error' in fatal_log[i]) or ('The tool has just encountered a fatal error:' in fatal_log[i]) or ('Killed' in fatal_log[i]):
								if 'Error: 0' in fatal_log[i]:
									fatal_text += fatal_log[i]
								else:
									fatal_text = fatal_log[i]

					stack_trace = ''
					just_track_trace = ''

					for i in range(fatal_line,len(fatal_log)):
						log_line = fatal_log[i]
						if 'PV-INFO: Fatal URL =' in log_line:
							stack_trace = fatal_log[i].split()[5]
							# just for easy include in html
							just_track_trace = stack_trace
						else:
							just_track_trace = 'no PVFatals'

					print(des_dir + fatal_file + '.gz', fatal_line, fatal_text)
					# except:
					#    print((des_dir, fatal_file, fatal_line, fatal_text), 'couldn\'t get info')
			
					tool_fails.append({
						'fatal_file' : fatal_file + '.gz'*gz,
						'design'     : des,
						'logfile'    : des_dir + fatal_file + '.gz'*gz, 
						'line'       : fatal_line,
						'fatal_text' : fatal_text,
						'status'     : status, 
						'stack_trace': just_track_trace,
						})

				fm_history_dict[nightly]['tool_fails'] = tool_fails


		nightly_count += 1	
		if nightly_count >= nightly_max:
			break

		

	# pp.pprint(fm_history_dict)
	return fm_history_dict


def fm_summary_html(branch, suite, fm_flow, fm_history_dict,all_links_dict):
	template_file = '/slowfs/dcopt105/vasquez/utils/suite_collectors_dev/v_repo/suite_collectors/fm_summary_html.jinja'
	env = Environment(loader=FileSystemLoader('/'))
	template = env.get_template(template_file)

	title = 'FM Summary'
	html = template.render(
        html_title = title,
		branch = branch,
		suite = suite,
        flow = fm_flow,
        fm_history_dict = fm_history_dict,
		all_links_dict = all_links_dict
        )
	
	html_name = '%s_%s_%s.php'%(branch,suite,fm_flow)
	report_file = open(html_name, 'w')
	report_file.write(html)
	report_file.close()
	print(html_name, 'written')
	return html_name

						

						








			




		
		

		# get the design_list from files



		# if cache_lines:
		# 	# get designs lists
		# 	for line in cache_lines:
		# 		# line = line.strip().split()

		# 		des_pattrn = '^Path\s*%s\/(\w+)'
		# 		m_des = re.match(des_pattrn, line)
		# 		if m_des:
		# 			des = 


		# 		if not on_des and len(line) == 2 \
		# 			and 'Path' in line \
		# 			and '%s/'%(flow) in line[1]:


		# 			# print('ON DES!!')
		# 			on_des = True

		# 		if len(line) == 2 and on_des:
		# 			if 'Status' in line and len(line) == 2:
		# 				_status = line[1]
		# 				# updating this
		# 				health_dict[tool][brnch][suite][nightly][flow][design]['prreport_status'] = _status
		# 				# is the last reported
		# 				break

		# 			if 'FatalLN' in line and len(line) == 2:
		# 				fatal_line = int(line[1])

		# 			if 'FatalFile' in line and len(line) == 2:
		# 				fatal_file = line[1]


		# nightly_count += 1	
		# if nightly_count >= nightly_max:
		# 	break;



	# store design count before start to append
	# new rows to the dataFrame
	
		# make graphics 
		# plt.switch_backend('agg') # no require display 
		# plt.figure(figsize=(28,4))
		# plt.style.use('ggplot')
		# plt.title('som_title')
		# # plt.gca().invert_xaxis()
		# plt.plot(nightly_df.columns, nightly_df.loc['Passing Rate'], label = 'TotalPower',marker='o')
		# plt.xlabel("Nightly Image")
		# plt.ylabel("Passing Rate %")
		# plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)
		# plt.tight_layout()
		# plt.savefig('some_image.png')

		# Graph = Line('sum_title', 'sum_subtitle', title_pos= 'center',width=1000)
		
		# Graph.add('sum_name',
        #       nightly_df.columns,
        #       nightly_df.loc['Passing Rate'],
        #       legend_orient = 'vertical',
        #       legend_pos = 'right',
        #       line_width= 2,
        #       is_toolbox_show = False,
        #       #is_smooth= True
        #       #tooltip_trigger= 'axis'
        #       #is_datazoom_show= scroll,
        #       #datazoom_orient='horizontal'
		# 	  mark_point = ["max", "min"]
        #     )
		# Graph.render()

		# print(nightly_df.to_string())

		# dump pkl file	
		# fm_pkl_name = branch + '_' + report_name + '_pandas.pkl'
		# file_fm = open(fm_pkl_name , 'wb')
		# pickle.dump(nightly_df, file_fm)
		# file_fm.close()

		# # dump an excel file

		# fm_xls_name = branch + '_' + report_name + '.xlsx'
		# writer = pd.ExcelWriter(fm_xls_name) 
		# nightly_df.to_excel(writer, report_name)
		# writer.save()
		# print('\ndump dataframe ' + fm_pkl_name)
		# print('exporting excel file ' + fm_xls_name )

	# 	#make an html

	# 	print('making a beautiful html...')
    

	# 	html_title = branch + '_' + flow 
	# 	html_table = ''
	# 	html_table += '''
	# 	<!DOCTYPE html>
	# 	<html>
	# 	<title>''' + html_title +'''</title>
	# 	<meta name="viewport" content="width=device-width, initial-scale=1">
	# 	<link rel="stylesheet" href="https://www.w3schools.com/w3css/4/w3.css">
	# 	<body>
	# 	'''

	# 	html_table += '''
	# 	<div class="w3-container w3-tiny">
	# 	<h2>''' + 'Formality verification results history' + '''</h2>
		
	# 	<div class="w3-container">
	# 		</br>
	# 		<b>Branch : </b>''' + branch +''' </br>
	# 		<b>Suite : </b>''' + suite +''' </br>
	# 		<b>Flow : </b>''' + flow +''' </br>
	# 		<b>Report : </b>''' + report +''' </br>
	# 	<div>

	# 	<br>

	# 	<a class="w3-button w3-deep-orange" href="''' + fm_xls_name + '''">Download .xlsx file</a>''' + '''

	# 	<div class="w3-responsive">
	# 	<table class="w3-table-all">'''

	# 	# lets make the first row
	# 	html_table += '''<tr class = "w3-deep-purple">
	# 	<th>design \ nightly</th>'''
	# 	for nightly in nightly_df.columns:
	# 		html_table += '<th class= "w3-border-left w3-border-right">' + nightly + '</th>\n'
	# 	html_table += '</tr>\n'

	# 	#now the nightlies
	# 	for design in nightly_df.index:
		
	# 		# highlight the Passing Rate Row
	# 		if design == 'Passing Rate' :  
	# 			html_table += '<tr class = "w3-topbar w3-bottombar w3-border-deep-purple">\n'

	# 		elif design == 'SUCCEEDED':
	# 			html_table += '<tr class = "w3-topbar w3-border-deep-purple">\n'
			
	# 		elif design == 'FAILED':
	# 			html_table += '<tr class = "w3-border-deep-purple">\n'
			
	# 		elif design == 'INCONCLUSIVE':
	# 			html_table += '<tr class = "w3-border-deep-purple">\n'
			
	# 		else:
	# 			#html_table += '<tr class = "w3-topbar w3-bottombar w3-border-deep-purple">\n'
	# 			html_table += '<tr>\n'

	# 		html_table += '<td class= "w3-border-left w3-border-right" ><b>' + design + '</b></td>\n'
		
		
	# 		# in case of numeric values in the dataframe
	# 		# this var will helps to color the next value if
	# 		# improves or degrades
	# 		prev_result = 0

	# 		for result in nightly_df.loc[design]:

	# 			result = str(result)
	# 			# lets set a color for known cases     
	# 			if 'SUCCEEDED' in result:
	# 				html_table += '<td class= "w3-border-left w3-border-right w3-pale-green">' + result + '</td>\n'
				
	# 			elif 'FAILED' in result:
	# 				html_table += '<td class= "w3-border-left w3-border-right w3-pale-red">' + result + '</td>\n'
				
	# 			elif 'INCONCLUSIVE' in result:
	# 				html_table += '<td class= "w3-border-left w3-border-right w3-light-grey">' + result + '</td>\n'
				
	# 			elif 'FATAL' in result:
	# 				html_table += '<td class= "w3-border-left w3-border-right w3-pale-yellow">' + result + '</td>\n'
				
	# 			elif design == 'Passing Rate':
					
	# 				result_num = float(result)

	# 				if 	result_num > prev_result:
	# 					# so its better
	# 					html_table += '<td class= "w3-border-left w3-border-right w3-pale-green">' + result + '%</td>\n'
					
	# 				elif result_num < prev_result:
	# 					# so its worst
	# 					html_table += '<td class= "w3-border-left w3-border-right w3-pale-red">' + result + '%</td>\n'						

	# 				else:
	# 					# so no change
	# 					html_table += '<td class= "w3-border-left w3-border-right">' + result + '%</td>\n'

	# 				# updates the previous value
	# 				prev_result = result_num

	# 			else:

	# 				html_table += '<td class= "w3-border-left w3-border-right">' + result + '</td>\n'

	# 		html_table += '</tr>\n'


	# 	html_table += '''
	# 	</table>
	# 	</div>
	# 	</div>'''

	# 	html_table +='''
	# 	</body>
	# 	</html>
	# 	'''
		
	# 	html_name = html_title + '.html'
	# 	print('see ' + html_name)

	# 	html_file = open( html_name, 'w')
	# 	html_file.write(html_table)
	# 	html_file.close()

	# 	return html_name

	# else:
	# 	print('There is no DF to work with.')

	# 	return ''
