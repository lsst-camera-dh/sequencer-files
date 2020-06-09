import scope
import raftstats
import multiscope
import os

rtm = "RTM19"
run = "9538"
#c = "S3"

#datadir = "/Users/nayman/Documents/REB/TS8/%s/rtm-scan-mode-data/rtm2-scan-tm-bias" % rtm
#datadir = "/Users/nayman/Documents/REB/TS8/%s/rtm9scans1" % rtm
#datadir = '/Users/nayman/Documents/REB/TS8/%s/singleclockscans/single%s' % (rtm, c)
#datadir = "/Users/nayman/Documents/REB/TS8/%s/RGhigh" % rtm
#datadir = "/Users/nayman/Documents/REB/TS8/RTM10/RTM10-scan-mode-images/"
#datadir = "/Users/nayman/Documents/REB/TS8/%s/rtm10-rebuilt-scans" % rtm
datadir = "/Users/nayman/Documents/REB/TS8/%s/run-%s/DSI" % (rtm, run)

#seqfile = 'ITL/TS8_ITL_2s_newflush_v4.seq'
seqfile = 'ITL/ts8-itl-2s-v5.seq'
#seqfile = "E2V/seq-e2v-2s.seq"

#tmbasefile = "rtm8run2scan1/00_rtm8_tm_scan_2.fits"
#tmbasefile = "00_scan_tm_TS8_ITL_injectRD_fix_2.fits"
#tmbasefile = "00_scan_tm_TS8_ITL_singleS3.fits"
#tmbasefile = "00_scan_tm_TS8_ITL_RGhigh_longS1_fix.fits"
#tmbasefile = "00_RTM10_scan_tm_TS8_ITL_RGhigh_allS.fits"
#tmbasefile = "basescan/00_TS8_ITL_longS1_scan_tm_2.fits"
#tmbasefile = "00_TS8_ITL_RGhigh_longS1_fix_bias_scan_dsi.fits"
#tmbasefile = "00_TS8_ITL_clockcross90_bias_scan_tm_2.fits"
#tmbasefile = "00_bias2.fits"
#tmbasefile = "00_seq-e2v-RGhigh_scan_tm_2.fits"
tmbasefile = sorted(os.listdir(datadir))[0]

#dsibasefile = "00_2s_camel_v3_scan_dsi_1.fits"
#dsibasefile = "00_TS8_ITL_clockcross90_bias_scan_dsi_2.fits"

# returns tuple: (list of files, list of segments)
#l = raftstats.get_fits_raft(inputfile='', datadir=datadir)
l = raftstats.get_fits_raft(inputfile=tmbasefile, datadir=datadir)
#ldsi = raftstats.get_fits_raft(inputfile=dsibasefile, datadir=datadir)


#---- Scan display for all raft channels

multiscope.raft_display_allchans(tmbasefile, datadir, '%s run-%s' % (rtm, run))
#multiscope.raft_display_allchans("", datadir, '%s run-%s' % (rtm, run))

#---- Combined display of single channel with clock sequences

#scope.combined_scope_display("02_2_scan_20180522052851_DSI.fits", "02_2_scan_20180522052418_TM.fits",
#                             seqfile=seqfile, c=10, datadir=datadir, loc="02")

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

for f in l[0][:3]:
    scope.cut_scan_plot(f, datadir=datadir, polynomfit=False, displayamps=range(16))
    #scope.stats_scan_plot(f, datadir=datadir, basecols=slice(70, 90), signalcols=slice(140, 160))

#multiscope.plot_corrcoef_raftscope(l[0], ROIrows=slice(10,1000), ROIcols=slice(150,170),
#                                   xylabels=l[1], title='RTM8 S1-only scan at low time', norm=False)

#---- Output of statistics to file
#raftstats.average_1D_tofile(l[0], l[1], datadir, 0, slice(1, 1000), norm=False)

#---- Comparing scans channel per channel for a single CCD

#datadir = "/Users/nayman/Documents/REB/TS8"

#listlabels = [s for s in ["%d%d" % (i, j) for i in range(3) for j in range(3)]]
#listlabels = ["R50", "R200"]

#listscans = ["rtm8scanmodetm1/%s_rtm8_tm_1_bias.fits" % s for s in listlabels]
#listscans =["RTM10/RTM10-scan-mode-images/%s_TS8_ITL_clockcross90_bias_scan_tm.fits",
#             "RTM10-R200/rtm10-rebuilt-scans/%s_TS8_ITL_clockcross90_bias_scan_tm_2.fits"]

#scope.compare_scope_display(listscans, listlabels, datadir, title='Channels of S01', diff=False)

#for s in ["%d%d" % (i, j) for i in range(3) for j in range(3)]:
#    scope.compare_scope_display([listscans[0] % s, listscans[1] % s], listlabels, datadir, title='Channels of S%s' % s, diff=False)
