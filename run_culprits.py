import pprint
import pickle

pp = pprint.PrettyPrinter(indent = 2)

TNSThres = 15.0
WNSThres = 5.0 
areaThres = 3.0 
powerThres = 5.0 
memThres = 10.0
rtmThres = 5.0 

suite_all_file = open('suite_all.pkl', 'rb')
suite_all = pickle.load(suite_all_file)
suite_all_file.close()

suite_means_file = open('suite_means.pkl', 'rb')
suite_means = pickle.load(suite_means_file)
suite_means_file.close();

k = 4;

metrics_selection = {'DCMvArea' : 0.3,
                     'DCWNS': 0.3,
                     'DCTNSPMT': 2,
                     'CLKDCAllOpt' : 0.4,
                     'DCStdCelTotPow' : 0.3,
                     'DCMem' : 0.5}

result = {}
for nightly in suite_means :

    result[nightly] = {}

    for report in suite_means[nightly]:
        result[nightly][report] = {}

        for metric in metrics_selection:
            
            # clean NaN values before sorting
            cleanList = []

            if metric in suite_means[nightly][report]:
                
                current_mean = float(suite_means[nightly][report][metric])
                
                # look if the metric is out of threshold
                if  abs(current_mean) > metrics_selection[metric]:

                    # then we sort this
                    for design in suite_all[nightly][report][metric]:
                            
                        current_design_value = suite_all[nightly][report][metric][design]

                        if current_design_value != '--':
                                
                            cleanList.append((design,float(current_design_value)))
                        
                        # sort designs from min to max
                        sor = sorted(cleanList, key=lambda x: x[1])
                        #print(nightly+' '+report+' '+metric)
                        #print(sor)
                        #if  k > (len(sor) - 1):
                        #    k = len(sor) - 1

                        best = sor[0:k] # the first k designs tuples (design,value)

                        lenSor=len(sor)
                        worst = sor[lenSor-k:lenSor] # last k designs tuples (design,value)

                        #turn best list to dict
                        bestDict = {}
                        for design in best:
                            bestDict[design[0]] = design[1]

                        # turn worst list to dict
                        worstDict = {}
                        for design in worst:
                            worstDict[design[0]] = design[1]

                        result[nightly][report][metric] = {}
                        result[nightly][report][metric]['mean'] = suite_means[nightly][report][metric]
                        result[nightly][report][metric]['best'] = bestDict
                        result[nightly][report][metric]['worst'] = worstDict

pp.pprint(result)



                        



