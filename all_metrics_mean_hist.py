import pickle
from jinja2 import Template
import pprint
pp = pprint.PrettyPrinter(indent=2)

def all_metrics_mean_hist(root_path, branch, suite, report, flow, baseline,mean_values_pkl_name, metric_selection):

    all_means = load_from_pkl(mean_values_pkl_name)
    #pp.pprint(all_means)

    # get a definitive list of metrics
    all_metrics = []
    all_ngs = []

    threshold = 10

    for n in all_means:
        if n not in all_ngs:
            all_ngs.append(n)

        for mt in all_means[n][flow]:
            if mt not in all_metrics:
                all_metrics.append(mt)

            if mt in metric_selection:
                threshold = metric_selection[mt][0]
                threshold = threshold if threshold != 0 else 1
            else:
                threshold = 10

            value = all_means[n][flow][mt]
            #pp.pprint(all_means)
            # if value and value != '--' and value.isnumeric():
            corner_cases = '-- Mean'.split()
            if value and value not in corner_cases:
                value = float(value)
                opacity = abs(value)/threshold if abs(value) <= threshold else 1
                color = '255,50,50,%s'%str(opacity) if value > 0 else '65,208,65,%s'%str(opacity)
                all_means[n][flow][mt] = {}
                all_means[n][flow][mt]['value'] = value
                all_means[n][flow][mt]['color'] = color

            else:
                all_means[n][flow][mt] = {}
                all_means[n][flow][mt]['value'] = value
                all_means[n][flow][mt]['color'] = '255,255,0,0'



    all_ngs.sort()

    template_text = open('/remote/pv/repo/user/vasquez/v_repo/suite_collectors/mean_hist_base.html', 'r').read()
    # template_text = open('mean_hist_base.html', 'r').read()
    template = Template(template_text)

    title = '%s mean hist'%flow

    html = template.render(
        html_title = title,
        branch = branch,
        suite = suite,
        flow = flow,
        baseline = baseline,
        report = report,
        all_means = all_means,
        all_ngs = all_ngs,
        all_metrics = all_metrics,
        metric_selection = metric_selection,
    )

    html_name = '%s_%s_%s_mean_hist.html'%(branch,suite,baseline)
    report_file = open(html_name, 'w')
    report_file.write(html)
    report_file.close()

    print('\t beautiful html with history for all the metrics mean values is created %s'%html_name)

    return html_name

def load_from_pkl(file_name):
    
    file = open(file_name, 'rb')
    var  = pickle.load(file)
    file.close()

    return var

#all_metrics_mean_hist('a','b','c','rname','SRM_ICC2_spg_timing_opt_area','P_SRM_ICC2_spg_timing_opt_area', 'q2019.12-SP_DC_ICC2_diff.srm_icc2_spg_timing_opt_area_means.pkl')

