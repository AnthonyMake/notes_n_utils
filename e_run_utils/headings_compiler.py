#!/slowfs/dcopt105/vasquez/cnda/Conda/bin/python

# useful to avoid duplicated metrics using a custom text below
# write the list of metrics as the string below and space-separated text 
# to put below the metric in prs report, like this: 
#
# Example:
# 
# metrics = '''
# FlowLong 
# DCMvArea <HEADING FOR AREA>
# ICPMvArea 
# DCICPMvArea
# DCWNS <HEADING FOR WNS>
# DCTNSPM
# DCTNSPMT
# DCTNSPF
# ICPWNS
# ICPTNSPM
# ICPTNSPMT
# '''

# new metric list for SRM_ICC2_spg_timing_opt_area in branch R suite RMS:

power_metrics = '''
FlowLong
DCMvArea
ICPMvArea
DCICPMvAreaE
DCWNS
DCTNSPM
DCTNSPMT
DCTNSPF
ICPWNS
ICPTNSPM
ICPTNSPMT
ICPTNSPF
DCICPWNSE
DCICPTNSE
Gap
DCStdCelDynPow  Raw
DCStdCelDynPow*(CVal("DCZroTRRegPer")<90)   ZroTR<90%
DCStdCelDynPow*(CVal("DCTotBrkAct")<=0)     BrkAct=0
DCStdCelDynPow*((CVal("DCZroTRRegPer")<90)&&(CVal("DCTotBrkAct")<=0))   Trust
DCStdCelTotPow
DCStdCelLeakPow
DCNoClkStdCelDynPow
Gap
DCClkNetInterPow
DCRegInterPow
DCSeqInterPow
DCCombInterPow
DCClkNetSWPow
DCRegSWPow
DCSeqSWPow
DCCombSWPow
Gap
ICPStdCelDynPow
ICPStdCelTotPow
ICPStdCelLeakPow
ICPNoClkStdCelDynPow
Gap
DCGNBBLVth
ICPGNBBLVth
DCVio
ICPVio
DCBufInvCnt
DCBufInvCntP
DCSeqInst
DCCombInst
DCInst
ICPInst
ICPBufInvCnt
ICPBufInvCntP
Gap 
CLKDCAllOpt
CLKDCFullOpt
CLKDCInsrtDFT
CLKDCIncrOpt
CLKDCOptnArea
Gap
CLKDCAllOpt*(max(CValAllFlows("CLKDCAllOpt"))>3) >=3.0
CLKDCFullOpt*(max(CValAllFlows("CLKDCAllOpt"))>3) >=3.0
CLKDCInsrtDFT*(max(CValAllFlows("CLKDCAllOpt"))>3) >=3.0
CLKDCIncrOpt*(max(CValAllFlows("CLKDCAllOpt"))>3) >=3.0
CLKDCOptnArea*(max(CValAllFlows("CLKDCAllOpt"))>3) >=3.0
Gap
CLKDCAllOpt*(max(CValAllFlows("CLKDCAllOpt"))>6) >=6.0
CLKDCFullOpt*(max(CValAllFlows("CLKDCAllOpt"))>6) >=6.0
CLKDCInsrtDFT*(max(CValAllFlows("CLKDCAllOpt"))>6) >=6.0
CLKDCIncrOpt*(max(CValAllFlows("CLKDCAllOpt"))>6) >=6.0
CLKDCOptnArea*(max(CValAllFlows("CLKDCAllOpt"))>6) >=6.0
Gap
CPUDCCngRpt
CLKDCCngRpt
ICPCPU*(max(CValAllFlows("CPUDCFullOpt"))>3)
ICPCLK*(max(CValAllFlows("CPUDCFullOpt"))>3)
DCICPCPU
DCMem
DCMCPkMem
MemDCFullOpt
MemDCIncrOpt
ICPMem
PCNBBArea
PCWNS
PCTNSPM
PCTNSPMT
PCStdCelDynPow
PCStdCelTotPow
PCStdCelLeakPow
PCNoClkStdCelDynPow
DPPMvArea
DPPWNS
DPPTNSPM
DPPTNSPMT
DPPStdCelDynPow
DPPStdCelTotPow
DPPStdCelLeakPow
DPPNoClkStdCelDynPow
DCAGWirLn
DCAGGRC*(max(CValAllFlows("DCAGPOvGC"))>0)
DCAGPOvGC*(max(CValAllFlows("DCAGPOvGC"))>0)
ICPAGGRC*(max(CValAllFlows("ICPAGPOvGC"))>0)
ICPAGPOvGC*(max(CValAllFlows("ICPAGPOvGC"))>0)
Gap
CLKplace
CLKplace_0
CLKplace_1
CLKplace_2
CLKplace_3
CLKDCICC2Ovr
DPRNBBArea
DPRWNS
DPRTNSPM
DPRTNSPMT
RejRatioLodHeMain
RejRatioLodHeIncr
RejRatioGpow1Ona
RejRatioGpow2Ona
CheckSum
Gap
DCRegTrSum
ICPRegTrSum
DCRegNum
ICPRegNum
DCZroTRRegNum
ICPZroTRRegNum
DCZroTRRegPer
ICPZroTRRegPer
DCCombTrSum
ICPCombTrSum
DCDynScnCnt
ICPDynScnCnt
DCScnCnt
ICPScnCnt
DCCA
Gap
DCTotBrkAct
Gap
DCCPUclk-gate
DCNClkGate
DCNGateReg
DCPGateReg
DCNClkGateAuto 
DCNGateRegAutoBit 
DCPGateRegAutoBit 
DCNUngatedRegBit 
DCPUngatedRegBit 
DCNGateRegBit 
DCPGateRegBit 
DCNumReg
Gap
DCMBPackR
Gap
SGCells 
SGRegsN 
SGRegsP 
Gap'''


metrics = power_metrics

columns = []
headings = []
for line in metrics.splitlines():
    
    line = line.strip().split()
    if not line: continue

    if len(line) == 2:
        columns.append(line[0])
        headings.append(line[1])
    elif len(line) == 1:
        columns.append(line[0])
        headings.append('')
    else:
        # ?
        print('whatsup here?',line)


print('-columns \'%s\''%' '.join(columns))
print('-headings \'%s\''%','.join(headings))
