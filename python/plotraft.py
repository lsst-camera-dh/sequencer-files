# !/usr/bin/env python

# Generic plot of raft data.
#
# Changelog
# 20170323: C. Juramy, initialized from raft scope plots.
#

import sys
import os.path
import numpy as np
from matplotlib import pyplot as plt

def get_text_data(cols, inputfile, datadir=''):
    """
    Builds up list of data arrays from all raft files (one array per CCD), plus list of segment names.
    :param datadir: optional, directory where data is stored
    :param inputfile: the first file (for Reb0 or S00). Full path if datadir is not given
    :return:
    """

    raftarrays = np.loadtxt(os.path.join(datadir, inputfile), skiprows=1, usecols=cols)
    # starts with 00 through 22
    raftarrays = raftarrays.reshape((9, 16, np.alen(raftarrays)/144, len(cols)))
    seglist = (["S%d%d" % (i, j) for i in range(3) for j in range(3)],
               ["Seg%d%d" % (k, l) for k in [0, 1] for l in range(8)])
    print raftarrays.shape
    return raftarrays, seglist

def raft_display_allchans_2D(colx, coly, inputfile, datadir=''):
    """
    Builds up data from all raft files and display 2D plots.
    :param datadir: optional, directory where data is stored
    :param inputfile: the first file (for Reb0 or S00). Full path if datadir is not given.
    :return:
    """
    raftarrays, seglist = get_text_data((colx, coly), inputfile, datadir)

    fig, axes = plt.subplots(nrows = 3, ncols = 3, figsize=(10, 10))
    color_idx = [plt.cm.jet(i) for i in np.linspace(0, 1, 16)]

    # plot all channels, with one subplot per CCD
    listaxes = []
    for num in range(9):
        ax = axes[num  / 3, num  % 3 ]

        # single CCD plot
        for c in range(16):
            # image extensions are labeled as 'Segment00' in CCS
            ax.plot(raftarrays[num, c, :, 0], raftarrays[num, c, :, 1], label=seglist[1][c],
                    color=color_idx[c], marker='o')
            if num == 0:
                # for common legend
                listaxes.append(ax)

            ax.set_title(seglist[0][num])
            ax.grid(True)

    # TODO: common legend that works
    #plt.legend(handles=listaxes,loc = 'upper center', bbox_to_anchor = (0.5, 0), bbox_transform = plt.gcf().transFigure)
    dataname = os.path.splitext(os.path.basename(inputfile))[0]
    plt.savefig(os.path.join(datadir, "raft-%s.png" % dataname))
    plt.show()


if __name__ == '__main__':

    itm = sys.argv[1]
    raft_display_allchans_2D(2, 5, itm)
