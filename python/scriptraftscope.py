import scope
import raftstats
import multiscope

rtm = "RTM10"
c = "S3"

#datadir = "/Users/nayman/Documents/REB/TS8/%s/camel_v3" % rtm
#datadir = "/Users/nayman/Documents/REB/TS8/%s/rtm9scans1" % rtm
#datadir = '/Users/nayman/Documents/REB/TS8/%s/singleclockscans/single%s' % (rtm, c)
datadir = '/Users/nayman/Documents/REB/TS8/RTM8/'
#datadir = '/Users/nayman/Documents/REB/TS8/RTM8/superscan'
#datadir = "/Users/nayman/Documents/REB/TS8/%s/RGhigh" % rtm
#datadir = "/Users/nayman/Documents/REB/TS8/%s/injectRD" % rtm

#seqfile = 'TS8_ITL_ResetFirst_CJ_20170321_mod3.seq'
seqfile = 'RTM1/TS8_ITL_2s_newflush_v2.seq'
#seqfile = 'RTM8/TS8_ITL_longS1_scan.seq'
#seqfile = "E2V/seq-e2v-RGhigh.seq"
#seqfile = "RTM10/TS8_ITL_2s_camel_v3.seq"

#tmbasefile = "00_scan_tm_TS8_ITL_injectRD_fix_2.fits"
#tmbasefile = "00_scan_tm_TS8_ITL_singleS3.fits"
#tmbasefile = "00_scan_tm_TS8_ITL_RGhigh_longS1_fix.fits"
#tmbasefile = "00_RTM10_scan_tm_TS8_ITL_RGhigh_allS.fits"
#tmbasefile = "basescan/00_TS8_ITL_longS1_scan_tm_2.fits"
#tmbasefile = "00_TS8_ITL_RGhigh_longS1_fix_bias_scan_dsi.fits"
#tmbasefile = "00_TS8_ITL_clockcross90_bias_scan_tm.fits"
#tmbasefile = "00_bias2.fits"
#tmbasefile = "00_seq-e2v-RGhigh_scan_tm_2.fits"
#tmbasefile = "00_2s_camel_v3_scan_tm_1.fits"
#dsibasefile = "00_2s_camel_v3_scan_dsi_1.fits"

# returns tuple: (list of files, list of segments)
#l = raftstats.get_fits_raft(inputfile=tmbasefile, datadir=datadir)
#ldsi = raftstats.get_fits_raft(inputfile=dsibasefile, datadir=datadir)


#---- Scan display for all raft channels

#multiscope.raft_display_allchans(tmbasefile, datadir, '%s with camel clocking' % (rtm,))

#---- Combined display of single channel with clock sequences

scope.combined_scope_display("rtm8scanmodedsi1/00_rtm8_dsi_1_bias.fits", "rtm8scanmodetm1/00_rtm8_tm_1_bias.fits",
                             seqfile=seqfile, c=12, datadir=datadir, loc="00")

#for f,s,d in zip(l[0],l[1],ldsi[0]):
#    scope.combined_scope_display(d, f,
#                                 seqfile=seqfile, c=12, datadir=datadir, loc=s)

#for f, s in zip(l[0], l[1]):
#    scope.combined_scope_display(None, f, seqfile=seqfile, c=12, datadir=datadir, loc=s)

#for c in [4]:
#    scope.combined_scope_display("00_seq-e2v-injectRD_scan_dsi_1.fits",
#                                 tmbasefile,
#                                 seqfile=seqfile, c=c, datadir=datadir, loc="01", display=True)

#for c in range(16):
#scope.combined_scope_display(dsibasefile, tmbasefile, seqfile=seqfile, c=12, datadir=datadir, loc="00")

#s = "20"
#scope.combined_scope_display(dsibasefile.replace("00_", s + '_'),
#                             tmbasefile.replace("00_", s + '_'),
#                                 seqfile=seqfile, c=12, datadir=datadir, loc=s)



#---- Display of all channels, one graph per CCD

#for s in ["%d%d" % (i, j) for i in range(3) for j in range(3)]:
#    scope.scan_scope_display(None, "rtm2-scan-tm-bias/%s-rtm2-scan-tm-bias_2.fits" % s, datadir=datadir)
#    scope.scan_scope_display(None, "%s_test-cj-mod3b_transp_dark_scan2.fits" % s, datadir=datadir)

# single CCD
#scope.scan_scope_display(None, "00_RTM1noise_rmBufferS1S3_2_tm.fits", datadir=datadir)


#---- Checking statistics on scans


#scope.cut_scan_plot(tmbasefile, datadir=datadir, polynomfit=False)
#scope.cut_scan_plot(tmbasefile.replace("00_", s + '_'), datadir=datadir, polynomfit=False)


#scope.cut_scan_plot(l[0][1], cutcolumns=[120], datadir=datadir, polynomfit=True, displayamps=range(16))

#for f in l[0]:
#    scope.cut_scan_plot(f, datadir=datadir, polynomfit=False, displayamps=range(16))
    #scope.stats_scan_plot(f, datadir=datadir, basecols=slice(70, 90), signalcols=slice(140, 160))

#multiscope.plot_corrcoef_raftscope(l[0], ROIrows=slice(10,1000), ROIcols=slice(150,170),
#                                   xylabels=l[1], title='RTM8 S1-only scan at low time', norm=False)

#---- Output of statistics to file
#raftstats.average_1D_tofile(l[0], l[1], datadir, 0, slice(1, 1000), norm=False)

#---- Comparing scans channel per channel for a single CCD

# Mixing raw and fits files does not work now
#listlabels = ["Baseline", "BSS=0", "REB0"]
#listlabels = [s for s in ["%d%d" % (i, j) for i in range(3) for j in range(3)]]

#listscans = ["rtm8scanmodetm1/01_rtm8_tm_1_bias.fits",
#             "specscans/BSS0/01_bias2.fits",
#             "specscans/REB0/01_bias2.fits"]
#listscans = ["rtm8scanmodetm1/%s_rtm8_tm_1_bias.fits" % s for s in listlabels]

#scope.compare_scope_display(listscans, listlabels, datadir, title='Channels of S01', diff=False)


