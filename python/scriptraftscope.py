import scope
import multiscope



#datadir = '/Users/nayman/Documents/REB/TS8/ETU2Dev/'
#datadir = '/Users/nayman/Documents/REB/TS8/ETU2Dev/cj-tst2'
datadir = '/Users/nayman/Documents/REB/TS8/ETU2Dev/mod3b_scan'

#seqfile = 'TS8_ITL_ResetFirst_20170313-scan-mode.seq'
#seqfile = 'TS8_ITL_ResetFirst_CJ_20170321_mod2.seq'
seqfile = 'TS8_ITL_ResetFirst_CJ_20170321_mod3.seq'

#multiscope.raft_display_allchans("scan-mode-transparent/Image_R00.Reb0_20170320200751.dat", datadir)
#scope.combined_scope_display("scan-mode-dsi/Image_R00.Reb0_20170320200320.dat",
#                             "scan-mode-transparent/Image_R00.Reb0_20170320200751.dat",
#                             seqfile=seqfile, c=0, datadir=datadir)

#multiscope.raft_display_allchans("scan-mode-tm-cj-mod2/00_test-cj-mod2.fits", datadir)
#scope.combined_scope_display("scan-mode-dsi-cj-mod2/01_test-cj-mod2-dsi.fits",
#                             "scan-mode-tm-cj-mod2/01_test-cj-mod2.fits",
#                             seqfile=seqfile, c=3, datadir=datadir, loc="01")

#multiscope.raft_display_allchans("00_test-cj-mod3b_flat_transp_scan2.fits", datadir)
#multiscope.raft_display_allchans("00_test-cj-mod3b_transp_dark_scan2.fits", datadir)
#for c in range(16):
    #scope.combined_scope_display("01_test-cj-mod3b_flat_scan2.fits",
    #                            "01_test-cj-mod3b_flat_transp_scan2.fits",
    #                            seqfile=seqfile, c=c, datadir=datadir, loc="01", display=False)
    #scope.combined_scope_display("01_test-cj-mod3_scan.fits",
    #                            "01_test-cj-mod3b_transp_dark_scan2.fits",
    #                            seqfile=seqfile, c=c, datadir=datadir, loc="01", display=False)

for s in ["%d%d" % (i, j) for i in range(2) for j in range(3)]:
    scope.scan_scope_display(None, "%s_test-cj-mod3b_transp_dark_scan2.fits" % s, datadir=datadir)