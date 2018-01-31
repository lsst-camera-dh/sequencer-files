import os
import scope
import multiscope
import raftstats

#datadir = '/Users/nayman/Documents/REB/TS8/RTM8/longscan'
#datadir = '/Users/nayman/Documents/REB/TS8/RTM8/rtm8seqtests3/longscans'
datadir = "/Users/nayman/Documents/REB/TS8/RTM10/longsettle"

#tmfile = "%s_TS8_ITL_longsettle_scan_fixclamp_tm_2.fits"
#tmfile = "%s_rtm8_TS8_ITL_longsettle_scan_bias_tm_2.fits"
#tmfile = "%s_longsettle_longS1_scan_bias_tm_3.fits"
#tmfile = "%s_scan_tm_TS8_ITL_longsettle_scan_fixclamp.fits"
tmfile = "%s_scan_tm_TS8_ITL_longsettle_longS1_scan_fixclamp.fits"

l = raftstats.get_fits_raft(inputfile=tmfile % "00", datadir=datadir)

#for s in ["%d%d" % (i, j) for i in range(3) for j in range(3)]:
#    scope.plot_long_scan(tmfile % s, 5, datadir, "RTM8/TS8_ITL_longsettle_longS1.seq")
#    scope.stats_long_scan(tmfile % s, 5, datadir)

multiscope.raft_display_longscan(tmfile % "00", 5, datadir, 'RTM10 settling with moved clamp and long S1')


#outstats = open(os.path.join(datadir, "statslongscan.txt"), 'w')
#for f in l[0]:
#    outstats.write(f+'\n')
    # targeting RD and RU windows in long scan
#    outstats.write(raftstats.repr_stats(f, True, ROI1rows=slice(402, 600), ROI1cols=slice(75, 105), ROI2rows=slice(802, 1000), ROI2cols=slice(129, 159)))

#outstats.close()
