import pandas as pd
import pickle

# suite_excel_dump.py - vasquez
# 
# Make and excel report from a selection of metrics from a pkl_all file, please be caution of not 
# source the means value dict, it wont work, the metrics should be valid ones.
# If used as function, returns the name of the excel file. 
#
# usage exmaple:
# all_pkl_name = 'srm_icc2_spg_opt_area_all.pkl'
# mean_pkl_name = 'srm_icc2_spg_opt_area_mean.pkl'
# 
# metrics_selection = ['DCWNS',
#                     'DCTNSPMT',
#                     'DCTNSPM',
#                     'CLKDCAllOpt',
#                     'DCStdCelTotPow',
#                     'DCMem']
#
# suite_excel_dump(pkl_name, metrics_selection)

def suite_excel_dump(all_pkl_name, mean_pkl_name, metrics_selection):

  print('\nsuite_excel_dump.py')
  
  print('\nMaking excel report from pkl file ' + all_pkl_name)

  suite_all_file = open(all_pkl_name, 'rb')
  suite_all = pickle.load(suite_all_file)
  suite_all_file.close()

  suite_mean_file = open(mean_pkl_name, 'rb')
  suite_mean = pickle.load(suite_mean_file)
  suite_mean_file.close()

  trend_df = pd.DataFrame()

  excel_name = all_pkl_name + '.xlsx'
  writer = pd.ExcelWriter(excel_name)

  for metric in metrics_selection:
    for nightly in suite_all:
      for report in suite_all[nightly]:
        metric_all_serie = pd.Series()

        if metric in suite_all[nightly][report]:
          
          for design in suite_all[nightly][report][metric]:
            metric_all_serie[design] = suite_all[nightly][report][metric][design]
          
          trend_df[nightly] = metric_all_serie
          trend_df.loc['Mean', nightly] = suite_mean[nightly][report][metric] if metric in suite_mean[nightly][report] else ''

        
        else:
          print('\t' + metric + ' is not present in ' + nightly + '/' + report)
    
    # just for show chronological order
    trend_df = trend_df.sort_index(axis=1 ,ascending=True)
    
    print('\t' + 'writing dataframe for ' + metric)
    #print(trend_df)
      
    trend_df.to_excel(writer, metric)

  print('\n\t' + excel_name + ' written')
 
  writer.save()

  return excel_name