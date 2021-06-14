#!/slowfs/dcopt105/vasquez/cnda/Conda/bin/python

import argparse, os
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from argparse import RawTextHelpFormatter


# parser = argparse.ArgumentParser(description='''QoR Trend maker:
# Makes a qor_trend chart for selected metrics from a functional QoR table html file and outputs as a png image file.
# If the html provided has more than one table, then the duplicated metrics will be renamed.

# Example Usage:

# qor_trend_image.py -source /remote/dcopt077/nightly_prs/o2018.06-SP/DC_ICC2/QoR_tracking/summary.SRM_ICC2_spg_opt_area.html -nightly_max 13 -metrics 'DCMvArea DCWNS DCTNSPMT CLKDCAllOpt DCStdCelTotPow' -title 'O-2018.06-SP DCG RMS QoR Trend (SRM_ICC2_spg_opt_area)' -image_name osp -improvement

# -vasquez@synopsys.com-''', formatter_class=RawTextHelpFormatter)

# parser.add_argument('-source', type= str,
#                 	help='The html file of the QoR table. -without clearcase-')

# parser.add_argument('-metrics', type= str,
#                 	help='list of metrics you want to plot as \'metric1 metric2 metric3 metric4\', if dont know, use -show_available_metrics.')

# parser.add_argument('-title', type = str,
#                 	help='the title you want to put in the top of the chart as \'Some title for this graphic\'.')

# parser.add_argument('-image_name', type = str,
#                     help = 'the name for the png image file, not spaces allowed.')

# parser.add_argument('-nightly_max', type = int,
# 					help = 'backwards number of nightly images to include.')

# parser.add_argument('-avoid_last', action = 'store_true',
# 					help = 'useful when last nightly messed up the chart.')

# parser.add_argument('-show_available', action = 'store_true',
# 					help = 'show the available metrics in the QoR table and exits.')

# parser.add_argument('-dup_suffix', type= str,
# 					help = 'Specify the the suffix to append to duplicated metrics, \'_diff\' or baseline letter would be usefull, default is \'+\'.')

# parser.add_argument('-improvement', action = 'store_true',
# 					help = 'Show percentage of improvement by applying rmorale\'s formula: (1/(1+x/100)-1)*100.')

# args = parser.parse_args()

def make_trend( source, metrics, title, image_name, nightly_max, avoid_last, show_available, dup_suffix, improvement):

	print('\nQoR Trend Image Generator\n')
	# check if the qor table exists
	if source != None:
		
		clearcase_start = 'https://clearcase'
		if clearcase_start in source:
			source.replace(clearcase_start, '')

		if os.path.isfile(source):

			# The qor table page usually has two tables we want the second one
			qor_df = pd.read_html(source)[1]

			not_metrics = ['Image', '#Designs', 'Comments', 'GAP', 'OtherLinks']
			
			avail_columns = qor_df.loc[1]
			
			# check if sufffix for duplicated
			if dup_suffix == None:
				suffix = '+'
			else:
				suffix = dup_suffix
			
			# look for duplicate columns
			new_columns = []
			avail_metrics = []

			for column in avail_columns.tolist() :
				# make a list the new names of columns	
				if column not in new_columns:
					new_columns.append(column)
				else:
					new_columns.append(column + suffix)

				# another list with only metrics
				if column not in not_metrics:
					if column not in avail_metrics:
						avail_metrics.append(column)
					else:
						avail_metrics.append(column + suffix)
					
			qor_df.columns = new_columns

			if show_available:

				print('available metrics: ' + " ".join(avail_metrics))
				
			else:
				
				qor_df.rename(columns = avail_columns, inplace = True)

				if nightly_max != None :
					
					print('Reading the qor_table for a max of ' + str(nightly_max) + ' nightly images.', end = ' ')
					
					if (avoid_last):
						print('-avoiding last Nightly-')
					else:
						print('')

					# define scope
					# the number two is just for the overhead rows
					start = 2 + avoid_last
					end   = 2 + nightly_max + avoid_last if qor_df.shape[0] >= 2+ nightly_max else qor_df.shape[0] + 2

					
					qor_df = qor_df[start : end]
					
					# in case we have -- values
					qor_df.replace({'--': np.nan}, inplace=True)

					# get the status in separate columns
					qor_df['done']   = qor_df['#Designs'].str.extract(r'done:\s([0-9]+)').fillna(0)
					qor_df['pend']   = qor_df['#Designs'].str.extract(r'pend:\s([0-9]+)').fillna(0)
					qor_df['fail']   = qor_df['#Designs'].str.extract(r'fail:\s([0-9]+)').fillna(0)

					# put the status in one field
					qor_df['status'] = 'd: ' + qor_df['done'].astype(str) + '\n' + 'p: ' + qor_df['pend'].astype(str) + '\n' + 'f: ' + qor_df['fail'].astype(str)

					# some extractions to get dates
					qor_df['YY'] = qor_df['Image'].str.extract(r'D([0-9]{4})[0-9]{2}[0-9]{2}_.*')
					qor_df['MM'] = qor_df['Image'].str.extract(r'D[0-9]{4}([0-9]{2})[0-9]{2}_.*')
					qor_df['DD'] = qor_df['Image'].str.extract(r'D[0-9]{4}[0-9]{2}([0-9]{2})_.*')
					
					# this wil not work in dcrt
					# qor_df['HH'] = qor_df['Image'].str.extract(r'D[0-9]{4}[0-9]{2}[0-9]{2}_([0-9]{2})_[0-9]{2}.*')
					# qor_df['mm'] = qor_df['Image'].str.extract(r'D[0-9]{4}[0-9]{2}[0-9]{2}_[0-9]{2}_([0-9]{2}).*')
					
					qor_df['x_label'] = qor_df['MM'] + '/' + qor_df['DD'] + '\n' + qor_df['status']

					# delete the some useless columns, idk
					qor_df.drop(columns = ['OtherLinks', '#Designs'], inplace = True)
					
					# let's plot
					plt.switch_backend('agg') # do not require display
					plt.figure(figsize=(16,6))
					plt.style.use('ggplot')
					plt.gca().invert_xaxis()

					if metrics != None: 
						
						metrics = metrics.split(' ')

						# in case any of the metric were valid ones
						data_to_show = False
						
						for metric in metrics:

							if metric in qor_df.columns:
								
								if improvement:
									# the old famous rmorale's formula
									qor_df[metric] = qor_df[metric].astype(float).apply(lambda x: ((1/(1+x/100))-1)*100)
								else:
									qor_df[metric] = qor_df[metric].astype(float)
								
								plt.plot(qor_df['Image'], qor_df[metric], label = metric, marker = 'o')
								
								# at least one metric is valid
								data_to_show = True

							else:
								print('Warning: The metric ' + metric + ' is not present, try -show_available or configure your QoR table to show the desired metrics.')


						if data_to_show:
							
							if title != None:

								plt.title(title)
								plt.xticks(qor_df['Image'], qor_df['x_label'], ha="left")
							
								plt.xlabel("Nightly Image\n-month/day, d: done, p: pending, f: fail")
								if improvement:
									plt.ylabel("Improvement %")
								else:
									plt.ylabel("Variation From Baseline %")

								plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)
								plt.tight_layout()

								if image_name != None:
									
									try:
										plt.savefig(image_name)
									except:
										print('Error: it was not possible save the image, maybe permissions issue.')
									print('Image file saved as \'' + image_name + '.png\'')
								else:
									print('Error: -image_name is not defined.')

							else:
								print('Error: -title is not defined.')

						else:
							print('Error: Any of your metrics is present in the QoR table.')

					else:
						print('Error: please specify -metrics. Try -show_available to display the list of available metrics')

				else:
					print('Error: please specify -nightly_max.')
		else:
			print('Error: ' + source + ' is not a valid file.')

	else:
		print('Error: Please provide a valid -source argument, try --help.')



# make_trend(args.source, args.metrics, args.title, args.image_name, args.nightly_max, args.avoid_last, args.show_available, args.dup_suffix, args.improvement)
