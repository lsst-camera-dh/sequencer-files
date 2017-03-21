import scope
import multiscope

datadir = '/Users/nayman/Documents/REB/TS8/ETU2Dev/'
seqfile = '/Users/nayman/Documents/REB/TS8/sequencer-files/'

multiscope.raft_display_allchans("scan-mode-transparent/Image_R00.Reb0_20170320200751.dat", datadir)
#scope.combined_scope_display("scan-mode-dsi/Image_R00.Reb0_20170320200320.dat",
#                             "scan-mode-transparent/Image_R00.Reb0_20170320200751.dat", 6, datadir=datadir)