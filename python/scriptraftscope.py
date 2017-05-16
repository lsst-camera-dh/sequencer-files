import scope
import multiscope



#datadir = '/Users/nayman/Documents/REB/TS8/ETU2Dev/'
#datadir = '/Users/nayman/Documents/REB/TS8/ETU2Dev/cj-tst2'
#datadir = '/Users/nayman/Documents/REB/TS8/ETU2Dev/mod3b_scan'
#datadir = '/Users/nayman/Documents/REB/TS8/ETU2Dev/cj20170324'
#datadir = '/Users/nayman/Documents/REB/TS8/RTM1/Run4846D/RTM1new_mod50'
datadir = '/Users/nayman/Documents/REB/TS8/RTM2/rtm-scan-mode-data/'


#seqfile = 'TS8_ITL_ResetFirst_20170313-scan-mode.seq'
#seqfile = 'TS8_ITL_ResetFirst_CJ_20170321_mod2.seq'
#seqfile = 'TS8_ITL_ResetFirst_CJ_20170321_mod3.seq'
#seqfile = 'TS8_ITL_ResetFirst_CJ_20170321_mod4s.seq'
#seqfile = 'RTM1/TS8_ITL_RTM1new_mod50.seq'
seqfile = 'RTM2/TS8_E2V_shorterP_scan.seq'

#tmbasefile = "rtm2-scan-tm-bias/00-rtm2-scan-tm-bias_2.fits"
tmbasefile = "rtm2-scan-tm-half-full/00-rtm2-scan-tm-675nm-25s_1.fits"
#older: "00_readRG-scan.fits", "00_mod4s_bias-scan.fits", "00_readS3Linvert-scan.fits", "00_readS2-scan.fits"
# "00_readS1-scan.fits", "00_readS1invert-scan.fits", "00_test-cj-mod3b_transp_dark_scan2.fits"
# "00_test-cj-mod3b_flat_transp_scan2.fits, "scan-mode-tm-cj-mod2/00_test-cj-mod2.fits"
# "scan-mode-transparent/Image_R00.Reb0_20170320200751.dat"
# "00_RTM1noise_rmBufferS1S3_2_tm.fits", "00_RTM1new_mod50_1s-scan.fits"

#---- Scan display for all raft channels

#multiscope.raft_display_allchans(tmbasefile, datadir)

#---- Combined display of single channel with clock sequences

#scope.combined_scope_display("scan-mode-dsi/Image_R00.Reb0_20170320200320.dat",
#                             "scan-mode-transparent/Image_R00.Reb0_20170320200751.dat",
#                             seqfile=seqfile, c=0, datadir=datadir)

#scope.combined_scope_display("scan-mode-dsi-cj-mod2/01_test-cj-mod2-dsi.fits",
#                             "scan-mode-tm-cj-mod2/01_test-cj-mod2.fits",
#                             seqfile=seqfile, c=3, datadir=datadir, loc="01")

#for c in range(16):
    #scope.combined_scope_display("rtm2-scan-dsi-bias/11-rtm2-scan-bias_2.fits",
    #                             "rtm2-scan-tm-bias/11-rtm2-scan-tm-bias_2.fits",
    #                           seqfile=seqfile, c=c, datadir=datadir, loc="11", display=False)
    #scope.combined_scope_display("rtm2-scan-dsi-half-full/11-rtm2-scan-675nm-25s_1.fits",
    #                            "rtm2-scan-tm-half-full/11-rtm2-scan-tm-675nm-25s_1.fits",
    #                            seqfile=seqfile, c=c, datadir=datadir, loc="11", display=False)

#for c in range(16):
#    scope.combined_scope_display("01_RTM1noise_rmBufferS1S3_2.fits",
#                             "01_RTM1noise_rmBufferS1S3_2_tm.fits",
#                             seqfile=seqfile, c=c, datadir=datadir, loc="01")



#---- Display of all channels, one graph per CCD

#for s in ["%d%d" % (i, j) for i in range(3) for j in range(3)]:
#    scope.scan_scope_display(None, "rtm2-scan-tm-bias/%s-rtm2-scan-tm-bias_2.fits" % s, datadir=datadir)
    #scope.scan_scope_display(None, "%s_test-cj-mod3b_transp_dark_scan2.fits" % s, datadir=datadir)

# single CCD
#scope.scan_scope_display(None, "00_RTM1noise_rmBufferS1S3_2_tm.fits", datadir=datadir)


#---- Comparing scans channel per channel for a single CCD

# Mixing raw and fits files does not work now
#listscans = ["reset-first/scan-mode-transparent/Image_R00.Reb0_20170320200751.dat",
#             "cj-tst2/scan-mode-tm-cj-mod2/00_test-cj-mod2.fits",
#             "mod3b_scan/00_test-cj-mod3b_transp_dark_scan2.fits"]
#listscans = ["cj-tst2/scan-mode-tm-cj-mod2/00_test-cj-mod2.fits",
#             "mod3b_scan/00_test-cj-mod3b_transp_dark_scan2.fits"]
#listlabels = ["Mod2", "Mod3"]

#listlabels = [s for s in ["%d%d" % (i, j) for i in range(2) for j in range(3)]]
#listscans = ["%s_RTM1noise_rmBufferS1S3_2_tm.fits" % s for s in listlabels]

#scope.compare_scope_display(listscans, listlabels, datadir)


#---- Checking statistics on scans

tmbasefile = "rtm2-scan-tm-bias/02-rtm2-scan-tm-bias_2.fits"
scope.cut_scan_plot(tmbasefile, 4, datadir=datadir, polynomfit=True)
#tmbasefile = "rtm2-scan-tm-half-full/02-rtm2-scan-tm-675nm-25s_1.fits"
#scope.cut_scan_plot(tmbasefile, 4, datadir=datadir, polynomfit=False)

tmbasefile = "rtm2-scan-tm-bias/11-rtm2-scan-tm-bias_2.fits"
scope.cut_scan_plot(tmbasefile, 4, datadir=datadir, polynomfit=True)
#tmbasefile = "rtm2-scan-tm-half-full/11-rtm2-scan-tm-675nm-25s_1.fits"
#scope.cut_scan_plot(tmbasefile, 4, datadir=datadir, polynomfit=False)

#basefile = "rtm2-scan-dsi-bias/02-rtm2-scan-bias_2.fits"
#scope.cut_scan_plot(basefile, 4, datadir=datadir, polynomfit=False)
#basefile = "rtm2-scan-dsi-half-full/02-rtm2-scan-675nm-25s_1.fits"
#scope.cut_scan_plot(basefile, 4, datadir=datadir, polynomfit=False)

#basefile = "rtm2-scan-dsi-bias/11-rtm2-scan-bias_2.fits"
#scope.cut_scan_plot(basefile, 4, datadir=datadir, polynomfit=False)
#basefile = "rtm2-scan-dsi-half-full/11-rtm2-scan-675nm-25s_1.fits"
#scope.cut_scan_plot(basefile, 4, datadir=datadir, polynomfit=False)

