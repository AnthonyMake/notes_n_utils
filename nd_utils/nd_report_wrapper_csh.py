#!/slowfs/dcopt105/vasquez/cnda/Conda/bin/python
import os, argparse

desc = '''
Put the wrappers to integrate nd_report to the actual prs structure. (-vasquez-)
'''
parser = argparse.ArgumentParser(description=desc)

parser.add_argument('-rundir', type=str,
                    help='directory where the flows are located. Example: \'/remote/dcopt077/nightly_prs/p2019.03-SP/DC_ICC2/D20190613_20_30/prs/run\'')

parser.add_argument('-flow',  type =str, help = 'Name of the flow you want to compare against baseline flow.')
parser.add_argument('-baseline', type =str, help = 'Name of the flow you want to use as reference for comparison.')
parser.add_argument('-designs', type =str, help = 'List of designs to analyze. This could be a long list.')
# parser.add_argument('-result_dir', type =str,nargs = '+', help = 'List of designs to analyze. This could be a long list, please consider use a .csh wrapper.')

args = parser.parse_args()

rundir   = args.rundir
flow     = args.flow
baseline = args.baseline
designs  = args.designs

repo = '/remote/pv/repo/user/vasquez/nd_report'

wrapper_csh = '''
#!/bin/csh
# wrapper to integrate nd_reports in to the actual prs_reports structure
# -vasquez-

set rundir     = "%s"
set flow       = "%s"
set baseline   = "%s"
set result_dir = "$cwd"
set script_dir = "%s"

set designs  = "%s"

# some burocracy
cd $result_dir
mkdir prs_report.nd_report_$flow.out
cd $result_dir/prs_report.nd_report_$flow.out

$script_dir/nd_report_argparse.py -rundir $rundir -flow $flow -baseline $baseline -designs $designs
'''%(rundir,flow,baseline,repo,designs)

wrapper_name = 'subreport_nd_report_%s.csh'

nd_report = open(wrapper_name, "w")
nd_report.write(wrapper_csh)
nd_report.close()

## print('report written to %s  , Thank You!'%report_name)

## wrapper_csh