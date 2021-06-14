import os, re, pickle
from bs4 import BeautifulSoup
import pandas as pd
import matplotlib.pyplot as plt
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

def suite_fm_history_html(root_path, branch, suite, report_name, flow, nightly_max):

	print('\nsuite_fm_history_html.py - vasquez')
	# get nightly images list for the desired suite
	nightlys_path = os.path.join(root_path, branch, suite)
	nightly_images = open(os.path.join(nightlys_path,'images.txt')).read().split('\n')

	report = 'prs_report.' + report_name + '.html'

	print('\tgetting verification results for last ' + str(nightly_max) + ' nightly images from:')
	print('\t' + branch + '>' + suite + '>' + report + '\n')
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

	nightly_df = pd.DataFrame()

	for nightly in nightly_images:
		
		target_report_file = os.path.join(nightlys_path,nightly,report)
		
		if os.path.isfile(target_report_file):
			try:
				raw_tab = pd.read_html(target_report_file)
			except:
				print('No tables found in %s'%target_report_file)
				continue

			# before was a list of dataframes, now we just take the first one
			raw_tab = raw_tab[0]
			# we know the usual position of the flow names
			avail_columns = raw_tab.loc[0]			
			
			# asign the flow names as column names
			raw_tab.rename(columns = avail_columns, inplace= True)
			
			# get rid off annoying overhead info
			raw_tab = raw_tab[2:]
	
			raw_tab.set_index(raw_tab['Design Name'], inplace= True)
			
			nightly_serie = pd.Series(raw_tab[flow])

			nightly_df[nightly] = nightly_serie

			nightly_count += 1
			print('\t' + nightly + ' got it')

		else:
			print('\t' + nightly + ' ' + report + ' is not present' )
		
		if nightly_count >= nightly_max:
			break;

	# store design count before start to append
	# new rows to the dataFrame
	count_designs = len(nightly_df.index)		

	if nightly_df.empty != True:
		
		# get rid off the annoying 1 in the top of the frame
		nightly_df.rename_axis(None, inplace = True)

		# get the pass rate
		for nightly in nightly_df.columns:
			
			count_inconclusive = nightly_df[nightly].str.count('INCONCLUSIVE*').sum()
			count_failed = nightly_df[nightly].str.count('FAILED*').sum()
			count_succeeded = nightly_df[nightly].str.count('SUCCEEDED*').sum()
			count_other = 	count_designs - count_failed - count_inconclusive -	count_succeeded

			#sum_succeeded = nightly_df[nightly].str.count('SUCCEEDED*').sum()
			# print(nightly + ' ' +str(value))
			nightly_df.loc['SUCCEEDED',nightly] = count_succeeded
			nightly_df.loc['FAILED',nightly] = count_failed
			nightly_df.loc['INCONCLUSIVE',nightly] = count_inconclusive
			nightly_df.loc['Other',nightly] = count_other
		
			nightly_df.loc['Passing Rate',nightly] = count_succeeded / count_designs * 100
			nightly_df.loc['Passing Rate',nightly] = nightly_df.loc['Passing Rate',nightly].round(2)


		
		nightly_df = nightly_df.sort_index(axis=1, ascending = True)

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
		fm_pkl_name = branch + '_' + report_name + '_pandas.pkl'
		file_fm = open(fm_pkl_name , 'wb')
		pickle.dump(nightly_df, file_fm)
		file_fm.close()

		# dump an excel file

		fm_xls_name = branch + '_' + report_name + '.xlsx'
		writer = pd.ExcelWriter(fm_xls_name) 
		nightly_df.to_excel(writer, report_name)
		writer.save()
		print('\ndump dataframe ' + fm_pkl_name)
		print('exporting excel file ' + fm_xls_name )

		#make an html

		print('making a beautiful html...')
    

		html_title = branch + '_' + flow 
		html_table = ''
		html_table += '''
		<!DOCTYPE html>
		<html>
		<title>''' + html_title +'''</title>
		<meta name="viewport" content="width=device-width, initial-scale=1">
		<link rel="stylesheet" href="https://www.w3schools.com/w3css/4/w3.css">
		<body>
		'''

		html_table += '''
		<div class="w3-container w3-tiny">
		<h2>''' + 'Formality verification results history' + '''</h2>
		
		<div class="w3-container">
			</br>
			<b>Branch : </b>''' + branch +''' </br>
			<b>Suite : </b>''' + suite +''' </br>
			<b>Flow : </b>''' + flow +''' </br>
			<b>Report : </b>''' + report +''' </br>
		<div>

		<br>

		<a class="w3-button w3-deep-orange" href="''' + fm_xls_name + '''">Download .xlsx file</a>''' + '''

		<div class="w3-responsive">
		<table class="w3-table-all">'''

		# lets make the first row
		html_table += '''<tr class = "w3-deep-purple">
		<th>design \ nightly</th>'''
		for nightly in nightly_df.columns:
			html_table += '<th class= "w3-border-left w3-border-right">' + nightly + '</th>\n'
		html_table += '</tr>\n'

		#now the nightlies
		for design in nightly_df.index:
		
			# highlight the Passing Rate Row
			if design == 'Passing Rate' :  
				html_table += '<tr class = "w3-topbar w3-bottombar w3-border-deep-purple">\n'

			elif design == 'SUCCEEDED':
				html_table += '<tr class = "w3-topbar w3-border-deep-purple">\n'
			
			elif design == 'FAILED':
				html_table += '<tr class = "w3-border-deep-purple">\n'
			
			elif design == 'INCONCLUSIVE':
				html_table += '<tr class = "w3-border-deep-purple">\n'
			
			else:
				#html_table += '<tr class = "w3-topbar w3-bottombar w3-border-deep-purple">\n'
				html_table += '<tr>\n'

			html_table += '<td class= "w3-border-left w3-border-right" ><b>' + design + '</b></td>\n'
		
		
			# in case of numeric values in the dataframe
			# this var will helps to color the next value if
			# improves or degrades
			prev_result = 0

			for result in nightly_df.loc[design]:

				result = str(result)
				# lets set a color for known cases     
				if 'SUCCEEDED' in result:
					html_table += '<td class= "w3-border-left w3-border-right w3-pale-green">' + result + '</td>\n'
				
				elif 'FAILED' in result:
					html_table += '<td class= "w3-border-left w3-border-right w3-pale-red">' + result + '</td>\n'
				
				elif 'INCONCLUSIVE' in result:
					html_table += '<td class= "w3-border-left w3-border-right w3-light-grey">' + result + '</td>\n'
				
				elif 'FATAL' in result:
					html_table += '<td class= "w3-border-left w3-border-right w3-pale-yellow">' + result + '</td>\n'
				
				elif design == 'Passing Rate':
					
					result_num = float(result)

					if 	result_num > prev_result:
						# so its better
						html_table += '<td class= "w3-border-left w3-border-right w3-pale-green">' + result + '%</td>\n'
					
					elif result_num < prev_result:
						# so its worst
						html_table += '<td class= "w3-border-left w3-border-right w3-pale-red">' + result + '%</td>\n'						

					else:
						# so no change
						html_table += '<td class= "w3-border-left w3-border-right">' + result + '%</td>\n'

					# updates the previous value
					prev_result = result_num

				else:

					html_table += '<td class= "w3-border-left w3-border-right">' + result + '</td>\n'

			html_table += '</tr>\n'


		html_table += '''
		</table>
		</div>
		</div>'''

		html_table +='''
		</body>
		</html>
		'''
		
		html_name = html_title + '.html'
		print('see ' + html_name)

		html_file = open( html_name, 'w')
		html_file.write(html_table)
		html_file.close()

		return html_name

	else:
		print('There is no DF to work with.')

		return ''
