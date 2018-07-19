# specific script to plot the differences between raft scans

import sys
import os.path
import numpy as np
from matplotlib import pyplot as plt
import multiscope

datadir = '/Users/nayman/Documents/REB/TS8/RTM13'

#seqfile = 'RTM1/TS8_ITL_2s_newflush_v2.seq'

#listlabels = ["Baseline", "BSS=0", "REB0"]
#listlabels = ["R50", "R200"]
listlabels = ["Unipolar", "Bipolar"]

#listscans = ["rtm8scanmodetm1/00_rtm8_tm_1_bias.fits",
#            "specscans/BSS0/00_bias2.fits",
#             "specscans/REB0/00_bias2.fits"]
#listscans = ["RTM10/RTM10-scan-mode-images/00_TS8_ITL_clockcross90_bias_scan_tm.fits",
#             "RTM10-R200/rtm10-rebuilt-scans/00_TS8_ITL_clockcross90_bias_scan_tm_2.fits"]
listscans = ["run-8442/00_0_scan_20180626200634_TM.fits",
             "run-8499/00_0_scan_20180701021633_TM.fits"]

fig, axes = plt.subplots(nrows = 3, ncols = 3, figsize=(17, 12))

color_idx = [plt.cm.jet(i) for i in np.linspace(0, 1, 16)]

# plot baseline on first row
raftarrays, seglist = multiscope.get_scandata_raft(listscans[0], datadir)
raftarrays2, seglist = multiscope.get_scandata_raft(listscans[1], datadir)


for j in range(3):

    for num in range(3):
        tmscope = raftarrays[num * 3 + j]
        ax = axes[0, num]

        # single CCD plot
        for c in range(16):
            tmchan = tmscope[c].mean(axis=0)
            ax.plot(tmchan, color=color_idx[c])

            ax.set_xlim(0, 255)
            ax.set_xticks(np.arange(0, 256, 32))
            ax.set_title(seglist[num * 3 + j])

            if num == 0:
                ax.set_ylabel('%s scan (ADU)' % listlabels[0])
            ax.grid(True)



    for num in range(3):
        tmscope = raftarrays2[num * 3 + j]
        ax = axes[1, num ]

        # single CCD plot
        for c in range(16):
            tmchan = tmscope[c].mean(axis=0)
            ax.plot(tmchan, color=color_idx[c])

            ax.set_xlim(0, 255)
            ax.set_xticks(np.arange(0, 256, 32))
            ax.set_title(seglist[num * 3 + j])

            if num == 0:
                ax.set_ylabel('%s scan (ADU)' % listlabels[1])
            ax.grid(True)

    # subtract first scan from second scan
    for num in range(3):
        tmscope = raftarrays[num * 3 + j]
        tmscope2 = raftarrays2[num * 3 + j]
        ax = axes[2, num]

        # single CCD plot
        for c in range(16):
            tmchan = tmscope2[c].mean(axis=0) - tmscope[c].mean(axis=0)
            ax.plot(tmchan, label=c, color=color_idx[c])

            ax.set_xlim(0, 255)
            ax.set_xticks(np.arange(0, 256, 32))
            ax.set_title(seglist[num * 3 + j])
            ax.set_ylim(-5000, 5000)

            if num == 0:
                ax.set_ylabel('%s - %s (ADU)' % (listlabels[1], listlabels[0]))
            ax.set_xlabel('Time increment (10 ns)')
            ax.grid(True)


    ax.legend(bbox_to_anchor=(1.05, 0), loc='lower left', borderaxespad=0.)

    plt.suptitle("Difference between scans", fontsize='x-large')

    plt.savefig(os.path.join(datadir, "diffraftscope%d.png" % j))
    plt.show()






