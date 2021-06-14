import os,sys,re

suite_path   = '/remote/dcopt077/nightly_prs/p2019.03-SP/DC_ICC2'
nightly_list = 'D20191017_03_25 D20191204_14_30'.split(' ')
report       = 'srm_icc2_spg_timing_opt_area'
flows        = 'SRM_ICC2_spg_timing_opt_area'.split(' ')

report_name  = "sign_off"

# removed ARCHS438 bad power reporting config
designs      = "ARCHS438,A53,A53_ARM,A57_Non_CPU,A73_CPU,ARCHS38_16nm,ARCHS38_7nm,CortexM3,X5376,archipelago_N12_6T,dcp212_Xm_Xttop,dcp245_SPEEDY28_TOP,dcp246_Xm_Xtmem,dcp247_VDD5_mux2,dcp269_rob,dcp270_enterprise_UPF,dcp275_archipelago,dcp276_xbar,dcp426_opf_fp,dcp427_DWC_usb3,dcp428_DWC_ddr,dcp514_JDSIIP3A,dcp517_PMA,dcp518_top,dcp519_fdeq_pnrb,dcp520_ccu_msw,dcp521_DWC_pcie_dm,dcp522_c8docsis31_rx_top,dcp550_memoir,dcp556_DSH,dcp557_opb_fp,dcp564_leon3_mp_20_sset_ssink,dcp568_mmu2,dcp569_GORDON,dcp570_b33,dcp579_pba_fp,dcp589_vd32043_top,dcp596_ibe,dcp597_mmu_thdo,dcp599_rgx_tpu_mcu,dcp607_mpcore,dcp611_arm926ejs,dcp615_CortexM3,dcp616_falcon_cpu,dcp630_jones,dcp631_mercer,dcp632_teague,dcp778_datapath,dcp780_cbs_pollux_tx_dig,dcp571_hrp_xb_m"

## columns      = 'FlowLong DCMvArea ICPMvArea DCICPMvAreaE Gap DCWNS DCTNSPM DCTNSPMT ICPWNS ICPTNSPM ICPTNSPMT DCICPWNSE Gap DCStdCelDynPow DCStdCelTotPow DCStdCelLeakPow DCNoClkStdCelDynPow Gap ICPStdCelDynPow ICPStdCelTotPow ICPStdCelLeakPow ICPNoClkStdCelDynPow DCGNBBLVth ICPGNBBLVth Gap DCVio ICPVio Gap DCBufInvCnt DCBufInvCntP DCSeqInst DCCombInst DCInst ICPInst Gap ICPBufInvCnt ICPBufInvCntP Gap CPUDCAllOpt CPUDCFullOpt CPUDCInsrtDFT CPUDCIncrOpt CPUDCOptnArea CPUDCIncrOptP Gap CLKDCAllOpt CLKDCFullOpt CLKDCInsrtDFT CLKDCIncrOpt CLKDCOptnArea Gap CPUDCCngRpt CLKDCCngRpt Gap ICPCPU  ICPCLK DCICPCPU DCMem MemDCFullOpt MemDCIncrOpt ICPMem Gap PCNBBArea PCWNS PCTNSPM PCTNSPMT PCStdCelDynPow PCStdCelTotPow PCStdCelLeakPow PCNoClkStdCelDynPow Gap DPPMvArea DPPWNS DPPTNSPM DPPTNSPMT DPPStdCelDynPow DPPStdCelTotPow DPPStdCelLeakPow DPPNoClkStdCelDynPow Gap DCAGWirLn DCAGGRC Gap DCCPUclk-gate DCNClkGate DCNGateReg DCPGateReg DCNumReg Gap CLKplace Gap CLKplace_0 CLKplace_1 CLKplace_2 CLKplace_3 Gap CLKDCICC2Ovr Gap DPRNBBArea DPRWNS DPRTNSPM DPRTNSPMT Gap'
columns = 'FlowLong DCMvArea ICPMvArea DCICPMvAreaE Gap DCWNS DCTNSPM DCTNSPMT ICPWNS ICPTNSPM ICPTNSPMT DCICPWNSE Gap DCStdCelDynPow DCStdCelTotPow DCStdCelLeakPow DCNoClkStdCelDynPow Gap ICPStdCelDynPow ICPStdCelTotPow ICPStdCelLeakPow ICPNoClkStdCelDynPow DCGNBBLVth ICPGNBBLVth Gap DCVio ICPVio Gap DCBufInvCnt DCBufInvCntP DCSeqInst DCCombInst DCInst ICPInst Gap ICPBufInvCnt ICPBufInvCntP Gap CPUDCAllOpt*(max(CValAllFlows(\"CPUDCFullOpt\"))>3) CPUDCFullOpt*(max(CValAllFlows(\"CPUDCFullOpt\"))>3) CPUDCInsrtDFT*(max(CValAllFlows(\"CPUDCFullOpt\"))>3) CPUDCIncrOpt*(max(CValAllFlows(\"CPUDCFullOpt\"))>3) CPUDCOptnArea*(max(CValAllFlows(\"CPUDCFullOpt\"))>3) CPUDCIncrOptP*(max(CValAllFlows(\"CPUDCFullOpt\"))>3) Gap CLKDCAllOpt*(max(CValAllFlows(\"CPUDCFullOpt\"))>3) CLKDCFullOpt*(max(CValAllFlows(\"CPUDCFullOpt\"))>3) CLKDCInsrtDFT*(max(CValAllFlows(\"CPUDCFullOpt\"))>3) CLKDCIncrOpt*(max(CValAllFlows(\"CPUDCFullOpt\"))>3) CLKDCOptnArea*(max(CValAllFlows(\"CPUDCFullOpt\"))>3) Gap CPUDCCngRpt CLKDCCngRpt Gap ICPCPU*(max(CValAllFlows(\"CPUDCFullOpt\"))>3)  ICPCLK*(max(CValAllFlows(\"CPUDCFullOpt\"))>3) DCICPCPU DCMem DCMCPkMem MemDCFullOpt MemDCIncrOpt ICPMem Gap PCNBBArea PCWNS PCTNSPM PCTNSPMT PCStdCelDynPow PCStdCelTotPow PCStdCelLeakPow PCNoClkStdCelDynPow Gap DPPMvArea DPPWNS DPPTNSPM DPPTNSPMT DPPStdCelDynPow DPPStdCelTotPow DPPStdCelLeakPow DPPNoClkStdCelDynPow Gap DCAGWirLn DCAGGRC*(max(CValAllFlows(\"DCAGPOvGC\"))>0) DCAGPOvGC*(max(CValAllFlows(\"DCAGPOvGC\"))>0) ICPAGGRC*(max(CValAllFlows(\"ICPAGPOvGC\"))>0) ICPAGPOvGC*(max(CValAllFlows(\"ICPAGPOvGC\"))>0) Gap DCCPUclk-gate DCNClkGate DCNGateReg DCPGateReg DCNumReg Gap CLKplace Gap CLKplace_0 CLKplace_1 CLKplace_2 CLKplace_3 Gap CLKDCICC2Ovr Gap DPRNBBArea DPRWNS DPRTNSPM DPRTNSPMT Gap'

rows         = "MeanVal Mean Mean1/X Min Max 95%High 95%Low StdDev SDMean NSDMean Count Histgrm"

cache_files    = []
flow_prefixes  = []
flow_name_w_prefix = []

def look_flows(cache_list):

    common_flows = []
    for cache in cache_list:
        
        if os.path.isfile(cache):
            cache_txt = open(cache, 'r').readlines()

            ptrn_flow = r'^Path\s+([A-Za-z0-9_]+)/.+'


            for line in cache_txt:
                m = re.match(ptrn_flow,line)
                if m:
                    flow = m.group(1)
                    
                    if flow not in common_flows:
                        common_flows.append(flow)
        else:
            print('%s is not a file?'%cache)
    
    print(common_flows)

for nightly in nightly_list:
    
    report_dir_name = 'prs_report.%s.out'%report
    cache_gz        = os.path.join(suite_path,nightly,report_dir_name,'prreport.cache.gz')

    if os.path.isfile(cache_gz):
        
        cmd_mk_temp_dir = 'mkdir %s'%nightly
        cmd_mk_ln = 'ln -s %s %s/prreport.cache.gz'%(cache_gz,nightly)
        cmd_unzip = 'zcat %s/prreport.cache.gz > %s/prreport.cache'%(nightly,nightly)

        try: 
            os.system(cmd_mk_temp_dir)
            os.system(cmd_mk_ln)
            os.system(cmd_unzip)
        except:
            print('Error: Couldn\'t uncompress %s in local dir'%cache_gz)

        cache_files.append('%s/%s'%(nightly,'prreport.cache'))
        flow_prefixes.append('%s_'%nightly)
        
        for f in flows: flow_name_w_prefix.append('%s_%s'%(nightly,f))

    else:
        print('Error: Couldn\'t locate %s'%cache_gz)

look_flows(cache_files)




prrreport_cmd = "/u/prsuite/prs/bin/prreport.pl -showall -rows \"%s\" -allbase -html -success \"^(Done|FM.*|NDBFail|PR*|PL*)\" -filterpg -stack -columns \'%s\' -rcache -cachefiles \"%s\" -flowprefixes \"%s\" -O/%s/%s"%(rows,columns,' '.join(cache_files),' '.join(flow_prefixes),','.join(flow_name_w_prefix),designs)

print('\n')
print(prrreport_cmd)

try:
    os.system('set PRSUITE_HOME=/u/prsuite/prs')
    os.system(prrreport_cmd)
    # print(prreport_cmd)
except:
    print('Error: Couldn\'t run prreport.')
