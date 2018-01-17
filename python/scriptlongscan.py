import scope
import multiscope


datadir = '/Users/nayman/Documents/REB/TS8/RTM8/longscan'

tmfile = "%s_rtm8_TS8_ITL_longsettle_scan_bias_tm_2.fits"
#tmfile = "%s_longsettle_longS1_scan_bias_tm_3.fits"

for s in ["%d%d" % (i, j) for i in range(3) for j in range(3)]:
#    scope.plot_long_scan(tmfile % s, 5, datadir, "RTM8/TS8_ITL_longsettle_longS1.seq")
    scope.stats_long_scan(tmfile % s, 5, datadir)

#multiscope.raft_display_longscan(tmfile % "00", 5, datadir, 'Long settling time in RTM8 with long S1')
