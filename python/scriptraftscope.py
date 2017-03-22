import scope
import multiscope

datadir = '/Users/nayman/Documents/REB/TS8/ETU2Dev/'
seqfile = '/Users/nayman/Documents/REB/TS8/sequencer-files/TS8_ITL_ResetFirst_20170313-scan-mode.seq'

#multiscope.raft_display_allchans("scan-mode-transparent/Image_R00.Reb0_20170320200751.dat", datadir)
scope.combined_scope_display("scan-mode-dsi/Image_R00.Reb0_20170320200320.dat",
                             "scan-mode-transparent/Image_R00.Reb0_20170320200751.dat",
                             seqfile=seqfile, c=0, datadir=datadir)