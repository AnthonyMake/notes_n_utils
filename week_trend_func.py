
import os, sys, time, pickle, re, pprint, json
from datetime import date, timedelta, datetime

crawler_script = '/remote/pv/repo/pvutil/dcprs/prs_html_crawler/prs_html_crawler.py'
colums_xml = '/slowfs/dcopt105/vasquez/utils/dc_qors/columns.xml'

def last_week_trend(root_path, branch, suite, flow, metrics, target_day, force = None, output_dir = 'default', suff = '' ):

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
  
	if output_dir == 'default':
		rpt_dir = os.path.join(nightlys_path,'week_trend')
		last_ng_dir = os.path.join(rpt_dir,for_report[0])

		if not os.path.isdir(rpt_dir):
			os.mkdir(rpt_dir)
			if not os.path.isdir(last_ng_dir):
				os.mkdir(last_ng_dir)
		else:
			if not os.path.isdir(last_ng_dir):
				os.mkdir(last_ng_dir)
	else:
		rpt_dir = output_dir
		last_ng_dir = os.path.join(rpt_dir,for_report[0])
		
		if not suff:
			pass
		else: 
			last_ng_dir = last_ng_dir + '_' + suff

		if not os.path.isdir(rpt_dir):
			print('%s directory not exists, cueck!'%output_dir)
			exit()
		else:
			if not os.path.isdir(last_ng_dir):
				os.mkdir(last_ng_dir)

	for n in for_report:
		flow_pointer = os.path.join(nightlys_path,n,'prs/run',flow)
		if suff:
			n = n + '_' + suff 
		
		pointer_loc =  os.path.join(last_ng_dir,n)
		

		if os.path.exists(pointer_loc):
			os.remove(pointer_loc)

		# print(pointer_loc, flow_pointer)
		os.symlink(flow_pointer,pointer_loc)

	# report
	# columns = 'FlowLong DCMvArea DCWNS DCTNSPMT DCStdCelTotPow CLKDCAllOpt*(max(CValAllFlows("CPUDCFullOpt"))>3) DCMem Gap'
	columns = metrics
	# columns = 'FlowLong DCMvArea ICPMvArea DCWNS ICPWNS DCTNSPMT ICPTNSPMT DCStdCelTotPow ICPStdCelTotPow CLKDCAllOpt*(max(CValAllFlows("CPUDCFullOpt"))>3) DCMem Gap'

	# fullsuite
	# columns = 'FlowLong DCMvArea ICPMvArea DCICPMvAreaE Gap DCWNS DCTNSPM DCTNSPMT DCTNSPF ICPWNS ICPTNSPM ICPTNSPMT ICPTNSPF DCICPWNSE DCICPTNSE Gap DCCArea DCNCArea DCNMArea Gap PCNMArea PCCArea PCNCArea Gap ICPCArea ICPNCArea ICPNMArea DCICPNMAreaE Gap DCStdCelDynPow DCStdCelTotPow DCStdCelLeakPow DCNoClkStdCelDynPow Gap ICPStdCelDynPow ICPStdCelTotPow ICPStdCelLeakPow ICPNoClkStdCelDynPow DCGNBBLVth ICPGNBBLVth Gap DCVio ICPVio Gap DCBufInvCnt DCBufInvCntP DCSeqInst DCCombInst DCInst ICPInst Gap ICPBufInvCnt ICPBufInvCntP Gap CPUDCAllOpt CPUDCFullOpt CPUDCInsrtDFT CPUDCIncrOpt CPUDCOptnArea CPUDCIncrOptP Gap CLKDCAllOpt CLKDCFullOpt CLKDCInsrtDFT CLKDCIncrOpt CLKDCOptnArea Gap CLKDCAllOpt*(max(CValAllFlows("CLKDCAllOpt"))>3) CLKDCFullOpt*(max(CValAllFlows("CLKDCAllOpt"))>3) CLKDCInsrtDFT*(max(CValAllFlows("CLKDCAllOpt"))>3) CLKDCIncrOpt*(max(CValAllFlows("CLKDCAllOpt"))>3) CLKDCOptnArea*(max(CValAllFlows("CLKDCAllOpt"))>3) Gap CLKDCAllOpt*(max(CValAllFlows("CLKDCAllOpt"))>6) CLKDCFullOpt*(max(CValAllFlows("CLKDCAllOpt"))>6) CLKDCInsrtDFT*(max(CValAllFlows("CLKDCAllOpt"))>6) CLKDCIncrOpt*(max(CValAllFlows("CLKDCAllOpt"))>6) CLKDCOptnArea*(max(CValAllFlows("CLKDCAllOpt"))>6) Gap CPUDCCngRpt CLKDCCngRpt Gap ICPCPU*(max(CValAllFlows("CLKDCAllOpt"))>3) ICPCLK*(max(CValAllFlows("CLKDCAllOpt"))>3) DCICPCPU DCMem DCMCPkMem MemDCFullOpt MemDCIncrOpt ICPMem Gap PCNBBArea PCWNS PCTNSPM PCTNSPMT PCStdCelDynPow PCStdCelTotPow PCStdCelLeakPow PCNoClkStdCelDynPow Gap DPPMvArea DPPWNS DPPTNSPM DPPTNSPMT DPPStdCelDynPow DPPStdCelTotPow DPPStdCelLeakPow DPPNoClkStdCelDynPow Gap DCAGWirLn DCAGGRC*(max(CValAllFlows("DCAGPOvGC"))>0) DCAGPOvGC*(max(CValAllFlows("DCAGPOvGC"))>0) ICPAGGRC*(max(CValAllFlows("ICPAGPOvGC"))>0) ICPAGPOvGC*(max(CValAllFlows("ICPAGPOvGC"))>0) Gap CLKplace Gap CLKplace_0 CLKplace_1 CLKplace_2 CLKplace_3 Gap CLKDCICC2Ovr Gap DPRNBBArea DPRWNS DPRTNSPM DPRTNSPMT Gap RejRatioLodHeMain RejRatioLodHeIncr RejRatioGpow1Ona RejRatioGpow2Ona Gap Gap DCNBBArea DCLsMissing DCLsStrategy DCIsoMiss DCIsoRedund DCIsoNoPDCr DCIsoUnused DCIsoConst DCIsoPwS DCIsoNonUPF DCIsoPortDt DCAoDriver DCAoLoad DCNAoDriver DCPassGtCasc DCPGNtMsmtch DCOpCondErr Gap DCUPFNumLS DCUPFAreaLS DCUPFNumISO DCUPFAreaISO DCUPFNumRET DCUPFAreaRET DCUPFNumAO DCUPFAreaAO DCUPFNumSO DCUPFAreaSO DCUPFNumPM DCUPFAreaPM DCUPFNumNPMC DCUPFAreaNPMC Gap CheckSum Gap DCNMxTranPM DCNMxTranPMT ICPNMxTranPM ICPNMxTranPMT Gap DCCPUclk-gate DCNClkGate DCNClkGateAuto DCPClkGateAuto DCNGateReg DCPGateReg DCNumReg Gap DCNGateRegBit DCPGateRegBit DCNGateRegAutoBit DCPGateRegAutoBit DCNUngatedRegBit DCPUngatedRegBit Gap SGCells SGRegsN SGRegsP Gap'
	
	rows = 'Values MeanVal Mean Min Max 95%High 95%Low StdDev SDMean NSDMean Count Histgrm'
	rpt_cmd = '/u/prsuite/prs/bin/prreport.pl -max_cores 8 -showall -rows \"%s\" -base %s -html -htmlbrief -success \"^(Done|FM.*)\" -filterpg -stack -columns \'%s\''%(rows,for_report[-1],columns)

	cding = 'cd %s;'%last_ng_dir

	print(cding+rpt_cmd)
	
	# data for crawler
	test_date = datetime.strptime(for_report[0].split('_')[0],'D%Y%m%d')
	base_date = datetime.strptime(for_report[1].split('_')[0],'D%Y%m%d')
	
	test_name = "%s_%s%s"%(suff, test_date.month, test_date.day)
	base_name = "%s_%s%s"%(suff, base_date.month, base_date.day)
	
	test_flow = "%s_%s"%(for_report[0],suff)
	base_flow = "%s_%s"%(for_report[1],suff)
	
	crawl_col = {
		"name" : [test_name, "vs" , base_name],
		"test" : test_flow,
		"base" : base_flow,
		"html" : "%s/html/index.html"%test_flow
	}

	os.system(cding+rpt_cmd)

	return crawl_col


def last_week_trend_multi(root_path, branch, suite, flow, metrics, target_day, force = None, output_dir = 'default', suff = '', add_multi = [] ):

	nightlys_path = os.path.join(root_path, branch, suite)
	nightly_images = open(os.path.join(nightlys_path,'images.txt')).read().split('\n')
	nightly_images.reverse()
	
	# calendar stuff
	weekdays   = 'Monday Tuesday Wednesday Thursday Friday Saturday Sunday'.split()
	today      = date.today()
	day_unit   = timedelta(days =1)
	trials = 2	
	days_back  = 14 + 7 
	for_report = []
	
	this_week_num = today.isocalendar()[1]
	prev_week_num = (today - 7*day_unit).isocalendar()[1]

	# print(this_week_num, prev_week_num)
	this_week_nightly = None
	prev_week_nightly = None


	# gather list of builds from this and prev week
	
	if not force:
		for trial in range(0,trials):
			this_week_ng_dates = []
			prev_week_ng_dates = []
			
			if trial > 0:
				# found nothing on this week so movint to the previous one.
				print('found nothing on this week so moving to the previous one.')
				this_week_num -= 1
				prev_week_num -= 1

			count = 0
			for ng in nightly_images:

				ng_date = ng.split('_')		
				if len(ng_date) != 3:
					continue

				ng_date = ng_date[0]
				build_date = datetime.strptime(ng_date,'D%Y%m%d')
				build_week = build_date.isocalendar()[1]

				# check if flow exists
				count += 1
				if not os.path.exists(os.path.join(nightlys_path,ng,'prs/run',flow)): 
					# print('not here:', os.path.join(nightlys_path,ng,'prs/run',flow))
					
					if count >= days_back:
						break
					continue

				# get nightlys from this week
				if build_week == this_week_num:
					this_week_ng_dates.append(
						(build_date,ng)
					)
				
				if build_week == prev_week_num:
					prev_week_ng_dates.append(
						(build_date,ng)
					)
				
				
				if count >= days_back:
					break
			
			if this_week_ng_dates and prev_week_ng_dates:
				break

			# print(this_week_ng_dates,prev_week_ng_dates)

			#if not this_week_ng_dates or not prev_week_ng_dates:
				#print('Can\'t find %s in any nightly run'%flow)
				
		# print(this_week_ng_dates,prev_week_ng_dates)
		
		# get the closer to target days for each week
		tup_diff_this_week = []
		tup_diff_prev_week = []

		# for this week
		for ng in this_week_ng_dates:
			# ng is written (datetime_obj, nightly name)
			day_diff = abs(ng[0].weekday() - weekdays.index(target_day))
			tup_diff_this_week.append(
				(day_diff, ng[1])
			)

		this_week_nightly = sorted(tup_diff_this_week, key=lambda tup:tup[0])[0][1]
		# for previous week
		#print(this_week_nightly)
		# for this week
		for ng in prev_week_ng_dates:
			# ng is written (datetime_obj, nightly name)
			day_diff = abs(ng[0].weekday() - weekdays.index(target_day))
			tup_diff_prev_week.append(
				(day_diff, ng[1])
			)

		prev_week_nightly = sorted(tup_diff_prev_week, key=lambda tup:tup[0])[0][1]

		print('will report this two: %s vs %s'%(this_week_nightly ,prev_week_nightly))
		
		for_report = [this_week_nightly, prev_week_nightly]
		
		# print(for_report)
		# exit()
			# if build_date.weekday() == weekdays.index(target_day):
			# 	for_report.append(ng)
			
			# if len(for_report) == 2:
			# 	break
	else:
		for_report = force

	if add_multi:
		for dr in add_multi:
			for_report.append(dr)

	print(for_report)
  
	if output_dir == 'default':
		rpt_dir = os.path.join(nightlys_path,'week_trend')
		last_ng_dir = os.path.join(rpt_dir,for_report[0])

		if not os.path.isdir(rpt_dir):
			os.mkdir(rpt_dir)
			if not os.path.isdir(last_ng_dir):
				os.mkdir(last_ng_dir)
		else:
			if not os.path.isdir(last_ng_dir):
				os.mkdir(last_ng_dir)
	else:
		rpt_dir = output_dir
		last_ng_dir = os.path.join(rpt_dir,for_report[0])
		
		if not suff:
			pass
		else: 
			last_ng_dir = last_ng_dir + '_' + suff

		if not os.path.isdir(rpt_dir):
			print('%s directory not exists, cueck!'%output_dir)
			exit()
		else:
			if not os.path.isdir(last_ng_dir):
				os.mkdir(last_ng_dir)

	for n in for_report:
		flow_pointer = os.path.join(nightlys_path,n,'prs/run',flow)
		if suff:
			n = n + '_' + suff 
		
		pointer_loc =  os.path.join(last_ng_dir,n)
		

		if os.path.exists(pointer_loc):
			os.remove(pointer_loc)

		# print(pointer_loc, flow_pointer)
		try:
			os.symlink(flow_pointer,pointer_loc)
		except:
			pass

	# report
	# columns = 'FlowLong DCMvArea DCWNS DCTNSPMT DCStdCelTotPow CLKDCAllOpt*(max(CValAllFlows("CPUDCFullOpt"))>3) DCMem Gap'
	columns = metrics
	# columns = 'FlowLong DCMvArea ICPMvArea DCWNS ICPWNS DCTNSPMT ICPTNSPMT DCStdCelTotPow ICPStdCelTotPow CLKDCAllOpt*(max(CValAllFlows("CPUDCFullOpt"))>3) DCMem Gap'

	# fullsuite
	# columns = 'FlowLong DCMvArea ICPMvArea DCICPMvAreaE Gap DCWNS DCTNSPM DCTNSPMT DCTNSPF ICPWNS ICPTNSPM ICPTNSPMT ICPTNSPF DCICPWNSE DCICPTNSE Gap DCCArea DCNCArea DCNMArea Gap PCNMArea PCCArea PCNCArea Gap ICPCArea ICPNCArea ICPNMArea DCICPNMAreaE Gap DCStdCelDynPow DCStdCelTotPow DCStdCelLeakPow DCNoClkStdCelDynPow Gap ICPStdCelDynPow ICPStdCelTotPow ICPStdCelLeakPow ICPNoClkStdCelDynPow DCGNBBLVth ICPGNBBLVth Gap DCVio ICPVio Gap DCBufInvCnt DCBufInvCntP DCSeqInst DCCombInst DCInst ICPInst Gap ICPBufInvCnt ICPBufInvCntP Gap CPUDCAllOpt CPUDCFullOpt CPUDCInsrtDFT CPUDCIncrOpt CPUDCOptnArea CPUDCIncrOptP Gap CLKDCAllOpt CLKDCFullOpt CLKDCInsrtDFT CLKDCIncrOpt CLKDCOptnArea Gap CLKDCAllOpt*(max(CValAllFlows("CLKDCAllOpt"))>3) CLKDCFullOpt*(max(CValAllFlows("CLKDCAllOpt"))>3) CLKDCInsrtDFT*(max(CValAllFlows("CLKDCAllOpt"))>3) CLKDCIncrOpt*(max(CValAllFlows("CLKDCAllOpt"))>3) CLKDCOptnArea*(max(CValAllFlows("CLKDCAllOpt"))>3) Gap CLKDCAllOpt*(max(CValAllFlows("CLKDCAllOpt"))>6) CLKDCFullOpt*(max(CValAllFlows("CLKDCAllOpt"))>6) CLKDCInsrtDFT*(max(CValAllFlows("CLKDCAllOpt"))>6) CLKDCIncrOpt*(max(CValAllFlows("CLKDCAllOpt"))>6) CLKDCOptnArea*(max(CValAllFlows("CLKDCAllOpt"))>6) Gap CPUDCCngRpt CLKDCCngRpt Gap ICPCPU*(max(CValAllFlows("CLKDCAllOpt"))>3) ICPCLK*(max(CValAllFlows("CLKDCAllOpt"))>3) DCICPCPU DCMem DCMCPkMem MemDCFullOpt MemDCIncrOpt ICPMem Gap PCNBBArea PCWNS PCTNSPM PCTNSPMT PCStdCelDynPow PCStdCelTotPow PCStdCelLeakPow PCNoClkStdCelDynPow Gap DPPMvArea DPPWNS DPPTNSPM DPPTNSPMT DPPStdCelDynPow DPPStdCelTotPow DPPStdCelLeakPow DPPNoClkStdCelDynPow Gap DCAGWirLn DCAGGRC*(max(CValAllFlows("DCAGPOvGC"))>0) DCAGPOvGC*(max(CValAllFlows("DCAGPOvGC"))>0) ICPAGGRC*(max(CValAllFlows("ICPAGPOvGC"))>0) ICPAGPOvGC*(max(CValAllFlows("ICPAGPOvGC"))>0) Gap CLKplace Gap CLKplace_0 CLKplace_1 CLKplace_2 CLKplace_3 Gap CLKDCICC2Ovr Gap DPRNBBArea DPRWNS DPRTNSPM DPRTNSPMT Gap RejRatioLodHeMain RejRatioLodHeIncr RejRatioGpow1Ona RejRatioGpow2Ona Gap Gap DCNBBArea DCLsMissing DCLsStrategy DCIsoMiss DCIsoRedund DCIsoNoPDCr DCIsoUnused DCIsoConst DCIsoPwS DCIsoNonUPF DCIsoPortDt DCAoDriver DCAoLoad DCNAoDriver DCPassGtCasc DCPGNtMsmtch DCOpCondErr Gap DCUPFNumLS DCUPFAreaLS DCUPFNumISO DCUPFAreaISO DCUPFNumRET DCUPFAreaRET DCUPFNumAO DCUPFAreaAO DCUPFNumSO DCUPFAreaSO DCUPFNumPM DCUPFAreaPM DCUPFNumNPMC DCUPFAreaNPMC Gap CheckSum Gap DCNMxTranPM DCNMxTranPMT ICPNMxTranPM ICPNMxTranPMT Gap DCCPUclk-gate DCNClkGate DCNClkGateAuto DCPClkGateAuto DCNGateReg DCPGateReg DCNumReg Gap DCNGateRegBit DCPGateRegBit DCNGateRegAutoBit DCPGateRegAutoBit DCNUngatedRegBit DCPUngatedRegBit Gap SGCells SGRegsN SGRegsP Gap'
	
	rows = 'Values MeanVal Mean Min Max 95%High 95%Low StdDev SDMean NSDMean Count Histgrm'
	if not add_multi:
		print('Reporting %s for %s'%(flow,target_day))
		rpt_cmd = '/u/prsuite/prs/bin/prreport.pl -max_cores 8 -showall -rows \"%s\" -base %s -html -htmlbrief -success \"^(Done|FM.*)\" -filterpg -stack -pairwise_wns -filterwns 0.015 -filterpg_useflow -units_conversion -noscatter -update -columns \'%s\' > %s_report.log' %(rows,for_report[-1],columns,flow)
	else:
		print('Reporting %s for %s'%(flow,target_day))
		rpt_cmd = '/u/prsuite/prs/bin/prreport.pl -max_cores 8 -showall -rows \"%s\" -allbase -html -htmlbrief -success \"^(Done|FM.*)\" -filterpg -stack -pairwise_wns -filterwns 0.015 -filterpg_useflow -units_conversion -noscatter -update -columns \'%s\' > %s_report.log'%(rows,columns,flow)

	cding = 'cd %s;'%last_ng_dir

	print(cding+rpt_cmd)
	
	# data for crawler
	test_date = datetime.strptime(for_report[0].split('_')[0],'D%Y%m%d')
	base_date = datetime.strptime(for_report[1].split('_')[0],'D%Y%m%d')
	
	test_name = "%s_%s%s"%(suff, test_date.month, test_date.day)
	base_name = "%s_%s%s"%(suff, base_date.month, base_date.day)
	
	test_flow = "%s_%s"%(for_report[0],suff)
	base_flow = "%s_%s"%(for_report[1],suff)
	
	crawl_col = [{
		"name" : [test_name, "vs" , base_name],
		"test" : test_flow,
		"base" : base_flow,
		"html" : "%s/%s/html/%s/index.html"%(output_dir,test_flow,base_flow) if add_multi else "%s/%s/html/index.html"%(output_dir,test_flow)
	}]

	if add_multi:
		for base in add_multi:
			base_flow = "%s_%s"%(base,suff)
			crawl_col.append({
				"name" : [test_name, "vs" , base],
				"test" : test_flow,
				"base" : base_flow,
				"html" : "%s/%s/html/%s/index.html"%(output_dir,test_flow,base_flow)
			})

	os.system(cding+rpt_cmd)

	return crawl_col


def report_n_crawl(columns,branch,suite,root_dir,branch_dir,week_dir,flow,ref_day,force_day,suff,baselines):

	if not os.path.exists(branch_dir) : os.mkdir(branch_dir)
	if not os.path.exists(week_dir)   : os.mkdir(week_dir)

	col_list = []


	col_list = last_week_trend_multi(
			root_dir,
			branch,
			suite, 
			flow,
			columns,
			ref_day,
			force_day,
			week_dir,
			suff,
			baselines
		)

	compare_json = {
			"table1": {
					"groups": ["stability","timing", "power", "area", "performance","links"],
					"columns": {}
					}
			}

	for i in range(len(col_list)):
		compare_json['table1']['columns']['c%s'%i] = col_list[i]

	# write compare conf
	json_file = open(os.path.join(week_dir,"compare_%s.json"%suff), "w")
	json_file.write(json.dumps(compare_json))
	json_file.close()

	#run_crawler
	compare_file = os.path.join(week_dir,"compare_%s.json"%suff)
	out_file = os.path.join(week_dir,"crawler_%s.html"%suff)
	crw_cmd = '%s -compare %s -out %s -xml %s -debug'%(crawler_script,compare_file,out_file,colums_xml)
	os.system(crw_cmd)


	print('DONE!!!!!')
	return True
