
__DCICC2_DESIGNS__ = 'A53 A53_ARM A57_Non_CPU A73_CPU ARCHS38_16nm ARCHS38_7nm ARCHS438 CortexM3 X5376 archipelago_N12_6T dcp212_Xm_Xttop dcp245_SPEEDY28_TOP dcp246_Xm_Xtmem dcp247_VDD5_mux2 dcp269_rob dcp270_enterprise_UPF dcp275_archipelago dcp276_xbar dcp426_opf_fp dcp427_DWC_usb3 dcp428_DWC_ddr dcp514_JDSIIP3A dcp517_PMA dcp518_top dcp519_fdeq_pnrb dcp520_ccu_msw dcp521_DWC_pcie_dm dcp522_c8docsis31_rx_top dcp550_memoir dcp556_DSH dcp557_opb_fp dcp564_leon3_mp_20_sset_ssink dcp568_mmu2 dcp569_GORDON dcp570_b33 dcp579_pba_fp dcp589_vd32043_top dcp596_ibe dcp597_mmu_thdo dcp599_rgx_tpu_mcu dcp607_mpcore dcp611_arm926ejs dcp615_CortexM3 dcp616_falcon_cpu dcp630_jones dcp631_mercer dcp632_teague dcp778_datapath dcp780_cbs_pollux_tx_dig dcp571_hrp_xb_m'.split(' ')

__DCICC2_DESIGNS_wlm__ = 'dcp212_Xm_Xttop dcp245_SPEEDY28_TOP dcp246_Xm_Xtmem dcp247_VDD5_mux2 dcp269_rob dcp270_enterprise_UPF dcp275_archipelago dcp276_xbar dcp426_opf_fp dcp427_DWC_usb3 dcp428_DWC_ddr dcp514_JDSIIP3A dcp517_PMA dcp518_top dcp519_fdeq_pnrb dcp520_ccu_msw dcp521_DWC_pcie_dm dcp522_c8docsis31_rx_top dcp550_memoir dcp556_DSH dcp557_opb_fp dcp564_leon3_mp_20_sset_ssink dcp568_mmu2 dcp569_GORDON dcp570_b33 dcp579_pba_fp dcp589_vd32043_top dcp596_ibe dcp597_mmu_thdo dcp599_rgx_tpu_mcu dcp607_mpcore dcp611_arm926ejs dcp615_CortexM3 dcp616_falcon_cpu dcp630_jones dcp631_mercer dcp632_teague dcp778_datapath dcp780_cbs_pollux_tx_dig dcp571_hrp_xb_m'.split(' ')

__DES_bwl24d2a4__ = 'dcp570_b33 dcp569_GORDON dcp426_opf_fp A73_CPU dcp579_pba_fp A57_Non_CPU dcp778_datapath dcp564_leon3_mp_20_sset_ssink dcp571_hrp_xb_m archipelago_N12_6T'.split(' ')

__DCICC2_DESIGNS__set = set(__DCICC2_DESIGNS__)
__DCICC2_DESIGNS_wlm__set = set(__DCICC2_DESIGNS_wlm__)
__DES_bwl24d2a4__set = set(__DES_bwl24d2a4__)


__DCICC2_DESIGNS_00__ = set(__DCICC2_DESIGNS__[:len(__DCICC2_DESIGNS__)//2])
__DCICC2_DESIGNS_01__ = set(__DCICC2_DESIGNS__[len(__DCICC2_DESIGNS__)//2:])

print(",".join(__DCICC2_DESIGNS_01__ - __DES_bwl24d2a4__set))


