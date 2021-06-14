
import os, sys, time, pickle, re, pprint
from datetime import date, timedelta, datetime

def last_week_trend(root_path, branch, suite, flows, metrics, target_day, force = None ):

	nightlys_path = os.path.join(root_path, branch, suite)
	nightly_images = open(os.path.join(nightlys_path,'images.txt')).read().split('\n')
	nightly_images.reverse()
	# calendar stuff
	weekdays = 'Monday Tuesday Wednesday Thursday Friday Saturday Sunday'.split()
	today = date.today()
	day_unit = timedelta(days =1)
	days_back = 7
	for_report = []
	
	if not force:
		for ng in nightly_images:
			ng_date = ng.split('_')
			
			if len(ng_date) != 3:
				continue
		
			ng_date = ng_date[0]
	
			build_date = datetime.strptime(ng_date,'D%Y%m%d')
	
			if build_date.weekday() == weekdays.index(target_day):
				for_report.append(ng)
			
			if len(for_report) == 2:
				break
	else:
		for_report = force

	print(for_report)

	rpt_dir = os.path.join(nightlys_path,'week_trend')
	last_ng_dir = os.path.join(rpt_dir,for_report[0])

	if not os.path.isdir(rpt_dir):
		os.mkdir(rpt_dir)
		if not os.path.isdir(last_ng_dir):
			os.mkdir(last_ng_dir)
	else:
		if not os.path.isdir(last_ng_dir):
			os.mkdir(last_ng_dir)

	count = 0
	for n in for_report:
		for flow in flows.split():
			flow_pointer = os.path.join(nightlys_path,n,'prs/run',flow)
			pointer_loc =  os.path.join(last_ng_dir,'%s_%s'%(n,flow))

			if os.path.exists(pointer_loc):
				os.remove(pointer_loc)

			os.symlink(flow_pointer,pointer_loc)
			count += 1

			# only first flow is pivot 
			if count >= len(flows.split()) + 1:
				break
				
	# report
	# columns = 'FlowLong DCMvArea DCWNS DCTNSPMT DCStdCelTotPow CLKDCAllOpt*(max(CValAllFlows("CPUDCFullOpt"))>3) DCMem Gap'
	columns = metrics
	# columns = 'FlowLong DCMvArea ICPMvArea DCWNS ICPWNS DCTNSPMT ICPTNSPMT DCStdCelTotPow ICPStdCelTotPow CLKDCAllOpt*(max(CValAllFlows("CPUDCFullOpt"))>3) DCMem Gap'

	# fullsuite
	# columns = 'FlowLong DCMvArea ICPMvArea DCICPMvAreaE Gap DCWNS DCTNSPM DCTNSPMT DCTNSPF ICPWNS ICPTNSPM ICPTNSPMT ICPTNSPF DCICPWNSE DCICPTNSE Gap DCCArea DCNCArea DCNMArea Gap PCNMArea PCCArea PCNCArea Gap ICPCArea ICPNCArea ICPNMArea DCICPNMAreaE Gap DCStdCelDynPow DCStdCelTotPow DCStdCelLeakPow DCNoClkStdCelDynPow Gap ICPStdCelDynPow ICPStdCelTotPow ICPStdCelLeakPow ICPNoClkStdCelDynPow DCGNBBLVth ICPGNBBLVth Gap DCVio ICPVio Gap DCBufInvCnt DCBufInvCntP DCSeqInst DCCombInst DCInst ICPInst Gap ICPBufInvCnt ICPBufInvCntP Gap CPUDCAllOpt CPUDCFullOpt CPUDCInsrtDFT CPUDCIncrOpt CPUDCOptnArea CPUDCIncrOptP Gap CLKDCAllOpt CLKDCFullOpt CLKDCInsrtDFT CLKDCIncrOpt CLKDCOptnArea Gap CLKDCAllOpt*(max(CValAllFlows("CLKDCAllOpt"))>3) CLKDCFullOpt*(max(CValAllFlows("CLKDCAllOpt"))>3) CLKDCInsrtDFT*(max(CValAllFlows("CLKDCAllOpt"))>3) CLKDCIncrOpt*(max(CValAllFlows("CLKDCAllOpt"))>3) CLKDCOptnArea*(max(CValAllFlows("CLKDCAllOpt"))>3) Gap CLKDCAllOpt*(max(CValAllFlows("CLKDCAllOpt"))>6) CLKDCFullOpt*(max(CValAllFlows("CLKDCAllOpt"))>6) CLKDCInsrtDFT*(max(CValAllFlows("CLKDCAllOpt"))>6) CLKDCIncrOpt*(max(CValAllFlows("CLKDCAllOpt"))>6) CLKDCOptnArea*(max(CValAllFlows("CLKDCAllOpt"))>6) Gap CPUDCCngRpt CLKDCCngRpt Gap ICPCPU*(max(CValAllFlows("CLKDCAllOpt"))>3) ICPCLK*(max(CValAllFlows("CLKDCAllOpt"))>3) DCICPCPU DCMem DCMCPkMem MemDCFullOpt MemDCIncrOpt ICPMem Gap PCNBBArea PCWNS PCTNSPM PCTNSPMT PCStdCelDynPow PCStdCelTotPow PCStdCelLeakPow PCNoClkStdCelDynPow Gap DPPMvArea DPPWNS DPPTNSPM DPPTNSPMT DPPStdCelDynPow DPPStdCelTotPow DPPStdCelLeakPow DPPNoClkStdCelDynPow Gap DCAGWirLn DCAGGRC*(max(CValAllFlows("DCAGPOvGC"))>0) DCAGPOvGC*(max(CValAllFlows("DCAGPOvGC"))>0) ICPAGGRC*(max(CValAllFlows("ICPAGPOvGC"))>0) ICPAGPOvGC*(max(CValAllFlows("ICPAGPOvGC"))>0) Gap CLKplace Gap CLKplace_0 CLKplace_1 CLKplace_2 CLKplace_3 Gap CLKDCICC2Ovr Gap DPRNBBArea DPRWNS DPRTNSPM DPRTNSPMT Gap RejRatioLodHeMain RejRatioLodHeIncr RejRatioGpow1Ona RejRatioGpow2Ona Gap Gap DCNBBArea DCLsMissing DCLsStrategy DCIsoMiss DCIsoRedund DCIsoNoPDCr DCIsoUnused DCIsoConst DCIsoPwS DCIsoNonUPF DCIsoPortDt DCAoDriver DCAoLoad DCNAoDriver DCPassGtCasc DCPGNtMsmtch DCOpCondErr Gap DCUPFNumLS DCUPFAreaLS DCUPFNumISO DCUPFAreaISO DCUPFNumRET DCUPFAreaRET DCUPFNumAO DCUPFAreaAO DCUPFNumSO DCUPFAreaSO DCUPFNumPM DCUPFAreaPM DCUPFNumNPMC DCUPFAreaNPMC Gap CheckSum Gap DCNMxTranPM DCNMxTranPMT ICPNMxTranPM ICPNMxTranPMT Gap DCCPUclk-gate DCNClkGate DCNClkGateAuto DCPClkGateAuto DCNGateReg DCPGateReg DCNumReg Gap DCNGateRegBit DCPGateRegBit DCNGateRegAutoBit DCPGateRegAutoBit DCNUngatedRegBit DCPUngatedRegBit Gap SGCells SGRegsN SGRegsP Gap'
	
	rows = 'Values MeanVal Mean Min Max 95%High 95%Low StdDev SDMean NSDMean Count Histgrm'
	rpt_cmd = '/u/prsuite/prs/bin/prreport.pl -showall -rows \"%s\" -allbase -html -htmlbrief -success \"^(Done|FM.*)\" -filterpg -stack -columns \'%s\''%(rows,columns)

	cding = 'cd %s;'%last_ng_dir

	print(cding+rpt_cmd)
	os.system(cding+rpt_cmd)

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

columns = 'FlowLong DCMvArea ICPMvArea DCWNS ICPWNS DCTNSPM ICPTNSPMT DCTNSPF ICPTNSPF DCStdCelDynPow DCStdCelLeakPow DCStdCelTotPow ICPStdCelDynPow ICPStdCelTotPow ICPStdCelLeakPow CLKDCAllOpt*(max(CValAllFlows("CPUDCFullOpt"))>3) DCMem Gap'

last_week_trend(
	'/remote/dcopt077/nightly_prs',
	'r2020.09-SP',
	'DC_ICC2', 
	'SRM_ICC2_spg_timing_opt_area SRM_ICC2_spg_timing_opt_area_link_placer_ATCnBAP Q_SRM_ICC2_spg_timing_opt_area', 
	columns,
	'Friday',
	# force = 'D20200908_20_30 D20200902_20_30'.split()
)


last_week_trend(
	'/slowfs/dcopt036/nightly_prs',
	's2021.06_ls',
	'DC_ICC2', 
	'SRM_ICC2_spg_timing_opt_area SRM_ICC2_spg_timing_opt_area_link_placer_ATCnBAP R_SRM_ICC2_spg_timing_opt_area', 
	columns,
	'Friday',
	# force = 'D20200921_12_01 D20200908_12_01'.split()
)





