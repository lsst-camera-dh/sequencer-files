import scope
import raftstats
import multiscope

rtm = "RTM8"

#datadir = '/Users/nayman/Documents/REB/TS8/ETU2Dev/'
#datadir = '/Users/nayman/Documents/REB/TS8/ETU2Dev/cj-tst2'
#datadir = '/Users/nayman/Documents/REB/TS8/ETU2Dev/mod3b_scan'
#datadir = '/Users/nayman/Documents/REB/TS8/ETU2Dev/cj20170324'
#datadir = '/Users/nayman/Documents/REB/TS8/RTM1/rmBufferS1S3'
#datadir = '/Users/nayman/Documents/REB/TS8/RTM2/rtm-scan-mode-data/'
#datadir = '/Users/nayman/Documents/REB/TS8/ETU1/IR2/2017-06-21'
#datadir = '/Users/nayman/Documents/REB/TS8/RTM8/rtm8scanmodetm1'
#datadir = '/Users/nayman/Documents/REB/TS8/RTM8/RDscans'
datadir = '/Users/nayman/Documents/REB/TS8/%s/rtm8seqtests3' % rtm

#seqfile = 'TS8_ITL_ResetFirst_20170313-scan-mode.seq'
#seqfile = 'TS8_ITL_ResetFirst_CJ_20170321_mod2.seq'
#seqfile = 'TS8_ITL_ResetFirst_CJ_20170321_mod3.seq'
#seqfile = 'TS8_ITL_ResetFirst_CJ_20170321_mod4s.seq'
#seqfile = 'RTM1/TS8_ITL_2s_newflush_v2.seq'
#seqfile = 'RTM2/seq-e2v-shorterp-2s.seq'
#seqfile = 'ETU1/TS8_ITL_fix.seq'
seqfile = 'RTM8/TS8_ITL_longS1_scan.seq'

tmbasefile = "basescan/00_TS8_ITL_longS1_scan_tm_2.fits"
#tmbasefile = "00_TS8_ITL_RGhigh_longS1_fix_bias_scan_dsi.fits"
#tmbasefile = "00_TS8_ITL_clockcross90_bias_scan_tm.fits"
#tmbasefile = "00_RD14_tm_1s_2.fits"
#tmbasefile = "00_rtm8_tm_1_bias.fits"
#tmbasefile = "REB0/00_bias2.fits"
#tmbasefile = "rtm2-scan-tm-bias/00-rtm2-scan-tm-bias_2.fits"
#tmbasefile = "00_shorterp-2s_scan_30s_flat_tm_exp1.fits"
#tmbasefile = "00_test_tm_20170621210028.fits"
#tmbasefile = "00_RTM1noise_rmBufferS1S3_2_tm.fits"
#dsibasefile = "00_test_tm_20170621204509.fits"

# returns tuple: (list of files, list of segments)
l = raftstats.get_fits_raft(inputfile=tmbasefile, datadir=datadir)


#older: "00_readRG-scan.fits", "00_mod4s_bias-scan.fits", "00_readS3Linvert-scan.fits", "00_readS2-scan.fits"
# "00_readS1-scan.fits", "00_readS1invert-scan.fits", "00_test-cj-mod3b_transp_dark_scan2.fits"
# "00_test-cj-mod3b_flat_transp_scan2.fits, "scan-mode-tm-cj-mod2/00_test-cj-mod2.fits"
# "scan-mode-transparent/Image_R00.Reb0_20170320200751.dat"
# "00_RTM1noise_rmBufferS1S3_2_tm.fits", "00_RTM1new_mod50_1s-scan.fits"

#---- Scan display for all raft channels

#multiscope.raft_display_allchans(tmbasefile, datadir, '%s with long S1 clocking and clamp during RD' % rtm)

#---- Combined display of single channel with clock sequences

#scope.combined_scope_display("scan-mode-dsi/Image_R00.Reb0_20170320200320.dat",
#                             "scan-mode-transparent/Image_R00.Reb0_20170320200751.dat",
#                             seqfile=seqfile, c=0, datadir=datadir)

for f,s in zip(l[0],l[1]):
    scope.combined_scope_display(None, f,
                                 seqfile=seqfile, c=12, datadir=datadir, loc=s)

#for c in range(16):
#    scope.combined_scope_display("rtm8scanmodetm1/01_rtm8_tm_1_bias.fits",
#                                 "rtm8scanmodedsi1/01_rtm8_dsi_1_bias.fits",
#                                 seqfile=seqfile, c=c, datadir=datadir, loc="01", display=True)
    #scope.combined_scope_display("rtm2-scan-dsi-half-full/11-rtm2-scan-675nm-25s_1.fits",
    #                            "rtm2-scan-tm-half-full/11-rtm2-scan-tm-675nm-25s_1.fits",
    #                            seqfile=seqfile, c=c, datadir=datadir, loc="11", display=False)

#s = "21"
#for c in range(16):
#    scope.combined_scope_display(dsibasefile.replace("00_", s + '_'),
#                                 tmbasefile.replace("00_", s + '_'),
#                                 seqfile=seqfile, c=c, datadir=datadir, loc=s)



#---- Display of all channels, one graph per CCD

#for s in ["%d%d" % (i, j) for i in range(3) for j in range(3)]:
#    scope.scan_scope_display(None, "rtm2-scan-tm-bias/%s-rtm2-scan-tm-bias_2.fits" % s, datadir=datadir)
#    scope.scan_scope_display(None, "%s_test-cj-mod3b_transp_dark_scan2.fits" % s, datadir=datadir)

# single CCD
#scope.scan_scope_display(None, "00_RTM1noise_rmBufferS1S3_2_tm.fits", datadir=datadir)


#---- Checking statistics on scans


#scope.cut_scan_plot(tmbasefile, datadir=datadir, polynomfit=False)


#scope.cut_scan_plot(l[0][1], cutcolumns=[120], datadir=datadir, polynomfit=True, displayamps=range(16))

#for f in l[0]:
#    scope.cut_scan_plot(f, datadir=datadir, polynomfit=False, displayamps=range(16))
    #scope.stats_scan_plot(f, datadir=datadir, basecols=slice(70, 90), signalcols=slice(140, 160))

#multiscope.plot_corrcoef_raftscope(l[0], ROIrows=slice(10,1000), ROIcols=slice(150,170),
#                                   xylabels=l[1], title='RTM8 S1-only scan at low time', norm=False)

#---- Comparing scans channel per channel for a single CCD

# Mixing raw and fits files does not work now
#listlabels = ["Baseline", "BSS=0", "REB0"]
#listlabels = [s for s in ["%d%d" % (i, j) for i in range(3) for j in range(3)]]

#listscans = ["rtm8scanmodetm1/01_rtm8_tm_1_bias.fits",
#             "specscans/BSS0/01_bias2.fits",
#             "specscans/REB0/01_bias2.fits"]
#listscans = ["rtm8scanmodetm1/%s_rtm8_tm_1_bias.fits" % s for s in listlabels]

#Sscope.compare_scope_display(listscans, listlabels, datadir, title='Channels of S01', diff=False)


