# !/usr/bin/env python

# Displays a scope-like view of the CCD output waveforms for the whole raft.
#
# Changelog
# 20161207: C. Juramy, initialized from LPNHE bench code.
#
# Syntax as main:
# python multiscope.py [s00-tm-scan.fits]
# python multiscope.py [<path>/s00/tm-scan.fits]
# (expects the name and path for the first of the image files of the raft, will go looking for the others)
#
# Syntax in a script:
# import multiscope
# multiscope.raft_display("tm-scan.fits")

import sys
import os.path
import numpy as np
from matplotlib import pyplot as plt
import scope


def raft_display_allchans(inputfile, datadir=''):
    """
    Builds up data from all raft files and display scans.
    :param datadir: optional, directory where data is stored
    :param inputfile: the first file (for Reb0 or S00). Full path if datadir is not given
    :return:
    """
    raftarrays = []
    if os.path.splitext(inputfile)[1] in [".fits", ".fz"]:
        # starts with s00 through s22
        seglist = ["s%d%d" % (i, j) for i in range(3) for j in range(3)]
        raftfits = [inputfile.replace("s00", s) for s in seglist]
        nccdperfile = 1
        for f in raftfits:
            raftarrays.append(scope.get_scandata_fromfile(f, datadir))
    else:
        # starts with Reb0 through Reb2
        reblist = ["Reb0", "Reb1", "Reb2"]
        rebraws = [inputfile.replace("Reb0", s) for s in reblist]
        seglist = [r + "-%s" % stripe for stripe in ['A', 'B', 'C'] for r in reblist]
        nccdperfile = 3
        for f in rebraws:
            raftarrays.append(scope.get_scandata_fromfile(f, datadir))

    fig, axes = plt.subplots(nrows = 3, ncols = 3, figsize=(10, 10))
    color_idx = [plt.cm.jet(i) for i in np.linspace(0, 1, 16)]

    # plot all channels, with one subplot per CCD
    for num,tmscope in enumerate(raftarrays):
        for stripe in range(nccdperfile):
            ax = axes[(num * nccdperfile) / 3, (num * nccdperfile) % 3 + stripe]

            # single CCD plot
            for c in range(16):
                # image extensions are labeled as 'Segment00' in CCS
                # they are in extensions 1 to 16
                tmchan = tmscope[c + stripe * 16, 1:, :].mean(axis=1)
                ax.plot(tmchan, label=c, color=color_idx[c])
            ax.set_xlim(0, 255)
            ax.set_xticks(np.arange(0, 256, 32))
            ax.set_title(seglist[num * nccdperfile + stripe])
            #ax.set_xlabel('Time increment (10 ns)')
            #ax.set_ylabel('Scan (ADU)')
            ax.grid(True)
    # TODO: common legend
    plt.savefig("multiscope.png")
    plt.show()


if __name__ == '__main__':

    itm = sys.argv[1]
    raft_display_allchans(itm)
