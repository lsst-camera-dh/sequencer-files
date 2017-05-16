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


def get_scandata_raft(inputfile, datadir=''):
    """
    Builds up list of data arrays from all raft files (one array per CCD), plus list of segment names.
    :param datadir: optional, directory where data is stored
    :param inputfile: the first file (for Reb0 or S00). Full path if datadir is not given
    :return:
    """
    raftarrays = []
    if os.path.splitext(inputfile)[1] in [".fits", ".fz"]:
        # starts with 00 through 22
        seglist = ["%d%d" % (i, j) for i in range(3) for j in range(3)]
        # when REB2 data is missing
        #seglist = ["%d%d" % (i, j) for i in range(2) for j in range(3)]
        raftfits = [inputfile.replace("00-", s + '-') for s in seglist]
        for f in raftfits:
            raftarrays.append(scope.get_scandata_fromfile(f, datadir))
    else:
        # starts with Reb0 through Reb2
        reblist = ["Reb0", "Reb1", "Reb2"]
        rebraws = [inputfile.replace("Reb0", s) for s in reblist]
        seglist = [r + "-%s" % stripe for r in reblist for stripe in ['A', 'B', 'C'] ]
        for f in rebraws:
            fullreb = scope.get_scandata_fromfile(f, datadir)  # 3D array: 48 channels, lines, columns
            #print fullreb.shape
            raftarrays.extend([a for a in np.split(fullreb, 3, axis=0)])  # splits REB data into 3 CCDs

    return raftarrays, seglist

def raft_display_allchans(inputfile, datadir=''):
    """
    Builds up data from all raft files and display scans.
    :param datadir: optional, directory where data is stored
    :param inputfile: the first file (for Reb0 or S00). Full path if datadir is not given
    :return:
    """
    raftarrays, seglist = get_scandata_raft(inputfile, datadir)

    fig, axes = plt.subplots(nrows = 3, ncols = 3, figsize=(15, 12))
    # when REB2 data is missing
    # fig, axes = plt.subplots(nrows = 2, ncols = 3, figsize=(15, 9))
    color_idx = [plt.cm.jet(i) for i in np.linspace(0, 1, 16)]

    # plot all channels, with one subplot per CCD
    listaxes = []
    for num,tmscope in enumerate(raftarrays):
        ax = axes[num  / 3, num  % 3 ]

        # single CCD plot
        for c in range(16):
            # image extensions are labeled as 'Segment00' in CCS
            # they are in extensions 1 to 16
            #print tmscope.shape
            tmchan = tmscope[c].mean(axis=0)
            ax.plot(tmchan, label=c, color=color_idx[c])
            if num == 0:
                # for common legend
                listaxes.append(ax)

            ax.set_xlim(0, 255)
            ax.set_xticks(np.arange(0, 256, 32))
            ax.set_title(seglist[num])
            #ax.set_xlabel('Time increment (10 ns)')
            #ax.set_ylabel('Scan (ADU)')
            ax.grid(True)

    # TODO: common legend that works
    #plt.legend(handles=listaxes,loc = 'upper center', bbox_to_anchor = (0.5, 0), bbox_transform = plt.gcf().transFigure)
    dataname = scope.get_rootfile(inputfile)
    #plt.title(dataname)  # TODO: put it above all plots
    plt.savefig(os.path.join(datadir, "multiscope-%s.png" % dataname))
    plt.show()


if __name__ == '__main__':

    itm = sys.argv[1]
    raft_display_allchans(itm)
