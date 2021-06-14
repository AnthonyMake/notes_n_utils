#!/slowfs/dcopt105/vasquez/cnda/Conda/bin/python
import sys

# utilitary function location
# sys.path.append('/slowfs/dcopt105/vasquez/utils/nd_repo/le_clon/nd_report')

from logfile_utils import *

log = 'example_log.out.gz'

str_log = log_to_str(log)
reports = get_action_dep_rpts(str_log)

pp.pprint(reports[-10:])



