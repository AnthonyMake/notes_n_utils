import os, re, pickle
from bs4 import BeautifulSoup
import pprint
import gc

pp = pprint.PrettyPrinter(indent = 2, depth = 4)

# suite_collector.py - vasquez
# 
# Collects al metrics and designs values for a certain report across a certain quantity
# of nightly images, as output return the following two dicts:
# 
# - suite_dict_all   : all the design values
# - suite_dict_means : all mean values
# 
# also dumps pickle files of those dicts with the folloing names:
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


def suite_collector( root_path, branch, suite, report_name, flow, baseline, nightly_max, target_metrics = None, only_mean = False, pickle_mode = True):

	print('\nsuite_collector.py')
		
	print('\nStart collecting data for ' + branch + ' '  + suite + ' ' +flow + ' for last ' + str(nightly_max) + ' nightly-images...')
	# get nightly images list for the desired suite
	nightlys_path = os.path.join(root_path, branch, suite)
	nightly_images = open(os.path.join(nightlys_path,'images.txt')).read().split('\n')

	report = 'prs_report.' + report_name + '.out'

	# workaround to remove spaces or nulls 
	# sometimes appears multiple times
	while '' in nightly_images:
		nightly_images.remove('')

	# sort from newest to oldest
	nightly_images.reverse()

	# in this dicts we will store the data
	suite_dict_all = {}
	suite_dict_means = {}

	# counter to avoid ancient nightly images
	nightly_count = 0

	for nightly in nightly_images:

		target_report_path = os.path.join(root_path, branch, suite, nightly, report, baseline)
		
		# detect if the report is all base.
		if os.path.isdir(target_report_path) == False:
			target_report_path = os.path.join(root_path, branch, suite, nightly, report)
		
		print('\t' + nightly, end= ' ')
		print(report, end = ', ')

		if os.path.isdir(target_report_path):
			# so the report exist
			suite_dict_all[nightly] = {}
			suite_dict_all[nightly][flow] = {}
			
			suite_dict_means[nightly] = {}
			suite_dict_means[nightly][flow] = {}
			
			# List of available designs in report files
			design_list = []

			report_files = []
			try:
				report_files = os.listdir(target_report_path)
			except:
				print('\tCannot access %s'%target_report_path)
				continue

			for fl in os.listdir(target_report_path):				
				design_file_ptrn = '^design_(.+)\.html'
				
				m_design = re.match(design_file_ptrn, fl)
				
				if m_design and m_design.group(1) != 'profiles_' + baseline:
					design = m_design.group(1)
					design_list.append(design)
					
			# get the histograms for the desired
			# suite/nightly/report/baseline
			
			histgrms_ptrn = '^Histgrm_*'
			histgrms = [f for f in os.listdir(target_report_path) if re.match(histgrms_ptrn, f)]

				# this a really bad (but effective) approach made based on 
				# the way the humans navigate the PRS reports 
			if not only_mean:
				for hist in histgrms:
					
					# histograms comes in two flavors:
					# -hist_metric_formula_flow.html 
					# -hist_metric_flow.html
					# this workaround is supposed to be useless
					# when we use the -write_data feature of
					# prreport.pl 
					
					ptrn_no_formula = 'Histgrm_([A-Za-z0-9_]+)_('+ flow +')\.html'
					
					ptrn_formula = 'Histgrm_([A-Za-z0-9]+)__[A-Za-z0-9_]+__('+ flow +')\.html'
					
					m_no_form = re.match(ptrn_no_formula, hist)
					m_form = re.match(ptrn_formula, hist)
					
					metric_flow = ''
					if m_form:
						metric = m_form.group(1)
						metric_flow = m_form.group(2)
						
					elif m_no_form:
						metric = m_no_form.group(1)
						metric_flow = m_no_form.group(2)
						
					if metric_flow == flow and metric != 'Gap' and metric != 'FlowLong':
						
						if target_metrics and metric not in target_metrics:
							continue
						# print('\n\t\t' + metric + ' ' + metric_flow)
						suite_dict_all[nightly][flow][metric] = {}
						
						# just initializes the entire design list
						for des in design_list:
							suite_dict_all[nightly][flow][metric][des] = '--'

						# scrap the design values from histogram html file
						histgrm_file = os.path.join(target_report_path,hist)
						
						is_valid = False;

						if os.path.isfile(histgrm_file):
							is_valid = True
							soup_obj= BeautifulSoup(open(histgrm_file), "html.parser")
							a_tags = soup_obj.find_all('a')
							design_ptrn = r'.*title="(.+)">\s+(.+)%'
							
							for a in a_tags:
								m_des = re.match(design_ptrn, str(a))
														
								if m_des:
									design_name  = m_des.group(1)
									design_value = m_des.group(2)

									#print('\t\t\t\t' + design_name + ' ' + design_value )
									suite_dict_all[nightly][flow][metric][design_name] = design_value

						else:
								print('the file ' + histgrm_file + ' could not be open')
				

			# Get the all the metric mean values from summary report
			# current flow from baseline
			
			report_file = os.path.join(target_report_path, 'index.html')
			
			if os.path.isfile(report_file):
				soup_obj = BeautifulSoup(open(report_file), "html.parser")
				span_tags = soup_obj.find_all('span')
			
				for tag in span_tags:
					# the formula thing again ...
					mean_ptrn_form = flow + '_Mean_([A-Za-z0-9]+)__.+'
					mean_ptrn_no_form = flow + '_Mean_([A-Za-z0-9_]+)'
				
					# when metric comes with formula
					m_mean_form = re.match(mean_ptrn_form, str(tag.get('id')))
				
					# when metric comes with no formula
					m_mean_no_form = re.match(mean_ptrn_no_form, str(tag.get('id')))
				
					if m_mean_form:
						
						mean_metric = m_mean_form.group(1)
						mean_metric_value = tag.contents[0]
						
						if target_metrics and mean_metric not in target_metrics:
							continue
						# normalize the value to parse as float
						mean_metric_value = mean_metric_value.replace(' ', '')
						mean_metric_value = mean_metric_value.replace('%', '')
						
						suite_dict_means[nightly][flow][mean_metric] = mean_metric_value
						
					elif m_mean_no_form: 
						
						mean_metric = m_mean_no_form.group(1)
						mean_metric_value = tag.contents[0]
						
						if mean_metric != 'Gap' and mean_metric != 'FlowLong':
							
							if target_metrics and mean_metric not in target_metrics:
								continue
							# normalize the value to parse as float
							mean_metric_value = mean_metric_value.replace(' ', '')
							mean_metric_value = mean_metric_value.replace('%', '')
							
							suite_dict_means[nightly][flow][mean_metric] = mean_metric_value
				
			else:
				print('index.html file not present for ' + report + '/' + nightly )
			
			print(str(len(design_list)) + ' designs, ' + str(len(suite_dict_means[nightly][flow])) + ' metrics')
			
		else:
			print('not present')
			nightly_count -= 1
		
		# just count to avoid ancient nightly images
		nightly_count += 1
		if nightly_count >= nightly_max:
			break;

	# save the colected data in pkl dicts
	# you can test the output with some nightly and metric
	# pp.pprint(suite_dict_all)
	# pp.pprint(suite_dict_means)

	# changing to pkl 
	# lets organize this on pkl_data folders so we can clean up this
	if not pickle_mode:
		return suite_dict_all, suite_dict_means

	if not os.path.exists('pkl_data'):
		os.mkdir('pkl_data')
		
	all_pkl_name   = branch + '_' + suite + '_' + report_name + '_' + baseline + '_all.pkl'
	means_pkl_name = branch + '_' + suite + '_' + report_name + '_' + baseline + '_means.pkl'

	all_pkl_name   = os.path.join('pkl_data', all_pkl_name)
	means_pkl_name = os.path.join('pkl_data', means_pkl_name)

	file_all   = open(all_pkl_name, 'wb')
	file_means = open(means_pkl_name,'wb')

	pickle.dump(suite_dict_all, file_all)
	pickle.dump(suite_dict_means, file_means)

	print('\n\tdump metrics design values data to ' + all_pkl_name )
	print('\tdump mean values data to ' + means_pkl_name )

	file_all.close()
	file_means.close()

	print('Done!')

	del suite_dict_all
	del suite_dict_means
	gc.collect()
	
	return [all_pkl_name, means_pkl_name]
# end of functiion suite_collector 
