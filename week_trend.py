
import os, sys, time, pickle, re, pprint
from datetime import date, timedelta, datetime

sys.path.append('/slowfs/dcopt105/vasquez/utils/suite_collectors_dev/v_repo/suite_collectors')
from week_trend_func import last_week_trend

columns = 'FlowLong DCMvArea ICPMvArea DCWNS ICPWNS DCTNSPM ICPTNSPMT DCTNSPF ICPTNSPF DCStdCelDynPow DCStdCelLeakPow DCStdCelTotPow ICPStdCelDynPow ICPStdCelTotPow ICPStdCelLeakPow CLKDCAllOpt*(max(CValAllFlows("CPUDCFullOpt"))>3) DCMem Gap'

# last_week_trend(
# 	'/remote/dcopt077/nightly_prs',
# 	'q2019.12-SP',
# 	'DC_ICC2', 
# 	'SRM_ICC2_spg_timing_opt_area', 
# 	'FlowLong DCMvArea DCWNS DCTNSPMT DCStdCelTotPow CLKDCAllOpt*(max(CValAllFlows("CPUDCFullOpt"))>3) DCMem Gap',
# 	'Monday',
# 	# force = 'D20200908_16_16 D20200831_16_00'.split()
# )

# # last_week_trend(
# # 	'/slowfs/dcopt036/nightly_prs',
# # 	'r2020.09_ls',
# # 	'DC_ICC2', 
# # 	'SRM_ICC2_spg_timing_opt_area', 
# # 	'FlowLong DCMvArea DCWNS DCTNSPMT DCStdCelTotPow CLKDCAllOpt*(max(CValAllFlows("CPUDCFullOpt"))>3) DCMem Gap',
# # 	'Monday'
# # )


## last_week_trend(
## 	'/remote/dcopt077/nightly_prs',
## 	'r2020.09-SP',
## 	'DC_ICC2', 
## 	'SRM_ICC2_spg_timing_opt_area', 
## 	columns,
## 	'Monday',
## 	force = 'D20201102_20_30 D20201026_20_30'.split()
## )

last_week_trend(
	'/slowfs/dcopt036/nightly_prs',
	's2021.06_ls',
	'DC_ICC2', 
	'SRM_ICC2_spg_timing_opt_area', 
	columns,
	'Monday',
	force = 'D20201103_12_01 D20201026_12_01'.split()
)



