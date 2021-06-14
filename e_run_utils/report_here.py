#! /slowfs/dcopt105/vasquez/cnda/Conda/bin/python
import os, subprocess

report_bin   = '/u/prsuite/prs/bin/prreport.pl'
report_name  = 'prodrigu_'
baseline     = 'SRM_ICC2_spg_timing_opt_area'
flows        = 'UPF_SRM_p2019.03_sp_dev UPF_SRM_p2019.03_sp_dev_base UPF_SRM_q2019.12_sp_dev UPF_SRM_q2019.12_sp_dev_base'.replace(' ',',')
designs      = 'dcp203_tnt_mpw_sset_ssink dcp246_Xm_Xtmem dcp270_enterprise_UPF dcp273_IP110TOP dcp523_rds_testpd_topio dcp563_gem_netra dcp563_gem_netra_iss dcp564_leon3_mp_20_sset_ssink dcp569_GORDON dcp589_vd32043_top dcp590_or1200_top dcp607_mpcore dcp607_mpcore_iss dcp610_arm1176jzfs dcp610_arm1176jzfs_iss dcp610_arm1176jzfs_snet_diff dcp610_arm1176jzfs_sset dcp610_arm1176jzfs_sset_diff dcp610_arm1176jzfs_sset_ssink dcp611_arm926ejs dcp611_arm926ejs_iss dcp611_arm926ejs_snet_diff dcp611_arm926ejs_sset dcp611_arm926ejs_sset_diff dcp611_arm926ejs_sset_ssink dcp615_CortexM3 dcp615_CortexM3_iss dcp615_CortexM3_snet_diff dcp615_CortexM3_sset dcp615_CortexM3_sset_diff dcp615_CortexM3_sset_ssink dcp616_falcon_cpu dcp616_falcon_cpu_iss dcp802_TI_eag_cpu upf564_leon3_01_sc upf564_leon3_02_sl upf564_leon3_06_sset upf564_leon3_08_sset_ssink upf564_leon3_19_sset_ssink upf564_leon3_20_sset_spa upf564_leon3_21_sset_fan upf564_leon3_22_sset_fan A57_Non_CPU A73_CPU A73_Non_CPU CortexM3 X5376 A57_CPU A72_CPU A75_prometheus_PAC16'.replace(' ',',')


report_cmd = '''cd ''' + os.getcwd() + '''\
    ;echo "Generating PRS report.''' + report_name + '''.out ..."
    ''' + report_bin + '''\
    -pairwise_wns -filterwns 0.015 -filterpg_useflow -units_conversion -update \
    -columns 'Flow DCNBBArea ICPNBBArea DCICPNBBAreaE DCWNS ICPWNS DCICPWNSE DCVio ICPVio DCCPU*(CVal("DCCPU","'''+baseline+'''")>1.0) ICPCPU DCICPCPU DCMem*(CVal("DCMem","''' + baseline + '''")>500)' \
    -O/''' +flows+'''/- \
    -rows "MeanVal Mean Min Max 95%High 95%Low StdDev SDMean NSDMean Count Histgrm" \
    -out report.''' + report_name +'''.out \
    -base ''' + baseline + ''' \
    -html \
    -success "^(Done|FM.*)" \
          -O/''' + flows + '/' + designs + '''  \
          -stack  \
          -filterpg  \
          -filtercor  \
          -allbase  \
          -columns 'FlowLong DCMvArea ICPMvArea DCICPMvAreaE Gap DCWNS DCTNSPM DCTNSPMT DCTNSPF ICPWNS ICPTNSPM ICPTNSPMT ICPTNSPF DCICPWNSE DCICPTNSE Gap DCStdCelDynPow DCStdCelTotPow DCStdCelLeakPow DCNoClkStdCelDynPow Gap ICPStdCelDynPow ICPStdCelTotPow ICPStdCelLeakPow ICPNoClkStdCelDynPow DCGNBBLVth ICPGNBBLVth Gap DCVio ICPVio Gap DCBufInvCnt DCBufInvCntP DCSeqInst DCCombInst DCInst ICPInst Gap ICPBufInvCnt ICPBufInvCntP Gap CPUDCAllOpt*(max(CValAllFlows("CPUDCFullOpt"))>3) CPUDCFullOpt*(max(CValAllFlows("CPUDCFullOpt"))>3) CPUDCInsrtDFT*(max(CValAllFlows("CPUDCFullOpt"))>3) CPUDCIncrOpt*(max(CValAllFlows("CPUDCFullOpt"))>3) CPUDCOptnArea*(max(CValAllFlows("CPUDCFullOpt"))>3) CPUDCIncrOptP*(max(CValAllFlows("CPUDCFullOpt"))>3) Gap CLKDCAllOpt*(max(CValAllFlows("CPUDCFullOpt"))>3) CLKDCFullOpt*(max(CValAllFlows("CPUDCFullOpt"))>3) CLKDCInsrtDFT*(max(CValAllFlows("CPUDCFullOpt"))>3) CLKDCIncrOpt*(max(CValAllFlows("CPUDCFullOpt"))>3) CLKDCOptnArea*(max(CValAllFlows("CPUDCFullOpt"))>3) Gap CPUDCCngRpt CLKDCCngRpt Gap ICPCPU*(max(CValAllFlows("CPUDCFullOpt"))>3) ICPCLK*(max(CValAllFlows("CPUDCFullOpt"))>3) DCICPCPU DCMem DCMCPkMem MemDCFullOpt MemDCIncrOpt ICPMem Gap PCNBBArea PCWNS PCTNSPM PCTNSPMT PCStdCelDynPow PCStdCelTotPow PCStdCelLeakPow PCNoClkStdCelDynPow Gap DPPMvArea DPPWNS DPPTNSPM DPPTNSPMT DPPStdCelDynPow DPPStdCelTotPow DPPStdCelLeakPow DPPNoClkStdCelDynPow Gap DCAGWirLn DCAGGRC*(max(CValAllFlows("DCAGPOvGC"))>0) DCAGPOvGC*(max(CValAllFlows("DCAGPOvGC"))>0) ICPAGGRC*(max(CValAllFlows("ICPAGPOvGC"))>0) ICPAGPOvGC*(max(CValAllFlows("ICPAGPOvGC"))>0) Gap DCCPUclk-gate DCNClkGate DCNGateReg DCPGateReg DCNumReg Gap CLKplace Gap CLKplace_0 CLKplace_1 CLKplace_2 CLKplace_3 Gap CLKDCICC2Ovr Gap DPRNBBArea DPRWNS DPRTNSPM DPRTNSPMT Gap ' \
          -rows 'MeanVal Mean Mean1/X Min Max 95%High 95%Low StdDev SDMean NSDMean Count Histgrm' \
    >&! ./LOG.prreport.''' + report_name

print(report_cmd)
try :
    cmd_obj = subprocess.run(report_cmd, executable= '/bin/csh',shell = True,stdout=subprocess.PIPE)
    cmd_ret = cmd_obj.stdout.decode("utf-8").split()
    
except:
    print('something went wrong')
