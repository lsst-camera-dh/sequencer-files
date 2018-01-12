# specific script to plot the differences between raft scans

import sys
import os.path
import numpy as np
from matplotlib import pyplot as plt
import multiscope

datadir = '/Users/nayman/Documents/REB/TS8/RTM8/RDscans'

seqfile = 'RTM1/TS8_ITL_2s_newflush_v2.seq'

#listlabels = ["Baseline", "BSS=0", "REB0"]
listlabels = ["RD=13", "RD=14"]

#listscans = ["rtm8scanmodetm1/00_rtm8_tm_1_bias.fits",
#            "specscans/BSS0/00_bias2.fits",
#             "specscans/REB0/00_bias2.fits"]
listscans = ["00_tm_bias_2.fits", "00_RD14_tm_bias_2.fits"]

fig, axes = plt.subplots(nrows = 3, ncols = 3, figsize=(15, 12))

color_idx = [plt.cm.jet(i) for i in np.linspace(0, 1, 16)]

# plot baseline on first row
raftarrays, seglist = multiscope.get_scandata_raft(listscans[0], datadir)

for num in range(3):
    tmscope = raftarrays[num * 4]
    ax = axes[0, num  % 3 ]

    # single CCD plot
    for c in range(16):
        tmchan = tmscope[c].mean(axis=0)
        ax.plot(tmchan, label=c, color=color_idx[c])

        ax.set_xlim(0, 255)
        ax.set_xticks(np.arange(0, 256, 32))
        ax.set_title(seglist[num * 4])

        if num%3 == 0:
            ax.set_ylabel('RD13 scan (ADU)')
        ax.grid(True)


raftarrays2, seglist = multiscope.get_scandata_raft(listscans[1], datadir)

for num in range(3):
    tmscope = raftarrays2[num * 4]
    ax = axes[1, num  % 3 ]

    # single CCD plot
    for c in range(16):
        tmchan = tmscope[c].mean(axis=0)
        ax.plot(tmchan, label=c, color=color_idx[c])

        ax.set_xlim(0, 255)
        ax.set_xticks(np.arange(0, 256, 32))
        ax.set_title(seglist[num * 4])

        if num%3 == 0:
            ax.set_ylabel('RD14 scan (ADU)')
        ax.grid(True)

# subtract baseline from second scan
for num in range(3):
    tmscope = raftarrays[num * 4]
    tmscope2 = raftarrays2[num * 4]
    ax = axes[2, num  % 3 ]

    # single CCD plot
    for c in range(16):
        tmchan = tmscope2[c].mean(axis=0) - tmscope[c].mean(axis=0)
        ax.plot(tmchan, color=color_idx[c])

        ax.set_xlim(0, 255)
        ax.set_xticks(np.arange(0, 256, 32))
        ax.set_title(seglist[num * 4])

        if num%3 == 0:
            ax.set_ylabel('RD14 - RD13 (ADU)')
        if num/3 == 2:
            ax.set_xlabel('Time increment (10 ns)')
        ax.grid(True)

# subtract baseline from REB0
#raftarrays3, seglist = multiscope.get_scandata_raft(listscans[2], datadir)
#
#for num,tmscope,tmscope2 in zip(range(3), raftarrays[:3], raftarrays3[:3]):
#    ax = axes[2, num  % 3 ]

    # single CCD plot
#    for c in range(16):
#        tmchan = tmscope2[c].mean(axis=0) - tmscope[c].mean(axis=0)
#        ax.plot(tmchan, color=color_idx[c])
#
#        ax.set_xlim(0, 255)
#        ax.set_xticks(np.arange(0, 256, 32))
#        ax.set_title(seglist[num])
#
#        if num%3 == 0:
#            ax.set_ylabel('REB0-Baseline (ADU)')
#        ax.set_xlabel('Time increment (10 ns)')
#        ax.grid(True)


ax.legend(bbox_to_anchor=(1.05, 0), loc='lower left', borderaxespad=0.)

plt.suptitle("Difference between scans", fontsize='x-large')

plt.savefig(os.path.join(datadir, "diffraftscope.png"))
plt.show()






