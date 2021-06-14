import os, re, pickle
from bs4 import BeautifulSoup
import pprint

from dask.distributed import Client,wait

#c5 = Client('pv128g005:8786')
c3 = Client('pv128g002:8786')

pp = pprint.PrettyPrinter(indent = 2, depth = 4)

# suite_collector.py - vasquez
# 
# Collects al metrics and designs values for a certain report across a certain quantity
# of nightly images, as output return the following two dicts:
# 
# - suite_dict_all   : all the design values
# - suite_dict_means : all mean values
# 
# also dumps pickle files of those dicts with the following names:
#
# report_name + '_all.pkl'
# report_name + '_means.pkl'
# 
# Usage example
# 
# branch   		= '/slowfs/dcopt036/nightly_prs/p2019.03_ls'
# suite    		= 'DC_ICC2'
# report_name	= 'srm_icc2_spg_opt_area'
# flow     		= 'SRM_ICC2_spg_opt_area'
# baseline 		=  'O_SRM_ICC2_spg_opt_area'
# all_base 		= True
# nightly_max 	= 5
# suite_collector(branch, suite, report_name, flow, baseline, all_base, nightly_max)


def suite_collector_nums(root_path, branch, suite, report_name, flow, baseline, nightly_max):

	print('\nsuite_collector_V2.py')

	#branch = branch_path.split('/')[-1]	
	

	print('\nStart collecting data for ' + branch + ' '  + suite + ' ' +flow + ' for last ' + str(nightly_max) + ' nightly-images...')
	# get nightly images list for the desired suite
	branch_path = os.path.join(root_path, branch)
	nightlys_path = os.path.join(root_path, branch, suite)
	nightly_images = open(os.path.join(nightlys_path,'images.txt')).read().split('\n')

	report = 'prs_report.' + report_name + '.out'

	# workaround to remove spaces or nulls 
	# sometimes appears multiple times
	while '' in nightly_images:
		nightly_images.remove('')

	# sort from newest to oldest
	nightly_images.reverse()


	suite_dict_all_values = {}

	# in this dicts we will store the data
	suite_dict_all = {}
	suite_dict_histograms = {}


	# counter to avoid ancient nightly images
	nightly_count = 0

	for nightly in nightly_images:

		target_report_path = os.path.join(branch_path, suite, nightly, report, baseline)
		
		# detect if the report is all base.
		if os.path.isdir(target_report_path) == False:
			target_report_path = os.path.join(branch_path, suite, nightly, report)
		
		print('\t' + nightly, end= ' ')
		print(report, end = ', ')

		if os.path.isdir(target_report_path):
			
			# so the report exist
			suite_dict_all_values[nightly] = {}
			suite_dict_all_values[nightly][flow] = {}
			
			suite_dict_histograms[nightly] = {}
			suite_dict_histograms[nightly][flow] = {}
			
			# List of available designs in report files
			design_list = []

			for fl in os.listdir(target_report_path):
				
				design_file_ptrn = '^design_(.+)\.html'
				
				m_design = re.match(design_file_ptrn, fl)
				
				if m_design and ('profiles' not in m_design.group(1)):
					design = m_design.group(1)
					design_list.append(design)
					des_all_page = os.path.join(target_report_path,fl)

					suite_dict_all_values[nightly][flow][design] = {}

					if not os.path.exists(des_all_page):
						print('No available %s'%des_all_page)
						continue
					
					soup_obj = BeautifulSoup(open(des_all_page), "html.parser")
					span_tags = soup_obj.find_all('span')


					for tag in span_tags:
						if tag.get('id') != None:
							
							flow_ptrn = '^%s_%s_(.+)'%(flow,design)
							base_ptrn = '^%s_%s_(.+)'%(baseline,design)
							val_ptrn  = '([0-9.\%\+-]+)'

							# metric_base = ''
							# metric_flow = ''
							# percentdiff = ''

							m_flow = re.match(flow_ptrn,tag.get('id').strip())
							m_base = re.match(base_ptrn,tag.get('id').strip())
							m_val  = re.match(val_ptrn, tag.getText().strip())
							
							#print(tag.getText())

							if m_flow and m_val:
								metric = m_flow.group(1)
								value  = m_val.group(1)

								if '_value' not in metric:
									if metric not in suite_dict_all_values[nightly][flow][design]:
										
										suite_dict_all_values[nightly][flow][design][metric] = {}
									
									value = value.replace('%', '').replace('e','E')
									value = float(value) if value != '--' else None
									suite_dict_all_values[nightly][flow][design][metric]['diff_percent'] = value
									
								else:
									metric = metric.replace('_value','')

									if metric not in suite_dict_all_values[nightly][flow][design]:
										suite_dict_all_values[nightly][flow][design][metric] = {}

									value = value.replace('%', '')
									value = float(value) if value != '--' else None
									suite_dict_all_values[nightly][flow][design][metric]['flow_val'] = value

							if m_base and m_val:
								metric = m_base.group(1).replace('_value','')
								value  = m_val.group(1)
	
								if metric not in suite_dict_all_values[nightly][flow][design]:
									suite_dict_all_values[nightly][flow][design][metric] = {}
								
								value = value.replace('%', '')
								value = float(value) if value != '--' else None
								suite_dict_all_values[nightly][flow][design][metric]['base_val'] = value

			
			# scrap the histograms!
			report_file = os.path.join(target_report_path, 'index.html')
			
			if os.path.isfile(report_file):
				soup_obj = BeautifulSoup(open(report_file), "html.parser")
				span_tags = soup_obj.find_all('span')

				for tag in span_tags:
					hist_ptrn = '(\w+)_Histgrm_(\w+)'
					#print(tag.get('id'))
					m_hist = re.match(hist_ptrn,str(tag.get('id')))

					if m_hist:
						
						hist_flow   = m_hist.group(1)
						hist_metric = m_hist.group(2)
						hist_value  = tag.text.strip()
						
						#print(hist_flow, hist_metric, hist_value)
						if hist_flow == flow and hist_metric != 'Gap':

							suite_dict_histograms[nightly][flow][hist_metric] = hist_value
				
			else:
				print('index.html file not present for ' + report + '/' + nightly )
			
						
		else:
			print('not present')
			nightly_count -= 1
		
		# just count to avoid ancient nightly images
		nightly_count += 1
		if nightly_count >= nightly_max:
			break;

	# save the colected data in pkl dicts
	# you can test the output with some nightly and metric
	
	# return suite_dict_all_values, suite_dict_histograms 


	# chaning to pkl approach
	# lets organize this on pkl_data folders so we can clean up this
	if not os.path.exists('pkl_data'):
		os.mkdir('pkl_data')

	all_nums_pkl_name   = branch + '_' + suite + '_' + report_name + '_' + baseline + '_all_nums.pkl'
	histograms_pkl_name = branch + '_' + suite + '_' + report_name + '_' + baseline + '_histograms.pkl'

	all_nums_pkl_name   = os.path.join('pkl_data', all_nums_pkl_name)
	histograms_pkl_name = os.path.join('pkl_data', histograms_pkl_name)
	
	file_all = open(all_nums_pkl_name , 'wb')
	file_hist = open(histograms_pkl_name ,'wb')

	pickle.dump(suite_dict_all_values, file_all)
	pickle.dump(suite_dict_histograms, file_hist)


	print('\n\tdump metrics design values data to ' + all_nums_pkl_name )
	print('\tdump histograms data to ' + histograms_pkl_name )


	file_all.close()
	file_hist.close()

	return all_nums_pkl_name, histograms_pkl_name 

# #end of function suite_collector 
# root_path 	= '/remote/dcopt077/nightly_prs'
# branch = 'q2019.12-SP'
# suite    		= 'DC_ICC2'
# report_name	    = 'diff.srm_icc2_spg_timing_opt_area'
# flow     		= 'SRM_ICC2_spg_timing_opt_area'
# baseline 		= 'SRM_ICC2_spg_timing_opt_area_prev'
# all_base 		= True
# nightly_max 	= 1

#                                                               # root_path, branch, suite, report_name, flow, baseline, nightly_max
# suite_dict_all_values, suite_dict_histograms = suite_collector_nums(root_path, branch, suite, report_name, flow, baseline, nightly_max)

# #pp.pprint(suite_dict_all_values)
# pp.pprint(suite_dict_histograms)
